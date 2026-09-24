from __future__ import annotations

import unittest

from tools.review_contract import (
    ReviewContractError,
    can_finalize_review_obligation,
    REVIEW_SCOPE_DISCOVERY_CEILINGS,
    required_closure_scope,
    remaining_closure_findings,
    review_convergence_state,
    select_review_realization,
    validate_closure_surface,
    validate_discovery_surface,
)


class ReviewContractTests(unittest.TestCase):
    def test_review_realization_is_capability_first_but_noncanonical(self) -> None:
        self.assertEqual(
            select_review_realization(
                current_context_produced_subject=False,
                independent_context_available=False,
            ),
            "current_context",
        )
        self.assertEqual(
            select_review_realization(
                current_context_produced_subject=True,
                independent_context_available=True,
            ),
            "internal_independent",
        )
        self.assertEqual(
            select_review_realization(
                current_context_produced_subject=True,
                independent_context_available=False,
            ),
            "fresh_context",
        )

    def test_discovery_requires_complete_acceptance_and_no_first_blocker_stop(self) -> None:
        evaluated = validate_discovery_surface(
            applicable_acceptance=["A1", "A2", "A3"],
            evaluated_acceptance=["A3", "A1", "A2"],
            stopped_at_first_blocker=False,
        )
        self.assertEqual(evaluated, frozenset({"A1", "A2", "A3"}))

        with self.assertRaisesRegex(ReviewContractError, "first blocker"):
            validate_discovery_surface(
                applicable_acceptance=["A1", "A2"],
                evaluated_acceptance=["A1"],
                stopped_at_first_blocker=True,
            )
        with self.assertRaisesRegex(ReviewContractError, "omitted applicable acceptance"):
            validate_discovery_surface(
                applicable_acceptance=["A1", "A2"],
                evaluated_acceptance=["A1"],
                stopped_at_first_blocker=False,
            )

    def test_closure_scope_requires_complete_causal_blast_radius(self) -> None:
        scope = {
            "known_findings": ["F1"],
            "defect_classes": ["review-state-bypass"],
            "root_cause_evidence": ["new attempts were indistinguishable from legacy history"],
            "repair_diff": ["tools/api.py"],
            "regression_evidence": ["test_api_contract"],
            "reachable_callers": ["tools/router.py"],
            "consumers": ["unchanged-consumer"],
            "providers": ["unchanged-provider"],
            "contracts": ["API-v2"],
            "sibling_representations": ["json-representation"],
            "negative_space": ["missing-optional-field"],
        }
        required = required_closure_scope(scope)
        self.assertIn("unchanged-consumer", required)
        self.assertIn("unchanged-provider", required)

        validate_closure_surface(scope=scope, evaluated_surface=required)
        with self.assertRaisesRegex(ReviewContractError, "omitted materially implicated surface"):
            validate_closure_surface(
                scope=scope,
                evaluated_surface=required - {"unchanged-consumer"},
            )

        incomplete = dict(scope)
        incomplete.pop("providers")
        with self.assertRaisesRegex(ReviewContractError, "omitted causal categories"):
            required_closure_scope(incomplete)

    def test_closure_rejects_literal_example_only_repair_evidence(self) -> None:
        scope = {
            "known_findings": ["F1"],
            "defect_classes": [],
            "root_cause_evidence": [],
            "repair_diff": ["tools/review_contract.py"],
            "regression_evidence": ["test_literal_example"],
            "reachable_callers": [],
            "consumers": [],
            "providers": [],
            "contracts": [],
            "sibling_representations": ["sibling-state-shape"],
            "negative_space": ["legacy-shaped-new-attempt"],
        }
        with self.assertRaisesRegex(ReviewContractError, "defect_classes.*must not be empty"):
            required_closure_scope(scope)

        scope["defect_classes"] = ["review-state-bypass"]
        with self.assertRaisesRegex(ReviewContractError, "root_cause_evidence.*must not be empty"):
            required_closure_scope(scope)

    def test_cumulative_closure_reports_remaining_source_findings(self) -> None:
        attempts = [
            {
                "attempt": "R01",
                "verdict": "red",
                "review_kind": "discovery",
                "material_finding_ids": ["F1", "F2"],
            },
            {
                "attempt": "R02",
                "verdict": "green",
                "review_kind": "closure_verification",
                "source_discovery_attempt": "R01",
                "material_finding_ids": ["F1"],
            },
        ]
        self.assertEqual(
            remaining_closure_findings(attempts, "R01"),
            frozenset({"F2"}),
        )
        attempts.append({
            "attempt": "R03",
            "verdict": "green",
            "review_kind": "closure_verification",
            "source_discovery_attempt": "R01",
            "material_finding_ids": ["F2"],
        })
        self.assertEqual(
            remaining_closure_findings(attempts, "R01"),
            frozenset(),
        )

    def test_discovery_epoch_ceiling_matrix_counts_only_new_classes(self) -> None:
        for scope, ceiling in REVIEW_SCOPE_DISCOVERY_CEILINGS.items():
            attempts = []
            for index in range(ceiling - 1):
                attempts.append({
                    "attempt": f"R{index + 1:02d}",
                    "verdict": "red",
                    "review_kind": "discovery",
                    "review_scope": scope,
                    "review_epoch": "E01",
                    "material_defect_class_ids": [f"class-{index}"],
                    "post_convergence_validation": False,
                })
            state = review_convergence_state(attempts)
            self.assertEqual(state.discovery_epochs, ceiling - 1)
            self.assertFalse(state.convergence_required, scope)

            attempts.append({
                "attempt": f"R{ceiling:02d}",
                "verdict": "red",
                "review_kind": "discovery",
                "review_scope": scope,
                "review_epoch": "E01",
                "material_defect_class_ids": [f"class-{ceiling - 1}"],
                "post_convergence_validation": False,
            })
            state = review_convergence_state(attempts)
            self.assertEqual(state.discovery_epochs, ceiling)
            self.assertTrue(state.convergence_required, scope)

    def test_known_class_recurrence_green_and_closure_do_not_consume_discovery_epoch(self) -> None:
        attempts = [
            {
                "attempt": "R01",
                "verdict": "red",
                "review_kind": "discovery",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": ["class-a"],
                "post_convergence_validation": False,
            },
            {
                "attempt": "R02",
                "verdict": "green",
                "review_kind": "closure_verification",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": ["class-a"],
                "post_convergence_validation": False,
            },
            {
                "attempt": "R03",
                "verdict": "red",
                "review_kind": "discovery",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": ["class-a"],
                "post_convergence_validation": False,
            },
            {
                "attempt": "R04",
                "verdict": "green",
                "review_kind": "discovery",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": [],
                "post_convergence_validation": False,
            },
        ]
        state = review_convergence_state(attempts)
        self.assertEqual(state.discovery_epochs, 1)
        self.assertFalse(state.convergence_required)

    def test_third_failed_closure_round_for_one_class_requires_convergence(self) -> None:
        attempts = [{
            "attempt": "R01",
            "verdict": "red",
            "review_kind": "discovery",
            "review_scope": "card",
            "review_epoch": "E01",
            "material_defect_class_ids": ["class-a"],
            "post_convergence_validation": False,
            "subject": {
                "repository": "owner/repo",
                "commit": "1" * 40,
                "path": "results/card.md",
                "blob": "2" * 40,
            },
        }]
        for number in range(2, 5):
            attempts.append({
                "attempt": f"R{number:02d}",
                "verdict": "red",
                "review_kind": "closure_verification",
                "source_discovery_attempt": "R01",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": ["class-a"],
                "failed_material_defect_class_ids": ["class-a"],
                "post_convergence_validation": False,
                "subject": {
                    "repository": "owner/repo",
                    "commit": f"{number}" * 40,
                    "path": "results/card.md",
                    "blob": f"{number + 3}" * 40,
                },
            })
            state = review_convergence_state(attempts)
            self.assertEqual(state.failed_closure_rounds["class-a"], number - 1)
            self.assertEqual(state.convergence_required, number == 4)

    def test_repeated_red_closure_of_same_repaired_subject_counts_one_round(self) -> None:
        repaired_subject = {
            "repository": "owner/repo",
            "commit": "4" * 40,
            "path": "results/card.md",
            "blob": "5" * 40,
        }
        attempts = [{
            "attempt": "R01",
            "verdict": "red",
            "review_kind": "discovery",
            "review_scope": "card",
            "review_epoch": "E01",
            "material_defect_class_ids": ["class-a"],
            "post_convergence_validation": False,
            "subject": {
                "repository": "owner/repo",
                "commit": "1" * 40,
                "path": "results/card.md",
                "blob": "2" * 40,
            },
        }]
        for number in range(2, 5):
            attempts.append({
                "attempt": f"R{number:02d}",
                "verdict": "red",
                "review_kind": "closure_verification",
                "source_discovery_attempt": "R01",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": ["class-a"],
                "failed_material_defect_class_ids": ["class-a"],
                "post_convergence_validation": False,
                "subject": repaired_subject,
            })
        state = review_convergence_state(attempts)
        self.assertEqual(state.failed_closure_rounds["class-a"], 1)
        self.assertFalse(state.convergence_required)


    def test_source_discovery_content_does_not_count_as_repair_round(self) -> None:
        source_subject = {
            "repository": "owner/repo",
            "commit": "1" * 40,
            "path": "results/card.md",
            "blob": "2" * 40,
        }
        attempts = [{
            "attempt": "R01",
            "verdict": "red",
            "review_kind": "discovery",
            "review_scope": "card",
            "review_epoch": "E01",
            "material_defect_class_ids": ["class-a"],
            "post_convergence_validation": False,
            "subject": source_subject,
        }]
        for attempt_id, commit, blob in (
            ("R02", "3" * 40, "4" * 40),
            ("R03", "5" * 40, "6" * 40),
            ("R04", "7" * 40, "2" * 40),
        ):
            attempts.append({
                "attempt": attempt_id,
                "verdict": "red",
                "review_kind": "closure_verification",
                "source_discovery_attempt": "R01",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": ["class-a"],
                "failed_material_defect_class_ids": ["class-a"],
                "post_convergence_validation": False,
                "subject": {
                    "repository": "owner/repo",
                    "commit": commit,
                    "path": "results/card.md",
                    "blob": blob,
                },
            })
        state = review_convergence_state(attempts)
        self.assertEqual(state.failed_closure_rounds["class-a"], 2)
        self.assertFalse(state.convergence_required)

    def test_same_content_different_commit_counts_one_repair_round(self) -> None:
        attempts = [{
            "attempt": "R01",
            "verdict": "red",
            "review_kind": "discovery",
            "review_scope": "card",
            "review_epoch": "E01",
            "material_defect_class_ids": ["class-a"],
            "post_convergence_validation": False,
            "subject": {
                "repository": "owner/repo",
                "commit": "1" * 40,
                "path": "results/card.md",
                "blob": "2" * 40,
            },
        }]
        for attempt_id, commit in (("R02", "3" * 40), ("R03", "4" * 40)):
            attempts.append({
                "attempt": attempt_id,
                "verdict": "red",
                "review_kind": "closure_verification",
                "source_discovery_attempt": "R01",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": ["class-a"],
                "failed_material_defect_class_ids": ["class-a"],
                "post_convergence_validation": False,
                "subject": {
                    "repository": "owner/repo",
                    "commit": commit,
                    "path": "results/card.md",
                    "blob": "5" * 40,
                },
            })
        state = review_convergence_state(attempts)
        self.assertEqual(state.failed_closure_rounds["class-a"], 1)
        self.assertFalse(state.convergence_required)

    def test_t01_adapted_class_recurrence_does_not_consume_discovery_epoch(self) -> None:
        attempts = [
            {
                "attempt": "R01",
                "verdict": "red",
                "review_kind": "discovery",
                "material_finding_ids": ["F1"],
            },
            {
                "attempt": "R02",
                "verdict": "green",
                "review_kind": "closure_verification",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": ["class-a"],
                "post_convergence_validation": False,
            },
            {
                "attempt": "R03",
                "verdict": "red",
                "review_kind": "discovery",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": ["class-a"],
                "post_convergence_validation": False,
            },
        ]
        state = review_convergence_state(attempts)
        self.assertEqual(state.discovery_epochs, 0)
        self.assertEqual(state.seen_defect_classes, frozenset({"class-a"}))
        self.assertFalse(state.convergence_required)

    def test_epoch_change_resets_derived_counts_and_post_convergence_is_single(self) -> None:
        attempts = [
            {
                "attempt": "R01",
                "verdict": "red",
                "review_kind": "discovery",
                "review_scope": "final",
                "review_epoch": "E01",
                "material_defect_class_ids": ["a"],
                "post_convergence_validation": False,
            },
            {
                "attempt": "R02",
                "verdict": "red",
                "review_kind": "discovery",
                "review_scope": "final",
                "review_epoch": "E02",
                "material_defect_class_ids": ["b"],
                "post_convergence_validation": False,
            },
        ]
        state = review_convergence_state(attempts)
        self.assertEqual(state.review_epoch, "E02")
        self.assertEqual(state.discovery_epochs, 1)
        self.assertEqual(state.seen_defect_classes, frozenset({"b"}))

        attempts.extend([
            {
                "attempt": "R03",
                "verdict": "green",
                "review_kind": "discovery",
                "review_scope": "final",
                "review_epoch": "E02",
                "material_defect_class_ids": [],
                "post_convergence_validation": True,
            },
            {
                "attempt": "R04",
                "verdict": "green",
                "review_kind": "discovery",
                "review_scope": "final",
                "review_epoch": "E02",
                "material_defect_class_ids": [],
                "post_convergence_validation": True,
            },
        ])
        with self.assertRaisesRegex(ReviewContractError, "only one post-convergence"):
            review_convergence_state(attempts)

    def test_revisited_repaired_content_counts_new_failed_round_after_transition(self) -> None:
        source = {
            "attempt": "R01",
            "verdict": "red",
            "review_kind": "discovery",
            "review_scope": "card",
            "review_epoch": "E01",
            "material_defect_class_ids": ["class-a"],
            "post_convergence_validation": False,
            "subject": {
                "repository": "owner/repo",
                "commit": "1" * 40,
                "path": "results/card.md",
                "blob": "2" * 40,
            },
        }
        attempts = [source]
        for attempt_id, commit, blob in (
            ("R02", "3" * 40, "4" * 40),
            ("R03", "5" * 40, "6" * 40),
            ("R04", "7" * 40, "4" * 40),
        ):
            attempts.append({
                "attempt": attempt_id,
                "verdict": "red",
                "review_kind": "closure_verification",
                "source_discovery_attempt": "R01",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": ["class-a"],
                "failed_material_defect_class_ids": ["class-a"],
                "post_convergence_validation": False,
                "subject": {
                    "repository": "owner/repo",
                    "commit": commit,
                    "path": "results/card.md",
                    "blob": blob,
                },
            })

        state = review_convergence_state(attempts)
        self.assertEqual(state.failed_closure_rounds["class-a"], 3)
        self.assertTrue(state.convergence_required)


    def test_multi_class_red_closure_counts_only_classes_that_failed(self) -> None:
        source = {
            "attempt": "R01",
            "verdict": "red",
            "review_kind": "discovery",
            "review_scope": "card",
            "review_epoch": "E01",
            "material_defect_class_ids": ["class-a", "class-b"],
            "post_convergence_validation": False,
            "subject": {
                "repository": "owner/repo",
                "commit": "1" * 40,
                "path": "results/card.md",
                "blob": "2" * 40,
            },
        }
        closure = {
            "attempt": "R02",
            "verdict": "red",
            "review_kind": "closure_verification",
            "source_discovery_attempt": "R01",
            "review_scope": "card",
            "review_epoch": "E01",
            "material_defect_class_ids": ["class-a", "class-b"],
            "failed_material_defect_class_ids": ["class-b"],
            "post_convergence_validation": False,
            "subject": {
                "repository": "owner/repo",
                "commit": "3" * 40,
                "path": "results/card.md",
                "blob": "4" * 40,
            },
        }

        state = review_convergence_state([source, closure])
        self.assertNotIn("class-a", state.failed_closure_rounds)
        self.assertEqual(state.failed_closure_rounds["class-b"], 1)
        self.assertFalse(state.convergence_required)


    def test_closure_cannot_finalize_review_obligation(self) -> None:
        self.assertTrue(can_finalize_review_obligation({
            "verdict": "green",
            "review_kind": "discovery",
        }))
        self.assertFalse(can_finalize_review_obligation({
            "verdict": "green",
            "review_kind": "closure_verification",
        }))
        self.assertFalse(can_finalize_review_obligation({
            "verdict": "red",
            "review_kind": "discovery",
        }))
        self.assertTrue(can_finalize_review_obligation({"verdict": "green"}))

    def test_expected_review_scope_binds_convergence_owner(self) -> None:
        for scope, ceiling in REVIEW_SCOPE_DISCOVERY_CEILINGS.items():
            attempts = [
                {
                    "attempt": f"R{index + 1:02d}",
                    "verdict": "red",
                    "review_kind": "discovery",
                    "review_scope": scope,
                    "review_epoch": "E01",
                    "material_defect_class_ids": [f"class-{index}"],
                    "post_convergence_validation": False,
                }
                for index in range(ceiling)
            ]
            bound = review_convergence_state(attempts, expected_review_scope=scope)
            self.assertEqual(bound.discovery_ceiling, ceiling)
            self.assertTrue(bound.convergence_required, scope)
            other = "final" if scope == "card" else "card"
            with self.subTest(scope=scope):
                with self.assertRaisesRegex(ReviewContractError, "does not match expected"):
                    review_convergence_state(attempts, expected_review_scope=other)
        with self.assertRaisesRegex(ReviewContractError, "unsupported expected review scope"):
            review_convergence_state([], expected_review_scope="program")


if __name__ == "__main__":
    unittest.main()
