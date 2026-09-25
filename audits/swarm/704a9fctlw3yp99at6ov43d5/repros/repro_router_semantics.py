#!/usr/bin/env python3
"""Non-mutating adversarial reproductions for PWv2 audit F1-F5.

Run from any checkout pinned to:
4fb4bfb7d7b1481d6f347c182fc96a5a1135e045

All mutations occur in TemporaryDirectory copies of the repository fixture.
"""

from contextlib import contextmanager
from pathlib import Path
import shutil
import tempfile

from tools.router import select_route


def find_root() -> Path:
    for parent in Path(__file__).resolve().parents:
        if (parent / "tools" / "router.py").is_file():
            return parent
    raise RuntimeError("repository root not found")


ROOT = find_root()
FIXTURE = ROOT / "tests/fixtures/router/valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"
RESULT = "implementation/workstreams/sample-workstream/results/M01-T04.md"
EVIDENCE = "implementation/workstreams/sample-workstream/evidence/M01-T04.md"
A = "a" * 40
B = "b" * 40


@contextmanager
def project_copy():
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp) / "project"
        shutil.copytree(FIXTURE, project)
        yield project


def route(project: Path):
    return select_route(project, [MANIFEST], package_root=ROOT)


def card_text(*, review="none", dependencies="none") -> str:
    return (
        "# Fixture Card\n"
        "- Card ID: M01-T04\n"
        "- Included scope: adversarial audit\n"
        "- Excluded scope: unrelated work\n"
        "- Authority refs: requirements/REQUIREMENTS.md\n"
        "- Dependencies: " + dependencies + "\n"
        "- Acceptance: exact durable semantics\n"
        "- Required tests/readback: audit reproduction\n"
        "- Review requirement: " + review + "\n"
        "- Technical contract: none\n"
    )


def install_card(project: Path, *, review="none", dependencies="none") -> None:
    (project / CARD).write_text(card_text(review=review, dependencies=dependencies))
    authority = project / "requirements/REQUIREMENTS.md"
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("# Accepted authority\n")


def install_result(project: Path, *, create_evidence=True) -> None:
    board = project / BOARD
    board.write_text(
        board.read_text()
        + "\n[cards.result]\n"
        + 'class = "result"\n'
        + 'path = "' + RESULT + '"\n'
        + 'commit = "' + A + '"\n'
        + 'blob = "' + B + '"\n'
    )
    result = project / RESULT
    result.parent.mkdir(parents=True, exist_ok=True)
    result.write_text(
        "# Card Result\n"
        "- Card ID: M01-T04\n"
        "- Implementation subject: owner/router-fixture@commit:" + A + "\n"
        "- Evidence refs: " + EVIDENCE + "\n"
        "- Tests/readback summary: GREEN\n"
    )
    if create_evidence:
        evidence = project / EVIDENCE
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text("# Durable evidence\n")


def add_green_review_with_missing_evidence(project: Path) -> None:
    review_path = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
    board = project / BOARD
    board.write_text(
        board.read_text().replace(
            '[cards.contract]\n',
            'review_attempts = [{ class = "review_attempt", path = "' + review_path + '" }]\n\n[cards.contract]\n',
            1,
        )
    )
    review = project / review_path
    review.parent.mkdir(parents=True, exist_ok=True)
    review.write_text(
        'attempt = "R01"\n'
        'verdict = "green"\n'
        'workstream_id = "sample-workstream"\n'
        'card_id = "M01-T04"\n'
        'evidence_path = "missing-review-evidence.md"\n'
        '[subject]\n'
        'class = "git_blob"\n'
        'repository = "owner/router-fixture"\n'
        'path = "' + RESULT + '"\n'
        'commit = "' + A + '"\n'
        'blob = "' + B + '"\n'
        '[acceptance]\n'
        'class = "task_card"\n'
        'path = "' + CARD + '"\n'
        '[independence]\n'
        'materially_produced_or_repaired_subject = false\n'
        'basis = "Independent semantic context."\n'
    )


