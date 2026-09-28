from __future__ import annotations

import copy
import unittest

from tools.execution_contract import parse_card_result
from tools.worker_evidence_contract import (
    WorkerEvidenceError,
    classify_worker_return,
    falsification_status,
    validate_worker_evidence,
)

REPO = "elmakus/project_workflow_v2"
PRE_COMMIT = "a" * 40
POST_COMMIT = "b" * 40
OTHER_COMMIT = "c" * 40


def code_record() -> dict:
    return {
        "card_id": "M02R-T12",
        "outcome_class": "code",
        "baseline": {
            "kind": "automated_check",
            "check": "python3 -m unittest tests.test_worker_evidence_contract",
            "status": "red",
            "subject": {"repository": REPO, "commit": PRE_COMMIT},
            "evidence": "evidence/M02R-T12-baseline-red.md: 1 failing falsification check",
        },
        "implementation": {
            "subject": {"repository": REPO, "commit": POST_COMMIT},
            "summary": "add runtime-neutral falsification-first worker evidence contract",
        },
        "verification": {
            "check": "python3 -m unittest tests.test_worker_evidence_contract",
            "status": "green",
            "subject": {"repository": REPO, "commit": POST_COMMIT},
            "evidence": "evidence/M02R-T12-verification-green.md: same check GREEN",
        },
        "sequence": {"baseline": 1, "implementation": 2, "verification": 3},
        "observable_justification": None,
    }


def observable_record(outcome_class: str = "documentation") -> dict:
    record = code_record()
    record["outcome_class"] = outcome_class
    record["baseline"]["kind"] = "observable_check"
    record["baseline"]["check"] = "observe migration rehearsal report lists exact blob identities"
    record["baseline"]["evidence"] = "evidence/M02R-T12-observable-red.md: rehearsal omits blob identities"
    record["verification"]["check"] = "observe migration rehearsal report lists exact blob identities"
    record["verification"]["evidence"] = "evidence/M02R-T12-observable-green.md: rehearsal lists exact blobs"
    record["observable_justification"] = (
        "unit test is unnatural for this documentation outcome; falsifiable "
        "observation is the rehearsal report naming exact blob identities"
    )
    return record


