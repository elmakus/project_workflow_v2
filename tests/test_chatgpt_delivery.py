from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROJECT_INSTRUCTIONS = ROOT / "prompts" / "CHATGPT_PROJECT_INSTRUCTIONS.md"
FRESH_SESSION = ROOT / "prompts" / "CHATGPT_FRESH_SESSION.md"
USER_STOP = ROOT / "workflow" / "USER_STOP.md"
ROUTER = ROOT / "workflow" / "ROUTER.md"


class ChatGPTDeliveryTests(unittest.TestCase):
    def test_project_instructions_are_thin_repository_router_bootstrap(self) -> None:
        text = PROJECT_INSTRUCTIONS.read_text(encoding="utf-8")
        self.assertIn("elmakus/project_workflow_v2", text)
        self.assertIn("workflow/ROUTER.md", text)
        self.assertIn("<owner/repository>", text)
        self.assertIn("bootstrap locator", text)
        self.assertNotIn("review_state:", text)
        self.assertNotIn("execution_policy:", text)
        self.assertNotIn("active_execution", text)
        self.assertNotIn("Context Health", text)

    def test_fresh_session_template_is_locator_only(self) -> None:
        lines = FRESH_SESSION.read_text(encoding="utf-8").splitlines()
        self.assertEqual(
            lines,
            [
                "Repository: <owner/repository>",
                "Branch: <exact-branch>",
                "Entry obligation: <route-or-obligation>",
                "Durable start pointer: <repository-relative-path>",
            ],
        )

    def test_user_stop_owns_real_stop_format_without_context_health_lifecycle(self) -> None:
        text = USER_STOP.read_text(encoding="utf-8")
        self.assertIn("USER ACTION REQUIRED:", text)
        self.assertIn("NEW CHAT START PROMPT", text)
        self.assertIn("prompts/CHATGPT_FRESH_SESSION.md", text)
        self.assertIn("there is no Project Workflow Context Health/FRESH lifecycle", text)
        self.assertIn("consumer repository", text)
        self.assertNotIn("review evidence:", text.lower())

    def test_router_points_to_canonical_user_stop_module(self) -> None:
        text = ROUTER.read_text(encoding="utf-8")
        self.assertIn("workflow/USER_STOP.md", text)


if __name__ == "__main__":
    unittest.main()
