import unittest

from tools.continuation_contract import (
    ContinuationContractError,
    classify_route_completion,
)


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


if __name__ == "__main__":
    unittest.main()
