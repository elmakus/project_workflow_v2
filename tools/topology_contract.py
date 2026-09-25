#!/usr/bin/env python3
"""Runtime-neutral risk-scoped topology challenge and review layering (BOOT-B, REQ-119..121).

Materially risky proposed Card topology must receive a fresh independent
decomposition/topology challenge before first launch: merger of
planner-declared preferred seams, a Card spanning multiple independently
falsifiable invariant families, whole-milestone absorption despite explicit
seams, Card Review substituting for Milestone integration review, or other
material deviation from accepted decomposition intent.

The challenge stays narrower than Plan Review: it evaluates exactly the
concrete Card-boundary dimensions (boundary fidelity, falsifiability, review
separation) and never re-litigates milestone strategy, ordering, requirement
coverage or premium gates. Simple/non-risky topology carries a durable
non-risky record but no mandatory fresh-challenge ceremony.

Card Review owns bounded local correctness while Milestone Review owns broader
composition/integration acceptance. A Card boundary so broad that Card Review
would substitute for Milestone review is rejected unless concrete atomicity
evidence justifies the single boundary.

The challenge is a second-order safeguard over the T05 sizing decision
(``tools/card_sizing_contract.py``) and the T04 seam fidelity
(``tools/seam_contract.py``): a GREEN challenge never cures an invalid primary
sizing audit or an unowned seam merge.

Every recorded challenge binds its exact subject. The ``proposal_digest``
covers the Board-local proposal (the Card's sizing audit, the topology
risk/scope/trigger fields excluding the challenge itself, and the accepted
seam decisions and Planning seam declarations); Board validation recomputes
it, so a material proposal change stales the challenge while ordinary
revision/status transitions do not. The ``card_contract_digest`` covers the
stable Card contract file bytes and is verified by the router at launch
refresh, which is the only stage that reads Card content. Missing,
mismatched or unsupported bindings fail closed. The digest proves subject
identity only; the independent challenger still judges semantic truth.

Out of scope here: late oversized-Card return to Execution Prep (REQ-130),
BOOT-C/BOOT-D, and changes to accepted Definition/P6 strategy.
"""

from __future__ import annotations

import hashlib
import re
from collections.abc import Iterable, Mapping
from typing import Any


def _canonical_json(value: Any) -> bytes:
    """Encode deterministic canonical JSON via the shared obligation helper.

    Imported lazily: ``tools.obligation_contract`` transitively imports this
    module through the state contract, so a top-level import would cycle.
    """
    try:
        from tools.obligation_contract import canonical_json
    except ModuleNotFoundError:  # direct script execution from tools/
        from obligation_contract import canonical_json
    return canonical_json(value)


RISK_CLASSES = frozenset({"simple", "risky"})

RISK_TRIGGERS = frozenset({
    "preferred_seam_merge",
    "multiple_invariant_families",
    "whole_milestone_absorption",
    "milestone_review_substitution",
    "material_deviation",
})

CHALLENGE_DIMENSIONS = (
    "boundary_fidelity",
    "falsifiability",
    "review_separation",
)

PLAN_REVIEW_ONLY_SCOPES = frozenset({
    "milestone_strategy",
    "milestone_ordering",
    "requirement_coverage",
    "premium_gates",
    "plan_approval",
    "definition_scope",
})

REVIEW_SCOPES = frozenset({"card_local", "milestone_integration"})

CHALLENGE_VERDICTS = frozenset({"green", "red"})

TOPOLOGY_AUDITED_STATUSES = frozenset({"planned", "ready", "in_progress"})

DIGEST_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


class TopologyError(ValueError):
    """Raised when a topology risk record or challenge is invalid."""


def _require_bool(value: Any, label: str) -> bool:
    if not isinstance(value, bool):
        raise TopologyError(f"{label} must be a boolean")
    return value


