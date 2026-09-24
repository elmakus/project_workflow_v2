#!/usr/bin/env python3
"""Non-mutating reproductions for PWv2 adversarial audit 8wu3nv7atoj98fvx5u4a1lzs.

Run from repository root:
    python audits/swarm/8wu3nv7atoj98fvx5u4a1lzs/repros/repro_router_counterexamples.py

A successful run means every asserted buggy route was reproduced.
"""

from pathlib import Path

from tests.test_router import BOARD, CARD, MANIFEST, ROOT, RouterTests
from tools.router import select_route


HELPER = RouterTests()


def route(project: Path):
    return select_route(project, [MANIFEST], package_root=ROOT)


def observed(name: str, routed) -> None:
    print(f"{name}: {routed.disposition}/{routed.obligation} subject={routed.subject!r}")


def F1_dependency_bytes() -> None:
    temp, project = HELPER.copy_fixture()
    try:
        dep_path = "implementation/workstreams/sample-workstream/results/M01-T03.md"
        commit = "a" * 40
        blob = "b" * 40
        dep = f"{dep_path}@{commit}:{blob}"
        HELPER.install_done_predecessor(project, path=dep_path, commit=commit, blob=blob)
        HELPER.make_ready_card(project, dependencies=dep)
        assert (route(project).disposition, route(project).obligation) == ("route", "execution_prep")
        (project / dep_path).write_text("# DIFFERENT bytes at same declared path/identity\n")
        got = route(project)
        observed("F1_dependency_bytes", got)
        assert (got.disposition, got.obligation) == ("route", "execution_prep")
    finally:
        temp.cleanup()


def F1_reviewed_result_bytes() -> None:
    temp, project = HELPER.copy_fixture()
    try:
        result_path = HELPER.install_reviewable_result(project, "required")
        HELPER.add_review_attempt(project, "green")
        assert route(project).obligation == "post_review_finalization"
        (project / result_path).write_text(
            "# Card Result\n"
            "- Card ID: M01-T04\n"
            "- Implementation subject: materially-different-subject\n"
            "- Evidence refs: implementation/workstreams/sample-workstream/evidence/M01-T04.md\n"
            "- Tests/readback summary: DIFFERENT BYTES\n"
        )
        got = route(project)
        observed("F1_reviewed_result_bytes", got)
        assert got.obligation == "post_review_finalization"
    finally:
        temp.cleanup()


def F2_cobound_execution_research() -> None:
    temp, project = HELPER.copy_fixture()
    try:
        HELPER.install_board_research(project, state="complete", reconciliation="pending")
        baseline = route(project)
        assert baseline.obligation == "execution_resolution"
        manifest = project / MANIFEST
        manifest.write_text(
            manifest.read_text()
            + "\n[research]\n"
            + 'class = "research"\n'
            + 'path = "implementation/workstreams/sample-workstream/RESEARCH.toml"\n'
        )
        got = route(project)
        observed("F2_cobound_execution_research", got)
        assert (got.disposition, got.obligation) == ("recovery", "recovery_boundary")
    finally:
        temp.cleanup()


def F3_unbound_research_target() -> None:
    temp, project = HELPER.copy_fixture()
    try:
        HELPER.install_board_research(project, state="complete", reconciliation="pending")
        research = project / "implementation/workstreams/sample-workstream/RESEARCH.toml"
        research.write_text(
            research.read_text()
            .replace('origin_role = "execution_resolution"', 'origin_role = "execution"')
            .replace('origin_subject = "M01-T04"', 'origin_subject = "M99-T99"')
            .replace(
                'return_target = "execution_resolution:M01-T04"',
                'return_target = "execution:M99-T99"',
            )
        )
        got = route(project)
        observed("F3_unbound_research_target", got)
        assert (got.disposition, got.obligation, got.subject) == (
            "route",
            "execution",
            "M99-T99",
        )
    finally:
        temp.cleanup()


def F4_done_bypasses_pending_review() -> None:
    temp, project = HELPER.copy_fixture()
    try:
        HELPER.install_reviewable_result(project, "required")
        HELPER.add_review_attempt(project, "pending")
        board = project / BOARD
        board.write_text(board.read_text().replace('status = "in_progress"', 'status = "done"', 1))
        got = route(project)
        observed("F4_done_bypasses_pending_review", got)
        assert (got.disposition, got.obligation) == ("route", "close")
    finally:
        temp.cleanup()


def F5_missing_result_evidence() -> None:
    temp, project = HELPER.copy_fixture()
    try:
        HELPER.install_reviewable_result(project, "none")
        evidence = project / "implementation/workstreams/sample-workstream/evidence/M01-T04.md"
        evidence.unlink()
        got = route(project)
        observed("F5_missing_result_evidence", got)
        assert got.obligation == "result_reconciliation"
    finally:
        temp.cleanup()


def F5_missing_review_evidence() -> None:
    temp, project = HELPER.copy_fixture()
    try:
        HELPER.install_reviewable_result(project, "required")
        HELPER.add_review_attempt(project, "green")
        evidence = project / "implementation/workstreams/sample-workstream/evidence/review-R01.md"
        evidence.unlink()
        got = route(project)
        observed("F5_missing_review_evidence", got)
        assert got.obligation == "post_review_finalization"
    finally:
        temp.cleanup()


def F6_mutable_acceptance_surface() -> None:
    temp, project = HELPER.copy_fixture()
    try:
        HELPER.install_reviewable_result(project, "required")
        HELPER.add_review_attempt(project, "green")
        card = project / CARD
        old = "- Acceptance: route only after current launch inputs are valid"
        new = "- Acceptance: NEW materially stronger acceptance never reviewed"
        card.write_text(card.read_text().replace(old, new))
        got = route(project)
        observed("F6_mutable_acceptance_surface", got)
        assert got.obligation == "post_review_finalization"
    finally:
        temp.cleanup()


def main() -> None:
    F1_dependency_bytes()
    F1_reviewed_result_bytes()
    F2_cobound_execution_research()
    F3_unbound_research_target()
    F4_done_bypasses_pending_review()
    F5_missing_result_evidence()
    F5_missing_review_evidence()
    F6_mutable_acceptance_surface()
    print("ALL COUNTEREXAMPLES REPRODUCED")


if __name__ == "__main__":
    main()
