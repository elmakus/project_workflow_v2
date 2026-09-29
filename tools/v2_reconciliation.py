#!/usr/bin/env python3
"""Deterministic intra-V2 schema reconciliation for Issue #23 M02.

Approved P1 bounded contract only. This module recognizes exactly two
evidenced producer-drift profiles and reconciles them into current canonical
records under Recovery semantics. It is separate from V1 discovery semantics
(``tools/v1_migration.py``) and must not be generalized into heuristic legacy
mapping.

Supported profiles (exact structural checks, no guessing):

- ``issue20-definition-planning-drift``: pre-Recovery #20
  ``DEFINITION.toml`` + ``PLANNING.toml`` shape with integer revisions,
  ``plan_artifact``, ``review_mode = "normal"``, no immutable ``[subject]``
  table and no plan-review locator.
- ``issue22-workstream-bundle-drift``: pre-Recovery #22
  ``WORKSTREAM.toml`` + ``DEFINITION.toml`` + ``PLANNING.toml`` +
  ``TRACKER.toml`` + ``TASK_BOARD.toml`` shape with missing
  ``created_from``/``task_board`` locator, legacy Definition string locators
  and uppercase enums, legacy Planning integer revision/``plan_artifact``/
  ``frozen_subject``/``normal`` mode, legacy Tracker ``number``/``url``/
  ``authority`` fields, and legacy Task Board ``review_pending`` /
  top-level ``result_path`` / ``review_requirement`` without exact
  result/review-attempt locators.

Authority rules (requirements R6-R11, decisions D3-D6):

- Preserve accepted scope and Definition authority verbatim only when the
  semantic path is durably valid; otherwise fail closed.
- Preserve an immutable subject-bound B/Plan Review/C or implementation-review
  approval only when the exact repository+commit+path+blob identity is already
  proven by durable Git evidence supplied by the caller. Never synthesize a
  missing commit/blob from mutable current content.
- When canonicalization changes or cannot prove the exact subject, reset the
  affected gate (``premium_b``/``premium_c`` to ``not_due`` with empty
  subjects, Planning to ``draft``) instead of transferring approval.
- Keep prior terminal review evidence append-only; this module never rewrites
  a review attempt onto a different subject. Any attempted identity-changing
  replacement without a lawful successor fails closed. Issue #26
  pending-attempt replacement is explicitly out of scope and fails closed.
- Unknown, ambiguous, contradictory or attempt-bound unsafe inputs remain
  fail-closed Recovery without mutation.
- Every proposed canonical output is validated with the production
  ``tools.state_contract`` validators before any mutation, and persisted only
  through ``render_validated_state_record`` / ``write_validated_state_record``.
- Apply accepts each affected file only in its exact expected-before or
  already-produced after-state, rejects unrelated divergence, and is
  deterministic/idempotent/restart-safe. No session/runtime identity or
  parallel migration state store becomes authority. No external tracker
  mutation is performed; TRACKER.toml reconciliation is file-only.

The supplied #20/#22 reproductions are producer drift under an
already-current executable contract, not evidence of a historical
schema-version transition. This module therefore performs structural
reconciliation, not version-upgrade inference.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from tools.state_contract import (
    ValidationError,
    render_validated_state_record,
    validate_state_record,
    write_validated_state_record,
)

SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA64 = re.compile(r"^[0-9a-f]{64}$")

PROFILE_ISSUE20 = "issue20-definition-planning-drift"
PROFILE_ISSUE22 = "issue22-workstream-bundle-drift"
SUPPORTED_PROFILES = (PROFILE_ISSUE20, PROFILE_ISSUE22)

_FILENAME_TO_KIND = {
    "WORKSTREAM.toml": "workstream",
    "DEFINITION.toml": "definition",
    "PLANNING.toml": "planning",
    "TRACKER.toml": "tracker",
    "TASK_BOARD.toml": "task_board",
}

_TRACKER_URL = re.compile(r"^https://github\.com/([^/ \t]+/[^/ \t]+)/issues/([1-9][0-9]*)$")
_AUTHORITY_ROOTS = ("requirements/", "decisions/", "planning/", "workflow/")


class V2ReconciliationError(ValueError):
    """A supported reconciliation cannot proceed safely; remain in Recovery."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise V2ReconciliationError(message)


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fingerprint_sources(source_bytes: dict[str, bytes]) -> str:
    """Fingerprint the exact source set deterministically (64-hex)."""
    _require(bool(source_bytes), "reconciliation: no source files supplied")
    digests = {}
    for name in sorted(source_bytes):
        payload = source_bytes[name]
        _require(isinstance(payload, (bytes, bytearray)), f"reconciliation: source {name!r} must be bytes")
        digests[name] = sha256_hex(bytes(payload))
    canonical = json.dumps(digests, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return sha256_hex(canonical.encode("utf-8"))


def _is_prohibited_shape(data: dict[str, Any], where: str) -> None:
    for key in data:
        normalized = str(key).lower()
        if normalized in {
            "execution_policy", "runtime", "model", "session", "worker",
            "worker_id", "orchestration_binding", "active_execution",
            "returned", "transfer_ready", "batch", "lane", "lanes",
            "scheduler", "context_health",
        } or normalized.startswith(
            ("runtime_", "model_", "session_", "worker_", "batch_", "lane_", "scheduler_", "context_health_")
        ):
            raise V2ReconciliationError(f"{where}: prohibited canonical key {key!r} remains Recovery")


def _is_legacy_definition(data: Any) -> bool:
    if not isinstance(data, dict):
        return False
    if not isinstance(data.get("source_scope"), str) or not data["source_scope"].strip():
        return False
    if not isinstance(data.get("revision"), int):
        return False
    if "source_scope_subject" in data:
        return False
    # Corroborating drift marker: string locator or uppercase lifecycle/audit.
    requirements_is_string = isinstance(data.get("requirements"), str)
    decisions_has_string = isinstance(data.get("decisions"), list) and any(
        isinstance(item, str) for item in data["decisions"]
    )
    state_upper = data.get("state") in {"ACTIVE", "GREEN"}
    audit_upper = data.get("completeness_audit") in {"PENDING", "GREEN"}
    return bool(requirements_is_string or decisions_has_string or state_upper or audit_upper)


def _is_legacy_planning(data: Any) -> bool:
    if not isinstance(data, dict):
        return False
    if not isinstance(data.get("revision"), int):
        return False
    if not isinstance(data.get("plan_artifact"), str):
        return False
    if data.get("review_mode") != "normal":
        return False
    if "subject" in data:
        return False
    if "frozen_subject" not in data:
        return False
    return True


def _is_legacy_workstream(data: Any) -> bool:
    if not isinstance(data, dict):
        return False
    for key in ("workstream_id", "kind", "branch", "integration_target"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            return False
    # Exact evidenced drift: missing created_from and missing task_board locator.
    if "created_from" in data:
        return False
    if "task_board" in data:
        return False
    return True


def _is_legacy_tracker(data: Any) -> bool:
    if not isinstance(data, dict):
        return False
    if "number" not in data:
        return False
    if "issue_number" in data:
        return False
    if "url" not in data and "authority" not in data:
        return False
    return True


def _is_legacy_board(data: Any) -> bool:
    if not isinstance(data, dict):
        return False
    has_review_pending = False
    cards = data.get("cards")
    if isinstance(cards, list):
        for card in cards:
            if isinstance(card, dict) and card.get("status") == "review_pending":
                has_review_pending = True
            if isinstance(card, dict) and "result" in card:
                result = card["result"]
                # Any exact result locator disqualifies the pure-drift profile.
                if isinstance(result, dict) and isinstance(result.get("commit"), str) and isinstance(
                    result.get("blob"), str
                ):
                    return False
            if isinstance(card, dict) and card.get("review_attempts"):
                return False
    has_top_legacy = "result_path" in data or "review_requirement" in data
    return bool(has_review_pending or has_top_legacy)


def detect_profile(records: dict[str, dict[str, Any]]) -> str:
    """Return the single supported profile for an exact source set or fail closed."""
    _require(isinstance(records, dict) and records, "reconciliation: empty source set remains Recovery")
    names = set(records)
    unknown = names - set(_FILENAME_TO_KIND)
    _require(not unknown, f"reconciliation: unsupported source file(s) {sorted(unknown)} remain Recovery")

    # Contradictory mixed current+legacy shapes fail closed before profile match.
    definition = records.get("DEFINITION.toml")
    if isinstance(definition, dict):
        _require(
            not ("source_scope" in definition and "source_scope_subject" in definition),
            "reconciliation: contradictory Definition legacy+current keys remain Recovery",
        )
    planning = records.get("PLANNING.toml")
    if isinstance(planning, dict):
        _require(
            not ("plan_artifact" in planning and "plan_path" in planning),
            "reconciliation: contradictory Planning legacy+current keys remain Recovery",
        )
    tracker = records.get("TRACKER.toml")
    if isinstance(tracker, dict):
        _require(
            not ("number" in tracker and "issue_number" in tracker),
            "reconciliation: contradictory Tracker legacy+current keys remain Recovery",
        )
        forbidden = {"authorization", "repair_authorized", "implementation_authorized", "requirements_approved", "plan_approved"}
        _require(not (forbidden & set(tracker)), "reconciliation: tracker carries workflow authorization; remains Recovery")

    if names == {"DEFINITION.toml", "PLANNING.toml"}:
        _require(
            _is_legacy_definition(definition) and _is_legacy_planning(planning),
            "reconciliation: two-file set does not match the exact #20 drift structure; remains Recovery",
        )
        return PROFILE_ISSUE20

    if names == {"WORKSTREAM.toml", "DEFINITION.toml", "PLANNING.toml", "TRACKER.toml", "TASK_BOARD.toml"}:
        _require(
            _is_legacy_workstream(records["WORKSTREAM.toml"]),
            "reconciliation: WORKSTREAM.toml does not match the exact #22 drift structure; remains Recovery",
        )
        _require(
            _is_legacy_definition(records["DEFINITION.toml"]),
            "reconciliation: DEFINITION.toml does not match the exact #22 drift structure; remains Recovery",
        )
        _require(
            _is_legacy_planning(records["PLANNING.toml"]),
            "reconciliation: PLANNING.toml does not match the exact #22 drift structure; remains Recovery",
        )
        _require(
            _is_legacy_tracker(records["TRACKER.toml"]),
            "reconciliation: TRACKER.toml does not match the exact #22 drift structure; remains Recovery",
        )
        _require(
            _is_legacy_board(records["TASK_BOARD.toml"]),
            "reconciliation: TASK_BOARD.toml does not match the exact #22 drift structure; remains Recovery",
        )
        return PROFILE_ISSUE22

    raise V2ReconciliationError(
        f"reconciliation: source set {sorted(names)} is not an explicitly supported profile; remains Recovery"
    )


def _authority_table(path: Any, where: str) -> dict[str, str]:
    _require(isinstance(path, str) and path, f"{where}: authority path must be a non-empty string")
    _require(".." not in path.split("/") and not path.startswith("/"), f"{where}: unsafe authority path")
    _require(path.startswith(_AUTHORITY_ROOTS), f"{where}: authority path outside accepted roots")
    return {"class": "authority", "path": path}


def _lower_enum(value: Any, allowed: set[str], where: str) -> str:
    _require(isinstance(value, str) and value.strip(), f"{where}: missing enum")
    lowered = value.strip().lower()
    _require(lowered in allowed, f"{where}: unsupported enum {value!r}; remains Recovery")
    return lowered


def canonicalize_definition(legacy: dict[str, Any], workstream_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    _require(isinstance(legacy, dict), "definition: legacy record must be a table")
    _is_prohibited_shape(legacy, "definition")
    _require(legacy.get("workstream_id") == workstream_id, "definition: wrong workstream_id; remains Recovery")
    scope = legacy.get("source_scope")
    _require(isinstance(scope, str) and scope.strip(), "definition: legacy source_scope must be non-empty")
    revision_int = legacy.get("revision")
    _require(isinstance(revision_int, int) and revision_int >= 1, "definition: legacy revision must be positive integer")
    canonical_revision = f"R{revision_int}"
    subject = f"{scope.strip()}@{revision_int}"

    state = _lower_enum(legacy.get("state"), {"active", "green"}, "definition.state")
    audit = _lower_enum(legacy.get("completeness_audit"), {"pending", "green"}, "definition.completeness_audit")
    premium_a = _lower_enum(legacy.get("premium_a"), {"not_due", "due", "satisfied"}, "definition.premium_a")

    requirements_raw = legacy.get("requirements")
    if isinstance(requirements_raw, str):
        requirements = _authority_table(requirements_raw.strip(), "definition.requirements")
    elif isinstance(requirements_raw, dict):
        _require(requirements_raw.get("class") == "authority", "definition: invalid requirements locator")
        requirements = _authority_table(requirements_raw.get("path"), "definition.requirements")
    else:
        raise V2ReconciliationError("definition: legacy requirements must be a path string or authority table")

    decisions_raw = legacy.get("decisions", [])
    _require(isinstance(decisions_raw, list), "definition: legacy decisions must be an array")
    decisions: list[dict[str, str]] = []
    for index, item in enumerate(decisions_raw):
        if isinstance(item, str):
            decisions.append(_authority_table(item.strip(), f"definition.decisions[{index}]"))
        elif isinstance(item, dict):
            _require(item.get("class") == "authority", f"definition.decisions[{index}]: invalid locator")
            decisions.append(_authority_table(item.get("path"), f"definition.decisions[{index}]"))
        else:
            raise V2ReconciliationError(f"definition.decisions[{index}]: unsupported shape; remains Recovery")

    canonical = {
        "workstream_id": workstream_id,
        "source_scope_subject": subject,
        "revision": canonical_revision,
        "state": state,
        "completeness_audit": audit,
        "premium_a": premium_a,
        "requirements": requirements,
        "decisions": decisions,
    }
    try:
        validate_state_record("definition", canonical, workstream_id=workstream_id)
    except ValidationError as exc:
        raise V2ReconciliationError(f"definition: canonical output invalid: {exc}") from exc
    decision = {
        "preserved": [
            "source scope text preserved verbatim; integer revision mapped deterministically to R{N}",
            "requirements/decision authority paths preserved verbatim as authority tables",
            "lifecycle/audit/premium_a enums normalized by case only",
        ],
        "reset": [],
        "reason": "Definition scope/authority unchanged; no subject-bound gate is transferred by this record",
    }
    return canonical, decision


def canonicalize_planning(
    legacy: dict[str, Any],
    workstream_id: str,
    definition_revision: str,
    plan_subject_evidence: dict[str, str] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    _require(isinstance(legacy, dict), "planning: legacy record must be a table")
    _is_prohibited_shape(legacy, "planning")
    _require(legacy.get("workstream_id") == workstream_id, "planning: wrong workstream_id; remains Recovery")

    cycle = legacy.get("cycle")
    _require(isinstance(cycle, int) and cycle >= 1, "planning: legacy cycle must be positive integer")

    entry_subject = legacy.get("entry_subject")
    _require(isinstance(entry_subject, str) and entry_subject.strip(), "planning: legacy entry_subject must be non-empty")
    _require(
        entry_subject.strip() == definition_revision,
        "planning: legacy entry_subject does not match reconciled Definition revision; remains Recovery",
    )

    revision_int = legacy.get("revision")
    _require(isinstance(revision_int, int) and revision_int >= 1, "planning: legacy revision must be positive integer")
    canonical_revision = f"P{revision_int}"

    plan_artifact = legacy.get("plan_artifact")
    _require(isinstance(plan_artifact, str) and plan_artifact.strip(), "planning: legacy plan_artifact must be non-empty")
    plan_path = plan_artifact.strip()
    _require(
        plan_path.startswith("planning/") and plan_path.endswith(".md") and ".." not in plan_path.split("/"),
        "planning: legacy plan_artifact is not a planning Markdown artifact; remains Recovery",
    )

    _require(legacy.get("review_mode") == "normal", "planning: supported drift requires review_mode normal")
    # Deterministic representation mapping documented in the plan: legacy
    # "normal" unambiguously meant independent review in the drift contract.
    review_mode = "independent"

    premium_a = _lower_enum(legacy.get("premium_a", "satisfied"), {"not_due", "due", "satisfied"}, "planning.premium_a")
    planner_audit = _lower_enum(
        legacy.get("planner_audit", "pending"), {"pending", "green"}, "planning.planner_audit"
    )

    frozen = legacy.get("frozen_subject")
    _require(isinstance(frozen, dict), "planning: legacy frozen_subject table is required for subject proof")
    proven_subject: dict[str, str] | None = None
    if plan_subject_evidence is not None:
        _require(
            isinstance(plan_subject_evidence, dict),
            "planning: plan subject evidence must be a repository/commit/path/blob table",
        )
        for key in ("repository", "commit", "path", "blob"):
            _require(
                isinstance(plan_subject_evidence.get(key), str) and plan_subject_evidence[key].strip(),
                f"planning: subject evidence missing {key}",
            )
        _require(
            isinstance(plan_subject_evidence["commit"], str) and SHA40.fullmatch(plan_subject_evidence["commit"]) is not None,
            "planning: subject evidence commit must be exact 40-hex",
        )
        _require(
            isinstance(plan_subject_evidence["blob"], str) and SHA40.fullmatch(plan_subject_evidence["blob"]) is not None,
            "planning: subject evidence blob must be exact 40-hex",
        )
        _require(
            all(frozen.get(key) == plan_subject_evidence[key] for key in ("repository", "commit", "path", "blob")),
            "planning: frozen_subject does not exactly match durable Git evidence; cannot prove subject",
        )
        _require(
            plan_subject_evidence["path"] == plan_path,
            "planning: proven subject path must equal plan_path; remains Recovery",
        )
        proven_subject = {
            "repository": plan_subject_evidence["repository"],
            "commit": plan_subject_evidence["commit"],
            "path": plan_subject_evidence["path"],
            "blob": plan_subject_evidence["blob"],
        }

    if proven_subject is not None:
        subject: dict[str, str] = proven_subject
        state = "frozen"
        premium_b = "due"
        key = f"{subject['repository']}@{subject['commit']}:{subject['path']}@{subject['blob']}"
        premium_b_subject = key
        premium_c = "not_due"
        premium_c_subject = ""
        preserved = ["exact immutable plan subject proven by durable Git evidence; B due preserved, C still not due"]
        reset = ["B satisfied/C approval never transferred from unprovable legacy state"]
        reason = "Subject provable; frozen with B due requiring fresh independent review"
    else:
        subject = {"repository": "", "commit": "", "path": "", "blob": ""}
        state = "draft"
        premium_b = "not_due"
        premium_b_subject = ""
        premium_c = "not_due"
        premium_c_subject = ""
        preserved = ["entry_subject scope preserved verbatim", "plan_artifact path preserved verbatim"]
        reset = ["immutable subject unprovable without exact Git evidence; B/C reset to not_due, draft requires new freeze/review"]
        reason = "Subject unprovable; B/Plan Review/C must become due again rather than transfer"

    canonical = {
        "workstream_id": workstream_id,
        "cycle": cycle,
        "entry_subject": entry_subject.strip(),
        "revision": canonical_revision,
        "state": state,
        "planner_audit": planner_audit if state == "draft" else "green",
        "plan_path": plan_path,
        "review_mode": review_mode,
        "review_exemption_basis": "",
        "review_exemption_base_subject": "",
        "premium_a": premium_a,
        "premium_a_subject": entry_subject.strip(),
        "premium_b": premium_b,
        "premium_b_subject": premium_b_subject,
        "premium_c": premium_c,
        "premium_c_subject": premium_c_subject,
        "subject": subject,
    }
    # Draft with green audit is valid; frozen requires green audit.
    if state == "draft" and canonical["planner_audit"] not in {"pending", "green"}:
        raise V2ReconciliationError("planning: draft audit invalid")
    try:
        validate_state_record("planning", canonical, workstream_id=workstream_id)
    except ValidationError as exc:
        raise V2ReconciliationError(f"planning: canonical output invalid: {exc}") from exc
    decision = {"preserved": preserved, "reset": reset, "reason": reason}
    return canonical, decision


def canonicalize_workstream(
    legacy: dict[str, Any],
    workstream_id: str,
    created_from_evidence: str | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    _require(isinstance(legacy, dict), "workstream: legacy record must be a table")
    _is_prohibited_shape(legacy, "workstream")
    _require(legacy.get("workstream_id") == workstream_id, "workstream: wrong workstream_id; remains Recovery")
    for key in ("kind", "branch", "integration_target"):
        _require(isinstance(legacy.get(key), str) and legacy[key].strip(), f"workstream: missing {key}")
    _require(legacy["kind"] in {"issue", "feature", "change"}, "workstream: invalid kind; remains Recovery")
    _require(
        isinstance(created_from_evidence, str) and SHA40.fullmatch(created_from_evidence) is not None,
        "workstream: exact created_from commit must be proven by durable Git evidence; cannot synthesize",
    )
    authority = legacy.get("authority")
    _require(isinstance(authority, list) and authority, "workstream: at least one authority locator is required")
    for index, ref in enumerate(authority):
        _require(isinstance(ref, dict) and ref.get("class") == "authority", f"workstream.authority[{index}]: invalid locator")
        _authority_table(ref.get("path"), f"workstream.authority[{index}]")

    canonical: dict[str, Any] = {
        "workstream_id": workstream_id,
        "kind": legacy["kind"],
        "branch": legacy["branch"],
        "created_from": created_from_evidence,
        "integration_target": legacy["integration_target"],
        "authority": [{"class": "authority", "path": ref["path"]} for ref in authority],
        "task_board": {
            "class": "task_board",
            "path": f"implementation/workstreams/{workstream_id}/TASK_BOARD.toml",
        },
    }
    for key in ("intake", "brainstorm", "research", "definition", "planning", "plan_review", "tracker"):
        if key in legacy:
            ref = legacy[key]
            _require(isinstance(ref, dict) and "class" in ref and "path" in ref, f"workstream.{key}: invalid locator")
            canonical[key] = {"class": ref["class"], "path": ref["path"]}
    try:
        validate_state_record("workstream", canonical)
    except ValidationError as exc:
        raise V2ReconciliationError(f"workstream: canonical output invalid: {exc}") from exc
    decision = {
        "preserved": ["stable identity/kind/branch/authority preserved verbatim"],
        "reset": [],
        "reason": "created_from bound only from proven Git evidence; task_board locator constructed deterministically",
    }
    return canonical, decision


def canonicalize_tracker(legacy: dict[str, Any], workstream_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    _require(isinstance(legacy, dict), "tracker: legacy record must be a table")
    _is_prohibited_shape(legacy, "tracker")
    _require(legacy.get("workstream_id") == workstream_id, "tracker: wrong workstream_id; remains Recovery")
    number = legacy.get("number")
    _require(isinstance(number, int) and number > 0, "tracker: legacy number must be a positive integer")
    url = legacy.get("url")
    _require(isinstance(url, str) and url.strip(), "tracker: legacy url must be non-empty")
    matched = _TRACKER_URL.fullmatch(url.strip())
    _require(matched is not None, "tracker: legacy url is not an exact owner/name/issues/N shape; remains Recovery")
    repository = matched.group(1)
    url_number = int(matched.group(2))
    _require(url_number == number, "tracker: legacy number contradicts url; remains Recovery")
    # Never synthesize verified readback from a drifted write. The number is
    # exact bookkeeping context only; correlation requires fresh readback.
    canonical = {
        "workstream_id": workstream_id,
        "provider": "github",
        "repository": repository,
        "dedup_key": f"project-workflow:{workstream_id}",
        "state": "create_pending_readback",
        "issue_number": 0,
        "candidate_issue_numbers": [],
        "readback_state": "uncertain",
        "final_pr": 0,
    }
    try:
        validate_state_record("tracker", canonical, workstream_id=workstream_id)
    except ValidationError as exc:
        raise V2ReconciliationError(f"tracker: canonical output invalid: {exc}") from exc
    decision = {
        "preserved": [f"repository {repository!r} parsed deterministically from exact url; legacy number retained only as readback context"],
        "reset": ["issue correlation reset to create_pending_readback/uncertain; verified link requires fresh exact readback"],
        "reason": "No verified readback proof in drifted source; must not synthesize linked/verified authority",
    }
    return canonical, decision


def canonicalize_task_board(
    legacy: dict[str, Any],
    workstream: dict[str, Any],
    workstream_id: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    _require(isinstance(legacy, dict), "task_board: legacy record must be a table")
    _is_prohibited_shape(legacy, "task_board")
    _require(legacy.get("workstream_id") == workstream_id, "task_board: wrong workstream_id; remains Recovery")
    revision = legacy.get("revision")
    _require(isinstance(revision, int) and revision >= 0, "task_board: revision must be non-negative integer")
    execution_ref = legacy.get("execution_ref")
    _require(isinstance(execution_ref, dict), "task_board: missing execution_ref")
    _require(execution_ref.get("branch") == workstream["branch"], "task_board: wrong original branch; remains Recovery")

    _require("result_path" not in legacy or isinstance(legacy.get("result_path"), str), "task_board: invalid legacy result_path")
    # Top-level result_path/review_requirement are drift markers and are dropped;
    # exact result identity without commit/blob proof must never be inherited.

    cards_raw = legacy.get("cards")
    _require(isinstance(cards_raw, list) and cards_raw, "task_board: cards must be a non-empty array")
    cards: list[dict[str, Any]] = []
    seen: set[str] = set()
    mapped_pending = 0
    for index, card in enumerate(cards_raw):
        label = f"task_board.cards[{index}]"
        _require(isinstance(card, dict), f"{label}: card must be a table")
        card_id = card.get("id")
        _require(isinstance(card_id, str) and card_id.strip(), f"{label}: missing id")
        _require(card_id not in seen, f"{label}: duplicate Card id {card_id!r}")
        seen.add(card_id)
        contract = card.get("contract")
        _require(isinstance(contract, dict) and contract.get("class") == "task_card", f"{label}: invalid contract locator")
        contract_path = contract.get("path")
        _require(
            isinstance(contract_path, str)
            and contract_path.startswith(f"implementation/workstreams/{workstream_id}/cards/")
            and contract_path.endswith(".md"),
            f"{label}: wrong Task Card class/path; remains Recovery",
        )
        status = card.get("status")
        _require(isinstance(status, str) and status, f"{label}: missing status")
        if status == "review_pending":
            # Deterministic safe mapping: awaiting review without exact result
            # proof becomes in_progress requiring correction/review, never done.
            status = "in_progress"
            mapped_pending += 1
        _require(
            status in {"planned", "ready", "in_progress", "blocked", "done"},
            f"{label}: unsupported status {card.get('status')!r}; remains Recovery",
        )
        _require(
            "result" not in card,
            f"{label}: legacy result without exact identity cannot transfer; remains Recovery",
        )
        _require(
            not card.get("review_attempts"),
            f"{label}: review history cannot be rewritten onto a reconciled board without a lawful successor; #26 replacement is out of scope",
        )
        entry: dict[str, Any] = {
            "id": card_id,
            "status": status,
            "contract": {"class": "task_card", "path": contract_path},
        }
        if status == "done":
            raise V2ReconciliationError(f"{label}: done without exact result proof cannot transfer; remains Recovery")
        if status == "blocked":
            _require("blocker" in card, f"{label}: blocked Card requires blocker locator")
            blocker = card["blocker"]
            _require(isinstance(blocker, dict), f"{label}: invalid blocker locator")
            entry["blocker"] = {"class": "blocker", "path": blocker.get("path")}
        elif "blocker" in card:
            blocker = card["blocker"]
            _require(isinstance(blocker, dict), f"{label}: invalid blocker locator")
            entry["blocker"] = {"class": "blocker", "path": blocker.get("path")}
        cards.append(entry)
    _require(mapped_pending >= 1 or "result_path" in legacy or "review_requirement" in legacy,
             "task_board: no evidenced drift marker; remains Recovery")

    canonical: dict[str, Any] = {
        "workstream_id": workstream_id,
        "revision": revision,
        "execution_ref": {"branch": workstream["branch"]},
        "cards": cards,
    }
    for key in ("research_obligation", "jit_triggers"):
        if key in legacy:
            canonical[key] = legacy[key]
    try:
        validate_state_record("task_board", canonical, workstream=workstream)
    except ValidationError as exc:
        raise V2ReconciliationError(f"task_board: canonical output invalid: {exc}") from exc
    decision = {
        "preserved": ["card identity/contract locators preserved verbatim", "revision/execution branch preserved verbatim"],
        "reset": ["review_pending mapped to in_progress; legacy result_path/review_requirement dropped without exact commit/blob proof"],
        "reason": "Changed/unprovable subjects must not inherit result/review authority",
    }
    return canonical, decision


def plan_reconciliation(
    *,
    records: dict[str, dict[str, Any]],
    source_bytes: dict[str, bytes],
    workstream_id: str,
    branch: str,
    created_from_evidence: str | None = None,
    plan_subject_evidence: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Build a complete in-memory reconciliation plan before any mutation.

    Raises :class:`V2ReconciliationError` for any unsupported, ambiguous,
    contradictory or attempt-bound unsafe input. Validates every proposed
    canonical output with the production validators and renders it with the
    shared validated-write boundary (validate -> render -> parse -> validate).
    No filesystem mutation occurs here.
    """
    _require(isinstance(workstream_id, str) and workstream_id.strip(), "reconciliation: workstream_id is required")
    _require(isinstance(branch, str) and branch.strip(), "reconciliation: branch is required")
    profile = detect_profile(records)
    _require(set(records) == set(source_bytes), "reconciliation: records and source bytes must cover the same files")
    source_fingerprint = fingerprint_sources(source_bytes)
    source_file_fingerprints = {name: sha256_hex(source_bytes[name]) for name in sorted(source_bytes)}

    outputs: dict[str, dict[str, Any]] = {}
    decisions: dict[str, dict[str, Any]] = {}
    rendered: dict[str, str] = {}

    if profile == PROFILE_ISSUE20:
        definition, definition_decision = canonicalize_definition(records["DEFINITION.toml"], workstream_id)
        planning, planning_decision = canonicalize_planning(
            records["PLANNING.toml"], workstream_id, definition["revision"], plan_subject_evidence
        )
        outputs = {"DEFINITION.toml": definition, "PLANNING.toml": planning}
        decisions = {"DEFINITION.toml": definition_decision, "PLANNING.toml": planning_decision}
    elif profile == PROFILE_ISSUE22:
        _require(created_from_evidence is not None, "reconciliation: #22 bundle requires created_from Git evidence")
        workstream, workstream_decision = canonicalize_workstream(
            records["WORKSTREAM.toml"], workstream_id, created_from_evidence
        )
        _require(workstream["branch"] == branch, "reconciliation: workstream branch contradicts caller branch")
        definition, definition_decision = canonicalize_definition(records["DEFINITION.toml"], workstream_id)
        planning, planning_decision = canonicalize_planning(
            records["PLANNING.toml"], workstream_id, definition["revision"], plan_subject_evidence
        )
        tracker, tracker_decision = canonicalize_tracker(records["TRACKER.toml"], workstream_id)
        board, board_decision = canonicalize_task_board(records["TASK_BOARD.toml"], workstream, workstream_id)
        outputs = {
            "WORKSTREAM.toml": workstream,
            "DEFINITION.toml": definition,
            "PLANNING.toml": planning,
            "TRACKER.toml": tracker,
            "TASK_BOARD.toml": board,
        }
        decisions = {
            "WORKSTREAM.toml": workstream_decision,
            "DEFINITION.toml": definition_decision,
            "PLANNING.toml": planning_decision,
            "TRACKER.toml": tracker_decision,
            "TASK_BOARD.toml": board_decision,
        }
    else:  # pragma: no cover - detect_profile already fails closed
        raise V2ReconciliationError(f"reconciliation: unsupported profile {profile!r}")

    # Validate + render every output through the shared production boundary.
    contexts: dict[str, dict[str, Any]] = {}
    canonical_workstream = outputs.get("WORKSTREAM.toml")
    for name, data in outputs.items():
        kind = _FILENAME_TO_KIND[name]
        if kind == "workstream":
            context: dict[str, Any] = {}
        elif kind == "task_board":
            _require(canonical_workstream is not None, "reconciliation: task_board requires canonical workstream context")
            context = {"workstream": canonical_workstream}
        else:
            context = {"workstream_id": workstream_id}
        contexts[name] = context
        try:
            text = render_validated_state_record(kind, data, **context)
        except ValidationError as exc:
            raise V2ReconciliationError(f"reconciliation: {name} failed production validation: {exc}") from exc
        rendered[name] = text

    try:
        expected_before = {name: source_bytes[name].decode("utf-8") for name in sorted(source_bytes)}
    except UnicodeDecodeError as exc:
        raise V2ReconciliationError("reconciliation: source bytes are not UTF-8 TOML text") from exc

    return {
        "profile": profile,
        "source_fingerprint": source_fingerprint,
        "source_file_fingerprints": source_file_fingerprints,
        "workstream_id": workstream_id,
        "branch": branch,
        "outputs": outputs,
        "output_text": rendered,
        "expected_before": expected_before,
        "authority_decisions": decisions,
        "validation": {name: "pass" for name in outputs},
    }


def apply_reconciliation_plan(*, plan: dict[str, Any], workdir: Path) -> dict[str, Any]:
    """Apply an exact in-memory plan restart-safely.

    Each affected file must currently contain either the exact expected-before
    bytes or the already-produced after bytes. Unrelated divergence fails
    closed. Reapplying a completed plan is a deterministic no-op. Persistence
    uses only ``write_validated_state_record``.
    """
    _require(isinstance(plan, dict), "reconciliation: plan must be a mapping")
    profile = plan.get("profile")
    _require(profile in SUPPORTED_PROFILES, f"reconciliation: unsupported plan profile {profile!r}")
    outputs = plan.get("outputs")
    output_text = plan.get("output_text")
    expected_before = plan.get("expected_before")
    _require(isinstance(outputs, dict) and outputs, "reconciliation: plan has no outputs")
    _require(isinstance(output_text, dict) and set(output_text) == set(outputs), "reconciliation: plan output text mismatch")
    _require(isinstance(expected_before, dict) and set(expected_before) == set(outputs), "reconciliation: plan before-state mismatch")
    _require(isinstance(workdir, Path), "reconciliation: workdir must be a Path")
    _require(workdir.is_dir(), f"reconciliation: workdir {workdir} is not a directory")

    # Verify the plan fingerprint is internally consistent before touching disk.
    _require(
        isinstance(plan.get("source_fingerprint"), str) and SHA64.fullmatch(plan["source_fingerprint"]) is not None,
        "reconciliation: plan source fingerprint is missing or invalid",
    )
    recomputed = fingerprint_sources({name: expected_before[name].encode("utf-8") for name in expected_before})
    _require(
        recomputed == plan["source_fingerprint"],
        "reconciliation: plan source fingerprint does not match expected-before bytes",
    )

    workstream_id = plan.get("workstream_id")
    _require(isinstance(workstream_id, str) and workstream_id, "reconciliation: plan workstream_id is required")
    canonical_workstream = outputs.get("WORKSTREAM.toml")

    applied: list[str] = []
    noop: list[str] = []
    for name in sorted(outputs):
        target = workdir / name
        current = target.read_text(encoding="utf-8") if target.is_file() else None
        before = expected_before[name]
        after = output_text[name]
        if current == after:
            noop.append(name)
            continue
        if current != before:
            raise V2ReconciliationError(
                f"reconciliation: source divergence detected for {name}; expected exact before-state or already-applied after-state"
            )
        kind = _FILENAME_TO_KIND[name]
        if kind == "workstream":
            context = {}
        elif kind == "task_board":
            _require(canonical_workstream is not None, "reconciliation: task_board requires canonical workstream context")
            context = {"workstream": canonical_workstream}
        else:
            context = {"workstream_id": workstream_id}
        try:
            written = write_validated_state_record(target, kind, outputs[name], **context)
        except ValidationError as exc:
            raise V2ReconciliationError(f"reconciliation: validated write failed for {name}: {exc}") from exc
        _require(written == after, f"reconciliation: non-deterministic render for {name}")
        applied.append(name)

    status = "noop" if not applied else "applied"
    return {
        "status": status,
        "profile": profile,
        "source_fingerprint": plan["source_fingerprint"],
        "applied": applied,
        "noop": noop,
    }
