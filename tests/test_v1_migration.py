from __future__ import annotations

import copy
import hashlib
import tomllib
import unittest
from pathlib import Path

from tools.v1_migration import MigrationInputError, dry_run, parse_bounded_yaml

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "fixtures" / "migration"
REPO = "elmakus/chatgpt-codex-project-workflow"
SHA = "a" * 40


class V1MigrationDryRunTests(unittest.TestCase):
    def texts(self, stem: str) -> tuple[str, str | None]:
        board = (FIX / f"{stem}-board.yaml").read_text()
        manifest_path = FIX / f"{stem}-workstream.yaml"
        return board, manifest_path.read_text() if manifest_path.exists() else None

    def plan(self, source_class: str, stem: str):
        board, manifest = self.texts(stem)
        return dry_run(
            source_class=source_class,
            repository=REPO,
            expected_commit=SHA,
            observed_commit=SHA,
            board_text=board,
            manifest_text=manifest,
            destination_workstream=f"migrated-{stem}",
        )

    def test_real_source_origins_are_exact_and_finite(self) -> None:
        with (FIX / "ORIGINS.toml").open("rb") as handle:
            origins = tomllib.load(handle)
        self.assertEqual(
            set(origins),
            {
                "chatgpt_workstream_yaml_v1",
                "codex_workstream_yaml_v1",
                "legacy_root_yaml_v1",
            },
        )
        for value in origins.values():
            self.assertRegex(value["commit"], r"^[0-9a-f]{40}$")
            self.assertRegex(value["board_blob"], r"^[0-9a-f]{40}$")
            if "manifest_blob" in value:
                self.assertRegex(value["manifest_blob"], r"^[0-9a-f]{40}$")

    def test_three_real_derived_classes_have_deterministic_mutation_free_dry_run(self) -> None:
        cases = (
            ("chatgpt_workstream_yaml_v1", "chatgpt"),
            ("codex_workstream_yaml_v1", "codex"),
            ("legacy_root_yaml_v1", "legacy-root"),
        )
        for source_class, stem in cases:
            with self.subTest(source_class=source_class):
                before = {
                    p: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in FIX.iterdir()
                    if p.is_file()
                }
                first = self.plan(source_class, stem)
                second = self.plan(source_class, stem)
                after = {
                    p: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in FIX.iterdir()
                    if p.is_file()
                }
                self.assertEqual(first, second)
                self.assertTrue(first["valid"])
                self.assertEqual(first["destination"]["root"], f"implementation/workstreams/migrated-{stem}")
                self.assertEqual(before, after)

    def test_legacy_root_never_becomes_root_v2_destination(self) -> None:
        plan = self.plan("legacy_root_yaml_v1", "legacy-root")
        self.assertTrue(plan["destination"]["manifest"].startswith("implementation/workstreams/"))
        self.assertTrue(plan["destination"]["task_board"].startswith("implementation/workstreams/"))
        self.assertNotEqual(plan["destination"]["task_board"], "implementation/TASK_BOARD.toml")

    def test_unknown_source_class_and_unknown_semantic_field_fail_closed(self) -> None:
        board, manifest = self.texts("chatgpt")
        with self.assertRaisesRegex(MigrationInputError, "unsupported source class"):
            dry_run(
                source_class="hypothetical_v0",
                repository=REPO,
                expected_commit=SHA,
                observed_commit=SHA,
                board_text=board,
                manifest_text=manifest,
                destination_workstream="migrated-chatgpt",
            )
        parsed = parse_bounded_yaml(board)
        self.assertIn("cards", parsed)
        changed = board.replace('research_obligation: null', 'research_obligation: null\nsemantic_surprise: true')
        with self.assertRaisesRegex(MigrationInputError, "unsupported fields"):
            dry_run(
                source_class="chatgpt_workstream_yaml_v1",
                repository=REPO,
                expected_commit=SHA,
                observed_commit=SHA,
                board_text=changed,
                manifest_text=manifest,
                destination_workstream="migrated-chatgpt",
            )

    def test_racing_source_identity_fails_closed(self) -> None:
        board, manifest = self.texts("chatgpt")
        with self.assertRaisesRegex(MigrationInputError, "source moved"):
            dry_run(
                source_class="chatgpt_workstream_yaml_v1",
                repository=REPO,
                expected_commit="a" * 40,
                observed_commit="b" * 40,
                board_text=board,
                manifest_text=manifest,
                destination_workstream="migrated-chatgpt",
            )

    def test_parallel_active_cards_are_reported_as_blocker_without_choosing_winner(self) -> None:
        board, manifest = self.texts("chatgpt")
        parsed = parse_bounded_yaml(board)
        card = copy.deepcopy(parsed["cards"][0])
        card["id"] = "M05-T06"
        card["execution_status"] = "in_progress"
        first = board.replace("execution_status: done", "execution_status: in_progress", 2)
        extra = (
            '\n  - id: "M05-T06"\n'
            '    title: "Competing active card"\n'
            '    milestone: "M05"\n'
            '    decision_state: accepted\n'
            '    execution_status: in_progress\n'
            '    executor: chatgpt\n'
            '    depends_on: []\n'
            '    openspec_change: null\n'
            '    contract: "implementation/workstreams/feature-common-preexecution-core/cards/M05-T06.md"\n'
            '    review_state: null\n'
            '    review_subject: null\n'
            '    review_evidence: null\n'
            '    result_commit: null\n'
            '    result_pr: null\n'
            '    evidence: null\n'
            '    tests_summary: null\n'
        )
        plan = dry_run(
            source_class="chatgpt_workstream_yaml_v1",
            repository=REPO,
            expected_commit=SHA,
            observed_commit=SHA,
            board_text=first.rstrip() + extra,
            manifest_text=manifest,
            destination_workstream="migrated-chatgpt",
        )
        self.assertFalse(plan["valid"])
        self.assertEqual(plan["blockers"], ["parallel_active_cards:M05-T05,M05-T06"])
        self.assertIn("card:M05-T05:in_progress", plan["outstanding_obligations"])
        self.assertIn("card:M05-T06:in_progress", plan["outstanding_obligations"])

    def test_terminal_review_without_exact_subject_fails_closed(self) -> None:
        board, manifest = self.texts("chatgpt")
        changed = board.replace('review_subject: "exact-subject"', "review_subject: null")
        with self.assertRaisesRegex(MigrationInputError, "terminal V1 review lacks exact review_subject"):
            dry_run(
                source_class="chatgpt_workstream_yaml_v1",
                repository=REPO,
                expected_commit=SHA,
                observed_commit=SHA,
                board_text=changed,
                manifest_text=manifest,
                destination_workstream="migrated-chatgpt",
            )


if __name__ == "__main__":
    unittest.main()
