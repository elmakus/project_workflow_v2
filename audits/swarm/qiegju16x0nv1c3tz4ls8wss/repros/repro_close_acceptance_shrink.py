#!/usr/bin/env python3
"""Reproduce acceptance-surface shrink being classified as reusable GREEN."""

from tools.close_contract import RefreshSnapshot, classify_review_coverage

reviewed = RefreshSnapshot(
    target_commit="target-old",
    content_fingerprint="same-content",
    behavior_fingerprint="same-behavior",
    acceptance=frozenset({"required-A", "required-B", "removed-required-C"}),
)
current = RefreshSnapshot(
    target_commit="target-new",
    content_fingerprint="same-content",
    behavior_fingerprint="same-behavior",
    acceptance=frozenset({"required-A", "required-B"}),
)

action = classify_review_coverage(
    reviewed,
    current,
    affected_compatibility_green=True,
)
print("acceptance_changed", reviewed.acceptance != current.acceptance)
print("action", action)
assert reviewed.acceptance != current.acceptance
assert action == "reuse_green_review"
