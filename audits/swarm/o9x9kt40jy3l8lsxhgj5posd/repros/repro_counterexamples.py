#!/usr/bin/env python3
"""Non-mutating repros for PWv2 swarm audit o9x9kt40jy3l8lsxhgj5posd.

Run from the exact audited checkout. This script copies the repository's router
fixture to temporary directories and calls production selector/validators.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from tools.router import select_route
from tools.state_contract import validate_plan_review, validate_planning

ROOT = Path(__file__).resolve().parents[4]
FIXTURE = ROOT / "tests/fixtures/router/valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"
RESULT = "implementation/workstreams/sample-workstream/results/M01-T04.md"
A = "a" * 40
B = "b" * 40
C = "c" * 40


def fresh_project():
    tmp = tempfile.TemporaryDirectory()
    project = Path(tmp.name) / "project"
    shutil.copytree(FIXTURE, project)
    return tmp, project


def write_card(project: Path, review: str) -> None:
    (project / CARD).write_text(
        "# Task Card\n"
        "- Card ID: M01-T04\n"
        "- Included scope: bounded implementation\n"
        "- Excluded scope: unrelated work\n"
        "- Authority refs: requirements/PROJECT_WORKFLOW_V2.md\n"
        "- Dependencies: none\n"
        "- Acceptance: exact behavior is verified\n"
        "- Required tests/readback: production selector\n"
        f"- Review requirement: {review}\n"
        "- Technical contract: none\n",
        encoding="utf-8",
    )


def add_result(project: Path, *, create_file: bool = True) -> None:
    board = project / BOARD
    board.write_text(
        board.read_text(encoding="utf-8")
        + "\n[cards.result]\n"
        + 'class = "result"\n'
        + f'path = "{RESULT}"\n'
        + f'commit = "{A}"\n'
        + f'blob = "{B}"\n',
        encoding="utf-8",
    )
    if create_file:
        result = project / RESULT
        result.parent.mkdir(parents=True, exist_ok=True)
        result.write_text(
            "# Card Result\n"
            "- Card ID: M01-T04\n"
            f"- Implementation subject: owner/repo@commit:{A}\n"
            "- Evidence refs: implementation/workstreams/sample-workstream/evidence/M01-T04.md\n"
            "- Tests/readback summary: GREEN\n",
            encoding="utf-8",
        )


def add_green_review(project: Path) -> None:
    review_path = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
    board = project / BOARD
    board.write_text(
        board.read_text(encoding="utf-8").replace(
            'status = "in_progress"\n',
            'status = "in_progress"\n'
            f'review_attempts = [{{ class = "review_attempt", path = "{review_path}" }}]\n',
            1,
        ),
        encoding="utf-8",
    )
    path = project / review_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        'workstream_id = "sample-workstream"\n'
        'card_id = "M01-T04"\n'
        'attempt = "R01"\n'
        'verdict = "green"\n'
        'evidence_path = "implementation/workstreams/sample-workstream/evidence/review-R01.md"\n'
        '[subject]\n'
        'class = "git_blob"\n'
        'repository = "owner/router-fixture"\n'
        f'commit = "{A}"\n'
        f'path = "{RESULT}"\n'
        f'blob = "{B}"\n'
        '[acceptance]\n'
        'class = "task_card"\n'
        f'path = "{CARD}"\n'
        '[independence]\n'
        'materially_produced_or_repaired_subject = false\n'
        'basis = "Fresh semantic reviewer context."\n',
        encoding="utf-8",
    )


def repro_done_review_bypass() -> None:
    tmp, project = fresh_project()
    try:
        write_card(project, "required")
        board = project / BOARD
        board.write_text(
            board.read_text(encoding="utf-8").replace(
                'status = "in_progress"', 'status = "done"', 1
            ),
            encoding="utf-8",
        )
        add_result(project, create_file=False)
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print("F1", routed.disposition, routed.obligation)
        assert (routed.disposition, routed.obligation) == ("route", "close")
    finally:
        tmp.cleanup()


def repro_mutated_result_reuses_green() -> None:
    tmp, project = fresh_project()
    try:
        write_card(project, "required")
        add_result(project)
        add_green_review(project)
        first = select_route(project, [MANIFEST], package_root=ROOT)
        assert first.obligation == "post_review_finalization"

        result = project / RESULT
        result.write_text(
            result.read_text(encoding="utf-8").replace(
                "Tests/readback summary: GREEN",
                "Tests/readback summary: MATERIAL CONTENT CHANGED AFTER REVIEW",
            ),
            encoding="utf-8",
        )
        second = select_route(project, [MANIFEST], package_root=ROOT)
        print("F2", second.disposition, second.obligation)
        assert second.obligation == "post_review_finalization"
    finally:
        tmp.cleanup()


def repro_editorial_exemption_is_content_blind() -> None:
    base = f"owner/repo@{A}:planning/MASTER_PLAN.md@{B}"
    planning = {
        "workstream_id": "sample-workstream",
        "cycle": 1,
        "entry_subject": "definition:R1|planning-cycle:1",
        "revision": "P1",
        "state": "approved",
        "planner_audit": "green",
        "plan_path": "planning/MASTER_PLAN.md",
        "review_mode": "editorial_exempt",
        "review_exemption_basis": "Wording only; strategy, milestones, coverage and gates unchanged.",
        "review_exemption_base_subject": base,
        "premium_a": "satisfied",
        "premium_a_subject": "definition:R1|planning-cycle:1",
        "premium_b": "satisfied",
        "premium_b_subject": base,
        "premium_c": "satisfied",
        "premium_c_subject": base,
        "subject": {
            "repository": "owner/repo",
            "commit": A,
            "path": "planning/MASTER_PLAN.md",
            "blob": C,
        },
    }
    review = {
        "workstream_id": "sample-workstream",
        "plan_revision": "P1",
        "planning_cycle": 1,
        "attempt": "R01",
        "verdict": "green",
        "evidence_path": "evidence/plan-review-R01.md",
        "subject": {
            "class": "git_blob",
            "repository": "owner/repo",
            "commit": A,
            "path": "planning/MASTER_PLAN.md",
            "blob": B,
        },
        "acceptance": {"class": "authority", "path": "requirements/REQUIREMENTS.md"},
        "independence": {
            "materially_produced_or_repaired_subject": False,
            "basis": "Fresh semantic review context.",
        },
    }
    validate_planning(planning, "sample-workstream")
    validate_plan_review(review, "sample-workstream", planning)
    print("F3 accepted changed plan subject solely from metadata/basis")


def repro_blocked_result_is_ignored() -> None:
    tmp, project = fresh_project()
    try:
        write_card(project, "none")
        add_result(project)
        blocker = "implementation/workstreams/sample-workstream/blockers/M01-T04.toml"
        board = project / BOARD
        text = board.read_text(encoding="utf-8")
        text = text.replace('status = "in_progress"', 'status = "blocked"', 1)
        text = text.replace(
            "[cards.contract]\n",
            f'[cards.blocker]\nclass = "blocker"\npath = "{blocker}"\n\n[cards.contract]\n',
            1,
        )
        board.write_text(text, encoding="utf-8")
        path = project / blocker
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            'workstream_id = "sample-workstream"\n'
            'card_id = "M01-T04"\n'
            'class = "bounded_correction"\n'
            'summary = "Synthetic blocker coexists with durable result."\n'
            'evidence_path = ""\n',
            encoding="utf-8",
        )
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print("F4", routed.disposition, routed.obligation)
        assert (routed.disposition, routed.obligation) == ("route", "execution")
    finally:
        tmp.cleanup()


if __name__ == "__main__":
    repro_done_review_bypass()
    repro_mutated_result_reuses_green()
    repro_editorial_exemption_is_content_blind()
    repro_blocked_result_is_ignored()
