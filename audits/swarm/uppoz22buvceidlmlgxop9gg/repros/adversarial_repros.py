#!/usr/bin/env python3
"""Non-mutating adversarial probes for PWv2 subject 4fb4bfb7d7b1481d6f347c182fc96a5a1135e045.

Run from the repository root at that exact commit:
    python3 audits/swarm/uppoz22buvceidlmlgxop9gg/repros/adversarial_repros.py
"""

from pathlib import Path

from tools.router import select_route
from tests.test_router import BOARD, CARD, MANIFEST, ROOT, RouterTests


def route(project: Path):
    return select_route(project, [MANIFEST], package_root=ROOT)


def f1_done_bypasses_result_and_required_review() -> None:
    helper = RouterTests()
    temp, project = helper.copy_fixture()
    try:
        # Make the stable Card explicitly review-required.
        (project / CARD).write_text(
            helper.task_card_content(review_requirement="required"),
            encoding="utf-8",
        )
        result_path = "implementation/workstreams/sample-workstream/results/M01-T04.md"
        board = project / BOARD
        board.write_text(
            board.read_text(encoding="utf-8")
            .replace('status = "in_progress"', 'status = "done"', 1)
            + '\n[cards.result]\n'
            + 'class = "result"\n'
            + f'path = "{result_path}"\n',
            encoding="utf-8",
        )
        # Intentionally do NOT create the result file and do NOT create a review attempt.
        assert not (project / result_path).exists()
        routed = route(project)
        print("F1", routed.disposition, routed.obligation, routed.read_set)
        assert (routed.disposition, routed.obligation) == ("route", "close")
        assert f"project:{result_path}" not in routed.read_set
        assert f"project:{CARD}" not in routed.read_set
    finally:
        temp.cleanup()


def f2_forged_result_identity_can_finalize_green() -> None:
    helper = RouterTests()
    temp, project = helper.copy_fixture()
    try:
        # Existing helper writes arbitrary a*40/b*40 identities into Board+review.
        # The temporary project is not a Git repository, so those identities cannot
        # resolve to immutable Git objects here.
        helper.install_reviewable_result(project, "required")
        helper.add_review_attempt(project, "green")
        assert not (project / ".git").exists()
        routed = route(project)
        print("F2-result", routed.disposition, routed.obligation, routed.read_set)
        assert (routed.disposition, routed.obligation) == (
            "route",
            "post_review_finalization",
        )
    finally:
        temp.cleanup()


def f2_forged_plan_identity_can_reach_execution() -> None:
    helper = RouterTests()
    temp, project = helper.copy_fixture()
    try:
        # RouterTests.planning_content uses repository owner/repo + synthetic hashes,
        # while PROJECT.md declares owner/router-fixture. It also does not create
        # planning/MASTER_PLAN.md or the terminal Plan Review evidence file.
        helper.install_approved_plan(project)
        plan = project / "planning/MASTER_PLAN.md"
        assert not plan.exists()
        routed = route(project)
        print("F2-plan", routed.disposition, routed.obligation, routed.read_set)
        assert (routed.disposition, routed.obligation) == ("route", "execution")
        assert "project:planning/MASTER_PLAN.md" not in routed.read_set
    finally:
        temp.cleanup()


def f3_orphan_execution_research_preempts_board() -> None:
    helper = RouterTests()
    temp, project = helper.copy_fixture()
    try:
        manifest = project / MANIFEST
        manifest.write_text(
            manifest.read_text(encoding="utf-8")
            + '\n[research]\nclass = "research"\n'
            + 'path = "implementation/workstreams/sample-workstream/RESEARCH.toml"\n',
            encoding="utf-8",
        )
        research = project / "implementation/workstreams/sample-workstream/RESEARCH.toml"
        research.write_text(
            'state = "active"\n'
            'workstream_id = "sample-workstream"\n'
            'origin_role = "execution"\n'
            'origin_subject = "M01-T04"\n'
            'return_target = "execution:M01-T04"\n'
            'return_reconciliation = "pending"\n'
            'return_result = ""\n'
            'finding = ""\n'
            'limitations = ""\n'
            'conflicts = ""\n'
            '[[sources]]\nclass = "official_upstream"\nstatus = "pending"\nweight = "primary"\n'
            '[[sources]]\nclass = "project_runtime"\nstatus = "pending"\nweight = "direct"\n'
            '[[sources]]\nclass = "tracker_discussion"\nstatus = "pending"\nweight = "supporting"\n'
            '[[sources]]\nclass = "practitioner_community"\nstatus = "pending"\nweight = "supporting"\n',
            encoding="utf-8",
        )
        # Deliberately leave Task Board without research_obligation.
        assert "research_obligation" not in (project / BOARD).read_text(encoding="utf-8")
        routed = route(project)
        print("F3", routed.disposition, routed.obligation, routed.read_set)
        assert (routed.disposition, routed.obligation) == ("route", "research")
        assert f"project:{BOARD}" not in routed.read_set
    finally:
        temp.cleanup()


def f4_nonblocked_human_blocker_is_ignored() -> None:
    helper = RouterTests()
    temp, project = helper.copy_fixture()
    try:
        blocker_path = (
            "implementation/workstreams/sample-workstream/"
            "blockers/M01-T04.toml"
        )
        board = project / BOARD
        board.write_text(
            board.read_text(encoding="utf-8").replace(
                "[cards.contract]\n",
                "[cards.blocker]\n"
                'class = "blocker"\n'
                f'path = "{blocker_path}"\n\n'
                "[cards.contract]\n",
                1,
            ),
            encoding="utf-8",
        )
        blocker = project / blocker_path
        blocker.parent.mkdir(parents=True, exist_ok=True)
        blocker.write_text(
            'workstream_id = "sample-workstream"\n'
            'card_id = "M01-T04"\n'
            'class = "human_authority"\n'
            'summary = "Human authorization is unresolved."\n'
            'evidence_path = ""\n',
            encoding="utf-8",
        )
        # Card remains in_progress even though it carries a human-authority blocker.
        assert 'status = "in_progress"' in board.read_text(encoding="utf-8")
        routed = route(project)
        print("F4", routed.disposition, routed.obligation, routed.read_set)
        assert (routed.disposition, routed.obligation) == ("route", "execution")
        assert f"project:{blocker_path}" not in routed.read_set
    finally:
        temp.cleanup()


if __name__ == "__main__":
    f1_done_bypasses_result_and_required_review()
    f2_forged_result_identity_can_finalize_green()
    f2_forged_plan_identity_can_reach_execution()
    f3_orphan_execution_research_preempts_board()
    f4_nonblocked_human_blocker_is_ignored()
    print("All four material defect classes reproduced.")
