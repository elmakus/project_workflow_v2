#!/usr/bin/env python3
"""Non-mutating adversarial repros for PWv2 commit 4fb4bfb7d7b1481d6f347c182fc96a5a1135e045.

Run from any checkout of that exact commit:
    python audits/swarm/k7m2q9v4x1c8n5r0t6w3z8pa/repros/router_adversarial_repros.py

The script uses the production selector and the repository's own fixture helpers.
"""

from __future__ import annotations

from pathlib import Path
import runpy
import sys


ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tools.router import select_route  # noqa: E402


TEST_NS = runpy.run_path(str(ROOT / "tests" / "test_router.py"))
RouterTests = TEST_NS["RouterTests"]
MANIFEST = TEST_NS["MANIFEST"]
BOARD = TEST_NS["BOARD"]
CARD = TEST_NS["CARD"]


def case() -> object:
    return RouterTests(
        methodName="test_valid_state_selects_same_route_independent_of_runtime_noise"
    )


def route(project: Path):
    return select_route(project, [MANIFEST], package_root=ROOT)


def observed(name: str, routed) -> None:
    print(
        f"{name}: {routed.disposition}/{routed.obligation}"
        f" subject={routed.subject!r}"
    )


def repro_explicit_user_stop_bypass() -> None:
    c = case()
    temp, project = c.copy_fixture()
    try:
        c.install_green_definition(project)
        c.install_state_record(
            project,
            "planning",
            "planning",
            "PLANNING.toml",
            c.planning_content(
                state="approved",
                premium_b="satisfied",
                premium_c="satisfied",
            ),
        )
        c.install_state_record(
            project,
            "plan_review",
            "plan_review",
            "PLAN_REVIEW.toml",
            c.plan_review_content("green"),
        )
        brainstorm = project / "implementation/workstreams/sample-workstream/BRAINSTORM.toml"
        brainstorm.write_text(
            brainstorm.read_text().replace(
                "explicit_user_stop = false",
                "explicit_user_stop = true",
            )
        )
        routed = route(project)
        observed("F1 explicit user stop bypass", routed)
        assert (routed.disposition, routed.obligation) == ("route", "execution")
    finally:
        temp.cleanup()


def repro_done_required_review_bypass() -> None:
    c = case()
    temp, project = c.copy_fixture()
    try:
        c.install_reviewable_result(project, "required")
        before = route(project)
        assert (before.disposition, before.obligation) == ("route", "review_freeze")

        board = project / BOARD
        board.write_text(
            board.read_text().replace(
                'status = "in_progress"',
                'status = "done"',
                1,
            )
        )
        routed = route(project)
        observed("F2 DONE required-review bypass", routed)
        assert (routed.disposition, routed.obligation) == ("route", "close")
    finally:
        temp.cleanup()


def repro_result_bytes_change_under_green() -> None:
    c = case()
    temp, project = c.copy_fixture()
    try:
        result_path = c.install_reviewable_result(project, "required")
        c.add_review_attempt(project, "green")
        baseline = route(project)
        assert baseline.obligation == "post_review_finalization"

        result_file = project / result_path
        result_file.write_text(
            result_file.read_text().replace(
                "- Tests/readback summary: GREEN",
                "- Tests/readback summary: CHANGED AFTER GREEN",
            )
        )
        routed = route(project)
        observed("F3 changed result bytes under old GREEN", routed)
        assert routed.obligation == "post_review_finalization"
    finally:
        temp.cleanup()


def repro_ready_dependency_bytes_change() -> None:
    c = case()
    temp, project = c.copy_fixture()
    try:
        dependency_path = (
            "implementation/workstreams/sample-workstream/results/M01-T03.md"
        )
        commit = "a" * 40
        blob = "b" * 40
        dependency = f"{dependency_path}@{commit}:{blob}"
        c.install_done_predecessor(
            project,
            path=dependency_path,
            commit=commit,
            blob=blob,
        )
        c.make_ready_card(project, dependencies=dependency)
        baseline = route(project)
        assert baseline.obligation == "execution_prep"

        (project / dependency_path).write_text(
            "# materially changed predecessor bytes under unchanged claimed identity\n"
        )
        routed = route(project)
        observed("F3 changed dependency bytes under unchanged tuple", routed)
        assert routed.obligation == "execution_prep"
    finally:
        temp.cleanup()


def repro_task_card_review_downgrade() -> None:
    c = case()
    temp, project = c.copy_fixture()
    try:
        c.install_reviewable_result(project, "required")
        before = route(project)
        assert before.obligation == "review_freeze"

        card = project / CARD
        card.write_text(
            card.read_text().replace(
                "- Review requirement: required",
                "- Review requirement: none",
            )
        )
        routed = route(project)
        observed("F4 mutable Task Card review downgrade", routed)
        assert routed.obligation == "result_reconciliation"
    finally:
        temp.cleanup()


def repro_research_return_to_nonexistent_card() -> None:
    c = case()
    temp, project = c.copy_fixture()
    try:
        c.install_board_research(project, state="complete", reconciliation="pending")
        research = project / "implementation/workstreams/sample-workstream/RESEARCH.toml"
        research.write_text(
            research.read_text().replace(
                'return_target = "execution_resolution:M01-T04"',
                'return_target = "execution_resolution:M99-T99"',
            )
        )
        routed = route(project)
        observed("F5 Research return to nonexistent Card", routed)
        assert (
            routed.disposition,
            routed.obligation,
            routed.subject,
        ) == ("route", "execution_resolution", "M99-T99")
    finally:
        temp.cleanup()


def repro_missing_green_review_evidence() -> None:
    c = case()
    temp, project = c.copy_fixture()
    try:
        c.install_reviewable_result(project, "required")
        review_path = c.add_review_attempt(project, "green")
        review = project / review_path
        old = (
            "implementation/workstreams/sample-workstream/"
            "evidence/review-R01.md"
        )
        review.write_text(
            review.read_text().replace(
                f'evidence_path = "{old}"',
                'evidence_path = "missing/review.md"',
            )
        )
        assert not (project / "missing/review.md").exists()
        routed = route(project)
        observed("F6 missing terminal review evidence", routed)
        assert routed.obligation == "post_review_finalization"
    finally:
        temp.cleanup()


def main() -> None:
    repro_explicit_user_stop_bypass()
    repro_done_required_review_bypass()
    repro_result_bytes_change_under_green()
    repro_ready_dependency_bytes_change()
    repro_task_card_review_downgrade()
    repro_research_return_to_nonexistent_card()
    repro_missing_green_review_evidence()
    print("All adversarial defect observations reproduced.")


if __name__ == "__main__":
    main()
