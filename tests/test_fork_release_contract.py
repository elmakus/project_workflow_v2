from __future__ import annotations

import unittest

from tools.fork_release_contract import (
    FORK_RELEASE_MODULE,
    ForkReleaseContractError,
    UpstreamLineage,
    canonical_order_key,
    module_for_operation,
    next_private_tag,
    select_latest_canonical,
    validate_latest_alias,
    verify_history_immutable,
)


class ForkReleaseContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.lineage = UpstreamLineage(
            repository="upstream/example",
            tag="v5.0.8",
            commit="a" * 40,
        )

    def test_module_is_trigger_only_and_requires_complete_lineage(self) -> None:
        self.assertIsNone(module_for_operation(None))
        self.assertIsNone(module_for_operation("ordinary_close"))
        self.assertEqual(
            module_for_operation("downstream_fork_release", lineage=self.lineage),
            FORK_RELEASE_MODULE,
        )
        with self.assertRaisesRegex(ForkReleaseContractError, "requires accepted upstream"):
            module_for_operation("downstream_fork_release")

    def test_lane_is_baseline_local_and_numeric(self) -> None:
        tags = [
            "v5.0.8",
            "v5.0.13",
            "v5.0.8-private.2",
            "v5.0.8-private.10",
            "v5.0.9-private.99",
            "v5.0.8-private.0",
            "v5.0.8-private.x",
        ]
        self.assertEqual(next_private_tag(self.lineage, tags), "v5.0.8-private.11")
        empty = UpstreamLineage("upstream/example", "v5.0.9", "b" * 40)
        self.assertEqual(next_private_tag(empty, ["v5.0.8-private.99"]), "v5.0.9-private.1")

    def test_cross_baseline_and_private_revision_order_is_numeric(self) -> None:
        self.assertGreater(
            canonical_order_key("v5.0.8-private.10"),
            canonical_order_key("v5.0.8-private.2"),
        )
        self.assertGreater(
            canonical_order_key("v5.0.9-private.1"),
            canonical_order_key("v5.0.8-private.99"),
        )
        self.assertEqual(
            select_latest_canonical([
                "v5.0.8-private.99",
                "v5.0.9-private.1",
                "v5.0.9",
                "v5.1.0-private.2",
            ]),
            "v5.1.0-private.2",
        )

    def test_published_history_is_immutable(self) -> None:
        before = {"v5.0.13", "v5.0.8-private.1"}
        self.assertEqual(
            verify_history_immutable(before, before | {"v5.0.8-private.2"}),
            "history_immutable",
        )
        with self.assertRaisesRegex(ForkReleaseContractError, "immutable"):
            verify_history_immutable(before, {"v5.0.8-private.2"})

    def test_optional_native_latest_alias_has_exact_artifact_identity(self) -> None:
        self.assertEqual(
            validate_latest_alias(
                alias_kind="native_latest",
                canonical_artifact_identity="artifact-sha",
                alias_artifact_identity="artifact-sha",
            ),
            "native_latest_same_artifact",
        )
        with self.assertRaisesRegex(ForkReleaseContractError, "exact accepted canonical artifact"):
            validate_latest_alias(
                alias_kind="native_latest",
                canonical_artifact_identity="artifact-sha",
                alias_artifact_identity="other",
            )
        with self.assertRaisesRegex(ForkReleaseContractError, "vlatest"):
            validate_latest_alias(
                alias_kind="vlatest",
                canonical_artifact_identity="artifact-sha",
                alias_artifact_identity="artifact-sha",
            )

    def test_release_quality_is_not_encoded_by_lineage_helper(self) -> None:
        tag = next_private_tag(self.lineage, [])
        self.assertEqual(tag, "v5.0.8-private.1")
        self.assertNotIn("alpha", tag)
        self.assertNotIn("beta", tag)


if __name__ == "__main__":
    unittest.main()