class WorkerEvidenceContractTests(unittest.TestCase):
    def test_automated_code_baseline_red_then_green_is_valid(self) -> None:
        normalized = validate_worker_evidence(code_record())
        self.assertEqual(normalized["baseline"]["status"], "red")
        self.assertEqual(normalized["verification"]["status"], "green")
        self.assertEqual(normalized["verification"]["check"], normalized["baseline"]["check"])
        self.assertEqual(
            falsification_status(code_record(), expected_card_id="M02R-T12"),
            "falsification_first_green",
        )

    def test_observable_documentation_migration_policy_paths_are_valid(self) -> None:
        for outcome_class in ("documentation", "migration", "policy"):
            with self.subTest(outcome_class=outcome_class):
                normalized = validate_worker_evidence(observable_record(outcome_class))
                self.assertEqual(normalized["baseline"]["kind"], "observable_check")
                self.assertIsNotNone(normalized["observable_justification"])

    def test_automated_check_remains_allowed_for_documentation_without_coercion(self) -> None:
        record = code_record()
        record["outcome_class"] = "documentation"
        normalized = validate_worker_evidence(record)
        self.assertEqual(normalized["baseline"]["kind"], "automated_check")
        self.assertIsNone(normalized["observable_justification"])

    def test_missing_baseline_key_fails_closed(self) -> None:
        record = code_record()
        del record["baseline"]
        with self.assertRaisesRegex(WorkerEvidenceError, "invalid top-level keys"):
            validate_worker_evidence(record)

    def test_missing_precheck_status_is_not_a_baseline(self) -> None:
        record = code_record()
        record["baseline"]["status"] = "green"
        with self.assertRaisesRegex(WorkerEvidenceError, "baseline.status must be exactly 'red'"):
            validate_worker_evidence(record)

    def test_non_green_verification_cannot_close_falsification(self) -> None:
        record = code_record()
        record["verification"]["status"] = "red"
        with self.assertRaisesRegex(WorkerEvidenceError, "verification.status must be exactly 'green'"):
            validate_worker_evidence(record)

    def test_generic_red_and_green_claims_fail(self) -> None:
        for generic in ("red", "green", "tests fail", "works", "TBD"):
            with self.subTest(generic=generic):
                record = code_record()
                record["baseline"]["check"] = generic
                record["verification"]["check"] = generic
                with self.assertRaisesRegex(WorkerEvidenceError, "must not be a generic claim|specific falsifiable"):
                    validate_worker_evidence(record)

    def test_generic_claim_punctuation_and_spacing_variants_fail(self) -> None:
        variants = (
            "tests fail.", "tests fail!", "tests fail:", "tests fail;",
            "Tests Fail", "  tests   fail  ", "TESTS FAIL.",
            "red.", "GREEN!", "tbd.", "n/a.", "(tests fail)",
            "\"tests fail\"", "test passes.", "works!",
        )
        for variant in variants:
            with self.subTest(variant=variant):
                record = code_record()
                record["baseline"]["check"] = variant
                record["verification"]["check"] = variant
                with self.assertRaisesRegex(WorkerEvidenceError, "generic claim|specific falsifiable"):
                    validate_worker_evidence(record)

    def test_multi_dash_card_id_accepted(self) -> None:
        record = code_record()
        record["card_id"] = "CUBC-M01-T01"
        normalized = validate_worker_evidence(record)
        self.assertEqual(normalized["card_id"], "CUBC-M01-T01")
        self.assertEqual(
            falsification_status(record, expected_card_id="CUBC-M01-T01"),
            "falsification_first_green",
        )

    def test_card_id_rejects_arbitrary_identifiers(self) -> None:
        for bad_id in ("M01", "", "-T01", "M01-", "M01--T01", "M01_T01",
                       "M01 T01", "card <id>", "M01-T01!"):
            with self.subTest(card_id=bad_id):
                record = code_record()
                record["card_id"] = bad_id
                with self.assertRaisesRegex(WorkerEvidenceError, "concrete Card id"):
                    validate_worker_evidence(record)

    def test_short_or_placeholder_checks_fail(self) -> None:
        record = code_record()
        record["baseline"]["check"] = "short"
        record["verification"]["check"] = "short"
        with self.assertRaisesRegex(WorkerEvidenceError, "specific falsifiable"):
            validate_worker_evidence(record)
        record = code_record()
        record["baseline"]["check"] = "python3 -m unittest <suite>"
        record["verification"]["check"] = "python3 -m unittest <suite>"
        with self.assertRaisesRegex(WorkerEvidenceError, "must not carry a placeholder"):
            validate_worker_evidence(record)

    def test_verification_must_close_same_check_for_minimum_change_control(self) -> None:
        record = code_record()
        record["verification"]["check"] = "python3 -m unittest tests.test_other_suite"
        with self.assertRaisesRegex(WorkerEvidenceError, "same falsifiable check"):
            validate_worker_evidence(record)

    def test_retrospective_red_on_implemented_subject_fails(self) -> None:
        record = code_record()
        record["baseline"]["subject"] = {"repository": REPO, "commit": POST_COMMIT}
        with self.assertRaisesRegex(WorkerEvidenceError, "retrospective RED"):
            validate_worker_evidence(record)

    def test_green_must_be_observed_on_implemented_subject(self) -> None:
        record = code_record()
        record["verification"]["subject"] = {"repository": REPO, "commit": OTHER_COMMIT}
        with self.assertRaisesRegex(WorkerEvidenceError, "implemented subject"):
            validate_worker_evidence(record)
        record = code_record()
        record["verification"]["subject"] = {"repository": REPO, "commit": PRE_COMMIT}
        with self.assertRaisesRegex(WorkerEvidenceError, "implemented subject"):
            validate_worker_evidence(record)

    def test_implementation_must_advance_subject(self) -> None:
        record = code_record()
        record["implementation"]["subject"] = {"repository": REPO, "commit": PRE_COMMIT}
        with self.assertRaisesRegex(WorkerEvidenceError, "implemented subject|retrospective RED"):
            validate_worker_evidence(record)

    def test_baseline_and_verification_require_distinct_evidence(self) -> None:
        record = code_record()
        record["verification"]["evidence"] = record["baseline"]["evidence"]
        with self.assertRaisesRegex(WorkerEvidenceError, "distinct observed evidence"):
            validate_worker_evidence(record)

    def test_generic_evidence_fails(self) -> None:
        record = code_record()
        record["baseline"]["evidence"] = "red"
        with self.assertRaisesRegex(WorkerEvidenceError, "generic claim|specific falsifiable"):
            validate_worker_evidence(record)

    def test_chronology_requires_baseline_before_implementation_before_verification(self) -> None:
        inverted = code_record()
        inverted["sequence"] = {"baseline": 3, "implementation": 2, "verification": 1}
        with self.assertRaisesRegex(WorkerEvidenceError, "baseline < implementation < verification"):
            validate_worker_evidence(inverted)
        green_before_impl = code_record()
        green_before_impl["sequence"] = {"baseline": 1, "implementation": 3, "verification": 2}
        with self.assertRaisesRegex(WorkerEvidenceError, "baseline < implementation < verification"):
            validate_worker_evidence(green_before_impl)
        tied = code_record()
        tied["sequence"] = {"baseline": 2, "implementation": 2, "verification": 3}
        with self.assertRaisesRegex(WorkerEvidenceError, "baseline < implementation < verification"):
            validate_worker_evidence(tied)

    def test_non_integer_or_negative_sequence_fails(self) -> None:
        record = code_record()
        record["sequence"] = {"baseline": True, "implementation": 2, "verification": 3}
        with self.assertRaisesRegex(WorkerEvidenceError, "must be an integer"):
            validate_worker_evidence(record)
        record = code_record()
        record["sequence"] = {"baseline": -1, "implementation": 0, "verification": 1}
        with self.assertRaisesRegex(WorkerEvidenceError, "must be non-negative"):
            validate_worker_evidence(record)

    def test_observable_check_requires_explicit_justification(self) -> None:
        record = observable_record()
        record["observable_justification"] = None
        with self.assertRaisesRegex(WorkerEvidenceError, "observable_justification must explain"):
            validate_worker_evidence(record)
        record = observable_record()
        record["observable_justification"] = "too short"
        with self.assertRaisesRegex(WorkerEvidenceError, "explicit observable predicate"):
            validate_worker_evidence(record)
        record = observable_record()
        record["observable_justification"] = "observe <target> with enough words to pass length here"
        with self.assertRaisesRegex(WorkerEvidenceError, "must not carry a placeholder"):
            validate_worker_evidence(record)

    def test_automated_check_rejects_stray_observable_justification(self) -> None:
        record = code_record()
        record["observable_justification"] = "stray justification that should not be present here"
        with self.assertRaisesRegex(WorkerEvidenceError, "must be null for an automated check"):
            validate_worker_evidence(record)

    def test_observable_cannot_substitute_for_automatable_code_outcome(self) -> None:
        record = code_record()
        record["baseline"]["kind"] = "observable_check"
        record["observable_justification"] = (
            "long enough justification naming an observable predicate for code"
        )
        with self.assertRaisesRegex(WorkerEvidenceError, "cannot substitute for an automatable"):
            validate_worker_evidence(record)

    def test_unknown_outcome_class_and_kind_fail(self) -> None:
        record = code_record()
        record["outcome_class"] = "operations"
        with self.assertRaisesRegex(WorkerEvidenceError, "outcome_class"):
            validate_worker_evidence(record)
        record = code_record()
        record["baseline"]["kind"] = "vibes_check"
        with self.assertRaisesRegex(WorkerEvidenceError, "baseline.kind"):
            validate_worker_evidence(record)

    def test_invalid_card_id_and_subject_identity_fail(self) -> None:
        record = code_record()
        record["card_id"] = "generic card"
        with self.assertRaisesRegex(WorkerEvidenceError, "concrete Card id"):
            validate_worker_evidence(record)
        record = code_record()
        record["baseline"]["subject"] = {"repository": REPO, "commit": "not-a-sha"}
        with self.assertRaisesRegex(WorkerEvidenceError, "commit must be exact 40-hex"):
            validate_worker_evidence(record)

    def test_telemetry_identity_is_non_canonical(self) -> None:
        for key in ("worker_id", "provider", "model_name", "session_uuid", "runtime_topology"):
            with self.subTest(key=key):
                record = code_record()
                record[key] = "worker-7"
                with self.assertRaisesRegex(WorkerEvidenceError, "telemetry key|invalid top-level keys"):
                    validate_worker_evidence(record)
        nested = code_record()
        nested["implementation"]["worker"] = "worker-7"
        with self.assertRaisesRegex(WorkerEvidenceError, "telemetry key"):
            validate_worker_evidence(nested)

    def test_worker_return_classification_composes_with_existing_lifecycle(self) -> None:
        self.assertEqual(
            classify_worker_return(evidence_valid=True, real_blocker=False), "reconcile"
        )
        self.assertEqual(
            classify_worker_return(evidence_valid=False, real_blocker=False), "correct"
        )
        self.assertEqual(
            classify_worker_return(evidence_valid=False, real_blocker=True), "block"
        )
        self.assertEqual(
            classify_worker_return(evidence_valid=True, real_blocker=True), "block"
        )

    def test_absent_evidence_is_legacy_compatible_not_retrospective(self) -> None:
        self.assertEqual(falsification_status(None), "legacy_compatible")
        self.assertEqual(
            falsification_status(None, expected_card_id="M02R-T12"), "legacy_compatible"
        )

    def test_evidence_card_binding_must_match_active_card(self) -> None:
        with self.assertRaisesRegex(WorkerEvidenceError, "does not match the active Card"):
            falsification_status(code_record(), expected_card_id="M02R-T11")

    def test_historical_card_result_shape_remains_valid(self) -> None:
        text = (
            "# Card Result\n"
            "- Card ID: M03-T02\n"
            "- Implementation subject: owner/repo@commit:" + ("a" * 40) + "\n"
            "- Evidence refs: implementation/workstreams/sample-workstream/evidence/build.md\n"
            "- Tests/readback summary: implementation and verification GREEN\n"
        )
        parsed = parse_card_result(text, "M03-T02", "sample-workstream")
        self.assertEqual(parsed["card_id"], "M03-T02")
        self.assertEqual(falsification_status(None), "legacy_compatible")

    def test_record_with_extra_top_level_key_fails(self) -> None:
        record = code_record()
        record["scope_guard"] = "yagni"
        with self.assertRaisesRegex(WorkerEvidenceError, "invalid top-level keys"):
            validate_worker_evidence(record)

    def test_valid_record_is_not_mutated_by_validation(self) -> None:
        record = code_record()
        snapshot = copy.deepcopy(record)
        validate_worker_evidence(record)
        self.assertEqual(record, snapshot)


if __name__ == "__main__":
    unittest.main()
