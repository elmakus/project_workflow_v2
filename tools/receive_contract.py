"""Runtime-neutral validation for PWv2 fresh-context locator receipt."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import PurePosixPath

from tools.continuation_contract import classify_route_completion, resume_action


class ReceiveContractError(ValueError):
    """Raised when a locator cannot be safely received."""


@dataclass(frozen=True)
class FreshContextLocator:
    repository: str
    branch: str
    entry_obligation: str
    durable_start_pointer: str


@dataclass(frozen=True)
class ReceiveExpectation:
    repository: str
    branch: str
    entry_obligation: str
    durable_start_pointer: str
    disposition: str
    transferable: bool
    independence_required: bool = False


@dataclass(frozen=True)
class ReceiveDecision:
    action: str
    obligation: str
    reason: str


_FIELDS = (
    ("Repository", "repository"),
    ("Branch", "branch"),
    ("Entry obligation", "entry_obligation"),
    ("Durable start pointer", "durable_start_pointer"),
)


def _clean(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ReceiveContractError(f"missing {field}")
    value = value.strip()
    if any(token in value for token in ("<", ">", "TBD")):
        raise ReceiveContractError(f"placeholder {field}")
    return value


def parse_fresh_context_locator(text: str) -> FreshContextLocator:
    """Parse exactly the four locator fields; narrative is never accepted as authority."""
    if not isinstance(text, str):
        raise ReceiveContractError("locator must be text")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if lines and lines[0] == "NEW CHAT START PROMPT":
        lines = lines[1:]
    if len(lines) != len(_FIELDS):
        raise ReceiveContractError("locator must contain exactly four fields")

    values: dict[str, str] = {}
    for line, (label, key) in zip(lines, _FIELDS, strict=True):
        prefix = f"{label}:"
        if not line.startswith(prefix):
            raise ReceiveContractError(f"expected {label}")
        values[key] = _clean(line[len(prefix):], label)

    pointer = PurePosixPath(values["durable_start_pointer"])
    if pointer.is_absolute() or "." in pointer.parts or ".." in pointer.parts:
        raise ReceiveContractError("unsafe durable start pointer")
    return FreshContextLocator(**values)


def validate_receive(
    locator: FreshContextLocator,
    expected: ReceiveExpectation,
    *,
    receiver_semantically_independent: bool,
) -> ReceiveDecision:
    """Bind untrusted locator assertions to freshly derived canonical expectations."""
    for field in ("repository", "branch", "entry_obligation", "durable_start_pointer"):
        if getattr(locator, field) != getattr(expected, field):
            raise ReceiveContractError(f"locator {field} does not match canonical current binding")

    if expected.disposition != "stop":
        raise ReceiveContractError("locator does not name the exact current handoff boundary")
    if not expected.transferable:
        return ReceiveDecision(
            "remain_stopped",
            expected.entry_obligation,
            "canonical owner state says this genuine stop is not transferable by receipt",
        )
    if expected.independence_required and not receiver_semantically_independent:
        raise ReceiveContractError("receiver is not semantically independent for this exact subject")

    return ReceiveDecision(
        "consume_handoff",
        expected.entry_obligation,
        "exact canonical transferable boundary validated; consume only the handoff/context-selection boundary",
    )


@dataclass(frozen=True)
class ReceiveContinuationDecision:
    receive_action: str
    continuation_action: str
    restart_action: str


def consume_handoff_and_classify(
    locator: FreshContextLocator,
    expected: ReceiveExpectation,
    *,
    receiver_semantically_independent: bool,
    freshly_routed_disposition: str,
    freshly_routed_obligation: str,
    durable_semantic_result: bool = False,
    external_effect_uncertain: bool = False,
) -> ReceiveContinuationDecision:
    """Consume an exact transferable handoff and enter canonical continuation.

    The caller must derive expected and the fresh route from canonical durable
    state. This helper deliberately cannot manufacture either. Receipt is checked
    first, so a duplicate/stale locator after durable advancement fails closed
    before any continuation or replay decision is returned.
    """
    received = validate_receive(
        locator,
        expected,
        receiver_semantically_independent=receiver_semantically_independent,
    )
    if received.action != "consume_handoff":
        return ReceiveContinuationDecision(received.action, "return", "no_replay")

    completion = classify_route_completion(
        disposition=freshly_routed_disposition,
        obligation=freshly_routed_obligation,
    )
    restart = resume_action(
        durable_semantic_result=durable_semantic_result,
        external_effect_uncertain=external_effect_uncertain,
    )
    return ReceiveContinuationDecision(received.action, completion.action, restart)
