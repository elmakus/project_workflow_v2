from __future__ import annotations

import unittest

from tools.review_contract import select_review_realization


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


if __name__ == "__main__":
    unittest.main()
