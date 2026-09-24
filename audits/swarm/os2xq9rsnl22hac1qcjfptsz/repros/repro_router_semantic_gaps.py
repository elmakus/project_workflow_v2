#!/usr/bin/env python3
"""Non-mutating PWv2 adversarial repros. Run from any checkout of the audited subject/branch."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tools.router import select_route

SPEC = importlib.util.spec_from_file_location("target_test_router", ROOT / "tests" / "test_router.py")
assert SPEC and SPEC.loader
T = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(T)


def harness():
    return T.RouterTests()


def outcome(r):
    return (r.disposition, r.obligation)


def require_bug(name, actual, vulnerable):
    print(f"{name}: actual={actual}, vulnerable_expected={vulnerable}")
    if actual != vulnerable:
        raise AssertionError(f"{name}: target no longer reproduces expected vulnerable behavior")


def repro_dependency_content_drift():
    h = harness()
    temp, project = h.copy_fixture()
    try:
        p = "implementation/workstreams/sample-workstream/results/M01-T03.md"
        commit, blob = "a" * 40, "b" * 40
        h.install_done_predecessor(project, path=p, commit=commit, blob=blob)
        h.make_ready_card(project, dependencies=f"{p}@{commit}:{blob}")
        require_bug("F1 baseline", outcome(select_route(project, [T.MANIFEST], package_root=ROOT)), ("route", "execution_prep"))
        (project / p).write_text("# CHANGED CONTENT WITH STALE DECLARED BLOB\n")
        require_bug("F1 content-only drift", outcome(select_route(project, [T.MANIFEST], package_root=ROOT)), ("route", "execution_prep"))
    finally:
        temp.cleanup()


def repro_green_review_acceptance_mutation():
    h = harness()
    temp, project = h.copy_fixture()
    try:
        h.install_reviewable_result(project, "required")
        h.add_review_attempt(project, "green")
        require_bug("F2 baseline", outcome(select_route(project, [T.MANIFEST], package_root=ROOT)), ("route", "post_review_finalization"))
        card = project / T.CARD
        card.write_text(card.read_text().replace(
            "- Acceptance: route only after current launch inputs are valid",
            "- Acceptance: materially different post-review acceptance criterion",
        ))
        require_bug("F2 changed Task Card acceptance", outcome(select_route(project, [T.MANIFEST], package_root=ROOT)), ("route", "post_review_finalization"))
    finally:
        temp.cleanup()


def _unbound_issue_intake():
    return (
        'workstream_id = "sample-workstream"\n'
        'kind = "issue"\n'
        'state = "active"\n'
        'diagnosis_revision = 2\n'
        'repair_subject = "repair:v2"\n'
        'diagnosis_prior_art_subject = ""\n'
        'diagnosis_prior_art_result = ""\n'
        'response_kind = "none"\n'
        'response_observed = false\n'
        'alignment_state = "pending"\n'
        'alignment_subject = ""\n'
        'micro_fix_candidate = false\n'
    )


def _unrelated_active_research():
    return (
        'state = "active"\n'
        'workstream_id = "sample-workstream"\n'
        'origin_role = "brainstorming"\n'
        'origin_subject = "later-fact:v1"\n'
        'return_target = "brainstorming"\n'
        'return_reconciliation = "pending"\n'
        'return_result = ""\n'
        'finding = ""\n'
        'limitations = ""\n'
        'conflicts = ""\n'
        '[[sources]]\nclass = "official_upstream"\nstatus = "pending"\nweight = "primary"\n'
        '[[sources]]\nclass = "project_runtime"\nstatus = "pending"\nweight = "direct"\n'
        '[[sources]]\nclass = "tracker_discussion"\nstatus = "pending"\nweight = "supporting"\n'
        '[[sources]]\nclass = "practitioner_community"\nstatus = "pending"\nweight = "supporting"\n'
    )


def repro_premature_research_slot_reuse():
    h = harness()
    temp, project = h.copy_fixture()
    try:
        h.install_intake(project, _unbound_issue_intake())
        require_bug("F3 baseline mandatory issue prior-art", outcome(select_route(project, [T.MANIFEST], package_root=ROOT)), ("route", "intake"))
        h.install_state_record(project, "research", "research", "RESEARCH.toml", _unrelated_active_research())
        require_bug("F3 unrelated Research masks Intake", outcome(select_route(project, [T.MANIFEST], package_root=ROOT)), ("route", "research"))
    finally:
        temp.cleanup()


def repro_invalid_result_is_treated_as_valid():
    h = harness()
    temp, project = h.copy_fixture()
    try:
        result_path = h.install_reviewable_result(project, "none")
        (project / result_path).write_text(
            "# Card Result\n"
            "- Card ID: M01-T04\n"
            "- Implementation subject: banana\n"
            "- Evidence refs: implementation/workstreams/sample-workstream/evidence/does-not-exist.md\n"
            "- Tests/readback summary: FAILED: acceptance test failed\n"
        )
        require_bug("F5 invalid semantic result", outcome(select_route(project, [T.MANIFEST], package_root=ROOT)), ("route", "result_reconciliation"))
    finally:
        temp.cleanup()


def repro_satisfied_jit_routes_close():
    h = harness()
    temp, project = h.copy_fixture()
    try:
        h.install_reviewable_result(project, "none")
        board = project / T.BOARD
        board.write_text(
            board.read_text().replace('status = "in_progress"', 'status = "done"', 1)
            + '\n[[jit_triggers]]\n'
              'id = "after-M01-T04"\n'
              'after_card = "M01-T04"\n'
              'state = "satisfied"\n'
              'condition = "DONE predecessor result makes downstream contract knowable."\n'
        )
        require_bug("F6 satisfied JIT", outcome(select_route(project, [T.MANIFEST], package_root=ROOT)), ("route", "close"))
    finally:
        temp.cleanup()


def repro_done_bypasses_pending_required_review():
    h = harness()
    temp, project = h.copy_fixture()
    try:
        h.install_reviewable_result(project, "required")
        h.add_review_attempt(project, "pending")
        board = project / T.BOARD
        board.write_text(board.read_text().replace('status = "in_progress"', 'status = "done"', 1))
        require_bug("F7 DONE with pending REQUIRED review", outcome(select_route(project, [T.MANIFEST], package_root=ROOT)), ("route", "close"))
    finally:
        temp.cleanup()


if __name__ == "__main__":
    repro_dependency_content_drift()
    repro_green_review_acceptance_mutation()
    repro_premature_research_slot_reuse()
    repro_invalid_result_is_treated_as_valid()
    repro_satisfied_jit_routes_close()
    repro_done_bypasses_pending_required_review()
    print("All six router counterexamples reproduced.")
