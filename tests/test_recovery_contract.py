from __future__ import annotations

import unittest

from tools.recovery_contract import (
    RecoveryContractError,
    classify_resolution,
    exact_result_subject,
)


class RecoveryContractTests(unittest.TestCase):
    def test_red_and_blocker_classification_has_distinct_owners(self) -> None:
        self.assertEqual(classify_resolution("bounded_correction"), ("execution", False))
        self.assertEqual(classify_resolution("plan_strategy"), ("planning", False))
        self.assertEqual(classify_resolution("definition_authority"), ("definition", False))
        self.assertEqual(classify_resolution("missing_evidence"), ("research", False))
        self.assertEqual(classify_resolution("human_authority"), ("user_stop", True))
        self.assertEqual(classify_resolution("runtime_access_input"), ("blocker_stop", True))
        with self.assertRaises(RecoveryContractError):
            classify_resolution("worker_disappeared")

    def test_exact_result_subject_requires_immutable_identity(self) -> None:
        ref = {
            "path": "implementation/workstreams/sample/results/M03-T02.md",
            "commit": "a" * 40,
            "blob": "b" * 40,
        }
        self.assertEqual(
            exact_result_subject("owner/repo", ref),
            f"owner/repo@{'a' * 40}:implementation/workstreams/sample/results/M03-T02.md@{'b' * 40}",
        )
        with self.assertRaises(RecoveryContractError):
            exact_result_subject("owner/repo", {"path": ref["path"]})


if __name__ == "__main__":
    unittest.main()
