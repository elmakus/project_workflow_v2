#!/usr/bin/env python3
"""Runtime-neutral semantic Card sizing and decomposition audit (BOOT-B, REQ-118/128/129).

A Card is the smallest meaningful execution-and-review ownership unit producing
one coherent independently falsifiable outcome substantial enough to justify
its own execution/result/review lifecycle. A candidate scope holding two or
more separable acceptance, contract, invariant or independently
useful/consumable delivery outcomes is split by default when each can reach a
valid independently verifiable state and GREEN on one stays valid/useful while
another is RED. Only concrete atomicity, invalid-intermediate-state,
materially inseparable acceptance or material coupling evidence rebuts the
split. File/module/layer/test/tool/step boundaries alone neither force nor
prevent a split, and scaffolding stays with the outcome it enables unless
independently consumed.

Before materializing or merging non-trivial scope, Execution Prep records one
durable sizing audit per affected Card covering all seven accepted dimensions:
independent implementability, falsifiability/testability, reviewability,
invariant/contract family, dependency ordering, atomic mutation/migration
constraints and cross-surface coupling. Omitted dimensions and generic or
missing rebuttal evidence fail closed.

A ``split`` decision never stands in for actual topology: every outcome in a
split audit must durably allocate to a distinct real destination, either an
existing materialized Card (``card:<id>``) or an existing JIT trigger
(``jit:<id>``) for downstream scope whose Card id is not yet knowable. The
allocation must cover every outcome, span at least two distinct destinations,
retain at least one outcome in the audited Card itself, and resolve to
executable Cards or unconsumed triggers bounded after the audited Card;
historical DONE Cards are never valid split destinations, and future Card ids
are never invented. A ``single`` decision must not claim split allocation.

The semantic judgments (is this outcome falsifiable, substantial, separable)
remain Execution Prep owned; this module only validates that the durable
record is complete, internally coherent and honestly classified.

The fresh independent topology challenge and Card/Milestone review layering
(REQ-119..121) live in ``tools/topology_contract.py`` as a second-order
safeguard over this sizing decision. Out of scope here: late oversized-Card
return to Execution Prep (REQ-130), BOOT-C/BOOT-D, and changes to accepted
seam fidelity (REQ-115..117 in ``tools/seam_contract.py``).
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


AUDIT_DIMENSIONS = (
    "independent_implementability",
    "falsifiability_testability",
    "reviewability",
    "invariant_contract_family",
    "dependency_ordering",
    "atomic_mutation_migration",
    "cross_surface_coupling",
)

OUTCOME_KINDS = frozenset({"acceptance", "contract", "invariant", "useful_outcome"})

STRUCTURAL_BOUNDARY_KINDS = frozenset({"file", "module", "layer", "test", "tool", "step"})

SIZING_DECISIONS = frozenset({"single", "split"})

ALLOCATION_KINDS = frozenset({"card", "jit"})

AUDITED_STATUSES = frozenset({"planned", "ready", "in_progress"})

TERMINAL_HISTORY_STATUSES = frozenset({"done", "returned"})

REBUTTAL_CLASSES = frozenset({
    "atomicity",
    "invalid_intermediate_state",
    "inseparable_acceptance",
    "material_coupling",
})

REJECTED_GENERIC_REBUTTAL_CLASSES = frozenset({
    "convenience",
    "same_milestone",
    "same-milestone",
    "same milestone",
    "fewer_cards",
    "fewer-cards",
    "fewer cards",
    "file_boundary",
    "module_boundary",
    "layer_boundary",
    "test_boundary",
    "tool_boundary",
    "step_boundary",
    "scaffolding_colocation",
})

SEAM_ONLY_REBUTTAL_CLASSES = frozenset({"new_predecessor_evidence"})

PLACEHOLDER_AUDIT_STATEMENTS = frozenset({"n/a", "na", "none", "tbd", "todo"})


class CardSizingError(ValueError):
    """Raised when a Card sizing decision or decomposition audit is invalid."""


def _require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise CardSizingError(f"{label} must be a boolean")
    return value


def parse_allocation(value: Any, label: str) -> tuple[str, str]:
    """Parse a durable split allocation of the form ``card:<id>`` or ``jit:<id>``.

    Returns the ``(kind, ref)`` pair. Anything else fails closed: a split
    allocation must name an existing materialized Card boundary or an existing
    JIT trigger boundary, never a speculative future Card id.
    """
    if not isinstance(value, str):
        raise CardSizingError(f"{label} must be a string")
    kind, sep, ref = value.partition(":")
    if sep != ":" or kind not in ALLOCATION_KINDS or not ref.strip():
        raise CardSizingError(
            f"{label}: invalid split allocation {value!r}; expected "
            "card:<materialized Card id> or jit:<existing JIT trigger id>"
        )
    return kind, ref


def validate_outcome(outcome: Mapping[str, Any], label: str) -> dict[str, Any]:
    """Validate one durable candidate outcome record.

    Each outcome names a semantic ``kind`` (acceptance/contract/invariant/
    useful_outcome), a non-empty durable ``statement``, and the
    invariant/contract ``family`` it belongs to. Structural file/module/layer/
    test/tool/step fragments are rejected: such boundaries alone neither force
    nor prevent a split. Outcomes that are not independently falsifiable or
    not substantial enough for their own lifecycle are rejected as meaningless
    micro-Cards, as is scaffolding that is not independently consumed. An
    optional ``allocated_to`` field carries a split allocation
    (``card:<id>`` or ``jit:<id>``); its format is validated here while
    destination resolution happens against the Task Board.
    """
    if not isinstance(outcome, Mapping):
        raise CardSizingError(f"{label}: outcome must be a table")
    outcome_id = outcome.get("id")
    if not isinstance(outcome_id, str) or not outcome_id.strip():
        raise CardSizingError(f"{label}: outcome id must be a non-empty string")
    kind = outcome.get("kind")
    if kind in STRUCTURAL_BOUNDARY_KINDS:
        raise CardSizingError(
            f"{label}: structural {kind!r} boundary alone neither forces nor prevents "
            "a split; restate the outcome as a separable acceptance, contract, "
            "invariant or independently useful/consumable delivery outcome"
        )
    if kind not in OUTCOME_KINDS:
        raise CardSizingError(
            f"{label}: unknown outcome kind {kind!r}; expected one of acceptance, "
            "contract, invariant, useful_outcome"
        )
    statement = outcome.get("statement")
    if not isinstance(statement, str) or not statement.strip():
        raise CardSizingError(f"{label}: outcome statement must be a durable non-empty statement")
    family = outcome.get("family")
    if not isinstance(family, str) or not family.strip():
        raise CardSizingError(
            f"{label}: outcome family must name a non-empty invariant/contract family"
        )
    independently_verifiable = _require_bool(
        outcome.get("independently_verifiable"), f"{label}: independently_verifiable"
    )
    independently_useful = _require_bool(
        outcome.get("independently_useful"), f"{label}: independently_useful"
    )
    falsifiable = _require_bool(outcome.get("falsifiable"), f"{label}: falsifiable")
    substantial = _require_bool(outcome.get("substantial"), f"{label}: substantial")
    scaffolding_only = _require_bool(outcome.get("scaffolding_only", False), f"{label}: scaffolding_only")
    independently_consumed = _require_bool(
        outcome.get("independently_consumed", False), f"{label}: independently_consumed"
    )
    if not falsifiable:
        raise CardSizingError(
            f"{label}: outcome is not independently falsifiable; a Card must produce "
            "one coherent independently falsifiable outcome"
        )
    if not substantial:
        raise CardSizingError(
            f"{label}: outcome is not substantial enough to justify its own "
            "execution/result/review lifecycle; meaningless micro-Cards are rejected"
        )
    if scaffolding_only and not independently_consumed:
        raise CardSizingError(
            f"{label}: scaffolding stays with the outcome it enables unless "
            "independently consumed"
        )
    allocated_to = outcome.get("allocated_to", "")
    if allocated_to != "":
        parse_allocation(allocated_to, f"{label}: allocated_to")
    return {
        "id": outcome_id,
        "kind": str(kind),
        "statement": statement,
        "family": family,
        "independently_verifiable": independently_verifiable,
        "independently_useful": independently_useful,
        "falsifiable": falsifiable,
        "substantial": substantial,
        "scaffolding_only": scaffolding_only,
        "independently_consumed": independently_consumed,
        "allocated_to": allocated_to if isinstance(allocated_to, str) else "",
    }


def validate_outcomes(outcomes: Iterable[Mapping[str, Any]], label: str) -> list[dict[str, Any]]:
    """Validate a non-empty candidate outcome set with unique outcome ids."""
    if not isinstance(outcomes, list):
        raise CardSizingError(f"{label}: outcomes must be an array of outcome records")
    if not outcomes:
        raise CardSizingError(f"{label}: at least one meaningful outcome is required")
    records = [validate_outcome(outcome, f"{label}[{index}]") for index, outcome in enumerate(outcomes)]
    seen: set[str] = set()
    for record in records:
        if record["id"] in seen:
            raise CardSizingError(f"{label}: duplicate outcome id {record['id']!r}")
        seen.add(record["id"])
    return records


def separable_outcomes(outcomes: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    """Return outcomes that are separable: independently verifiable and useful.

    An outcome is separable when it can reach a valid independently verifiable
    state and GREEN on it stays valid/useful while a sibling outcome is RED.
    """
    return [
        dict(outcome)
        for outcome in outcomes
        if outcome.get("independently_verifiable") is True
        and outcome.get("independently_useful") is True
    ]


def required_decision(outcomes: Iterable[Mapping[str, Any]]) -> str:
    """Return the presumptive sizing decision: ``\"split\"`` for two or more
    separable outcomes, else ``\"single\"``."""
    return "split" if len(separable_outcomes(outcomes)) >= 2 else "single"


