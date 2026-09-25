from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from tools.card_sizing_contract import (
    AUDIT_DIMENSIONS,
    REBUTTAL_CLASSES,
    CardSizingError,
    parse_allocation,
    required_decision,
    separable_outcomes,
    validate_audit_dimensions,
    validate_outcome,
    validate_sizing_audit,
    validate_sizing_audits,
    validate_sizing_decision,
    validate_split_coverage,
)
from tools.router import select_route
from tools.state_contract import (
    ValidationError,
    read_toml,
    validate_board,
)

ROOT = Path(__file__).resolve().parents[1]
VALID = ROOT / "tests" / "fixtures" / "state" / "valid"
ROUTER_FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"
ROUTER_MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
ROUTER_BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"


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


def _audit(card_id: str = "M01-T02", **overrides) -> dict:
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


def _split_outcomes(first_dest: str = "card:M01-T02",
                    second_dest: str = "card:M01-T03") -> list[dict]:
    return [
        _outcome("first", kind="invariant", family="identity",
                 allocated_to=first_dest),
        _outcome("second", kind="useful_outcome", family="bundles",
                 allocated_to=second_dest),
    ]


def _add_card(board: dict, card_id: str, status: str) -> None:
    card: dict = {
        "id": card_id,
        "status": status,
        "contract": {
            "class": "task_card",
            "path": f"implementation/workstreams/sample-workstream/cards/{card_id}.md",
        },
    }
    if status == "blocked":
        card["blocker"] = {
            "class": "blocker",
            "path": f"implementation/workstreams/sample-workstream/blockers/{card_id}.toml",
        }
    board["cards"].append(card)


def _add_trigger(board: dict, trigger_id: str, after_card: str, state: str) -> None:
    board.setdefault("jit_triggers", []).append({
        "id": trigger_id,
        "after_card": after_card,
        "state": state,
        "condition": f"Downstream boundary {trigger_id} holds split scope.",
    })


def _m02_mega_outcomes() -> list[dict]:
    """Replay the historical M02-T01 whole-milestone scope as four separable outcomes.

    The fixture is immutable in-test evidence derived from the stable M02-T01
    Card text (REQ-018..033: contracts, authority resolution, identity/
    freshness/stale reconciliation, governed mutation/readback). It never edits
    the historical M02 Board or reviews.
    """
    return [
        _outcome(
            "m02-obligation-result-contracts",
            kind="contract",
            statement="Versioned transport-neutral Obligation/Result contracts with schema goldens.",
            family="execution-contracts",
        ),
        _outcome(
            "m02-authority-resolution",
            kind="invariant",
            statement="PW-owned exact authority resolution with bounded required-source bundles.",
            family="authority-resolution",
        ),
        _outcome(
            "m02-identity-freshness",
            kind="invariant",
            statement="Deterministic obligation identity, minimal fingerprints, stale-result reconciliation.",
            family="result-identity",
        ),
        _outcome(
            "m02-governed-mutation",
            kind="acceptance",
            statement="Mutation pre/postconditions with coordinator-owned writes and mandatory readback.",
            family="governed-mutation",
        ),
    ]


class SemanticInvariantTests(unittest.TestCase):
    def test_one_coherent_falsifiable_substantial_outcome_is_single(self) -> None:
        decision = validate_sizing_decision(outcomes=[_outcome()], decision="single")
        self.assertEqual(decision, "single")
        self.assertEqual(required_decision([_outcome()]), "single")
        record = validate_sizing_audit(_audit(), "task_board.sizing_audits[0]")
        self.assertEqual(record["decision"], "single")

    def test_non_falsifiable_fragment_is_rejected_as_micro_card(self) -> None:
        with self.assertRaisesRegex(CardSizingError, "not independently falsifiable"):
            validate_outcome(
                _outcome(falsifiable=False), "task_board.sizing_audits[0].outcomes[0]"
            )

    def test_insubstantial_fragment_is_rejected_as_micro_card(self) -> None:
        with self.assertRaisesRegex(CardSizingError, "not substantial enough"):
            validate_outcome(
                _outcome("rename-helper", substantial=False),
                "task_board.sizing_audits[0].outcomes[0]",
            )

    def test_empty_outcome_set_is_rejected(self) -> None:
        with self.assertRaisesRegex(CardSizingError, "at least one meaningful outcome"):
            validate_sizing_decision(outcomes=[], decision="single")

    def test_split_of_coherent_scope_is_rejected_as_fragmentation(self) -> None:
        coherent = _outcome(independently_useful=False)
        with self.assertRaisesRegex(CardSizingError, "must not be split into"):
            validate_sizing_decision(outcomes=[coherent], decision="split")

    def test_duplicate_outcome_ids_are_rejected(self) -> None:
        with self.assertRaisesRegex(CardSizingError, "duplicate outcome id"):
            validate_sizing_decision(
                outcomes=[_outcome("same"), _outcome("same")], decision="split"
            )


