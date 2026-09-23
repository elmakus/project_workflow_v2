from __future__ import annotations

import unittest
from pathlib import Path

from tools.v1_migration import MigrationInputError, convert_dry_run, dry_run

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "fixtures" / "migration"
REPO = "elmakus/chatgpt-codex-project-workflow"
SHA = "a" * 40


class MigrationRehearsalTests(unittest.TestCase):
    def source(self):
        return (
            (FIX / "chatgpt-board.yaml").read_text(encoding="utf-8"),
            (FIX / "chatgpt-workstream.yaml").read_text(encoding="utf-8"),
        )

    def plan(self, board: str, manifest: str):
        return dry_run(
            source_class="chatgpt_workstream_yaml_v1",
            repository=REPO,
            expected_commit=SHA,
            observed_commit=SHA,
            board_text=board,
            manifest_text=manifest,
            destination_workstream="migrated-rehearsal",
        )

    def test_activated_workstream_review_requires_explicit_reconciliation(self):
        board = (FIX / "codex-board.yaml").read_text(encoding="utf-8")
        manifest = (FIX / "codex-workstream.yaml").read_text(encoding="utf-8")
        for state in ("pending", "red", "green"):
            with self.subTest(state=state):
                changed = manifest.replace("  state: green", f"  state: {state}", 1)
                plan = dry_run(
                    source_class="codex_workstream_yaml_v1",
                    repository=REPO,
                    expected_commit=SHA,
                    observed_commit=SHA,
                    board_text=board,
                    manifest_text=changed,
                    destination_workstream="migrated-codex",
                )
                self.assertFalse(plan["valid"])
                self.assertIn(
                    "workstream_review_reconciliation_required",
                    plan["blockers"],
                )
                self.assertIn(
                    f"workstream_review:{state}",
                    plan["outstanding_obligations"],
                )

    def test_preexecution_promotion_research_and_plan_review_require_explicit_reconstitution(self):
        board, manifest = self.source()
        cases = {
            "exploratory_scope": "brainstorming/PWV2_SCOPE.md",
            "research_obligation": "research/PWV2-RESEARCH.md",
            "plan_review": "planning/PWV2_PLAN_REVIEW.md",
        }
        for field, value in cases.items():
            with self.subTest(field=field):
                changed = manifest.replace(
                    f"  {field}: null",
                    f'  {field}: "{value}"',
                )
                plan = self.plan(board, changed)
                self.assertFalse(plan["valid"])
                self.assertIn(
                    f"preexecution_reconstitution_required:{field}",
                    plan["blockers"],
                )
                self.assertIn(
                    f"preexecution:{field}:{value}",
                    plan["outstanding_obligations"],
                )

    def test_board_research_obligation_is_not_silently_converted(self):
        board, manifest = self.source()
        changed = board.replace(
            "research_obligation: null",
            'research_obligation: "research/M06-active.md"',
        )
        plan = self.plan(changed, manifest)
        self.assertFalse(plan["valid"])
        self.assertIn(
            "preexecution_reconstitution_required:research_obligation",
            plan["blockers"],
        )
        self.assertIn(
            "research:research/M06-active.md",
            plan["outstanding_obligations"],
        )

    def test_stacked_parent_dependency_is_preserved_and_blocks_automatic_cutover(self):
        board, manifest = self.source()
        changed = manifest.replace(
            "parent_workstream: null\nparent_branch: null\nparent_dependency: null",
            'parent_workstream: "parent-ws"\n'
            'parent_branch: "feat/parent"\n'
            'parent_dependency: "unmerged-parent-only"',
        )
        plan = self.plan(board, changed)
        self.assertFalse(plan["valid"])
        self.assertIn("stacked_parent_dependency_requires_reconciliation", plan["blockers"])
        self.assertIn(
            "stacked_parent_dependency:parent-ws:feat/parent:unmerged-parent-only",
            plan["outstanding_obligations"],
        )

    def test_single_active_card_survives_conversion_without_scheduler_state(self):
        board, manifest = self.source()
        changed = board.replace(
            '    execution_status: done\n    executor: chatgpt',
            '    execution_status: in_progress\n    executor: chatgpt',
            1,
        ).replace(
            '    review_state: green\n    review_subject: "exact-subject"\n'
            '    review_evidence: "implementation/workstreams/feature-common-preexecution-core/evidence/M05-T05-independent-review-R01-2026-09-23.md"\n'
            '    result_commit: "e95bea2e828e86601cb127fd7564d013a51b0846"\n'
            '    result_pr: 5\n'
            '    evidence: "implementation/workstreams/feature-common-preexecution-core/evidence/M05-T05-cumulative-acceptance-P2-2026-09-23.md"\n'
            '    tests_summary: "GREEN"',
            '    review_state: null\n    review_subject: null\n'
            '    review_evidence: null\n    result_commit: null\n'
            '    result_pr: null\n    evidence: null\n    tests_summary: null',
        )
        plan = self.plan(changed, manifest)
        self.assertTrue(plan["valid"])
        self.assertIn("card:M05-T05:in_progress", plan["outstanding_obligations"])
        bundle = convert_dry_run(
            plan=plan,
            board_text=changed,
            manifest_text=manifest,
        )
        card = bundle["task_board"]["cards"][0]
        self.assertEqual(card["status"], "in_progress")
        forbidden = {"active_execution", "returned", "transfer_ready", "batch", "lane", "scheduler"}
        self.assertTrue(forbidden.isdisjoint(card))

    def test_result_complete_card_remains_a_result_not_new_execution(self):
        board, manifest = self.source()
        bundle = convert_dry_run(
            plan=self.plan(board, manifest),
            board_text=board,
            manifest_text=manifest,
        )
        card = bundle["task_board"]["cards"][0]
        self.assertEqual(card["status"], "blocked")  # terminal review proof is intentionally not invented
        self.assertIn("result", card)
        self.assertEqual(len(bundle["result_provenance"]), 1)
        self.assertEqual(bundle["result_provenance"][0]["source_result_commit"],
                         "e95bea2e828e86601cb127fd7564d013a51b0846")

    def test_nested_unknown_semantics_and_unresolved_external_effect_fail_closed(self):
        board, manifest = self.source()
        bad_manifest = manifest.replace(
            "  plan_review: null",
            "  plan_review: null\n  semantic_surprise: true",
        )
        with self.assertRaisesRegex(MigrationInputError, "unsupported fields"):
            self.plan(board, bad_manifest)

        bad_board = board.replace(
            "research_obligation: null",
            'research_obligation: null\nexternal_effect: "uncertain"',
        )
        with self.assertRaisesRegex(MigrationInputError, "unsupported fields"):
            self.plan(bad_board, manifest)

    def test_ordinary_router_has_no_migration_runtime_dependency(self):
        router = (ROOT / "tools" / "router.py").read_text(encoding="utf-8")
        workflow = (ROOT / "workflow" / "ROUTER.md").read_text(encoding="utf-8")
        self.assertNotIn("v1_migration", router)
        self.assertNotIn("migration_apply", router)
        self.assertNotIn("from tools.v1_migration", workflow)
        self.assertNotIn("migration_apply", workflow)

    def test_rehearsal_documentation_keeps_cutover_and_coverage_boundaries_explicit(self):
        doc = (ROOT / "docs" / "V1_MIGRATION_REHEARSAL.md").read_text(encoding="utf-8")
        for token in (
            "fixture-only",
            "one live owner",
            "forward-repair",
            "M07",
            "KEEP CORE",
            "GENERALIZE",
            "TRIGGER-ONLY",
            "MIGRATION-ONLY",
            "DROP",
            "BOOTSTRAP",
            "A02",
            "A03",
            "A05",
            "A06",
            "A07",
            "A10",
            "A15",
            "A17",
        ):
            self.assertIn(token, doc)


if __name__ == "__main__":
    unittest.main()
