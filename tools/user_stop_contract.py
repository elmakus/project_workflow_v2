#!/usr/bin/env python3
"""Observable, runtime-neutral delivery postconditions for established user stops."""
from __future__ import annotations
from dataclasses import dataclass

HANDOFF_NONE = "none"
HANDOFF_OFFERED = "offered"
HANDOFF_REQUIRED = "required"
HANDOFF_POLICIES = {HANDOFF_NONE, HANDOFF_OFFERED, HANDOFF_REQUIRED}
_PREMIUM_POLICIES = {"premium_A": HANDOFF_OFFERED, "premium_B": HANDOFF_REQUIRED, "premium_C": HANDOFF_OFFERED}
_LOCATOR_FIELDS = ("Repository:", "Branch:", "Entry obligation:", "Durable start pointer:")
_PLACEHOLDERS = {"tbd", "todo", "unknown", "unset", "none", "n/a", "na", "placeholder"}

class DeliveryContractError(ValueError):
    pass

def _validate_locator_values(locator: tuple[str, str, str, str]) -> None:
    for value in locator:
        normalized = value.strip()
        if (
            not normalized
            or "<" in normalized
            or ">" in normalized
            or normalized.lower() in _PLACEHOLDERS
        ):
            raise DeliveryContractError("handoff locator contains an unresolved placeholder")

@dataclass(frozen=True)
class DeliveryRequirement:
    established_boundary: bool
    handoff_policy: str = HANDOFF_NONE
    expected_locator: tuple[str, str, str, str] | None = None

    def __post_init__(self) -> None:
        if self.handoff_policy not in HANDOFF_POLICIES:
            raise DeliveryContractError(f"invalid handoff policy {self.handoff_policy!r}")
        if not self.established_boundary and self.handoff_policy != HANDOFF_NONE:
            raise DeliveryContractError("handoff policy cannot create a semantic boundary")
        if self.handoff_policy == HANDOFF_NONE:
            if self.expected_locator is not None:
                raise DeliveryContractError("handoff-free delivery cannot carry an expected locator")
            return
        if self.expected_locator is None:
            raise DeliveryContractError("offered/required handoff needs exact expected locator identity")
        _validate_locator_values(self.expected_locator)

def router_stop_handoff_policy(*, disposition: str, obligation: str) -> str:
    if disposition != "stop":
        return HANDOFF_NONE
    return _PREMIUM_POLICIES.get(obligation, HANDOFF_NONE)

def review_realization_handoff_policy(realization: str) -> str:
    if realization == "fresh_context":
        return HANDOFF_REQUIRED
    if realization in {"current_context", "internal_independent"}:
        return HANDOFF_NONE
    raise DeliveryContractError(f"unknown review realization {realization!r}")

def _extract_exact_locator_prompt(text: str) -> tuple[str, str, str, str] | None:
    lines = text.splitlines()
    markers = [index for index, line in enumerate(lines) if line.strip() == "NEW CHAT START PROMPT"]
    if len(markers) != 1:
        return None
    tail = [line.strip() for line in lines[markers[0] + 1:]]
    while tail and not tail[0]:
        tail.pop(0)
    while tail and not tail[-1]:
        tail.pop()
    if len(tail) != len(_LOCATOR_FIELDS):
        return None
    values: list[str] = []
    for line, prefix in zip(tail, _LOCATOR_FIELDS):
        if not line.startswith(prefix):
            return None
        value = line[len(prefix):].strip()
        values.append(value)
    locator = tuple(values)
    if len(locator) != 4:
        return None
    try:
        _validate_locator_values(locator)
    except DeliveryContractError:
        return None
    return locator  # type: ignore[return-value]

def validate_user_stop_delivery(requirement: DeliveryRequirement, text: str) -> None:
    """Validate delivery only; never infer or manufacture stop legality from prose."""
    if not requirement.established_boundary:
        if requirement.handoff_policy != HANDOFF_NONE:
            raise DeliveryContractError("non-boundary cannot require handoff")
        return
    if requirement.handoff_policy == HANDOFF_NONE:
        return
    locator = _extract_exact_locator_prompt(text)
    if locator is None or locator != requirement.expected_locator:
        raise DeliveryContractError("offered/required fresh-context handoff needs the exact locator-only prompt")
    if requirement.handoff_policy == HANDOFF_REQUIRED and "USER ACTION REQUIRED:" not in text:
        raise DeliveryContractError("required fresh-context handoff needs explicit user action")