class StructuralBoundaryTests(unittest.TestCase):
    def test_structural_kinds_cannot_force_a_split(self) -> None:
        for kind in ("file", "module", "layer", "test", "tool", "step"):
            with self.subTest(kind=kind):
                with self.assertRaisesRegex(CardSizingError, "neither forces nor prevents"):
                    validate_outcome(
                        _outcome(f"only-{kind}", kind=kind),
                        "task_board.sizing_audits[0].outcomes[0]",
                    )

    def test_shared_module_colocation_does_not_prevent_a_split(self) -> None:
        first = _outcome(
            "router-predicate",
            kind="invariant",
            statement="Router predicate in tools/router.py with its own parity fixtures.",
            family="routing",
            allocated_to="card:M01-T02",
        )
        second = _outcome(
            "router-recovery",
            kind="acceptance",
            statement="Recovery routing in tools/router.py verified by disjoint fixtures.",
            family="recovery",
            allocated_to="jit:after-M01-T02",
        )
        self.assertEqual(required_decision([first, second]), "split")
        decision = validate_sizing_decision(outcomes=[first, second], decision="split")
        self.assertEqual(decision, "split")

    def test_unknown_outcome_kind_is_rejected(self) -> None:
        with self.assertRaisesRegex(CardSizingError, "unknown outcome kind"):
            validate_outcome(
                _outcome(kind="milestone"), "task_board.sizing_audits[0].outcomes[0]"
            )


class ScaffoldingTests(unittest.TestCase):
    def test_unconsumed_scaffolding_cannot_stand_alone(self) -> None:
        with self.assertRaisesRegex(CardSizingError, "stays with the outcome it enables"):
            validate_outcome(
                _outcome("scaffold", scaffolding_only=True),
                "task_board.sizing_audits[0].outcomes[0]",
            )

    def test_independently_consumed_scaffolding_is_a_real_outcome(self) -> None:
        record = validate_outcome(
            _outcome(
                "shared-harness",
                kind="useful_outcome",
                statement="Shared harness consumed independently by two later Cards.",
                scaffolding_only=True,
                independently_consumed=True,
            ),
            "task_board.sizing_audits[0].outcomes[0]",
        )
        self.assertTrue(record["independently_consumed"])


