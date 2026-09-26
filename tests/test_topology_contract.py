from __future__ import annotations

import copy
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.router import classify_jit_refinement, select_route
from tools.state_contract import (
    ValidationError,
    read_toml,
    validate_board,
)
from tools.topology_contract import (
    CHALLENGE_DIMENSIONS,
    RISK_TRIGGERS,
    TopologyError,
    compute_card_contract_digest,
    compute_proposal_digest,
    effective_separable_families,
    ready_topology_hold,
    validate_challenge,
    validate_topology_audit,
    validate_topology_audits,
)

ROOT = Path(__file__).resolve().parents[1]
VALID = ROOT / "tests" / "fixtures" / "state" / "valid"
ROUTER_FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"
ROUTER_MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
ROUTER_BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
ROUTER_CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"
_PLACEHOLDER_PROPOSAL_DIGEST = "sha256:" + "0" * 64
_PLACEHOLDER_CARD_DIGEST = "sha256:" + "1" * 64


def _challenge(**overrides) -> dict:
    record = {
        "verdict": "green",
        "evaluated": ["boundary_fidelity", "falsifiability", "review_separation"],
        "scope_statement": "Card holds one transport-neutral contract outcome; boundary, falsifiability and review split checked.",
        "independent": True,
        "independence_basis": "Challenger did not author the Execution Prep topology proposal.",
        "fresh": True,
        "challenge_basis": "Fresh review of the current proposed boundary against seam intent and sizing outcomes.",
        "proposal_digest": "sha256:" + "0" * 64,
        "card_contract_digest": "sha256:" + "1" * 64,
    }
    record.update(overrides)
    return record


def _simple_audit(card_id: str = "M01-T02", **overrides) -> dict:
    record = {
        "card_id": card_id,
        "risk": "simple",
        "triggers": [],
        "risk_basis": "Single coherent outcome in one invariant family; no seam merge, absorption or deviation.",
        "review_scope": "card_local",
        "atomicity_rationale_class": "",
        "atomicity_rationale": "",
    }
    record.update(overrides)
    return record


def _risky_audit(card_id: str = "M01-T02", **overrides) -> dict:
    record = {
        "card_id": card_id,
        "risk": "risky",
        "triggers": ["material_deviation"],
        "risk_basis": "Proposed boundary deviates materially from accepted decomposition intent.",
        "review_scope": "card_local",
        "atomicity_rationale_class": "",
        "atomicity_rationale": "",
        "challenge": _challenge(),
    }
    record.update(overrides)
    return record


def _outcome(outcome_id: str = "outcome-contracts", **overrides) -> dict:
    record = {
        "id": outcome_id,
        "kind": "contract",
        "statement": "Versioned transport-neutral Obligation/Result contracts with golden fixtures.",
        "family": "execution-contracts",
        "independently_verifiable": True,
        "independently_useful": True,
        "falsifiable": True,
        "substantial": True,
        "scaffolding_only": False,
        "independently_consumed": False,
    }
    record.update(overrides)
    return record


def _dimensions(**overrides) -> dict:
    record = {
        "independent_implementability": "Each outcome builds and passes alone against its own fixtures.",
        "falsifiability_testability": "Each outcome owns an observable failing check before GREEN.",
        "reviewability": "Each outcome fits one bounded Card review without integration scope.",
        "invariant_contract_family": "Outcomes span distinct contract families with named invariants.",
        "dependency_ordering": "No outcome depends on another's result; any order launches safely.",
        "atomic_mutation_migration": "No atomic mutation or migration forces joint landing.",
        "cross_surface_coupling": "No shared mutable surface couples the outcomes materially.",
    }
    record.update(overrides)
    return record


def _sizing_audit(card_id: str = "M01-T02", **overrides) -> dict:
    record = {
        "card_id": card_id,
        "decision": "single",
        "rebuttal_class": "",
        "rebuttal": "",
        "outcomes": [_outcome()],
        "dimensions": _dimensions(),
    }
    record.update(overrides)
    return record


def _m02_mega_outcomes() -> list[dict]:
    return [
        _outcome("m02-obligation-result-contracts", kind="contract",
                 statement="Versioned transport-neutral Obligation/Result contracts with schema goldens.",
                 family="execution-contracts"),
        _outcome("m02-authority-resolution", kind="invariant",
                 statement="PW-owned exact authority resolution with bounded required-source bundles.",
                 family="authority-resolution"),
        _outcome("m02-identity-freshness", kind="invariant",
                 statement="Deterministic obligation identity, minimal fingerprints, stale-result reconciliation.",
                 family="result-identity"),
        _outcome("m02-governed-mutation", kind="acceptance",
                 statement="Mutation pre/postconditions with coordinator-owned writes and mandatory readback.",
                 family="governed-mutation"),
    ]


def _cards(*entries: tuple[str, str]) -> list[dict]:
    return [{"id": card_id, "status": status} for card_id, status in entries]


def _bind_proposal(board: dict, card_id: str, planning_seams=None) -> str:
    """Bind the Card's recorded challenge to the exact current Board proposal."""
    sizing = next(audit for audit in board["sizing_audits"] if audit["card_id"] == card_id)
    audit = next(audit for audit in board["topology_audits"] if audit["card_id"] == card_id)
    digest = compute_proposal_digest(
        card_id=card_id,
        sizing_audit=sizing,
        topology_audit=audit,
        seam_decisions=board.get("seam_decisions"),
        planning_seams=planning_seams,
    )
    audit["challenge"]["proposal_digest"] = digest
    return digest


