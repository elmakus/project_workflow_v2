#!/usr/bin/env python3
"""Minimal non-mutating repro for PWv2 audit F2 at 4fb4bfb7d7b1481d6f347c182fc96a5a1135e045."""
from pathlib import PurePosixPath

workstream_id = "sample-workstream"
raw = "implementation/workstreams/sample-workstream/evidence/DOES-NOT-EXIST.md"
p = PurePosixPath(raw)
prefix = f"implementation/workstreams/{workstream_id}/evidence/"
assert not p.is_absolute()
assert "." not in p.parts and ".." not in p.parts
assert raw.startswith(prefix) and raw.endswith(".md")
print({"parser_shape_check": "accepted", "evidence_ref": raw, "existence_checked": False})
