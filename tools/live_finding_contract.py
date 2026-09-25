#!/usr/bin/env python3
"""Runtime-neutral live-finding classification, trusted authority boundary and
affected-JIT reconciliation gate (BOOT-C, REQ-122/123/124).

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
correction. An accepted authorization cites one typed acceptance-decision
record (``findings/*.toml``) whose content names the exact finding id,
finding class and accepting stage and carries an explicit accepted decision;
readable-but-unrelated files, other records, RED attempts and tracker-flavored
prose can never satisfy this proof. Cited evidence must read back and the
decision record must verify by content at the serving boundary, else the
board fails closed to Recovery. A material observation cannot mutate
authority without both a valid classification and such a verified proof.

GitHub issues/comments and similar trackers may supply untrusted observations
or locators but can never approve scope, authorize repair, mutate accepted
authority, reset review epochs or substitute for durable classification.
Tracker pointers are informational only and never satisfy the evidence or
authorization requirement. No free prose appears in the acceptance proof, so
neither arbitrary text nor tracker shorthand can become authority.

A classified finding may additionally target one exact downstream JIT trigger
it materially affects (REQ-123): the targeting names the trigger, the next
affected facet (authority, topology or semantics), durable materiality
evidence and a pending/reconciled state. A satisfied trigger with a pending
material finding is held until the owning stage's reconciliation is accepted
through one typed reconciliation-decision record (``findings/*.toml`` naming
the exact finding id, finding class, trigger id and accepting stage with an
explicit reconciled decision) and verified by readback at the serving
boundary; only then may the affected trigger be consumed, without erasing
the finding or its decision history. Explicitly unrelated findings,
speculative hardening and already-reconciled findings never block a trigger
merely by being present. Missing, stale, ambiguous, forged or contradictory
trigger/materiality/reconciliation bindings fail closed, as do
tracker-derived approval and Worker self-authorization.

Intentional live-consumer prerequisites (REQ-127) live in
``tools/live_consumer_contract.py`` and compose with this gate; immutable
historical replay/corpus (REQ-125/126), BOOT-D Worker discipline
(REQ-131/132) and M03+ are intentionally out of scope.
"""

from __future__ import annotations

import tomllib
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

ACCEPTANCE_RECORD_CLASSES = frozenset({"finding_acceptance"})

ACCEPTANCE_DECISION_FIELDS = frozenset({
    "finding_id",
    "finding_class",
    "accepting_stage",
    "decision",
})

ACCEPTANCE_DECISION_ACCEPTED = "accepted"

DOWNSTREAM_DISPOSITIONS = frozenset({"material", "unrelated"})

MATERIALITY_ASPECTS = frozenset({"authority", "topology", "semantics"})

RECONCILIATION_STATES = frozenset({"pending", "reconciled"})

RECONCILIATION_RECORD_CLASSES = frozenset({"finding_reconciliation"})

RECONCILIATION_DECISION_FIELDS = frozenset({
    "finding_id",
    "finding_class",
    "trigger_id",
    "accepting_stage",
    "decision",
})

RECONCILIATION_DECISION_RECONCILED = "reconciled"