def f1_same_metadata_changed_dependency_bytes():
    with project_copy() as project:
        dep_path = "implementation/workstreams/sample-workstream/results/M01-T03.md"
        pred = (
            '[[cards]]\n'
            'id = "M01-T03"\n'
            'status = "done"\n'
            '[cards.contract]\n'
            'class = "task_card"\n'
            'path = "implementation/workstreams/sample-workstream/cards/M01-T03.md"\n'
            '[cards.result]\n'
            'class = "result"\n'
            'path = "' + dep_path + '"\n'
            'commit = "' + A + '"\n'
            'blob = "' + B + '"\n\n'
        )
        board = project / BOARD
        board.write_text(board.read_text().replace('[[cards]]\n', pred + '[[cards]]\n', 1))
        (project / "implementation/workstreams/sample-workstream/cards/M01-T03.md").write_text("# predecessor\n")
        dep = project / dep_path
        dep.parent.mkdir(parents=True, exist_ok=True)
        dep.write_text("# predecessor result v1\n")
        board.write_text(board.read_text().replace('status = "in_progress"', 'status = "ready"', 1))
        install_card(project, dependencies=dep_path + "@" + A + ":" + B)

        first = route(project)
        dep.write_text("# materially different predecessor result v2\n")
        second = route(project)
        print("F1", first.disposition, first.obligation, "=> after byte-only mutation =>", second.disposition, second.obligation)
        assert (first.disposition, first.obligation) == ("route", "execution_prep")
        assert (second.disposition, second.obligation) == ("route", "execution_prep")


def f2_done_required_review_bypass():
    with project_copy() as project:
        install_card(project, review="required")
        install_result(project)
        board = project / BOARD
        board.write_text(board.read_text().replace('status = "in_progress"', 'status = "done"', 1))
        got = route(project)
        print("F2", got.disposition, got.obligation)
        assert (got.disposition, got.obligation) == ("route", "close")


def f3_ready_with_result_ignores_recovery_truth():
    with project_copy() as project:
        install_card(project)
        install_result(project)
        board = project / BOARD
        board.write_text(board.read_text().replace('status = "in_progress"', 'status = "ready"', 1))
        got = route(project)
        print("F3", got.disposition, got.obligation)
        assert (got.disposition, got.obligation) == ("route", "execution_prep")


def f4_missing_evidence_is_accepted():
    with project_copy() as project:
        install_card(project, review="none")
        install_result(project, create_evidence=False)
        got = route(project)
        print("F4-result", got.disposition, got.obligation)
        assert (got.disposition, got.obligation) == ("route", "result_reconciliation")

    with project_copy() as project:
        install_card(project, review="required")
        install_result(project, create_evidence=True)
        add_green_review_with_missing_evidence(project)
        got = route(project)
        print("F4-review", got.disposition, got.obligation)
        assert (got.disposition, got.obligation) == ("route", "post_review_finalization")


def f5_research_redirects_to_nonexistent_card():
    with project_copy() as project:
        board = project / BOARD
        board.write_text(
            board.read_text()
            + '\n[research_obligation]\n'
            + 'class = "research"\n'
            + 'path = "implementation/workstreams/sample-workstream/RESEARCH.toml"\n'
        )
        research = project / "implementation/workstreams/sample-workstream/RESEARCH.toml"
        research.write_text(
            'state = "complete"\n'
            'workstream_id = "sample-workstream"\n'
            'origin_role = "execution_resolution"\n'
            'origin_subject = "M01-T04"\n'
            'return_target = "execution:M99-T99"\n'
            'return_reconciliation = "pending"\n'
            'return_result = ""\n'
            'finding = "Recovered fact."\n'
            'limitations = "none"\n'
            'conflicts = "none"\n'
            '[[sources]]\nclass = "official_upstream"\nstatus = "not_relevant"\nweight = "primary"\n'
            '[[sources]]\nclass = "project_runtime"\nstatus = "checked"\nweight = "direct"\n'
            '[[sources]]\nclass = "tracker_discussion"\nstatus = "not_relevant"\nweight = "supporting"\n'
            '[[sources]]\nclass = "practitioner_community"\nstatus = "not_relevant"\nweight = "supporting"\n'
        )
        got = route(project)
        print("F5", got.disposition, got.obligation, got.subject)
        assert (got.disposition, got.obligation, got.subject) == ("route", "execution", "M99-T99")


if __name__ == "__main__":
    f1_same_metadata_changed_dependency_bytes()
    f2_done_required_review_bypass()
    f3_ready_with_result_ignores_recovery_truth()
    f4_missing_evidence_is_accepted()
    f5_research_redirects_to_nonexistent_card()
    print("F1-F5 vulnerable behaviors reproduced")