def validate_rebuttal(
    *,
    rebuttal_class: object,
    rebuttal: object,
    label: str,
) -> str:
    """Require concrete qualifying evidence rebutting the split presumption.

    Only concrete atomicity, invalid-intermediate-state, materially
    inseparable acceptance or material coupling evidence qualifies. Generic
    convenience / same-milestone / fewer-cards claims, structural-boundary
    claims and empty rationale are rejected, as is seam-only predecessor
    evidence, which justifies seam deviation but never a sizing split rebuttal.
    """
    if rebuttal_class in REJECTED_GENERIC_REBUTTAL_CLASSES:
        raise CardSizingError(
            f"{label}: generic {rebuttal_class!r} evidence cannot rebut the split "
            "presumption; expected one of atomicity, invalid_intermediate_state, "
            "inseparable_acceptance, material_coupling"
        )
    if rebuttal_class in SEAM_ONLY_REBUTTAL_CLASSES:
        raise CardSizingError(
            f"{label}: {rebuttal_class!r} justifies Planning-seam deviation, not a "
            "Card-sizing split rebuttal; expected one of atomicity, "
            "invalid_intermediate_state, inseparable_acceptance, material_coupling"
        )
    if rebuttal_class not in REBUTTAL_CLASSES:
        raise CardSizingError(
            f"{label}: unknown rebuttal class {rebuttal_class!r}; expected one of "
            "atomicity, invalid_intermediate_state, inseparable_acceptance, "
            "material_coupling"
        )
    if not isinstance(rebuttal, str) or not rebuttal.strip():
        raise CardSizingError(f"{label}: split rebuttal requires durable non-empty evidence")
    return str(rebuttal_class)


