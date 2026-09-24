#!/usr/bin/env python3
"""Executable M01 Project Workflow V2 state-envelope contract."""

from __future__ import annotations

import argparse
import re
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from tools.review_contract import REVIEW_KINDS, review_kind
except ModuleNotFoundError:  # direct script execution from tools/
    from review_contract import REVIEW_KINDS, review_kind

SHA40 = re.compile(r"^[0-9a-f]{40}$")
CARD_STATUSES = {"planned", "ready", "in_progress", "blocked", "done"}
INTAKE_KINDS = {"issue", "feature", "change"}
INTAKE_STATES = {"active", "complete"}
RESPONSE_KINDS = {"none", "question", "concern", "alternative", "authorization"}
ALIGNMENT_STATES = {"not_required", "pending", "authorized"}
BRAINSTORM_STATES = {"active", "ready_for_definition", "promoted"}
AUDIT_STATES = {"pending", "green"}
PROMOTION_STATES = {"pending", "authorized"}
RESEARCH_STATES = {"active", "complete", "consumed"}
RESEARCH_RETURN_TARGETS = {"intake", "brainstorming", "definition"}
EXECUTION_RESEARCH_ORIGIN_ROLES = {"execution_prep", "execution", "execution_resolution"}
BLOCKER_CLASSES = {"missing_evidence", "human_authority", "runtime_access_input"}
RESEARCH_SOURCE_CLASSES = {
    "official_upstream",
    "project_runtime",
    "tracker_discussion",
    "practitioner_community",
}
RESEARCH_SOURCE_STATUSES = {"pending", "checked", "not_relevant", "unavailable"}
RETURN_RECONCILIATION_STATES = {"pending", "applied"}
DEFINITION_STATES = {"active", "green"}
PREMIUM_A_STATES = {"not_due", "due", "satisfied"}
PLANNING_STATES = {"draft", "frozen", "approved"}
PLANNING_REVIEW_MODES = {"independent", "editorial_exempt"}
PREMIUM_GATE_STATES = {"not_due", "due", "satisfied"}
TRACKER_STATES = {"discovery", "create_pending_readback", "linked", "ambiguous", "unavailable"}
TRACKER_READBACK_STATES = {"pending", "verified", "uncertain", "not_applicable"}
JIT_TRIGGER_STATES = {"waiting", "satisfied", "consumed"}
TASK_CARD_REVIEW_REQUIREMENTS = {"none", "required", "recommended"}
PROHIBITED_KEY_PREFIXES = ("runtime_", "model_", "session_", "worker_", "batch_", "lane_", "scheduler_", "context_health_")
PROHIBITED_KEYS = {
    "execution_policy",
    "runtime",
    "model",
    "session",
    "worker",
    "worker_id",
    "orchestration_binding",
    "active_execution",
    "returned",
    "transfer_ready",
    "batch",
    "lane",
    "lanes",
    "scheduler",
    "context_health",
}


class ValidationError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def read_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        value = tomllib.load(handle)
    _require(isinstance(value, dict), f"{path}: top-level TOML must be a table")
    return value


