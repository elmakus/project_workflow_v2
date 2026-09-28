import unittest

from tools.continuation_contract import (
    ContinuationContractError,
    classify_route_completion,
    classify_progress,
    ProgressObservation,
    resume_action,
)
from tools.review_contract import review_delivery_policy, select_review_realization
from tools.user_stop_contract import HANDOFF_NONE, HANDOFF_REQUIRED


class ContinuationContractTests(unittest.TestCase):
    def test_non_stop_obligations_must_continue(self):
        for obligation in (
            "execution",
            "execution_prep",
            "post_review_finalization",
            "result_reconciliation",
            "review",
            "research",
            "research_cleanup",
            "close",
            "planning",
            "definition",
        ):
            with self.subTest(obligation=obligation):
                decision = classify_route_completion(
                    disposition="route", obligation=obligation
                )
                self.assertEqual(decision.action, "continue")
                self.assertFalse(decision.legal_return)

    def test_real_router_stop_permits_return(self):
        for obligation in (
            "explicit_user_stop",
            "premium_A",
            "premium_B",
            "premium_C",
            "independent_review",
            "runtime_blocker",
            "end_of_approved_scope",
        ):
            with self.subTest(obligation=obligation):
                decision = classify_route_completion(
                    disposition="stop", obligation=obligation
                )
                self.assertEqual(decision.action, "return")
                self.assertTrue(decision.legal_return)

    def test_recovery_is_fail_closed_not_normal_return(self):
        decision = classify_route_completion(
            disposition="recovery", obligation="recovery_boundary"
        )
        self.assertEqual(decision.action, "recover")
        self.assertFalse(decision.legal_return)

    def test_invalid_route_shape_fails_closed(self):
        for disposition, obligation in (
            ("", "execution"),
            ("route", ""),
            ("unknown", "execution"),
        ):
            with self.subTest(disposition=disposition, obligation=obligation):
                with self.assertRaises(ContinuationContractError):
                    classify_route_completion(
                        disposition=disposition, obligation=obligation
                    )

    def test_claimed_success_without_progress_fails_closed(self):
        state = ProgressObservation("route:execution:M02-T01", "evidence:1")
        with self.assertRaises(ContinuationContractError):
            classify_progress(previous=state, current=state)

    def test_evidence_free_semantic_cycle_fails_closed(self):
        previous = ProgressObservation("route:review:M02-T01", "evidence:1")
        current = ProgressObservation("route:execution:M02-T01", "evidence:1")
        with self.assertRaises(ContinuationContractError):
            classify_progress(
                previous=previous,
                current=current,
                seen=frozenset({(current.fingerprint, current.evidence_epoch)}),
            )

    def test_new_evidence_allows_same_semantic_shape_to_progress(self):
        previous = ProgressObservation("route:review:M02-T01", "evidence:1")
        current = ProgressObservation("route:execution:M02-T01", "evidence:2")
        self.assertEqual(
            classify_progress(previous=previous, current=current, seen=frozenset()),
            "continue",
        )

    def test_restart_reconciles_durable_result_without_replay(self):
        self.assertEqual(
            resume_action(durable_semantic_result=True, external_effect_uncertain=False),
            "reconcile_without_replay",
        )

    def test_uncertain_external_effect_requires_readback_before_retry(self):
        self.assertEqual(
            resume_action(durable_semantic_result=False, external_effect_uncertain=True),
            "readback_external_effect_before_retry",
        )

    def test_green_and_red_review_transitions_do_not_stop_by_verdict(self):
        for obligation in ("post_review_finalization", "execution", "research"):
            with self.subTest(obligation=obligation):
                decision = classify_route_completion(
                    disposition="route", obligation=obligation
                )
                self.assertEqual(decision.action, "continue")
                self.assertFalse(decision.legal_return)

    def test_review_independence_is_recomputed_for_repaired_subject(self):
        self.assertEqual(
            select_review_realization(
                current_context_produced_subject=True,
                independent_context_available=False,
            ),
            "fresh_context",
        )
        self.assertEqual(
            review_delivery_policy(
                current_context_produced_subject=True,
                independent_context_available=False,
            ),
            HANDOFF_REQUIRED,
        )

    def test_internal_independent_review_avoids_synthetic_handoff(self):
        self.assertEqual(
            select_review_realization(
                current_context_produced_subject=True,
                independent_context_available=True,
            ),
            "internal_independent",
        )
        self.assertEqual(
            review_delivery_policy(
                current_context_produced_subject=True,
                independent_context_available=True,
            ),
            HANDOFF_NONE,
        )
        self.assertEqual(
            review_delivery_policy(
                current_context_produced_subject=False,
                independent_context_available=False,
            ),
            HANDOFF_NONE,
        )


if __name__ == "__main__":
    unittest.main()