def validate_sizing_decision(
    *,
    outcomes: Iterable[Mapping[str, Any]],
    decision: str,
    rebuttal_class: str = "",
    rebuttal: str = "",
    label: str = "sizing",
) -> str:
    """Validate one durable Card sizing decision against the split presumption.

    Returns the validated decision. A ``\"single`` decision over two or more
    separable outcomes requires qualifying concrete rebuttal; a ``\"split\"``
    decision over a coherent non-separable scope is rejected as meaningless
    fragmentation; and a decision that follows the presumption must not claim
    deviation rationale. A ``split`` decision must also durably allocate every
    outcome to a real destination across at least two distinct destinations,
    so the audit cannot stand in for actual topology; a ``single`` decision
    must not claim split allocation. Destination resolution against materialized
    Cards and JIT triggers happens at Task Board level.
    """
    records = validate_outcomes(list(outcomes), f"{label}.outcomes")
    if decision not in SIZING_DECISIONS:
        raise CardSizingError(
            f"{label}: unknown sizing decision {decision!r}; expected one of single, split"
        )
    if not isinstance(rebuttal_class, str) or not isinstance(rebuttal, str):
        raise CardSizingError(f"{label}: rebuttal_class and rebuttal must be strings")
    if decision == "single" and any(record["allocated_to"] for record in records):
        raise CardSizingError(
            f"{label}: a single decision owns its scope in this Card and must not "
            "claim split allocation"
        )
    presumption = required_decision(records)
    if presumption == "split" and decision == "single":
        validate_rebuttal(rebuttal_class=rebuttal_class, rebuttal=rebuttal, label=label)
        return decision
    if presumption == "single" and decision == "split":
        raise CardSizingError(
            f"{label}: a coherent non-separable scope must not be split into "
            "meaningless micro-Cards"
        )
    if rebuttal_class.strip() or rebuttal.strip():
        raise CardSizingError(
            f"{label}: a {decision} decision that follows the split presumption "
            "must not claim deviation rationale"
        )
    if decision == "split":
        validate_split_coverage(records, label)
    return decision


