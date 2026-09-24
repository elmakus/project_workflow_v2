#!/usr/bin/env python3
"""Runtime-neutral review-context and review-pass semantic helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping


REVIEW_KINDS = frozenset({"discovery", "closure_verification"})
CAUSAL_SCOPE_KEYS = (
    "known_findings",
    "defect_classes",
    "root_cause_evidence",
    "repair_diff",
    "regression_evidence",
    "reachable_callers",
    "consumers",
    "providers",
    "contracts",
    "sibling_representations",
    "negative_space",
)


class ReviewContractError(ValueError):
    """Raised when review-pass semantic evidence is incomplete or contradictory."""


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


def review_kind(attempt: Mapping[str, object]) -> str:
    """Return explicit PWv2.1 review kind, treating historical attempts as discovery."""
    kind = attempt.get("review_kind", "discovery")
    if kind not in REVIEW_KINDS:
        raise ReviewContractError(f"unsupported review kind {kind!r}")
    return str(kind)


def validate_discovery_surface(
    *,
    applicable_acceptance: Iterable[str],
    evaluated_acceptance: Iterable[str],
    stopped_at_first_blocker: bool,
) -> frozenset[str]:
    """Require a discovery pass to cover the complete applicable acceptance surface."""
    applicable = frozenset(item for item in applicable_acceptance if item)
    evaluated = frozenset(item for item in evaluated_acceptance if item)
    if stopped_at_first_blocker:
        raise ReviewContractError("fresh discovery cannot stop at the first blocker")
    missing = applicable - evaluated
    if missing:
        raise ReviewContractError(
            "fresh discovery omitted applicable acceptance: " + ", ".join(sorted(missing))
        )
    return evaluated


def required_closure_scope(scope: Mapping[str, Iterable[str]]) -> frozenset[str]:
    """Build the complete materially implicated closure surface.

    Every causal category must be explicitly accounted for. Categories may be
    empty when no material member exists, while known findings, repair diff and
    regression evidence must each contain at least one concrete item.
    """
    missing_keys = [key for key in CAUSAL_SCOPE_KEYS if key not in scope]
    if missing_keys:
        raise ReviewContractError(
            "closure scope omitted causal categories: " + ", ".join(missing_keys)
        )

    normalized: dict[str, frozenset[str]] = {}
    for key in CAUSAL_SCOPE_KEYS:
        raw = scope[key]
        if isinstance(raw, (str, bytes)):
            raise ReviewContractError(f"closure scope {key!r} must be an iterable of concrete items")
        values = frozenset(item for item in raw if isinstance(item, str) and item)
        normalized[key] = values

    for key in (
        "known_findings",
        "defect_classes",
        "root_cause_evidence",
        "repair_diff",
        "regression_evidence",
    ):
        if not normalized[key]:
            raise ReviewContractError(f"closure scope {key!r} must not be empty")

    required: set[str] = set()
    for values in normalized.values():
        required.update(values)
    return frozenset(required)


def validate_closure_surface(
    *,
    scope: Mapping[str, Iterable[str]],
    evaluated_surface: Iterable[str],
) -> frozenset[str]:
    """Require closure verification to cover the known finding and causal blast radius."""
    required = required_closure_scope(scope)
    evaluated = frozenset(item for item in evaluated_surface if item)
    missing = required - evaluated
    if missing:
        raise ReviewContractError(
            "closure verification omitted materially implicated surface: "
            + ", ".join(sorted(missing))
        )
    return evaluated


def remaining_closure_findings(
    attempts: Iterable[Mapping[str, object]],
    source_discovery_attempt: str,
) -> frozenset[str]:
    """Return source-discovery findings not yet covered by GREEN closure attempts."""
    source_findings: set[str] | None = None
    closed: set[str] = set()

    for attempt in attempts:
        if attempt.get("attempt") == source_discovery_attempt:
            if review_kind(attempt) != "discovery" or attempt.get("verdict") != "red":
                raise ReviewContractError("closure source must be a RED discovery attempt")
            raw = attempt.get("material_finding_ids")
            if not isinstance(raw, list) or not all(
                isinstance(item, str) and item for item in raw
            ):
                raise ReviewContractError(
                    "closure source discovery must record material_finding_ids"
                )
            source_findings = set(raw)
            continue

        if source_findings is None:
            continue
        if (
            attempt.get("review_kind") == "closure_verification"
            and attempt.get("source_discovery_attempt") == source_discovery_attempt
            and attempt.get("verdict") == "green"
        ):
            raw = attempt.get("material_finding_ids")
            if not isinstance(raw, list) or not all(
                isinstance(item, str) and item for item in raw
            ):
                raise ReviewContractError(
                    "GREEN closure attempt must record material_finding_ids"
                )
            closed.update(raw)

    if source_findings is None:
        raise ReviewContractError("closure source discovery attempt was not found")
    return frozenset(source_findings - closed)


def can_finalize_review_obligation(attempt: Mapping[str, object]) -> bool:
    """Only a GREEN fresh discovery pass may satisfy the review obligation.

    A GREEN closure pass proves known-finding closure but intentionally requires
    a subsequent fresh full-scope discovery pass.
    """
    return attempt.get("verdict") == "green" and review_kind(attempt) == "discovery"
