#!/usr/bin/env python3
"""RF014 JIT lifecycle terminality and exact consumed proof (H026).

Pending/satisfied JIT obligations participate in terminal completeness: an
all-DONE Board with a waiting/satisfied ordinary trigger cannot Close. A
consumed trigger must bind exact downstream materialization/consumer proof —
the downstream Card id plus its Task Card contract path with exact Git
commit/blob identity — verified through the RF007 resolver, causally bound
to this trigger: the downstream materializes after its predecessor on the
Board and either is the bound late-oversize residual Card, is recorded in a
durable trigger resolution, or declares the exact predecessor result as a
Task Card dependency. An unrelated later Card with valid identity is not
proof. Prose-only, caller-attested, path-only or mismatched bindings fail
closed.

Historic compatibility (REQ-125): prose-only consumed triggers stay
shape-valid in :func:`tools.state_contract.validate_board` so correctly
terminal M01/M02/M02R history and non-terminal Boards validate unchanged.
Presence plus Git identity plus the consumer edge is enforced at the
terminality serving boundary (router Close gate and Close verification)
where proof is required. Boards that reach terminality with
missing/dangling/stale/sibling/unproved/forged proof fail closed with an
exact reason; migration is append-only proof addition, never history
rewrite.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

try:
    from tools.exact_locator import (
        ExactLocatorError,
        normalize_locator_path,
        verify_exact_git_locator,
        verify_worktree_freshness,
    )
except ModuleNotFoundError:  # direct script execution from tools/
    from exact_locator import (
        ExactLocatorError,
        normalize_locator_path,
        verify_exact_git_locator,
        verify_worktree_freshness,
    )

_SHA40 = re.compile(r"^[0-9a-f]{40}$")

CONSUMED_PROOF_KEYS = frozenset({"card", "path", "commit", "blob"})


class JitTerminalityError(ValueError):
    """A JIT consumed proof or terminality binding is missing or unproved.

    ``kind`` names the failure class for owning-boundary mapping:
    ``missing``, ``dangling``, ``stale``, ``sibling``, ``unproved`` or
    ``forged``.
    """

    def __init__(self, message: str, *, kind: str) -> None:
        super().__init__(message)
        self.kind = kind


def _fail(label: str, detail: str, kind: str) -> JitTerminalityError:
    return JitTerminalityError(f"{label}: {detail}", kind=kind)


def validate_consumed_proof_shape(
    proof: Any,
    workstream_id: str,
    label: str,
) -> dict[str, str]:
    """Validate one consumed-proof table shape without Git readback.

    Requires exactly ``card``/``path``/``commit``/``blob`` with the path
    matching the exact downstream Card contract location. Prose strings,
    path-only tables, malformed hex and sibling paths fail closed here so
    no bypass reaches the Git serving boundary.
    """
    if not isinstance(proof, Mapping):
        raise _fail(
            label,
            "consumed proof must be a table with exact card/path/commit/blob; "
            "prose or caller-attested proof cannot bind downstream materialization",
            "unproved",
        )
    keys = set(proof)
    if keys != CONSUMED_PROOF_KEYS:
        missing = sorted(CONSUMED_PROOF_KEYS - keys)
        extra = sorted(keys - CONSUMED_PROOF_KEYS)
        if missing and not extra:
            if "commit" in missing or "blob" in missing:
                raise _fail(
                    label,
                    "consumed proof requires exact commit + blob Git identity; "
                    "path-only proof cannot bind downstream materialization",
                    "unproved",
                )
            raise _fail(
                label,
                f"consumed proof is missing {missing}; expected exactly card/path/commit/blob",
                "unproved",
            )
        if extra:
            raise _fail(
                label,
                f"consumed proof carries unexpected prose keys {extra}; "
                "expected exactly card/path/commit/blob",
                "unproved",
            )
        raise _fail(
            label,
            f"consumed proof keys mismatch missing={missing} extra={extra}",
            "unproved",
        )
    card = proof.get("card")
    if not isinstance(card, str) or not card.strip():
        raise _fail(label, "consumed proof card must be a non-empty string", "unproved")
    raw_path = proof.get("path")
    try:
        locator_path = normalize_locator_path(raw_path, f"{label}.path")
    except ExactLocatorError as exc:
        raise _fail(
            label,
            f"consumed proof path {raw_path!r} is sibling: {exc}",
            "sibling",
        ) from exc
    expected = f"implementation/workstreams/{workstream_id}/cards/{card}.md"
    if locator_path != expected:
        raise _fail(
            label,
            f"consumed proof path {locator_path!r} does not match exact downstream "
            f"Card path {expected!r} (sibling workstream or Card)",
            "sibling",
        )
    commit = proof.get("commit")
    blob = proof.get("blob")
    if not isinstance(commit, str) or _SHA40.fullmatch(commit) is None:
        raise _fail(
            label,
            "consumed proof commit must be exact 40-hex Git identity; "
            "path-only proof cannot bind downstream materialization",
            "unproved",
        )
    if not isinstance(blob, str) or _SHA40.fullmatch(blob) is None:
        raise _fail(
            label,
            "consumed proof blob must be exact 40-hex Git identity; "
            "path-only proof cannot bind downstream materialization",
            "unproved",
        )
    return {"card": card, "path": locator_path, "commit": commit, "blob": blob}


def _ordered_board_cards(
    board: Mapping[str, Any],
) -> tuple[list[Mapping[str, Any]], dict[str, Mapping[str, Any]]]:
    """Return Board Cards in Board order plus an id index."""
    cards = board.get("cards", [])
    ordered = [
        card for card in cards
        if isinstance(card, Mapping) and isinstance(card.get("id"), str)
    ]
    return ordered, {str(card["id"]): card for card in ordered}


def residual_cards_for_trigger(board: Mapping[str, Any], trigger_id: Any) -> list[str]:
    """Return residual Cards bound to one trigger by late-oversize returns."""
    returns = board.get("late_oversize_returns", []) or []
    bound: list[str] = []
    if isinstance(returns, list):
        for record in returns:
            if not isinstance(record, Mapping):
                continue
            if record.get("residual_trigger") != trigger_id:
                continue
            residual = record.get("residual_card")
            if isinstance(residual, str) and residual:
                bound.append(residual)
    return bound


def has_trigger_resolution(
    board: Mapping[str, Any], trigger_id: Any, card_id: str
) -> bool:
    """Check durable trigger-to-Card resolutions for one binding."""
    returns = board.get("late_oversize_returns", []) or []
    if not isinstance(returns, list):
        return False
    for record in returns:
        if not isinstance(record, Mapping):
            continue
        resolutions = record.get("jit_resolutions", []) or []
        if not isinstance(resolutions, list):
            continue
        for entry in resolutions:
            if not isinstance(entry, Mapping):
                continue
            if entry.get("trigger") == trigger_id and entry.get("card") == card_id:
                return True
    return False


def validate_trigger_consumed_proof(
    trigger: Mapping[str, Any],
    board: Mapping[str, Any],
    label: str,
) -> dict[str, str] | None:
    """Validate one trigger's consumed proof against Board coherence.

    Returns the validated proof, or None when the trigger carries no proof.
    Absence stays shape-valid here for historic prose-only triggers; the
    terminality serving boundary requires presence. Premature proof on
    waiting/satisfied triggers, unknown/self downstream Cards, Board-order
    violations, Board/proof contract mismatches and handoff triggers naming
    a Card other than their bound residual Card fail closed here.
    """
    state = trigger.get("state")
    if state in {"waiting", "satisfied"} and "consumed_proof" in trigger:
        raise _fail(
            label,
            f"premature consumed proof on {state} trigger; proof is allowed "
            "only on consumed triggers once the downstream Card materializes",
            "unproved",
        )
    if "consumed_proof" not in trigger:
        return None
    workstream_id = str(board.get("workstream_id", ""))
    proof = validate_consumed_proof_shape(
        trigger.get("consumed_proof"), workstream_id, f"{label}.consumed_proof"
    )
    ordered, cards_by_id = _ordered_board_cards(board)
    card = proof["card"]
    if card not in cards_by_id:
        raise _fail(
            label,
            f"consumed proof names unknown downstream Card {card!r}; "
            "the binding is dangling until the downstream Card materializes",
            "dangling",
        )
    after_card = trigger.get("after_card")
    if card == after_card:
        raise _fail(
            label,
            f"consumed proof downstream Card {card!r} must name a different "
            "Card than the predecessor; a trigger cannot consume itself",
            "forged",
        )
    positions = {str(entry["id"]): index for index, entry in enumerate(ordered)}
    if positions.get(card, -1) <= positions.get(str(after_card), -1):
        raise _fail(
            label,
            f"JIT trigger {trigger.get('id', '?')!r} consumed proof downstream "
            f"Card {card!r} must materialize after predecessor {after_card!r} "
            "on the Board order; an earlier Card cannot be this trigger's "
            "downstream materialization",
            "forged",
        )
    downstream = cards_by_id[card]
    contract = downstream.get("contract") if isinstance(downstream, Mapping) else None
    board_path = contract.get("path") if isinstance(contract, Mapping) else None
    if isinstance(board_path, str) and board_path != proof["path"]:
        raise _fail(
            label,
            f"consumed proof path {proof['path']!r} does not match Board "
            f"downstream Card contract path {board_path!r} (sibling or forged binding)",
            "sibling",
        )
    bound = residual_cards_for_trigger(board, trigger.get("id"))
    if bound and card not in bound:
        raise _fail(
            label,
            f"JIT trigger {trigger.get('id', '?')!r} is a late-oversize residual "
            f"trigger bound to residual Card {bound[0]!r}; proof names unrelated "
            f"downstream Card {card!r}",
            "forged",
        )
    return proof


def verify_consumed_proof_git(
    *,
    project_root: Path,
    repository: str,
    proof: Mapping[str, str],
    label: str,
) -> bytes:
    """Prove one consumed-proof locator through the RF007 resolver.

    Returns the verified downstream contract bytes so callers never re-read
    past the proof. Dangling/stale/sibling/unproved Git failures map to the
    RF014 failure classes with exact reasons.
    """
    try:
        verify_exact_git_locator(
            project_root=project_root,
            repository=repository,
            expected_repository=repository,
            commit=proof["commit"],
            path=proof["path"],
            blob=proof["blob"],
            label=label,
        )
        return verify_worktree_freshness(
            project_root=project_root,
            path=proof["path"],
            blob=proof["blob"],
            label=label,
        )
    except ExactLocatorError as exc:
        kind = exc.kind
        if kind in {"dangling", "not_blob", "missing", "git_unavailable"}:
            raise _fail(label, f"downstream binding is dangling: {exc}", "dangling") from exc
        if kind in {"blob_mismatch", "mutated"}:
            raise _fail(label, f"downstream binding is stale: {exc}", "stale") from exc
        if kind in {"repository", "escape", "unsafe_path"}:
            raise _fail(label, f"downstream binding is sibling: {exc}", "sibling") from exc
        raise _fail(label, f"downstream binding is unproved: {exc}", "unproved") from exc


def verify_consumed_trigger(
    *,
    project_root: Path,
    project_repository: str,
    board: Mapping[str, Any],
    trigger: Mapping[str, Any],
    label: str,
) -> dict[str, str]:
    """Fully verify one consumed trigger's downstream materialization proof.

    Requires presence, Board coherence, RF007 Git identity plus worktree
    freshness, canonical Task Card parsing of the downstream contract, and
    the consumer edge binding this trigger to its exact downstream: a
    handoff trigger must name its bound residual Card (checked in Board
    coherence), otherwise the binding must be recorded in a durable
    trigger resolution or the downstream must declare the exact
    predecessor result as a Task Card dependency. Missing proof,
    dangling/stale/sibling Git bindings and forged Card bindings fail
    closed with exact reasons.
    """
    trigger_id = trigger.get("id", "?")
    workstream_id = str(board.get("workstream_id", ""))
    try:
        proof = validate_trigger_consumed_proof(trigger, board, label)
    except JitTerminalityError as exc:
        raise JitTerminalityError(str(exc), kind=exc.kind) from exc
    if proof is None:
        raise _fail(
            label,
            f"JIT trigger {trigger_id!r} is consumed with missing downstream "
            "materialization proof; consumed state requires an exact downstream "
            "Card/contract/Git-identity proof, not prose or path-only",
            "missing",
        )
    content = verify_consumed_proof_git(
        project_root=project_root,
        repository=project_repository,
        proof=proof,
        label=f"{label}.consumed_proof",
    )
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise _fail(
            label,
            f"consumed trigger {trigger_id!r} downstream contract "
            f"{proof['path']!r} is not readable Task Card text: {exc}",
            "forged",
        ) from exc
    # Canonical Task Card parser (lazy import: state_contract owns this
    # module, so a top-level import would be circular). Anchored field
    # validation rejects Card IDs forged inside free prose.
    try:
        from tools.state_contract import ValidationError, parse_task_card
    except ModuleNotFoundError:  # direct script execution from tools/
        from state_contract import ValidationError, parse_task_card
    try:
        parsed = parse_task_card(text, proof["card"], workstream_id)
    except ValidationError as exc:
        raise _fail(
            label,
            f"consumed trigger {trigger_id!r} proof is forged: downstream "
            f"contract {proof['path']!r} is not a valid Task Card for "
            f"{proof['card']!r}: {exc}",
            "forged",
        ) from exc
    _verify_consumer_edge(board, trigger, proof, parsed, label)
    return proof


def _verify_consumer_edge(
    board: Mapping[str, Any],
    trigger: Mapping[str, Any],
    proof: Mapping[str, str],
    parsed: Mapping[str, Any],
    label: str,
) -> None:
    """Prove the downstream Card consumed this exact trigger/predecessor.

    Handoff triggers are already bound to their residual Card by Board
    coherence. Other triggers must either be recorded in a durable
    trigger resolution for this downstream Card or declare the exact
    predecessor result (path plus commit/blob identity from the Board
    result locator) as a Task Card dependency. An unrelated later Card,
    a superseded dependency identity and a predecessor result without
    exact identity fail closed as forged, stale or unproved.
    """
    trigger_id = trigger.get("id", "?")
    if residual_cards_for_trigger(board, trigger.get("id")):
        return
    if has_trigger_resolution(board, trigger.get("id"), proof["card"]):
        return
    _, cards_by_id = _ordered_board_cards(board)
    after_card = trigger.get("after_card")
    predecessor = cards_by_id.get(str(after_card))
    result = predecessor.get("result") if isinstance(predecessor, Mapping) else None
    if not isinstance(result, Mapping):
        raise _fail(
            label,
            f"consumed trigger {trigger_id!r} predecessor {after_card!r} has no "
            "result; the consumer edge is unproved until the predecessor "
            "result is durable",
            "unproved",
        )
    expected_path = result.get("path")
    expected_commit = result.get("commit")
    expected_blob = result.get("blob")
    if (
        not isinstance(expected_path, str)
        or not isinstance(expected_commit, str)
        or _SHA40.fullmatch(expected_commit) is None
        or not isinstance(expected_blob, str)
        or _SHA40.fullmatch(expected_blob) is None
    ):
        raise _fail(
            label,
            f"consumed trigger {trigger_id!r} predecessor {after_card!r} result "
            "has no exact Git identity; the consumer edge is unproved without "
            "an exact predecessor result locator",
            "unproved",
        )
    dependencies = parsed.get("dependencies", [])
    if not any(
        isinstance(entry, Mapping) and entry.get("path") == expected_path
        for entry in dependencies
    ):
        raise _fail(
            label,
            f"consumed trigger {trigger_id!r} proof is forged: downstream Card "
            f"{proof['card']!r} declares no dependency on predecessor "
            f"{after_card!r} result {expected_path!r}; an unrelated later "
            "Card with valid identity is not proof this trigger was consumed",
            "forged",
        )
    if not any(
        isinstance(entry, Mapping)
        and entry.get("path") == expected_path
        and entry.get("commit") == expected_commit
        and entry.get("blob") == expected_blob
        for entry in dependencies
    ):
        raise _fail(
            label,
            f"consumed trigger {trigger_id!r} downstream Card {proof['card']!r} "
            f"dependency on {expected_path!r} is stale: it does not match the "
            f"exact predecessor result {expected_commit}:{expected_blob}",
            "stale",
        )
