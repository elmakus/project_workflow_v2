#!/usr/bin/env python3
"""Runtime-neutral review-context selection helpers."""

from __future__ import annotations

from tools.user_stop_contract import review_realization_handoff_policy


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


def review_delivery_policy(
    *,
    current_context_produced_subject: bool,
    independent_context_available: bool,
) -> str:
    """Derive delivery policy after Review capability realization."""
    realization = select_review_realization(
        current_context_produced_subject=current_context_produced_subject,
        independent_context_available=independent_context_available,
    )
    return review_realization_handoff_policy(realization)
