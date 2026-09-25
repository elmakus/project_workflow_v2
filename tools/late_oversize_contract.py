#!/usr/bin/env python3
"""Runtime-neutral late-oversize Card return (BOOT-B, REQ-130).

When execution or review first produces material evidence that an active Card
is oversized or contains newly exposed separable review-worthy outcomes, the
Worker must not silently broaden, merge, self-split or rewrite Card authority.
At the smallest safe durable boundary the independently valid evidence is
preserved on the current Card and only the remaining unaccepted scope returns
to Execution Prep for bounded re-decomposition; stronger accepted Planning
seams remain authoritative unless revised by their owning stage.

The return is recorded durably in ``TASK_BOARD.toml`` (``late_oversize_returns``,
one record per returning Card) and routes through the router to Execution Prep.
It is not a new product-scope authorization and never declares the current Card
GREEN. The record is never removed: it moves from ``pending`` (residual scope
not yet materialized; the returning Card stays ``in_progress``) to
``residual_bound`` (the residual Card is materialized with its own T04/T05/T06
gates), and persists as durable handoff evidence after the original reaches its
non-GREEN terminal disposition — status ``returned`` with the bound return,
explicitly marked ``claims_green = false``, retaining any existing result,
review history and preserved evidence. Full ``done`` stays reserved for
accepted GREEN-reviewed Card completion and can never hold a return. The
residual trigger advances only through a distinct validated handoff path bound
to the residual Card once the original is ``returned``; a ``returned`` Card is
never a full DONE predecessor.

Binding is by outcome coverage, not Card id alone: every residual outcome
must match the residual anchor Card's sizing audit on identity and content,
the anchor audit must persist while bound, and consumed JIT triggers on the
covered graph must record their materialized Card (``jit_resolutions``).
Close requires every residual outcome to terminate in accepted downstream
Cards through allocations, resolutions, and chained handoffs.

A normal implementation defect correctable inside the Card and a trivial
structural fragment are not oversize evidence and are rejected here; BOOT-C
live-finding classification and BOOT-D Worker discipline stay out of scope.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from pathlib import PurePosixPath
from typing import Any

try:
    from tools.card_sizing_contract import (
        CardSizingError,
        parse_allocation,
        separable_outcomes,
        validate_outcome,
    )
except ModuleNotFoundError:  # direct script execution from tools/
    from card_sizing_contract import (
        CardSizingError,
        parse_allocation,
        separable_outcomes,
        validate_outcome,
    )

LATE_ORIGINS = frozenset({"execution", "review"})

LATE_RETURN_STATES = frozenset({"pending", "residual_bound"})

RETURNING_STATUSES = frozenset({"in_progress"})

BOUND_CARD_STATUSES = frozenset({"in_progress", "returned"})


class LateOversizeError(ValueError):
    """Raised when a late-oversize return record or topology action is invalid."""


def _require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise LateOversizeError(f"{label} must be a boolean")
    return value


def _require_statement(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LateOversizeError(
            f"{label} requires a durable non-empty statement"
        )
    return value


def _validate_preserved_refs(
    refs: Any, label: str, workstream_id: str
) -> list[str]:
    """Validate workstream-local preserved-evidence locators.

    Each ref must be a workstream-local ``evidence/*.md`` path without
    traversal. The list may be empty only when the durable preserved basis
    explicitly accounts for the absence; existence is verified by the router
    when it serves the pending return.
    """
    if not isinstance(refs, list):
        raise LateOversizeError(f"{label} must be an array of evidence refs")
    prefix = f"implementation/workstreams/{workstream_id}/evidence/"
    seen: set[str] = set()
    for index, ref in enumerate(refs):
        item = f"{label}[{index}]"
        if not isinstance(ref, str) or not ref:
            raise LateOversizeError(f"{item}: evidence ref must be a non-empty string")
        path = PurePosixPath(ref)
        if (
            path.is_absolute()
            or "." in path.parts
            or ".." in path.parts
            or not ref.startswith(prefix)
            or not ref.endswith(".md")
        ):
            raise LateOversizeError(
                f"{item}: invalid workstream evidence ref {ref!r}; expected "
                f"{prefix}*.md"
            )
        if ref in seen:
            raise LateOversizeError(f"{item}: duplicate evidence ref {ref!r}")
        seen.add(ref)
    return list(refs)


def _validate_residual_outcomes(outcomes: Any, label: str) -> list[dict[str, Any]]:
    """Require at least one separable review-worthy residual outcome.

    Each outcome reuses the T05 semantic outcome contract: structural
    file/module/layer/test/tool/step fragments and non-falsifiable or
    insubstantial micro-Cards are rejected there. Every residual outcome must
    additionally be separable (independently verifiable and independently
    useful), so ordinary bugs and trivial fragments cannot masquerade as
    oversize scope needing re-decomposition.
    """
    if not isinstance(outcomes, list) or not outcomes:
        raise LateOversizeError(
            f"{label} requires at least one separable review-worthy outcome"
        )
    records: list[dict[str, Any]] = []
    for index, outcome in enumerate(outcomes):
        try:
            record = validate_outcome(outcome, f"{label}[{index}]")
        except CardSizingError as exc:
            raise LateOversizeError(f"{exc}") from exc
        records.append(record)
    non_separable = [
        record["id"] for record in records
        if record.get("independently_verifiable") is not True
        or record.get("independently_useful") is not True
    ]
    if non_separable:
        raise LateOversizeError(
            f"{label}: residual outcome(s) are not separable review-worthy "
            "outcomes: " + ", ".join(non_separable)
        )
    if not separable_outcomes(records):
        raise LateOversizeError(
            f"{label} requires at least one separable review-worthy outcome"
        )
    seen: set[str] = set()
    for record in records:
        if record["id"] in seen:
            raise LateOversizeError(
                f"{label}: duplicate outcome id {record['id']!r}; residual "
                "outcomes must be uniquely identifiable downstream"
            )
        seen.add(record["id"])
    return records


def _validate_residual_coverage(
    residuals: list[dict[str, Any]],
    audit: Mapping[str, Any],
    label: str,
    anchor_id: str,
) -> None:
    """Require every residual outcome to be covered in the anchor audit.

    Each residual outcome must match an outcome in the residual (anchor)
    Card's T05 sizing audit on identity and content (id, kind, statement,
    family). Missing coverage means unaccepted scope would be silently
    dropped; changed content means relabelled scope would silently replace
    the returned outcome. Extra anchor outcomes beyond the residual set are
    allowed: re-decomposition may legitimately reframe scope, but it must
    never lose returned scope.
    """
    by_id: dict[str, Mapping[str, Any]] = {}
    outcomes = audit.get("outcomes", [])
    if isinstance(outcomes, list):
        for outcome in outcomes:
            if isinstance(outcome, Mapping) and isinstance(outcome.get("id"), str):
                by_id[outcome["id"]] = outcome
    for residual in residuals:
        rid = residual.get("id", "")
        covering = by_id.get(rid)
        if covering is None:
            raise LateOversizeError(
                f"{label}: residual outcome {rid!r} has no covering outcome "
                f"in residual Card {anchor_id!r} sizing audit; every returned "
                "outcome must be covered downstream or unaccepted scope is "
                "silently lost"
            )
        for field in ("kind", "statement", "family"):
            if covering.get(field) != residual.get(field):
                raise LateOversizeError(
                    f"{label}: residual outcome {rid!r} changed downstream "
                    f"({field} differs in residual Card {anchor_id!r} sizing "
                    "audit); relabelled scope cannot silently replace the "
                    "returned outcome"
                )


def _validate_jit_resolutions(
    resolutions: Any,
    label: str,
    *,
    card_id: str,
    anchor_id: str,
    anchor_audit: Mapping[str, Any],
    cards_by_id: Mapping[str, Mapping[str, Any]],
    triggers_by_id: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, str]]:
    """Validate trigger-to-Card bindings for JIT-allocated residual outcomes.

    A resolution records which materialized Card a consumed JIT trigger
    became — the linkage triggers themselves lack. Each entry must name an
    existing consumed trigger actually referenced by a ``jit:<id>`` allocation
    in the anchor sizing audit, and an existing Card that is neither the
    returning Card nor its anchor. Unresolved or premature bindings fail
    closed so downstream completion stays checkable.
    """
    if not isinstance(resolutions, list):
        raise LateOversizeError(f"{label} must be an array of trigger bindings")
    allocated: set[str] = set()
    outcomes = anchor_audit.get("outcomes", [])
    if isinstance(outcomes, list):
        for outcome in outcomes:
            if not isinstance(outcome, Mapping):
                continue
            dest = outcome.get("allocated_to", "")
            if isinstance(dest, str) and dest.startswith("jit:"):
                allocated.add(dest[4:])
    seen: set[str] = set()
    validated: list[dict[str, str]] = []
    for index, entry in enumerate(resolutions):
        item = f"{label}[{index}]"
        if not isinstance(entry, Mapping):
            raise LateOversizeError(f"{item}: resolution must be a table")
        trigger_id = entry.get("trigger")
        target_id = entry.get("card")
        if not isinstance(trigger_id, str) or not trigger_id.strip():
            raise LateOversizeError(f"{item}: trigger must be a non-empty string")
        if not isinstance(target_id, str) or not target_id.strip():
            raise LateOversizeError(f"{item}: card must be a non-empty string")
        if trigger_id in seen:
            raise LateOversizeError(
                f"{item}: duplicate resolution for trigger {trigger_id!r}"
            )
        seen.add(trigger_id)
        trigger = triggers_by_id.get(trigger_id)
        if trigger is None:
            raise LateOversizeError(
                f"{item}: unknown JIT trigger {trigger_id!r}; resolutions "
                "must bind an existing trigger"
            )
        if target_id not in cards_by_id:
            raise LateOversizeError(
                f"{item}: unknown Card {target_id!r}; resolutions must bind "
                "a materialized Card"
            )
        if target_id == card_id or target_id == anchor_id:
            raise LateOversizeError(
                f"{item}: resolution card must name a different Card than "
                f"the returning Card {card_id!r} or its residual anchor "
                f"{anchor_id!r}"
            )
        if trigger.get("state") != "consumed":
            raise LateOversizeError(
                f"{item}: trigger {trigger_id!r} is {trigger.get('state')}; "
                "a resolution attests materialization, so only consumed "
                "triggers may be bound"
            )
        if trigger_id not in allocated:
            raise LateOversizeError(
                f"{item}: trigger {trigger_id!r} is not allocated any "
                "residual outcome in the anchor sizing audit; resolutions "
                "must attach to real residual allocations"
            )
        validated.append({"trigger": trigger_id, "card": target_id})
    return validated


def validate_late_return(
    record: Mapping[str, Any],
    label: str,
    *,
    cards_by_id: Mapping[str, Mapping[str, Any]],
    triggers_by_id: Mapping[str, Mapping[str, Any]],
    workstream_id: str,
    sizing_audits_by_id: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Validate one durable late-oversize return record.

    A ``pending`` record binds an ``in_progress`` Card (late evidence arises
    only during execution or review), names the material new evidence,
    distinguishes preserved independently valid evidence from the residual
    unaccepted scope, and parks that residual scope on the Card's own waiting
    downstream JIT trigger — the smallest safe durable boundary for Execution
    Prep re-decomposition. A ``residual_bound`` record additionally names the
    materialized residual Card and persists through the original's non-GREEN
    terminal disposition (status ``returned``). A ``done`` Card can never hold
    a return: done stays reserved for accepted GREEN-reviewed completion.
    Review-origin returns must bind one exact durable review attempt locator
    on the same Card so history is preserved, never erased. Bounded
    correction, required-seam merges and GREEN claims are rejected.
    """
    if not isinstance(record, Mapping):
        raise LateOversizeError(f"{label}: late-oversize return must be a table")
    card_id = record.get("card_id")
    if not isinstance(card_id, str) or not card_id.strip():
        raise LateOversizeError(f"{label}: card_id must be a non-empty string")
    card = cards_by_id.get(card_id)
    if card is None:
        raise LateOversizeError(
            f"{label}: unknown card_id {card_id!r}; late-oversize returns must "
            "bind a materialized Task Board Card"
        )
    state = record.get("state")
    if state not in LATE_RETURN_STATES:
        raise LateOversizeError(
            f"{label}: unknown return state {state!r}; expected one of "
            "pending, residual_bound"
        )
    status = card.get("status")
    if status == "done":
        raise LateOversizeError(
            f"{label}: Card {card_id!r} is done with a late-oversize return; "
            "done is reserved for accepted GREEN-reviewed Card completion — "
            "a handed-off original uses the returned disposition, never done"
        )
    residual_card = record.get("residual_card", "")
    if not isinstance(residual_card, str):
        raise LateOversizeError(f"{label}: residual_card must be a string")
    if state == "pending":
        if status not in RETURNING_STATUSES:
            raise LateOversizeError(
                f"{label}: Card {card_id!r} is {status} with a pending "
                "late-oversize return; only an in_progress Card may hold a "
                "pending return — planned/ready scope uses the prelaunch "
                "sizing/topology gates, blocked Cards route via their "
                "blocker, and a returned terminal Card requires a bound "
                "residual, so the residual must be bound before the original "
                "goes terminal"
            )
        if residual_card.strip():
            raise LateOversizeError(
                f"{label}: a pending return must not claim residual_card "
                "binding; Execution Prep binds the materialized residual Card "
                "when the return moves to residual_bound"
            )
        if record.get("jit_resolutions", []):
            raise LateOversizeError(
                f"{label}: a pending return must not claim jit_resolutions; "
                "trigger-to-Card bindings are recorded once downstream Cards "
                "materialize under a bound return"
            )
    else:
        if status not in BOUND_CARD_STATUSES:
            raise LateOversizeError(
                f"{label}: Card {card_id!r} is {status} with a bound "
                "late-oversize return; only an in_progress Card awaiting "
                "handoff finalization or a returned non-GREEN terminal Card "
                "may hold a bound return"
            )
        if not residual_card.strip():
            raise LateOversizeError(
                f"{label}: a residual_bound return requires residual_card "
                "naming the materialized residual Card"
            )
        if residual_card == card_id:
            raise LateOversizeError(
                f"{label}: residual_card must name a different Card than the "
                f"returning Card {card_id!r}"
            )
        if residual_card not in cards_by_id:
            raise LateOversizeError(
                f"{label}: unknown residual Card {residual_card!r}; the bound "
                "residual must be a materialized Task Board Card"
            )
    origin = record.get("origin")
    if origin not in LATE_ORIGINS:
        raise LateOversizeError(
            f"{label}: unknown origin {origin!r}; expected one of execution, review"
        )
    origin_attempt = record.get("origin_attempt", "")
    if not isinstance(origin_attempt, str):
        raise LateOversizeError(f"{label}: origin_attempt must be a string")
    origin_attempt_path = record.get("origin_attempt_path", "")
    if not isinstance(origin_attempt_path, str):
        raise LateOversizeError(f"{label}: origin_attempt_path must be a string")
    attempts = card.get("review_attempts", [])
    if origin == "review":
        if not origin_attempt.strip():
            raise LateOversizeError(
                f"{label}: origin_attempt must name the originating review "
                "attempt for a review-discovered return"
            )
        if not isinstance(attempts, list) or not attempts:
            raise LateOversizeError(
                f"{label}: a review-discovered return requires at least one "
                "durable review_attempt locator on the Card; prior review "
                "history must be preserved, never erased"
            )
        if not origin_attempt_path.strip():
            raise LateOversizeError(
                f"{label}: origin_attempt_path must name the exact durable "
                "review attempt locator carrying the originating attempt"
            )
        locator_paths = [
            attempt.get("path")
            for attempt in attempts
            if isinstance(attempt, Mapping)
        ]
        if origin_attempt_path not in locator_paths:
            raise LateOversizeError(
                f"{label}: origin_attempt_path {origin_attempt_path!r} is not "
                f"a durable review attempt on Card {card_id!r}; foreign or "
                "fabricated attempt bindings are rejected"
            )
    else:
        if origin_attempt.strip():
            raise LateOversizeError(
                f"{label}: origin_attempt must be empty for an "
                "execution-discovered return"
            )
        if origin_attempt_path.strip():
            raise LateOversizeError(
                f"{label}: origin_attempt_path must be empty for an "
                "execution-discovered return"
            )
    material_evidence = _require_statement(
        record.get("material_evidence"), f"{label}: material_evidence"
    )
    preserved_refs = _validate_preserved_refs(
        record.get("preserved_refs", []), f"{label}: preserved_refs",
        workstream_id,
    )
    preserved_basis = _require_statement(
        record.get("preserved_basis"), f"{label}: preserved_basis"
    )
    residual_scope = _require_statement(
        record.get("residual_scope"), f"{label}: residual_scope"
    )
    residual_outcomes = _validate_residual_outcomes(
        record.get("residual_outcomes", []), f"{label}.residual_outcomes"
    )
    audits = sizing_audits_by_id or {}
    if state == "residual_bound":
        anchor_audit = audits.get(residual_card)
        if anchor_audit is None:
            raise LateOversizeError(
                f"{label}: residual_bound return requires the residual Card "
                f"{residual_card!r} sizing audit on the board; coverage "
                "evidence must persist while the return is bound"
            )
        _validate_residual_coverage(
            residual_outcomes, anchor_audit, label, residual_card
        )
        jit_resolutions = _validate_jit_resolutions(
            record.get("jit_resolutions", []),
            f"{label}.jit_resolutions",
            card_id=card_id,
            anchor_id=residual_card,
            anchor_audit=anchor_audit,
            cards_by_id=cards_by_id,
            triggers_by_id=triggers_by_id,
        )
    else:
        jit_resolutions = []
    residual_trigger = record.get("residual_trigger")
    if not isinstance(residual_trigger, str) or not residual_trigger.strip():
        raise LateOversizeError(
            f"{label}: residual_trigger must name the waiting downstream JIT "
            "trigger holding the residual scope"
        )
    trigger = triggers_by_id.get(residual_trigger)
    if trigger is None:
        raise LateOversizeError(
            f"{label}: residual_trigger names unknown JIT trigger "
            f"{residual_trigger!r}"
        )
    if status != "returned" and trigger.get("state") != "waiting":
        raise LateOversizeError(
            f"{label}: residual_trigger {residual_trigger!r} is "
            f"{trigger.get('state')}; residual scope parks only on a waiting "
            "trigger until the handoff goes terminal — satisfied/consumed "
            "triggers require a DONE predecessor or a bound return handoff"
        )
    if trigger.get("after_card") != card_id:
        raise LateOversizeError(
            f"{label}: residual_trigger {residual_trigger!r} is bounded after "
            f"Card {trigger.get('after_card')!r}, not the returning Card "
            f"{card_id!r}; residual scope parks only on a trigger bounded "
            "after the returning Card itself"
        )
    bounded = _require_bool(
        record.get("bounded_correction_applies"),
        f"{label}: bounded_correction_applies",
    )
    if bounded is not False:
        raise LateOversizeError(
            f"{label}: bounded correction inside the current Card applies, so "
            "this is an ordinary implementation defect, not late-oversize "
            "evidence; keep the Card in_progress and correct it"
        )
    not_bug_basis = _require_statement(
        record.get("not_bug_basis"), f"{label}: not_bug_basis"
    )
    merges_required = _require_bool(
        record.get("merges_required_seam"), f"{label}: merges_required_seam"
    )
    if merges_required is not False:
        raise LateOversizeError(
            f"{label}: a late-oversize return must not merge a required_seam; "
            "evidence that a required seam is wrong returns to Strategic "
            "Planning for accepted revision"
        )
    seam_basis = _require_statement(record.get("seam_basis"), f"{label}: seam_basis")
    preserves = _require_bool(
        record.get("preserves_history"), f"{label}: preserves_history"
    )
    if preserves is not True:
        raise LateOversizeError(
            f"{label}: preserves_history must be true; the return preserves "
            "the durable result locator and review history"
        )
    claims_green = _require_bool(record.get("claims_green"), f"{label}: claims_green")
    if claims_green is not False:
        raise LateOversizeError(
            f"{label}: a late-oversize return must not claim GREEN; it is not "
            "a new product-scope authorization and never finalizes the Card"
        )
    return {
        "card_id": card_id,
        "origin": str(origin),
        "origin_attempt": origin_attempt,
        "origin_attempt_path": origin_attempt_path,
        "state": str(state),
        "residual_card": residual_card,
        "jit_resolutions": jit_resolutions,
        "material_evidence": material_evidence,
        "preserved_refs": preserved_refs,
        "preserved_basis": preserved_basis,
        "residual_scope": residual_scope,
        "residual_outcomes": residual_outcomes,
        "residual_trigger": residual_trigger,
        "bounded_correction_applies": False,
        "not_bug_basis": not_bug_basis,
        "merges_required_seam": False,
        "seam_basis": seam_basis,
        "preserves_history": True,
        "claims_green": False,
    }


def validate_late_returns(
    returns: Iterable[Mapping[str, Any]] | None,
    cards: Iterable[Mapping[str, Any]],
    triggers: Iterable[Mapping[str, Any]] | None,
    workstream_id: str,
    sizing_audits: Iterable[Mapping[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    """Validate durable Task Board late-oversize returns.

    The array is optional: Boards without late evidence omit it entirely, so
    legacy and historical terminal Boards stay valid. Each record must bind a
    distinct materialized Card exactly once. Bound records additionally prove
    residual-outcome coverage against the anchor sizing audits. Returns the
    Card id to validated record mapping.
    """
    if returns is None:
        return {}
    if not isinstance(returns, list):
        raise LateOversizeError(
            "task_board late_oversize_returns must be an array of return records"
        )
    cards_by_id = {card["id"]: card for card in cards}
    triggers_by_id = {trigger["id"]: trigger for trigger in (triggers or [])}
    audits_by_id = {
        audit["card_id"]: audit
        for audit in (sizing_audits or [])
        if isinstance(audit, Mapping) and isinstance(audit.get("card_id"), str)
    }
    records: dict[str, dict[str, Any]] = {}
    for index, record in enumerate(returns):
        label = f"task_board.late_oversize_returns[{index}]"
        if not isinstance(record, Mapping):
            raise LateOversizeError(f"{label}: late-oversize return must be a table")
        card_id = record.get("card_id")
        if not isinstance(card_id, str) or not card_id.strip():
            raise LateOversizeError(f"{label}: card_id must be a non-empty string")
        if card_id in records:
            raise LateOversizeError(
                f"{label}: duplicate late-oversize return for Card {card_id!r}"
            )
        records[card_id] = validate_late_return(
            record, label, cards_by_id=cards_by_id,
            triggers_by_id=triggers_by_id, workstream_id=workstream_id,
            sizing_audits_by_id=audits_by_id,
        )
    return records


def classify_worker_topology_action(
    *,
    broadens_scope: bool,
    merges_cards: bool,
    splits_card: bool,
    rewrites_card: bool,
    main_authorized_return: bool,
) -> str:
    """Classify a Worker topology action to its exact durable owner.

    Returns ``"execution_prep"`` when Main has authorized a durable
    late-oversize return and the Worker only supplies topology evidence for
    Main/Execution Prep re-decomposition, else ``"execution"`` for ordinary
    implementation with no topology effect. A Worker that broadens scope,
    merges Cards, self-splits or rewrites the stable Card without a
    Main-authorized return is rejected: Main retains topology/authority
    decisions and the Worker never materializes Cards, triggers or contract
    rewrites.
    """
    for name, value in (
        ("broadens_scope", broadens_scope),
        ("merges_cards", merges_cards),
        ("splits_card", splits_card),
        ("rewrites_card", rewrites_card),
        ("main_authorized_return", main_authorized_return),
    ):
        if not isinstance(value, bool):
            raise LateOversizeError(f"{name} must be a boolean")
    topology = broadens_scope or merges_cards or splits_card or rewrites_card
    if topology and not main_authorized_return:
        actions = ", ".join(
            name for name, active in (
                ("broaden scope", broadens_scope),
                ("merge Cards", merges_cards),
                ("self-split", splits_card),
                ("rewrite the stable Card", rewrites_card),
            )
            if active
        )
        raise LateOversizeError(
            f"Worker must not silently {actions}; Main owns Card "
            "topology/authority — record execution/review evidence and let "
            "Main reconcile a durable late-oversize return to Execution Prep"
        )
    if topology:
        return "execution_prep"
    return "execution"


def classify_execution_return(
    *,
    acceptance_valid: bool,
    real_blocker: bool,
    late_oversize_evidence: bool,
) -> str:
    """Classify a returned implementation with late-oversize awareness.

    A real unresolved blocker still routes to ``"block"``. Material
    late-oversize evidence otherwise routes to ``"return_to_execution_prep"``
    for Main-owned bounded re-decomposition — never to ``"reconcile"``, so a
    partially valid Card cannot launder failed acceptance into GREEN.
    Without late evidence the classification matches the ordinary
    execution contract (``"correct"`` / ``"reconcile"``).
    """
    for name, value in (
        ("acceptance_valid", acceptance_valid),
        ("real_blocker", real_blocker),
        ("late_oversize_evidence", late_oversize_evidence),
    ):
        if not isinstance(value, bool):
            raise LateOversizeError(f"{name} must be a boolean")
    if real_blocker:
        return "block"
    if late_oversize_evidence:
        return "return_to_execution_prep"
    if not acceptance_valid:
        return "correct"
    return "reconcile"


def _held_card(board: Mapping[str, Any], state: str) -> str | None:
    """Return the in-progress Card whose return is in the given lifecycle state.

    Boards carry at most one in-progress Card, and each returning Card holds at
    most one return record, so the held Card is unambiguous. Returns None when
    no in-progress Card has a durable return in that state.
    """
    cards = board.get("cards", [])
    returns = board.get("late_oversize_returns", [])
    if not isinstance(cards, list) or not isinstance(returns, list):
        return None
    in_progress = {
        card["id"]
        for card in cards
        if isinstance(card, Mapping) and card.get("status") == "in_progress"
    }
    for record in returns:
        if (
            isinstance(record, Mapping)
            and record.get("card_id") in in_progress
            and record.get("state") == state
        ):
            return str(record["card_id"])
    return None


def pending_late_return(board: Mapping[str, Any]) -> str | None:
    """Return the in-progress Card with a ``pending`` late-oversize return.

    The residual scope is not yet materialized: Execution Prep must
    materialize the residual Card and bind the return before the original can
    go terminal. Returns None when no in-progress Card holds a pending return.
    """
    return _held_card(board, "pending")


def bound_handoff_hold(board: Mapping[str, Any]) -> str | None:
    """Return the in-progress Card with a ``residual_bound`` return.

    The residual Card is materialized but the original has not yet reached its
    non-GREEN terminal disposition: Execution Prep owns handoff finalization
    (transition the original to returned). A bound return on a returned
    original releases the hold so the residual can proceed. Returns None when
    no in-progress Card holds a bound return.
    """
    return _held_card(board, "residual_bound")


def _outcome_by_id(
    items: Any, outcome_id: str
) -> Mapping[str, Any] | None:
    if not isinstance(items, list):
        return None
    for item in items:
        if isinstance(item, Mapping) and item.get("id") == outcome_id:
            return item
    return None


def _outcome_content_mismatch(
    first: Mapping[str, Any], second: Mapping[str, Any]
) -> str | None:
    for field in ("kind", "statement", "family"):
        if first.get(field) != second.get(field):
            return field
    return None


def _resolve_card_owner(
    outcome_id: str,
    owner_id: str,
    record: Mapping[str, Any],
    cards: Mapping[str, Mapping[str, Any]],
    returns: Mapping[str, Mapping[str, Any]],
    resolve_chained: Any,
) -> str | None:
    """Resolve one Card owner's completion for a residual outcome.

    ``done`` owners are accepted completion. ``returned`` owners recurse
    through their own chained return, which must carry the outcome forward.
    Any other status is concrete unfinished work.
    """
    owner = cards.get(owner_id)
    if owner is None:
        return (
            f"Residual outcome {outcome_id!r} from Card {record.get('card_id')} "
            f"is allocated to unknown Card {owner_id!r}; Execution Prep must "
            "repair the downstream allocation before Close"
        )
    status = owner.get("status")
    if status == "done":
        return None
    if status == "returned":
        chained = returns.get(owner_id)
        if chained is None or chained.get("state") != "residual_bound":
            return (
                f"Residual outcome {outcome_id!r} from Card "
                f"{record.get('card_id')} is handed to returned Card "
                f"{owner_id!r} without a bound return; Execution Prep must "
                "bind the chained handoff before Close"
            )
        carried = _outcome_by_id(
            chained.get("residual_outcomes", []), outcome_id
        )
        if carried is None:
            return (
                f"Residual outcome {outcome_id!r} from Card "
                f"{record.get('card_id')} is not carried by the chained "
                f"return on Card {owner_id!r}; Execution Prep must re-bind "
                "the dropped scope before Close"
            )
        return resolve_chained(carried, chained)
    return (
        f"Residual outcome {outcome_id!r} from Card {record.get('card_id')} "
        f"awaits {status} Card {owner_id!r}; Execution Prep owns the "
        "unfinished downstream Card before Close"
    )


def unfinished_residual_scope(board: Mapping[str, Any]) -> str | None:
    """Return a concrete obligation for incomplete residual scope, if any.

    Walks every bound return's residual outcomes through the anchor sizing
    audit allocations: single-audit outcomes must land in the done anchor,
    ``card:`` allocations in their done owner, and ``jit:`` allocations in a
    consumed trigger with a recorded resolution to a done Card. Chained
    handoffs (an owner that is itself ``returned``) recurse with a cycle
    guard; a cycle means scope never lands and fails closed. Returns None
    only when every residual outcome terminates in accepted (done)
    downstream Cards. ``done`` here means accepted completion as attested by
    Main's durable result/review lifecycle; review acceptance itself stays
    human-owned.
    """
    cards_list = board.get("cards", [])
    returns_list = board.get("late_oversize_returns", [])
    audits_list = board.get("sizing_audits", [])
    triggers_list = board.get("jit_triggers", [])
    cards = {
        card["id"]: card
        for card in cards_list
        if isinstance(card, Mapping) and isinstance(card.get("id"), str)
    }
    returns = {
        item["card_id"]: item
        for item in returns_list
        if isinstance(item, Mapping) and isinstance(item.get("card_id"), str)
    }
    audits = {
        audit["card_id"]: audit
        for audit in audits_list
        if isinstance(audit, Mapping) and isinstance(audit.get("card_id"), str)
    }
    triggers = {
        trigger["id"]: trigger
        for trigger in triggers_list
        if isinstance(trigger, Mapping) and isinstance(trigger.get("id"), str)
    }

    def resolve(
        identity: Mapping[str, Any],
        record: Mapping[str, Any],
        visited: frozenset[tuple[str, str]],
    ) -> str | None:
        outcome_id = identity.get("id", "")
        key = (str(record.get("card_id")), str(outcome_id))
        if key in visited:
            return (
                f"Residual outcome {outcome_id!r} cycles through chained "
                "handoffs without landing in accepted scope; Execution Prep "
                "must break the cycle with a completing downstream Card "
                "before Close"
            )
        visited = visited | {key}
        anchor_id = record.get("residual_card", "")
        audit = audits.get(anchor_id)
        if audit is None:
            return (
                f"Residual outcome {outcome_id!r} from Card "
                f"{record.get('card_id')} loses its sizing audit on residual "
                f"Card {anchor_id!r}; Execution Prep must restore coverage "
                "evidence before Close"
            )
        covering = _outcome_by_id(audit.get("outcomes", []), str(outcome_id))
        if covering is None:
            return (
                f"Residual outcome {outcome_id!r} from Card "
                f"{record.get('card_id')} has no covering outcome in "
                f"residual Card {anchor_id!r}; Execution Prep must re-bind "
                "the dropped scope before Close"
            )
        mismatch = _outcome_content_mismatch(identity, covering)
        if mismatch is not None:
            return (
                f"Residual outcome {outcome_id!r} from Card "
                f"{record.get('card_id')} changed downstream ({mismatch} "
                f"differs in residual Card {anchor_id!r}); Execution Prep "
                "must reconcile the relabelled scope before Close"
            )
        if audit.get("decision") == "split":
            try:
                kind, ref = parse_allocation(
                    covering.get("allocated_to"),
                    f"residual outcome {outcome_id!r}",
                )
            except CardSizingError as exc:
                return (
                    f"Residual outcome {outcome_id!r} from Card "
                    f"{record.get('card_id')} has an unreadable allocation: "
                    f"{exc}; Execution Prep must repair it before Close"
                )
        else:
            kind, ref = "card", anchor_id
        if kind == "card":
            return _resolve_card_owner(
                str(outcome_id), ref, record, cards, returns,
                lambda carried, chained: resolve(carried, chained, visited),
            )
        trigger = triggers.get(ref)
        if trigger is None:
            return (
                f"Residual outcome {outcome_id!r} from Card "
                f"{record.get('card_id')} is parked on unknown JIT trigger "
                f"{ref!r}; Execution Prep must repair the allocation before "
                "Close"
            )
        trigger_state = trigger.get("state")
        if trigger_state in ("waiting", "satisfied"):
            return (
                f"Residual outcome {outcome_id!r} from Card "
                f"{record.get('card_id')} is parked on JIT trigger {ref!r} "
                f"({trigger_state}); Execution Prep must materialize its "
                "downstream Card before Close"
            )
        if trigger_state != "consumed":
            return (
                f"Residual outcome {outcome_id!r} from Card "
                f"{record.get('card_id')} is parked on JIT trigger {ref!r} "
                f"in unknown state {trigger_state!r}; Execution Prep must "
                "repair the trigger before Close"
            )
        resolutions = record.get("jit_resolutions", [])
        target = None
        if isinstance(resolutions, list):
            for entry in resolutions:
                if isinstance(entry, Mapping) and entry.get("trigger") == ref:
                    target = entry.get("card")
        if not isinstance(target, str) or not target:
            return (
                f"Residual outcome {outcome_id!r} from Card "
                f"{record.get('card_id')} sits on consumed JIT trigger "
                f"{ref!r} with no recorded materialized Card; Execution "
                "Prep must bind the trigger to its Card before Close"
            )
        return _resolve_card_owner(
            str(outcome_id), target, record, cards, returns,
            lambda carried, chained: resolve(carried, chained, visited),
        )

    for card_id in sorted(returns):
        record = returns[card_id]
        if record.get("state") == "pending":
            return (
                f"Card {card_id} holds a pending late-oversize return; "
                "Execution Prep must materialize and bind the residual Card "
                "before Close"
            )
        if record.get("state") != "residual_bound":
            continue
        residuals = record.get("residual_outcomes", [])
        if not isinstance(residuals, list):
            continue
        for residual in residuals:
            if not isinstance(residual, Mapping):
                continue
            gap = resolve(residual, record, frozenset())
            if gap is not None:
                return gap
    return None
