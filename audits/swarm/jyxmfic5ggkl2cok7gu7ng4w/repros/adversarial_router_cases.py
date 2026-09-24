#!/usr/bin/env python3
"""Non-mutating PWv2 swarm reproductions for subject 4fb4bfb7d7b1481d6f347c182fc96a5a1135e045.

Run from the repository checkout at that exact commit (or the audit branch based on it):
    python audits/swarm/jyxmfic5ggkl2cok7gu7ng4w/repros/adversarial_router_cases.py

The assertions below encode the vulnerable behavior observed from the exact source.
They should fail after the corresponding defect is repaired.
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tools.router import select_route  # noqa: E402

FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"
RESULT = "implementation/workstreams/sample-workstream/results/M01-T04.md"


def copy_fixture() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    temp = tempfile.TemporaryDirectory()
    project = Path(temp.name) / "project"
    shutil.copytree(FIXTURE, project)
    return temp, project


def card_text(review_requirement: str) -> str:
    return (
        "# Fixture Card\n"
        "- Card ID: M01-T04\n"
        "- Included scope: adversarial exact-subject probe\n"
        "- Excluded scope: unrelated changes\n"
        "- Authority refs: requirements/REQUIREMENTS.md\n"
        "- Dependencies: none\n"
        "- Acceptance: exact current bytes are reviewed\n"
        "- Required tests/readback: this reproduction\n"
        f"- Review requirement: {review_requirement}\n"
        "- Technical contract: none\n"
    )


def install_result(project: Path, review_requirement: str = "required") -> Path:
    (project / CARD).write_text(card_text(review_requirement), encoding="utf-8")
    authority = project / "requirements/REQUIREMENTS.md"
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("# Accepted authority\n", encoding="utf-8")
    board = project / BOARD
    board.write_text(
        board.read_text(encoding="utf-8")
        + "\n[cards.result]\n"
        + 'class = "result"\n'
        + f'path = "{RESULT}"\n'
        + f'commit = "{"a" * 40}"\n'
        + f'blob = "{"b" * 40}"\n',
        encoding="utf-8",
    )
    evidence = project / "implementation/workstreams/sample-workstream/evidence/M01-T04.md"
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text("# Evidence\n", encoding="utf-8")
    result_file = project / RESULT
    result_file.parent.mkdir(parents=True, exist_ok=True)
    result_file.write_text(
        "# Card Result\n"
        "- Card ID: M01-T04\n"
        f"- Implementation subject: owner/repo@commit:{'a' * 40}\n"
        "- Evidence refs: implementation/workstreams/sample-workstream/evidence/M01-T04.md\n"
        "- Tests/readback summary: GREEN\n",
        encoding="utf-8",
    )
    return result_file


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
    evidence = project / "implementation/workstreams/sample-workstream/evidence/review-R01.md"
    evidence.write_text("# Review evidence\n", encoding="utf-8")
    review = project / review_path
    review.parent.mkdir(parents=True, exist_ok=True)
    review.write_text(
        'workstream_id = "sample-workstream"\n'
        'card_id = "M01-T04"\n'
        'attempt = "R01"\n'
        'verdict = "green"\n'
        'evidence_path = "implementation/workstreams/sample-workstream/evidence/review-R01.md"\n'
        '[subject]\n'
        'class = "git_blob"\n'
        'repository = "owner/router-fixture"\n'
        f'commit = "{"a" * 40}"\n'
        f'path = "{RESULT}"\n'
        f'blob = "{"b" * 40}"\n'
        '[acceptance]\n'
        'class = "task_card"\n'
        f'path = "{CARD}"\n'
        '[independence]\n'
        'materially_produced_or_repaired_subject = false\n'
        'basis = "Independent semantic reviewer."\n',
        encoding="utf-8",
    )


def install_intake(project: Path) -> None:
    ws = project / MANIFEST
    ws.write_text(
        ws.read_text(encoding="utf-8")
        + '\n[intake]\nclass = "intake"\n'
        + 'path = "implementation/workstreams/sample-workstream/INTAKE.toml"\n',
        encoding="utf-8",
    )
    (project / "implementation/workstreams/sample-workstream/INTAKE.toml").write_text(
        'workstream_id = "sample-workstream"\n'
        'kind = "issue"\n'
        'state = "active"\n'
        'diagnosis_revision = 1\n'
        'repair_subject = "repair:v1"\n'
        'diagnosis_prior_art_subject = "repair:v1"\n'
        'diagnosis_prior_art_result = "prior-art:v1"\n'
        'response_kind = "none"\n'
        'response_observed = false\n'
        'alignment_state = "pending"\n'
        'alignment_subject = ""\n'
        'micro_fix_candidate = false\n',
        encoding="utf-8",
    )


def research_text(*, state: str, origin_role: str, origin_subject: str, return_target: str) -> str:
    pending = state == "active"
    return (
        f'state = "{state}"\n'
        'workstream_id = "sample-workstream"\n'
        f'origin_role = "{origin_role}"\n'
        f'origin_subject = "{origin_subject}"\n'
        f'return_target = "{return_target}"\n'
        'return_reconciliation = "pending"\n'
        'return_result = ""\n'
        f'finding = "{"Durable fact." if not pending else ""}"\n'
        'limitations = "none"\n'
        f'conflicts = "{"none" if not pending else ""}"\n'
        '[[sources]]\nclass = "official_upstream"\n'
        f'status = "{"pending" if pending else "checked"}"\nweight = "primary"\n'
        '[[sources]]\nclass = "project_runtime"\n'
        f'status = "{"pending" if pending else "checked"}"\nweight = "direct"\n'
        '[[sources]]\nclass = "tracker_discussion"\n'
        f'status = "{"pending" if pending else "not_relevant"}"\nweight = "supporting"\n'
        '[[sources]]\nclass = "practitioner_community"\n'
        f'status = "{"pending" if pending else "not_relevant"}"\nweight = "supporting"\n'
    )


def case_f1_same_path_result_mutation_keeps_green() -> None:
    temp, project = copy_fixture()
    try:
        result_file = install_result(project, "required")
        add_green_review(project)
        before = select_route(project, [MANIFEST], package_root=ROOT)
        assert (before.disposition, before.obligation) == ("route", "post_review_finalization")

        # Change the actual current bytes without changing the Board's declared commit/blob
        # or the GREEN review subject. Exact Git identity is never dereferenced.
        result_file.write_text(result_file.read_text(encoding="utf-8") + "\nUNREVIEWED MUTATION\n", encoding="utf-8")
        after = select_route(project, [MANIFEST], package_root=ROOT)
        print("F1", after.disposition, after.obligation)
        assert (after.disposition, after.obligation) == ("route", "post_review_finalization")
    finally:
        temp.cleanup()


def case_f2_done_required_without_green_routes_close() -> None:
    temp, project = copy_fixture()
    try:
        install_result(project, "required")
        board = project / BOARD
        board.write_text(
            board.read_text(encoding="utf-8").replace('status = "in_progress"', 'status = "done"', 1),
            encoding="utf-8",
        )
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print("F2", routed.disposition, routed.obligation)
        assert (routed.disposition, routed.obligation) == ("route", "close")
    finally:
        temp.cleanup()


def case_f3_unrelated_research_preempts_alignment_stop() -> None:
    temp, project = copy_fixture()
    try:
        install_intake(project)
        baseline = select_route(project, [MANIFEST], package_root=ROOT)
        assert (baseline.disposition, baseline.obligation) == ("stop", "issue_alignment")

        ws = project / MANIFEST
        ws.write_text(
            ws.read_text(encoding="utf-8")
            + '\n[research]\nclass = "research"\n'
            + 'path = "implementation/workstreams/sample-workstream/RESEARCH.toml"\n',
            encoding="utf-8",
        )
        (project / "implementation/workstreams/sample-workstream/RESEARCH.toml").write_text(
            research_text(
                state="active",
                origin_role="brainstorming",
                origin_subject="unrelated-scope@1",
                return_target="brainstorming",
            ),
            encoding="utf-8",
        )
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print("F3", routed.disposition, routed.obligation, routed.subject)
        assert (routed.disposition, routed.obligation) == ("route", "research")
        assert routed.subject == "unrelated-scope@1"
    finally:
        temp.cleanup()


def case_f4_execution_research_accepts_wrong_or_empty_card_subject() -> None:
    temp, project = copy_fixture()
    try:
        board = project / BOARD
        board.write_text(
            board.read_text(encoding="utf-8")
            + '\n[research_obligation]\nclass = "research"\n'
            + 'path = "implementation/workstreams/sample-workstream/RESEARCH.toml"\n',
            encoding="utf-8",
        )
        research = project / "implementation/workstreams/sample-workstream/RESEARCH.toml"
        research.write_text(
            research_text(
                state="complete",
                origin_role="execution_resolution",
                origin_subject="M01-T04",
                return_target="execution:M99-T99",
            ),
            encoding="utf-8",
        )
        wrong = select_route(project, [MANIFEST], package_root=ROOT)
        print("F4-wrong", wrong.disposition, wrong.obligation, repr(wrong.subject))
        assert (wrong.disposition, wrong.obligation, wrong.subject) == ("route", "execution", "M99-T99")

        research.write_text(
            research_text(
                state="complete",
                origin_role="execution_resolution",
                origin_subject="M01-T04",
                return_target="execution:",
            ),
            encoding="utf-8",
        )
        empty = select_route(project, [MANIFEST], package_root=ROOT)
        print("F4-empty", empty.disposition, empty.obligation, repr(empty.subject))
        assert (empty.disposition, empty.obligation, empty.subject) == ("route", "execution", "")
    finally:
        temp.cleanup()


if __name__ == "__main__":
    case_f1_same_path_result_mutation_keeps_green()
    case_f2_done_required_without_green_routes_close()
    case_f3_unrelated_research_preempts_alignment_stop()
    case_f4_execution_research_accepts_wrong_or_empty_card_subject()
    print("All four vulnerable behaviors reproduced.")