def validate_split_coverage(
    outcomes: Iterable[Mapping[str, Any]], label: str
) -> list[str]:
    """Require complete durable split allocation across distinct destinations.

    Every outcome in a split decision must name its destination Card or JIT
    trigger, and the destinations must span at least two distinct boundaries:
    a split that allocates everything to one destination is not a split.
    Returns the sorted distinct destinations.
    """
    records = list(outcomes)
    uncovered = sorted(record["id"] for record in records if not record.get("allocated_to"))
    if uncovered:
        raise CardSizingError(
            f"{label}: split decision leaves outcome(s) without durable allocation: "
            + ", ".join(uncovered)
        )
    destinations = sorted({str(record["allocated_to"]) for record in records})
    if len(destinations) < 2:
        raise CardSizingError(
            f"{label}: split decision allocates every outcome to one destination "
            f"{destinations[0]!r}; a split must span at least two distinct Card or "
            "JIT trigger boundaries"
        )
    return destinations


def validate_audit_dimensions(
    dimensions: Mapping[str, Any], label: str
) -> dict[str, str]:
    """Require an explicit durable statement for every accepted audit dimension.

    All seven dimensions (independent implementability,
    falsifiability/testability, reviewability, invariant/contract family,
    dependency ordering, atomic mutation/migration constraints, cross-surface
    coupling) must each carry a non-empty, non-placeholder statement. Omitted,
    empty, placeholder or undeclared dimensions fail closed.
    """
    if not isinstance(dimensions, Mapping):
        raise CardSizingError(f"{label}: dimensions must be a table")
    unknown = sorted(set(dimensions) - set(AUDIT_DIMENSIONS))
    if unknown:
        raise CardSizingError(
            f"{label}: unknown audit dimension(s): {', '.join(unknown)}; expected only "
            + ", ".join(AUDIT_DIMENSIONS)
        )
    missing = [name for name in AUDIT_DIMENSIONS if name not in dimensions]
    if missing:
        raise CardSizingError(
            f"{label}: missing durable audit for dimension(s): {', '.join(missing)}"
        )
    records: dict[str, str] = {}
    for name in AUDIT_DIMENSIONS:
        statement = dimensions[name]
        if not isinstance(statement, str) or not statement.strip():
            raise CardSizingError(
                f"{label}: audit dimension {name!r} requires a durable non-empty statement"
            )
        if statement.strip().lower() in PLACEHOLDER_AUDIT_STATEMENTS:
            raise CardSizingError(
                f"{label}: audit dimension {name!r} carries placeholder evidence, "
                "not a durable audit statement"
            )
        records[name] = statement
    return records


