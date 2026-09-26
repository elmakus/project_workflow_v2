from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tools.migration_apply import (
    MigrationApplyError,
    SimulatedMigrationCrash,
    apply_fixture_conversion,
    authorization_for,
    readback_fixture_destination,
    reconcile_uncertain_external_effect,
    rollback_fixture_staging,
)
from tools.v1_migration import convert_dry_run, dry_run

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "fixtures" / "migration"
REPO = "elmakus/chatgpt-codex-project-workflow"
SHA = "a" * 40


class MigrationApplyTests(unittest.TestCase):
    def texts(self):
        return (
            (FIX / "chatgpt-board.yaml").read_text(encoding="utf-8"),
            (FIX / "chatgpt-workstream.yaml").read_text(encoding="utf-8"),
        )

    def artifact_reader(self, repository: str, commit: str, path: str):
        self.assertEqual(repository, REPO)
        self.assertEqual(commit, SHA)
        return f"# exact source artifact\n\n{repository}@{commit}:{path}\n".encode("utf-8")

    def bundle(self):
        board, manifest = self.texts()
        plan = dry_run(
            source_class="chatgpt_workstream_yaml_v1",
            repository=REPO,
            expected_commit=SHA,
            observed_commit=SHA,
            board_text=board,
            manifest_text=manifest,
            destination_workstream="migrated-chatgpt",
        )
        return convert_dry_run(plan=plan, board_text=board, manifest_text=manifest)

    def apply(self, destination: Path, *, bundle=None, board=None, manifest=None, crash_at=None):
        bundle = bundle or self.bundle()
        source_board, source_manifest = self.texts()
        return apply_fixture_conversion(
            bundle=bundle,
            destination_root=destination,
            authorization=authorization_for(bundle),
            observed_commit=SHA,
            board_text=source_board if board is None else board,
            manifest_text=source_manifest if manifest is None else manifest,
            crash_at=crash_at,
            source_artifact_reader=self.artifact_reader,
        )

    def test_apply_requires_explicit_exact_authorization(self):
        board, manifest = self.texts()
        bundle = self.bundle()
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaisesRegex(MigrationApplyError, "authorization"):
                apply_fixture_conversion(
                    bundle=bundle,
                    destination_root=Path(td) / "migrated-chatgpt",
                    authorization="yes",
                    observed_commit=SHA,
                    board_text=board,
                    manifest_text=manifest,
                    source_artifact_reader=self.artifact_reader,
                )

    def test_apply_readback_and_repeat_are_idempotent(self):
        bundle = self.bundle()
        with tempfile.TemporaryDirectory() as td:
            destination = Path(td) / "migrated-chatgpt"
            first = self.apply(destination, bundle=bundle)
            self.assertEqual(first["status"], "applied")
            self.assertEqual(readback_fixture_destination(destination, bundle)["status"], "verified")
            self.assertTrue((destination / "cards" / "M05-T05.md").is_file())
            self.assertTrue((destination / "results" / "M05-T05.md").is_file())
            second = self.apply(destination, bundle=bundle)
            self.assertEqual(second["status"], "noop")

    def test_apply_fails_closed_when_exact_source_artifacts_cannot_be_materialized(self):
        board, manifest = self.texts()
        bundle = self.bundle()
        with tempfile.TemporaryDirectory() as td:
            destination = Path(td) / "migrated-chatgpt"
            with self.assertRaisesRegex(MigrationApplyError, "artifact reader"):
                apply_fixture_conversion(
                    bundle=bundle,
                    destination_root=destination,
                    authorization=authorization_for(bundle),
                    observed_commit=SHA,
                    board_text=board,
                    manifest_text=manifest,
                )
            self.assertFalse(destination.exists())

    def test_changed_source_fails_closed_before_destination_mutation(self):
        board, _ = self.texts()
        bundle = self.bundle()
        with tempfile.TemporaryDirectory() as td:
            destination = Path(td) / "migrated-chatgpt"
            with self.assertRaisesRegex(MigrationApplyError, "source divergence"):
                self.apply(destination, bundle=bundle, board=board + "\n# changed\n")
            self.assertFalse(destination.exists())

    def test_changed_destination_fails_closed(self):
        bundle = self.bundle()
        with tempfile.TemporaryDirectory() as td:
            destination = Path(td) / "migrated-chatgpt"
            self.apply(destination, bundle=bundle)
            with (destination / "WORKSTREAM.toml").open("a", encoding="utf-8") as handle:
                handle.write("\n# divergence\n")
            with self.assertRaisesRegex(MigrationApplyError, "destination divergence"):
                self.apply(destination, bundle=bundle)

    def test_restart_after_crash_before_record_rebuilds_stage(self):
        bundle = self.bundle()
        with tempfile.TemporaryDirectory() as td:
            destination = Path(td) / "migrated-chatgpt"
            with self.assertRaises(SimulatedMigrationCrash):
                self.apply(destination, bundle=bundle, crash_at="before_record")
            result = self.apply(destination, bundle=bundle)
            self.assertEqual(result["status"], "applied")
            self.assertEqual(readback_fixture_destination(destination, bundle)["status"], "verified")

    def test_restart_after_record_promotes_verified_existing_stage(self):
        bundle = self.bundle()
        with tempfile.TemporaryDirectory() as td:
            destination = Path(td) / "migrated-chatgpt"
            with self.assertRaises(SimulatedMigrationCrash):
                self.apply(destination, bundle=bundle, crash_at="after_record")
            result = self.apply(destination, bundle=bundle)
            self.assertEqual(result["status"], "applied")
            self.assertEqual(readback_fixture_destination(destination, bundle)["status"], "verified")

    def test_restart_after_promotion_is_verified_noop_without_source_recovery_dependency(self):
        bundle = self.bundle()
        with tempfile.TemporaryDirectory() as td:
            destination = Path(td) / "migrated-chatgpt"
            with self.assertRaises(SimulatedMigrationCrash):
                self.apply(destination, bundle=bundle, crash_at="after_promotion")
            self.assertEqual(readback_fixture_destination(destination, bundle)["status"], "verified")
            result = self.apply(destination, bundle=bundle)
            self.assertEqual(result["status"], "noop")

    def test_unactivated_stage_can_roll_back_but_activated_destination_cannot(self):
        bundle = self.bundle()
        with tempfile.TemporaryDirectory() as td:
            destination = Path(td) / "migrated-chatgpt"
            with self.assertRaises(SimulatedMigrationCrash):
                self.apply(destination, bundle=bundle, crash_at="after_record")
            self.assertEqual(rollback_fixture_staging(destination, bundle)["status"], "rolled_back")
            self.assertFalse(destination.exists())
            self.apply(destination, bundle=bundle)
            with self.assertRaisesRegex(MigrationApplyError, "forward-repair"):
                rollback_fixture_staging(destination, bundle)

    def test_uncertain_external_effect_is_read_back_before_retry(self):
        calls = []
        result = reconcile_uncertain_external_effect(
            lambda: calls.append("readback") or "expected_effect"
        )
        self.assertEqual(calls, ["readback"])
        self.assertEqual(result["action"], "do_not_retry")

        result = reconcile_uncertain_external_effect(lambda: "no_effect")
        self.assertEqual(result["action"], "retry_permitted")

        with self.assertRaisesRegex(MigrationApplyError, "retry is forbidden"):
            reconcile_uncertain_external_effect(lambda: "unknown")

    def test_terminal_review_without_migration_proof_blocks_with_obligation_not_evidence(self):
        board, manifest = self.texts()
        plan = dry_run(
            source_class="chatgpt_workstream_yaml_v1",
            repository=REPO,
            expected_commit=SHA,
            observed_commit=SHA,
            board_text=board,
            manifest_text=manifest,
            destination_workstream="migrated-chatgpt",
        )
        proof = {
            "attempt": "R01",
            "verdict": "green",
            "source_review_subject": "exact-subject",
            "subject": {
                "repository": REPO,
                "commit": "b" * 40,
                "path": "implementation/workstreams/feature-common-preexecution-core/evidence/reviewed.md",
                "blob": "c" * 40,
            },
            "materially_produced_or_repaired_subject": False,
            "independence_basis": "Exact V1 evidence proves semantic independence.",
            "evidence_path": (
                "implementation/workstreams/feature-common-preexecution-core/evidence/"
                "M05-T05-independent-review-R01-2026-09-23.md"
            ),
        }
        bundle = convert_dry_run(
            plan=plan,
            board_text=board,
            manifest_text=manifest,
            review_proofs={"M05-T05": [proof]},
        )
        # RF006: no manufactured provenance means no routable attempt and no
        # terminal evidence; the Card blocks with a precise obligation.
        self.assertNotIn("M05-T05", bundle["review_attempts"])
        with tempfile.TemporaryDirectory() as td:
            destination = Path(td) / "migrated-chatgpt"
            self.apply(destination, bundle=bundle)
            evidence = destination / "evidence" / "migrated-M05-T05-R01.md"
            self.assertFalse(evidence.exists())
            blocker = destination / "blockers" / "M05-T05-migration-review.toml"
            self.assertTrue(blocker.is_file())
            self.assertIn("legacy migration proof", blocker.read_text(encoding="utf-8"))
            self.assertEqual(
                readback_fixture_destination(destination, bundle)["status"],
                "verified",
            )

    def test_activated_destination_readback_survives_source_disappearance(self):
        bundle = self.bundle()
        with tempfile.TemporaryDirectory() as td:
            destination = Path(td) / "migrated-chatgpt"
            self.apply(destination, bundle=bundle)
            # A10-style recovery: activated output is self-verifying and does not need V1 source files.
            self.assertEqual(readback_fixture_destination(destination, bundle)["status"], "verified")


if __name__ == "__main__":
    unittest.main()
