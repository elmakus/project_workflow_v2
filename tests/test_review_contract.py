from __future__ import annotations

import unittest

from tools.review_contract import (
    ReviewContractError,
    can_finalize_review_obligation,
    required_closure_scope,
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


if __name__ == "__main__":
    unittest.main()
