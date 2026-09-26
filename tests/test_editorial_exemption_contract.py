from __future__ import annotations

import copy
import unittest

from tools.editorial_exemption_contract import (
    EditorialExemptionError,
    validate_editorial_classification_locator,
    validate_editorial_exemption_classification,
)


class EditorialExemptionContractTests(unittest.TestCase):
    def subject(self, blob: str) -> dict[str, str]:
        return {
            "class": "git_blob",
            "repository": "owner/repo",
            "commit": "a" * 40,
            "path": "planning/MASTER_PLAN.md",
            "blob": blob,
        }

    def planning(self) -> dict[str, object]:
        base = f"owner/repo@{'a' * 40}:planning/MASTER_PLAN.md@{'b' * 40}"
        return {
            "workstream_id": "sample-workstream",
            "cycle": 2,
            "revision": "P2",
            "review_mode": "editorial_exempt",
            "review_exemption_base_subject": base,
            "subject": {
                key: value
                for key, value in self.subject("c" * 40).items()
                if key != "class"
            },
        }

    def classification(self) -> dict[str, object]:
        return {
            "workstream_id": "sample-workstream",
            "planning_cycle": 2,
            "plan_revision": "P2",
            "verdict": "green",
            "classification": "editorial_only",
            "inspected_diff_evidence": (
                "Compared the exact prior and changed plan blobs; only editorial wording changed."
            ),
            "base_subject": self.subject("b" * 40),
            "changed_subject": self.subject("c" * 40),
            "unchanged": {
                "strategy": True,
                "milestone_topology": True,
                "requirement_coverage": True,
                "gates": True,
                "acceptance_semantics": True,
            },
            "independence": {
                "materially_produced_or_repaired_changed_subject": False,
                "basis": "Fresh semantic classifier did not author or repair the changed subject.",
            },
        }

    def test_exact_editorial_only_classification_is_accepted(self) -> None:
        record = validate_editorial_exemption_classification(
            self.classification(),
            workstream_id="sample-workstream",
            planning=self.planning(),
        )
        self.assertEqual(record["classification"], "editorial_only")
        self.assertEqual(record["verdict"], "green")

    def test_non_editorial_or_non_green_classification_is_rejected(self) -> None:
        for field, value, pattern in (
            ("classification", "material", "editorial_only"),
            ("verdict", "red", "GREEN"),
        ):
            candidate = self.classification()
            candidate[field] = value
            with self.subTest(field=field), self.assertRaisesRegex(EditorialExemptionError, pattern):
                validate_editorial_exemption_classification(
                    candidate,
                    workstream_id="sample-workstream",
                    planning=self.planning(),
                )

    def test_subject_mismatch_is_rejected(self) -> None:
        for field, blob, pattern in (
            ("base_subject", "d" * 40, "base subject"),
            ("changed_subject", "d" * 40, "changed subject"),
        ):
            candidate = self.classification()
            candidate[field] = self.subject(blob)
            with self.subTest(field=field), self.assertRaisesRegex(EditorialExemptionError, pattern):
                validate_editorial_exemption_classification(
                    candidate,
                    workstream_id="sample-workstream",
                    planning=self.planning(),
                )

    def test_missing_or_placeholder_diff_evidence_is_rejected(self) -> None:
        for evidence in ("", "none", "TBD"):
            candidate = self.classification()
            candidate["inspected_diff_evidence"] = evidence
            with self.subTest(evidence=evidence), self.assertRaisesRegex(
                EditorialExemptionError, "inspected_diff_evidence"
            ):
                validate_editorial_exemption_classification(
                    candidate,
                    workstream_id="sample-workstream",
                    planning=self.planning(),
                )

    def test_every_unchanged_dimension_must_be_explicitly_true(self) -> None:
        for dimension in (
            "strategy",
            "milestone_topology",
            "requirement_coverage",
            "gates",
            "acceptance_semantics",
        ):
            candidate = self.classification()
            candidate["unchanged"] = copy.deepcopy(candidate["unchanged"])
            candidate["unchanged"][dimension] = False
            with self.subTest(dimension=dimension), self.assertRaisesRegex(
                EditorialExemptionError, dimension
            ):
                validate_editorial_exemption_classification(
                    candidate,
                    workstream_id="sample-workstream",
                    planning=self.planning(),
                )

    def test_classifier_must_be_independent_of_changed_subject(self) -> None:
        candidate = self.classification()
        candidate["independence"] = {
            "materially_produced_or_repaired_changed_subject": True,
            "basis": "Same context changed the plan.",
        }
        with self.assertRaisesRegex(EditorialExemptionError, "not independent"):
            validate_editorial_exemption_classification(
                candidate,
                workstream_id="sample-workstream",
                planning=self.planning(),
            )

    def test_proof_locator_is_exact_and_workstream_local(self) -> None:
        valid = {
            "class": "git_blob",
            "repository": "owner/repo",
            "commit": "a" * 40,
            "path": (
                "implementation/workstreams/sample-workstream/"
                "planning_classifications/P2-E01.toml"
            ),
            "blob": "b" * 40,
        }
        record = validate_editorial_classification_locator(valid, "sample-workstream")
        self.assertEqual(record["blob"], "b" * 40)

        for path in (
            "implementation/workstreams/other/planning_classifications/P2-E01.toml",
            "implementation/workstreams/sample-workstream/evidence/P2-E01.toml",
            "../planning_classifications/P2-E01.toml",
        ):
            candidate = dict(valid)
            candidate["path"] = path
            with self.subTest(path=path), self.assertRaises(EditorialExemptionError):
                validate_editorial_classification_locator(candidate, "sample-workstream")


if __name__ == "__main__":
    unittest.main()