class SplitDecisionMatrixTests(unittest.TestCase):
    def test_two_separable_outcomes_require_split_by_default(self) -> None:
        outcomes = [
            _outcome("first", kind="invariant", family="identity",
                     allocated_to="card:M01-T02"),
            _outcome("second", kind="useful_outcome", family="bundles",
                     allocated_to="card:M01-T03"),
        ]
        self.assertEqual(len(separable_outcomes(outcomes)), 2)
        self.assertEqual(required_decision(outcomes), "split")
        self.assertEqual(
            validate_sizing_decision(outcomes=outcomes, decision="split"), "split"
        )

    def test_single_over_separable_outcomes_without_rebuttal_fails(self) -> None:
        outcomes = [
            _outcome("first", kind="acceptance", family="routing"),
            _outcome("second", kind="contract", family="schemas"),
        ]
        with self.assertRaisesRegex(CardSizingError, "unknown rebuttal class"):
            validate_sizing_decision(outcomes=outcomes, decision="single")

    def test_each_qualifying_rebuttal_class_permits_single(self) -> None:
        self.assertEqual(
            REBUTTAL_CLASSES,
            {"atomicity", "invalid_intermediate_state",
             "inseparable_acceptance", "material_coupling"},
        )
        for rebuttal_class in sorted(REBUTTAL_CLASSES):
            with self.subTest(rebuttal_class=rebuttal_class):
                outcomes = [
                    _outcome("first", kind="invariant", family="migration"),
                    _outcome("second", kind="contract", family="compat"),
                ]
                decision = validate_sizing_decision(
                    outcomes=outcomes,
                    decision="single",
                    rebuttal_class=rebuttal_class,
                    rebuttal=f"Concrete {rebuttal_class} evidence with exact migration paths.",
                )
                self.assertEqual(decision, "single")

    def test_atomic_mutation_rebuttal_covers_migration_coupling(self) -> None:
        outcomes = [
            _outcome("migrate", kind="invariant", family="migration"),
            _outcome("compat", kind="contract", family="compat"),
        ]
        record = validate_sizing_audit(
            _audit(
                decision="single",
                outcomes=outcomes,
                rebuttal_class="atomicity",
                rebuttal="Single atomic migration rewrites both stores; partial landing corrupts recovery.",
                dimensions=_dimensions(
                    atomic_mutation_migration="Joint landing is atomic; split landing has no valid intermediate state.",
                    cross_surface_coupling="Shared migration transaction couples both surfaces materially.",
                ),
            ),
            "task_board.sizing_audits[0]",
        )
        self.assertEqual(record["decision"], "single")

    def test_material_coupling_rebuttal_covers_cross_surface_coupling(self) -> None:
        outcomes = [
            _outcome("writer", kind="invariant", family="mutation"),
            _outcome("reader", kind="useful_outcome", family="consumers"),
        ]
        record = validate_sizing_audit(
            _audit(
                decision="single",
                outcomes=outcomes,
                rebuttal_class="material_coupling",
                rebuttal="Shared mutable Task Board revision couples writer and reader acceptance.",
                dimensions=_dimensions(
                    cross_surface_coupling="Writer/reader share one mutable revision with joint acceptance.",
                ),
            ),
            "task_board.sizing_audits[0]",
        )
        self.assertEqual(record["decision"], "single")

    def test_dependent_outcomes_without_independent_usefulness_stay_single(self) -> None:
        first = _outcome("schema", kind="contract", family="schemas")
        second = _outcome(
            "consumer",
            kind="useful_outcome",
            family="consumers",
            independently_useful=False,
        )
        self.assertEqual(required_decision([first, second]), "single")
        record = validate_sizing_audit(
            _audit(
                outcomes=[first, second],
                dimensions=_dimensions(
                    dependency_ordering="Consumer needs the schema result first; strict order enforced.",
                ),
            ),
            "task_board.sizing_audits[0]",
        )
        self.assertEqual(record["decision"], "single")

    def test_non_verifiable_outcome_is_not_separable(self) -> None:
        first = _outcome("first")
        second = _outcome("second", independently_verifiable=False)
        self.assertEqual(required_decision([first, second]), "single")

    def test_generic_rebuttal_classes_are_rejected(self) -> None:
        outcomes = [_outcome("first"), _outcome("second")]
        for rejected in ("convenience", "same_milestone", "same-milestone",
                         "fewer_cards", "fewer-cards", "file_boundary",
                         "step_boundary", "scaffolding_colocation"):
            with self.subTest(rebuttal_class=rejected):
                with self.assertRaisesRegex(CardSizingError, "cannot rebut the split"):
                    validate_sizing_decision(
                        outcomes=outcomes,
                        decision="single",
                        rebuttal_class=rejected,
                        rebuttal="Merge for convenience in one milestone.",
                    )

    def test_seam_only_predecessor_evidence_cannot_rebut_a_split(self) -> None:
        outcomes = [_outcome("first"), _outcome("second")]
        with self.assertRaisesRegex(CardSizingError, "Planning-seam deviation"):
            validate_sizing_decision(
                outcomes=outcomes,
                decision="single",
                rebuttal_class="new_predecessor_evidence",
                rebuttal="Predecessor result suggests one Card.",
            )

    def test_unknown_rebuttal_class_and_empty_evidence_are_rejected(self) -> None:
        outcomes = [_outcome("first"), _outcome("second")]
        with self.assertRaisesRegex(CardSizingError, "unknown rebuttal class"):
            validate_sizing_decision(
                outcomes=outcomes,
                decision="single",
                rebuttal_class="faster_reviews",
                rebuttal="One review is faster.",
            )
        with self.assertRaisesRegex(CardSizingError, "durable non-empty evidence"):
            validate_sizing_decision(
                outcomes=outcomes,
                decision="single",
                rebuttal_class="atomicity",
                rebuttal="   ",
            )

    def test_decisions_following_the_presumption_must_not_claim_rationale(self) -> None:
        with self.assertRaisesRegex(CardSizingError, "must not claim deviation rationale"):
            validate_sizing_decision(
                outcomes=[_outcome()],
                decision="single",
                rebuttal_class="atomicity",
                rebuttal="Atomic but unnecessary.",
            )
        with self.assertRaisesRegex(CardSizingError, "must not claim deviation rationale"):
            validate_sizing_decision(
                outcomes=[_outcome("first"), _outcome("second")],
                decision="split",
                rebuttal_class="atomicity",
                rebuttal="Atomic but splitting anyway.",
            )


