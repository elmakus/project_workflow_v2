#!/usr/bin/env python3
"""Runtime-neutral Planning seam-intent and JIT fidelity helpers (BOOT-B, REQ-115..117).

Strategic Planning classifies meaningful decomposition intent as exactly one of
``required_seam`` / ``preferred_seam`` / ``illustrative`` without speculative
future Card IDs. Execution Prep owns exact JIT Card materialization: it cannot
merge a ``required_seam`` (wrong-seam evidence returns to Strategic Planning
for accepted revision), it preserves a ``preferred_seam`` by default (merge or
split deviation needs durable qualifying technical rationale), and it may
freely ignore ``illustrative`` intent as non-binding.

Later BOOT-B outcomes (REQ-118..121 decomposition audit/topology challenge and
REQ-128..130 semantic Card sizing) are intentionally not implemented here.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any


SEAM_CLASSES = frozenset({"required_seam", "preferred_seam", "illustrative"})
SEAM_DECISIONS = frozenset({"preserved", "merged", "split"})
QUALIFYING_RATIONALE_CLASSES = frozenset({
    "coupling",
    "atomicity",
    "invalid_intermediate_state",
    "non_separable_acceptance",
    "new_predecessor_evidence",
})
REJECTED_GENERIC_RATIONALE_CLASSES = frozenset({
    "convenience",
    "same_milestone",
    "same-milestone",
    "same milestone",
    "fewer_cards",
    "fewer-cards",
    "fewer cards",
})


class SeamContractError(ValueError):
    """Raised when seam intent or JIT fidelity evidence is incomplete or contradictory."""


def validate_seam_declarations(seams: Iterable[Mapping[str, Any]]) -> list[dict[str, str]]:
    """Validate durable Planning seam declarations.

    Each seam binds a stable seam ``id``, a ``class`` from exactly
    ``required_seam`` / ``preferred_seam`` / ``illustrative``, and a non-empty
    durable ``intent``. No Card-ID binding is required or read: Planning never
    invents future Card identities.
    """
    if not isinstance(seams, list):
        raise SeamContractError("planning seams must be an array of seam records")
    records: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, seam in enumerate(seams):
        label = f"planning.seams[{index}]"
        if not isinstance(seam, Mapping):
            raise SeamContractError(f"{label}: seam must be a table")
        seam_id = seam.get("id")
        seam_class = seam.get("class")
        intent = seam.get("intent")
        if not isinstance(seam_id, str) or not seam_id.strip():
            raise SeamContractError(f"{label}: seam id must be a non-empty string")
        if seam_id in seen:
            raise SeamContractError(f"{label}: duplicate seam id {seam_id!r}")
        seen.add(seam_id)
        if seam_class not in SEAM_CLASSES:
            raise SeamContractError(
                f"{label}: unknown seam class {seam_class!r}; "
                "expected one of illustrative, preferred_seam, required_seam"
            )
        if not isinstance(intent, str) or not intent.strip():
            raise SeamContractError(
                f"{label}: seam intent must be a durable non-empty statement"
            )
        records.append({"id": seam_id, "class": str(seam_class), "intent": intent})
    return records


def seam_class_by_id(seams: Iterable[Mapping[str, Any]]) -> dict[str, str]:
    """Index validated seam declarations by seam id."""
    return {record["id"]: record["class"] for record in validate_seam_declarations(list(seams))}


def validate_preferred_deviation_rationale(
    *,
    rationale_class: object,
    rationale: object,
    label: str,
) -> str:
    """Require durable qualifying technical rationale for preferred-seam deviation.

    Only concrete coupling, atomicity, invalid-intermediate-state,
    non-separable-acceptance or new-predecessor evidence qualifies. Generic
    convenience / same-milestone / fewer-cards claims are rejected, as is a
    missing or empty durable rationale.
    """
    if rationale_class in REJECTED_GENERIC_RATIONALE_CLASSES:
        raise SeamContractError(
            f"{label}: generic {rationale_class!r} rationale is insufficient for "
            "preferred-seam deviation; expected one of atomicity, coupling, "
            "invalid_intermediate_state, new_predecessor_evidence, non_separable_acceptance"
        )
    if rationale_class not in QUALIFYING_RATIONALE_CLASSES:
        raise SeamContractError(
            f"{label}: unknown rationale class {rationale_class!r}; expected one of "
            "atomicity, coupling, invalid_intermediate_state, "
            "new_predecessor_evidence, non_separable_acceptance"
        )
    if not isinstance(rationale, str) or not rationale.strip():
        raise SeamContractError(
            f"{label}: preferred-seam deviation requires durable non-empty rationale"
        )
    return str(rationale_class)


def classify_seam_jit_decision(
    *,
    seam_id: str,
    seam_class: str,
    decision: str,
    rationale_class: str = "",
    rationale: str = "",
) -> str:
    """Classify one JIT seam decision to its exact durable owner.

    Returns ``\"execution_prep\"`` for every durable decision. Raises
    :class:`SeamContractError` when the decision violates seam fidelity:
    merging a ``required_seam`` is always rejected (the caller routes the
    evidence to Strategic Planning for accepted revision instead of
    persisting the merge), and ``preferred_seam`` merge/split deviation
    without qualifying durable rationale is rejected. Splitting within a
    ``required_seam`` boundary preserves the seam and stays in Execution
    Prep; ``illustrative`` intent is non-binding.
    """
    label = f"seam {seam_id!r}"
    if seam_class not in SEAM_CLASSES:
        raise SeamContractError(f"{label}: unknown seam class {seam_class!r}")
    if decision not in SEAM_DECISIONS:
        raise SeamContractError(
            f"{label}: unknown seam decision {decision!r}; "
            "expected one of merged, preserved, split"
        )
    if not isinstance(rationale_class, str) or not isinstance(rationale, str):
        raise SeamContractError(f"{label}: rationale_class and rationale must be strings")

    if seam_class == "required_seam" and decision == "merged":
        raise SeamContractError(
            f"{label}: Execution Prep must not merge a required_seam into another "
            "Card boundary; evidence that the seam is wrong returns to Strategic "
            "Planning for accepted revision"
        )
    if seam_class == "preferred_seam" and decision in {"merged", "split"}:
        validate_preferred_deviation_rationale(
            rationale_class=rationale_class, rationale=rationale, label=label
        )
        return "execution_prep"
    if rationale_class.strip() or rationale.strip():
        raise SeamContractError(
            f"{label}: a {seam_class} {decision} decision must not claim deviation rationale"
        )
    return "execution_prep"


def validate_seam_decisions(
    decisions: Iterable[Mapping[str, Any]],
    seams: Iterable[Mapping[str, Any]],
) -> dict[str, str]:
    """Validate durable Execution Prep JIT decisions against declared Planning seams.

    Every decision must bind a declared seam id exactly once, and every
    declared seam must carry exactly one durable decision: silently omitting
    a seam is a bypass, not preservation. Returns the seam id to
    owning-stage mapping. A rejected required-seam merge raises instead of
    returning: the caller routes that evidence to Strategic Planning for
    accepted revision rather than persisting the merge.
    """
    if not isinstance(decisions, list):
        raise SeamContractError("task_board seam_decisions must be an array of decision records")
    classes = seam_class_by_id(seams)
    seen: set[str] = set()
    owners: dict[str, str] = {}
    for index, decision in enumerate(decisions):
        label = f"task_board.seam_decisions[{index}]"
        if not isinstance(decision, Mapping):
            raise SeamContractError(f"{label}: decision must be a table")
        seam_id = decision.get("seam_id")
        action = decision.get("decision")
        if not isinstance(seam_id, str) or not seam_id.strip():
            raise SeamContractError(f"{label}: seam_id must be a non-empty string")
        if seam_id in seen:
            raise SeamContractError(f"{label}: duplicate decision for seam {seam_id!r}")
        seen.add(seam_id)
        if seam_id not in classes:
            raise SeamContractError(
                f"{label}: unknown seam_id {seam_id!r}; JIT seam decisions must bind "
                "a declared Planning seam"
            )
        if not isinstance(action, str) or action not in SEAM_DECISIONS:
            raise SeamContractError(
                f"{label}: unknown seam decision {action!r}; "
                "expected one of merged, preserved, split"
            )
        rationale_class = decision.get("rationale_class", "")
        rationale = decision.get("rationale", "")
        try:
            owners[seam_id] = classify_seam_jit_decision(
                seam_id=seam_id,
                seam_class=classes[seam_id],
                decision=action,
                rationale_class=rationale_class,  # type: ignore[arg-type]
                rationale=rationale,  # type: ignore[arg-type]
            )
        except SeamContractError as exc:
            raise SeamContractError(f"{label}: {exc}") from exc
    missing = sorted(set(classes) - seen)
    if missing:
        raise SeamContractError(
            "task_board.seam_decisions: missing durable JIT decision for declared "
            + ", ".join(f"seam {seam_id!r}" for seam_id in missing)
        )
    return owners