class RiskClassificationTests(unittest.TestCase):
    def test_simple_topology_needs_no_challenge_ceremony(self) -> None:
        record = validate_topology_audit(_simple_audit(), "topology", "ready")
        self.assertEqual(record["risk"], "simple")
        self.assertNotIn("challenge", record)

    def test_unknown_risk_class_is_rejected(self) -> None:
        with self.assertRaisesRegex(TopologyError, "unknown risk class"):
            validate_topology_audit(_simple_audit(risk="maybe"), "topology", "ready")

    def test_empty_risk_basis_fails_closed(self) -> None:
        with self.assertRaisesRegex(TopologyError, "risk_basis requires a durable"):
            validate_topology_audit(_simple_audit(risk_basis="  "), "topology", "ready")
        with self.assertRaisesRegex(TopologyError, "risk_basis requires a durable"):
            validate_topology_audit(_risky_audit(risk_basis=""), "topology", "ready")

    def test_simple_topology_must_not_list_triggers(self) -> None:
        with self.assertRaisesRegex(TopologyError, "must not list risk triggers"):
            validate_topology_audit(
                _simple_audit(triggers=["material_deviation"]), "topology", "ready"
            )

    def test_simple_topology_must_not_claim_challenge_ceremony(self) -> None:
        with self.assertRaisesRegex(TopologyError, "must not claim a fresh topology challenge"):
            validate_topology_audit(
                _simple_audit(challenge=_challenge()), "topology", "ready"
            )

    def test_simple_topology_cannot_substitute_milestone_review(self) -> None:
        with self.assertRaisesRegex(TopologyError, "cannot substitute Card Review"):
            validate_topology_audit(
                _simple_audit(review_scope="milestone_integration"), "topology", "ready"
            )

    def test_risky_topology_requires_triggers(self) -> None:
        with self.assertRaisesRegex(TopologyError, "requires at least one durable risk trigger"):
            validate_topology_audit(_risky_audit(triggers=[]), "topology", "ready")

    def test_unknown_and_duplicate_triggers_are_rejected(self) -> None:
        self.assertEqual(
            RISK_TRIGGERS,
            {"preferred_seam_merge", "multiple_invariant_families",
             "whole_milestone_absorption", "milestone_review_substitution",
             "material_deviation"},
        )
        with self.assertRaisesRegex(TopologyError, "unknown risk trigger"):
            validate_topology_audit(
                _risky_audit(triggers=["milestone_strategy"]), "topology", "ready"
            )
        with self.assertRaisesRegex(TopologyError, "duplicate risk trigger"):
            validate_topology_audit(
                _risky_audit(triggers=["material_deviation", "material_deviation"]),
                "topology", "ready",
            )
        with self.assertRaisesRegex(TopologyError, "triggers must be an array"):
            validate_topology_audit(
                _risky_audit(triggers="material_deviation"), "topology", "ready"  # type: ignore[arg-type]
            )

    def test_unknown_review_scope_is_rejected(self) -> None:
        with self.assertRaisesRegex(TopologyError, "unknown review scope"):
            validate_topology_audit(
                _simple_audit(review_scope="milestone"), "topology", "ready"
            )


class ChallengeScopeTests(unittest.TestCase):
    def test_challenge_evaluates_exactly_the_narrow_dimensions(self) -> None:
        self.assertEqual(
            CHALLENGE_DIMENSIONS,
            ("boundary_fidelity", "falsifiability", "review_separation"),
        )
        record = validate_challenge(_challenge(), "challenge")
        self.assertEqual(record["verdict"], "green")

    def test_red_challenge_is_a_valid_non_green_outcome(self) -> None:
        record = validate_challenge(_challenge(verdict="red"), "challenge")
        self.assertEqual(record["verdict"], "red")

    def test_unknown_verdict_is_rejected(self) -> None:
        with self.assertRaisesRegex(TopologyError, "unknown challenge verdict"):
            validate_challenge(_challenge(verdict="pending"), "challenge")

    def test_challenge_must_cover_all_narrow_dimensions(self) -> None:
        with self.assertRaisesRegex(TopologyError, "must evaluate boundary_fidelity"):
            validate_challenge(
                _challenge(evaluated=["boundary_fidelity", "falsifiability"]), "challenge"
            )

    def test_plan_review_scope_is_rejected_as_too_broad(self) -> None:
        for broad in ("milestone_strategy", "milestone_ordering",
                      "requirement_coverage", "premium_gates"):
            with self.subTest(scope=broad):
                with self.assertRaisesRegex(TopologyError, "narrower than Plan Review"):
                    validate_challenge(
                        _challenge(evaluated=[
                            "boundary_fidelity", "falsifiability",
                            "review_separation", broad,
                        ]),
                        "challenge",
                    )

    def test_unknown_and_duplicate_dimensions_are_rejected(self) -> None:
        with self.assertRaisesRegex(TopologyError, "unknown challenge dimension"):
            validate_challenge(
                _challenge(evaluated=[
                    "boundary_fidelity", "falsifiability", "review_separation",
                    "velocity",
                ]),
                "challenge",
            )
        with self.assertRaisesRegex(TopologyError, "duplicate challenge dimension"):
            validate_challenge(
                _challenge(evaluated=[
                    "boundary_fidelity", "falsifiability",
                    "review_separation", "review_separation",
                ]),
                "challenge",
            )

    def test_empty_scope_statement_is_rejected(self) -> None:
        with self.assertRaisesRegex(TopologyError, "scope_statement requires a durable"):
            validate_challenge(_challenge(scope_statement="  "), "challenge")

    def test_self_certified_challenge_is_rejected(self) -> None:
        with self.assertRaisesRegex(TopologyError, "self-certification is rejected"):
            validate_challenge(_challenge(independent=False), "challenge")
        with self.assertRaisesRegex(TopologyError, "independence_basis requires a durable"):
            validate_challenge(_challenge(independence_basis=""), "challenge")

    def test_stale_or_reused_challenge_is_rejected(self) -> None:
        with self.assertRaisesRegex(TopologyError, "must be fresh"):
            validate_challenge(_challenge(fresh=False), "challenge")
        with self.assertRaisesRegex(TopologyError, "challenge_basis requires a durable"):
            validate_challenge(_challenge(challenge_basis="   "), "challenge")

    def test_challenge_must_be_a_table(self) -> None:
        with self.assertRaisesRegex(TopologyError, "challenge must be a table"):
            validate_topology_audit(_risky_audit(challenge="green"), "topology", "ready")