class SplitAllocationTests(unittest.TestCase):
    def test_split_without_any_allocation_is_rejected(self) -> None:
        outcomes = [_outcome("first"), _outcome("second")]
        with self.assertRaisesRegex(
            CardSizingError, "without durable allocation: first, second"
        ):
            validate_sizing_decision(outcomes=outcomes, decision="split")

    def test_split_with_partially_missing_allocation_names_uncovered_outcome(self) -> None:
        outcomes = [
            _outcome("first", allocated_to="card:M01-T02"),
            _outcome("second"),
        ]
        with self.assertRaisesRegex(
            CardSizingError, "without durable allocation: second"
        ):
            validate_sizing_decision(outcomes=outcomes, decision="split")

    def test_split_to_one_destination_is_rejected(self) -> None:
        for outcomes in (
            _split_outcomes("card:M01-T02", "card:M01-T02"),
            [
                _outcome("a", allocated_to="jit:after-M01-T02"),
                _outcome("b", allocated_to="jit:after-M01-T02"),
                _outcome("c", allocated_to="jit:after-M01-T02"),
            ],
        ):
            with self.subTest(outcomes=[o["id"] for o in outcomes]):
                with self.assertRaisesRegex(CardSizingError, "one destination"):
                    validate_sizing_decision(outcomes=outcomes, decision="split")

    def test_split_coverage_returns_sorted_distinct_destinations(self) -> None:
        destinations = validate_split_coverage(
            [
                {"id": "b", "allocated_to": "jit:after-M01-T02"},
                {"id": "a", "allocated_to": "card:M01-T02"},
            ],
            "sizing",
        )
        self.assertEqual(destinations, ["card:M01-T02", "jit:after-M01-T02"])

    def test_malformed_allocations_are_rejected(self) -> None:
        for bad in ("M01-T03", "card:", "card:  ", "split:M01-T03", "jit:",
                    " CARD:M01-T03"):
            with self.subTest(allocated_to=bad):
                with self.assertRaisesRegex(CardSizingError, "invalid split allocation"):
                    validate_outcome(
                        _outcome(allocated_to=bad),
                        "task_board.sizing_audits[0].outcomes[0]",
                    )
        for bad in (42, None, ["card:M01-T03"]):
            with self.subTest(allocated_to=bad):
                with self.assertRaisesRegex(CardSizingError, "must be a string"):
                    validate_outcome(
                        _outcome(allocated_to=bad),
                        "task_board.sizing_audits[0].outcomes[0]",
                    )

    def test_parse_allocation_returns_kind_and_ref(self) -> None:
        self.assertEqual(
            parse_allocation("card:M01-T03", "label"), ("card", "M01-T03")
        )
        self.assertEqual(
            parse_allocation("jit:after-M01-T02", "label"), ("jit", "after-M01-T02")
        )

    def test_single_decision_must_not_claim_split_allocation(self) -> None:
        with self.assertRaisesRegex(CardSizingError, "must not claim split allocation"):
            validate_sizing_decision(
                outcomes=[_outcome(allocated_to="card:M01-T02")],
                decision="single",
            )
        with self.assertRaisesRegex(CardSizingError, "must not claim split allocation"):
            validate_sizing_decision(
                outcomes=_split_outcomes(),
                decision="single",
                rebuttal_class="atomicity",
                rebuttal="Concrete atomic cutover with exact migration paths.",
            )

    def test_split_across_card_and_trigger_destinations_is_valid(self) -> None:
        decision = validate_sizing_decision(
            outcomes=_split_outcomes("card:M01-T02", "jit:after-M01-T02"),
            decision="split",
        )
        self.assertEqual(decision, "split")


class DecompositionAuditTests(unittest.TestCase):
    def test_all_seven_dimensions_are_required(self) -> None:
        self.assertEqual(
            AUDIT_DIMENSIONS,
            ("independent_implementability", "falsifiability_testability",
             "reviewability", "invariant_contract_family", "dependency_ordering",
             "atomic_mutation_migration", "cross_surface_coupling"),
        )
        records = validate_audit_dimensions(_dimensions(), "task_board.sizing_audits[0].dimensions")
        self.assertEqual(set(records), set(AUDIT_DIMENSIONS))

    def test_each_dimension_covers_its_accepted_concern(self) -> None:
        dimensions = _dimensions(
            independent_implementability="Kernel helper builds alone; docs follow without code coupling.",
            falsifiability_testability="Helper parity test fails before the fix and passes after.",
            reviewability="One bounded Card review covers helper plus contract text.",
            invariant_contract_family="Routing invariant family stays disjoint from recovery family.",
            dependency_ordering="No DONE predecessor result is consumed; order is free.",
            atomic_mutation_migration="No atomic multi-path mutation; migration is lazy per workstream.",
            cross_surface_coupling="Helper, docs and fixtures share no mutable surface.",
        )
        records = validate_audit_dimensions(dimensions, "audit.dimensions")
        for name in AUDIT_DIMENSIONS:
            self.assertTrue(records[name].strip())

    def test_missing_dimension_fails_closed(self) -> None:
        for name in AUDIT_DIMENSIONS:
            with self.subTest(dimension=name):
                dimensions = _dimensions()
                del dimensions[name]
                with self.assertRaisesRegex(CardSizingError, "missing durable audit"):
                    validate_audit_dimensions(dimensions, "audit.dimensions")

    def test_empty_and_placeholder_dimensions_fail_closed(self) -> None:
        with self.assertRaisesRegex(CardSizingError, "non-empty statement"):
            validate_audit_dimensions(
                _dimensions(reviewability="   "), "audit.dimensions"
            )
        for placeholder in ("n/a", "N/A", "none", "TBD", "todo"):
            with self.subTest(placeholder=placeholder):
                with self.assertRaisesRegex(CardSizingError, "placeholder evidence"):
                    validate_audit_dimensions(
                        _dimensions(cross_surface_coupling=placeholder),
                        "audit.dimensions",
                    )

    def test_undeclared_dimension_is_rejected(self) -> None:
        with self.assertRaisesRegex(CardSizingError, "unknown audit dimension"):
            validate_audit_dimensions(
                _dimensions(topology_challenge="Fresh challenge."), "audit.dimensions"
            )

    def test_audit_without_dimensions_table_fails_closed(self) -> None:
        audit = _audit()
        del audit["dimensions"]
        with self.assertRaisesRegex(CardSizingError, "missing durable audit"):
            validate_sizing_audit(audit, "task_board.sizing_audits[0]")
        audit = _audit(dimensions="all seven addressed")
        with self.assertRaisesRegex(CardSizingError, "dimensions must be a table"):
            validate_sizing_audit(audit, "task_board.sizing_audits[0]")


