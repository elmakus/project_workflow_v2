#!/usr/bin/env python3
"""Runtime-neutral M03 execution/delegation return contract."""

from __future__ import annotations

from typing import Any

from tools.exact_locator import ExactLocatorError, normalize_locator_path


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
        if normalized in wanted:
            _require(normalized not in fields, f"card_result: duplicate field {key!r}")
            fields[normalized] = value.strip()

    missing = sorted(wanted - set(fields))
    _require(not missing, f"card_result: missing field(s): {', '.join(missing)}")
    for key, value in fields.items():
        _require(value and "<" not in value and ">" not in value,
                 f"card_result: unresolved field {key!r}")

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
    }
