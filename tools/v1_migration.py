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
MANIFEST_INTAKE_KEYS = {"state", "record"}
MANIFEST_ROUTING_KEYS = {"exploratory_scope", "research_obligation", "plan_review"}
MANIFEST_AUTHORITY_KEYS = {"requirements", "decisions", "plan"}
MANIFEST_REVIEW_KEYS = {"requirement", "state", "subject", "evidence", "covered_by"}
MANIFEST_CLEANUP_KEYS = {"state", "ref", "verified_head", "evidence"}


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
    intake = _require_mapping(manifest.get("intake"), "manifest.intake")
    _unknown_keys(intake, MANIFEST_INTAKE_KEYS, "manifest.intake")
    if not isinstance(intake.get("state"), str) or not isinstance(intake.get("record"), str):
        raise MigrationInputError("manifest.intake: exact state and record are required")

    routing = manifest.get("routing")
    if routing is not None:
        routing = _require_mapping(routing, "manifest.routing")
        _unknown_keys(routing, MANIFEST_ROUTING_KEYS, "manifest.routing")
        for key in MANIFEST_ROUTING_KEYS:
            value = routing.get(key)
            if value is not None and (not isinstance(value, str) or not value):
                raise MigrationInputError(f"manifest.routing.{key}: expected non-empty string or null")

    authority = _require_mapping(manifest.get("authority"), "manifest.authority")
    _unknown_keys(authority, MANIFEST_AUTHORITY_KEYS, "manifest.authority")
    if not isinstance(authority.get("requirements"), str) or not authority["requirements"]:
        raise MigrationInputError("manifest.authority: exact requirements path is required")
    if not isinstance(authority.get("plan"), str) or not authority["plan"]:
        raise MigrationInputError("manifest.authority: exact plan path is required")
    decisions = authority.get("decisions")
    if not isinstance(decisions, list) or not all(isinstance(value, str) and value for value in decisions):
        raise MigrationInputError("manifest.authority: decisions must be a list of exact paths")

    review = manifest.get("review")
    if review is not None:
        review = _require_mapping(review, "manifest.review")
        _unknown_keys(review, MANIFEST_REVIEW_KEYS, "manifest.review")
        if review.get("requirement") not in {"NONE", "RECOMMENDED", "REQUIRED"}:
            raise MigrationInputError("manifest.review: unsupported requirement")
        if review.get("state") not in {None, "pending", "in_progress", "green", "red"}:
            raise MigrationInputError("manifest.review: unsupported state")
        for key in ("subject", "evidence", "covered_by"):
            if review.get(key) is not None and not isinstance(review.get(key), str):
                raise MigrationInputError(f"manifest.review.{key}: expected string or null")

    cleanup = manifest.get("branch_cleanup")
    if cleanup is not None:
        cleanup = _require_mapping(cleanup, "manifest.branch_cleanup")
        _unknown_keys(cleanup, MANIFEST_CLEANUP_KEYS, "manifest.branch_cleanup")
        for key in MANIFEST_CLEANUP_KEYS:
            if cleanup.get(key) is not None and not isinstance(cleanup.get(key), str):
                raise MigrationInputError(f"manifest.branch_cleanup.{key}: expected string or null")

    parent_values = [manifest.get("parent_workstream"), manifest.get("parent_branch"), manifest.get("parent_dependency")]
    present_parent = [value is not None for value in parent_values]
    if any(present_parent) and not all(present_parent):
        raise MigrationInputError("manifest: stacked parent provenance must be complete")
    if all(present_parent) and not all(isinstance(value, str) and value for value in parent_values):
        raise MigrationInputError("manifest: stacked parent provenance must use exact non-empty strings")


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
        contract = card.get("contract")
        if not isinstance(contract, str) or not contract:
            raise MigrationInputError(f"board.cards[{index}]: exact Task Card contract path is required")
        if card.get("execution_status") == "done":
            result_commit = card.get("result_commit")
            if not isinstance(result_commit, str) or SHA40.fullmatch(result_commit) is None:
                raise MigrationInputError(
                    f"board.cards[{index}]: DONE V1 Card requires exact result_commit"
                )
            if not isinstance(card.get("evidence"), str) or not card["evidence"]:
                raise MigrationInputError(
                    f"board.cards[{index}]: DONE V1 Card requires result evidence"
                )
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


