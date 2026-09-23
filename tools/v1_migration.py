#!/usr/bin/env python3
"""Bounded, read-only V1 migration discovery for PWV2 M06-T01."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SHA40 = re.compile(r"^[0-9a-f]{40}$")
WORKSTREAM_ID = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SUPPORTED_SOURCE_CLASSES = {
    "chatgpt_workstream_yaml_v1",
    "codex_workstream_yaml_v1",
    "legacy_root_yaml_v1",
}

MANIFEST_KEYS = {
    "id", "kind", "status", "branch", "base_ref", "integration_target",
    "parent_workstream", "parent_branch", "parent_dependency", "intake",
    "routing", "task_board", "authority", "review", "branch_cleanup", "pr", "result",
}
BOARD_KEYS = {
    "project", "workstream_id", "plan_revision", "current_milestone",
    "execution_ref", "research_obligation", "milestones", "cards",
}
MILESTONE_KEYS = {
    "decision_state", "execution_status", "contract", "checkpoint",
    "implementation_head", "handoff", "acceptance_evidence",
    "review_state", "review_subject", "review_evidence",
}
CARD_KEYS = {
    "id", "title", "milestone", "decision_state", "execution_status", "executor",
    "depends_on", "openspec_change", "contract", "review_state",
    "review_subject", "review_evidence", "result_commit", "result_pr",
    "evidence", "tests_summary",
}
EXECUTION_REF_KEYS = {"branch", "pr", "head"}


class MigrationInputError(ValueError):
    """The bounded reader cannot safely interpret this input."""


@dataclass(frozen=True)
class _Line:
    indent: int
    text: str
    number: int


def _strip_comment(raw: str) -> str:
    quote: str | None = None
    escaped = False
    for i, ch in enumerate(raw):
        if escaped:
            escaped = False
            continue
        if ch == "\\" and quote == '"':
            escaped = True
            continue
        if quote:
            if ch == quote:
                quote = None
            continue
        if ch in {"'", '"'}:
            quote = ch
            continue
        if ch == "#" and (i == 0 or raw[i - 1].isspace()):
            return raw[:i].rstrip()
    return raw.rstrip()


def _tokenize(text: str) -> list[_Line]:
    result: list[_Line] = []
    for number, raw in enumerate(text.splitlines(), 1):
        if "\t" in raw[: len(raw) - len(raw.lstrip())]:
            raise MigrationInputError(f"line {number}: tabs are not supported in bounded V1 YAML")
        stripped = raw.lstrip(" ")
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw) - len(stripped)
        if indent % 2:
            raise MigrationInputError(f"line {number}: indentation must use two-space steps")
        content = _strip_comment(stripped)
        if content:
            result.append(_Line(indent, content, number))
    return result


def _scalar(raw: str, number: int) -> Any:
    raw = raw.strip()
    if raw == "null" or raw == "~":
        return None
    if raw == "true":
        return True
    if raw == "false":
        return False
    if re.fullmatch(r"-?[0-9]+", raw):
        return int(raw)
    if raw.startswith(("[", "{")):
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise MigrationInputError(f"line {number}: unsupported inline YAML value") from exc
    if raw.startswith(("'", '"')):
        try:
            value = ast.literal_eval(raw)
        except (SyntaxError, ValueError) as exc:
            raise MigrationInputError(f"line {number}: invalid quoted scalar") from exc
        if not isinstance(value, str):
            raise MigrationInputError(f"line {number}: quoted scalar must be text")
        return value
    if raw[0] in "&*!|>":
        raise MigrationInputError(f"line {number}: YAML tags/anchors/block scalars are unsupported")
    return raw


def _key_value(text: str, number: int) -> tuple[str, str]:
    if ":" not in text:
        raise MigrationInputError(f"line {number}: expected key: value")
    key, value = text.split(":", 1)
    key = key.strip()
    if not re.fullmatch(r"[A-Za-z0-9_-]+", key):
        raise MigrationInputError(f"line {number}: unsupported YAML key {key!r}")
    return key, value.strip()


def _parse_block(lines: list[_Line], index: int, indent: int) -> tuple[Any, int]:
    if index >= len(lines) or lines[index].indent != indent:
        raise MigrationInputError("internal bounded-YAML indentation mismatch")
    is_list = lines[index].text.startswith("- ")
    if is_list:
        output: list[Any] = []
        while index < len(lines) and lines[index].indent == indent:
            line = lines[index]
            if not line.text.startswith("- "):
                break
            item_text = line.text[2:].strip()
            index += 1
            if ":" in item_text and re.match(r"^[A-Za-z0-9_-]+\s*:", item_text):
                key, raw = _key_value(item_text, line.number)
                item: dict[str, Any] = {}
                if raw:
                    item[key] = _scalar(raw, line.number)
                elif index < len(lines) and lines[index].indent > indent:
                    child, index = _parse_block(lines, index, lines[index].indent)
                    item[key] = child
                else:
                    item[key] = None
                if index < len(lines) and lines[index].indent > indent:
                    child, index = _parse_block(lines, index, lines[index].indent)
                    if not isinstance(child, dict):
                        raise MigrationInputError(
                            f"line {line.number}: list mapping continuation must be a mapping"
                        )
                    for child_key, child_value in child.items():
                        if child_key in item:
                            raise MigrationInputError(
                                f"line {line.number}: duplicate key {child_key!r}"
                            )
                        item[child_key] = child_value
                output.append(item)
            else:
                if not item_text:
                    raise MigrationInputError(f"line {line.number}: empty sequence items unsupported")
                output.append(_scalar(item_text, line.number))
                if index < len(lines) and lines[index].indent > indent:
                    raise MigrationInputError(
                        f"line {line.number}: nested scalar sequence items unsupported"
                    )
        return output, index

    output_dict: dict[str, Any] = {}
    while index < len(lines) and lines[index].indent == indent:
        line = lines[index]
        if line.text.startswith("- "):
            break
        key, raw = _key_value(line.text, line.number)
        if key in output_dict:
            raise MigrationInputError(f"line {line.number}: duplicate key {key!r}")
        index += 1
        if raw:
            output_dict[key] = _scalar(raw, line.number)
        elif index < len(lines) and lines[index].indent > indent:
            child, index = _parse_block(lines, index, lines[index].indent)
            output_dict[key] = child
        else:
            output_dict[key] = None
    return output_dict, index


def parse_bounded_yaml(text: str) -> dict[str, Any]:
    lines = _tokenize(text)
    if not lines:
        raise MigrationInputError("empty V1 YAML input")
    if lines[0].indent != 0:
        raise MigrationInputError("top-level V1 YAML must start at indentation zero")
    result, index = _parse_block(lines, 0, 0)
    if index != len(lines) or not isinstance(result, dict):
        raise MigrationInputError("V1 YAML must be exactly one top-level mapping")
    return result


def _unknown_keys(value: dict[str, Any], allowed: set[str], where: str) -> None:
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise MigrationInputError(f"{where}: unsupported fields: {', '.join(unknown)}")


def _require_mapping(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise MigrationInputError(f"{where}: expected mapping")
    return value


def _require_list(value: Any, where: str) -> list[Any]:
    if not isinstance(value, list):
        raise MigrationInputError(f"{where}: expected list")
    return value


def validate_manifest(manifest: dict[str, Any], source_class: str) -> None:
    _unknown_keys(manifest, MANIFEST_KEYS, "manifest")
    for key in ("id", "branch", "integration_target"):
        if not isinstance(manifest.get(key), str) or not manifest[key]:
            raise MigrationInputError(f"manifest: missing {key}")
    if source_class == "legacy_root_yaml_v1":
        raise MigrationInputError("legacy root source must not manufacture a branch-local manifest")
    authority = _require_mapping(manifest.get("authority"), "manifest.authority")
    if not isinstance(authority.get("requirements"), str) or not authority["requirements"]:
        raise MigrationInputError("manifest.authority: exact requirements path is required")
    if not isinstance(authority.get("plan"), str) or not authority["plan"]:
        raise MigrationInputError("manifest.authority: exact plan path is required")
    decisions = authority.get("decisions")
    if not isinstance(decisions, list):
        raise MigrationInputError("manifest.authority: decisions must be a list")


def validate_board(board: dict[str, Any], source_class: str, manifest: dict[str, Any] | None) -> None:
    _unknown_keys(board, BOARD_KEYS, "board")
    for key in ("project", "plan_revision", "current_milestone"):
        if not isinstance(board.get(key), str) or not board[key]:
            raise MigrationInputError(f"board: missing {key}")
    execution_ref = _require_mapping(board.get("execution_ref"), "board.execution_ref")
    _unknown_keys(execution_ref, EXECUTION_REF_KEYS, "board.execution_ref")
    if not isinstance(execution_ref.get("branch"), str) or not execution_ref["branch"]:
        raise MigrationInputError("board.execution_ref: branch is required")

    milestones = _require_mapping(board.get("milestones"), "board.milestones")
    for milestone_id, milestone in milestones.items():
        data = _require_mapping(milestone, f"board.milestones.{milestone_id}")
        _unknown_keys(data, MILESTONE_KEYS, f"board.milestones.{milestone_id}")

    cards = _require_list(board.get("cards"), "board.cards")
    seen: set[str] = set()
    for index, card_value in enumerate(cards):
        card = _require_mapping(card_value, f"board.cards[{index}]")
        _unknown_keys(card, CARD_KEYS, f"board.cards[{index}]")
        card_id = card.get("id")
        if not isinstance(card_id, str) or not card_id or card_id in seen:
            raise MigrationInputError(f"board.cards[{index}]: invalid/duplicate id")
        seen.add(card_id)
        if card.get("execution_status") not in {"planned", "ready", "in_progress", "blocked", "done"}:
            raise MigrationInputError(f"board.cards[{index}]: unsupported execution_status")
        review_state = card.get("review_state")
        if review_state in {"green", "red"} and not card.get("review_subject"):
            raise MigrationInputError(
                f"board.cards[{index}]: terminal V1 review lacks exact review_subject"
            )

    if source_class == "legacy_root_yaml_v1":
        if "workstream_id" in board:
            raise MigrationInputError("legacy root board unexpectedly claims branch-local workstream_id")
        if manifest is not None:
            raise MigrationInputError("legacy root source must not provide manifest")
    else:
        if manifest is None:
            raise MigrationInputError(f"{source_class}: branch-local manifest is required")
        if board.get("workstream_id") != manifest.get("id"):
            raise MigrationInputError("manifest/board workstream identity mismatch")
        if execution_ref["branch"] != manifest.get("branch"):
            raise MigrationInputError("manifest/board branch identity mismatch")


def _digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _semantic_summary(board: dict[str, Any]) -> tuple[list[str], list[str]]:
    outstanding: list[str] = []
    blockers: list[str] = []
    cards = _require_list(board["cards"], "board.cards")
    active = [card["id"] for card in cards if card["execution_status"] == "in_progress"]
    if len(active) > 1:
        blockers.append("parallel_active_cards:" + ",".join(sorted(active)))
    for card in cards:
        status = card["execution_status"]
        if status != "done":
            outstanding.append(f"card:{card['id']}:{status}")
        review = card.get("review_state")
        if review in {"pending", "in_progress", "red"}:
            outstanding.append(f"review:{card['id']}:{review}")
    research = board.get("research_obligation")
    if research is not None:
        outstanding.append(f"research:{research}")
    for milestone_id, milestone in board["milestones"].items():
        status = milestone.get("execution_status")
        if status != "done":
            outstanding.append(f"milestone:{milestone_id}:{status}")
        review = milestone.get("review_state")
        if review in {"pending", "in_progress", "red"}:
            outstanding.append(f"milestone_review:{milestone_id}:{review}")
    return sorted(outstanding), sorted(blockers)


def dry_run(
    *,
    source_class: str,
    repository: str,
    expected_commit: str,
    observed_commit: str,
    board_text: str,
    manifest_text: str | None,
    destination_workstream: str,
) -> dict[str, Any]:
    if source_class not in SUPPORTED_SOURCE_CLASSES:
        raise MigrationInputError(f"unsupported source class {source_class!r}")
    if repository.count("/") != 1 or not all(part.strip() for part in repository.split("/", 1)):
        raise MigrationInputError("source repository must be exact owner/name")
    for label, commit in (("expected", expected_commit), ("observed", observed_commit)):
        if SHA40.fullmatch(commit) is None:
            raise MigrationInputError(f"{label} source commit must be lowercase 40-hex")
    if expected_commit != observed_commit:
        raise MigrationInputError("source moved since dry-run identity was selected")
    if WORKSTREAM_ID.fullmatch(destination_workstream) is None:
        raise MigrationInputError("destination workstream id is invalid")

    board = parse_bounded_yaml(board_text)
    manifest = parse_bounded_yaml(manifest_text) if manifest_text is not None else None
    if manifest is not None:
        validate_manifest(manifest, source_class)
    validate_board(board, source_class, manifest)
    outstanding, blockers = _semantic_summary(board)

    source_identity = {
        "class": source_class,
        "repository": repository,
        "commit": expected_commit,
        "board_sha256": _digest(board_text),
        "manifest_sha256": _digest(manifest_text) if manifest_text is not None else None,
    }
    fingerprint = hashlib.sha256(
        json.dumps(source_identity, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    root = f"implementation/workstreams/{destination_workstream}"
    return {
        "schema": "pwv2-m06-dry-run-v1",
        "valid": not blockers,
        "source": source_identity,
        "source_fingerprint": fingerprint,
        "destination": {
            "workstream_id": destination_workstream,
            "root": root,
            "manifest": f"{root}/WORKSTREAM.toml",
            "task_board": f"{root}/TASK_BOARD.toml",
        },
        "mapping": {
            "authority": "common_v2_authority_locators",
            "cards": "common_v2_task_board_and_stable_contract_locators",
            "results": "reconcile_as_results",
            "reviews": "append_only_exact_subject_attempts",
            "legacy_runtime_policy_scheduler": "drop_from_canonical_output",
            "historical_source": f"{root}/migration/",
        },
        "outstanding_obligations": outstanding,
        "blockers": blockers,
    }


def _main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    dry = sub.add_parser("dry-run")
    dry.add_argument("--source-class", required=True, choices=sorted(SUPPORTED_SOURCE_CLASSES))
    dry.add_argument("--repository", required=True)
    dry.add_argument("--expected-commit", required=True)
    dry.add_argument("--observed-commit", required=True)
    dry.add_argument("--board", type=Path, required=True)
    dry.add_argument("--manifest", type=Path)
    dry.add_argument("--destination-workstream", required=True)
    args = parser.parse_args()
    try:
        plan = dry_run(
            source_class=args.source_class,
            repository=args.repository,
            expected_commit=args.expected_commit,
            observed_commit=args.observed_commit,
            board_text=args.board.read_text(encoding="utf-8"),
            manifest_text=args.manifest.read_text(encoding="utf-8") if args.manifest else None,
            destination_workstream=args.destination_workstream,
        )
    except (MigrationInputError, OSError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, sort_keys=True))
        return 2
    print(json.dumps(plan, sort_keys=True, indent=2))
    return 0 if plan["valid"] else 3


if __name__ == "__main__":
    raise SystemExit(_main())
