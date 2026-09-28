from __future__ import annotations

import copy
import hashlib
import unittest
from pathlib import Path

from tools.card_sizing_contract import (
    CardSizingError,
    required_decision,
    separable_outcomes,
    validate_sizing_audit,
    validate_sizing_decision,
)
from tools.historical_replay_contract import (
    CORPUS,
    EXCERPTS,
    M02_ACCEPTANCE_REQS,
    M02_CONVERGENCE_REPLAY,
    M02_DEFECT_CLASSES,
    M02_DEFECT_CLASS_IDS,
    M02_MEGA_OUTCOME_IDS,
    NON_TERMINAL_M02_ATTEMPTS,
    SOURCES,
    SOURCE_COMMIT,
    SOURCE_REPOSITORY,
    TERMINAL_M02,
    HistoricalReplayError,
    assert_terminal_m02_preserved,
    class_level_closure_scope,
    corpus_entry,
    first_blocker_stop_discovery,
    literal_only_closure_scope,
    mega_sizing_outcomes,
    provenance_record,
    r02_style_partial_discovery,
    r09_style_exhaustive_discovery,
    terminal_m02_record,
    validate_corpus,
    validate_corpus_entry,
    validate_source_provenance,
)
from tools.policy_kernel import PolicyKernel
from tools.review_contract import (
    REVIEW_SCOPE_DISCOVERY_CEILINGS,
    ReviewContractError,
    remaining_closure_findings,
    required_closure_scope,
    review_convergence_state,
    validate_closure_surface,
    validate_discovery_surface,
)
from tools.state_contract import (
    ValidationError,
    read_toml,
    validate_board,
    validate_review,
    validate_review_history,
)
from tools.topology_contract import compute_proposal_digest

ROOT = Path(__file__).resolve().parents[1]
VALID = ROOT / "tests" / "fixtures" / "state" / "valid"
REGISTRY = ROOT / "policy" / "mechanical_policy.json"


def _severity(*finding_ids: str) -> list[dict[str, str]]:
    return [
        {"id": finding_id, "surface": "correctness", "evidence": f"evidence/review-R01.md#{finding_id}"}
        for finding_id in finding_ids
    ]


def _discovery_attempt(
    attempt_id: str,
    verdict: str,
    findings: list[str],
    classes: list[str],
    blob_char: str,
    *,
    post: bool = False,
    basis: str = "",
) -> dict:
    attempt = read_toml(VALID / "REVIEW_ATTEMPT.toml")
    attempt.update({
        "attempt": attempt_id,
        "verdict": verdict,
        "review_kind": "discovery",
        "source_discovery_attempt": "",
        "discovery_complete": True,
        "material_finding_ids": findings,
        "review_scope": "card",
        "review_epoch": "E01",
        "epoch_reset_basis": "",
        "material_defect_class_ids": classes,
        "post_convergence_validation": post,
        "convergence_basis": basis,
    })
    if verdict == "red":
        attempt["finding_severity"] = _severity(*findings)
    attempt["subject"]["blob"] = blob_char * 40
    return attempt


def _closure_attempt(
    attempt_id: str,
    source_id: str,
    findings: list[str],
    classes: list[str],
    blob_char: str,
) -> dict:
    attempt = read_toml(VALID / "REVIEW_ATTEMPT.toml")
    attempt.update({
        "attempt": attempt_id,
        "verdict": "green",
        "review_kind": "closure_verification",
        "source_discovery_attempt": source_id,
        "discovery_complete": False,
        "material_finding_ids": findings,
        "review_scope": "card",
        "review_epoch": "E01",
        "epoch_reset_basis": "",
        "material_defect_class_ids": classes,
        "post_convergence_validation": False,
        "convergence_basis": "",
    })
    attempt["subject"]["blob"] = blob_char * 40
    return attempt


def _five_epoch_history() -> list[dict]:
    """Five RED discoveries with closures, one new corpus class per epoch."""
    attempts: list[dict] = []
    blobs = "456789abcd"
    for index, record in enumerate(M02_DEFECT_CLASSES[:5]):
        epoch = f"R{index + 1:02d}"
        finding = f"F{index + 1}"
        attempts.append(
            _discovery_attempt(epoch, "red", [finding], [record["id"]], blobs[2 * index])
        )
        attempts.append(
            _closure_attempt(f"C{index + 1:02d}", epoch, [finding], [record["id"]], blobs[2 * index + 1])
        )
    return attempts


