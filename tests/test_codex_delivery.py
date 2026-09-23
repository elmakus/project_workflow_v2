from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / ".codex-plugin" / "plugin.json"
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
SKILL = ROOT / "skills" / "project_workflow_v2" / "SKILL.md"
HOOKS = ROOT / "hooks" / "hooks.json"
SESSION_START = ROOT / "hooks" / "session-start.py"
ROUTER = ROOT / "workflow" / "ROUTER.md"


class CodexDeliveryTests(unittest.TestCase):
    def test_package_identity_and_single_local_pw_source(self) -> None:
        plugin = json.loads(PLUGIN.read_text(encoding="utf-8"))
        marketplace = json.loads(MARKETPLACE.read_text(encoding="utf-8"))

        self.assertEqual(plugin["name"], "pw")
        self.assertEqual(plugin["version"], "0.2.0")
        self.assertEqual(plugin["skills"], "./skills/")
        self.assertEqual(marketplace["name"], "project-workflow-v2")

        entries = marketplace["plugins"]
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["name"], "pw")
        self.assertEqual(entries[0]["source"], {"source": "local", "path": "."})
        self.assertEqual(
            [p.relative_to(ROOT).as_posix() for p in ROOT.rglob("plugin.json")],
            [".codex-plugin/plugin.json"],
        )

    def test_skill_is_thin_local_bootstrap(self) -> None:
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("name: project_workflow_v2", text)
        self.assertIn("$pw:project_workflow_v2", text)
        self.assertIn("<plugin-root>/workflow/ROUTER.md", text)
        self.assertIn("fail closed", text)
        self.assertIn("Do not fetch remote workflow policy", text)
        self.assertNotIn("review_state:", text)
        self.assertNotIn("execution_status:", text)
        self.assertNotIn("premium_stop_", text)
        self.assertLess(len(text), 1800)

        self.assertFalse((ROOT / "skills" / "project_workflow_v2" / "workflow").exists())
        self.assertFalse((ROOT / "skills" / "project_workflow_v2" / "references").exists())

    def test_canonical_workflow_is_byte_preserving_package_payload(self) -> None:
        def digest_tree(root: Path) -> dict[str, str]:
            return {
                path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(root.rglob("*"))
                if path.is_file()
            }

        source = ROOT / "workflow"
        with tempfile.TemporaryDirectory() as tmp:
            installed = Path(tmp) / "installed-workflow"
            shutil.copytree(source, installed)
            self.assertEqual(digest_tree(source), digest_tree(installed))

    def test_session_start_read_set_is_router_only(self) -> None:
        text = SESSION_START.read_text(encoding="utf-8")
        self.assertIn('root / "workflow" / "ROUTER.md"', text)
        self.assertNotIn(".glob(", text)
        self.assertNotIn(".rglob(", text)
        self.assertNotIn("PROJECT.md", text)
        for module in (ROOT / "workflow").glob("*.md"):
            if module.name != "ROUTER.md":
                self.assertNotIn(module.name, text)

    def test_hook_manifest_is_bounded_local_command(self) -> None:
        manifest = json.loads(HOOKS.read_text(encoding="utf-8"))
        hooks = manifest["hooks"]["SessionStart"]
        self.assertEqual(len(hooks), 1)
        commands = hooks[0]["hooks"]
        self.assertEqual(
            commands,
            [{"type": "command", "command": 'python3 "$PLUGIN_ROOT/hooks/session-start.py"'}],
        )
        command = commands[0]["command"]
        for forbidden in ("curl ", "wget ", "http://", "https://"):
            self.assertNotIn(forbidden, command)

    def _copy_package(self, destination: Path) -> Path:
        (destination / "hooks").mkdir(parents=True)
        (destination / "workflow").mkdir(parents=True)
        shutil.copy2(SESSION_START, destination / "hooks" / "session-start.py")
        shutil.copy2(ROUTER, destination / "workflow" / "ROUTER.md")
        return destination / "hooks" / "session-start.py"

    def _run_hook(self, script: Path, root: Path, source: str = "startup") -> str:
        env = os.environ.copy()
        env["PLUGIN_ROOT"] = str(root)
        proc = subprocess.run(
            ["python3", str(script)],
            input=json.dumps({"source": source}),
            text=True,
            capture_output=True,
            env=env,
            check=True,
        )
        payload = json.loads(proc.stdout)
        return payload["hookSpecificOutput"]["additionalContext"]

    def test_startup_resume_and_compaction_share_same_thin_local_bootstrap(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pw"
            script = self._copy_package(root)
            contexts = [self._run_hook(script, root, source) for source in ("startup", "resume", "compaction")]

        self.assertEqual(contexts[0], contexts[1])
        self.assertEqual(contexts[1], contexts[2])
        self.assertIn("Canonical bundled router:", contexts[0])
        self.assertIn("local router first", contexts[0])
        self.assertIn("not workflow policy", contexts[0])
        self.assertLessEqual(len(contexts[0]), 900)

    def test_missing_and_malformed_router_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "pw"
            script = self._copy_package(root)
            (root / "workflow" / "ROUTER.md").unlink()
            missing = self._run_hook(script, root)

            (root / "workflow" / "ROUTER.md").write_text("not a V2 router\n", encoding="utf-8")
            malformed = self._run_hook(script, root)

        for context in (missing, malformed):
            self.assertIn("BLOCKING Project Workflow V2 plugin-package error", context)
            self.assertIn("Do not fall back to V1", context)

    def test_router_path_escape_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "pw"
            script = self._copy_package(root)
            outside = base / "outside-router.md"
            shutil.copy2(ROUTER, outside)
            (root / "workflow" / "ROUTER.md").unlink()
            (root / "workflow" / "ROUTER.md").symlink_to(outside)

            context = self._run_hook(script, root)

        self.assertIn("resolves outside the installed package root", context)

    def test_plugin_root_source_mismatch_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            actual_root = Path(tmp) / "actual"
            script = self._copy_package(actual_root)
            other_root = Path(tmp) / "other"
            self._copy_package(other_root)

            context = self._run_hook(script, other_root)

        self.assertIn("configured PLUGIN_ROOT does not match", context)
        self.assertIn("BLOCKING Project Workflow V2 plugin-package error", context)


if __name__ == "__main__":
    unittest.main()