def read_project(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    _require(lines and lines[0] == "+++", f"{path}: missing TOML front matter")
    try:
        end = lines.index("+++", 1)
    except ValueError as exc:
        raise ValidationError(f"{path}: unterminated TOML front matter") from exc
    return tomllib.loads("\n".join(lines[1:end]))


def reject_prohibited_keys(value: Any, where: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower()
            _require(normalized not in PROHIBITED_KEYS and not normalized.startswith(PROHIBITED_KEY_PREFIXES),
                     f"{where}: prohibited canonical key {key!r}")
            reject_prohibited_keys(child, f"{where}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_prohibited_keys(child, f"{where}[{index}]")


def _safe_relative_path(raw: Any, label: str) -> str:
    _require(isinstance(raw, str) and raw, f"{label}: path must be non-empty string")
    path = PurePosixPath(raw)
    _require(not path.is_absolute(), f"{label}: absolute paths are not durable artifact locators")
    _require(".." not in path.parts and "." not in path.parts, f"{label}: path traversal is forbidden")
    return raw


def validate_locator(
    ref: Any,
    expected_class: str,
    label: str,
    workstream_id: str | None = None,
) -> str:
    _require(isinstance(ref, dict), f"{label}: locator must be a table")
    _require(ref.get("class") == expected_class, f"{label}: expected class {expected_class!r}")
    path = _safe_relative_path(ref.get("path"), label)

    if expected_class == "task_board":
        _require(workstream_id is not None, f"{label}: workstream binding required")
        expected = f"implementation/workstreams/{workstream_id}/TASK_BOARD.toml"
        _require(path == expected, f"{label}: expected exact path {expected!r}")
    elif expected_class == "task_card":
        _require(workstream_id is not None, f"{label}: workstream binding required")
        prefix = f"implementation/workstreams/{workstream_id}/cards/"
        _require(path.startswith(prefix) and path.endswith(".md"), f"{label}: wrong Task Card class/path")
    elif expected_class in {"intake", "brainstorm", "research", "definition", "planning", "plan_review", "tracker"}:
        _require(workstream_id is not None, f"{label}: workstream binding required")
        filenames = {
            "intake": "INTAKE.toml",
            "brainstorm": "BRAINSTORM.toml",
            "research": "RESEARCH.toml",
            "definition": "DEFINITION.toml",
            "planning": "PLANNING.toml",
            "plan_review": "PLAN_REVIEW.toml",
            "tracker": "TRACKER.toml",
        }
        expected = f"implementation/workstreams/{workstream_id}/{filenames[expected_class]}"
        _require(path == expected, f"{label}: expected exact path {expected!r}")
    elif expected_class == "review_attempt":
        _require(workstream_id is not None, f"{label}: workstream binding required")
        prefix = f"implementation/workstreams/{workstream_id}/reviews/"
        _require(path.startswith(prefix) and path.endswith(".toml"),
                 f"{label}: wrong review_attempt class/path")
    elif expected_class in {"evidence", "result"}:
        _require(workstream_id is not None, f"{label}: workstream binding required")
        directory = "evidence" if expected_class == "evidence" else "results"
        prefix = f"implementation/workstreams/{workstream_id}/{directory}/"
        _require(path.startswith(prefix) and path.endswith(".md"), f"{label}: wrong {expected_class} class/path")
        if expected_class == "result" and ("commit" in ref or "blob" in ref):
            _require(
                isinstance(ref.get("commit"), str) and SHA40.fullmatch(ref["commit"]) is not None
                and isinstance(ref.get("blob"), str) and SHA40.fullmatch(ref["blob"]) is not None,
                f"{label}: exact result identity requires commit + blob 40-hex",
            )
    elif expected_class == "blocker":
        _require(workstream_id is not None, f"{label}: workstream binding required")
        prefix = f"implementation/workstreams/{workstream_id}/blockers/"
        _require(path.startswith(prefix) and path.endswith(".toml"),
                 f"{label}: wrong blocker class/path")
    elif expected_class == "authority":
        allowed = ("requirements/", "decisions/", "planning/", "workflow/")
        _require(path.startswith(allowed), f"{label}: authority path is outside accepted authority roots")
    else:
        raise ValidationError(f"{label}: unsupported locator class {expected_class!r}")
    return path


def validate_project(data: dict[str, Any]) -> None:
    reject_prohibited_keys(data, "project")
    _require(data.get("project_workflow") == "v2", "project: project_workflow must be 'v2'")
    for key in ("project_id", "repository", "workstream_root"):
        _require(isinstance(data.get(key), str) and data[key], f"project: missing {key}")
    _require(data["workstream_root"] == "implementation/workstreams", "project: unsupported workstream_root")


def validate_workstream(data: dict[str, Any]) -> None:
    reject_prohibited_keys(data, "workstream")
    for key in ("workstream_id", "kind", "branch", "integration_target"):
        _require(isinstance(data.get(key), str) and data[key], f"workstream: missing {key}")
    _require(isinstance(data.get("created_from"), str) and SHA40.fullmatch(data["created_from"]) is not None,
             "workstream: created_from must be exact 40-hex commit")
    authority = data.get("authority")
    _require(isinstance(authority, list) and authority, "workstream: at least one exact authority locator is required")
    for index, ref in enumerate(authority):
        validate_locator(ref, "authority", f"workstream.authority[{index}]")
    locator_classes = {
        "task_board": "task_board",
        "intake": "intake",
        "brainstorm": "brainstorm",
        "research": "research",
        "definition": "definition",
        "planning": "planning",
        "plan_review": "plan_review",
        "tracker": "tracker",
    }
    present = [key for key in locator_classes if key in data]
    _require(present,
             "workstream: at least one concrete workstream-local state locator is required")
    for key in present:
        validate_locator(data[key], locator_classes[key], f"workstream.{key}", data["workstream_id"])


def validate_intake(data: dict[str, Any], workstream_id: str) -> None:
    reject_prohibited_keys(data, "intake")
    _require(data.get("workstream_id") == workstream_id, "intake: wrong workstream_id")
    kind = data.get("kind")
    _require(kind in INTAKE_KINDS, f"intake: invalid kind {kind!r}")
    state = data.get("state")
    _require(state in INTAKE_STATES, f"intake: invalid state {state!r}")
    _require(isinstance(data.get("diagnosis_revision"), int) and data["diagnosis_revision"] >= 0,
             "intake: diagnosis_revision must be non-negative integer")
    repair_subject = data.get("repair_subject")
    _require(isinstance(repair_subject, str), "intake: repair_subject must be a string")
    diagnosis_prior_art_subject = data.get("diagnosis_prior_art_subject")
    diagnosis_prior_art_result = data.get("diagnosis_prior_art_result")
    _require(isinstance(diagnosis_prior_art_subject, str),
             "intake: diagnosis_prior_art_subject must be a string")
    _require(isinstance(diagnosis_prior_art_result, str),
             "intake: diagnosis_prior_art_result must be a string")
    response_kind = data.get("response_kind")
    _require(response_kind in RESPONSE_KINDS, f"intake: invalid response_kind {response_kind!r}")
    response_observed = data.get("response_observed")
    _require(isinstance(response_observed, bool), "intake: response_observed must be boolean")
    _require(response_observed == (response_kind != "none"),
             "intake: response_observed must match response_kind")
    alignment_state = data.get("alignment_state")
    _require(alignment_state in ALIGNMENT_STATES, f"intake: invalid alignment_state {alignment_state!r}")
    alignment_subject = data.get("alignment_subject")
    _require(isinstance(alignment_subject, str), "intake: alignment_subject must be a string")
    micro_fix_candidate = data.get("micro_fix_candidate")
    _require(isinstance(micro_fix_candidate, bool), "intake: micro_fix_candidate must be boolean")

    if kind == "issue":
        _require(alignment_state != "not_required", "intake: issue alignment cannot be not_required")
        if diagnosis_prior_art_subject or diagnosis_prior_art_result:
            _require(bool(diagnosis_prior_art_subject.strip()) and bool(diagnosis_prior_art_result.strip()),
                     "intake: diagnosis prior-art binding requires exact subject and result")
            _require(diagnosis_prior_art_subject == repair_subject,
                     "intake: stale diagnosis prior-art subject for current repair_subject")
        if alignment_state == "pending":
            _require(alignment_subject == "", "intake: pending alignment must not retain an authorized subject")
            _require(not micro_fix_candidate, "intake: micro-fix candidate requires exact issue authorization")
            _require(state != "complete", "intake: issue cannot complete while alignment is pending")
        else:
            _require(response_observed and response_kind == "authorization",
                     "intake: authorized issue requires an explicit authorization response")
            _require(bool(repair_subject), "intake: authorized issue requires repair_subject")
            _require(alignment_subject == repair_subject,
                     "intake: authorized alignment subject is stale for current repair_subject")
            _require(
                diagnosis_prior_art_subject == repair_subject and bool(diagnosis_prior_art_result.strip()),
                "intake: authorized issue requires exact durable diagnosis prior-art binding",
            )
    else:
        _require(alignment_state == "not_required",
                 "intake: feature/change discovery must not manufacture issue-repair alignment")
        _require(alignment_subject == "", "intake: non-issue alignment_subject must be empty")
        _require(diagnosis_prior_art_subject == "" and diagnosis_prior_art_result == "",
                 "intake: non-issue must not retain diagnosis prior-art binding")
        _require(not micro_fix_candidate, "intake: micro-fix candidate is issue-only")

    if state == "complete" and kind == "issue":
        _require(alignment_state == "authorized", "intake: completed issue requires exact authorization")


def validate_brainstorm(data: dict[str, Any], workstream_id: str) -> None:
    reject_prohibited_keys(data, "brainstorm")
    _require(data.get("workstream_id") == workstream_id, "brainstorm: wrong workstream_id")
    _require(isinstance(data.get("scope_id"), str) and data["scope_id"].strip(),
             "brainstorm: missing scope_id")
    _require(isinstance(data.get("revision"), int) and data["revision"] >= 1,
             "brainstorm: revision must be positive integer")
    state = data.get("state")
    _require(state in BRAINSTORM_STATES, f"brainstorm: invalid state {state!r}")
    challenge = data.get("challenge_audit")
    _require(challenge in AUDIT_STATES, f"brainstorm: invalid challenge_audit {challenge!r}")
    explicit_user_stop = data.get("explicit_user_stop")
    _require(isinstance(explicit_user_stop, bool), "brainstorm: explicit_user_stop must be boolean")
    promotion_state = data.get("promotion_state")
    _require(promotion_state in PROMOTION_STATES, f"brainstorm: invalid promotion_state {promotion_state!r}")
    promotion_subject = data.get("promotion_subject")
    _require(isinstance(promotion_subject, str), "brainstorm: promotion_subject must be a string")
    exact_subject = f"{data['scope_id']}@{data['revision']}"

    if state in {"ready_for_definition", "promoted"}:
        _require(challenge == "green", "brainstorm: Definition readiness requires GREEN challenge audit")
    if promotion_state == "pending":
        _require(promotion_subject == "", "brainstorm: pending promotion must not retain a subject")
    else:
        _require(challenge == "green", "brainstorm: promotion authorization requires GREEN challenge audit")
        _require(promotion_subject == exact_subject,
                 "brainstorm: promotion authorization is stale for current scope revision")
    if state == "promoted":
        _require(promotion_state == "authorized",
                 "brainstorm: promoted state requires exact user authorization")


def validate_research(data: dict[str, Any], workstream_id: str) -> None:
    reject_prohibited_keys(data, "research")
    _require(data.get("workstream_id") == workstream_id, "research: wrong workstream_id")
    state = data.get("state")
    _require(state in RESEARCH_STATES, f"research: invalid state {state!r}")
    origin_role = data.get("origin_role")
    _require(
        origin_role in {"intake", "brainstorming", "definition"} | EXECUTION_RESEARCH_ORIGIN_ROLES,
        "research: invalid origin_role",
    )
    _require(isinstance(data.get("origin_subject"), str) and data["origin_subject"].strip(),
             "research: missing origin_subject")
    return_target = data.get("return_target")
    execution_return = isinstance(return_target, str) and (
        return_target.startswith("execution_resolution:")
        or return_target.startswith("execution_prep:")
        or return_target.startswith("execution:")
    )
    _require(return_target in RESEARCH_RETURN_TARGETS or execution_return,
             f"research: invalid return_target {return_target!r}")
    reconciliation = data.get("return_reconciliation")
    _require(reconciliation in RETURN_RECONCILIATION_STATES,
             f"research: invalid return_reconciliation {reconciliation!r}")
    return_result = data.get("return_result")
    _require(isinstance(return_result, str), "research: return_result must be a string")
    finding = data.get("finding")
    limitations = data.get("limitations")
    conflicts = data.get("conflicts")
    _require(isinstance(finding, str), "research: finding must be a string")
    _require(isinstance(limitations, str), "research: limitations must be a string")
    _require(isinstance(conflicts, str), "research: conflicts must be a string")

    sources = data.get("sources")
    _require(isinstance(sources, list), "research: sources must be an array")
    seen: set[str] = set()
    for index, source in enumerate(sources):
        label = f"research.sources[{index}]"
        _require(isinstance(source, dict), f"{label}: source must be table")
        source_class = source.get("class")
        _require(source_class in RESEARCH_SOURCE_CLASSES, f"{label}: invalid class {source_class!r}")
        _require(source_class not in seen, f"{label}: duplicate source class {source_class!r}")
        seen.add(source_class)
        _require(source.get("status") in RESEARCH_SOURCE_STATUSES,
                 f"{label}: invalid status {source.get('status')!r}")
        _require(isinstance(source.get("weight"), str) and source["weight"].strip(),
                 f"{label}: weight must be non-empty")
    _require(seen == RESEARCH_SOURCE_CLASSES,
             "research: all proportional prior-art source classes must be accounted for")

    if state in {"complete", "consumed"}:
        _require(bool(finding.strip()), "research: completed Research requires a finding")
        _require(bool(conflicts.strip()), "research: completed Research requires explicit conflict accounting")
        _require(all(source["status"] != "pending" for source in sources),
                 "research: completed Research cannot leave a source class pending")
    if reconciliation == "applied":
        _require(bool(return_result.strip()), "research: applied return requires exact return_result")
    else:
        _require(return_result == "", "research: pending return reconciliation must not retain result")
    if state == "active":
        _require(reconciliation == "pending", "research: active Research cannot have applied return")
    if state == "consumed":
        _require(reconciliation == "applied", "research: consumed Research requires applied return")


def validate_definition(data: dict[str, Any], workstream_id: str) -> None:
    reject_prohibited_keys(data, "definition")
    _require(data.get("workstream_id") == workstream_id, "definition: wrong workstream_id")
    _require(isinstance(data.get("source_scope_subject"), str) and data["source_scope_subject"].strip(),
             "definition: missing source_scope_subject")
    _require(isinstance(data.get("revision"), str) and data["revision"].strip(),
             "definition: missing revision")
    state = data.get("state")
    _require(state in DEFINITION_STATES, f"definition: invalid state {state!r}")
    audit = data.get("completeness_audit")
    _require(audit in AUDIT_STATES, f"definition: invalid completeness_audit {audit!r}")
    premium_a = data.get("premium_a")
    _require(premium_a in PREMIUM_A_STATES, f"definition: invalid premium_a {premium_a!r}")
    validate_locator(data.get("requirements"), "authority", "definition.requirements")
    decisions = data.get("decisions")
    _require(isinstance(decisions, list), "definition: decisions must be an array")
    for index, decision in enumerate(decisions):
        validate_locator(decision, "authority", f"definition.decisions[{index}]")

    if state == "active":
        _require(premium_a == "not_due", "definition: premium A cannot be due before Definition GREEN")
    else:
        _require(audit == "green", "definition: GREEN state requires GREEN completeness audit")
        _require(decisions, "definition: GREEN state requires accepted decision authority")
        _require(premium_a in {"due", "satisfied"},
                 "definition: GREEN state requires premium stop A due or satisfied")


def _git_blob_subject_key(subject: Any, label: str) -> str:
    _require(isinstance(subject, dict), f"{label}: subject must be a table")
    repository = subject.get("repository")
    path = subject.get("path")
    commit = subject.get("commit")
    blob = subject.get("blob")
    _require(isinstance(repository, str) and repository.strip(), f"{label}: missing repository")
    _require(isinstance(path, str) and path.strip(), f"{label}: missing path")
    _safe_relative_path(path, label)
    _require(isinstance(commit, str) and SHA40.fullmatch(commit) is not None,
             f"{label}: commit must be exact 40-hex")
    _require(isinstance(blob, str) and SHA40.fullmatch(blob) is not None,
             f"{label}: blob must be exact 40-hex")
    return f"{repository}@{commit}:{path}@{blob}"


def validate_planning(data: dict[str, Any], workstream_id: str) -> None:
    reject_prohibited_keys(data, "planning")
    _require(data.get("workstream_id") == workstream_id, "planning: wrong workstream_id")
    cycle = data.get("cycle")
    _require(isinstance(cycle, int) and cycle >= 1, "planning: cycle must be positive integer")
    entry_subject = data.get("entry_subject")
    _require(isinstance(entry_subject, str) and entry_subject.strip(), "planning: missing entry_subject")
    revision = data.get("revision")
    _require(isinstance(revision, str) and revision.strip(), "planning: missing revision")
    state = data.get("state")
    _require(state in PLANNING_STATES, f"planning: invalid state {state!r}")
    audit = data.get("planner_audit")
    _require(audit in AUDIT_STATES, f"planning: invalid planner_audit {audit!r}")
    plan_path = _safe_relative_path(data.get("plan_path"), "planning.plan_path")
    _require(plan_path.startswith("planning/") and plan_path.endswith(".md"),
             "planning: plan_path must be a planning Markdown artifact")

    review_mode = data.get("review_mode")
    _require(review_mode in PLANNING_REVIEW_MODES, f"planning: invalid review_mode {review_mode!r}")
    exemption_basis = data.get("review_exemption_basis")
    exemption_base_subject = data.get("review_exemption_base_subject")
    _require(isinstance(exemption_basis, str), "planning: review_exemption_basis must be a string")
    _require(isinstance(exemption_base_subject, str),
             "planning: review_exemption_base_subject must be a string")
    if review_mode == "independent":
        _require(exemption_basis == "" and exemption_base_subject == "",
                 "planning: independent review mode must not claim an editorial exemption")
    else:
        _require(bool(exemption_basis.strip()),
                 "planning: editorial exemption requires a bounded semantic basis")
        _require(bool(exemption_base_subject.strip()),
                 "planning: editorial exemption requires the prior reviewed subject")

    premium_a = data.get("premium_a")
    premium_b = data.get("premium_b")
    premium_c = data.get("premium_c")
    for name, value in (("premium_a", premium_a), ("premium_b", premium_b), ("premium_c", premium_c)):
        _require(value in PREMIUM_GATE_STATES, f"planning: invalid {name} {value!r}")
    premium_a_subject = data.get("premium_a_subject")
    premium_b_subject = data.get("premium_b_subject")
    premium_c_subject = data.get("premium_c_subject")
    for name, value in (
        ("premium_a_subject", premium_a_subject),
        ("premium_b_subject", premium_b_subject),
        ("premium_c_subject", premium_c_subject),
    ):
        _require(isinstance(value, str), f"planning: {name} must be a string")

    _require(premium_a in {"due", "satisfied"} and premium_a_subject == entry_subject,
             "planning: current cycle requires exact premium A gate subject")

    subject = data.get("subject")
    if state == "draft":
        _require(review_mode == "independent",
                 "planning: editorial exemption applies only to a previously approved cycle")
        _require(isinstance(subject, dict), "planning: draft subject table is required")
        _require(all(subject.get(key, "") == "" for key in ("repository", "commit", "path", "blob")),
                 "planning: draft must not claim a frozen immutable subject")
        _require(premium_b == "not_due" and premium_b_subject == "",
                 "planning: premium B is not due before freeze")
        _require(premium_c == "not_due" and premium_c_subject == "",
                 "planning: premium C is not due before approval")
        return

    _require(premium_a == "satisfied",
             "planning: frozen/approved plan requires premium A satisfied for the current cycle")
    subject_key = _git_blob_subject_key(subject, "planning.subject")
    _require(subject["path"] == plan_path, "planning: frozen subject path must equal plan_path")
    _require(audit == "green", "planning: frozen/approved plan requires GREEN planner audit")

    if review_mode == "editorial_exempt":
        _require(state == "approved",
                 "planning: editorial exemption is only valid on an already approved planning cycle")
        _require(subject_key != exemption_base_subject,
                 "planning: editorial exemption requires a changed plan subject")
        _require(premium_b == "satisfied" and premium_b_subject == exemption_base_subject,
                 "planning: editorial exemption must preserve prior reviewed premium B subject")
        _require(premium_c == "satisfied" and premium_c_subject == exemption_base_subject,
                 "planning: editorial exemption must preserve prior satisfied premium C subject")
        return

    _require(premium_b in {"due", "satisfied"} and premium_b_subject == subject_key,
             "planning: frozen subject requires exact premium B gate subject")
    if state == "frozen":
        _require(premium_c == "not_due" and premium_c_subject == "",
                 "planning: premium C cannot be due before GREEN Plan Review consumption")
    else:
        _require(premium_b == "satisfied",
                 "planning: approved plan requires premium B satisfied")
        _require(premium_c in {"due", "satisfied"} and premium_c_subject == subject_key,
                 "planning: approved plan requires exact premium C gate subject")


def validate_plan_review(data: dict[str, Any], workstream_id: str, planning: dict[str, Any]) -> None:
    validate_review(data)
    _require(data.get("workstream_id") == workstream_id, "plan_review: wrong workstream_id")
    _require(data.get("plan_revision") == planning.get("revision"),
             "plan_review: wrong plan_revision")
    _require(data.get("planning_cycle") == planning.get("cycle"),
             "plan_review: wrong planning_cycle")
    _require(planning.get("state") in {"frozen", "approved"},
             "plan_review: planning subject must be frozen")
    review_key = _git_blob_subject_key(data.get("subject"), "plan_review.subject")
    planning_key = _git_blob_subject_key(planning.get("subject"), "planning.subject")
    if planning.get("review_mode") == "editorial_exempt":
        _require(data.get("verdict") == "green",
                 "plan_review: editorial exemption requires prior GREEN review coverage")
        _require(review_key == planning.get("review_exemption_base_subject"),
                 "plan_review: editorial exemption base does not match prior reviewed subject")
    else:
        _require(review_key == planning_key, "plan_review: subject does not match frozen plan")
    evidence_path = data.get("evidence_path")
    _require(isinstance(evidence_path, str), "plan_review: evidence_path must be a string")
    if data.get("verdict") in {"green", "red"}:
        _require(bool(evidence_path.strip()), "plan_review: terminal verdict requires evidence_path")
        _safe_relative_path(evidence_path, "plan_review.evidence_path")
    else:
        _require(evidence_path == "", "plan_review: pending attempt must not claim evidence")


def validate_tracker(data: dict[str, Any], workstream_id: str) -> None:
    reject_prohibited_keys(data, "tracker")
    _require(data.get("workstream_id") == workstream_id, "tracker: wrong workstream_id")
    _require(data.get("provider") == "github", "tracker: provider must be github")
    repository = data.get("repository")
    _require(
        isinstance(repository, str)
        and repository.count("/") == 1
        and all(part.strip() for part in repository.split("/", 1)),
        "tracker: repository must be exact owner/name",
    )
    dedup_key = data.get("dedup_key")
    _require(isinstance(dedup_key, str) and dedup_key.strip(), "tracker: missing dedup_key")
    state = data.get("state")
    _require(state in TRACKER_STATES, f"tracker: invalid state {state!r}")
    issue_number = data.get("issue_number")
    _require(isinstance(issue_number, int) and issue_number >= 0,
             "tracker: issue_number must be non-negative integer")
    candidates = data.get("candidate_issue_numbers")
    _require(isinstance(candidates, list), "tracker: candidate_issue_numbers must be an array")
    _require(
        all(isinstance(number, int) and number > 0 for number in candidates)
        and len(set(candidates)) == len(candidates),
        "tracker: candidate Issue numbers must be unique positive integers",
    )
    readback = data.get("readback_state")
    _require(readback in TRACKER_READBACK_STATES, f"tracker: invalid readback_state {readback!r}")
    final_pr = data.get("final_pr")
    _require(isinstance(final_pr, int) and final_pr >= 0,
             "tracker: final_pr must be non-negative integer")

    forbidden_authority = {
        "authorization",
        "repair_authorized",
        "implementation_authorized",
        "requirements_approved",
        "plan_approved",
    }
    _require(
        not (forbidden_authority & set(data)),
        "tracker: GitHub Issue bookkeeping must not carry workflow authorization/approval",
    )

    if state == "discovery":
        _require(issue_number == 0 and not candidates and readback == "pending",
                 "tracker: discovery must not claim an Issue or completed readback")
    elif state == "create_pending_readback":
        _require(issue_number == 0 and not candidates and readback in {"pending", "uncertain"},
                 "tracker: pending create must require readback before retry")
    elif state == "linked":
        _require(issue_number > 0 and not candidates and readback == "verified",
                 "tracker: linked Issue requires one positive Issue number and verified readback")
    elif state == "ambiguous":
        _require(issue_number == 0 and len(candidates) >= 2 and readback == "uncertain",
                 "tracker: ambiguous recovery requires multiple candidates and uncertain readback")
    else:
        _require(issue_number == 0 and not candidates and readback == "not_applicable",
                 "tracker: unavailable capability must not claim Issue state")

    if final_pr > 0:
        _require(state == "linked", "tracker: final PR correlation requires a linked Issue")


def parse_task_card(text: str, expected_id: str, workstream_id: str) -> dict[str, Any]:
    """Parse the stable Markdown Task Card fields needed for launch readiness."""
    wanted = {
        "card id",
        "included scope",
        "excluded scope",
        "authority refs",
        "dependencies",
        "acceptance",
        "required tests/readback",
        "review requirement",
        "technical contract",
    }
    fields: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("- ") or ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        normalized = key.strip().lower()
        if normalized in wanted:
            _require(normalized not in fields, f"task_card: duplicate field {key!r}")
            fields[normalized] = value.strip()

    missing = sorted(wanted - set(fields))
    _require(not missing, f"task_card: missing stable field(s): {', '.join(missing)}")
    for key, value in fields.items():
        _require(value and "<" not in value and ">" not in value,
                 f"task_card: unresolved field {key!r}")

    _require(fields["card id"] == expected_id, "task_card: Card ID does not match Task Board")

    authority_refs = [part.strip() for part in fields["authority refs"].split(",") if part.strip()]
    _require(authority_refs and authority_refs != ["none"], "task_card: at least one authority ref is required")
    for index, raw in enumerate(authority_refs):
        path = _safe_relative_path(raw, f"task_card.authority_refs[{index}]")
        _require(path.startswith(("requirements/", "decisions/", "planning/", "workflow/")),
                 f"task_card.authority_refs[{index}]: outside accepted authority roots")

    dependencies: list[dict[str, str]] = []
    if fields["dependencies"].lower() != "none":
        raw_dependencies = [part.strip() for part in fields["dependencies"].split(",") if part.strip()]
        _require(raw_dependencies, "task_card: dependencies must be exact result refs or none")
        expected_prefix = f"implementation/workstreams/{workstream_id}/results/"
        for index, raw in enumerate(raw_dependencies):
            matched = re.fullmatch(r"(.+)@([0-9a-f]{40}):([0-9a-f]{40})", raw)
            _require(matched is not None,
                     f"task_card.dependencies[{index}]: exact result ref must be path@commit:blob")
            path = _safe_relative_path(matched.group(1), f"task_card.dependencies[{index}]")
            _require(path.startswith(expected_prefix) and path.endswith(".md"),
                     f"task_card.dependencies[{index}]: must be exact workstream result ref")
            dependencies.append({
                "path": path,
                "commit": matched.group(2),
                "blob": matched.group(3),
            })

    review_requirement = fields["review requirement"].lower()
    _require(review_requirement in TASK_CARD_REVIEW_REQUIREMENTS,
             "task_card: invalid review requirement")

    technical_contract: str | None = None
    if fields["technical contract"].lower() != "none":
        technical_contract = _safe_relative_path(fields["technical contract"], "task_card.technical_contract")
        _require(technical_contract.startswith(("openspec/", "contracts/")),
                 "task_card: technical contract must use openspec/ or contracts/ when present")

    return {
        "card_id": expected_id,
        "authority_refs": authority_refs,
        "dependencies": dependencies,
        "review_requirement": review_requirement,
        "technical_contract": technical_contract,
    }


def validate_board(
    data: dict[str, Any],
    workstream: dict[str, Any],
    expected_revision: int | None = None,
) -> None:
    reject_prohibited_keys(data, "task_board")
    _require(data.get("workstream_id") == workstream["workstream_id"], "task_board: wrong workstream_id")
    _require(isinstance(data.get("revision"), int) and data["revision"] >= 0, "task_board: revision must be non-negative integer")
    if expected_revision is not None:
        _require(data["revision"] == expected_revision,
                 f"task_board: stale expected revision {expected_revision}; current is {data['revision']}")
    execution_ref = data.get("execution_ref")
    _require(isinstance(execution_ref, dict), "task_board: missing execution_ref")
    _require(execution_ref.get("branch") == workstream["branch"], "task_board: wrong original branch")

    cards = data.get("cards")
    _require(isinstance(cards, list), "task_board: cards must be an array")
    ids: set[str] = set()
    active = 0
    for index, card in enumerate(cards):
        label = f"task_board.cards[{index}]"
        _require(isinstance(card, dict), f"{label}: card must be table")
        card_id = card.get("id")
        _require(isinstance(card_id, str) and card_id, f"{label}: missing id")
        _require(card_id not in ids, f"{label}: duplicate Card id {card_id!r}")
        ids.add(card_id)
        status = card.get("status")
        _require(status in CARD_STATUSES, f"{label}: invalid status {status!r}")
        active += int(status == "in_progress")
        validate_locator(card.get("contract"), "task_card", f"{label}.contract", workstream["workstream_id"])
        if "result" in card:
            validate_locator(card["result"], "result", f"{label}.result", workstream["workstream_id"])
        attempts = card.get("review_attempts", [])
        _require(isinstance(attempts, list), f"{label}: review_attempts must be an array")
        attempt_paths: set[str] = set()
        for attempt_index, attempt_ref in enumerate(attempts):
            attempt_path = validate_locator(
                attempt_ref,
                "review_attempt",
                f"{label}.review_attempts[{attempt_index}]",
                workstream["workstream_id"],
            )
            _require(attempt_path not in attempt_paths,
                     f"{label}: duplicate review attempt locator {attempt_path!r}")
            attempt_paths.add(attempt_path)
        if status == "done":
            _require("result" in card, f"{label}: done Card requires an exact result locator")
    _require(active <= 1, "task_board: more than one Project Workflow Card is in_progress")

    research_obligation = data.get("research_obligation")
    if research_obligation is not None:
        validate_locator(
            research_obligation,
            "research",
            "task_board.research_obligation",
            workstream["workstream_id"],
        )

    for index, card in enumerate(cards):
        if card["status"] == "blocked":
            _require("blocker" in card, f"task_board.cards[{index}]: blocked Card requires blocker locator")
        if "blocker" in card:
            validate_locator(
                card["blocker"],
                "blocker",
                f"task_board.cards[{index}].blocker",
                workstream["workstream_id"],
            )

    triggers = data.get("jit_triggers", [])
    _require(isinstance(triggers, list), "task_board: jit_triggers must be an array")
    trigger_ids: set[str] = set()
    cards_by_id = {card["id"]: card for card in cards}
    for index, trigger in enumerate(triggers):
        label = f"task_board.jit_triggers[{index}]"
        _require(isinstance(trigger, dict), f"{label}: trigger must be table")
        trigger_id = trigger.get("id")
        _require(isinstance(trigger_id, str) and trigger_id.strip(), f"{label}: missing id")
        _require(trigger_id not in trigger_ids, f"{label}: duplicate trigger id {trigger_id!r}")
        trigger_ids.add(trigger_id)
        after_card = trigger.get("after_card")
        _require(after_card in cards_by_id, f"{label}: after_card must name an existing Card")
        state = trigger.get("state")
        _require(state in JIT_TRIGGER_STATES, f"{label}: invalid state {state!r}")
        condition = trigger.get("condition")
        _require(isinstance(condition, str) and condition.strip(), f"{label}: missing condition")
        if state in {"satisfied", "consumed"}:
            predecessor = cards_by_id[after_card]
            _require(predecessor["status"] == "done" and "result" in predecessor,
                     f"{label}: satisfied trigger requires DONE predecessor result")


def validate_blocker(data: dict[str, Any], workstream_id: str, card_id: str) -> None:
    reject_prohibited_keys(data, "blocker")
    _require(data.get("workstream_id") == workstream_id, "blocker: wrong workstream_id")
    _require(data.get("card_id") == card_id, "blocker: wrong card_id")
    _require(data.get("class") in BLOCKER_CLASSES, "blocker: invalid class")
    _require(isinstance(data.get("summary"), str) and data["summary"].strip(),
             "blocker: missing summary")
    evidence_path = data.get("evidence_path", "")
    _require(isinstance(evidence_path, str), "blocker: evidence_path must be a string")
    if evidence_path:
        path = _safe_relative_path(evidence_path, "blocker.evidence_path")
        prefix = f"implementation/workstreams/{workstream_id}/evidence/"
        _require(path.startswith(prefix) and path.endswith(".md"),
                 "blocker: evidence must be workstream-local Markdown")


def _review_subject_key(data: dict[str, Any]) -> str:
    subject = data["subject"]
    return f"{subject['repository']}@{subject['commit']}:{subject['path']}@{subject['blob']}"


def validate_review(data: dict[str, Any]) -> None:
    reject_prohibited_keys(data, "review")
    _require(isinstance(data.get("attempt"), str) and data["attempt"], "review: missing attempt")
    verdict = data.get("verdict")
    _require(verdict in {"pending", "in_progress", "green", "red"}, "review: invalid verdict")

    subject = data.get("subject")
    _require(isinstance(subject, dict) and subject.get("class") == "git_blob", "review: subject must be git_blob")
    for key in ("repository", "path"):
        _require(isinstance(subject.get(key), str) and subject[key], f"review.subject: missing {key}")
    for key in ("commit", "blob"):
        _require(isinstance(subject.get(key), str) and SHA40.fullmatch(subject[key]) is not None,
                 f"review.subject: {key} must be exact 40-hex")
    _safe_relative_path(subject["path"], "review.subject")

    acceptance = data.get("acceptance")
    _require(isinstance(acceptance, dict), "review: missing acceptance identity")
    acceptance_class = acceptance.get("class")
    if acceptance_class == "authority":
        validate_locator(acceptance, "authority", "review.acceptance")
    elif acceptance_class == "task_card":
        workstream_id = data.get("workstream_id")
        _require(isinstance(workstream_id, str) and workstream_id,
                 "review: task-card acceptance requires workstream_id")
        path = validate_locator(acceptance, "task_card", "review.acceptance", workstream_id)
        card_id = data.get("card_id")
        _require(isinstance(card_id, str) and card_id, "review: task-card acceptance requires card_id")
        _require(PurePosixPath(path).stem == card_id,
                 "review: acceptance Task Card does not match card_id")
    else:
        raise ValidationError("review: unsupported acceptance identity")

    independence = data.get("independence")
    _require(isinstance(independence, dict), "review: missing semantic independence")
    _require(independence.get("materially_produced_or_repaired_subject") is False,
             "review: reviewer is not semantically independent of exact subject")
    _require(isinstance(independence.get("basis"), str) and independence["basis"].strip(),
             "review: independence basis must be durable")

    evidence_path = data.get("evidence_path", "")
    _require(isinstance(evidence_path, str), "review: evidence_path must be a string")
    if verdict in {"green", "red"}:
        _require(bool(evidence_path.strip()), "review: terminal verdict requires evidence_path")
        _safe_relative_path(evidence_path, "review.evidence_path")
    else:
        _require(evidence_path == "", "review: non-terminal attempt must not claim terminal evidence")

    v21_fields = {
        "review_kind", "source_discovery_attempt", "discovery_complete", "material_finding_ids",
    }
    explicit_v21 = "review_kind" in data
    _require(explicit_v21 or not any(key in data for key in v21_fields - {"review_kind"}),
             "review: PWv2.1 review fields require explicit review_kind")
    if explicit_v21:
        kind = data.get("review_kind")
        _require(kind in REVIEW_KINDS, f"review: invalid review_kind {kind!r}")
        source = data.get("source_discovery_attempt")
        _require(isinstance(source, str), "review: source_discovery_attempt must be a string")
        discovery_complete = data.get("discovery_complete")
        _require(isinstance(discovery_complete, bool), "review: discovery_complete must be boolean")
        finding_ids = data.get("material_finding_ids")
        _require(isinstance(finding_ids, list), "review: material_finding_ids must be an array")
        _require(
            all(isinstance(item, str) and item.strip() for item in finding_ids),
            "review: material_finding_ids must contain non-empty strings",
        )
        _require(len(set(finding_ids)) == len(finding_ids),
                 "review: material_finding_ids must be unique")

        if kind == "discovery":
            _require(source == "", "review: discovery attempt must not name source_discovery_attempt")
            if verdict in {"green", "red"}:
                _require(discovery_complete,
                         "review: terminal discovery attempt requires complete acceptance-surface discovery")
            if verdict == "green":
                _require(not finding_ids,
                         "review: GREEN discovery attempt cannot retain material blocking findings")
            if verdict == "red":
                _require(bool(finding_ids),
                         "review: RED discovery attempt must record the complete material finding set")
        else:
            _require(bool(source.strip()),
                     "review: closure_verification requires source_discovery_attempt")
            _require(not discovery_complete,
                     "review: closure_verification cannot claim full discovery completion")
            _require(bool(finding_ids),
                     "review: closure_verification must name the known material findings it verifies")


def validate_review_history(
    attempts: list[dict[str, Any]],
    *,
    expected_card_id: str | None = None,
    workstream_id: str | None = None,
) -> None:
    _require(isinstance(attempts, list) and attempts,
             "review_history: at least one attempt is required")
    seen_ids: set[str] = set()
    attempts_by_id: dict[str, dict[str, Any]] = {}
    open_findings: dict[str, set[str]] = {}
    legacy_prefix = True
    nonterminal = 0
    for index, attempt in enumerate(attempts):
        validate_review(attempt)
        attempt_id = attempt["attempt"]
        explicit_v21 = "review_kind" in attempt
        if explicit_v21:
            legacy_prefix = False
        else:
            _require(legacy_prefix,
                     "review_history: legacy review attempts must form the initial historical prefix")
            _require(attempt["verdict"] in {"green", "red"},
                     "review_history: new/active review attempts require explicit review_kind")
        _require(attempt_id not in seen_ids, f"review_history: duplicate attempt {attempt_id!r}")
        seen_ids.add(attempt_id)
        if expected_card_id is not None:
            _require(attempt.get("card_id") == expected_card_id,
                     "review_history: attempt belongs to another Card")
        if workstream_id is not None:
            _require(attempt.get("workstream_id") == workstream_id,
                     "review_history: attempt belongs to another workstream")

        if explicit_v21 and review_kind(attempt) == "discovery":
            still_open = {source_id for source_id, findings in open_findings.items() if findings}
            _require(
                not still_open,
                "review_history: fresh discovery cannot start before all known material findings are closure-verified",
            )
            if attempt["verdict"] == "red":
                open_findings[attempt_id] = set(attempt["material_finding_ids"])

        if attempt.get("review_kind") == "closure_verification":
            source_id = attempt["source_discovery_attempt"]
            source = attempts_by_id.get(source_id)
            _require(source is not None,
                     "review_history: closure source discovery must be an earlier attempt")
            _require(review_kind(source) == "discovery",
                     "review_history: closure source must be a discovery attempt")
            _require(source["verdict"] == "red",
                     "review_history: closure source discovery must be RED")
            source_findings = source.get("material_finding_ids")
            _require(isinstance(source_findings, list),
                     "review_history: PWv2.1 closure source must record material_finding_ids")
            _require(set(attempt["material_finding_ids"]).issubset(set(source_findings)),
                     "review_history: closure may verify only findings frozen by its source discovery")
            if attempt["verdict"] == "green":
                open_findings[source_id].difference_update(attempt["material_finding_ids"])

        attempts_by_id[attempt_id] = attempt
        if attempt["verdict"] in {"pending", "in_progress"}:
            nonterminal += 1
            _require(index == len(attempts) - 1,
                     "review_history: only the latest attempt may be non-terminal")
    _require(nonterminal <= 1, "review_history: multiple active attempts are forbidden")


def validate_external_effect(data: dict[str, Any], workstream_id: str) -> None:
    reject_prohibited_keys(data, "external_effect")
    for key in (
        "obligation_id", "operation", "target", "expected_state",
        "readback_state", "observation",
    ):
        _require(isinstance(data.get(key), str) and data[key], f"external_effect: missing {key}")
    readback_state = data["readback_state"]
    observation = data["observation"]
    _require(readback_state in {"pending", "verified", "uncertain"},
             "external_effect: invalid readback_state")
    _require(
        observation in {"unknown", "expected_effect", "no_effect", "unexpected_effect"},
        "external_effect: invalid observation",
    )
    if readback_state in {"pending", "uncertain"}:
        _require(observation == "unknown",
                 "external_effect: non-verified readback cannot claim an observation")
    else:
        _require(observation != "unknown",
                 "external_effect: verified readback requires a concrete observation")
    validate_locator(data.get("evidence"), "evidence", "external_effect.evidence", workstream_id)


def validate_bundle(
    project_path: Path,
    workstream_path: Path,
    board_path: Path,
    review_path: Path,
    effect_path: Path,
    expected_revision: int | None = None,
) -> None:
    project = read_project(project_path)
    workstream = read_toml(workstream_path)
    board = read_toml(board_path)
    review = read_toml(review_path)
    effect = read_toml(effect_path)

    validate_project(project)
    validate_workstream(workstream)
    validate_board(board, workstream, expected_revision)
    validate_review(review)
    validate_external_effect(effect, workstream["workstream_id"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the implemented PWV2 M01 durable state envelope.")
    parser.add_argument("project", type=Path)
    parser.add_argument("workstream", type=Path)
    parser.add_argument("task_board", type=Path)
    parser.add_argument("review_attempt", type=Path)
    parser.add_argument("external_effect", type=Path)
    parser.add_argument("--expect-revision", type=int)
    args = parser.parse_args()
    try:
        validate_bundle(
            args.project,
            args.workstream,
            args.task_board,
            args.review_attempt,
            args.external_effect,
            args.expect_revision,
        )
    except (OSError, tomllib.TOMLDecodeError, ValidationError) as exc:
        print(f"INVALID: {exc}")
        return 2
    print("VALID: PWV2 M01 state envelope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
