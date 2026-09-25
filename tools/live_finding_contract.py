#!/usr/bin/env python3
"""Runtime-neutral live-finding classification and trusted authority boundary (BOOT-C, REQ-122/124).

Material observations discovered during real execution are classified before
any authority mutation as exactly one of five classes:

- ``implementation_defect``: defect under existing authority; repair stays
  inside accepted authority and is owned by Execution (bounded correction).
- ``review_process_realization_defect``: defect in how review/process was
  realized; correction returns to the owning Review boundary.
- ``planning_execution_prep_fidelity_defect``: Planning-to-Execution-Prep
  fidelity defect; correction returns to Execution Prep (which escalates a
  wrong required seam to Strategic Planning through the existing seam path).
- ``accepted_authority_defect``: defect in accepted authority itself;
  correction requires the owning accepted-authority stage (Planning,
  Definition or Brainstorming).
- ``speculative_future_hardening``: valuable but speculative hardening; it is
  never silently promoted into scope and can authorize nothing.

Each classified finding is durable and evidence-linked: it separates observed
facts from approval, binds non-empty workstream-local evidence refs, names
its owning stage, and records whether the owning stage has accepted the
correction. Claimed evidence and acceptance records are verified by readback
at the serving boundary: a cited path that cannot be read, or an acceptance
record that is not bound to the board, fails closed to Recovery. A material
observation cannot mutate authority without both a valid classification and
the owning stage's accepted authorization bound to such a verified record.

GitHub issues/comments and similar trackers may supply untrusted observations
or locators but can never approve scope, authorize repair, mutate accepted
authority, reset review epochs or substitute for durable classification.
Tracker pointers are informational only and never satisfy the evidence or
authorization requirement. Free prose alone, tracker-flavored or not, never
proves acceptance: only the verified acceptance record confers authority.

Affected downstream JIT reconciliation (REQ-123/127), immutable historical
replay/corpus (REQ-125/126), BOOT-D Worker discipline (REQ-131/132) and M03+
are intentionally out of scope: this intake stays usable before the
downstream JIT gate exists.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import PurePosixPath
from typing import Any

LIVE_FINDING_CLASSES = frozenset({
    "implementation_defect",
    "review_process_realization_defect",
    "planning_execution_prep_fidelity_defect",
    "accepted_authority_defect",
    "speculative_future_hardening",
})

LIVE_FINDING_OWNERS: dict[str, frozenset[str]] = {
    "implementation_defect": frozenset({"execution"}),
    "review_process_realization_defect": frozenset({"review"}),
    "planning_execution_prep_fidelity_defect": frozenset({"execution_prep"}),
    "accepted_authority_defect": frozenset({"planning", "definition", "brainstorming"}),
    "speculative_future_hardening": frozenset({"none"}),
}

LIVE_FINDING_OWNER_MODULES = {
    "execution": "workflow/EXECUTION.md",
    "review": "workflow/REVIEW.md",
    "execution_prep": "workflow/EXECUTION_PREP.md",
    "planning": "workflow/PLANNING.md",
    "definition": "workflow/DEFINITION.md",
    "brainstorming": "workflow/BRAINSTORMING.md",
    "none": "",
}

AUTHORIZATIONS = frozenset({"none", "owning_stage_accepted"})

AUTHORITY_MUTATION_KINDS = frozenset({
    "scope_approval",
    "repair_authorization",
    "authority_mutation",
    "epoch_reset",
})

TRACKER_NON_AUTHORITY_KINDS = frozenset({
    "scope",
    "repair",
    "authority",
    "epoch_reset",
    "classification",
})

TRACKER_PROVENANCE_MARKERS = (
    "tracker.toml",
    "tracker/",
    "issue#",
    "issue #",
    "github.com",
    "http://",
    "https://",
)

ACCEPTANCE_RECORD_CLASSES = frozenset({"evidence", "review_attempt", "result"})

FORBIDDEN_AUTHORITY_KEYS = frozenset({
    "scope_approved",
    "scope_authorized",
    "repair_authorized",
    "repair_approved",
    "authority_mutated",
    "authority_approved",
    "epoch_reset",
    "epoch_reset_basis",
})


class LiveFindingError(ValueError):
    """Raised when live-finding classification or intake authority is invalid."""


def is_tracker_provenance(value: str) -> bool:
    """Return whether a cited record path is a tracker/issue pointer.

    Workstream-local record paths can never legitimately contain ``#`` (issue
    shorthand such as ``owner/repo#12``) or a URL, so those fail here with a
    tracker-specific reason instead of a generic shape error.
    """
    if "#" in value:
        return True
    lowered = value.lower()
    return any(marker in lowered for marker in TRACKER_PROVENANCE_MARKERS)


def live_finding_owner_module(owner_stage: str) -> str:
    """Return the canonical workflow owner module for a finding owner stage."""
    try:
        return LIVE_FINDING_OWNER_MODULES[owner_stage]
    except KeyError as exc:
        raise LiveFindingError(f"unknown live-finding owner stage {owner_stage!r}") from exc


def classify_live_finding_owner(*, finding_class: str, owner_stage: str) -> str:
    """Validate the owning-stage boundary for one live-finding class.

    Returns the owner stage. Raises :class:`LiveFindingError` when the class
    is unknown/ambiguous or the owner is outside that class's boundary:
    implementation defects stay in Execution, review/process realization
    defects return to Review, Planning-to-Execution-Prep fidelity defects
    return to Execution Prep, accepted-authority defects require their owning
    accepted-authority stage, and speculative hardening owns no mutation.
    """
    allowed = LIVE_FINDING_OWNERS.get(finding_class)
    if allowed is None:
        raise LiveFindingError(
            f"unknown live-finding class {finding_class!r}; expected exactly one of "
            + ", ".join(sorted(LIVE_FINDING_CLASSES))
        )
    if owner_stage not in allowed:
        raise LiveFindingError(
            f"live-finding class {finding_class!r} requires owner stage "
            f"in [{', '.join(sorted(allowed))}], not {owner_stage!r}"
        )
    return owner_stage


def _require_statement(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LiveFindingError(f"{label} requires a durable non-empty statement")
    return value


def _validate_evidence_refs(refs: Any, label: str, workstream_id: str) -> list[str]:
    """Require durable workstream-local evidence links, never tracker pointers."""
    if not isinstance(refs, list) or not refs:
        raise LiveFindingError(
            f"{label} requires at least one durable evidence ref; "
            "evidence-free classification fails closed"
        )
    prefix = f"implementation/workstreams/{workstream_id}/evidence/"
    seen: set[str] = set()
    for index, ref in enumerate(refs):
        item = f"{label}[{index}]"
        if not isinstance(ref, str) or not ref:
            raise LiveFindingError(f"{item}: evidence ref must be a non-empty string")
        if is_tracker_provenance(ref):
            raise LiveFindingError(
                f"{item}: tracker/issue pointers are untrusted locators and cannot "
                "serve as durable classification evidence"
            )
        path = PurePosixPath(ref)
        if (
            path.is_absolute()
            or "." in path.parts
            or ".." in path.parts
            or not ref.startswith(prefix)
            or not ref.endswith(".md")
        ):
            raise LiveFindingError(
                f"{item}: invalid workstream evidence ref {ref!r}; expected {prefix}*.md"
            )
        if ref in seen:
            raise LiveFindingError(f"{item}: duplicate evidence ref {ref!r}")
        seen.add(ref)
    return list(refs)


def _validate_record_path(
    path: Any, label: str, workstream_id: str, record_class: str
) -> str:
    """Validate one workstream-local record path of the expected class."""
    if not isinstance(path, str) or not path:
        raise LiveFindingError(f"{label}: record path must be a non-empty string")
    if is_tracker_provenance(path):
        raise LiveFindingError(
            f"{label}: tracker/issue pointers are untrusted locators and cannot "
            "serve as durable records"
        )
    pure = PurePosixPath(path)
    expected = {
        "evidence": (
            f"implementation/workstreams/{workstream_id}/evidence/",
            ".md",
        ),
        "review_attempt": (
            f"implementation/workstreams/{workstream_id}/reviews/",
            ".toml",
        ),
        "result": (
            f"implementation/workstreams/{workstream_id}/results/",
            ".md",
        ),
    }[record_class]
    if (
        pure.is_absolute()
        or "." in pure.parts
        or ".." in pure.parts
        or not path.startswith(expected[0])
        or not path.endswith(expected[1])
    ):
        raise LiveFindingError(
            f"{label}: invalid {record_class} record path {path!r}; "
            f"expected {expected[0]}*{expected[1]}"
        )
    return path


def _validate_acceptance(
    acceptance: Any, label: str, *, workstream_id: str, owner_stage: str
) -> dict[str, Any]:
    """Validate the owning stage's structured acceptance citation.

    Acceptance binds the owning stage to one verifiable durable record: an
    evidence file, a board-bound review attempt, or a board-bound Card result.
    The accompanying statement is descriptive only and confers no authority;
    only the verified record does. Existence and board binding are verified
    by readback at the serving boundary (see ``verify_live_finding_records``).
    """
    if not isinstance(acceptance, Mapping):
        raise LiveFindingError(
            f"{label}: acceptance must be a table binding the owning stage "
            "to one verifiable durable record; free prose cannot prove acceptance"
        )
    stage = acceptance.get("stage")
    if stage != owner_stage:
        raise LiveFindingError(
            f"{label}: acceptance stage {stage!r} does not match the finding's "
            f"owning stage {owner_stage!r}; only the owning stage can accept"
        )
    cited = acceptance.get("record")
    if not isinstance(cited, Mapping):
        raise LiveFindingError(
            f"{label}: acceptance must cite one verifiable record table"
        )
    record_class = cited.get("class")
    if record_class not in ACCEPTANCE_RECORD_CLASSES:
        raise LiveFindingError(
            f"{label}: unknown acceptance record class {record_class!r}; "
            "expected one of " + ", ".join(sorted(ACCEPTANCE_RECORD_CLASSES))
        )
    record_path = _validate_record_path(
        cited.get("path"), f"{label}: record", workstream_id, str(record_class)
    )
    statement = _require_statement(
        acceptance.get("statement"), f"{label}: statement"
    )
    return {
        "stage": owner_stage,
        "record": {"class": str(record_class), "path": record_path},
        "statement": statement,
    }


def validate_live_finding(
    record: Mapping[str, Any],
    label: str,
    *,
    workstream_id: str,
) -> dict[str, Any]:
    """Validate one durable evidence-linked live-finding classification.

    The record separates observed facts (``observed``) from approval
    (``authorization``): ``none`` records a classified but not yet authorized
    correction, while ``owning_stage_accepted`` binds the owning stage to one
    verifiable durable acceptance record. Speculative hardening must stay
    unauthorized. Tracker locators may be retained as untrusted input in
    ``tracker_locators`` but never satisfy evidence or authorization.
    """
    if not isinstance(record, Mapping):
        raise LiveFindingError(f"{label}: live finding must be a table")
    if "authorization_basis" in record:
        raise LiveFindingError(
            f"{label}: free-prose authorization_basis cannot prove owning-stage "
            "acceptance; bind authorization to a verifiable acceptance record"
        )
    present_forbidden = FORBIDDEN_AUTHORITY_KEYS & set(record)
    if present_forbidden:
        raise LiveFindingError(
            f"{label}: observation tracker-style authority claims "
            f"({', '.join(sorted(present_forbidden))}) cannot approve scope, "
            "authorize repair, mutate authority or reset epochs; record the "
            "owning stage's durable authorization instead"
        )
    finding_id = record.get("id")
    if not isinstance(finding_id, str) or not finding_id.strip():
        raise LiveFindingError(f"{label}: finding id must be a non-empty string")
    finding_class = record.get("finding_class")
    if finding_class not in LIVE_FINDING_CLASSES:
        raise LiveFindingError(
            f"{label}: missing or ambiguous live-finding class {finding_class!r}; "
            "expected exactly one of " + ", ".join(sorted(LIVE_FINDING_CLASSES))
        )
    observed = _require_statement(record.get("observed"), f"{label}: observed")
    evidence_refs = _validate_evidence_refs(
        record.get("evidence_refs"), f"{label}: evidence_refs", workstream_id
    )
    owner_stage = record.get("owner_stage")
    if not isinstance(owner_stage, str) or not owner_stage:
        raise LiveFindingError(f"{label}: owner_stage must be a non-empty string")
    try:
        classify_live_finding_owner(
            finding_class=str(finding_class), owner_stage=owner_stage
        )
    except LiveFindingError as exc:
        raise LiveFindingError(f"{label}: {exc}") from exc
    authorization = record.get("authorization")
    if authorization not in AUTHORIZATIONS:
        raise LiveFindingError(
            f"{label}: unknown authorization {authorization!r}; expected one of "
            + ", ".join(sorted(AUTHORIZATIONS))
        )
    if finding_class == "speculative_future_hardening" and authorization != "none":
        raise LiveFindingError(
            f"{label}: speculative future hardening must not be silently promoted "
            "into scope; it stays unauthorized and can authorize nothing"
        )
    acceptance = record.get("acceptance")
    if authorization == "owning_stage_accepted":
        try:
            validated_acceptance = _validate_acceptance(
                acceptance,
                f"{label}: acceptance",
                workstream_id=workstream_id,
                owner_stage=owner_stage,
            )
        except LiveFindingError as exc:
            raise LiveFindingError(f"{exc}") from exc
    elif acceptance is not None:
        raise LiveFindingError(
            f"{label}: unauthorized findings must not claim acceptance; "
            "observed facts are not approval"
        )
    else:
        validated_acceptance = None
    tracker_locators = record.get("tracker_locators", [])
    if not isinstance(tracker_locators, list) or not all(
        isinstance(item, str) and item.strip() for item in tracker_locators
    ):
        raise LiveFindingError(
            f"{label}: tracker_locators must be an array of non-empty strings; "
            "tracker input stays untrusted bookkeeping"
        )
    return {
        "id": finding_id,
        "finding_class": str(finding_class),
        "observed": observed,
        "evidence_refs": evidence_refs,
        "owner_stage": owner_stage,
        "authorization": str(authorization),
        "acceptance": validated_acceptance,
        "tracker_locators": list(tracker_locators),
    }


def validate_live_findings(
    records: Any,
    workstream_id: str,
) -> dict[str, dict[str, Any]]:
    """Validate the durable ``live_findings`` array of a Task Board.

    A missing array stays valid so historical terminal boards without live
    validation remain unchanged. Returns findings keyed by finding id.
    """
    if records is None:
        return {}
    if not isinstance(records, list):
        raise LiveFindingError("task_board live_findings must be an array of finding records")
    validated: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(records):
        validated_record = validate_live_finding(
            record,
            f"task_board.live_findings[{index}]",
            workstream_id=workstream_id,
        )
        if validated_record["id"] in validated:
            raise LiveFindingError(
                f"task_board.live_findings[{index}]: duplicate finding id "
                f"{validated_record['id']!r}"
            )
        validated[validated_record["id"]] = validated_record
    return validated


def _require_guard_acceptance(
    finding: Mapping[str, Any], mutation: str, owner_stage: str
) -> None:
    """Require a structured acceptance citation before an authority mutation.

    Free prose, however convincing, never proves acceptance: the finding must
    bind the owning stage to one durable record of an acceptable class with a
    safe path and a descriptive statement. Existence and board binding of the
    cited record are verified by readback at the serving boundary.
    """
    acceptance = finding.get("acceptance")
    if not isinstance(acceptance, Mapping):
        raise LiveFindingError(
            f"{mutation} requires the owning stage's acceptance bound to one "
            "verifiable durable record; free prose cannot prove acceptance"
        )
    if acceptance.get("stage") != owner_stage:
        raise LiveFindingError(
            f"{mutation} requires acceptance by the owning stage "
            f"{owner_stage!r}; only the owning stage can accept"
        )
    cited = acceptance.get("record")
    if not isinstance(cited, Mapping):
        raise LiveFindingError(
            f"{mutation} requires acceptance bound to one verifiable record"
        )
    if cited.get("class") not in ACCEPTANCE_RECORD_CLASSES:
        raise LiveFindingError(
            f"{mutation} requires an acceptance record of class evidence, "
            "review_attempt or result"
        )
    record_path = cited.get("path")
    if not isinstance(record_path, str) or not record_path.strip():
        raise LiveFindingError(
            f"{mutation} requires a verifiable acceptance record path"
        )
    pure = PurePosixPath(record_path)
    if pure.is_absolute() or "." in pure.parts or ".." in pure.parts:
        raise LiveFindingError(
            f"{mutation} requires a safe workstream-local acceptance record path"
        )
    if is_tracker_provenance(record_path):
        raise LiveFindingError(
            f"{mutation} cannot rest on tracker issue/comment approval; only the "
            "owning stage's verified durable record authorizes the mutation"
        )
    statement = acceptance.get("statement")
    if not isinstance(statement, str) or not statement.strip():
        raise LiveFindingError(
            f"{mutation} requires a descriptive acceptance statement alongside "
            "the verified record"
        )


def require_classified_authority_mutation(
    finding: Mapping[str, Any] | None,
    *,
    mutation: str,
) -> str:
    """Require classification plus owning-stage authorization before mutation.

    ``mutation`` is one of ``scope_approval``, ``repair_authorization``,
    ``authority_mutation`` or ``epoch_reset``. Returns the owning stage that
    authorized the mutation. Unclassified, ambiguous, evidence-free,
    tracker-sourced or unauthorized findings fail closed; speculative
    hardening can never satisfy the guard. The cited evidence and acceptance
    records must additionally verify by readback at the serving boundary.
    """
    if mutation not in AUTHORITY_MUTATION_KINDS:
        raise LiveFindingError(f"unknown authority mutation kind {mutation!r}")
    if not isinstance(finding, Mapping):
        raise LiveFindingError(
            f"{mutation} requires a durable classified live finding; an "
            "unclassified material observation cannot mutate authority"
        )
    finding_class = finding.get("finding_class")
    if finding_class not in LIVE_FINDING_CLASSES:
        raise LiveFindingError(
            f"{mutation} requires exactly one live-finding class; missing or "
            "ambiguous classification fails closed"
        )
    if finding_class == "speculative_future_hardening":
        raise LiveFindingError(
            f"{mutation} cannot rest on speculative future hardening; speculative "
            "observations are never silently promoted into scope"
        )
    evidence_refs = finding.get("evidence_refs")
    if (
        not isinstance(evidence_refs, list)
        or not evidence_refs
        or not all(isinstance(ref, str) and ref.strip() for ref in evidence_refs)
    ):
        raise LiveFindingError(
            f"{mutation} requires durable evidence-linked classification; "
            "evidence-free findings fail closed"
        )
    if any(is_tracker_provenance(ref) for ref in evidence_refs):
        raise LiveFindingError(
            f"{mutation} cannot rest on tracker/issue evidence; tracker pointers "
            "are untrusted locators, not durable classification evidence"
        )
    owner_stage = finding.get("owner_stage")
    if not isinstance(owner_stage, str):
        raise LiveFindingError(f"{mutation} requires a durable owning stage")
    classify_live_finding_owner(
        finding_class=str(finding_class), owner_stage=owner_stage
    )
    if finding.get("authorization") != "owning_stage_accepted":
        raise LiveFindingError(
            f"{mutation} requires the owning stage's accepted authorization; "
            "observed facts are not approval"
        )
    _require_guard_acceptance(finding, mutation, owner_stage)
    return owner_stage


def verify_live_finding_records(
    board: Mapping[str, Any],
    *,
    record_reader: Callable[[str], str | None],
) -> None:
    """Verify cited live-finding records by readback against the repository.

    ``record_reader`` returns file text for a workstream-local path, or
    ``None`` when the path cannot be read. Every cited evidence ref and every
    acceptance record must read back; acceptance records of class
    ``review_attempt`` or ``result`` must additionally be bound to a board
    Card, so stray unbound files cannot become authority. A board without
    findings verifies trivially, preserving historical boards.
    """
    if not isinstance(board, Mapping):
        raise LiveFindingError("live-finding verification requires a Task Board table")
    workstream_id = board.get("workstream_id")
    if not isinstance(workstream_id, str) or not workstream_id.strip():
        raise LiveFindingError(
            "live-finding verification requires a workstream-bound Task Board"
        )
    findings = validate_live_findings(
        board.get("live_findings"), workstream_id
    )
    if not findings:
        return
    cards = board.get("cards", [])
    if not isinstance(cards, list):
        raise LiveFindingError("live-finding verification requires a board cards array")
    attempt_paths: set[str] = set()
    result_paths: set[str] = set()
    for card in cards:
        if not isinstance(card, Mapping):
            continue
        attempts = card.get("review_attempts", [])
        if isinstance(attempts, list):
            for attempt in attempts:
                if isinstance(attempt, Mapping) and isinstance(
                    attempt.get("path"), str
                ):
                    attempt_paths.add(attempt["path"])
        result = card.get("result")
        if isinstance(result, Mapping) and isinstance(result.get("path"), str):
            result_paths.add(result["path"])
    for finding_id, finding in findings.items():
        for ref in finding["evidence_refs"]:
            if record_reader(ref) is None:
                raise LiveFindingError(
                    f"live finding {finding_id!r} cites durable evidence {ref!r} "
                    "that cannot be read back; nonexistent evidence fails closed "
                    "to Recovery"
                )
        acceptance = finding["acceptance"]
        if acceptance is None:
            continue
        cited = acceptance["record"]
        if record_reader(cited["path"]) is None:
            raise LiveFindingError(
                f"live finding {finding_id!r} cites acceptance record "
                f"{cited['path']!r} that cannot be read back; unverifiable "
                "acceptance fails closed to Recovery"
            )
        if cited["class"] == "review_attempt" and cited["path"] not in attempt_paths:
            raise LiveFindingError(
                f"live finding {finding_id!r} cites acceptance attempt "
                f"{cited['path']!r} that is not bound to any board Card; "
                "unbound records cannot become authority"
            )
        if cited["class"] == "result" and cited["path"] not in result_paths:
            raise LiveFindingError(
                f"live finding {finding_id!r} cites acceptance result "
                f"{cited['path']!r} that is not bound to any board Card; "
                "unbound records cannot become authority"
            )


def tracker_cannot_authorize(kind: str, *, source: str = "tracker") -> None:
    """Fail closed on any tracker approval/authority/epoch/classification claim.

    ``kind`` is one of ``scope``, ``repair``, ``authority``, ``epoch_reset``
    or ``classification``. This helper always raises: tracker issues,
    comments and similar inputs are untrusted bookkeeping and can never
    approve scope, authorize repair, mutate accepted authority, reset review
    epochs or substitute for durable classification.
    """
    if kind not in TRACKER_NON_AUTHORITY_KINDS:
        raise LiveFindingError(f"unknown tracker non-authority kind {kind!r}")
    if kind == "scope":
        detail = "approve scope"
    elif kind == "repair":
        detail = "authorize repair"
    elif kind == "authority":
        detail = "mutate accepted authority"
    elif kind == "epoch_reset":
        detail = "reset review epochs"
    else:
        detail = "substitute for durable live-finding classification"
    raise LiveFindingError(
        f"{source} issue/comment cannot {detail}; it requires a durable "
        "classified live finding plus the owning stage's accepted authorization"
    )
