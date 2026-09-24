#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
with tempfile.TemporaryDirectory() as tmp:
    pw = Path(tmp) / "pw"
    (pw / "hooks").mkdir(parents=True)
    (pw / "workflow").mkdir(parents=True)
    shutil.copy2(ROOT / "hooks" / "session-start.py", pw / "hooks" / "session-start.py")
    (pw / "workflow" / "ROUTER.md").write_text(
        "# Project Workflow V2 Router\n\nProduction selector: `tools/router.py`.\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["PLUGIN_ROOT"] = str(pw)
    proc = subprocess.run(
        ["python3", str(pw / "hooks" / "session-start.py")],
        text=True, capture_output=True, check=True, env=env,
    )
    context = json.loads(proc.stdout)["hookSpecificOutput"]["additionalContext"]
    print(context)
    # Bug: semantically empty router passes the two-sentinel validity check.
    assert "BLOCKING Project Workflow V2 plugin-package error" not in context
    assert "Project Workflow V2 package is enabled." in context
