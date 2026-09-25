#!/usr/bin/env python3
"""Platform-path reproduction for PWv2 audit F6."""

from pathlib import PurePosixPath
import ntpath

from tools.state_contract import validate_locator

raw = r"implementation/workstreams/sample-workstream/cards/..\..\other/cards/M01-T99.md"

# Production validation is POSIX-token based and raw-prefix based.
parts = PurePosixPath(raw).parts
assert ".." not in parts
assert raw.startswith("implementation/workstreams/sample-workstream/cards/")
validate_locator(
    {"class": "task_card", "path": raw},
    "task_card",
    "audit.task_card",
    "sample-workstream",
)

# Host-native Windows interpretation treats the embedded backslashes as separators.
resolved = ntpath.normpath(ntpath.join(r"C:\repo", raw))
expected = r"C:\repo\implementation\workstreams\other\cards\M01-T99.md"
print("PurePosix parts:", parts)
print("Windows normalized:", resolved)
assert resolved.lower() == expected.lower()
print("F6 vulnerable path accepted by validator and normalizes cross-workstream on Windows")
