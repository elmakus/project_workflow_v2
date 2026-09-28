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

class DeliveryContractError(ValueError):
    pass

@dataclass(frozen=True)
class DeliveryRequirement:
    established_boundary: bool
    handoff_policy: str = HANDOFF_NONE
    def __post_init__(self) -> None:
        if self.handoff_policy not in HANDOFF_POLICIES:
            raise DeliveryContractError(f"invalid handoff policy {self.handoff_policy!r}")
        if not self.established_boundary and self.handoff_policy != HANDOFF_NONE:
            raise DeliveryContractError("handoff policy cannot create a semantic boundary")

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

def _has_exact_locator(text: str) -> bool:
    lines = [line.strip() for line in text.splitlines()]
    for start in range(0, len(lines) - len(_LOCATOR_FIELDS) + 1):
        candidate = lines[start:start + len(_LOCATOR_FIELDS)]
        values = []
        for line, prefix in zip(candidate, _LOCATOR_FIELDS):
            if not line.startswith(prefix):
                break
            value = line[len(prefix):].strip()
            if not value or "<" in value or ">" in value:
                break
            values.append(value)
        if len(values) == len(_LOCATOR_FIELDS):
            return True
    return False

def validate_user_stop_delivery(requirement: DeliveryRequirement, text: str) -> None:
    """Validate delivery only; never infer or manufacture stop legality from prose."""
    if not requirement.established_boundary:
        if requirement.handoff_policy != HANDOFF_NONE:
            raise DeliveryContractError("non-boundary cannot require handoff")
        return
    if requirement.handoff_policy == HANDOFF_NONE:
        return
    if "NEW CHAT START PROMPT" not in text or not _has_exact_locator(text):
        raise DeliveryContractError("offered/required fresh-context handoff needs exact locator-only prompt")
    if requirement.handoff_policy == HANDOFF_REQUIRED and "USER ACTION REQUIRED:" not in text:
        raise DeliveryContractError("required fresh-context handoff needs explicit user action")