def _dimensions(**overrides) -> dict:
    record = {
        "independent_implementability": "Each surface builds and passes alone against its own fixtures.",
        "falsifiability_testability": "Each surface owns an observable failing check before GREEN.",
        "reviewability": "Each surface fits one bounded Card review without integration scope.",
        "invariant_contract_family": "Surfaces span distinct invariant families with named bindings.",
        "dependency_ordering": "No surface depends on another result; any order launches safely.",
        "atomic_mutation_migration": "No atomic mutation or migration forces joint landing.",
        "cross_surface_coupling": "No shared mutable surface couples the outcomes materially.",
    }
    record.update(overrides)
    return record


def _board_outcomes() -> list[dict]:
    """Corpus mega outcomes without the replay-level provenance envelope."""
    return [
        {key: value for key, value in outcome.items() if key != "provenance"}
        for outcome in mega_sizing_outcomes()
    ]


def _sizing_audit(card_id: str = "M01-T02", **overrides) -> dict:
    record = {
        "card_id": card_id,
        "decision": "single",
        "rebuttal_class": "",
        "rebuttal": "",
        "outcomes": _board_outcomes(),
        "dimensions": _dimensions(),
    }
    record.update(overrides)
    return record


def _challenge(**overrides) -> dict:
    record = {
        "verdict": "green",
        "evaluated": ["boundary_fidelity", "falsifiability", "review_separation"],
        "scope_statement": "Whole-milestone boundary checked against seam intent and sizing outcomes.",
        "independent": True,
        "independence_basis": "Challenger did not author the Execution Prep topology proposal.",
        "fresh": True,
        "challenge_basis": "Fresh review of the current proposed boundary.",
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
        "risk_basis": "Single coherent outcome in one invariant family.",
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


def _bind_proposal(board: dict, card_id: str) -> None:
    sizing = next(audit for audit in board["sizing_audits"] if audit["card_id"] == card_id)
    audit = next(audit for audit in board["topology_audits"] if audit["card_id"] == card_id)
    audit["challenge"]["proposal_digest"] = compute_proposal_digest(
        card_id=card_id,
        sizing_audit=sizing,
        topology_audit=audit,
        seam_decisions=board.get("seam_decisions"),
        planning_seams=None,
    )


class ProvenanceTests(unittest.TestCase):
    def test_every_pinned_source_validates(self) -> None:
        self.assertEqual(len(SOURCES), 13)
        for source_key in SOURCES:
            with self.subTest(source=source_key):
                record = validate_source_provenance(
                    provenance_record(source_key), f"corpus.{source_key}"
                )
                self.assertEqual(record["repository"], SOURCE_REPOSITORY)
                self.assertEqual(record["commit"], SOURCE_COMMIT)

    def test_substituted_provenance_is_rejected(self) -> None:
        base = provenance_record("m02-card")
        mutations = {
            "repository": "other/project",
            "commit": "f" * 40,
            "blob": "f" * 40,
            "bytes": base["bytes"] + 1,
            "sha256": "f" * 64,
        }
        for field, value in mutations.items():
            with self.subTest(field=field):
                candidate = dict(base)
                candidate[field] = value
                with self.assertRaises(HistoricalReplayError):
                    validate_source_provenance(candidate, "corpus.m02-card")

    def test_unknown_source_path_is_rejected(self) -> None:
        candidate = provenance_record("m02-card")
        candidate["path"] = "implementation/workstreams/other/cards/M02-T01.md"
        with self.assertRaisesRegex(HistoricalReplayError, "unknown corpus source path"):
            validate_source_provenance(candidate, "corpus.unknown")

    def test_malformed_blob_is_rejected(self) -> None:
        candidate = provenance_record("m02-card")
        candidate["blob"] = "not-a-blob"
        with self.assertRaisesRegex(HistoricalReplayError, "blob must be exact 40-hex"):
            validate_source_provenance(candidate, "corpus.m02-card")

    def test_unknown_source_key_is_rejected(self) -> None:
        with self.assertRaisesRegex(HistoricalReplayError, "unknown corpus source"):
            provenance_record("invented-source")

    def test_full_corpus_validates(self) -> None:
        records = validate_corpus(CORPUS)
        self.assertEqual(len(records), 5)
        self.assertEqual(
            {record["failure_class"] for record in records},
            {
                "oversized-card-topology",
                "incomplete-discovery",
                "literal-only-repair",
                "convergence-misuse",
                "terminal-preservation",
            },
        )
        for record in records:
            entry = corpus_entry(record["id"])
            self.assertEqual(entry["id"], record["id"])

    def test_excerpt_digests_are_self_consistent(self) -> None:
        for excerpt_id, pinned in EXCERPTS.items():
            with self.subTest(excerpt=excerpt_id):
                digest = hashlib.sha256(pinned["text"].encode("utf-8")).hexdigest()
                self.assertEqual(digest, pinned["sha256"])

    def test_tampered_excerpt_text_is_rejected(self) -> None:
        entry = copy.deepcopy(corpus_entry("m02-mega-topology"))
        entry["excerpts"][0]["text"] += " (paraphrased)"
        with self.assertRaisesRegex(HistoricalReplayError, "does not match pinned verbatim text"):
            validate_corpus_entry(entry, "corpus.m02-mega-topology")

    def test_excerpt_outside_entry_sources_is_rejected(self) -> None:
        entry = copy.deepcopy(corpus_entry("m02-terminal-preservation"))
        entry["excerpts"] = [{"id": "r09-full-pass", "text": EXCERPTS["r09-full-pass"]["text"]}]
        with self.assertRaisesRegex(HistoricalReplayError, "not drawn from an entry source"):
            validate_corpus_entry(entry, "corpus.m02-terminal-preservation")

    def test_unknown_excerpt_is_rejected(self) -> None:
        entry = copy.deepcopy(corpus_entry("m02-mega-topology"))
        entry["excerpts"] = [{"id": "invented-anecdote", "text": "a plausible story"}]
        with self.assertRaisesRegex(HistoricalReplayError, "unknown corpus excerpt"):
            validate_corpus_entry(entry, "corpus.m02-mega-topology")

    def test_duplicate_corpus_ids_are_rejected(self) -> None:
        entry = corpus_entry("m02-mega-topology")
        with self.assertRaisesRegex(HistoricalReplayError, "duplicate corpus entry id"):
            validate_corpus([entry, copy.deepcopy(entry)])

    def test_corpus_entry_must_not_carry_a_verdict(self) -> None:
        entry = copy.deepcopy(corpus_entry("m02-convergence-misuse"))
        entry["verdict"] = "green"
        with self.assertRaisesRegex(HistoricalReplayError, "must not carry a review verdict"):
            validate_corpus_entry(entry, "corpus.m02-convergence-misuse")

    def test_replay_must_derive_canonical_surfaces(self) -> None:
        entry = copy.deepcopy(corpus_entry("m02-mega-topology"))
        entry["replay"] = {"sizing_outcome_ids": ("invented-surface",)}
        with self.assertRaisesRegex(HistoricalReplayError, "exactly the four P2-permitted"):
            validate_corpus_entry(entry, "corpus.m02-mega-topology")

    def test_replay_must_derive_known_defect_classes(self) -> None:
        entry = copy.deepcopy(corpus_entry("m02-literal-class-repair"))
        entry["replay"] = {"defect_classes": ("invented-class",)}
        with self.assertRaisesRegex(HistoricalReplayError, "unknown defect classes"):
            validate_corpus_entry(entry, "corpus.m02-literal-class-repair")

    def test_defect_classes_derive_from_pinned_review_evidence(self) -> None:
        self.assertEqual(len(M02_DEFECT_CLASSES), 7)
        self.assertEqual(len(M02_DEFECT_CLASS_IDS), 7)
        for record in M02_DEFECT_CLASSES:
            with self.subTest(defn=record["id"]):
                self.assertIn(record["source"], SOURCES)
                self.assertTrue(record["finding_title"])
                self.assertTrue(record["finding"])


class MegaCardReplayTests(unittest.TestCase):
    def test_mega_outcomes_bind_corpus_provenance(self) -> None:
        outcomes = mega_sizing_outcomes()
        self.assertEqual([outcome["id"] for outcome in outcomes], list(M02_MEGA_OUTCOME_IDS))
        families = {outcome["family"] for outcome in outcomes}
        self.assertEqual(len(families), 4)
        for outcome in outcomes:
            with self.subTest(outcome=outcome["id"]):
                self.assertEqual(outcome["provenance"]["corpus_entry"], "m02-mega-topology")
                self.assertEqual(
                    set(outcome["provenance"]["sources"]),
                    {"m02-card", "p2-plan", "m02-convergence"},
                )

    def test_historical_mega_topology_requires_split(self) -> None:
        outcomes = mega_sizing_outcomes()
        self.assertEqual(len(separable_outcomes(outcomes)), 4)
        self.assertEqual(required_decision(outcomes), "split")
        with self.assertRaisesRegex(CardSizingError, "unknown rebuttal class"):
            validate_sizing_decision(outcomes=outcomes, decision="single")
        with self.assertRaisesRegex(CardSizingError, "cannot rebut the split"):
            validate_sizing_decision(
                outcomes=outcomes,
                decision="single",
                rebuttal_class="same_milestone",
                rebuttal="The complete M02 milestone belongs in one Card.",
            )

    def test_valid_atomicity_rebuttal_is_honest_not_silent(self) -> None:
        record = validate_sizing_audit(
            _sizing_audit(
                card_id="M02-T01",
                decision="single",
                rebuttal_class="atomicity",
                rebuttal="Concrete atomic cutover migrates contracts, resolution and readback jointly.",
            ),
            "task_board.sizing_audits[0]",
        )
        self.assertEqual(record["decision"], "single")

    def test_valid_p2_split_allocation_passes(self) -> None:
        outcomes = _board_outcomes()
        destinations = (
            "card:M02-T01",
            "card:M02-T02",
            "jit:after-M02-T01",
            "jit:after-M02-T02",
        )
        for outcome, destination in zip(outcomes, destinations):
            outcome["allocated_to"] = destination
        decision = validate_sizing_decision(outcomes=outcomes, decision="split")
        self.assertEqual(decision, "split")

    def test_board_rejects_mega_single_without_rebuttal(self) -> None:
        workstream = read_toml(VALID / "WORKSTREAM.toml")
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["sizing_audits"] = [_sizing_audit(card_id="M01-T02")]
        with self.assertRaisesRegex(ValidationError, "unknown rebuttal class"):
            validate_board(board, workstream)


class TopologyReplayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workstream = read_toml(VALID / "WORKSTREAM.toml")

    def test_mega_topology_cannot_launch_simple(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        for card in board["cards"]:
            if card["id"] == "M01-T02":
                card["status"] = "ready"
        board["sizing_audits"] = [
            _sizing_audit(
                card_id="M01-T02",
                decision="single",
                rebuttal_class="atomicity",
                rebuttal="Concrete atomic cutover migrates contracts, resolution and readback jointly.",
            )
        ]
        board["topology_audits"] = [_simple_audit(card_id="M01-T02")]
        with self.assertRaisesRegex(ValidationError, "multiple_invariant_families trigger"):
            validate_board(board, self.workstream)

    def test_mega_topology_with_green_challenge_is_honest(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        for card in board["cards"]:
            if card["id"] == "M01-T02":
                card["status"] = "planned"
        board["sizing_audits"] = [
            _sizing_audit(
                card_id="M01-T02",
                decision="single",
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

    def test_terminal_done_state_needs_no_topology_challenge(self) -> None:
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["cards"] = [card for card in board["cards"] if card["status"] == "done"]
        board.pop("topology_audits", None)
        board.pop("sizing_audits", None)
        validate_board(board, self.workstream)
        self.assertEqual([card["id"] for card in board["cards"]], ["M01-T01"])


class IncompleteDiscoveryReplayTests(unittest.TestCase):
    def test_replay_binds_full_m02_acceptance(self) -> None:
        self.assertEqual(len(M02_ACCEPTANCE_REQS), 16)
        self.assertEqual(M02_ACCEPTANCE_REQS[0], "PWV21-REQ-018")
        self.assertEqual(M02_ACCEPTANCE_REQS[-1], "PWV21-REQ-033")

    def test_partial_r02_style_discovery_is_rejected(self) -> None:
        case = r02_style_partial_discovery()
        self.assertEqual(case["corpus_entry"], "m02-incomplete-discovery")
        with self.assertRaisesRegex(ReviewContractError, "omitted applicable acceptance"):
            validate_discovery_surface(
                applicable_acceptance=case["applicable_acceptance"],
                evaluated_acceptance=case["evaluated_acceptance"],
                stopped_at_first_blocker=case["stopped_at_first_blocker"],
            )

    def test_first_blocker_stop_is_rejected(self) -> None:
        case = first_blocker_stop_discovery()
        with self.assertRaisesRegex(ReviewContractError, "first blocker"):
            validate_discovery_surface(
                applicable_acceptance=case["applicable_acceptance"],
                evaluated_acceptance=case["evaluated_acceptance"],
                stopped_at_first_blocker=case["stopped_at_first_blocker"],
            )

    def test_green_discovery_retaining_findings_is_rejected(self) -> None:
        attempt = read_toml(VALID / "REVIEW_ATTEMPT.toml")
        attempt.update({
            "review_kind": "discovery",
            "source_discovery_attempt": "",
            "discovery_complete": True,
            "material_finding_ids": ["F1"],
            "verdict": "green",
        })
        with self.assertRaisesRegex(
            ValidationError, "cannot retain material blocking findings"
        ):
            validate_review(attempt)

    def test_exhaustive_r09_style_discovery_passes(self) -> None:
        case = r09_style_exhaustive_discovery()
        evaluated = validate_discovery_surface(
            applicable_acceptance=case["applicable_acceptance"],
            evaluated_acceptance=case["evaluated_acceptance"],
            stopped_at_first_blocker=case["stopped_at_first_blocker"],
        )
        self.assertEqual(evaluated, frozenset(M02_ACCEPTANCE_REQS))

    def test_complete_red_discovery_with_findings_passes(self) -> None:
        attempt = read_toml(VALID / "REVIEW_ATTEMPT.toml")
        attempt.update({
            "review_kind": "discovery",
            "source_discovery_attempt": "",
            "discovery_complete": True,
            "material_finding_ids": ["R09-F01", "R09-F02", "R09-F03", "R09-F04"],
            "finding_severity": _severity("R09-F01", "R09-F02", "R09-F03", "R09-F04"),
            "verdict": "red",
        })
        validate_review(attempt)


class LiteralRepairReplayTests(unittest.TestCase):
    def test_literal_only_repair_without_class_is_rejected(self) -> None:
        scope = literal_only_closure_scope()
        self.assertEqual(scope["corpus_entry"], "m02-literal-class-repair")
        with self.assertRaisesRegex(ReviewContractError, "defect_classes.*must not be empty"):
            required_closure_scope(scope)

    def test_repair_without_root_cause_is_rejected(self) -> None:
        scope = dict(literal_only_closure_scope())
        scope["defect_classes"] = ["r09-f01-caller-projection-derivation"]
        with self.assertRaisesRegex(ReviewContractError, "root_cause_evidence.*must not be empty"):
            required_closure_scope(scope)

    def test_closure_with_omitted_causal_category_is_rejected(self) -> None:
        scope = dict(class_level_closure_scope())
        scope.pop("negative_space")
        with self.assertRaisesRegex(ReviewContractError, "omitted causal categories"):
            required_closure_scope(scope)

    def test_class_level_repair_passes_with_full_surface(self) -> None:
        scope = class_level_closure_scope()
        required = required_closure_scope(scope)
        self.assertIn("r09-f01-caller-projection-derivation", required)
        self.assertIn("sibling-rule-input-shape", required)
        self.assertIn("downstream-obligation-consumer", required)
        validate_closure_surface(scope=scope, evaluated_surface=required)
        with self.assertRaisesRegex(ReviewContractError, "omitted materially implicated surface"):
            validate_closure_surface(
                scope=scope,
                evaluated_surface=required - {"downstream-obligation-consumer"},
            )

    def test_closure_accounting_tracks_remaining_source_findings(self) -> None:
        attempts = [
            {
                "attempt": "R09",
                "verdict": "red",
                "review_kind": "discovery",
                "material_finding_ids": ["R09-F01", "R09-F02", "R09-F03", "R09-F04"],
            },
            {
                "attempt": "R09-C1",
                "verdict": "green",
                "review_kind": "closure_verification",
                "source_discovery_attempt": "R09",
                "material_finding_ids": ["R09-F01", "R09-F02"],
            },
        ]
        self.assertEqual(
            remaining_closure_findings(attempts, "R09"),
            frozenset({"R09-F03", "R09-F04"}),
        )
        attempts.append({
            "attempt": "R09-C2",
            "verdict": "green",
            "review_kind": "closure_verification",
            "source_discovery_attempt": "R09",
            "material_finding_ids": ["R09-F03", "R09-F04"],
        })
        self.assertEqual(remaining_closure_findings(attempts, "R09"), frozenset())


class ConvergenceReplayTests(unittest.TestCase):
    def test_replay_ceiling_matches_corrected_card_ceiling(self) -> None:
        self.assertEqual(
            M02_CONVERGENCE_REPLAY["discovery_ceiling"],
            REVIEW_SCOPE_DISCOVERY_CEILINGS[M02_CONVERGENCE_REPLAY["review_scope"]],
        )
        self.assertEqual(M02_CONVERGENCE_REPLAY["discovery_ceiling"], 5)
        self.assertEqual(len(M02_CONVERGENCE_REPLAY["fresh_epochs"]), 5)

    def test_five_fresh_epochs_require_convergence(self) -> None:
        attempts = []
        for index, record in enumerate(M02_DEFECT_CLASSES[:5]):
            attempts.append({
                "attempt": f"R{index + 1:02d}",
                "verdict": "red",
                "review_kind": "discovery",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": [record["id"]],
                "post_convergence_validation": False,
            })
        state = review_convergence_state(attempts)
        self.assertEqual(state.discovery_epochs, 5)
        self.assertEqual(state.discovery_ceiling, 5)
        self.assertTrue(state.convergence_required)
        self.assertEqual(
            state.seen_defect_classes,
            frozenset(record["id"] for record in M02_DEFECT_CLASSES[:5]),
        )

    def test_ordinary_discovery_after_threshold_is_rejected(self) -> None:
        attempts = _five_epoch_history()
        validate_review_history(attempts)
        ordinary_r12 = _discovery_attempt(
            "R12", "red", ["F6"], [M02_DEFECT_CLASSES[5]["id"]], "e"
        )
        with self.assertRaisesRegex(
            ValidationError, "not another ordinary discovery"
        ):
            validate_review_history([*attempts, ordinary_r12])

    def test_post_convergence_r12_validation_passes(self) -> None:
        attempts = _five_epoch_history()
        post = _discovery_attempt(
            "R12",
            "green",
            [],
            [],
            "e",
            post=True,
            basis="Main convergence/root-cause analysis: five fresh epochs reached the card ceiling",
        )
        validate_review_history([*attempts, post])
        state = review_convergence_state([*attempts, post])
        self.assertTrue(state.convergence_required)
        self.assertEqual(state.post_convergence_attempt, "R12")
        self.assertEqual(state.post_convergence_verdict, "green")

    def test_second_post_convergence_validation_is_rejected(self) -> None:
        attempts = _five_epoch_history()
        first = _discovery_attempt(
            "R12", "green", [], [], "e", post=True,
            basis="Main convergence/root-cause analysis",
        )
        second = _discovery_attempt(
            "R13", "green", [], [], "f", post=True,
            basis="Repeated post-convergence validation",
        )
        with self.assertRaisesRegex(ValidationError, "post-convergence"):
            validate_review_history([*attempts, first, second])

    def test_post_convergence_without_threshold_is_rejected(self) -> None:
        short = _five_epoch_history()[:2]
        validate_review_history(short)
        post = _discovery_attempt(
            "R12", "green", [], [], "e", post=True,
            basis="Premature convergence claim",
        )
        with self.assertRaisesRegex(
            ValidationError, "requires a reached convergence threshold"
        ):
            validate_review_history([*short, post])

    def test_post_convergence_requires_basis_and_ordinary_must_not_claim_it(self) -> None:
        post_without_basis = _discovery_attempt("R12", "green", [], [], "e", post=True)
        with self.assertRaisesRegex(ValidationError, "requires durable convergence_basis"):
            validate_review(post_without_basis)
        ordinary_with_basis = _discovery_attempt(
            "R06", "red", ["F6"], [M02_DEFECT_CLASSES[5]["id"]], "e",
            basis="Misused convergence claim",
        )
        with self.assertRaisesRegex(ValidationError, "must not claim convergence_basis"):
            validate_review(ordinary_with_basis)


class TerminalPreservationTests(unittest.TestCase):
    def test_exact_terminal_record_is_preserved(self) -> None:
        record = terminal_m02_record()
        preserved = assert_terminal_m02_preserved(record)
        self.assertEqual(preserved, TERMINAL_M02)
        self.assertEqual(record, TERMINAL_M02)

    def test_reopened_card_status_is_rejected(self) -> None:
        for status in ("planned", "ready", "in_progress", "blocked", "returned"):
            with self.subTest(status=status):
                record = terminal_m02_record()
                record["card_status"] = status
                with self.assertRaisesRegex(HistoricalReplayError, "reopening"):
                    assert_terminal_m02_preserved(record)

    def test_rewritten_terminal_fields_are_rejected(self) -> None:
        base = terminal_m02_record()
        for field in (
            "result_commit",
            "result_blob",
            "card_review_blob",
            "milestone_review_blob",
        ):
            with self.subTest(field=field):
                record = dict(base)
                record[field] = "0" * 40
                with self.assertRaisesRegex(HistoricalReplayError, "must not be rewritten"):
                    assert_terminal_m02_preserved(record)

    def test_flipped_terminal_verdicts_are_rejected(self) -> None:
        for field in ("card_review_verdict", "milestone_review_verdict"):
            with self.subTest(field=field):
                record = terminal_m02_record()
                record[field] = "red"
                with self.assertRaisesRegex(HistoricalReplayError, "must not be rewritten"):
                    assert_terminal_m02_preserved(record)

    def test_wrong_card_binding_is_rejected(self) -> None:
        record = terminal_m02_record()
        record["card_id"] = "M02R-T10"
        with self.assertRaisesRegex(HistoricalReplayError, "binds Card"):
            assert_terminal_m02_preserved(record)

    def test_non_terminal_red_attempts_are_not_active_authority(self) -> None:
        self.assertEqual(
            {(item["attempt"], item["verdict"]) for item in NON_TERMINAL_M02_ATTEMPTS},
            {("R01", "red"), ("M02-MILESTONE-R01", "red")},
        )
        record = terminal_m02_record()
        record["card_review_attempt"] = "R01"
        with self.assertRaisesRegex(HistoricalReplayError, "non-terminal history"):
            assert_terminal_m02_preserved(record)
        record = terminal_m02_record()
        record["milestone_review_attempt"] = "M02-MILESTONE-R01"
        with self.assertRaisesRegex(HistoricalReplayError, "non-terminal history"):
            assert_terminal_m02_preserved(record)

    def test_terminal_guard_does_not_mutate_its_input(self) -> None:
        record = terminal_m02_record()
        snapshot = dict(record)
        assert_terminal_m02_preserved(record)
        self.assertEqual(record, snapshot)

    def test_done_only_m02_board_remains_valid(self) -> None:
        workstream = read_toml(VALID / "WORKSTREAM.toml")
        board = read_toml(VALID / "TASK_BOARD.toml")
        board["cards"] = [
            {
                "id": "M02-T01",
                "status": "done",
                "contract": {
                    "class": "task_card",
                    "path": "implementation/workstreams/sample-workstream/cards/M02-T01.md",
                },
                "result": {
                    "class": "result",
                    "path": "implementation/workstreams/sample-workstream/results/M02-T01.md",
                },
            }
        ]
        board.pop("sizing_audits", None)
        board.pop("topology_audits", None)
        validate_board(board, workstream)

    def test_terminal_done_board_still_routes_to_close(self) -> None:
        kernel = PolicyKernel.from_path(REGISTRY)
        board = {"cards": [{"id": "M02-T01", "status": "done"}]}
        self.assertTrue(kernel.matches("PWV21-K012", {"board": board}))
        self.assertFalse(
            kernel.matches(
                "PWV21-K011",
                {"board": {"cards": [{"id": "M02-T01", "status": "done"}]}},
            )
        )


if __name__ == "__main__":
    unittest.main()
