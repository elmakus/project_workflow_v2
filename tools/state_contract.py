#!/usr/bin/env python3
"""Executable M01 Project Workflow V2 state-envelope contract."""

from __future__ import annotations

import argparse
import re
import tomllib
from pathlib import Path, PurePosixPath
from typing import Any

SHA40 = re.compile(r"^[0-9a-f]{40}$")
CARD_STATUSES = {"planned", "ready", "in_progress", "blocked", "done"}
PROHIBITED_KEY_PREFIXES = ("runtime_", "model_", "session_", "worker_", "batch_", "lane_", "scheduler_", "context_health_")
PROHIBITED_KEYS = {
    "execution_policy",
    "runtime",
    "model",
    "session",
    "worker",
    "worker_id",
    "orchestration_binding",
    "active_execution",
    "returned",
    "transfer_ready",
    "batch",
    "lane",
    "lanes",
    "scheduler",
    "context_health",
}


class ValidationError(ValueError):
    pass


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValidationError(message)


def _read_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        value = tomllib.load(handle)
    _require(isinstance(value, dict), f"{path}: top-level TOML must be a table")
    return value


def read_project(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    _require(lines and lines[0] == "+++", f"{path}: missing TOML front matter")
    try:
        end = lines.index("+++", 1)
    except ValueError as exc:
        raise ValidationError(f"{path}: unterminated TOML front matter") from exc
    return tomllib.loads("\n".join(lines[1:end]))


def reject_prohibited_keys(value: Any, where: str = "$") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = str(key).lower()
            _require(normalized not in PROHIBITED_KEYS and not normalized.startswith(PROHIBITED_KEY_PREFIXES),
                     f"{where}: prohibited canonical key {key!r}")
            reject_prohibited_keys(child, f"{where}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_prohibited_keys(child, f"{where}[{index}]")


def _safe_relative_path(raw: Any, label: str) -> str:
    _require(isinstance(raw, str) and raw, f"{label}: path must be non-empty string")
    path = PurePosixPath(raw)
    _require(not path.is_absolute(), f"{label}: absolute paths are not durable artifact locators")
    _require(".." not in path.parts and "." not in path.parts, f"{label}: path traversal is forbidden")
    return raw


def validate_locator(
    ref: Any,
    expected_class: str,
    label: str,
    workstream_id: str | None = None,
) -> str:
    _require(isinstance(ref, dict), f"{label}: locator must be a table")
    _require(ref.get("class") == expected_class, f"{label}: expected class {expected_class!r}")
    path = _safe_relative_path(ref.get("path"), label)

    if expected_class == "task_board":
        _require(workstream_id is not None, f"{label}: workstream binding required")
        expected = f"implementation/workstreams/{workstream_id}/TASK_BOARD.toml"
        _require(path == expected, f"{label}: expected exact path {expected!r}")
    elif expected_class == "task_card":
        _require(workstream_id is not None, f"{label}: workstream binding required")
        prefix = f"implementation/workstreams/{workstream_id}/cards/"
        _require(path.startswith(prefix) and path.endswith(".md"), f"{label}: wrong Task Card class/path")
    elif expected_class in {"evidence", "result"}:
        _require(workstream_id is not None, f"{label}: workstream binding required")
        directory = "evidence" if expected_class == "evidence" else "results"
        prefix = f"implementation/workstreams/{workstream_id}/{directory}/"
        _require(path.startswith(prefix) and path.endswith(".md"), f"{label}: wrong {expected_class} class/path")
    elif expected_class == "authority":
        allowed = ("requirements/", "decisions/", "planning/", "workflow/")
        _require(path.startswith(allowed), f"{label}: authority path is outside accepted authority roots")
    else:
        raise ValidationError(f"{label}: unsupported locator class {expected_class!r}")
    return path


def validate_project(data: dict[str, Any]) -> None:
    reject_prohibited_keys(data, "project")
    _require(data.get("project_workflow") == "v2", "project: project_workflow must be 'v2'")
    for key in ("project_id", "repository", "workstream_root"):
        _require(isinstance(data.get(key), str) and data[key], f"project: missing {key}")
    _require(data["workstream_root"] == "implementation/workstreams", "project: unsupported workstream_root")


def validate_workstream(data: dict[str, Any]) -> None:
    reject_prohibited_keys(data, "workstream")
    for key in ("workstream_id", "kind", "branch", "integration_target"):
        _require(isinstance(data.get(key), str) and data[key], f"workstream: missing {key}")
    _require(isinstance(data.get("created_from"), str) and SHA40.fullmatch(data["created_from"]) is not None,
             "workstream: created_from must be exact 40-hex commit")
    authority = data.get("authority")
    _require(isinstance(authority, list) and authority, "workstream: at least one exact authority locator is required")
    for index, ref in enumerate(authority):
        validate_locator(ref, "authority", f"workstream.authority[{index}]")
    validate_locator(data.get("task_board"), "task_board", "workstream.task_board", data["workstream_id"])


def validate_board(
    data: dict[str, Any],
    workstream: dict[str, Any],
    expected_revision: int | None = None,
) -> None:
    reject_prohibited_keys(data, "task_board")
    _require(data.get("workstream_id") == workstream["workstream_id"], "task_board: wrong workstream_id")
    _require(isinstance(data.get("revision"), int) and data["revision"] >= 0, "task_board: revision must be non-negative integer")
    if expected_revision is not None:
        _require(data["revision"] == expected_revision,
                 f"task_board: stale expected revision {expected_revision}; current is {data['revision']}")
    execution_ref = data.get("execution_ref")
    _require(isinstance(execution_ref, dict), "task_board: missing execution_ref")
    _require(execution_ref.get("branch") == workstream["branch"], "task_board: wrong original branch")

    cards = data.get("cards")
    _require(isinstance(cards, list), "task_board: cards must be an array")
    ids: set[str] = set()
    active = 0
    for index, card in enumerate(cards):
        label = f"task_board.cards[{index}]"
        _require(isinstance(card, dict), f"{label}: card must be table")
        card_id = card.get("id")
        _require(isinstance(card_id, str) and card_id, f"{label}: missing id")
        _require(card_id not in ids, f"{label}: duplicate Card id {card_id!r}")
        ids.add(card_id)
        status = card.get("status")
        _require(status in CARD_STATUSES, f"{label}: invalid status {status!r}")
        active += int(status == "in_progress")
        validate_locator(card.get("contract"), "task_card", f"{label}.contract", workstream["workstream_id"])
        if "result" in card:
            validate_locator(card["result"], "result", f"{label}.result", workstream["workstream_id"])
        if status == "done":
            _require("result" in card, f"{label}: done Card requires an exact result locator")
    _require(active <= 1, "task_board: more than one Project Workflow Card is in_progress")


def validate_review(data: dict[str, Any]) -> None:
    reject_prohibited_keys(data, "review")
    _require(isinstance(data.get("attempt"), str) and data["attempt"], "review: missing attempt")
    _require(data.get("verdict") in {"pending", "green", "red"}, "review: invalid verdict")

    subject = data.get("subject")
    _require(isinstance(subject, dict) and subject.get("class") == "git_blob", "review: subject must be git_blob")
    for key in ("repository", "path"):
        _require(isinstance(subject.get(key), str) and subject[key], f"review.subject: missing {key}")
    for key in ("commit", "blob"):
        _require(isinstance(subject.get(key), str) and SHA40.fullmatch(subject[key]) is not None,
                 f"review.subject: {key} must be exact 40-hex")
    _safe_relative_path(subject["path"], "review.subject")

    validate_locator(data.get("acceptance"), "authority", "review.acceptance")
    independence = data.get("independence")
    _require(isinstance(independence, dict), "review: missing semantic independence")
    _require(independence.get("materially_produced_or_repaired_subject") is False,
             "review: reviewer is not semantically independent of exact subject")
    _require(isinstance(independence.get("basis"), str) and independence["basis"].strip(),
             "review: independence basis must be durable")


def validate_external_effect(data: dict[str, Any], workstream_id: str) -> None:
    reject_prohibited_keys(data, "external_effect")
    for key in ("obligation_id", "operation", "target", "expected_state", "readback_state"):
        _require(isinstance(data.get(key), str) and data[key], f"external_effect: missing {key}")
    _require(data["readback_state"] in {"pending", "verified", "uncertain"},
             "external_effect: invalid readback_state")
    validate_locator(data.get("evidence"), "evidence", "external_effect.evidence", workstream_id)


def validate_bundle(
    project_path: Path,
    workstream_path: Path,
    board_path: Path,
    review_path: Path,
    effect_path: Path,
    expected_revision: int | None = None,
) -> None:
    project = read_project(project_path)
    workstream = _read_toml(workstream_path)
    board = _read_toml(board_path)
    review = _read_toml(review_path)
    effect = _read_toml(effect_path)

    validate_project(project)
    validate_workstream(workstream)
    validate_board(board, workstream, expected_revision)
    validate_review(review)
    validate_external_effect(effect, workstream["workstream_id"])


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate the implemented PWV2 M01 durable state envelope.")
    parser.add_argument("project", type=Path)
    parser.add_argument("workstream", type=Path)
    parser.add_argument("task_board", type=Path)
    parser.add_argument("review_attempt", type=Path)
    parser.add_argument("external_effect", type=Path)
    parser.add_argument("--expect-revision", type=int)
    args = parser.parse_args()
    try:
        validate_bundle(
            args.project,
            args.workstream,
            args.task_board,
            args.review_attempt,
            args.external_effect,
            args.expect_revision,
        )
    except (OSError, tomllib.TOMLDecodeError, ValidationError) as exc:
        print(f"INVALID: {exc}")
        return 2
    print("VALID: PWV2 M01 state envelope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