def validate_sizing_audit(audit: Mapping[str, Any], label: str) -> dict[str, Any]:
    """Validate one durable pre-materialization/merge sizing audit record."""
    if not isinstance(audit, Mapping):
        raise CardSizingError(f"{label}: sizing audit must be a table")
    card_id = audit.get("card_id")
    if not isinstance(card_id, str) or not card_id.strip():
        raise CardSizingError(f"{label}: card_id must be a non-empty string")
    decision = audit.get("decision")
    if not isinstance(decision, str):
        raise CardSizingError(f"{label}: decision must be a string")
    validated_decision = validate_sizing_decision(
        outcomes=audit.get("outcomes", []),  # type: ignore[arg-type]
        decision=decision,
        rebuttal_class=audit.get("rebuttal_class", ""),  # type: ignore[arg-type]
        rebuttal=audit.get("rebuttal", ""),  # type: ignore[arg-type]
        label=label,
    )
    dimensions = validate_audit_dimensions(audit.get("dimensions", {}), f"{label}.dimensions")  # type: ignore[arg-type]
    outcomes = validate_outcomes(audit.get("outcomes", []), f"{label}.outcomes")  # type: ignore[arg-type]
    return {
        "card_id": card_id,
        "decision": validated_decision,
        "dimensions": dimensions,
        "outcomes": outcomes,
    }


def validate_split_resolution(
    outcomes: Iterable[Mapping[str, Any]],
    cards_by_id: Mapping[str, Mapping[str, Any]],
    triggers_by_id: Mapping[str, Mapping[str, Any]],
    label: str,
    audited_card_id: str,
) -> None:
    """Resolve every split allocation against real Task Board boundaries.

    The audited Card must retain at least one outcome: a split audit that
    allocates every outcome away leaves its own Card with no coherent outcome.
    ``card:<id>`` destinations must name a materialized Card in an executable
    lifecycle status: historical DONE Cards never own split scope, and blocked
    Cards cannot accept new scope while blocked. ``jit:<id>`` destinations
    must name an existing unconsumed JIT trigger bounded after the audited
    Card itself, preserving valid JIT where the downstream Card id is not yet
    knowable. Dangling destinations fail closed.
    """
    records = list(outcomes)
    retained = f"card:{audited_card_id}"
    if not any(record.get("allocated_to") == retained for record in records):
        raise CardSizingError(
            f"{label}: split audit must retain at least one outcome in the "
            f"audited Card {retained!r}; a split audit cannot allocate every "
            "outcome away"
        )
    for record in records:
        outcome_label = f"{label}.outcomes[{record['id']}]"
        kind, ref = parse_allocation(record.get("allocated_to"), f"{outcome_label}: allocated_to")
        if kind == "card":
            if ref not in cards_by_id:
                raise CardSizingError(
                    f"{outcome_label}: split allocation names unknown Card {ref!r}; "
                    "split scope must land on a materialized Card boundary"
                )
            status = cards_by_id[ref].get("status")
            if status == "done":
                raise CardSizingError(
                    f"{outcome_label}: split allocation names terminal DONE Card "
                    f"{ref!r}; historical Cards never own split scope"
                )
            if status not in AUDITED_STATUSES:
                raise CardSizingError(
                    f"{outcome_label}: split allocation names {status} Card {ref!r}; "
                    "split scope must land on a planned, ready or in_progress Card "
                    "or an unconsumed JIT trigger"
                )
        else:
            if ref not in triggers_by_id:
                raise CardSizingError(
                    f"{outcome_label}: split allocation names unknown JIT trigger "
                    f"{ref!r}; split scope must land on an existing trigger boundary"
                )
            trigger = triggers_by_id[ref]
            if trigger.get("state") == "consumed":
                raise CardSizingError(
                    f"{outcome_label}: split allocation names consumed JIT trigger "
                    f"{ref!r}; allocate to the materialized Card instead"
                )
            if trigger.get("after_card") != audited_card_id:
                raise CardSizingError(
                    f"{outcome_label}: split allocation names JIT trigger {ref!r} "
                    f"bounded after Card {trigger.get('after_card')!r}, not the "
                    f"audited Card {audited_card_id!r}; split scope may only defer "
                    "through the audited Card's own downstream triggers"
                )


