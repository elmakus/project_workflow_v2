#!/usr/bin/env python3
"""Non-mutating adversarial repros for PWv2 selector/state gaps.

Run from an exact checkout of:
4fb4bfb7d7b1481d6f347c182fc96a5a1135e045

The script mutates only TemporaryDirectory fixture copies.
"""

from pathlib import Path

from tools.router import select_route
from tests.test_router import BOARD, MANIFEST, RouterTests


def helper() -> RouterTests:
    return RouterTests("test_active_card_routes_to_runtime_neutral_execution")


def show(name: str, routed) -> None:
    print(f"{name}: {routed.disposition}/{routed.obligation} subject={routed.subject!r}")


def f1_same_path_result_mutation_keeps_green_review() -> None:
    h = helper()
    temp, project = h.copy_fixture()
    try:
        result_path = h.install_reviewable_result(project, "required")
        h.add_review_attempt(project, "green")
        result_file = project / result_path
        result_file.write_text(
            "# Card Result\n"
            "- Card ID: M01-T04\n"
            "- Implementation subject: owner/router-fixture@MUTATED-AFTER-REVIEW\n"
            "- Evidence refs: implementation/workstreams/sample-workstream/evidence/M01-T04.md\n"
            "- Tests/readback summary: syntactically valid but changed at the same path\n",
            encoding="utf-8",
        )
        routed = select_route(project, [MANIFEST])
        show("F1-result", routed)
        assert (routed.disposition, routed.obligation) == (
            "route",
            "post_review_finalization",
        )
    finally:
        temp.cleanup()

    temp, project = h.copy_fixture()
    try:
        dependency_path = (
            "implementation/workstreams/sample-workstream/results/M01-T03.md"
        )
        commit = "a" * 40
        blob = "b" * 40
        dependency = f"{dependency_path}@{commit}:{blob}"
        h.install_done_predecessor(
            project, path=dependency_path, commit=commit, blob=blob
        )
        h.make_ready_card(project, dependencies=dependency)
        (project / dependency_path).write_text(
            "# same path, changed bytes, metadata left unchanged\n",
            encoding="utf-8",
        )
        routed = select_route(project, [MANIFEST])
        show("F1-dependency", routed)
        assert (routed.disposition, routed.obligation) == (
            "route",
            "execution_prep",
        )
    finally:
        temp.cleanup()


def f2_missing_terminal_evidence_is_not_dereferenced() -> None:
    h = helper()
    temp, project = h.copy_fixture()
    try:
        h.install_reviewable_result(project, "required")
        h.add_review_attempt(project, "green")
        (project / (
            "implementation/workstreams/sample-workstream/"
            "evidence/review-R01.md"
        )).unlink()
        (project / (
            "implementation/workstreams/sample-workstream/"
            "evidence/M01-T04.md"
        )).unlink()
        routed = select_route(project, [MANIFEST])
        show("F2", routed)
        assert (routed.disposition, routed.obligation) == (
            "route",
            "post_review_finalization",
        )
    finally:
        temp.cleanup()


def f3_research_short_circuits_explicit_user_stop() -> None:
    h = helper()
    temp, project = h.copy_fixture()
    try:
        h.install_state_record(
            project,
            "brainstorm",
            "brainstorm",
            "BRAINSTORM.toml",
            (
                'workstream_id = "sample-workstream"\n'
                'scope_id = "scope-stop"\n'
                'revision = 1\n'
                'state = "active"\n'
                'challenge_audit = "pending"\n'
                'explicit_user_stop = true\n'
                'promotion_state = "pending"\n'
                'promotion_subject = ""\n'
            ),
        )
        h.install_state_record(
            project,
            "research",
            "research",
            "RESEARCH.toml",
            (
                'state = "active"\n'
                'workstream_id = "sample-workstream"\n'
                'origin_role = "brainstorming"\n'
                'origin_subject = "scope-stop@1"\n'
                'return_target = "brainstorming"\n'
                'return_reconciliation = "pending"\n'
                'return_result = ""\n'
                'finding = ""\n'
                'limitations = ""\n'
                'conflicts = ""\n'
                '[[sources]]\nclass = "official_upstream"\n'
                'status = "pending"\nweight = "primary"\n'
                '[[sources]]\nclass = "project_runtime"\n'
                'status = "pending"\nweight = "direct"\n'
                '[[sources]]\nclass = "tracker_discussion"\n'
                'status = "pending"\nweight = "supporting"\n'
                '[[sources]]\nclass = "practitioner_community"\n'
                'status = "pending"\nweight = "supporting"\n'
            ),
        )
        routed = select_route(project, [MANIFEST])
        show("F3", routed)
        assert (routed.disposition, routed.obligation) == ("route", "research")
        assert not any("BRAINSTORM.toml" in item for item in routed.read_set)
    finally:
        temp.cleanup()


def f4_definition_accepts_non_promoted_brainstorm_state() -> None:
    h = helper()
    temp, project = h.copy_fixture()
    try:
        h.install_green_definition(project)
        brainstorm = (
            project
            / "implementation/workstreams/sample-workstream/BRAINSTORM.toml"
        )
        brainstorm.write_text(
            brainstorm.read_text(encoding="utf-8").replace(
                'state = "promoted"', 'state = "active"'
            ),
            encoding="utf-8",
        )
        routed = select_route(project, [MANIFEST])
        show("F4", routed)
        assert (routed.disposition, routed.obligation) == ("route", "planning")
    finally:
        temp.cleanup()


def f5_done_card_bypasses_result_and_review_validation() -> None:
    h = helper()
    temp, project = h.copy_fixture()
    try:
        result_path = h.install_reviewable_result(project, "required")
        board = project / BOARD
        board.write_text(
            board.read_text(encoding="utf-8").replace(
                'status = "in_progress"', 'status = "done"', 1
            ),
            encoding="utf-8",
        )
        (project / result_path).unlink()
        routed = select_route(project, [MANIFEST])
        show("F5", routed)
        assert (routed.disposition, routed.obligation) == ("route", "close")
    finally:
        temp.cleanup()


if __name__ == "__main__":
    f1_same_path_result_mutation_keeps_green_review()
    f2_missing_terminal_evidence_is_not_dereferenced()
    f3_research_short_circuits_explicit_user_stop()
    f4_definition_accepts_non_promoted_brainstorm_state()
    f5_done_card_bypasses_result_and_review_validation()
    print("All five selector/state defect classes reproduced.")