def _require_digest(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TopologyError(
            f"{label} requires a durable subject binding to the exact challenged content"
        )
    if DIGEST_RE.fullmatch(value) is None:
        raise TopologyError(
            f"{label}: unsupported topology subject binding {value!r}; "
            "expected sha256:<64 hex>"
        )
    return value


def topology_proposal_material(
    *,
    card_id: str,
    sizing_audit: Mapping[str, Any],
    topology_audit: Mapping[str, Any],
    seam_decisions: Iterable[Mapping[str, Any]] | None = None,
    planning_seams: Iterable[Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Project the exact Board-local proposal a challenge was evaluated against.

    The material covers the Card's sizing audit, the topology risk/scope/
    trigger fields (excluding the challenge/verdict itself, which carries
    the binding), and the accepted seam decisions plus Planning seam
    declarations. Board revision and Card lifecycle status are excluded, so
    ordinary status transitions do not stale a bound challenge.
    """
    decisions = sorted(
        (dict(decision) for decision in (seam_decisions or []) if isinstance(decision, Mapping)),
        key=lambda decision: str(decision.get("seam_id", "")),
    )
    seams = sorted(
        (
            {"id": seam.get("id"), "class": seam.get("class"), "intent": seam.get("intent")}
            for seam in (planning_seams or [])
            if isinstance(seam, Mapping)
        ),
        key=lambda seam: str(seam.get("id", "")),
    )
    triggers = topology_audit.get("triggers", [])
    return {
        "card_id": card_id,
        "sizing_audit": dict(sizing_audit),
        "topology": {
            "card_id": topology_audit.get("card_id"),
            "risk": topology_audit.get("risk"),
            "triggers": sorted(triggers) if isinstance(triggers, list) else triggers,
            "risk_basis": topology_audit.get("risk_basis"),
            "review_scope": topology_audit.get("review_scope"),
            "atomicity_rationale_class": topology_audit.get("atomicity_rationale_class", ""),
            "atomicity_rationale": topology_audit.get("atomicity_rationale", ""),
        },
        "seam_decisions": decisions,
        "planning_seams": seams,
    }


def compute_proposal_digest(
    *,
    card_id: str,
    sizing_audit: Mapping[str, Any],
    topology_audit: Mapping[str, Any],
    seam_decisions: Iterable[Mapping[str, Any]] | None = None,
    planning_seams: Iterable[Mapping[str, Any]] | None = None,
) -> str:
    """Return the deterministic ``sha256:`` digest of the challenged proposal."""
    material = topology_proposal_material(
        card_id=card_id,
        sizing_audit=sizing_audit,
        topology_audit=topology_audit,
        seam_decisions=seam_decisions,
        planning_seams=planning_seams,
    )
    try:
        payload = _canonical_json(material)
    except ValueError as exc:
        raise TopologyError(f"topology proposal material is not serializable: {exc}") from exc
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def compute_card_contract_digest(content: bytes) -> str:
    """Return the deterministic ``sha256:`` digest of Card contract file bytes."""
    if not isinstance(content, (bytes, bytearray)):
        raise TopologyError("card contract content must be bytes")
    return "sha256:" + hashlib.sha256(bytes(content)).hexdigest()


def validate_challenge(challenge: Mapping[str, Any], label: str) -> dict[str, Any]:
    """Validate one fresh independent topology challenge record.

    The challenge evaluates exactly the narrow concrete dimensions
    (boundary fidelity, falsifiability, review separation): omitting one
    leaves the boundary unchecked, while claiming Plan Review scope
    (milestone strategy/ordering/coverage/gates) exceeds the narrow mandate.
    Self-certified or reused/stale challenges are rejected: the challenger
    must be independent of the Execution Prep proposal and the challenge
    must be fresh for the current proposed topology.
    """
    if not isinstance(challenge, Mapping):
        raise TopologyError(f"{label}: challenge must be a table")
    verdict = challenge.get("verdict")
    if verdict not in CHALLENGE_VERDICTS:
        raise TopologyError(
            f"{label}: unknown challenge verdict {verdict!r}; expected one of green, red"
        )
    evaluated = challenge.get("evaluated")
    if not isinstance(evaluated, list):
        raise TopologyError(f"{label}: evaluated must be an array of concrete dimensions")
    seen: set[str] = set()
    for dimension in evaluated:
        if dimension in seen:
            raise TopologyError(f"{label}: duplicate challenge dimension {dimension!r}")
        seen.add(dimension)  # type: ignore[arg-type]
        if dimension in PLAN_REVIEW_ONLY_SCOPES:
            raise TopologyError(
                f"{label}: challenge dimension {dimension!r} belongs to Plan Review; "
                "the topology challenge must stay narrower than Plan Review"
            )
        if dimension not in CHALLENGE_DIMENSIONS:
            raise TopologyError(
                f"{label}: unknown challenge dimension {dimension!r}; expected only "
                + ", ".join(CHALLENGE_DIMENSIONS)
            )
    missing = [name for name in CHALLENGE_DIMENSIONS if name not in seen]
    if missing:
        raise TopologyError(
            f"{label}: challenge must evaluate boundary_fidelity, falsifiability "
            f"and review_separation; missing: {', '.join(missing)}"
        )
    scope_statement = challenge.get("scope_statement")
    if not isinstance(scope_statement, str) or not scope_statement.strip():
        raise TopologyError(
            f"{label}: scope_statement requires a durable non-empty statement "
            "of the concrete Card boundary evaluated"
        )
    independent = _require_bool(challenge.get("independent"), f"{label}: independent")
    if independent is not True:
        raise TopologyError(
            f"{label}: challenge must be independent; self-certification is rejected"
        )
    independence_basis = challenge.get("independence_basis")
    if not isinstance(independence_basis, str) or not independence_basis.strip():
        raise TopologyError(
            f"{label}: independence_basis requires a durable non-empty statement"
        )
    fresh = _require_bool(challenge.get("fresh"), f"{label}: fresh")
    if fresh is not True:
        raise TopologyError(
            f"{label}: challenge must be fresh; a reused or stale challenge is rejected"
        )
    challenge_basis = challenge.get("challenge_basis")
    if not isinstance(challenge_basis, str) or not challenge_basis.strip():
        raise TopologyError(
            f"{label}: challenge_basis requires a durable non-empty statement"
        )
    proposal_digest = _require_digest(
        challenge.get("proposal_digest"), f"{label}: proposal_digest"
    )
    card_contract_digest = _require_digest(
        challenge.get("card_contract_digest"), f"{label}: card_contract_digest"
    )
    return {
        "verdict": str(verdict),
        "evaluated": list(evaluated),
        "scope_statement": scope_statement,
        "independent": True,
        "independence_basis": independence_basis,
        "fresh": True,
        "challenge_basis": challenge_basis,
        "proposal_digest": proposal_digest,
        "card_contract_digest": card_contract_digest,
    }


def validate_topology_audit(
    audit: Mapping[str, Any], label: str, status: str
) -> dict[str, Any]:
    """Validate one durable per-Card topology risk record for its launch status.

    ``simple`` topology records a durable non-risky basis with no triggers
    and no challenge ceremony. ``risky`` topology names at least one durable
    risk trigger and carries a fresh independent challenge: ``ready`` Cards
    must record the challenge (RED blocks launch via the router), while
    ``in_progress`` Cards must already hold a GREEN one. ``planned`` (and
    exempt-history) risk may defer the challenge until first launch.
    """
    if not isinstance(audit, Mapping):
        raise TopologyError(f"{label}: topology audit must be a table")
    card_id = audit.get("card_id")
    if not isinstance(card_id, str) or not card_id.strip():
        raise TopologyError(f"{label}: card_id must be a non-empty string")
    risk = audit.get("risk")
    if risk not in RISK_CLASSES:
        raise TopologyError(
            f"{label}: unknown risk class {risk!r}; expected one of risky, simple"
        )
    triggers = audit.get("triggers")
    if not isinstance(triggers, list):
        raise TopologyError(f"{label}: triggers must be an array of risk triggers")
    seen: set[str] = set()
    for trigger in triggers:
        if trigger in seen:
            raise TopologyError(f"{label}: duplicate risk trigger {trigger!r}")
        seen.add(trigger)  # type: ignore[arg-type]
        if trigger not in RISK_TRIGGERS:
            raise TopologyError(
                f"{label}: unknown risk trigger {trigger!r}; expected one of "
                + ", ".join(sorted(RISK_TRIGGERS))
            )
    risk_basis = audit.get("risk_basis")
    if not isinstance(risk_basis, str) or not risk_basis.strip():
        raise TopologyError(
            f"{label}: risk_basis requires a durable non-empty statement"
        )
    review_scope = audit.get("review_scope")
    if review_scope not in REVIEW_SCOPES:
        raise TopologyError(
            f"{label}: unknown review scope {review_scope!r}; expected one of "
            "card_local, milestone_integration"
        )
    rationale_class = audit.get("atomicity_rationale_class", "")
    rationale = audit.get("atomicity_rationale", "")
    if not isinstance(rationale_class, str) or not isinstance(rationale, str):
        raise TopologyError(
            f"{label}: atomicity_rationale_class and atomicity_rationale must be strings"
        )
    if risk == "simple" and review_scope != "card_local":
        raise TopologyError(
            f"{label}: simple topology cannot substitute Card Review for "
            "Milestone integration review"
        )
    if review_scope == "milestone_integration":
        if "milestone_review_substitution" not in seen:
            raise TopologyError(
                f"{label}: milestone_integration review scope requires the "
                "milestone_review_substitution trigger"
            )
        if rationale_class != "atomicity" or not rationale.strip():
            raise TopologyError(
                f"{label}: milestone_integration review scope requires concrete "
                "atomicity rationale; only concrete atomicity evidence justifies a "
                "Card boundary that substitutes for Milestone integration review"
            )
    else:
        if "milestone_review_substitution" in seen:
            raise TopologyError(
                f"{label}: milestone_review_substitution trigger requires "
                "milestone_integration review scope"
            )
        if rationale_class.strip() or rationale.strip():
            raise TopologyError(
                f"{label}: card_local review scope must not claim atomicity rationale"
            )
    challenge: dict[str, Any] | None = None
    if risk == "simple":
        if triggers:
            raise TopologyError(
                f"{label}: simple topology must not list risk triggers"
            )
        if "challenge" in audit:
            raise TopologyError(
                f"{label}: simple topology must not claim a fresh topology challenge"
            )
    else:
        if not triggers:
            raise TopologyError(
                f"{label}: risky topology requires at least one durable risk trigger"
            )
        if "challenge" in audit:
            challenge = validate_challenge(audit["challenge"], f"{label}.challenge")
        elif status == "ready":
            raise TopologyError(
                f"{label}: risky topology requires a recorded fresh independent "
                "challenge before first launch"
            )
        elif status == "in_progress":
            raise TopologyError(
                f"{label}: in_progress Card must not run without a GREEN fresh "
                "independent topology challenge"
            )
        if challenge is not None and status == "in_progress" and challenge["verdict"] != "green":
            raise TopologyError(
                f"{label}: in_progress Card must not run without a GREEN fresh "
                "independent topology challenge"
            )
    record: dict[str, Any] = {
        "card_id": card_id,
        "risk": str(risk),
        "triggers": list(triggers),
        "risk_basis": risk_basis,
        "review_scope": str(review_scope),
        "atomicity_rationale_class": rationale_class,
        "atomicity_rationale": rationale,
    }
    if challenge is not None:
        record["challenge"] = challenge
    return record


def effective_separable_families(
    sizing_audit: Mapping[str, Any], card_id: str
) -> frozenset[str]:
    """Return distinct invariant families in the Card's effective boundary.

    A ``single`` sizing decision keeps every candidate outcome in the Card,
    while a ``split`` decision keeps only outcomes allocated back to the
    audited Card itself. Only separable outcomes (independently verifiable
    and independently useful) can force a multi-family topology challenge.
    """
    outcomes = sizing_audit.get("outcomes", [])
    if not isinstance(outcomes, list):
        return frozenset()
    if sizing_audit.get("decision") == "split":
        retained = f"card:{card_id}"
        outcomes = [o for o in outcomes if isinstance(o, Mapping) and o.get("allocated_to") == retained]
    families = {
        str(outcome["family"])
        for outcome in outcomes
        if isinstance(outcome, Mapping)
        and outcome.get("independently_verifiable") is True
        and outcome.get("independently_useful") is True
        and isinstance(outcome.get("family"), str)
        and outcome["family"].strip()
    }
    return frozenset(families)


def _preferred_merge_exists(
    seam_decisions: Iterable[Mapping[str, Any]] | None,
    planning_seams: Iterable[Mapping[str, Any]] | None,
) -> bool:
    if not seam_decisions:
        return False
    classes = {
        seam["id"]: seam.get("class")
        for seam in (planning_seams or [])
        if isinstance(seam, Mapping) and isinstance(seam.get("id"), str)
    }
    return any(
        isinstance(decision, Mapping)
        and classes.get(decision.get("seam_id")) == "preferred_seam"
        and decision.get("decision") == "merged"
        for decision in seam_decisions
    )


def validate_topology_audits(
    audits: Iterable[Mapping[str, Any]] | None,
    cards: Iterable[Mapping[str, Any]],
    sizing_audits: Iterable[Mapping[str, Any]] | None,
    seam_decisions: Iterable[Mapping[str, Any]] | None = None,
    planning_seams: Iterable[Mapping[str, Any]] | None = None,
) -> dict[str, str]:
    """Validate durable Task Board topology audits against materialized Cards.

    Every Card in an executable lifecycle status (``planned``/``ready``/
    ``in_progress``) must carry exactly one topology audit: omitting the
    audit array, or omitting one active Card from it, is a bypass. ``done``
    Cards are exempt so historical terminal state stays valid, as are
    ``blocked`` Cards while blocked; any return to an executable status
    re-triggers the gate.

    Risk claims compose with the T04 seam and T05 sizing gates: a Card whose
    effective sizing boundary spans two or more independently falsifiable
    invariant families must be risky with the multiple-family trigger, a
    claimed family trigger without multi-family scope is dishonest, a
    claimed preferred-seam merge requires a Board-recorded merged preferred
    seam, a Board-recorded preferred merge requires an owning risky audit
    while executable Cards exist, and whole-milestone absorption requires
    explicit declared Planning seams. Every recorded challenge must bind the
    exact current proposal digest; a stale binding fails closed. The Card
    contract digest is format-checked here and value-verified by the router
    at launch refresh. Returns the Card id to risk mapping.
    """
    if audits is None:
        audits = []
    if not isinstance(audits, list):
        raise TopologyError("task_board topology_audits must be an array of audit records")
    cards_by_id = {card["id"]: card for card in cards}
    sizing_by_id = {
        audit["card_id"]: audit
        for audit in (sizing_audits or [])
        if isinstance(audit, Mapping) and isinstance(audit.get("card_id"), str)
    }
    decisions_list = list(seam_decisions) if seam_decisions else []
    if decisions_list and planning_seams is None:
        raise TopologyError(
            "task_board topology_audits: seam decisions require accepted Planning "
            "seams to verify preferred-merge ownership"
        )
    risks: dict[str, str] = {}
    records: dict[str, dict[str, Any]] = {}
    for index, audit in enumerate(audits):
        label = f"task_board.topology_audits[{index}]"
        if not isinstance(audit, Mapping):
            raise TopologyError(f"{label}: topology audit must be a table")
        card_id = audit.get("card_id")
        if not isinstance(card_id, str) or not card_id.strip():
            raise TopologyError(f"{label}: card_id must be a non-empty string")
        if card_id in risks:
            raise TopologyError(f"{label}: duplicate topology audit for Card {card_id!r}")
        if card_id not in cards_by_id:
            raise TopologyError(
                f"{label}: unknown card_id {card_id!r}; topology audits must bind "
                "a materialized Task Board Card"
            )
        try:
            record = validate_topology_audit(
                audit, label, str(cards_by_id[card_id].get("status"))
            )
        except TopologyError as exc:
            raise TopologyError(f"{exc}") from exc
        risks[card_id] = record["risk"]
        records[card_id] = record
    missing = sorted(
        card_id
        for card_id, card in cards_by_id.items()
        if card.get("status") in TOPOLOGY_AUDITED_STATUSES and card_id not in risks
    )
    if missing:
        raise TopologyError(
            "task_board.topology_audits: missing durable topology audit for "
            + ", ".join(f"Card {card_id!r}" for card_id in missing)
        )
    for index, (card_id, record) in enumerate(records.items()):
        label = f"task_board.topology_audits[{card_id}]"
        status = cards_by_id[card_id].get("status")
        sizing = sizing_by_id.get(card_id)
        if sizing is None:
            if status in TOPOLOGY_AUDITED_STATUSES:
                raise TopologyError(
                    f"{label}: missing durable sizing audit for Card {card_id!r}; "
                    "topology risk composes with the primary sizing decision"
                )
            continue
        families = effective_separable_families(sizing, card_id)
        if len(families) >= 2 and (
            record["risk"] != "risky" or "multiple_invariant_families" not in record["triggers"]
        ):
            raise TopologyError(
                f"{label}: Card boundary spans {len(families)} independently "
                "falsifiable invariant families and requires a risky topology "
                "audit with the multiple_invariant_families trigger"
            )
        if "multiple_invariant_families" in record["triggers"] and len(families) < 2:
            raise TopologyError(
                f"{label}: claims multiple_invariant_families but its sizing "
                "boundary spans a single invariant family"
            )
        if "preferred_seam_merge" in record["triggers"] and not _preferred_merge_exists(
            decisions_list, planning_seams
        ):
            raise TopologyError(
                f"{label}: claims preferred_seam_merge but the Task Board records "
                "no merged preferred_seam"
            )
        if "whole_milestone_absorption" in record["triggers"] and not list(
            planning_seams or []
        ):
            raise TopologyError(
                f"{label}: whole_milestone_absorption requires explicit declared "
                "Planning seams"
            )
        if "challenge" in record:
            expected = compute_proposal_digest(
                card_id=card_id,
                sizing_audit=sizing,
                topology_audit=record,
                seam_decisions=decisions_list,
                planning_seams=planning_seams,
            )
            if record["challenge"]["proposal_digest"] != expected:
                raise TopologyError(
                    f"{label}: topology challenge subject does not match the exact "
                    "current proposed topology; the sizing audit, risk fields or "
                    "seam decisions changed — renew the fresh challenge before launch"
                )
    if _preferred_merge_exists(decisions_list, planning_seams) and any(
        card.get("status") in TOPOLOGY_AUDITED_STATUSES for card in cards_by_id.values()
    ):
        owned = any(
            cards_by_id[card_id].get("status") in TOPOLOGY_AUDITED_STATUSES
            and "preferred_seam_merge" in record["triggers"]
            for card_id, record in records.items()
        )
        if not owned:
            raise TopologyError(
                "task_board.topology_audits: merged preferred_seam has no owning "
                "risky topology audit with the preferred_seam_merge trigger"
            )
    return risks


def ready_topology_hold(board: Mapping[str, Any]) -> str | None:
    """Return the single READY Card held for a GREEN topology challenge, if any.

    A READY Card with materially risky topology must hold in Execution Prep
    until its fresh independent challenge is GREEN. Simple topology, GREEN
    challenges, and non-launch board shapes never hold.
    """
    cards = board.get("cards", [])
    if not isinstance(cards, list):
        return None
    ready = [card for card in cards if isinstance(card, Mapping) and card.get("status") == "ready"]
    if len(ready) != 1:
        return None
    card_id = ready[0].get("id")
    audits = board.get("topology_audits", [])
    if not isinstance(audits, list):
        return None
    for audit in audits:
        if isinstance(audit, Mapping) and audit.get("card_id") == card_id:
            if audit.get("risk") != "risky":
                return None
            challenge = audit.get("challenge")
            if not isinstance(challenge, Mapping) or challenge.get("verdict") != "green":
                return str(card_id)
            return None
    return None
