#!/usr/bin/env python3
"""Runtime-neutral review-context selection helpers."""

from __future__ import annotations


def select_review_realization(
    *,
    current_context_produced_subject: bool,
    independent_context_available: bool,
) -> str:
    """Choose transient review realization without persisting runtime identity."""
    if not current_context_produced_subject:
        return "current_context"
    if independent_context_available:
        return "internal_independent"
    return "fresh_context"
