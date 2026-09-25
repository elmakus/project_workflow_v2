#!/usr/bin/env python3
"""Runtime-neutral YAGNI-bounded Worker scope discipline (BOOT-D, REQ-132).

The accepted Card outcome is the binding boundary for Worker implementation
and any post-GREEN refactor. Speculative functionality, premature
abstraction/future-proofing and adjacent scope outside the Card are
forbidden; a genuine accepted need remains allowed. After GREEN local
evidence, bounded in-scope refactoring is permitted only with renewed GREEN
verification of the same local check, distinct renewed evidence, no new
product/architecture scope and no concealed change. DRY is guidance rather
than an absolute mandate: local duplication may remain when abstraction
would increase coupling, risk or scope.

A record binds one Card, one accepted-scope boundary, at least one
classified scope item and at most one disclosed post-GREEN refactor.
Forbidden kinds fail closed even when an authority flag is claimed; such
work must be reclassified as a genuine accepted need with real Card
authority, which Main owns. Provider, model, worker, session, retry,
worktree, Paseo, scheduler, invocation and runtime identity are
non-canonical and rejected as fields, matching the typed
obligation/result boundary and the REQ-131 evidence contract.

This MUST-level execution discipline constrains Worker scope inside an
already-authorized Card. It creates no new Card, Milestone or premium gate,
no runtime worker catalog, no fixed size/LOC/time category and no scheduler
semantics. Historical Card results without a Worker scope record remain
valid; absence means legacy-compatible, never retrospective scope proof.
Out of scope here: REQ-131 falsification-first chronology itself (separate
already-GREEN contract), M03 and historical M02 rewrites.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

CARD_ID = re.compile(r"^[A-Za-z0-9]+(?:-[A-Za-z0-9]+)+$")

ITEM_KINDS = frozenset({
    "accepted_need",
    "speculative_functionality",
    "future_proofing_abstraction",
    "adjacent_scope",
    "dry_abstraction",
})
FORBIDDEN_KINDS = frozenset({
    "speculative_functionality",
    "future_proofing_abstraction",
    "adjacent_scope",
})
DRY_RESOLUTIONS = frozenset({"abstract", "keep_duplication"})

TELEMETRY_KEY_ROOTS = (
    "provider", "model", "worker", "session", "retry", "retries",
    "worktree", "paseo", "runtime", "invocation", "scheduler",
)

GENERIC_SCOPE_CLAIMS = frozenset({
    "red", "green", "fail", "pass", "failing", "passing",
    "tests fail", "tests pass", "test fails", "test passes",
    "it fails", "it passes", "broken", "works", "failing check",
    "passing check", "red baseline", "green verification",
    "yagni", "in scope", "out of scope", "in-scope", "in scope!",
    "n/a", "na", "none", "tbd", "todo",
})

MIN_SCOPE_LEN = 8
MIN_ITEM_LEN = 8
MIN_SUMMARY_LEN = 8
MIN_CHECK_LEN = 8
MIN_EVIDENCE_LEN = 8


class WorkerScopeError(ValueError):
    """Raised when Worker YAGNI-bounded scope evidence is invalid."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise WorkerScopeError(message)


