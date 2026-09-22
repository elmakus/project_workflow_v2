#!/usr/bin/env python3
"""Thin Project Workflow V2 SessionStart bootstrap."""

from __future__ import annotations

import json
import os
from pathlib import Path

MAX_CONTEXT_CHARS = 700

def plugin_root() -> Path:
    configured = os.environ.get("PLUGIN_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[1]

def build_context(root: Path) -> str:
    router = root / "workflow" / "ROUTER.md"
    if router.is_file():
        text = (
            "Project Workflow V2 is available from the installed pw plugin. "
            f"Read the bundled canonical router at {router}. "
            "Load workflow semantics progressively from that bundled package and recover "
            "project truth from durable repository state. "
            "The $pw:project_workflow_v2 Skill and this SessionStart hook are bootstrap only."
        )
    else:
        text = (
            "Project Workflow V2 plugin bootstrap is present, but its bundled canonical router "
            f"is missing at {router}. Fail closed and do not reconstruct workflow policy."
        )
    return text[:MAX_CONTEXT_CHARS]

def main() -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": build_context(plugin_root()),
        }
    }, ensure_ascii=False, separators=(",", ":")))

if __name__ == "__main__":
    main()
