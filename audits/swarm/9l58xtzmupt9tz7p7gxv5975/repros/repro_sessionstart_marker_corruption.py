#!/usr/bin/env python3
"""Reproduce marker-preserving malformed-router acceptance by SessionStart.

Run from an exact checkout of:
4fb4bfb7d7b1481d6f347c182fc96a5a1135e045

Only a TemporaryDirectory package copy is modified.
"""

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[4]
HOOK = ROOT / "hooks" / "session-start.py"


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        package = Path(tmp) / "pw"
        (package / "hooks").mkdir(parents=True)
        (package / "workflow").mkdir(parents=True)
        shutil.copy2(HOOK, package / "hooks" / "session-start.py")

        # Deliberately malformed/truncated router that preserves only the two
        # sentinel substrings checked by canonical_router().
        (package / "workflow" / "ROUTER.md").write_text(
            "# Project Workflow V2 Router\n\n"
            "CORRUPTED/TRUNCATED POLICY BODY\n\n"
            "Production selector: `tools/router.py`.\n",
            encoding="utf-8",
        )

        env = os.environ.copy()
        env["PLUGIN_ROOT"] = str(package)
        proc = subprocess.run(
            [sys.executable, str(package / "hooks" / "session-start.py")],
            text=True,
            capture_output=True,
            check=True,
            env=env,
        )
        payload = json.loads(proc.stdout)
        context = payload["hookSpecificOutput"]["additionalContext"]
        print(context)
        assert "BLOCKING Project Workflow V2 plugin-package error" not in context
        assert "Project Workflow V2 package is enabled" in context


if __name__ == "__main__":
    main()
