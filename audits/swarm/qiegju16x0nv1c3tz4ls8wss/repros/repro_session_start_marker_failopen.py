#!/usr/bin/env python3
"""Reproduce SessionStart accepting a semantically empty marker-preserving router."""

from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[4]
HOOK = ROOT / "hooks" / "session-start.py"

with tempfile.TemporaryDirectory() as tmp:
    installed = Path(tmp) / "pw"
    (installed / "hooks").mkdir(parents=True)
    (installed / "workflow").mkdir(parents=True)
    shutil.copy2(HOOK, installed / "hooks" / "session-start.py")
    (installed / "workflow" / "ROUTER.md").write_text(
        "# Project Workflow V2 Router\n\n"
        "This router intentionally contains no workflow semantics.\n\n"
        "Production selector: `tools/router.py`.\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["PLUGIN_ROOT"] = str(installed)
    proc = subprocess.run(
        ["python3", str(installed / "hooks" / "session-start.py")],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    payload = json.loads(proc.stdout)
    context = payload["hookSpecificOutput"]["additionalContext"]
    print(context)
    assert context.startswith("Project Workflow V2 package is enabled.")
    assert "BLOCKING Project Workflow V2 plugin-package error" not in context
