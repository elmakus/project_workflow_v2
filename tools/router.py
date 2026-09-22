#!/usr/bin/env python3
"""Minimal runtime-neutral Project Workflow V2 M01 obligation selector."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath

from tools.state_contract import (
    ValidationError,
    read_project,
    read_toml,
    validate_board,
    validate_intake,
    validate_project,
    validate_workstream,
)

PRIORITY_FOUNDATION = (
    "explicit_human_or_premium_boundary",
    "independent_review_or_red_correction",
    "research_return",
    "result_reconciliation",
    "current_card",
    "next_legal_stage",
)

REAL_STOP_FOUNDATION = (
    "explicit_user_stop",
    "unresolved_user_or_product_decision",
    "authorization_alignment_or_promotion_gate",
    "premium_gate",
    "independence_boundary",
    "nonremediable_access_runtime_or_input_blocker",
    "end_of_approved_scope",
)


@dataclass(frozen=True)
class RouteResult:
    disposition: str
    obligation: str
    subject: str | None
    owner_module: str | None
    reason: str
    read_set: tuple[str, ...]


class Reads:
    def __init__(self, project_root: Path, package_root: Path) -> None:
        self.project_root = project_root.resolve()
        self.package_root = package_root.resolve()
        self.items: list[str] = []

    def _read_path(self, root: Path, raw: str, owner: str) -> Path:
        rel = PurePosixPath(raw)
        if rel.is_absolute() or "." in rel.parts or ".." in rel.parts:
            raise ValidationError(f"unsafe {owner} path {raw!r}")
        path = (root / Path(*rel.parts)).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ValidationError(f"{owner} path escapes root: {raw!r}") from exc
        self.items.append(f"{owner}:{raw}")
        return path

    def project(self, raw: str) -> Path:
        return self._read_path(self.project_root, raw, "project")

    def package(self, raw: str) -> Path:
        return self._read_path(self.package_root, raw, "package")


def result(reads: Reads, disposition: str, obligation: str, reason: str,
           subject: str | None = None, owner_module: str | None = None) -> RouteResult:
    return RouteResult(disposition, obligation, subject, owner_module, reason, tuple(reads.items))


def recovery(reads: Reads, reason: str) -> RouteResult:
    try:
        reads.package("workflow/RECOVERY.md").read_text(encoding="utf-8")
    except OSError:
        reason += "; recovery module unreadable"
    return result(reads, "recovery", "recovery_boundary", reason,
                  owner_module="workflow/RECOVERY.md")


def select_route(project_root: Path, selected_workstreams: list[str], *,
                 package_root: Path | None = None, entry: str = "continue") -> RouteResult:
    reads = Reads(project_root, package_root or Path(__file__).resolve().parents[1])
    try:
        reads.package("workflow/ROUTER.md").read_text(encoding="utf-8")
        project = read_project(reads.project("PROJECT.md"))
        validate_project(project)
    except (OSError, ValidationError) as exc:
        return recovery(reads, f"bootstrap project identity invalid: {exc}")

    intake_entries = {
        "new_managed_intent": "change",
        "new_issue": "issue",
        "new_feature": "feature",
    }
    if entry in intake_entries:
        return result(
            reads, "route", "intake",
            "Common Intake owns new managed intent before implementation authority exists",
            subject=intake_entries[entry], owner_module="workflow/INTAKE.md",
        )
    if entry != "continue":
        return recovery(reads, f"unknown entry kind {entry!r}")
    if len(selected_workstreams) != 1:
        return recovery(reads, f"expected exactly one selected workstream, got {len(selected_workstreams)}")

    try:
        manifest_rel = selected_workstreams[0]
        workstream = read_toml(reads.project(manifest_rel))
        validate_workstream(workstream)
        expected_manifest = f"implementation/workstreams/{workstream['workstream_id']}/WORKSTREAM.toml"
        if manifest_rel != expected_manifest:
            raise ValidationError(f"selected manifest must be exact path {expected_manifest!r}")
        intake = None
        if "intake" in workstream:
            intake = read_toml(reads.project(workstream["intake"]["path"]))
            validate_intake(intake, workstream["workstream_id"])
            if intake["state"] == "active":
                if intake["kind"] == "issue" and intake["alignment_state"] == "pending":
                    response = intake["response_kind"]
                    if response == "none":
                        return result(
                            reads, "stop", "issue_alignment",
                            "Issue diagnosis has a proposed repair but no subsequent user alignment response yet",
                            subject=intake["repair_subject"], owner_module="workflow/INTAKE.md",
                        )
                    if response in {"question", "concern", "alternative"}:
                        return result(
                            reads, "unavailable", "brainstorming",
                            "User response continues repair alignment; full Brainstorming semantics arrive in M02-T02",
                            subject=intake["repair_subject"], owner_module="workflow/BRAINSTORMING.md",
                        )
                    return result(
                        reads, "route", "intake",
                        "Explicit authorization response exists and Intake must reconcile the exact aligned subject",
                        subject=intake["repair_subject"], owner_module="workflow/INTAKE.md",
                    )
                return result(
                    reads, "route", "intake",
                    "Selected workstream has active Intake/discovery state",
                    subject=intake["kind"], owner_module="workflow/INTAKE.md",
                )

        if "task_board" not in workstream:
            if intake is None:
                raise ValidationError("selected workstream has neither Intake nor Task Board")
            if intake["kind"] == "issue" and intake["micro_fix_candidate"]:
                return result(
                    reads, "unavailable", "execution_prep",
                    "Aligned issue is a bounded micro-fix candidate; Execution Prep semantics arrive in M03",
                    subject=intake["repair_subject"], owner_module="workflow/EXECUTION_PREP.md",
                )
            return result(
                reads, "unavailable", "brainstorming",
                "Completed pre-execution Intake continues to Brainstorming; full semantics arrive in M02-T02",
                subject=intake["kind"], owner_module="workflow/BRAINSTORMING.md",
            )

        board = read_toml(reads.project(workstream["task_board"]["path"]))
        validate_board(board, workstream)
    except (OSError, ValidationError, KeyError) as exc:
        return recovery(reads, f"selected workstream identity invalid: {exc}")

    active = [card for card in board["cards"] if card["status"] == "in_progress"]
    ready = [card for card in board["cards"] if card["status"] == "ready"]

    if active:
        card = active[0]
        try:
            reads.project(card["contract"]["path"]).read_text(encoding="utf-8")
        except (OSError, ValidationError, KeyError) as exc:
            return recovery(reads, f"current Card contract invalid: {exc}")
        return result(
            reads, "unavailable", "execution",
            "Current Card is identified, but Execution lifecycle semantics are not implemented until M03",
            subject=card["id"], owner_module="workflow/EXECUTION.md",
        )

    if len(ready) == 1:
        card = ready[0]
        try:
            reads.project(card["contract"]["path"]).read_text(encoding="utf-8")
        except (OSError, ValidationError, KeyError) as exc:
            return recovery(reads, f"ready Card contract invalid: {exc}")
        return result(
            reads, "unavailable", "execution",
            "Ready Card is identified, but Execution lifecycle semantics are not implemented until M03",
            subject=card["id"], owner_module="workflow/EXECUTION.md",
        )

    if len(ready) > 1:
        return result(reads, "unavailable", "execution_selection",
                      "Multiple ready Cards require later dependency semantics; M01 does not guess",
                      owner_module="workflow/EXECUTION.md")

    if any(card["status"] == "blocked" for card in board["cards"]):
        return result(reads, "unavailable", "blocked_resolution",
                      "Blocked-Card resolution belongs to later Research/Execution/Recovery semantics")

    if board["cards"] and all(card["status"] == "done" for card in board["cards"]):
        return result(reads, "unavailable", "milestone_finalization",
                      "Milestone finalization/Close is not implemented yet",
                      owner_module="workflow/CLOSE.md")

    return result(reads, "unavailable", "card_preparation",
                  "No executable Card is selected; later Execution Prep/JIT semantics are unavailable in M01")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--workstream", action="append", default=[])
    parser.add_argument("--entry", default="continue")
    args = parser.parse_args()
    routed = select_route(args.project_root, args.workstream, entry=args.entry)
    print(json.dumps(asdict(routed), indent=2))
    return 2 if routed.disposition == "recovery" else 0


if __name__ == "__main__":
    raise SystemExit(main())
