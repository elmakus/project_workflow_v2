#!/usr/bin/env python3
"""Runtime-neutral falsification-first Worker execution/evidence contract (BOOT-D, REQ-131).

Where an accepted Card outcome can be meaningfully falsified, the Worker
starts from a failing automated or observable acceptance check on the
pre-implementation subject, then implements the minimum in-scope change and
demonstrates the same check GREEN on the implemented subject. Documentation,
migration, workflow-policy and other outcomes that cannot naturally use a
unit test use an explicit justified observable check instead of an
artificial test.

A record binds one Card, one outcome class, one RED baseline, one bounded
implementation step and one GREEN verification of the same check, with
strict chronology (baseline < implementation < verification), exact Git
subject identity (baseline subject differs from implementation subject;
verification subject equals implementation subject) and distinct baseline /
verification evidence. Missing, generic, retrospective or out-of-order
baselines, GREEN-before-implementation claims and unjustified observable
checks fail closed. Provider, model, worker, session, retry, worktree,
Paseo, scheduler, invocation and runtime identity are non-canonical and
rejected as fields, matching the typed obligation/result boundary.

This SHOULD-level execution discipline constrains Worker evidence inside an
already-authorized Card. It creates no new Card, Milestone or premium gate,
no runtime worker catalog, no fixed size/LOC/time category and no scheduler
semantics. Historical Card results without a Worker evidence record remain
valid; absence means legacy-compatible, never retrospective falsification.
Out of scope here: REQ-132 YAGNI/refactor/DRY scope discipline (separate
next Card), M03 and historical M02 rewrites.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from tools.obligation_contract import validate_git_subject

CARD_ID = re.compile(r"^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+$")

OUTCOME_CLASSES = frozenset({"code", "documentation", "migration", "policy"})
AUTOMATABLE_OUTCOME_CLASSES = frozenset({"code"})
OBSERVABLE_ELIGIBLE_CLASSES = frozenset({"documentation", "migration", "policy"})
BASELINE_KINDS = frozenset({"automated_check", "observable_check"})

TELEMETRY_KEY_ROOTS = (
    "provider", "model", "worker", "session", "retry", "retries",
    "worktree", "paseo", "runtime", "invocation", "scheduler",
)

GENERIC_CHECK_CLAIMS = frozenset({
    "red", "green", "fail", "pass", "failing", "passing",
    "tests fail", "tests pass", "test fails", "test passes",
    "it fails", "it passes", "broken", "works", "failing check",
    "passing check", "red baseline", "green verification",
    "n/a", "na", "none", "tbd", "todo",
})

MIN_CHECK_LEN = 8
MIN_EVIDENCE_LEN = 8
MIN_SUMMARY_LEN = 8
MIN_JUSTIFICATION_LEN = 24


class WorkerEvidenceError(ValueError):
    """Raised when Worker falsification-first evidence is invalid."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise WorkerEvidenceError(message)