class MegaCardRegressionTests(unittest.TestCase):
    def test_historical_m02_topology_fails_without_concrete_rebuttal(self) -> None:
        outcomes = _m02_mega_outcomes()
        self.assertEqual(len(separable_outcomes(outcomes)), 4)
        self.assertEqual(required_decision(outcomes), "split")
        with self.assertRaisesRegex(CardSizingError, "unknown rebuttal class"):
            validate_sizing_decision(outcomes=outcomes, decision="single")
        with self.assertRaisesRegex(CardSizingError, "cannot rebut the split"):
            validate_sizing_decision(
                outcomes=outcomes,
                decision="single",
                rebuttal_class="same_milestone",
                rebuttal="M02 milestone scope belongs in one Card.",
            )

    def test_m02_surfaces_split_cleanly_across_distinct_families(self) -> None:
        outcomes = _m02_mega_outcomes()
        families = {outcome["family"] for outcome in outcomes}
        self.assertEqual(len(families), 4)
        kinds = {outcome["kind"] for outcome in outcomes}
        self.assertTrue({"contract", "invariant", "acceptance"} <= kinds)
        destinations = ("card:M02-T01", "card:M02-T02", "jit:after-M02-T01", "jit:after-M02-T02")
        for outcome, destination in zip(outcomes, destinations):
            outcome["allocated_to"] = destination
        decision = validate_sizing_decision(outcomes=outcomes, decision="split")
        self.assertEqual(decision, "split")

    def test_m02_merge_with_concrete_atomicity_is_honest_not_silent(self) -> None:
        outcomes = _m02_mega_outcomes()
        record = validate_sizing_audit(
            _audit(
                card_id="M02-T01",
                decision="single",
                outcomes=outcomes,
                rebuttal_class="atomicity",
                rebuttal="Concrete atomic cutover migrates contracts, resolution and readback jointly.",
            ),
            "task_board.sizing_audits[0]",
        )
        self.assertEqual(record["card_id"], "M02-T01")


class SizingBoardBindingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workstream = read_toml(VALID / "WORKSTREAM.toml")

    def test_active_card_without_audit_fails_closed(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board.pop("sizing_audits", None)
        with self.assertRaisesRegex(ValidationError, "missing durable sizing audit"):
            validate_board(board, self.workstream)

    def test_done_only_board_without_audits_remains_valid(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["cards"] = [card for card in board["cards"] if card["status"] == "done"]
        board.pop("sizing_audits", None)
        board.pop("topology_audits", None)
        validate_board(board, self.workstream)
        self.assertEqual([card["id"] for card in board["cards"]], ["M01-T01"])

    def test_planned_and_ready_cards_require_audits(self) -> None:
        for status in ("planned", "ready"):
            with self.subTest(status=status):
                board = read_toml(VALID / "TASK_BOARD.toml")
                board.pop("sizing_audits", None)
                for card in board["cards"]:
                    if card["id"] == "M01-T02":
                        card["status"] = status
                with self.assertRaisesRegex(
                    ValidationError, "missing durable sizing audit for Card 'M01-T02'"
                ):
                    validate_board(board, self.workstream)
                board["sizing_audits"] = [_audit(card_id="M01-T02")]
                validate_board(board, self.workstream)

    def test_blocked_card_without_audit_validates_until_reactivated(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
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
        with self.assertRaisesRegex(ValidationError, "missing durable sizing audit"):
            validate_board(board, self.workstream)

    def test_board_accepts_a_valid_sizing_audit(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        validate_board(board, self.workstream)
        self.assertEqual(len(board["sizing_audits"]), 1)

    def test_board_rejects_mega_card_single_without_rebuttal(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["sizing_audits"] = [
            _audit(card_id="M01-T02", decision="single", outcomes=_m02_mega_outcomes())
        ]
        with self.assertRaisesRegex(ValidationError, "unknown rebuttal class"):
            validate_board(board, self.workstream)

    def test_board_rejects_micro_card_and_missing_dimensions(self) -> None:
        micro = read_toml(VALID / "TASK_BOARD.toml")
        micro["sizing_audits"] = [
            _audit(card_id="M01-T02", outcomes=[_outcome(substantial=False)])
        ]
        with self.assertRaisesRegex(ValidationError, "not substantial enough"):
            validate_board(micro, self.workstream)

        dimensions = _dimensions()
        del dimensions["reviewability"]
        omitted = read_toml(VALID / "TASK_BOARD.toml")
        omitted["sizing_audits"] = [
            _audit(card_id="M01-T02", dimensions=dimensions)
        ]
        with self.assertRaisesRegex(ValidationError, "missing durable audit"):
            validate_board(omitted, self.workstream)

    def test_sizing_audits_must_bind_existing_cards_exactly_once(self) -> None:
        unknown = read_toml(VALID / "TASK_BOARD.toml")
        unknown["sizing_audits"] = [_audit(card_id="M09-T99")]
        with self.assertRaisesRegex(ValidationError, "unknown card_id"):
            validate_board(unknown, self.workstream)

        duplicate = read_toml(VALID / "TASK_BOARD.toml")
        duplicate["sizing_audits"] = [
            _audit(card_id="M01-T02"),
            _audit(card_id="M01-T02"),
        ]
        with self.assertRaisesRegex(ValidationError, "duplicate sizing audit"):
            validate_board(duplicate, self.workstream)

        malformed = read_toml(VALID / "TASK_BOARD.toml")
        malformed["sizing_audits"] = {"card_id": "M01-T02"}
        with self.assertRaisesRegex(ValidationError, "must be an array"):
            validate_board(malformed, self.workstream)

    def test_sizing_and_seam_surfaces_compose_on_one_board(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["sizing_audits"] = [_audit(card_id="M01-T02")]
        board["seam_decisions"] = [
            {"seam_id": "BOOT-A", "decision": "preserved"},
        ]
        validate_board(
            board,
            self.workstream,
            planning_seams=[
                {"id": "BOOT-A", "class": "required_seam",
                 "intent": "Review closure stays standalone."},
            ],
        )

    def test_done_card_without_audit_coexists_with_audited_active(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        validate_board(board, self.workstream)
        self.assertEqual(len(board["cards"]), 2)
        audited = {audit["card_id"] for audit in board["sizing_audits"]}
        self.assertEqual(audited, {"M01-T02"})


class SplitTopologyBoardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workstream = read_toml(VALID / "WORKSTREAM.toml")

    def test_lone_card_split_without_allocation_is_rejected(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["sizing_audits"] = [
            _audit(
                card_id="M01-T02",
                decision="split",
                outcomes=[_outcome("first"), _outcome("second")],
            )
        ]
        with self.assertRaisesRegex(ValidationError, "without durable allocation"):
            validate_board(board, self.workstream)

    def test_split_allocating_everything_to_self_is_rejected(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["sizing_audits"] = [
            _audit(
                card_id="M01-T02",
                decision="split",
                outcomes=_split_outcomes("card:M01-T02", "card:M01-T02"),
            )
        ]
        with self.assertRaisesRegex(ValidationError, "one destination"):
            validate_board(board, self.workstream)

    def test_split_to_unknown_card_is_rejected(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["sizing_audits"] = [
            _audit(
                card_id="M01-T02",
                decision="split",
                outcomes=_split_outcomes("card:M01-T02", "card:M09-T99"),
            )
        ]
        with self.assertRaisesRegex(ValidationError, "unknown Card 'M09-T99'"):
            validate_board(board, self.workstream)

    def test_split_to_done_card_is_rejected(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["sizing_audits"] = [
            _audit(
                card_id="M01-T02",
                decision="split",
                outcomes=_split_outcomes("card:M01-T02", "card:M01-T01"),
            )
        ]
        with self.assertRaisesRegex(ValidationError, "terminal DONE Card 'M01-T01'"):
            validate_board(board, self.workstream)

    def test_split_to_blocked_card_is_rejected(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        _add_card(board, "M01-T03", "blocked")
        board["sizing_audits"] = [
            _audit(
                card_id="M01-T02",
                decision="split",
                outcomes=_split_outcomes("card:M01-T02", "card:M01-T03"),
            )
        ]
        with self.assertRaisesRegex(ValidationError, "names blocked Card 'M01-T03'"):
            validate_board(board, self.workstream)

    def test_split_to_unknown_trigger_is_rejected(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["sizing_audits"] = [
            _audit(
                card_id="M01-T02",
                decision="split",
                outcomes=_split_outcomes("card:M01-T02", "jit:after-M01-T02"),
            )
        ]
        with self.assertRaisesRegex(ValidationError, "unknown JIT trigger 'after-M01-T02'"):
            validate_board(board, self.workstream)

    def test_split_to_consumed_trigger_is_rejected(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        _add_trigger(board, "after-M01-T01", "M01-T01", "consumed")
        board["sizing_audits"] = [
            _audit(
                card_id="M01-T02",
                decision="split",
                outcomes=_split_outcomes("card:M01-T02", "jit:after-M01-T01"),
            )
        ]
        with self.assertRaisesRegex(ValidationError, "consumed JIT trigger 'after-M01-T01'"):
            validate_board(board, self.workstream)

    def test_split_to_sibling_card_is_valid(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        _add_card(board, "M01-T03", "planned")
        board["sizing_audits"] = [
            _audit(
                card_id="M01-T02",
                decision="split",
                outcomes=_split_outcomes("card:M01-T02", "card:M01-T03"),
            ),
            _audit(card_id="M01-T03"),
        ]
        board["topology_audits"].append({
            "card_id": "M01-T03",
            "risk": "simple",
            "triggers": [],
            "risk_basis": "Single coherent outcome in one invariant family; no seam merge or deviation.",
            "review_scope": "card_local",
            "atomicity_rationale_class": "",
            "atomicity_rationale": "",
        })
        validate_board(board, self.workstream)

    def test_split_to_waiting_trigger_is_valid(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        _add_trigger(board, "after-M01-T02", "M01-T02", "waiting")
        board["sizing_audits"] = [
            _audit(
                card_id="M01-T02",
                decision="split",
                outcomes=_split_outcomes("card:M01-T02", "jit:after-M01-T02"),
            )
        ]
        validate_board(board, self.workstream)

    def test_split_to_foreign_predecessor_trigger_is_rejected(self) -> None:
        for state in ("waiting", "satisfied"):
            with self.subTest(state=state):
                board = read_toml(VALID / "TASK_BOARD.toml")
                _add_trigger(board, "after-M01-T01", "M01-T01", state)
                board["sizing_audits"] = [
                    _audit(
                        card_id="M01-T02",
                        decision="split",
                        outcomes=_split_outcomes("card:M01-T02", "jit:after-M01-T01"),
                    )
                ]
                with self.assertRaisesRegex(
                    ValidationError,
                    "bounded after Card 'M01-T01', not the audited Card 'M01-T02'",
                ):
                    validate_board(board, self.workstream)

    def test_split_allocating_everything_away_is_rejected(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        _add_trigger(board, "after-M01-T02a", "M01-T02", "waiting")
        _add_trigger(board, "after-M01-T02b", "M01-T02", "waiting")
        board["sizing_audits"] = [
            _audit(
                card_id="M01-T02",
                decision="split",
                outcomes=_split_outcomes("jit:after-M01-T02a", "jit:after-M01-T02b"),
            )
        ]
        with self.assertRaisesRegex(
            ValidationError, "must retain at least one outcome in the audited Card"
        ):
            validate_board(board, self.workstream)

    def test_split_to_sibling_and_trigger_without_self_is_rejected(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        _add_card(board, "M01-T03", "planned")
        _add_trigger(board, "after-M01-T02", "M01-T02", "waiting")
        board["sizing_audits"] = [
            _audit(
                card_id="M01-T02",
                decision="split",
                outcomes=_split_outcomes("card:M01-T03", "jit:after-M01-T02"),
            ),
            _audit(card_id="M01-T03"),
        ]
        with self.assertRaisesRegex(
            ValidationError, "must retain at least one outcome in the audited Card"
        ):
            validate_board(board, self.workstream)

    def test_single_audit_with_allocation_is_rejected_at_board(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["sizing_audits"] = [
            _audit(
                card_id="M01-T02",
                decision="single",
                outcomes=[_outcome(allocated_to="card:M01-T02")],
            )
        ]
        with self.assertRaisesRegex(ValidationError, "must not claim split allocation"):
            validate_board(board, self.workstream)


class SizingRouterPathTests(unittest.TestCase):
    def copy_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(ROUTER_FIXTURE, project)
        return temp, project

    def install_audit(self, project: Path, audit: str) -> None:
        board = project / ROUTER_BOARD
        board.write_text(board.read_text() + audit)

    def strip_fixture_audit(self, project: Path) -> None:
        board = project / ROUTER_BOARD
        text = board.read_text()
        self.assertIn("# sizing audit for M01-T04", text)
        board.write_text(text.split("# sizing audit for M01-T04")[0])

    def valid_audit_toml(self) -> str:
        dimensions = "".join(
            f"{name} = \"Durable {name.replace('_', ' ')} statement for M01-T04.\"\n"
            for name in AUDIT_DIMENSIONS
        )
        return (
            "[[sizing_audits]]\n"
            "card_id = \"M01-T04\"\n"
            "decision = \"single\"\n"
            "rebuttal_class = \"\"\n"
            "rebuttal = \"\"\n"
            "[[sizing_audits.outcomes]]\n"
            "id = \"router-precedence\"\n"
            "kind = \"invariant\"\n"
            "statement = \"Approved-plan board precedence with durable fixtures.\"\n"
            "family = \"routing\"\n"
            "independently_verifiable = true\n"
            "independently_useful = true\n"
            "falsifiable = true\n"
            "substantial = true\n"
            "scaffolding_only = false\n"
            "independently_consumed = false\n"
            "[sizing_audits.dimensions]\n"
            f"{dimensions}"
        )

    def mega_audit_toml(self) -> str:
        outcomes = ""
        for outcome in _m02_mega_outcomes():
            outcomes += (
                "[[sizing_audits.outcomes]]\n"
                f"id = \"{outcome['id']}\"\n"
                f"kind = \"{outcome['kind']}\"\n"
                f"statement = \"{outcome['statement']}\"\n"
                f"family = \"{outcome['family']}\"\n"
                "independently_verifiable = true\n"
                "independently_useful = true\n"
                "falsifiable = true\n"
                "substantial = true\n"
                "scaffolding_only = false\n"
                "independently_consumed = false\n"
            )
        dimensions = "".join(
            f"{name} = \"Durable {name.replace('_', ' ')} statement for M01-T04.\"\n"
            for name in AUDIT_DIMENSIONS
        )
        return (
            "[[sizing_audits]]\n"
            "card_id = \"M01-T04\"\n"
            "decision = \"single\"\n"
            "rebuttal_class = \"\"\n"
            "rebuttal = \"\"\n"
            f"{outcomes}"
            "[sizing_audits.dimensions]\n"
            f"{dimensions}"
        )

    def split_audit_toml(self, first_dest: str | None,
                         second_dest: str | None) -> str:
        def outcome_toml(oid: str, kind: str, statement: str, family: str,
                         dest: str | None) -> str:
            text = (
                "[[sizing_audits.outcomes]]\n"
                f"id = \"{oid}\"\n"
                f"kind = \"{kind}\"\n"
                f"statement = \"{statement}\"\n"
                f"family = \"{family}\"\n"
                "independently_verifiable = true\n"
                "independently_useful = true\n"
                "falsifiable = true\n"
                "substantial = true\n"
                "scaffolding_only = false\n"
                "independently_consumed = false\n"
            )
            if dest is not None:
                text += f"allocated_to = \"{dest}\"\n"
            return text

        dimensions = "".join(
            f"{name} = \"Durable {name.replace('_', ' ')} statement for M01-T04.\"\n"
            for name in AUDIT_DIMENSIONS
        )
        return (
            "[[sizing_audits]]\n"
            "card_id = \"M01-T04\"\n"
            "decision = \"split\"\n"
            "rebuttal_class = \"\"\n"
            "rebuttal = \"\"\n"
            + outcome_toml("o1", "invariant", "First separable invariant.",
                           "routing", first_dest)
            + outcome_toml("o2", "acceptance", "Second separable acceptance.",
                           "recovery", second_dest)
            + "[sizing_audits.dimensions]\n"
            f"{dimensions}"
        )

    def test_router_accepts_valid_sizing_audit_on_real_board(self) -> None:
        temp, project = self.copy_fixture()
        try:
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution", "M01-T04"),
            )
        finally:
            temp.cleanup()

    def test_router_recovers_on_missing_audit_for_active_card(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.strip_fixture_audit(project)
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("missing durable sizing audit for Card 'M01-T04'", routed.reason)
        finally:
            temp.cleanup()

    def test_router_recovers_on_mega_card_single_without_rebuttal(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.strip_fixture_audit(project)
            self.install_audit(project, self.mega_audit_toml())
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("rebuttal", routed.reason)
        finally:
            temp.cleanup()

    def test_router_recovers_on_omitted_audit_dimension(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.strip_fixture_audit(project)
            audit = self.valid_audit_toml().replace(
                "reviewability = \"Durable reviewability statement for M01-T04.\"\n", ""
            )
            self.install_audit(project, audit)
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("missing durable audit", routed.reason)
        finally:
            temp.cleanup()

    def test_router_recovers_on_lone_card_split_without_allocation(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.strip_fixture_audit(project)
            self.install_audit(project, self.split_audit_toml(None, None))
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("without durable allocation", routed.reason)
        finally:
            temp.cleanup()

    def test_router_recovers_on_split_allocating_everything_to_self(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.strip_fixture_audit(project)
            self.install_audit(
                project, self.split_audit_toml("card:M01-T04", "card:M01-T04")
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("one destination", routed.reason)
        finally:
            temp.cleanup()

    def test_router_recovers_on_split_to_dangling_destination(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.strip_fixture_audit(project)
            self.install_audit(
                project, self.split_audit_toml("card:M01-T04", "card:M09-T99")
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("unknown Card 'M09-T99'", routed.reason)
        finally:
            temp.cleanup()

    def test_router_split_to_waiting_trigger_routes_to_execution(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.strip_fixture_audit(project)
            self.install_audit(
                project,
                self.split_audit_toml("card:M01-T04", "jit:after-M01-T04"),
            )
            self.install_audit(
                project,
                "[[jit_triggers]]\n"
                "id = \"after-M01-T04\"\n"
                "after_card = \"M01-T04\"\n"
                "state = \"waiting\"\n"
                "condition = \"Downstream boundary holds the second separable outcome.\"\n",
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution", "M01-T04"),
            )
        finally:
            temp.cleanup()

    def test_router_blocked_card_without_audit_routes_to_blocked_owner(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.strip_fixture_audit(project)
            board = project / ROUTER_BOARD
            text = board.read_text().replace('status = "in_progress"', 'status = "blocked"')
            text += (
                "[cards.blocker]\n"
                "class = \"blocker\"\n"
                "path = \"implementation/workstreams/sample-workstream/blockers/M01-T04.toml\"\n"
            )
            board.write_text(text)
            blocker_dir = project / "implementation/workstreams/sample-workstream/blockers"
            blocker_dir.mkdir()
            (blocker_dir / "M01-T04.toml").write_text(
                "workstream_id = \"sample-workstream\"\n"
                "card_id = \"M01-T04\"\n"
                "class = \"missing_evidence\"\n"
                "summary = \"Prior-art measurement is missing for the exact repair subject.\"\n"
            )
            routed = select_route(project, [ROUTER_MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "research_handoff", "M01-T04"),
            )
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