def _reject_telemetry_keys(value: Any, where: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).lower()
            _require(
                not normalized.startswith(TELEMETRY_KEY_ROOTS),
                f"{where}: telemetry key {key!r} is non-canonical",
            )
            _reject_telemetry_keys(child, f"{where}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_telemetry_keys(child, f"{where}[{index}]")


def _normalize_generic_candidate(text: str) -> str:
    collapsed = " ".join(text.strip().lower().split())
    return collapsed.strip(".,!?:;'\"()[]")


def _is_generic_claim(text: str) -> bool:
    return _normalize_generic_candidate(text) in GENERIC_SCOPE_CLAIMS


def _require_specific_text(value: Any, label: str, min_len: int) -> str:
    _require(isinstance(value, str) and value.strip(), f"{label} must be a non-empty string")
    text = value.strip()
    _require(len(text) >= min_len, f"{label} must carry a specific falsifiable statement")
    _require("<" not in text and ">" not in text, f"{label} must not carry a placeholder")
    _require(not _is_generic_claim(text), f"{label} must not be a generic claim")
    return value if isinstance(value, str) else text


def _require_boolean(value: Any, label: str) -> bool:
    _require(isinstance(value, bool), f"{label} must be a boolean")
    return value


def _validate_item(item: Any, label: str) -> dict[str, Any]:
    _require(isinstance(item, Mapping), f"{label} must be an object")
    _require("kind" in item, f"{label}: invalid keys")
    kind = item["kind"]
    _require(kind in ITEM_KINDS, f"{label}.kind must be one of {sorted(ITEM_KINDS)}")
    if kind == "dry_abstraction":
        _require(
            set(item) == {
                "description", "kind", "accepted_authority",
                "adds_coupling_or_risk", "resolution",
            },
            f"{label}: invalid keys",
        )
    else:
        _require(
            set(item) == {"description", "kind", "accepted_authority"},
            f"{label}: invalid keys",
        )
    description = _require_specific_text(item["description"], f"{label}.description", MIN_ITEM_LEN)
    accepted_authority = _require_boolean(item["accepted_authority"], f"{label}.accepted_authority")
    if kind in FORBIDDEN_KINDS:
        raise WorkerScopeError(
            f"{label}: {kind} is forbidden outside accepted Card authority; "
            "reclassify as a genuine accepted_need only with real Card authority"
        )
    if kind == "accepted_need":
        _require(
            accepted_authority is True,
            f"{label}: accepted_need requires genuine accepted authority",
        )
        return {"description": description, "kind": kind, "accepted_authority": True}
    adds_coupling_or_risk = _require_boolean(
        item["adds_coupling_or_risk"], f"{label}.adds_coupling_or_risk"
    )
    resolution = item["resolution"]
    _require(
        resolution in DRY_RESOLUTIONS,
        f"{label}.resolution must be one of {sorted(DRY_RESOLUTIONS)}",
    )
    if adds_coupling_or_risk:
        _require(
            resolution == "keep_duplication",
            f"{label}: DRY cannot force abstraction when it adds coupling, risk or scope",
        )
    if resolution == "abstract":
        _require(
            accepted_authority is True,
            f"{label}: dry_abstraction requires genuine accepted authority",
        )
        _require(
            adds_coupling_or_risk is False,
            f"{label}: DRY cannot force abstraction when it adds coupling, risk or scope",
        )
    return {
        "description": description,
        "kind": kind,
        "accepted_authority": accepted_authority,
        "adds_coupling_or_risk": adds_coupling_or_risk,
        "resolution": resolution,
    }


def _validate_refactor(refactor: Any, label: str) -> dict[str, Any]:
    _require(isinstance(refactor, Mapping), f"{label} must be an object")
    _require(
        set(refactor) == {
            "summary", "adds_new_scope", "disclosed",
            "local_green_check", "local_green_evidence",
            "renewed_check", "renewed_evidence",
        },
        f"{label}: invalid keys",
    )
    summary = _require_specific_text(refactor["summary"], f"{label}.summary", MIN_SUMMARY_LEN)
    adds_new_scope = _require_boolean(refactor["adds_new_scope"], f"{label}.adds_new_scope")
    _require(
        adds_new_scope is False,
        f"{label}: post-GREEN refactor must not add new scope",
    )
    disclosed = _require_boolean(refactor["disclosed"], f"{label}.disclosed")
    _require(
        disclosed is True,
        f"{label}: post-GREEN refactor must be disclosed, never concealed",
    )
    local_check = _require_specific_text(
        refactor["local_green_check"], f"{label}.local_green_check", MIN_CHECK_LEN
    )
    renewed_check = _require_specific_text(
        refactor["renewed_check"], f"{label}.renewed_check", MIN_CHECK_LEN
    )
    _require(
        renewed_check.strip() == local_check.strip(),
        f"{label}: renewed verification must repeat the same local GREEN check",
    )
    local_evidence = _require_specific_text(
        refactor["local_green_evidence"], f"{label}.local_green_evidence", MIN_EVIDENCE_LEN
    )
    renewed_evidence = _require_specific_text(
        refactor["renewed_evidence"], f"{label}.renewed_evidence", MIN_EVIDENCE_LEN
    )
    _require(
        renewed_evidence.strip() != local_evidence.strip(),
        f"{label}: renewed verification requires distinct renewed evidence",
    )
    return {
        "summary": summary,
        "adds_new_scope": False,
        "disclosed": True,
        "local_green_check": local_check,
        "local_green_evidence": local_evidence,
        "renewed_check": renewed_check,
        "renewed_evidence": renewed_evidence,
    }


def validate_worker_scope(record: Mapping[str, Any], label: str = "worker_scope") -> dict[str, Any]:
    """Validate one YAGNI-bounded Worker scope record.

    The record proves every implemented item stays within the Card's
    accepted scope boundary and that any post-GREEN refactor is bounded,
    disclosed and re-verified. Anything else fails closed.
    """
    _require(isinstance(record, Mapping), f"{label} must be an object")
    _reject_telemetry_keys(record, label)
    expected = {"card_id", "accepted_scope", "items", "post_green_refactor"}
    _require(set(record) == expected, f"{label}: invalid top-level keys")

    card_id = record["card_id"]
    _require(
        isinstance(card_id, str) and CARD_ID.fullmatch(card_id) is not None,
        f"{label}.card_id must be a concrete Card id",
    )
    accepted_scope = _require_specific_text(
        record["accepted_scope"], f"{label}.accepted_scope", MIN_SCOPE_LEN
    )

    items = record["items"]
    _require(isinstance(items, list) and len(items) >= 1, f"{label}.items must carry at least one scope item")
    normalized_items = [
        _validate_item(item, f"{label}.items[{index}]") for index, item in enumerate(items)
    ]

    refactor = record["post_green_refactor"]
    if refactor is None:
        normalized_refactor = None
    else:
        normalized_refactor = _validate_refactor(refactor, f"{label}.post_green_refactor")

    return {
        "card_id": card_id,
        "accepted_scope": accepted_scope,
        "items": normalized_items,
        "post_green_refactor": normalized_refactor,
    }


def scope_status(
    worker_scope: Mapping[str, Any] | None,
    *,
    expected_card_id: str | None = None,
    label: str = "worker_scope",
) -> str:
    """Return the lifecycle status of optional Worker scope evidence.

    Absence is legacy-compatible: historical valid results without a Worker
    scope record remain valid and never become retrospective scope claims.
    Presence is validated strictly and must bind the expected Card when one
    is supplied, including the Card bound by the REQ-131 evidence record.
    """
    if worker_scope is None:
        return "legacy_compatible"
    normalized = validate_worker_scope(worker_scope, label)
    if expected_card_id is not None:
        _require(
            normalized["card_id"] == expected_card_id,
            f"{label}.card_id does not match the active Card",
        )
    return "in_scope_green"
