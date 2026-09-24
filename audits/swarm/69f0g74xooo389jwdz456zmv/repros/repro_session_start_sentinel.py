#!/usr/bin/env python3
"""Non-mutating SessionStart sentinel-preserving malformed-router reproduction (F5)."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SOURCE_HOOK = ROOT / "hooks" / "session-start.py"


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        package = Path(tmp) / "pw"
        (package / "hooks").mkdir(parents=True)
        (package / "workflow").mkdir(parents=True)
        hook = package / "hooks" / "session-start.py"
        shutil.copy2(SOURCE_HOOK, hook)

        # Semantically empty/truncated router preserving exactly the two sentinels
        # accepted by canonical_router().
        (package / "workflow" / "ROUTER.md").write_text(
            "# Project Workflow V2 Router\n\n"
            "Production selector: `tools/router.py`.\n",
            encoding="utf-8",
        )

        env = os.environ.copy()
        env["PLUGIN_ROOT"] = str(package)
        proc = subprocess.run(
            [sys.executable, str(hook)],
            text=True,
            capture_output=True,
            check=True,
            env=env,
        )
        payload = json.loads(proc.stdout)
        context = payload["hookSpecificOutput"]["additionalContext"]

        # Defect: malformed router is accepted as canonical rather than blocking.
        assert "BLOCKING Project Workflow V2 plugin-package error" not in context
        assert "Canonical bundled router:" in context
        print(context)


if __name__ == "__main__":
    main()
