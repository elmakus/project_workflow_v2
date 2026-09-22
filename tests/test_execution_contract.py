from __future__ import annotations

import unittest

from tools.execution_contract import (
    ExecutionContractError,
    choose_realization,
    classify_return,
    parse_card_result,
)


class ExecutionContractTests(unittest.TestCase):
    def result_text(self) -> str:
        return (
            "# Card Result\n"
            "- Card ID: M03-T02\n"
            "- Implementation subject: owner/repo@commit:" + ("a" * 40) + "\n"
            "- Evidence refs: implementation/workstreams/sample-workstream/evidence/build.md, "
            "implementation/workstreams/sample-workstream/evidence/tests.md\n"
            "- Tests/readback summary: implementation and verification GREEN\n"
        )

    def test_delegated_and_direct_realizations_share_semantic_result_contract(self) -> None:
        self.assertEqual(choose_realization(True, True, True), "delegate")
        self.assertEqual(choose_realization(False, True, True), "direct")
        self.assertEqual(choose_realization(True, False, True), "direct")
        parsed = parse_card_result(self.result_text(), "M03-T02", "sample-workstream")
        self.assertEqual(parsed["card_id"], "M03-T02")
        self.assertEqual(len(parsed["evidence_refs"]), 2)

    def test_return_classification_keeps_bad_result_in_card_and_real_blocker_distinct(self) -> None:
        self.assertEqual(classify_return(acceptance_valid=True, real_blocker=False), "reconcile")
        self.assertEqual(classify_return(acceptance_valid=False, real_blocker=False), "correct")
        self.assertEqual(classify_return(acceptance_valid=False, real_blocker=True), "block")

    def test_result_rejects_runtime_identity_and_cross_workstream_evidence(self) -> None:
        with self.assertRaisesRegex(ExecutionContractError, "runtime identity"):
            parse_card_result(
                self.result_text() + "- Worker ID: worker-7\n",
                "M03-T02",
                "sample-workstream",
            )
        with self.assertRaisesRegex(ExecutionContractError, "invalid workstream evidence"):
            parse_card_result(
                self.result_text().replace(
                    "implementation/workstreams/sample-workstream/evidence/build.md",
                    "implementation/workstreams/other/evidence/build.md",
                ),
                "M03-T02",
                "sample-workstream",
            )

    def test_result_is_semantic_and_does_not_require_worker_count(self) -> None:
        parsed = parse_card_result(self.result_text(), "M03-T02", "sample-workstream")
        self.assertNotIn("worker", " ".join(parsed.keys()))
        self.assertIn("implementation_subject", parsed)


if __name__ == "__main__":
    unittest.main()
