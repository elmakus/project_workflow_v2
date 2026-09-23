#!/usr/bin/env python3
"""Thin fail-closed SessionStart bootstrap for the installed Project Workflow V2 package."""

from __future__ import annotations

import json
import os
from pathlib import Path


MAX_CONTEXT_CHARS = 900
ROUTER_HEADER = "# Project Workflow V2 Router"
ROUTER_SELECTOR = "Production selector: `tools/router.py`."


class BootstrapError(RuntimeError):
    """The installed package cannot establish one unambiguous local authority root."""


def installed_root() -> Path:
    script_root = Path(__file__).resolve().parents[1]
    configured = os.environ.get("PLUGIN_ROOT")
    if not configured:
        return script_root

    configured_root = Path(configured).expanduser().resolve()
    if configured_root != script_root:
        raise BootstrapError(
            "configured PLUGIN_ROOT does not match the root containing this SessionStart hook"
        )
    return script_root


def canonical_router(root: Path) -> Path:
    root = root.resolve()
    candidate = root / "workflow" / "ROUTER.md"
    if not candidate.is_file():
        raise BootstrapError(f"canonical bundled router is missing at {candidate}")

    router = candidate.resolve()
    try:
        router.relative_to(root)
    except ValueError as exc:
        raise BootstrapError("canonical router resolves outside the installed package root") from exc

    try:
        text = router.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise BootstrapError("canonical bundled router is unreadable") from exc

    if ROUTER_HEADER not in text or ROUTER_SELECTOR not in text:
        raise BootstrapError("canonical bundled router is malformed or not Project Workflow V2")
    return router


def build_context() -> str:
    try:
        router = canonical_router(installed_root())
        context = (
            "Project Workflow V2 package is enabled. "
            f"Canonical bundled router: {router}. "
            "Read that local router first, then recover only the exact durable consumer-project "
            "state and authority it requests. This SessionStart message is bootstrap context, "
            "not workflow policy. Do not fetch remote workflow policy during ordinary operation."
        )
    except BootstrapError as exc:
        context = (
            f"BLOCKING Project Workflow V2 plugin-package error: {exc}. "
            "Do not fall back to V1, another package/source, runtime-specific policy, "
            "remote workflow policy, or reconstructed chat memory."
        )
    return context[:MAX_CONTEXT_CHARS]


def main() -> None:
    output = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": build_context(),
        }
    }
    print(json.dumps(output, ensure_ascii=False, separators=(",", ":")))


if __name__ == "__main__":
    main()
