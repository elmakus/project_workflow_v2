#!/usr/bin/env python3
"""Thin fail-closed SessionStart bootstrap for the installed Project Workflow V2 package."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path


MAX_CONTEXT_CHARS = 900
MAX_MANIFEST_BYTES = 4096
MANIFEST_VERSION = 1
MANIFEST_ROUTER = "workflow/ROUTER.md"


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


def _inside_root(root: Path, candidate: Path, label: str) -> Path:
    resolved = candidate.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise BootstrapError(f"{label} resolves outside the installed package root") from exc
    return resolved


def expected_router_blob(root: Path) -> str:
    candidate = root / ".codex-plugin" / "router-integrity.json"
    if not candidate.is_file():
        raise BootstrapError(f"canonical router integrity manifest is missing at {candidate}")

    manifest = _inside_root(
        root, candidate, "canonical router integrity manifest"
    )
    try:
        raw = manifest.read_bytes()
    except OSError as exc:
        raise BootstrapError("canonical router integrity manifest is unreadable") from exc
    if len(raw) > MAX_MANIFEST_BYTES:
        raise BootstrapError("canonical router integrity manifest is malformed")
    try:
        data = json.loads(raw.decode("utf-8"))
    except (ValueError, UnicodeError) as exc:
        raise BootstrapError("canonical router integrity manifest is malformed") from exc

    if (
        not isinstance(data, dict)
        or set(data) != {"version", "router", "git_blob_sha1"}
        or type(data["version"]) is not int
        or data["version"] != MANIFEST_VERSION
        or data["router"] != MANIFEST_ROUTER
        or not isinstance(data["git_blob_sha1"], str)
        or len(data["git_blob_sha1"]) != 40
    ):
        raise BootstrapError("canonical router integrity manifest is malformed")
    blob = data["git_blob_sha1"]
    if any(c not in "0123456789abcdef" for c in blob):
        raise BootstrapError("canonical router integrity manifest is malformed")
    return blob


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob %d\x00" % len(data) + data).hexdigest()


def canonical_router(root: Path) -> Path:
    root = root.resolve()
    candidate = root / "workflow" / "ROUTER.md"
    if not candidate.is_file():
        raise BootstrapError(f"canonical bundled router is missing at {candidate}")

    router = _inside_root(root, candidate, "canonical router")

    try:
        data = router.read_bytes()
    except OSError as exc:
        raise BootstrapError("canonical bundled router is unreadable") from exc
    try:
        data.decode("utf-8")
    except UnicodeError as exc:
        raise BootstrapError("canonical bundled router is unreadable") from exc

    expected = expected_router_blob(root)
    if git_blob_sha1(data) != expected:
        raise BootstrapError(
            "canonical bundled router failed integrity verification against the shipped package manifest"
        )
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