DOWNSTREAM_MATERIAL_KEYS = frozenset({
    "disposition",
    "trigger",
    "aspect",
    "material_evidence_refs",
    "reconciliation",
    "acceptance",
})

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
        "finding_acceptance": (
            f"implementation/workstreams/{workstream_id}/findings/",
            ".toml",
        ),
        "finding_reconciliation": (
            f"implementation/workstreams/{workstream_id}/findings/",
            ".toml",
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

    Acceptance binds the owning stage to one typed acceptance-decision
    record (``findings/*.toml``). There is no free-prose field: the decision
    document's content — exact finding id, finding class, accepting stage
    and explicit accepted decision — is the proof, verified by readback at
    the serving boundary (see ``verify_live_finding_records``).
    """
    if not isinstance(acceptance, Mapping):
        raise LiveFindingError(
            f"{label}: acceptance must be a table binding the owning stage "
            "to one typed acceptance-decision record"
        )
    if "statement" in acceptance:
        raise LiveFindingError(
            f"{label}: free-form acceptance statements cannot prove acceptance; "
            "the typed decision record carries the proof"
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
            f"{label}: acceptance must cite one acceptance-decision record table"
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
    return {
        "stage": owner_stage,
        "record": {"class": str(record_class), "path": record_path},
    }


def _is_worker_identity(stage: Any) -> bool:
    """Return whether an accepting stage value claims Worker identity.

    Worker output can never finalize shared workflow state, so a Worker
    stage value in a reconciliation citation is self-authorization, not an
    owning-stage decision, and fails with an explicit reason.
    """
    if not isinstance(stage, str):
        return False
    head = stage.strip().lower().replace("-", "_").replace(":", "_").replace(" ", "_")
    return head == "worker" or head.startswith("worker_")


def _validate_reconciliation_acceptance(
    acceptance: Any, label: str, *, workstream_id: str, owner_stage: str
) -> dict[str, Any]:
    """Validate the owning stage's structured reconciliation citation.

    Reconciliation binds the owning stage to one typed
    reconciliation-decision record (``findings/*.toml``). Only the owning
    stage can reconcile: tracker provenance, Worker identity stages and
    free-prose statements can never satisfy this citation. The decision
    document's content — exact finding id, finding class, trigger id,
    accepting stage and explicit reconciled decision — is the proof,
    verified by readback at the serving boundary.
    """
    if not isinstance(acceptance, Mapping):
        raise LiveFindingError(
            f"{label}: reconciliation must bind the owning stage to one "
            "typed reconciliation-decision record"
        )
    if "statement" in acceptance:
        raise LiveFindingError(
            f"{label}: free-form reconciliation statements cannot prove "
            "reconciliation; the typed decision record carries the proof"
        )
    unexpected = set(acceptance) - {"stage", "record"}
    if unexpected:
        raise LiveFindingError(
            f"{label}: unexpected reconciliation acceptance keys "
            f"({', '.join(sorted(str(key) for key in unexpected))}); expected "
            "exactly stage and record"
        )
    stage = acceptance.get("stage")
    if _is_worker_identity(stage):
        raise LiveFindingError(
            f"{label}: Worker self-authorization cannot reconcile an affected "
            f"JIT trigger; only the owning stage {owner_stage!r} can reconcile"
        )
    if stage != owner_stage:
        raise LiveFindingError(
            f"{label}: reconciliation stage {stage!r} does not match the finding's "
            f"owning stage {owner_stage!r}; only the owning stage can reconcile"
        )
    cited = acceptance.get("record")
    if not isinstance(cited, Mapping):
        raise LiveFindingError(
            f"{label}: reconciliation must cite one reconciliation-decision record table"
        )
    unexpected_record = set(cited) - {"class", "path"}
    if unexpected_record:
        raise LiveFindingError(
            f"{label}: unexpected reconciliation record keys "
            f"({', '.join(sorted(str(key) for key in unexpected_record))}); "
            "expected exactly class and path"
        )
    record_class = cited.get("class")
    if record_class not in RECONCILIATION_RECORD_CLASSES:
        raise LiveFindingError(
            f"{label}: unknown reconciliation record class {record_class!r}; "
            "expected one of " + ", ".join(sorted(RECONCILIATION_RECORD_CLASSES))
        )
    record_path = _validate_record_path(
        cited.get("path"), f"{label}: record", workstream_id, str(record_class)
    )
    return {
        "stage": owner_stage,
        "record": {"class": str(record_class), "path": record_path},
    }


def _validate_downstream(
    downstream: Any,
    label: str,
    *,
    workstream_id: str,
    finding_class: str,
    owner_stage: str,
) -> dict[str, Any] | None:
    """Validate one finding's durable downstream materiality disposition.

    A missing disposition stays valid and never blocks: findings recorded
    before the affected-JIT gate, or with no downstream effect, impose no
    hold merely by being present. An explicit ``unrelated`` disposition
    records that absence of effect and must not claim targeting or
    reconciliation. A ``material`` disposition durably targets exactly one
    downstream JIT trigger id, the next affected facet (``authority``,
    ``topology`` or ``semantics``), at least one workstream-local
    materiality evidence ref, and a ``pending``/``reconciled`` state; a
    ``reconciled`` state binds the owning stage's typed reconciliation
    citation while a ``pending`` state must not claim one. Speculative
    future hardening can never be material. Trigger existence and the
    consumed/pending hold are enforced at the board boundary, where the
    trigger set is visible.
    """
    if downstream is None:
        return None
    if not isinstance(downstream, Mapping):
        raise LiveFindingError(
            f"{label}: downstream must be a table carrying the finding's "
            "materiality disposition"
        )
    if "reconciliation_basis" in downstream or "statement" in downstream:
        raise LiveFindingError(
            f"{label}: free-prose reconciliation claims cannot prove targeting or "
            "reconciliation; record exact trigger/aspect/evidence bindings plus the "
            "typed decision record"
        )
    unexpected = set(downstream) - DOWNSTREAM_MATERIAL_KEYS
    if unexpected:
        raise LiveFindingError(
            f"{label}: unexpected downstream keys "
            f"({', '.join(sorted(str(key) for key in unexpected))}); downstream "
            "carries only disposition, trigger, aspect, material_evidence_refs, "
            "reconciliation and acceptance"
        )
    disposition = downstream.get("disposition")
    if disposition not in DOWNSTREAM_DISPOSITIONS:
        raise LiveFindingError(
            f"{label}: missing or ambiguous downstream disposition {disposition!r}; "
            "expected exactly one of " + ", ".join(sorted(DOWNSTREAM_DISPOSITIONS))
        )
    if finding_class == "speculative_future_hardening" and disposition == "material":
        raise LiveFindingError(
            f"{label}: speculative future hardening must not be targeted as "
            "material to a downstream trigger; it stays non-blocking and can "
            "authorize nothing"
        )
    if disposition == "unrelated":
        if set(downstream) != {"disposition"}:
            raise LiveFindingError(
                f"{label}: explicitly unrelated findings must not claim trigger "
                "targeting, materiality evidence or reconciliation"
            )
        return {"disposition": "unrelated"}
    trigger_id = downstream.get("trigger")
    if not isinstance(trigger_id, str) or not trigger_id.strip():
        raise LiveFindingError(
            f"{label}: material targeting requires the exact affected JIT trigger id"
        )
    aspect = downstream.get("aspect")
    if aspect not in MATERIALITY_ASPECTS:
        raise LiveFindingError(
            f"{label}: missing or ambiguous materiality aspect {aspect!r}; "
            "expected exactly one of " + ", ".join(sorted(MATERIALITY_ASPECTS))
        )
    material_evidence_refs = _validate_evidence_refs(
        downstream.get("material_evidence_refs"),
        f"{label}: material_evidence_refs",
        workstream_id,
    )
    reconciliation = downstream.get("reconciliation")
    if reconciliation not in RECONCILIATION_STATES:
        raise LiveFindingError(
            f"{label}: missing or ambiguous reconciliation state {reconciliation!r}; "
            "expected one of " + ", ".join(sorted(RECONCILIATION_STATES))
        )
    acceptance = downstream.get("acceptance")
    if reconciliation == "reconciled":
        validated_acceptance = _validate_reconciliation_acceptance(
            acceptance,
            f"{label}: acceptance",
            workstream_id=workstream_id,
            owner_stage=owner_stage,
        )
    elif acceptance is not None:
        raise LiveFindingError(
            f"{label}: pending reconciliation must not claim acceptance; "
            "the affected trigger stays held until the owning stage reconciles"
        )
    else:
        validated_acceptance = None
    return {
        "disposition": "material",
        "trigger": trigger_id,
        "aspect": str(aspect),
        "material_evidence_refs": material_evidence_refs,
        "reconciliation": str(reconciliation),
        "acceptance": validated_acceptance,
    }


def parse_acceptance_decision(text: str, record_path: str) -> dict[str, str]:
    """Parse one typed acceptance-decision document.

    The document must be TOML carrying exactly ``finding_id``,
    ``finding_class``, ``accepting_stage`` and ``decision`` as non-empty
    strings. Anything else — Markdown notes, result prose, review attempts,
    tracker exports — fails here, so unrelated records can never satisfy an
    acceptance proof no matter how readable they are.
    """
    try:
        document = tomllib.loads(text)
    except (tomllib.TOMLDecodeError, ValueError) as exc:
        raise LiveFindingError(
            f"acceptance record {record_path!r} is not a typed "
            f"acceptance-decision document: {exc}"
        ) from exc
    if not isinstance(document, dict):
        raise LiveFindingError(
            f"acceptance record {record_path!r} must be a TOML table"
        )
    keys = set(document)
    if keys != ACCEPTANCE_DECISION_FIELDS:
        missing = sorted(ACCEPTANCE_DECISION_FIELDS - keys)
        extra = sorted(keys - ACCEPTANCE_DECISION_FIELDS)
        raise LiveFindingError(
            f"acceptance record {record_path!r} has wrong decision fields "
            f"missing={missing} extra={extra}; expected exactly "
            + ", ".join(sorted(ACCEPTANCE_DECISION_FIELDS))
        )
    decision: dict[str, str] = {}
    for key in sorted(ACCEPTANCE_DECISION_FIELDS):
        value = document[key]
        if not isinstance(value, str) or not value.strip():
            raise LiveFindingError(
                f"acceptance record {record_path!r}: decision field {key!r} "
                "must be a non-empty string"
            )
        decision[key] = value
    return decision


def verify_acceptance_decision(
    finding: Mapping[str, Any], record_path: str, record_text: str | None
) -> None:
    """Verify a cited decision document proves this finding's acceptance.

    ``record_text`` is the read-back file content, or ``None`` when the path
    cannot be read. The document must name this exact finding id and class,
    the finding's owning stage, and an explicit accepted decision; a decision
    for another finding, another stage, or any other verdict fails closed.
    """
    finding_id = finding.get("id")
    if record_text is None:
        raise LiveFindingError(
            f"live finding {finding_id!r} cites acceptance record "
            f"{record_path!r} that cannot be read back; unverifiable "
            "acceptance fails closed to Recovery"
        )
    decision = parse_acceptance_decision(record_text, record_path)
    if decision["finding_id"] != finding_id:
        raise LiveFindingError(
            f"live finding {finding_id!r} cites acceptance record "
            f"{record_path!r} decided for finding {decision['finding_id']!r}; "
            "unrelated decisions cannot become authority"
        )
    if decision["finding_class"] != finding.get("finding_class"):
        raise LiveFindingError(
            f"live finding {finding_id!r} cites acceptance record "
            f"{record_path!r} decided for class "
            f"{decision['finding_class']!r}; mismatched classes fail closed"
        )
    if decision["accepting_stage"] != finding.get("owner_stage"):
        raise LiveFindingError(
            f"live finding {finding_id!r} cites acceptance record "
            f"{record_path!r} accepted by stage "
            f"{decision['accepting_stage']!r}; only the owning stage can accept"
        )
    if decision["decision"] != ACCEPTANCE_DECISION_ACCEPTED:
        raise LiveFindingError(
            f"live finding {finding_id!r} cites acceptance record "
            f"{record_path!r} with decision {decision['decision']!r}; only an "
            "explicit accepted decision authorizes a mutation"
        )


def parse_reconciliation_decision(text: str, record_path: str) -> dict[str, str]:
    """Parse one typed reconciliation-decision document.

    The document must be TOML carrying exactly ``finding_id``,
    ``finding_class``, ``trigger_id``, ``accepting_stage`` and ``decision``
    as non-empty strings. The five-field shape is deliberately distinct
    from the four-field acceptance-decision shape, so an authority-mutation
    acceptance can never prove trigger reconciliation and a reconciliation
    can never prove authority mutation. Anything else — Markdown notes,
    result prose, review attempts, tracker exports — fails here, so
    unrelated records can never satisfy a reconciliation proof no matter
    how readable they are.
    """
    try:
        document = tomllib.loads(text)
    except (tomllib.TOMLDecodeError, ValueError) as exc:
        raise LiveFindingError(
            f"reconciliation record {record_path!r} is not a typed "
            f"reconciliation-decision document: {exc}"
        ) from exc
    if not isinstance(document, dict):
        raise LiveFindingError(
            f"reconciliation record {record_path!r} must be a TOML table"
        )
    keys = set(document)
    if keys != RECONCILIATION_DECISION_FIELDS:
        missing = sorted(RECONCILIATION_DECISION_FIELDS - keys)
        extra = sorted(keys - RECONCILIATION_DECISION_FIELDS)
        raise LiveFindingError(
            f"reconciliation record {record_path!r} has wrong decision fields "
            f"missing={missing} extra={extra}; expected exactly "
            + ", ".join(sorted(RECONCILIATION_DECISION_FIELDS))
        )
    decision: dict[str, str] = {}
    for key in sorted(RECONCILIATION_DECISION_FIELDS):
        value = document[key]
        if not isinstance(value, str) or not value.strip():
            raise LiveFindingError(
                f"reconciliation record {record_path!r}: decision field {key!r} "
                "must be a non-empty string"
            )
        decision[key] = value
    return decision


def verify_reconciliation_decision(
    finding: Mapping[str, Any],
    downstream: Mapping[str, Any],
    record_path: str,
    record_text: str | None,
) -> None:
    """Verify a cited decision document proves this trigger reconciliation.

    ``record_text`` is the read-back file content, or ``None`` when the path
    cannot be read. The document must name this exact finding id and class,
    the exact targeted trigger id, the finding's owning stage, and an
    explicit reconciled decision; a decision for another finding, another
    class, another trigger, another stage, or any other verdict fails
    closed.
    """
    finding_id = finding.get("id")
    if record_text is None:
        raise LiveFindingError(
            f"live finding {finding_id!r} cites reconciliation record "
            f"{record_path!r} that cannot be read back; unverifiable "
            "reconciliation fails closed to Recovery"
        )
    decision = parse_reconciliation_decision(record_text, record_path)
    if decision["finding_id"] != finding_id:
        raise LiveFindingError(
            f"live finding {finding_id!r} cites reconciliation record "
            f"{record_path!r} decided for finding {decision['finding_id']!r}; "
            "unrelated decisions cannot release an affected trigger"
        )
    if decision["finding_class"] != finding.get("finding_class"):
        raise LiveFindingError(
            f"live finding {finding_id!r} cites reconciliation record "
            f"{record_path!r} decided for class "
            f"{decision['finding_class']!r}; mismatched classes fail closed"
        )
    if decision["trigger_id"] != downstream.get("trigger"):
        raise LiveFindingError(
            f"live finding {finding_id!r} cites reconciliation record "
            f"{record_path!r} decided for trigger {decision['trigger_id']!r}; "
            "a reconciliation for another trigger cannot release this one"
        )
    if decision["accepting_stage"] != finding.get("owner_stage"):
        raise LiveFindingError(
            f"live finding {finding_id!r} cites reconciliation record "
            f"{record_path!r} reconciled by stage "
            f"{decision['accepting_stage']!r}; only the owning stage can reconcile"
        )
    if decision["decision"] != RECONCILIATION_DECISION_RECONCILED:
        raise LiveFindingError(
            f"live finding {finding_id!r} cites reconciliation record "
            f"{record_path!r} with decision {decision['decision']!r}; only an "
            "explicit reconciled decision releases the affected trigger"
        )


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
    ``tracker_locators`` but never satisfy evidence or authorization. The
    optional ``downstream`` table records the finding's affected-JIT
    disposition: absent or ``unrelated`` never blocks, while ``material``
    durably targets exactly one downstream trigger id plus aspect, evidence
    and pending/reconciled state.
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
    downstream = _validate_downstream(
        record.get("downstream"),
        f"{label}: downstream",
        workstream_id=workstream_id,
        finding_class=str(finding_class),
        owner_stage=owner_stage,
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
        "downstream": downstream,
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
    """Require a typed acceptance-decision citation before a mutation.

    The finding must bind the owning stage to one ``finding_acceptance``
    decision record at a safe path. There is no prose to judge: the decision
    document's content is verified by readback at the serving boundary.
    """
    acceptance = finding.get("acceptance")
    if not isinstance(acceptance, Mapping):
        raise LiveFindingError(
            f"{mutation} requires the owning stage's acceptance bound to one "
            "typed acceptance-decision record"
        )
    if "statement" in acceptance:
        raise LiveFindingError(
            f"{mutation} cannot rest on free-form acceptance statements; only "
            "the typed decision record proves acceptance"
        )
    if acceptance.get("stage") != owner_stage:
        raise LiveFindingError(
            f"{mutation} requires acceptance by the owning stage "
            f"{owner_stage!r}; only the owning stage can accept"
        )
    cited = acceptance.get("record")
    if not isinstance(cited, Mapping):
        raise LiveFindingError(
            f"{mutation} requires acceptance bound to one decision record"
        )
    if cited.get("class") not in ACCEPTANCE_RECORD_CLASSES:
        raise LiveFindingError(
            f"{mutation} requires a finding_acceptance decision record; "
            "readable-but-unrelated files, results and review attempts "
            "cannot prove acceptance"
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
            "owning stage's verified decision record authorizes the mutation"
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
    hardening can never satisfy the guard. This checks the citation shape;
    the decision document's content must additionally verify by readback at
    the serving boundary before any downstream consumer relies on it.
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
    ``None`` when the path cannot be read. Every cited evidence ref must
    read back, and every cited acceptance-decision record must read back and
    prove this finding's acceptance by content: exact finding id and class,
    the owning stage, and an explicit accepted decision. A board without
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
        verify_acceptance_decision(
            finding, cited["path"], record_reader(cited["path"])
        )


def validate_finding_trigger_gates(
    findings: Mapping[str, Mapping[str, Any]],
    triggers: Any,
) -> dict[str, list[str]]:
    """Enforce the affected-JIT hold between material findings and triggers.

    ``findings`` are validated live findings keyed by finding id (see
    ``validate_live_findings``) and ``triggers`` is the Task Board
    ``jit_triggers`` array. Every material targeting must name an existing
    trigger; a trigger already ``consumed`` while a material finding
    targeting it is still ``pending`` fails closed, since the affected
    trigger cannot be consumed before owning-stage reconciliation.
    Returns the pending hold set: trigger ids mapped to the sorted
    blocking finding ids. Untargeted triggers, explicitly unrelated
    findings, findings without a downstream disposition and reconciled
    findings impose no hold. Reconciliation content is verified by
    readback at the serving boundary (see
    ``verify_finding_trigger_records``).
    """
    if triggers is None:
        triggers = []
    if not isinstance(triggers, list):
        raise LiveFindingError("task_board jit_triggers must be an array of trigger records")
    states: dict[str, str] = {}
    for index, trigger in enumerate(triggers):
        if not isinstance(trigger, Mapping):
            raise LiveFindingError(
                f"task_board.jit_triggers[{index}]: trigger must be a table"
            )
        trigger_id = trigger.get("id")
        if not isinstance(trigger_id, str) or not trigger_id.strip():
            raise LiveFindingError(
                f"task_board.jit_triggers[{index}]: trigger id must be a non-empty string"
            )
        state = trigger.get("state")
        if not isinstance(state, str) or not state.strip():
            raise LiveFindingError(
                f"task_board.jit_triggers[{index}]: trigger state must be a non-empty string"
            )
        states[trigger_id] = state
    holds: dict[str, list[str]] = {}
    for finding_id in sorted(findings):
        finding = findings[finding_id]
        downstream = finding.get("downstream")
        if not isinstance(downstream, Mapping):
            continue
        if downstream.get("disposition") != "material":
            continue
        trigger_id = downstream.get("trigger")
        if trigger_id not in states:
            raise LiveFindingError(
                f"live finding {finding_id!r} targets unknown JIT trigger "
                f"{trigger_id!r}; missing, stale or forged targeting fails closed"
            )
        if downstream.get("reconciliation") == "reconciled":
            continue
        if states[trigger_id] == "consumed":
            raise LiveFindingError(
                f"JIT trigger {trigger_id!r} is consumed while material live "
                f"finding {finding_id!r} is still pending reconciliation; the "
                "affected trigger cannot be consumed before the owning stage "
                f"{finding.get('owner_stage')!r} reconciles"
            )
        holds.setdefault(trigger_id, []).append(finding_id)
    return {trigger_id: sorted(ids) for trigger_id, ids in sorted(holds.items())}


def require_reconciled_trigger_consumption(
    board: Mapping[str, Any],
    trigger_id: str,
    *,
    record_reader: Callable[[str], str | None] | None = None,
) -> str:
    """Require owning-stage reconciliation before one trigger is consumed.

    ``board`` is the Task Board table and ``trigger_id`` names the JIT
    trigger Execution Prep is about to consume. The trigger must exist and
    no material live finding targeting it may still be pending: pending
    blockers fail closed naming the findings and their owning stages.
    Unrelated findings, findings without a downstream disposition and
    reconciled findings never block. When ``record_reader`` is given, the
    targeting findings' materiality evidence and reconciliation decisions
    must additionally read back and verify by content; citation shape
    alone never releases the hold. Trigger lifecycle (waiting, satisfied,
    DONE predecessor) stays owned by the state contract — this guard owns
    reconciliation only. Returns the trigger id.
    """
    if not isinstance(board, Mapping):
        raise LiveFindingError("trigger consumption requires a Task Board table")
    workstream_id = board.get("workstream_id")
    if not isinstance(workstream_id, str) or not workstream_id.strip():
        raise LiveFindingError(
            "trigger consumption requires a workstream-bound Task Board"
        )
    triggers = board.get("jit_triggers", [])
    if not isinstance(triggers, list) or not any(
        isinstance(trigger, Mapping) and trigger.get("id") == trigger_id
        for trigger in triggers
    ):
        raise LiveFindingError(
            f"JIT trigger {trigger_id!r} does not exist on this Task Board; "
            "consuming an unknown trigger fails closed"
        )
    findings = validate_live_findings(board.get("live_findings"), workstream_id)
    holds = validate_finding_trigger_gates(findings, triggers)
    blockers = holds.get(trigger_id, [])
    if blockers:
        owners = sorted({str(findings[fid].get("owner_stage")) for fid in blockers})
        raise LiveFindingError(
            f"JIT trigger {trigger_id!r} is held by pending material live "
            f"finding(s) {', '.join(blockers)}; owning-stage reconciliation "
            f"({', '.join(owners)}) must be accepted and read back before "
            "the affected trigger is consumed"
        )
    if record_reader is not None:
        for finding_id, finding in sorted(findings.items()):
            downstream = finding.get("downstream")
            if not isinstance(downstream, Mapping):
                continue
            if downstream.get("disposition") != "material":
                continue
            if downstream.get("trigger") != trigger_id:
                continue
            for ref in downstream.get("material_evidence_refs", []):
                if record_reader(ref) is None:
                    raise LiveFindingError(
                        f"live finding {finding_id!r} cites durable materiality "
                        f"evidence {ref!r} that cannot be read back; unverifiable "
                        "targeting fails closed to Recovery"
                    )
            acceptance = downstream.get("acceptance")
            if acceptance is None:
                continue
            cited = acceptance["record"]
            verify_reconciliation_decision(
                finding, downstream, cited["path"], record_reader(cited["path"])
            )
    return trigger_id


def verify_finding_trigger_records(
    board: Mapping[str, Any],
    *,
    record_reader: Callable[[str], str | None],
) -> None:
    """Verify cited affected-JIT targeting records by readback.

    ``record_reader`` returns file text for a workstream-local path, or
    ``None`` when the path cannot be read. Every material targeting's
    evidence refs must read back, and every cited reconciliation-decision
    record must read back and prove this finding's reconciliation by
    content: exact finding id and class, exact trigger id, the owning
    stage, and an explicit reconciled decision. Dangling targeting and
    consumed/pending contradictions fail closed as well. A board without
    material findings verifies trivially, preserving historical boards.
    """
    if not isinstance(board, Mapping):
        raise LiveFindingError("affected-JIT verification requires a Task Board table")
    workstream_id = board.get("workstream_id")
    if not isinstance(workstream_id, str) or not workstream_id.strip():
        raise LiveFindingError(
            "affected-JIT verification requires a workstream-bound Task Board"
        )
    findings = validate_live_findings(
        board.get("live_findings"), workstream_id
    )
    material = {
        finding_id: finding
        for finding_id, finding in findings.items()
        if isinstance(finding.get("downstream"), Mapping)
        and finding["downstream"].get("disposition") == "material"
    }
    if not material:
        return
    validate_finding_trigger_gates(findings, board.get("jit_triggers", []))
    for finding_id in sorted(material):
        finding = material[finding_id]
        downstream = finding["downstream"]
        for ref in downstream["material_evidence_refs"]:
            if record_reader(ref) is None:
                raise LiveFindingError(
                    f"live finding {finding_id!r} cites durable materiality "
                    f"evidence {ref!r} that cannot be read back; nonexistent "
                    "materiality evidence fails closed to Recovery"
                )
        acceptance = downstream["acceptance"]
        if acceptance is None:
            continue
        cited = acceptance["record"]
        verify_reconciliation_decision(
            finding, downstream, cited["path"], record_reader(cited["path"])
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
