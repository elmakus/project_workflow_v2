#!/usr/bin/env python3
"""Minimal non-mutating repro for PWv2 audit F1 at 4fb4bfb7d7b1481d6f347c182fc96a5a1135e045.

The production refresh algorithm compares the Card dependency tuple to the DONE
predecessor tuple and then only reads the path. This script demonstrates that
metadata equality does not prove the file is the declared Git blob.
"""
from hashlib import sha1

declared_blob = "b" * 40
content = b"MUTATED CONTENT\n"
actual_blob = sha1(b"blob " + str(len(content)).encode() + b"\0" + content).hexdigest()
board_tuple = ("implementation/workstreams/ws/results/M01-T01.md", "a" * 40, declared_blob)
card_tuple = board_tuple
assert card_tuple == board_tuple
assert actual_blob != declared_blob
print({"tuple_check": "accepted", "declared_blob": declared_blob, "actual_blob": actual_blob})
