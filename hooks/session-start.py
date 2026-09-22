#!/usr/bin/env python3
"""Bounded Project Workflow V2 M01 SessionStart bootstrap."""

from __future__ import annotations

import json
import os
from pathlib import Path

MAX_CONTEXT_CHARS = 900
SESSION_PROBE = "PWV2_M01_SESSION_SENTINEL_4D2A"


def plugin_root() -> Path:
    configured = os.environ.get("PLUGIN_ROOT")
    if configured:
        return Path(configured).expanduser().resolve()
    return Path(__file__).resolve().parents[1]


def build_context(root: Path) -> str:
    router = root / "workflow" / "ROUTER.md"
    if router.is_file():
        context = (
            "Project Workflow V2 package is enabled for this workspace. "
            f"M01 session probe token: {SESSION_PROBE}. "
            f"Canonical router: {router}. "
            "Read only the canonical V2 router and exact durable project state required by the current obligation. "
            "This SessionStart message is bootstrap context, not workflow policy."
        )
    else:
        context = (
            "Project Workflow V2 package is enabled, but the canonical router is missing at "
            f"{router}. Treat this as a blocking plugin-package error. "
            "Do not fall back to V1, runtime-specific policy, or reconstructed chat memory."
        )
    return context[:MAX_CONTEXT_CHARS]


def main() -> None:
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": build_context(plugin_root()),
        }
    }
    print(json.dumps(output, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