def _reject_telemetry_keys(value: Any, where: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).lower()
            _require(
                not normalized.startswith(TELEMETRY_KEY_ROOTS),
                f"{where}: telemetry key {key!r} is non-canonical",
            )
            _reject_telemetry_keys(child, f"{where}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_telemetry_keys(child, f"{where}[{index}]")


def _normalize_generic_candidate(text: str) -> str:
    collapsed = " ".join(text.strip().lower().split())
    return collapsed.strip(".,!?:;'\"()[]")


def _is_generic_claim(text: str) -> bool:
    return _normalize_generic_candidate(text) in GENERIC_CHECK_CLAIMS


def _require_specific_text(value: Any, label: str, min_len: int) -> str:
    _require(isinstance(value, str) and value.strip(), f"{label} must be a non-empty string")
    text = value.strip()
    _require(len(text) >= min_len, f"{label} must carry a specific falsifiable statement")
    _require("<" not in text and ">" not in text, f"{label} must not carry a placeholder")
    _require(not _is_generic_claim(text), f"{label} must not be a generic claim")
    return value if isinstance(value, str) else text


def _require_sequence_number(value: Any, label: str) -> int:
    _require(isinstance(value, int) and not isinstance(value, bool), f"{label} must be an integer")
    _require(value >= 0, f"{label} must be non-negative")
    return value


def validate_worker_evidence(record: Mapping[str, Any], label: str = "worker_evidence") -> dict[str, Any]:
    """Validate one falsification-first Worker evidence record.

    The record proves RED baseline -> bounded implementation -> GREEN
    verification of the same check with truthful order and subject/evidence
    identity. Anything else fails closed.
    """
    _require(isinstance(record, Mapping), f"{label} must be an object")
    _reject_telemetry_keys(record, label)
    expected = {
        "card_id", "outcome_class", "baseline", "implementation",
        "verification", "sequence", "observable_justification",
    }
    _require(set(record) == expected, f"{label}: invalid top-level keys")

    card_id = record["card_id"]
    _require(
        isinstance(card_id, str) and CARD_ID.fullmatch(card_id) is not None,
        f"{label}.card_id must be a concrete Card id",
    )
    outcome_class = record["outcome_class"]
    _require(outcome_class in OUTCOME_CLASSES, f"{label}.outcome_class must be one of {sorted(OUTCOME_CLASSES)}")

    baseline = record["baseline"]
    _require(isinstance(baseline, Mapping), f"{label}.baseline must be an object")
    _require(
        set(baseline) == {"kind", "check", "status", "subject", "evidence"},
        f"{label}.baseline: invalid keys",
    )
    kind = baseline["kind"]
    _require(kind in BASELINE_KINDS, f"{label}.baseline.kind must be one of {sorted(BASELINE_KINDS)}")
    if outcome_class in AUTOMATABLE_OUTCOME_CLASSES:
        _require(
            kind == "automated_check",
            f"{label}: observable check cannot substitute for an automatable {outcome_class!r} outcome",
        )
    else:
        _require(
            outcome_class in OBSERVABLE_ELIGIBLE_CLASSES,
            f"{label}.outcome_class must be one of {sorted(OUTCOME_CLASSES)}",
        )
    baseline_check = _require_specific_text(baseline["check"], f"{label}.baseline.check", MIN_CHECK_LEN)
    _require(baseline["status"] == "red", f"{label}.baseline.status must be exactly 'red'")
    try:
        baseline_subject = validate_git_subject(baseline["subject"], f"{label}.baseline.subject")
    except ValueError as exc:
        raise WorkerEvidenceError(str(exc)) from exc
    baseline_evidence = _require_specific_text(
        baseline["evidence"], f"{label}.baseline.evidence", MIN_EVIDENCE_LEN
    )

    implementation = record["implementation"]
    _require(isinstance(implementation, Mapping), f"{label}.implementation must be an object")
    _require(set(implementation) == {"subject", "summary"}, f"{label}.implementation: invalid keys")
    try:
        implementation_subject = validate_git_subject(
            implementation["subject"], f"{label}.implementation.subject"
        )
    except ValueError as exc:
        raise WorkerEvidenceError(str(exc)) from exc
    summary = _require_specific_text(
        implementation["summary"], f"{label}.implementation.summary", MIN_SUMMARY_LEN
    )

    verification = record["verification"]
    _require(isinstance(verification, Mapping), f"{label}.verification must be an object")
    _require(
        set(verification) == {"check", "status", "subject", "evidence"},
        f"{label}.verification: invalid keys",
    )
    verification_check = _require_specific_text(
        verification["check"], f"{label}.verification.check", MIN_CHECK_LEN
    )
    _require(verification["status"] == "green", f"{label}.verification.status must be exactly 'green'")
    try:
        verification_subject = validate_git_subject(
            verification["subject"], f"{label}.verification.subject"
        )
    except ValueError as exc:
        raise WorkerEvidenceError(str(exc)) from exc
    verification_evidence = _require_specific_text(
        verification["evidence"], f"{label}.verification.evidence", MIN_EVIDENCE_LEN
    )

    _require(
        verification_check.strip() == baseline_check.strip(),
        f"{label}: verification must close the same falsifiable check as the baseline",
    )
    _require(
        verification_evidence.strip() != baseline_evidence.strip(),
        f"{label}: baseline and verification require distinct observed evidence",
    )
    _require(
        baseline_subject != implementation_subject,
        f"{label}: retrospective RED on the implemented subject is not a pre-implementation baseline",
    )
    _require(
        verification_subject == implementation_subject,
        f"{label}: GREEN must be observed on the implemented subject",
    )

    sequence = record["sequence"]
    _require(isinstance(sequence, Mapping), f"{label}.sequence must be an object")
    _require(
        set(sequence) == {"baseline", "implementation", "verification"},
        f"{label}.sequence: invalid keys",
    )
    baseline_seq = _require_sequence_number(sequence["baseline"], f"{label}.sequence.baseline")
    implementation_seq = _require_sequence_number(
        sequence["implementation"], f"{label}.sequence.implementation"
    )
    verification_seq = _require_sequence_number(
        sequence["verification"], f"{label}.sequence.verification"
    )
    _require(
        baseline_seq < implementation_seq < verification_seq,
        f"{label}.sequence must order baseline < implementation < verification",
    )

    justification = record["observable_justification"]
    if kind == "observable_check":
        _require(
            isinstance(justification, str) and justification.strip(),
            f"{label}.observable_justification must explain why an automated check is unnatural",
        )
        text = justification.strip()
        _require(
            len(text) >= MIN_JUSTIFICATION_LEN,
            f"{label}.observable_justification must carry an explicit observable predicate",
        )
        _require("<" not in text and ">" not in text, f"{label}.observable_justification must not carry a placeholder")
        _require(
            not _is_generic_claim(text),
            f"{label}.observable_justification must not be a generic claim",
        )
    else:
        _require(
            justification is None,
            f"{label}.observable_justification must be null for an automated check",
        )

    return {
        "card_id": card_id,
        "outcome_class": outcome_class,
        "baseline": {
            "kind": kind,
            "check": baseline_check,
            "status": "red",
            "subject": baseline_subject,
            "evidence": baseline_evidence,
        },
        "implementation": {"subject": implementation_subject, "summary": summary},
        "verification": {
            "check": verification_check,
            "status": "green",
            "subject": verification_subject,
            "evidence": verification_evidence,
        },
        "sequence": {
            "baseline": baseline_seq,
            "implementation": implementation_seq,
            "verification": verification_seq,
        },
        "observable_justification": justification,
    }


def classify_worker_return(*, evidence_valid: bool, real_blocker: bool) -> str:
    """Classify a Worker return before Main reconciles durable state."""
    if real_blocker:
        return "block"
    if not evidence_valid:
        return "correct"
    return "reconcile"


def falsification_status(
    worker_evidence: Mapping[str, Any] | None,
    *,
    expected_card_id: str | None = None,
    label: str = "worker_evidence",
) -> str:
    """Return the lifecycle status of optional Worker falsification evidence.

    Absence is legacy-compatible: historical valid results without a Worker
    evidence record remain valid and never become retrospective claims.
    Presence is validated strictly and must bind the expected Card when one
    is supplied.
    """
    if worker_evidence is None:
        return "legacy_compatible"
    normalized = validate_worker_evidence(worker_evidence, label)
    if expected_card_id is not None:
        _require(
            normalized["card_id"] == expected_card_id,
            f"{label}.card_id does not match the active Card",
        )
    return "falsification_first_green"
