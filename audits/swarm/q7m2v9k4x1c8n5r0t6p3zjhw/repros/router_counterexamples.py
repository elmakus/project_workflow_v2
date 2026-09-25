#!/usr/bin/env python3
"""Non-mutating PWv2 adversarial reproductions for audit q7m2v9k4x1c8n5r0t6p3zjhw.

Run from a checkout of 4fb4bfb7d7b1481d6f347c182fc96a5a1135e045:
    python3 audits/swarm/q7m2v9k4x1c8n5r0t6p3zjhw/repros/router_counterexamples.py
"""

from pathlib import Path

from tests.test_router import RouterTests, MANIFEST, BOARD, CARD, ROOT
from tools.router import select_route


H = RouterTests()


def route(project: Path):
    r = select_route(project, [MANIFEST], package_root=ROOT)
    return r.disposition, r.obligation, r.reason


def f1_path_only_result():
    temp, project = H.copy_fixture()
    try:
        result_path = "implementation/workstreams/sample-workstream/results/M01-T04.md"
        (project / CARD).write_text(H.task_card_content(review_requirement="none"))
        authority = project / "requirements" / "REQUIREMENTS.md"
        authority.parent.mkdir(parents=True, exist_ok=True)
        authority.write_text("# Accepted authority\n")
        board = project / BOARD
        board.write_text(
            board.read_text()
            + '\n[cards.result]\nclass = "result"\n'
            + f'path = "{result_path}"\n'
        )
        evidence = project / "implementation/workstreams/sample-workstream/evidence/M01-T04.md"
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text("# evidence\n")
        result = project / result_path
        result.parent.mkdir(parents=True, exist_ok=True)
        result.write_text(
            "# Card Result\n"
            "- Card ID: M01-T04\n"
            "- Implementation subject: owner/repo@deadbeef\n"
            "- Evidence refs: implementation/workstreams/sample-workstream/evidence/M01-T04.md\n"
            "- Tests/readback summary: GREEN\n"
        )
        return route(project)
    finally:
        temp.cleanup()


def f2_same_tuple_content_drift():
    temp, project = H.copy_fixture()
    try:
        p = "implementation/workstreams/sample-workstream/results/M01-T03.md"
        commit, blob = "a" * 40, "b" * 40
        dep = f"{p}@{commit}:{blob}"
        H.install_done_predecessor(project, path=p, commit=commit, blob=blob)
        H.make_ready_card(project, dependencies=dep)
        before = route(project)
        (project / p).write_text("# changed bytes, recorded commit/blob unchanged\n")
        after = route(project)
        return before, after
    finally:
        temp.cleanup()


def f3_ready_card_with_result():
    temp, project = H.copy_fixture()
    try:
        H.install_reviewable_result(project, "none")
        board = project / BOARD
        board.write_text(board.read_text().replace('status = "in_progress"', 'status = "ready"', 1))
        return route(project)
    finally:
        temp.cleanup()


def f4_unactivated_recommended_review():
    temp, project = H.copy_fixture()
    try:
        H.install_reviewable_result(project, "recommended")
        return route(project)
    finally:
        temp.cleanup()


def f5_research_masks_explicit_stop():
    temp, project = H.copy_fixture()
    try:
        manifest = project / MANIFEST
        manifest.write_text(
            manifest.read_text()
            + '\n[brainstorm]\nclass = "brainstorm"\n'
              'path = "implementation/workstreams/sample-workstream/BRAINSTORM.toml"\n'
            + '\n[research]\nclass = "research"\n'
              'path = "implementation/workstreams/sample-workstream/RESEARCH.toml"\n'
        )
        ws = project / "implementation/workstreams/sample-workstream"
        (ws / "BRAINSTORM.toml").write_text(
            'workstream_id = "sample-workstream"\n'
            'scope_id = "scope-stop"\n'
            'revision = 1\n'
            'state = "active"\n'
            'challenge_audit = "pending"\n'
            'explicit_user_stop = true\n'
            'promotion_state = "pending"\n'
            'promotion_subject = ""\n'
        )
        (ws / "RESEARCH.toml").write_text(
            'state = "active"\n'
            'workstream_id = "sample-workstream"\n'
            'origin_role = "brainstorming"\n'
            'origin_subject = "scope-stop@1"\n'
            'return_target = "brainstorming"\n'
            'return_reconciliation = "pending"\n'
            'return_result = ""\n'
            'finding = ""\nlimitations = ""\nconflicts = ""\n'
            '[[sources]]\nclass = "official_upstream"\nstatus = "pending"\nweight = "primary"\n'
            '[[sources]]\nclass = "project_runtime"\nstatus = "pending"\nweight = "direct"\n'
            '[[sources]]\nclass = "tracker_discussion"\nstatus = "pending"\nweight = "supporting"\n'
            '[[sources]]\nclass = "practitioner_community"\nstatus = "pending"\nweight = "supporting"\n'
        )
        return route(project)
    finally:
        temp.cleanup()


if __name__ == "__main__":
    print("F1", f1_path_only_result())
    print("F2", f2_same_tuple_content_drift())
    print("F3", f3_ready_card_with_result())
    print("F4", f4_unactivated_recommended_review())
    print("F5", f5_research_masks_explicit_stop())