def validate_sizing_audits(
    audits: Iterable[Mapping[str, Any]] | None,
    cards: Iterable[Mapping[str, Any]],
    jit_triggers: Iterable[Mapping[str, Any]] | None = None,
) -> dict[str, str]:
    """Validate durable Task Board sizing audits against materialized Cards.

    Every audit must bind an existing Card id exactly once, and every Card in
    an executable lifecycle status (``planned``/``ready``/``in_progress``)
    must carry exactly one audit: omitting the audit array, or omitting one
    active Card from it, is a bypass, not a trivial-scope exemption. Trivial
    single-outcome scope is recorded the same way, with one coherent outcome
    and no separability; there is no silent omission path. ``done`` Cards are
    exempt so historical terminal state stays valid, as are ``blocked`` Cards
    while blocked so legacy migrated boards validate; any return to an
    executable status re-triggers the gate. Split allocations resolve against
    materialized Cards and JIT triggers while the audited Card is executable:
    unretained, dangling, terminal, consumed or foreign-predecessor
    destinations fail closed. ``done`` and ``returned`` Cards keep their
    audits as immutable history with shape/decision/coverage rules still
    enforced, but destination liveness is not re-checked: fulfilled
    destinations (completed Cards, consumed triggers) are success, not
    violation. Returns the Card id to validated-decision mapping.
    """
    if audits is None:
        audits = []
    if not isinstance(audits, list):
        raise CardSizingError("task_board sizing_audits must be an array of audit records")
    cards_by_id = {card["id"]: card for card in cards}
    triggers_by_id = {trigger["id"]: trigger for trigger in (jit_triggers or [])}
    decisions: dict[str, str] = {}
    for index, audit in enumerate(audits):
        label = f"task_board.sizing_audits[{index}]"
        if not isinstance(audit, Mapping):
            raise CardSizingError(f"{label}: sizing audit must be a table")
        card_id = audit.get("card_id")
        if not isinstance(card_id, str) or not card_id.strip():
            raise CardSizingError(f"{label}: card_id must be a non-empty string")
        if card_id in decisions:
            raise CardSizingError(f"{label}: duplicate sizing audit for Card {card_id!r}")
        if card_id not in cards_by_id:
            raise CardSizingError(
                f"{label}: unknown card_id {card_id!r}; sizing audits must bind "
                "a materialized Task Board Card"
            )
        try:
            record = validate_sizing_audit(audit, label)
        except CardSizingError as exc:
            raise CardSizingError(f"{exc}") from exc
        if (
            record["decision"] == "split"
            and cards_by_id[card_id].get("status") not in TERMINAL_HISTORY_STATUSES
        ):
            try:
                validate_split_resolution(
                    record["outcomes"], cards_by_id, triggers_by_id, label, card_id
                )
            except CardSizingError as exc:
                raise CardSizingError(f"{exc}") from exc
        decisions[card_id] = record["decision"]
    missing = sorted(
        card_id
        for card_id, card in cards_by_id.items()
        if card.get("status") in AUDITED_STATUSES and card_id not in decisions
    )
    if missing:
        raise CardSizingError(
            "task_board.sizing_audits: missing durable sizing audit for "
            + ", ".join(f"Card {card_id!r}" for card_id in missing)
        )
    return decisions