class ReviewLayeringTests(unittest.TestCase):
    def test_milestone_substituting_boundary_requires_atomicity_rationale(self) -> None:
        record = validate_topology_audit(
            _risky_audit(
                triggers=["milestone_review_substitution"],
                review_scope="milestone_integration",
                atomicity_rationale_class="atomicity",
                atomicity_rationale="Single atomic cutover migrates stores jointly; partial landing corrupts recovery.",
            ),
            "topology", "planned",
        )
        self.assertEqual(record["review_scope"], "milestone_integration")

    def test_layering_rejects_generic_and_non_atomicity_rationale(self) -> None:
        for rejected in ("convenience", "same_milestone", "fewer_cards",
                         "material_coupling", "inseparable_acceptance",
                         "invalid_intermediate_state", "faster_reviews"):
            with self.subTest(rationale_class=rejected):
                with self.assertRaisesRegex(TopologyError, "only concrete atomicity"):
                    validate_topology_audit(
                        _risky_audit(
                            triggers=["milestone_review_substitution"],
                            review_scope="milestone_integration",
                            atomicity_rationale_class=rejected,
                            atomicity_rationale="One Card is easier to review.",
                        ),
                        "topology", "planned",
                    )

    def test_layering_rejects_empty_atomicity_evidence(self) -> None:
        with self.assertRaisesRegex(TopologyError, "requires concrete atomicity rationale"):
            validate_topology_audit(
                _risky_audit(
                    triggers=["milestone_review_substitution"],
                    review_scope="milestone_integration",
                    atomicity_rationale_class="atomicity",
                    atomicity_rationale="   ",
                ),
                "topology", "planned",
            )

    def test_card_local_scope_must_not_claim_atomicity_rationale(self) -> None:
        with self.assertRaisesRegex(TopologyError, "must not claim atomicity rationale"):
            validate_topology_audit(
                _risky_audit(
                    atomicity_rationale_class="atomicity",
                    atomicity_rationale="Atomic but local.",
                ),
                "topology", "ready",
            )

    def test_substitution_trigger_and_scope_bind_both_directions(self) -> None:
        with self.assertRaisesRegex(TopologyError, "requires milestone_integration review scope"):
            validate_topology_audit(
                _risky_audit(triggers=["milestone_review_substitution"]),
                "topology", "ready",
            )
        with self.assertRaisesRegex(TopologyError, "requires the milestone_review_substitution trigger"):
            validate_topology_audit(
                _risky_audit(
                    triggers=["material_deviation"],
                    review_scope="milestone_integration",
                    atomicity_rationale_class="atomicity",
                    atomicity_rationale="Single atomic cutover.",
                ),
                "topology", "ready",
            )


class LaunchStatusGateTests(unittest.TestCase):
    def test_ready_risky_without_challenge_is_rejected(self) -> None:
        audit = _risky_audit()
        del audit["challenge"]
        with self.assertRaisesRegex(TopologyError, "before first launch"):
            validate_topology_audit(audit, "topology", "ready")

    def test_ready_risky_red_is_recorded_but_not_green(self) -> None:
        record = validate_topology_audit(
            _risky_audit(challenge=_challenge(verdict="red")), "topology", "ready"
        )
        self.assertEqual(record["challenge"]["verdict"], "red")

    def test_in_progress_requires_green_challenge(self) -> None:
        audit = _risky_audit()
        del audit["challenge"]
        with self.assertRaisesRegex(TopologyError, "without a GREEN fresh independent"):
            validate_topology_audit(audit, "topology", "in_progress")
        with self.assertRaisesRegex(TopologyError, "without a GREEN fresh independent"):
            validate_topology_audit(
                _risky_audit(challenge=_challenge(verdict="red")),
                "topology", "in_progress",
            )
        record = validate_topology_audit(_risky_audit(), "topology", "in_progress")
        self.assertEqual(record["challenge"]["verdict"], "green")

    def test_planned_risky_may_defer_the_challenge_until_launch(self) -> None:
        audit = _risky_audit()
        del audit["challenge"]
        record = validate_topology_audit(audit, "topology", "planned")
        self.assertNotIn("challenge", record)


class TopologyBoardBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workstream = read_toml(VALID / "WORKSTREAM.toml")

    def test_fixture_board_carries_simple_topology_without_ceremony(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        validate_board(board, self.workstream)
        self.assertEqual(
            [(audit["card_id"], audit["risk"]) for audit in board["topology_audits"]],
            [("M01-T02", "simple")],
        )

    def test_active_card_without_topology_audit_fails_closed(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board.pop("topology_audits", None)
        with self.assertRaisesRegex(ValidationError, "missing durable topology audit"):
            validate_board(board, self.workstream)

    def test_planned_and_ready_cards_require_topology_audits(self) -> None:
        for status in ("planned", "ready"):
            with self.subTest(status=status):
                board = read_toml(VALID / "TASK_BOARD.toml")
                board.pop("topology_audits", None)
                for card in board["cards"]:
                    if card["id"] == "M01-T02":
                        card["status"] = status
                with self.assertRaisesRegex(
                    ValidationError, "missing durable topology audit for Card 'M01-T02'"
                ):
                    validate_board(board, self.workstream)
                board["topology_audits"] = [_simple_audit(card_id="M01-T02")]
                validate_board(board, self.workstream)

    def test_done_only_board_without_topology_remains_valid(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["cards"] = [card for card in board["cards"] if card["status"] == "done"]
        board.pop("topology_audits", None)
        board.pop("sizing_audits", None)
        validate_board(board, self.workstream)

    def test_blocked_card_without_topology_validates_until_reactivated(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board.pop("topology_audits", None)
        board.pop("sizing_audits", None)
        for card in board["cards"]:
            if card["id"] == "M01-T02":
                card["status"] = "blocked"
                card["blocker"] = {
                    "class": "blocker",
                    "path": "implementation/workstreams/sample-workstream/blockers/M01-T02.toml",
                }
        validate_board(board, self.workstream)
        for card in board["cards"]:
            if card["id"] == "M01-T02":
                card["status"] = "in_progress"
        board["sizing_audits"] = [_sizing_audit(card_id="M01-T02")]
        with self.assertRaisesRegex(ValidationError, "missing durable topology audit"):
            validate_board(board, self.workstream)

    def test_topology_audits_must_bind_existing_cards_exactly_once(self) -> None:
        unknown = read_toml(VALID / "TASK_BOARD.toml")
        unknown["topology_audits"] = [_simple_audit(card_id="M09-T99")]
        with self.assertRaisesRegex(ValidationError, "unknown card_id"):
            validate_board(unknown, self.workstream)

        duplicate = read_toml(VALID / "TASK_BOARD.toml")
        duplicate["topology_audits"] = [
            _simple_audit(card_id="M01-T02"),
            _simple_audit(card_id="M01-T02"),
        ]
        with self.assertRaisesRegex(ValidationError, "duplicate topology audit"):
            validate_board(duplicate, self.workstream)

        malformed = read_toml(VALID / "TASK_BOARD.toml")
        malformed["topology_audits"] = {"card_id": "M01-T02"}
        with self.assertRaisesRegex(ValidationError, "must be an array"):
            validate_board(malformed, self.workstream)

    def test_ready_risky_without_challenge_fails_board_closed(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        for card in board["cards"]:
            if card["id"] == "M01-T02":
                card["status"] = "ready"
        audit = _risky_audit(card_id="M01-T02",
                             challenge=_challenge(verdict="red"))
        del audit["challenge"]
        board["topology_audits"] = [audit]
        with self.assertRaisesRegex(ValidationError, "before first launch"):
            validate_board(board, self.workstream)

    def test_in_progress_risky_red_fails_board_closed(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["topology_audits"] = [
            _risky_audit(card_id="M01-T02", challenge=_challenge(verdict="red"))
        ]
        with self.assertRaisesRegex(ValidationError, "without a GREEN fresh independent"):
            validate_board(board, self.workstream)

    def test_in_progress_risky_green_is_valid(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["topology_audits"] = [_risky_audit(card_id="M01-T02")]
        _bind_proposal(board, "M01-T02")
        validate_board(board, self.workstream)


class SizingCompositionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workstream = read_toml(VALID / "WORKSTREAM.toml")

    def test_multi_family_single_boundary_requires_risky_challenge(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["sizing_audits"] = [
            _sizing_audit(
                card_id="M01-T02",
                decision="single",
                outcomes=_m02_mega_outcomes(),
                rebuttal_class="atomicity",
                rebuttal="Concrete atomic cutover migrates contracts, resolution and readback jointly.",
            )
        ]
        board["topology_audits"] = [_simple_audit(card_id="M01-T02")]
        with self.assertRaisesRegex(
            ValidationError, "multiple_invariant_families trigger"
        ):
            validate_board(board, self.workstream)

        board["topology_audits"] = [
            _risky_audit(
                card_id="M01-T02",
                triggers=["multiple_invariant_families"],
                risk_basis="Single Card spans four independently falsifiable invariant families.",
            )
        ]
        _bind_proposal(board, "M01-T02")
        validate_board(board, self.workstream)

    def test_effective_families_follow_split_retention(self) -> None:
        split = _sizing_audit(
            card_id="M01-T02",
            decision="split",
            outcomes=[
                _outcome("first", kind="invariant", family="identity",
                         allocated_to="card:M01-T02"),
                _outcome("second", kind="useful_outcome", family="bundles",
                         allocated_to="card:M01-T03"),
            ],
        )
        self.assertEqual(
            effective_separable_families(split, "M01-T02"), frozenset({"identity"})
        )
        single = _sizing_audit(
            card_id="M01-T02",
            decision="single",
            outcomes=_m02_mega_outcomes(),
            rebuttal_class="atomicity",
            rebuttal="Concrete atomic cutover.",
        )
        self.assertEqual(len(effective_separable_families(single, "M01-T02")), 4)

    def test_split_retaining_one_family_stays_simple(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["cards"].append({
            "id": "M01-T03",
            "status": "planned",
            "contract": {
                "class": "task_card",
                "path": "implementation/workstreams/sample-workstream/cards/M01-T03.md",
            },
        })
        board["sizing_audits"] = [
            _sizing_audit(
                card_id="M01-T02",
                decision="split",
                outcomes=[
                    _outcome("first", kind="invariant", family="identity",
                             allocated_to="card:M01-T02"),
                    _outcome("second", kind="useful_outcome", family="bundles",
                             allocated_to="card:M01-T03"),
                ],
            ),
            _sizing_audit(card_id="M01-T03"),
        ]
        board["topology_audits"] = [
            _simple_audit(card_id="M01-T02"),
            _simple_audit(card_id="M01-T03"),
        ]
        validate_board(board, self.workstream)

    def test_dishonest_family_trigger_without_multi_family_is_rejected(self) -> None:
        with self.assertRaisesRegex(TopologyError, "single invariant family"):
            validate_topology_audits(
                [_risky_audit(triggers=["multiple_invariant_families"])],
                _cards(("M01-T02", "planned")),
                [_sizing_audit()],
            )

    def test_green_challenge_cannot_cure_invalid_sizing(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["sizing_audits"] = [
            _sizing_audit(
                card_id="M01-T02",
                decision="single",
                outcomes=_m02_mega_outcomes(),
            )
        ]
        board["topology_audits"] = [
            _risky_audit(
                card_id="M01-T02",
                triggers=["multiple_invariant_families"],
                risk_basis="Single Card spans four independently falsifiable invariant families.",
            )
        ]
        with self.assertRaisesRegex(ValidationError, "rebuttal"):
            validate_board(board, self.workstream)


class SeamCompositionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workstream = read_toml(VALID / "WORKSTREAM.toml")

    def _seams(self) -> list[dict]:
        return [
            {"id": "BOOT-A", "class": "required_seam",
             "intent": "Review discovery/convergence/observation closure stays a standalone outcome."},
            {"id": "helper-less-derivation", "class": "preferred_seam",
             "intent": "Helper-less derivation is its own outcome unless coupling evidence says otherwise."},
            {"id": "example-split", "class": "illustrative",
             "intent": "Non-binding example of how Cards could split; JIT may ignore it."},
        ]

    def test_unowned_preferred_merge_requires_risky_challenge(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["seam_decisions"] = [
            {"seam_id": "BOOT-A", "decision": "preserved"},
            {"seam_id": "helper-less-derivation", "decision": "merged",
             "rationale_class": "atomicity",
             "rationale": "Single atomic migration cannot land across two Cards."},
            {"seam_id": "example-split", "decision": "preserved"},
        ]
        with self.assertRaisesRegex(ValidationError, "no owning risky topology audit"):
            validate_board(board, self.workstream, planning_seams=self._seams())

    def test_owned_preferred_merge_with_green_challenge_is_valid(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["seam_decisions"] = [
            {"seam_id": "BOOT-A", "decision": "preserved"},
            {"seam_id": "helper-less-derivation", "decision": "merged",
             "rationale_class": "atomicity",
             "rationale": "Single atomic migration cannot land across two Cards."},
            {"seam_id": "example-split", "decision": "preserved"},
        ]
        board["topology_audits"] = [
            _risky_audit(
                card_id="M01-T02",
                triggers=["preferred_seam_merge"],
                risk_basis="Merges preferred seam helper-less-derivation with atomicity rationale.",
            )
        ]
        _bind_proposal(board, "M01-T02", planning_seams=self._seams())
        validate_board(board, self.workstream, planning_seams=self._seams())

    def test_claimed_merge_without_board_merge_is_rejected(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["seam_decisions"] = [
            {"seam_id": "BOOT-A", "decision": "preserved"},
            {"seam_id": "helper-less-derivation", "decision": "preserved"},
            {"seam_id": "example-split", "decision": "preserved"},
        ]
        board["topology_audits"] = [
            _risky_audit(
                card_id="M01-T02",
                triggers=["preferred_seam_merge"],
                risk_basis="Claims a preferred merge the Board does not record.",
            )
        ]
        with self.assertRaisesRegex(ValidationError, "no merged preferred_seam"):
            validate_board(board, self.workstream, planning_seams=self._seams())

    def test_absorption_requires_explicit_declared_seams(self) -> None:
        with self.assertRaisesRegex(TopologyError, "requires explicit declared Planning seams"):
            validate_topology_audits(
                [_risky_audit(triggers=["whole_milestone_absorption"])],
                _cards(("M01-T02", "planned")),
                [_sizing_audit()],
                [],
                None,
            )

    def test_absorption_with_explicit_seams_is_valid(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        for card in board["cards"]:
            if card["id"] == "M01-T02":
                card["status"] = "planned"
        board["sizing_audits"] = [
            _sizing_audit(
                card_id="M01-T02",
                decision="single",
                outcomes=_m02_mega_outcomes(),
                rebuttal_class="atomicity",
                rebuttal="Concrete atomic cutover migrates contracts, resolution and readback jointly.",
            )
        ]
        board["seam_decisions"] = [
            {"seam_id": "BOOT-A", "decision": "preserved"},
            {"seam_id": "helper-less-derivation", "decision": "preserved"},
            {"seam_id": "example-split", "decision": "preserved"},
        ]
        board["topology_audits"] = [
            _risky_audit(
                card_id="M01-T02",
                triggers=["multiple_invariant_families", "whole_milestone_absorption"],
                risk_basis="One Card absorbs the whole milestone across explicit seams and four families.",
            )
        ]
        _bind_proposal(board, "M01-T02", planning_seams=self._seams())
        validate_board(board, self.workstream, planning_seams=self._seams())


class MegaCardRegressionTests(unittest.TestCase):
    """Historical M02 mega-Card topology replays as immutable in-test evidence."""

    def setUp(self) -> None:
        self.workstream = read_toml(VALID / "WORKSTREAM.toml")

    def test_m02_mega_topology_cannot_launch_simple(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        for card in board["cards"]:
            if card["id"] == "M01-T02":
                card["status"] = "ready"
        board["sizing_audits"] = [
            _sizing_audit(
                card_id="M01-T02",
                decision="single",
                outcomes=_m02_mega_outcomes(),
                rebuttal_class="atomicity",
                rebuttal="Concrete atomic cutover migrates contracts, resolution and readback jointly.",
            )
        ]
        board["topology_audits"] = [_simple_audit(card_id="M01-T02")]
        with self.assertRaisesRegex(
            ValidationError, "multiple_invariant_families trigger"
        ):
            validate_board(board, self.workstream)

    def test_m02_mega_topology_with_green_challenge_is_honest(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        for card in board["cards"]:
            if card["id"] == "M01-T02":
                card["status"] = "planned"
        board["sizing_audits"] = [
            _sizing_audit(
                card_id="M01-T02",
                decision="single",
                outcomes=_m02_mega_outcomes(),
                rebuttal_class="atomicity",
                rebuttal="Concrete atomic cutover migrates contracts, resolution and readback jointly.",
            )
        ]
        board["topology_audits"] = [
            _risky_audit(
                card_id="M01-T02",
                triggers=["multiple_invariant_families", "material_deviation"],
                risk_basis="Whole-milestone Card spans four separable families; challenged before launch.",
            )
        ]
        _bind_proposal(board, "M01-T02")
        validate_board(board, self.workstream)

    def test_historical_done_state_needs_no_topology_challenge(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["cards"] = [card for card in board["cards"] if card["status"] == "done"]
        board.pop("topology_audits", None)
        board.pop("sizing_audits", None)
        validate_board(board, self.workstream)
        self.assertEqual([card["id"] for card in board["cards"]], ["M01-T01"])


class StaleChallengeTests(unittest.TestCase):
    """A GREEN challenge binds the exact challenged proposal, not a stale one."""

    def setUp(self) -> None:
        self.workstream = read_toml(VALID / "WORKSTREAM.toml")

    def _seams(self) -> list[dict]:
        return [
            {"id": "BOOT-A", "class": "required_seam",
             "intent": "Review discovery/convergence/observation closure stays a standalone outcome."},
            {"id": "helper-less-derivation", "class": "preferred_seam",
             "intent": "Helper-less derivation is its own outcome unless coupling evidence says otherwise."},
            {"id": "example-split", "class": "illustrative",
             "intent": "Non-binding example of how Cards could split; JIT may ignore it."},
        ]

    def _bound_board(self) -> dict:
        board = read_toml(VALID / "TASK_BOARD.toml")
        for card in board["cards"]:
            if card["id"] == "M01-T02":
                card["status"] = "planned"
        board["topology_audits"] = [_risky_audit(card_id="M01-T02")]
        _bind_proposal(board, "M01-T02")
        validate_board(board, self.workstream)
        return board

    def test_bound_challenge_survives_status_and_revision_changes(self) -> None:
        board = self._bound_board()
        for status in ("ready", "in_progress"):
            with self.subTest(status=status):
                for card in board["cards"]:
                    if card["id"] == "M01-T02":
                        card["status"] = status
                board["revision"] += 1
                validate_board(board, self.workstream)

    def test_stale_green_after_sizing_change_is_rejected(self) -> None:
        board = self._bound_board()
        board["sizing_audits"][0]["dimensions"]["reviewability"] = (
            "Rewritten reviewability evidence after the challenge was recorded."
        )
        with self.assertRaisesRegex(
            ValidationError, "does not match the exact current proposed topology"
        ):
            validate_board(board, self.workstream)

    def test_stale_green_after_risk_field_change_is_rejected(self) -> None:
        board = self._bound_board()
        board["topology_audits"][0]["risk_basis"] = (
            "Rewritten risk basis describing a different deviation."
        )
        with self.assertRaisesRegex(
            ValidationError, "does not match the exact current proposed topology"
        ):
            validate_board(board, self.workstream)

    def test_stale_green_after_seam_decision_change_is_rejected(self) -> None:
        board = self._bound_board()
        board["seam_decisions"] = [
            {"seam_id": "BOOT-A", "decision": "preserved"},
            {"seam_id": "helper-less-derivation", "decision": "preserved"},
            {"seam_id": "example-split", "decision": "preserved"},
        ]
        _bind_proposal(board, "M01-T02", planning_seams=self._seams())
        validate_board(board, self.workstream, planning_seams=self._seams())
        board["seam_decisions"][2] = {"seam_id": "example-split", "decision": "merged"}
        with self.assertRaisesRegex(
            ValidationError, "does not match the exact current proposed topology"
        ):
            validate_board(board, self.workstream, planning_seams=self._seams())

    def test_missing_and_unsupported_binding_fail_closed(self) -> None:
        missing = _challenge()
        del missing["proposal_digest"]
        with self.assertRaisesRegex(TopologyError, "requires a durable subject binding"):
            validate_challenge(missing, "challenge")
        for bad in ("", "md5:" + "0" * 32, "sha256:xyz", "sha256:" + "0" * 63):
            with self.subTest(binding=bad or "<empty>"):
                with self.assertRaisesRegex(TopologyError, "subject binding"):
                    validate_challenge(_challenge(proposal_digest=bad), "challenge")
        card_missing = _challenge()
        del card_missing["card_contract_digest"]
        with self.assertRaisesRegex(TopologyError, "requires a durable subject binding"):
            validate_challenge(card_missing, "challenge")
        with self.assertRaisesRegex(TopologyError, "unsupported topology subject binding"):
            validate_challenge(
                _challenge(card_contract_digest="not-a-digest"), "challenge"
            )

    def test_proposal_digest_is_deterministic_and_material_sensitive(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        sizing = next(audit for audit in board["sizing_audits"] if audit["card_id"] == "M01-T02")
        audit = _risky_audit(card_id="M01-T02")
        first = compute_proposal_digest(
            card_id="M01-T02", sizing_audit=sizing, topology_audit=audit
        )
        second = compute_proposal_digest(
            card_id="M01-T02", sizing_audit=sizing, topology_audit=audit
        )
        self.assertEqual(first, second)
        self.assertRegex(first, r"^sha256:[0-9a-f]{64}$")
        moved = copy.deepcopy(audit)
        moved["triggers"] = ["material_deviation", "whole_milestone_absorption"]
        self.assertNotEqual(
            first,
            compute_proposal_digest(
                card_id="M01-T02", sizing_audit=sizing, topology_audit=moved,
                planning_seams=[{"id": "S", "class": "required_seam", "intent": "I."}],
            ),
        )
        self.assertRegex(
            compute_card_contract_digest(b"# Card\n"), r"^sha256:[0-9a-f]{64}$"
        )


class TopologyRouterPathTests(unittest.TestCase):
    def copy_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(ROUTER_FIXTURE, project)
        return temp, project

    def task_card_content(self) -> str:
        return (
            "# Fixture Card\n"
            "- Card ID: M01-T04\n"
            "- Included scope: prove launch readiness\n"
            "- Excluded scope: runtime-specific orchestration\n"
            "- Authority refs: requirements/REQUIREMENTS.md\n"
            "- Dependencies: none\n"
            "- Acceptance: route only after current launch inputs are valid\n"
            "- Required tests/readback: production router fixture\n"
            "- Review requirement: none\n"
            "- Technical contract: none\n"
        )

    def make_ready_card(self, project: Path) -> None:
        board = project / ROUTER_BOARD
        board.write_text(board.read_text().replace(
            'status = "in_progress"', 'status = "ready"'))
        (project / ROUTER_CARD).write_text(self.task_card_content())
        authority = project / "requirements" / "REQUIREMENTS.md"
        authority.parent.mkdir(parents=True, exist_ok=True)
        authority.write_text("# Accepted authority\n")

    def simple_topology_block(self) -> str:
        return (
            "# topology audit for M01-T04: simple single-outcome scope needs no fresh challenge.\n"
            "[[topology_audits]]\n"
            'card_id = "M01-T04"\n'
            'risk = "simple"\n'
            "triggers = []\n"
            'risk_basis = "Single coherent outcome in one invariant family with no seam merge, milestone absorption or material deviation."\n'
            'review_scope = "card_local"\n'
            'atomicity_rationale_class = ""\n'
            'atomicity_rationale = ""\n'
        )

    def risky_topology_block(self, verdict: str) -> str:
        return (
            "# topology audit for M01-T04: risky boundary challenged before first launch.\n"
            "[[topology_audits]]\n"
            'card_id = "M01-T04"\n'
            'risk = "risky"\n'
            'triggers = ["material_deviation"]\n'
            'risk_basis = "Proposed boundary deviates materially from accepted decomposition intent."\n'
            'review_scope = "card_local"\n'
            'atomicity_rationale_class = ""\n'
            'atomicity_rationale = ""\n'
            "[topology_audits.challenge]\n"
            f'verdict = "{verdict}"\n'
            'evaluated = ["boundary_fidelity", "falsifiability", "review_separation"]\n'
            'scope_statement = "Card holds one contract outcome with a deviating boundary; fidelity, falsifiability and review split checked."\n'
            "independent = true\n"
            'independence_basis = "Challenger did not author the Execution Prep topology proposal."\n'
            "fresh = true\n"
            'challenge_basis = "Fresh review of the current proposed boundary against sizing outcomes."\n'
            f'proposal_digest = "{_PLACEHOLDER_PROPOSAL_DIGEST}"\n'
            f'card_contract_digest = "{_PLACEHOLDER_CARD_DIGEST}"\n'
        )

    def install_risky_topology(self, project: Path, verdict: str) -> None:
        import tomllib

        board = project / ROUTER_BOARD
        text = board.read_text()
        self.assertIn(self.simple_topology_block(), text)
        board.write_text(text.replace(
            self.simple_topology_block(), self.risky_topology_block(verdict)))
        data = tomllib.loads(board.read_text())
        sizing = next(audit for audit in data["sizing_audits"] if audit["card_id"] == "M01-T04")
        audit = next(audit for audit in data["topology_audits"] if audit["card_id"] == "M01-T04")
        proposal = compute_proposal_digest(
            card_id="M01-T04",
            sizing_audit=sizing,
            topology_audit=audit,
            seam_decisions=data.get("seam_decisions"),
            planning_seams=None,
        )
        card_digest = compute_card_contract_digest((project / ROUTER_CARD).read_bytes())
        rebound = board.read_text().replace(_PLACEHOLDER_PROPOSAL_DIGEST, proposal)
        rebound = rebound.replace(_PLACEHOLDER_CARD_DIGEST, card_digest)
        self.assertNotIn(_PLACEHOLDER_PROPOSAL_DIGEST, rebound)
        self.assertNotIn(_PLACEHOLDER_CARD_DIGEST, rebound)
        board.write_text(rebound)

    def test_ready_simple_topology_launches_without_ceremony(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.make_ready_card(project)
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution_prep"))
            self.assertEqual(routed.subject, "M01-T04")
        finally:
            temp.cleanup()

    def test_ready_risky_red_routes_to_topology_challenge(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.make_ready_card(project)
            self.install_risky_topology(project, "red")
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "topology_challenge", "M01-T04"),
            )
            self.assertEqual(routed.owner_module, "workflow/EXECUTION_PREP.md")
            self.assertIn("fresh independent topology challenge", routed.reason)
        finally:
            temp.cleanup()

    def test_ready_risky_green_proceeds_to_launch_refresh(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.make_ready_card(project)
            self.install_risky_topology(project, "green")
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution_prep", "M01-T04"),
            )
        finally:
            temp.cleanup()

    def test_ready_risky_without_challenge_recovers(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.make_ready_card(project)
            board = project / ROUTER_BOARD
            text = board.read_text()
            self.assertIn(self.simple_topology_block(), text)
            risky_without_challenge = self.risky_topology_block("red").split(
                "[topology_audits.challenge]")[0]
            board.write_text(text.replace(
                self.simple_topology_block(), risky_without_challenge))
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("before first launch", routed.reason)
        finally:
            temp.cleanup()

    def test_ready_green_bound_to_old_card_contract_recovers(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.make_ready_card(project)
            self.install_risky_topology(project, "green")
            bound = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (bound.disposition, bound.obligation, bound.subject),
                ("route", "execution_prep", "M01-T04"),
            )
            card = project / ROUTER_CARD
            card.write_text(card.read_text().replace(
                "prove launch readiness", "prove a materially rewritten launch scope"))
            stale = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (stale.disposition, stale.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("stale", stale.reason)
        finally:
            temp.cleanup()

    def test_in_progress_risky_green_routes_to_execution(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_risky_topology(project, "green")
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution", "M01-T04"),
            )
        finally:
            temp.cleanup()

    def test_topology_hold_helper_only_holds_single_ready_risky(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        self.assertIsNone(ready_topology_hold(board))
        held = copy.deepcopy(board)
        for card in held["cards"]:
            if card["id"] == "M01-T02":
                card["status"] = "ready"
        held["topology_audits"] = [
            _risky_audit(card_id="M01-T02", challenge=_challenge(verdict="red"))
        ]
        self.assertEqual(ready_topology_hold(held), "M01-T02")
        held["topology_audits"] = [_risky_audit(card_id="M01-T02")]
        self.assertIsNone(ready_topology_hold(held))

    def test_topology_challenge_refinement_stays_in_execution_prep(self) -> None:
        owner, reason = classify_jit_refinement("topology_challenge")
        self.assertEqual(owner, "execution_prep")
        self.assertIn("fresh independent", reason)


if __name__ == "__main__":
    unittest.main()
