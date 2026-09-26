#!/usr/bin/env python3
"""Runtime-neutral M03 execution/delegation return contract."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from tools.exact_locator import ExactLocatorError, normalize_locator_path

CARD_RESULT_SUCCESS = "success"
CARD_RESULT_STATUSES = frozenset({"success", "failed", "blocked"})
FAILED_SUMMARY_PREFIX = "FAILED:"


class ExecutionContractError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ExecutionContractError(message)


def choose_realization(
    delegated_capability: bool,
    bounded_context: bool,
    valid_return_path: bool,
) -> str:
    """Return transient runtime realization; never persist this value in PW state."""
    return "delegate" if delegated_capability and bounded_context and valid_return_path else "direct"


def classify_return(*, acceptance_valid: bool, real_blocker: bool) -> str:
    """Classify a returned implementation before Main mutates canonical state."""
    if real_blocker:
        return "block"
    if not acceptance_valid:
        return "correct"
    return "reconcile"


def parse_card_result(text: str, expected_card_id: str, workstream_id: str) -> dict[str, Any]:
    wanted = {
        "card id",
        "implementation subject",
        "evidence refs",
        "tests/readback summary",
    }
    optional_status = "result status"
    forbidden_fragments = ("runtime", "provider", "model", "session", "worker", "invocation")
    fields: dict[str, str] = {}

    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("- ") or ":" not in line:
            continue
        key, value = line[2:].split(":", 1)
        normalized = key.strip().lower()
        _require(
            not any(fragment in normalized for fragment in forbidden_fragments),
            f"card_result: runtime identity field {key!r} is non-canonical",
        )
        if normalized in wanted or normalized == optional_status:
            _require(normalized not in fields, f"card_result: duplicate field {key!r}")
            fields[normalized] = value.strip()

    missing = sorted(wanted - set(fields))
    _require(not missing, f"card_result: missing field(s): {', '.join(missing)}")
    for key, value in fields.items():
        _require(value and "<" not in value and ">" not in value,
                 f"card_result: unresolved field {key!r}")
    if optional_status in fields:
        _require(
            fields[optional_status] in CARD_RESULT_STATUSES,
            f"card_result: invalid result status {fields[optional_status]!r}",
        )

    _require(fields["card id"] == expected_card_id,
             "card_result: Card ID does not match active Card")

    evidence = [part.strip() for part in fields["evidence refs"].split(",") if part.strip()]
    _require(evidence, "card_result: at least one evidence ref is required")
    prefix = f"implementation/workstreams/{workstream_id}/evidence/"
    for index, raw in enumerate(evidence):
        try:
            normalize_locator_path(raw, f"card_result.evidence[{index}]")
        except ExactLocatorError as exc:
            raise ExecutionContractError(
                f"card_result.evidence[{index}]: invalid workstream evidence ref: {exc}"
            ) from exc
        _require(
            raw.startswith(prefix) and raw.endswith(".md"),
            f"card_result.evidence[{index}]: invalid workstream evidence ref",
        )

    return {
        "card_id": expected_card_id,
        "implementation_subject": fields["implementation subject"],
        "evidence_refs": evidence,
        "tests_summary": fields["tests/readback summary"],
        "result_status": fields.get(optional_status),
    }


def _is_failed_summary(summary: Any) -> bool:
    """Return whether a summary carries the exact normative FAILED prefix.

    Fail-closed mismatch only: a stripped summary starting with ``FAILED:``
    (case-insensitive, prefix-only) can never be accepted success. This
    never infers success; GREEN/success substrings still authorize nothing.
    """
    return (
        isinstance(summary, str)
        and summary.strip().upper().startswith(FAILED_SUMMARY_PREFIX)
    )


def is_accepted_success(parsed_result: Mapping[str, Any]) -> bool:
    """Return whether a parsed Card Result is accepted success.

    Only the exact structured ``Result status: success`` value authorizes
    result reconciliation, review, or no-replay recovery, and only when the
    free-text summary does not carry the exact normative ``FAILED:`` prefix.
    A ``success`` status co-edited with a FAILED summary is contradictory
    and fails closed. The summary, evidence presence, and implementation
    subject never authorize by presence, non-emptiness, or substring.
    """
    try:
        return (
            parsed_result.get("result_status") == CARD_RESULT_SUCCESS
            and not _is_failed_summary(parsed_result.get("tests_summary"))
        )
    except AttributeError:
        return False
