#!/usr/bin/env python3
"""Adversarial reproductions for audit k7m2v9q4x1n8c5r0t6p3b2d9.

Run from a checkout of elmakus/project_workflow_v2 at exactly
4fb4bfb7d7b1481d6f347c182fc96a5a1135e045.

These assertions encode the defective behavior observed by the audit. A correct
repair should cause the relevant assertion(s) to fail.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from tools.close_contract import close_continuation
from tools.router import select_route

ROOT = Path(__file__).resolve().parents[4]
FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"


def fresh_project():
    temp = tempfile.TemporaryDirectory()
    project = Path(temp.name) / "project"
    shutil.copytree(FIXTURE, project)
    return temp, project


def card_text(review_requirement="required"):
    return (
        "# Fixture Card\n"
        "- Card ID: M01-T04\n"
        "- Included scope: adversarial review fixture\n"
        "- Excluded scope: none\n"
        "- Authority refs: requirements/REQUIREMENTS.md\n"
        "- Dependencies: none\n"
        "- Acceptance: original acceptance surface\n"
        "- Required tests/readback: original required checks\n"
        f"- Review requirement: {review_requirement}\n"
        "- Technical contract: none\n"
    )


def install_result(project, review_requirement="required"):
    (project / CARD).write_text(card_text(review_requirement), encoding="utf-8")

    authority = project / "requirements/REQUIREMENTS.md"
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("# Accepted authority\n", encoding="utf-8")

    result_rel = "implementation/workstreams/sample-workstream/results/M01-T04.md"
    board = project / BOARD
    board.write_text(
        board.read_text(encoding="utf-8")
        + "\n[cards.result]\n"
        + 'class = "result"\n'
        + f'path = "{result_rel}"\n'
        + 'commit = "' + ("a" * 40) + '"\n'
        + 'blob = "' + ("b" * 40) + '"\n',
        encoding="utf-8",
    )

    evidence = project / "implementation/workstreams/sample-workstream/evidence/M01-T04.md"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text("# implementation evidence\n", encoding="utf-8")

    result = project / result_rel
    result.parent.mkdir(parents=True, exist_ok=True)
    result.write_text(
        "# Card Result\n"
        "- Card ID: M01-T04\n"
        "- Implementation subject: original-subject\n"
        "- Evidence refs: implementation/workstreams/sample-workstream/evidence/M01-T04.md\n"
        "- Tests/readback summary: GREEN\n",
        encoding="utf-8",
    )
    return result


def install_green_review(project, create_evidence=True):
    review_rel = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
    board = project / BOARD
    board.write_text(
        board.read_text(encoding="utf-8").replace(
            'status = "in_progress"\n',
            'status = "in_progress"\n'
            + f'review_attempts = [{{ class = "review_attempt", path = "{review_rel}" }}]\n',
            1,
        ),
        encoding="utf-8",
    )

    evidence_rel = "implementation/workstreams/sample-workstream/evidence/review-R01.md"
    if create_evidence:
        evidence = project / evidence_rel
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text("# review evidence\n", encoding="utf-8")

    review = project / review_rel
    review.parent.mkdir(parents=True, exist_ok=True)
    review.write_text(
        'workstream_id = "sample-workstream"\n'
        'card_id = "M01-T04"\n'
        'attempt = "R01"\n'
        'verdict = "green"\n'
        + f'evidence_path = "{evidence_rel}"\n'
        + '[subject]\n'
        + 'class = "git_blob"\n'
        + 'repository = "owner/router-fixture"\n'
        + 'commit = "' + ("a" * 40) + '"\n'
        + 'path = "implementation/workstreams/sample-workstream/results/M01-T04.md"\n'
        + 'blob = "' + ("b" * 40) + '"\n'
        + '[acceptance]\n'
        + 'class = "task_card"\n'
        + f'path = "{CARD}"\n'
        + '[independence]\n'
        + 'materially_produced_or_repaired_subject = false\n'
        + 'basis = "Fresh semantic reviewer context."\n',
        encoding="utf-8",
    )


def f01_result_content_swap_after_green():
    temp, project = fresh_project()
    try:
        result = install_result(project)
        install_green_review(project)
        result.write_text(
            "# Card Result\n"
            "- Card ID: M01-T04\n"
            "- Implementation subject: materially-changed-after-review\n"
            "- Evidence refs: implementation/workstreams/sample-workstream/evidence/M01-T04.md\n"
            "- Tests/readback summary: CHANGED AFTER GREEN\n",
            encoding="utf-8",
        )
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        assert (routed.disposition, routed.obligation) == (
            "route",
            "post_review_finalization",
        ), routed
    finally:
        temp.cleanup()


def f02_acceptance_surface_changes_after_green():
    temp, project = fresh_project()
    try:
        install_result(project)
        install_green_review(project)
        card = project / CARD
        card.write_text(
            card.read_text(encoding="utf-8")
            .replace("original acceptance surface", "materially stronger acceptance after GREEN")
            .replace("original required checks", "new mandatory checks after GREEN"),
            encoding="utf-8",
        )
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        assert (routed.disposition, routed.obligation) == (
            "route",
            "post_review_finalization",
        ), routed
    finally:
        temp.cleanup()


def install_issue_and_misdirected_research(project):
    workstream = project / MANIFEST
    workstream.write_text(
        workstream.read_text(encoding="utf-8")
        + '\n[intake]\nclass = "intake"\n'
        + 'path = "implementation/workstreams/sample-workstream/INTAKE.toml"\n'
        + '\n[research]\nclass = "research"\n'
        + 'path = "implementation/workstreams/sample-workstream/RESEARCH.toml"\n',
        encoding="utf-8",
    )

    intake = project / "implementation/workstreams/sample-workstream/INTAKE.toml"
    intake.write_text(
        'workstream_id = "sample-workstream"\n'
        'kind = "issue"\n'
        'state = "active"\n'
        'diagnosis_revision = 1\n'
        'repair_subject = "repair:v1"\n'
        'diagnosis_prior_art_subject = ""\n'
        'diagnosis_prior_art_result = ""\n'
        'response_kind = "none"\n'
        'response_observed = false\n'
        'alignment_state = "pending"\n'
        'alignment_subject = ""\n'
        'micro_fix_candidate = false\n',
        encoding="utf-8",
    )

    research = project / "implementation/workstreams/sample-workstream/RESEARCH.toml"
    research.write_text(
        'workstream_id = "sample-workstream"\n'
        'state = "complete"\n'
        'origin_role = "intake"\n'
        'origin_subject = "repair:v1"\n'
        'return_target = "definition"\n'
        'return_reconciliation = "pending"\n'
        'return_result = ""\n'
        'finding = "completed finding"\n'
        'limitations = "none"\n'
        'conflicts = "none"\n'
        '[[sources]]\nclass = "official_upstream"\nstatus = "checked"\nweight = "primary"\n'
        '[[sources]]\nclass = "project_runtime"\nstatus = "checked"\nweight = "direct"\n'
        '[[sources]]\nclass = "tracker_discussion"\nstatus = "not_relevant"\nweight = "supporting"\n'
        '[[sources]]\nclass = "practitioner_community"\nstatus = "unavailable"\nweight = "supporting"\n',
        encoding="utf-8",
    )


def f03_research_owner_mismatch_bypasses_intake():
    temp, project = fresh_project()
    try:
        install_issue_and_misdirected_research(project)
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        assert (routed.disposition, routed.obligation) == ("route", "definition"), routed
    finally:
        temp.cleanup()


def f04_close_stop_is_disconnected():
    temp, project = fresh_project()
    try:
        install_result(project, review_requirement="none")
        board = project / BOARD
        board.write_text(
            board.read_text(encoding="utf-8").replace(
                'status = "in_progress"', 'status = "done"', 1
            ),
            encoding="utf-8",
        )
        first = select_route(project, [MANIFEST], package_root=ROOT)
        second = select_route(project, [MANIFEST], package_root=ROOT)
        assert (first.disposition, first.obligation) == ("route", "close"), first
        assert (second.disposition, second.obligation) == ("route", "close"), second

        helper = close_continuation(
            approved_scope_durably_complete=True,
            next_authorized_obligation=False,
            explicit_authorization_gate_due=False,
        )
        assert helper == "end_of_scope_stop", helper
    finally:
        temp.cleanup()


def f05_missing_terminal_review_evidence():
    temp, project = fresh_project()
    try:
        install_result(project)
        install_green_review(project, create_evidence=False)
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        assert (routed.disposition, routed.obligation) == (
            "route",
            "post_review_finalization",
        ), routed
    finally:
        temp.cleanup()


def main():
    f01_result_content_swap_after_green()
    f02_acceptance_surface_changes_after_green()
    f03_research_owner_mismatch_bypasses_intake()
    f04_close_stop_is_disconnected()
    f05_missing_terminal_review_evidence()
    print("All five current-behavior counterexamples reproduced.")


if __name__ == "__main__":
    main()