def _semantic_summary(
    board: dict[str, Any],
    manifest: dict[str, Any] | None,
) -> tuple[list[str], list[str]]:
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
        blockers.append("preexecution_reconstitution_required:research_obligation")

    for milestone_id, milestone in board["milestones"].items():
        status = milestone.get("execution_status")
        if status != "done":
            outstanding.append(f"milestone:{milestone_id}:{status}")
        review = milestone.get("review_state")
        if review in {"pending", "in_progress", "red"}:
            outstanding.append(f"milestone_review:{milestone_id}:{review}")

    if manifest is not None:
        routing = manifest.get("routing") or {}
        for key in ("exploratory_scope", "research_obligation", "plan_review"):
            value = routing.get(key)
            if value is not None:
                outstanding.append(f"preexecution:{key}:{value}")
                blockers.append(f"preexecution_reconstitution_required:{key}")

        review = manifest.get("review") or {}
        if review.get("state") in {"pending", "in_progress", "red", "green"}:
            outstanding.append(f"workstream_review:{review['state']}")
            blockers.append("workstream_review_reconciliation_required")

        if manifest.get("parent_dependency") is not None:
            outstanding.append(
                "stacked_parent_dependency:"
                + ":".join(
                    [
                        str(manifest["parent_workstream"]),
                        str(manifest["parent_branch"]),
                        str(manifest["parent_dependency"]),
                    ]
                )
            )
            blockers.append("stacked_parent_dependency_requires_reconciliation")

    return sorted(set(outstanding)), sorted(set(blockers))

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
    outstanding, blockers = _semantic_summary(board, manifest)

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



def _authority_locators(manifest: dict[str, Any] | None, board: dict[str, Any]) -> list[dict[str, str]]:
    paths: list[str] = []
    if manifest is not None:
        authority = manifest.get("authority", {})
        for value in [authority.get("requirements"), *(authority.get("decisions") or []), authority.get("plan")]:
            if isinstance(value, str) and value.startswith(("requirements/", "decisions/", "planning/", "workflow/")):
                paths.append(value)
    else:
        for milestone in board["milestones"].values():
            value = milestone.get("contract")
            if isinstance(value, str) and value.startswith(("requirements/", "decisions/", "planning/", "workflow/")):
                paths.append(value.split("#", 1)[0])
    unique = list(dict.fromkeys(paths))
    if not unique:
        raise MigrationInputError("cannot preserve accepted authority: no exact V1 authority path is available")
    return [{"class": "authority", "path": value} for value in unique]


def _normalized_review_attempts(
    *,
    source_card: dict[str, Any],
    destination_workstream: str,
    proof: list[dict[str, Any]] | None,
) -> tuple[list[dict[str, Any]], list[dict[str, str]], str | None]:
    review_state = source_card.get("review_state")
    if review_state is None:
        return [], [], None
    if review_state not in {"pending", "in_progress", "green", "red"}:
        raise MigrationInputError(
            f"card {source_card['id']}: unsupported V1 review_state {review_state!r}"
        )
    if not proof:
        return [], [], (
            f"V1 review {review_state!r} cannot be reused without exact immutable subject "
            "and semantic independence proof"
        )

    if proof[-1].get("source_review_subject") != source_card.get("review_subject"):
        return [], [], "review proof is not bound to the exact current V1 review_subject"
    attempts: list[dict[str, Any]] = []
    refs: list[dict[str, str]] = []
    for index, item in enumerate(proof, 1):
        attempt_id = item.get("attempt") or f"R{index:02d}"
        verdict = item.get("verdict")
        subject = item.get("subject")
        basis = item.get("independence_basis")
        produced = item.get("materially_produced_or_repaired_subject")
        source_evidence = item.get("evidence_path", "")
        if verdict not in {"pending", "in_progress", "green", "red"}:
            return [], [], f"review proof {attempt_id}: invalid verdict"
        if not isinstance(subject, dict):
            return [], [], f"review proof {attempt_id}: missing exact subject"
        if (
            not isinstance(subject.get("repository"), str)
            or not subject["repository"]
            or not isinstance(subject.get("path"), str)
            or not subject["path"]
            or SHA40.fullmatch(str(subject.get("commit", ""))) is None
            or SHA40.fullmatch(str(subject.get("blob", ""))) is None
        ):
            return [], [], f"review proof {attempt_id}: subject is not exact git-blob identity"
        if produced is not False or not isinstance(basis, str) or not basis.strip():
            return [], [], f"review proof {attempt_id}: semantic independence is unproven"

        evidence_path = ""
        if verdict in {"green", "red"}:
            if not isinstance(source_evidence, str) or not source_evidence:
                return [], [], f"review proof {attempt_id}: terminal evidence is missing"
            evidence_path = (
                f"implementation/workstreams/{destination_workstream}/evidence/"
                f"migrated-{source_card['id']}-{attempt_id}.md"
            )
        attempt = {
            "workstream_id": destination_workstream,
            "card_id": source_card["id"],
            "attempt": attempt_id,
            "verdict": verdict,
            "evidence_path": evidence_path,
            "subject": {
                "class": "git_blob",
                "repository": subject["repository"],
                "commit": subject["commit"],
                "path": subject["path"],
                "blob": subject["blob"],
            },
            "acceptance": {
                "class": "task_card",
                "path": (
                    f"implementation/workstreams/{destination_workstream}/cards/"
                    f"{source_card['id']}.md"
                ),
            },
            "independence": {
                "materially_produced_or_repaired_subject": False,
                "basis": basis,
            },
        }
        if verdict in {"pending", "in_progress"}:
            # A migrated active attempt is newly materialized V2 state, not historical
            # terminal review history, so bind it to the explicit PWv2.1 discovery
            # contract rather than relying on the legacy compatibility projection.
            attempt.update({
                "review_kind": "discovery",
                "source_discovery_attempt": "",
                "discovery_complete": False,
                "material_finding_ids": [],
                "review_scope": "card",
                "review_epoch": "E01",
                "epoch_reset_basis": "",
                "material_defect_class_ids": [],
                "post_convergence_validation": False,
                "convergence_basis": "",
            })
        attempts.append(attempt)
        refs.append({
            "class": "review_attempt",
            "path": (
                f"implementation/workstreams/{destination_workstream}/reviews/"
                f"{source_card['id']}-{attempt_id}.toml"
            ),
        })

    if attempts[-1]["verdict"] != review_state:
        return [], [], (
            f"V1 current review state {review_state!r} does not match exact proof "
            f"{attempts[-1]['verdict']!r}"
        )
    nonterminal = [a for a in attempts if a["verdict"] in {"pending", "in_progress"}]
    if len(nonterminal) > 1 or (nonterminal and attempts[-1] is not nonterminal[-1]):
        return [], [], "review proof history has invalid non-terminal ordering"
    return attempts, refs, None


