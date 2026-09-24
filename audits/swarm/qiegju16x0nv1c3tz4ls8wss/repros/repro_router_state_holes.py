#!/usr/bin/env python3
"""Non-mutating reproductions for router/state defects. Run from exact audit subject checkout."""

from __future__ import annotations

import hashlib
from pathlib import Path

from tests.test_router import BOARD, MANIFEST, RouterTests, ROOT
from tools.router import select_route


def git_blob_oid(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def f1_done_bypasses_required_red_review() -> None:
    t = RouterTests()
    temp, project = t.copy_fixture()
    try:
        t.install_reviewable_result(project, "required")
        t.add_review_attempt(project, "red")
        board = project / BOARD
        board.write_text(board.read_text().replace('status = "in_progress"', 'status = "done"', 1))
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print("F1", routed.disposition, routed.obligation)
        assert (routed.disposition, routed.obligation) == ("route", "close")
    finally:
        temp.cleanup()


def f2_satisfied_jit_trigger_is_skipped_by_close() -> None:
    t = RouterTests()
    temp, project = t.copy_fixture()
    try:
        t.install_reviewable_result(project, "none")
        board = project / BOARD
        board.write_text(
            board.read_text().replace('status = "in_progress"', 'status = "done"', 1)
            + '\n[[jit_triggers]]\n'
              'id = "after-M01-T04"\n'
              'after_card = "M01-T04"\n'
              'state = "satisfied"\n'
              'condition = "Materialize the accepted downstream Card now."\n'
        )
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print("F2", routed.disposition, routed.obligation)
        assert (routed.disposition, routed.obligation) == ("route", "close")
    finally:
        temp.cleanup()


def f3_changed_result_bytes_keep_stale_declared_blob_valid() -> None:
    t = RouterTests()
    temp, project = t.copy_fixture()
    try:
        result_rel = t.install_reviewable_result(project, "none")
        result_path = project / result_rel
        initial = result_path.read_bytes()
        initial_oid = git_blob_oid(initial)

        board = project / BOARD
        board.write_text(board.read_text().replace("b" * 40, initial_oid))
        first = select_route(project, [MANIFEST], package_root=ROOT)

        result_path.write_text(
            result_path.read_text().replace(
                "- Tests/readback summary: GREEN",
                "- Tests/readback summary: CHANGED-BYTES-STILL-SYNTACTICALLY-VALID",
            )
        )
        changed_oid = git_blob_oid(result_path.read_bytes())
        second = select_route(project, [MANIFEST], package_root=ROOT)

        print("F3 declared_blob", initial_oid)
        print("F3 actual_after_change", changed_oid)
        print("F3 routes", first.obligation, second.obligation)
        assert changed_oid != initial_oid
        assert first.obligation == second.obligation == "result_reconciliation"
    finally:
        temp.cleanup()


def f4_stale_planning_survives_definition_revision_change() -> None:
    t = RouterTests()
    temp, project = t.copy_fixture()
    try:
        t.install_approved_plan(project)
        definition = project / "implementation/workstreams/sample-workstream/DEFINITION.toml"
        definition.write_text(definition.read_text().replace('revision = "R1"', 'revision = "R2"', 1))
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print("F4", routed.disposition, routed.obligation, routed.subject)
        assert (routed.disposition, routed.obligation) == ("route", "execution")
    finally:
        temp.cleanup()


def f7_active_research_preempts_explicit_user_stop() -> None:
    t = RouterTests()
    temp, project = t.copy_fixture()
    try:
        t.install_state_record(
            project,
            "brainstorm",
            "brainstorm",
            "BRAINSTORM.toml",
            'workstream_id = "sample-workstream"\n'
            'scope_id = "scope-stop"\n'
            'revision = 1\n'
            'state = "active"\n'
            'challenge_audit = "pending"\n'
            'explicit_user_stop = true\n'
            'promotion_state = "pending"\n'
            'promotion_subject = ""\n',
        )
        t.install_state_record(
            project,
            "research",
            "research",
            "RESEARCH.toml",
            'workstream_id = "sample-workstream"\n'
            'state = "active"\n'
            'origin_role = "brainstorming"\n'
            'origin_subject = "scope-stop@1"\n'
            'return_target = "brainstorming"\n'
            'return_reconciliation = "pending"\n'
            'return_result = ""\n'
            'finding = ""\n'
            'limitations = ""\n'
            'conflicts = ""\n'
            '[[sources]]\nclass = "official_upstream"\nstatus = "pending"\nweight = "primary"\n'
            '[[sources]]\nclass = "project_runtime"\nstatus = "pending"\nweight = "direct"\n'
            '[[sources]]\nclass = "tracker_discussion"\nstatus = "pending"\nweight = "supporting"\n'
            '[[sources]]\nclass = "practitioner_community"\nstatus = "pending"\nweight = "supporting"\n',
        )
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print("F7", routed.disposition, routed.obligation)
        assert (routed.disposition, routed.obligation) == ("route", "research")
    finally:
        temp.cleanup()


if __name__ == "__main__":
    f1_done_bypasses_required_red_review()
    f2_satisfied_jit_trigger_is_skipped_by_close()
    f3_changed_result_bytes_keep_stale_declared_blob_valid()
    f4_stale_planning_survives_definition_revision_change()
    f7_active_research_preempts_explicit_user_stop()
