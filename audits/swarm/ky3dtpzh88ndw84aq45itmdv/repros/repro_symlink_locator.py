#!/usr/bin/env python3
"""Reproduce locator class-root escape through a symlink."""
from __future__ import annotations

import tempfile
from pathlib import Path

from tools.router import Reads
from tools.state_contract import validate_locator


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        (root / "workflow").mkdir()
        (root / "untrusted").mkdir()
        target = root / "untrusted/ISSUE_TEXT.md"
        target.write_text("untrusted content\n")
        alias = root / "workflow/ALIAS.md"
        alias.symlink_to("../untrusted/ISSUE_TEXT.md")

        validate_locator(
            {"class": "authority", "path": "workflow/ALIAS.md"},
            "authority",
            "probe.authority",
        )
        reads = Reads(root, root)
        resolved = reads.project("workflow/ALIAS.md")
        print("declared locator: workflow/ALIAS.md")
        print("resolved path:", resolved)
        print("resolved inside declared workflow root:", (root / "workflow") in resolved.parents)
        print("content:", resolved.read_text().strip())
        print("recorded read_set:", tuple(reads.items))