def convert_dry_run(
    *,
    plan: dict[str, Any],
    board_text: str,
    manifest_text: str | None,
    review_proofs: dict[str, list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    """Build a canonical V2 bundle in memory. This function performs no writes."""
    if plan.get("schema") != "pwv2-m06-dry-run-v1" or plan.get("valid") is not True:
        raise MigrationInputError("conversion requires a GREEN exact M06 dry run")
    source = plan.get("source")
    if not isinstance(source, dict):
        raise MigrationInputError("conversion plan is missing exact source identity")
    expected_fingerprint = hashlib.sha256(
        json.dumps(source, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if plan.get("source_fingerprint") != expected_fingerprint:
        raise MigrationInputError("conversion plan source fingerprint is inconsistent")
    actual_board_sha256 = _digest(board_text)
    actual_manifest_sha256 = _digest(manifest_text) if manifest_text is not None else None
    if source.get("board_sha256") != actual_board_sha256:
        raise MigrationInputError("conversion board diverges from GREEN dry-run source")
    if source.get("manifest_sha256") != actual_manifest_sha256:
        raise MigrationInputError("conversion manifest diverges from GREEN dry-run source")

    source_class = source["class"]
    board = parse_bounded_yaml(board_text)
    manifest = parse_bounded_yaml(manifest_text) if manifest_text is not None else None
    if manifest is not None:
        validate_manifest(manifest, source_class)
    validate_board(board, source_class, manifest)

    destination_workstream = plan["destination"]["workstream_id"]
    source_branch = board["execution_ref"]["branch"]
    live_branch = (
        source_branch
        if source_class != "legacy_root_yaml_v1"
        else f"migration/{destination_workstream}"
    )
    created_from = (
        manifest.get("base_ref")
        if manifest is not None and isinstance(manifest.get("base_ref"), str)
        and SHA40.fullmatch(manifest["base_ref"])
        else plan["source"]["commit"]
    )
    integration_target = (
        manifest.get("integration_target")
        if manifest is not None
        else "main"
    )
    workstream: dict[str, Any] = {
        "kind": (manifest.get("kind") if manifest is not None else "migration") or "migration",
        "workstream_id": destination_workstream,
        "branch": live_branch,
        "created_from": created_from,
        "integration_target": integration_target,
        "authority": _authority_locators(manifest, board),
        "task_board": {
            "class": "task_board",
            "path": f"implementation/workstreams/{destination_workstream}/TASK_BOARD.toml",
        },
    }

    artifact_plan: list[dict[str, str]] = []
    review_attempts: dict[str, list[dict[str, Any]]] = {}
    review_obligations: list[dict[str, str]] = []
    result_provenance: list[dict[str, Any]] = []
    canonical_cards: list[dict[str, Any]] = []
    proofs = review_proofs or {}

    for source_card in board["cards"]:
        card_id = source_card["id"]
        status = source_card["execution_status"]
        canonical: dict[str, Any] = {
            "id": card_id,
            "status": status,
            "contract": {
                "class": "task_card",
                "path": f"implementation/workstreams/{destination_workstream}/cards/{card_id}.md",
            },
        }
        source_contract = source_card.get("contract")
        if isinstance(source_contract, str) and source_contract:
            artifact_plan.append({
                "kind": "task_card",
                "source": source_contract,
                "destination": canonical["contract"]["path"],
            })

        if status == "done":
            result_path = f"implementation/workstreams/{destination_workstream}/results/{card_id}.md"
            canonical["result"] = {"class": "result", "path": result_path}
            result_provenance.append({
                "card_id": card_id,
                "source_result_commit": source_card.get("result_commit"),
                "source_result_pr": source_card.get("result_pr"),
                "source_evidence": source_card.get("evidence"),
                "destination": result_path,
            })

        attempts, refs, review_problem = _normalized_review_attempts(
            source_card=source_card,
            destination_workstream=destination_workstream,
            proof=proofs.get(card_id),
        )
        if attempts:
            canonical["review_attempts"] = refs
            review_attempts[card_id] = attempts
            for attempt, ref in zip(attempts, refs):
                if attempt["evidence_path"]:
                    source_attempt = next(
                        item for item in proofs[card_id] if (item.get("attempt") or "") == attempt["attempt"]
                    )
                    artifact_plan.append({
                        "kind": "review_evidence",
                        "source": source_attempt["evidence_path"],
                        "destination": attempt["evidence_path"],
                    })
        if review_problem is not None:
            blocker_path = (
                f"implementation/workstreams/{destination_workstream}/blockers/"
                f"{card_id}-migration-review.toml"
            )
            canonical["status"] = "blocked"
            canonical["blocker"] = {"class": "blocker", "path": blocker_path}
            review_obligations.append({
                "card_id": card_id,
                "source_review_state": str(source_card.get("review_state")),
                "source_review_subject": str(source_card.get("review_subject")),
                "source_review_evidence": str(source_card.get("review_evidence")),
                "reason": review_problem,
                "blocker_path": blocker_path,
            })
        elif attempts and attempts[-1]["verdict"] in {"pending", "in_progress", "red"}:
            review_state = attempts[-1]["verdict"]
            blocker_path = (
                f"implementation/workstreams/{destination_workstream}/blockers/"
                f"{card_id}-{review_state.replace('_', '-')}-review.toml"
            )
            canonical["status"] = "blocked"
            canonical["blocker"] = {"class": "blocker", "path": blocker_path}
            reason = (
                "exact RED history is preserved and corrective review remains outstanding"
                if review_state == "red"
                else f"exact {review_state} review remains outstanding and blocks completion"
            )
            review_obligations.append({
                "card_id": card_id,
                "source_review_state": review_state,
                "source_review_subject": str(source_card.get("review_subject")),
                "source_review_evidence": str(source_card.get("review_evidence")),
                "reason": reason,
                "blocker_path": blocker_path,
            })
        canonical_cards.append(canonical)

    task_board: dict[str, Any] = {
        "workstream_id": destination_workstream,
        "revision": 0,
        "execution_ref": {"branch": live_branch},
        "cards": canonical_cards,
    }
    source_research = board.get("research_obligation")
    if source_research is not None:
        research_path = f"implementation/workstreams/{destination_workstream}/RESEARCH.toml"
        locator = {"class": "research", "path": research_path}
        task_board["research_obligation"] = locator
        workstream["research"] = locator
        artifact_plan.append({
            "kind": "research",
            "source": str(source_research),
            "destination": research_path,
        })

    provenance = {
        "source": plan["source"],
        "source_fingerprint": plan["source_fingerprint"],
        "source_branch": source_branch,
        "source_base_ref": manifest.get("base_ref") if manifest is not None else None,
        "source_parent_workstream": manifest.get("parent_workstream") if manifest is not None else None,
        "source_parent_branch": manifest.get("parent_branch") if manifest is not None else None,
        "source_parent_dependency": manifest.get("parent_dependency") if manifest is not None else None,
        "source_integration_target": integration_target,
        "source_plan_revision": board.get("plan_revision"),
        "source_current_milestone": board.get("current_milestone"),
        "source_milestones": board.get("milestones"),
        "source_review_snapshots": [
            {
                "card_id": card["id"],
                "review_state": card.get("review_state"),
                "review_subject": card.get("review_subject"),
                "review_evidence": card.get("review_evidence"),
            }
            for card in board["cards"]
            if card.get("review_state") is not None
        ],
    }
    bundle = {
        "schema": "pwv2-m06-conversion-v1",
        "source_fingerprint": plan["source_fingerprint"],
        "workstream": workstream,
        "task_board": task_board,
        "review_attempts": review_attempts,
        "review_obligations": review_obligations,
        "result_provenance": result_provenance,
        "artifact_plan": artifact_plan,
        "provenance": provenance,
    }
    bundle["output_fingerprint"] = hashlib.sha256(
        json.dumps(bundle, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return bundle


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
