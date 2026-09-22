from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.router import PRIORITY_FOUNDATION, REAL_STOP_FOUNDATION, select_route

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"


class RouterTests(unittest.TestCase):
    def copy_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(FIXTURE, project)
        return temp, project

    def test_valid_state_selects_same_route_independent_of_runtime_noise(self) -> None:
        expected = None
        for noise in (
            {},
            {"RUNTIME": "chatgpt", "MODEL_ID": "one", "SESSION_ID": "alpha"},
            {"RUNTIME": "codex", "MODEL_ID": "two", "SESSION_ID": "beta"},
        ):
            with patch.dict(os.environ, noise, clear=False):
                routed = select_route(FIXTURE, [MANIFEST], package_root=ROOT)
            semantic = (routed.disposition, routed.obligation, routed.subject, routed.owner_module)
            expected = expected or semantic
            self.assertEqual(semantic, expected)
        self.assertEqual(expected, ("unavailable", "execution", "M01-T04", "workflow/EXECUTION.md"))

    def test_progressive_disclosure_read_set_is_exact(self) -> None:
        routed = select_route(FIXTURE, [MANIFEST], package_root=ROOT)
        self.assertEqual(
            routed.read_set,
            (
                "package:workflow/ROUTER.md",
                "project:PROJECT.md",
                f"project:{MANIFEST}",
                f"project:{BOARD}",
                f"project:{CARD}",
            ),
        )
        joined = "\n".join(routed.read_set)
        self.assertNotIn("migration/UNRELATED.md", joined)
        self.assertNotIn("untrusted/ISSUE_TEXT.md", joined)
        self.assertNotIn("templates/", joined)

    def test_new_managed_intent_routes_to_unimplemented_intake_without_board(self) -> None:
        routed = select_route(FIXTURE, [MANIFEST], package_root=ROOT, entry="new_managed_intent")
        self.assertEqual((routed.disposition, routed.obligation), ("unavailable", "intake"))
        self.assertEqual(routed.read_set, ("package:workflow/ROUTER.md", "project:PROJECT.md"))

    def test_missing_or_ambiguous_selection_routes_to_recovery(self) -> None:
        for selected in ([], [MANIFEST, MANIFEST]):
            with self.subTest(selected=selected):
                routed = select_route(FIXTURE, selected, package_root=ROOT)
                self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
                self.assertIn("package:workflow/RECOVERY.md", routed.read_set)

    def test_invalid_binding_and_legacy_policy_fail_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            board = project / BOARD
            original = board.read_text()
            board.write_text(original.replace('branch = "feat/sample-workstream"', 'branch = "feat/other"'))
            self.assertEqual(select_route(project, [MANIFEST], package_root=ROOT).disposition, "recovery")

            board.write_text(original.replace("revision = 3", 'revision = 3\nexecution_policy = "chatgpt_only"'))
            self.assertEqual(select_route(project, [MANIFEST], package_root=ROOT).disposition, "recovery")
        finally:
            temp.cleanup()

    def test_missing_cross_workstream_and_escape_locators_fail_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            workstream = project / MANIFEST
            original = workstream.read_text()
            workstream.write_text(original.replace(
                "implementation/workstreams/sample-workstream/TASK_BOARD.toml",
                "implementation/workstreams/other/TASK_BOARD.toml",
            ))
            self.assertEqual(select_route(project, [MANIFEST], package_root=ROOT).disposition, "recovery")
            self.assertEqual(select_route(project, ["../outside.toml"], package_root=ROOT).disposition, "recovery")
        finally:
            temp.cleanup()

    def test_future_lifecycle_is_identified_but_not_implemented(self) -> None:
        routed = select_route(FIXTURE, [MANIFEST], package_root=ROOT)
        self.assertEqual(routed.disposition, "unavailable")
        self.assertIn("not implemented until M03", routed.reason)
        self.assertNotEqual(routed.disposition, "real_stop")

    def test_priority_and_real_stop_foundations_are_runtime_neutral(self) -> None:
        self.assertEqual(
            PRIORITY_FOUNDATION,
            (
                "explicit_human_or_premium_boundary",
                "independent_review_or_red_correction",
                "research_return",
                "result_reconciliation",
                "current_card",
                "next_legal_stage",
            ),
        )
        self.assertIn("premium_gate", REAL_STOP_FOUNDATION)
        self.assertIn("independence_boundary", REAL_STOP_FOUNDATION)
        combined = " ".join(PRIORITY_FOUNDATION + REAL_STOP_FOUNDATION)
        for forbidden in ("chatgpt", "codex", "model_id", "session_id", "worker_id"):
            self.assertNotIn(forbidden, combined)


if __name__ == "__main__":
    unittest.main()
