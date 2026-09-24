#!/usr/bin/env python3
"""Non-mutating reproductions for PWv2 swarm audit novka0hlkl74xbxwtotil5iz.

Run from the audit branch. The script copies the repository's existing router fixture
into temporary directories and mutates only those temporary copies.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SUBJECT = "4fb4bfb7d7b1481d6f347c182fc96a5a1135e045"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"
RESULT = "implementation/workstreams/sample-workstream/results/M01-T04.md"


def find_root() -> Path:
    here = Path(__file__).resolve()
    for parent in here.parents:
        if (parent / "tools" / "router.py").exists() and (parent / "tests" / "fixtures" / "router").exists():
            return parent
    raise RuntimeError("repository root not found")


ROOT = find_root()
sys.path.insert(0, str(ROOT))

from tools.router import select_route  # noqa: E402


FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"


def assert_product_matches_subject() -> None:
    subprocess.run(
        [
            "git",
            "diff",
            "--quiet",
            SUBJECT,
            "--",
            "workflow",
            "tools",
            "tests",
            "hooks",
            "skills",
            "templates",
            "schemas",
        ],
        cwd=ROOT,
        check=True,
    )


def copy_project() -> tuple[tempfile.TemporaryDirectory[str], Path]:
    temp = tempfile.TemporaryDirectory()
    project = Path(temp.name) / "project"
    shutil.copytree(FIXTURE, project)
    return temp, project


def task_card(review_requirement: str) -> str:
    return (
        "# Fixture Card\n"
        "- Card ID: M01-T04\n"
        "- Included scope: prove review and routing invariants\n"
        "- Excluded scope: unrelated behavior\n"
        "- Authority refs: requirements/REQUIREMENTS.md\n"
        "- Dependencies: none\n"
        "- Acceptance: exact reviewed result must satisfy this Card\n"
        "- Required tests/readback: exact subject verification\n"
        f"- Review requirement: {review_requirement}\n"
        "- Technical contract: none\n"
    )


def install_result(project: Path, review_requirement: str = "required") -> None:
    (project / CARD).write_text(task_card(review_requirement), encoding="utf-8")
    authority = project / "requirements" / "REQUIREMENTS.md"
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
    evidence.write_text("# Verified implementation evidence\n", encoding="utf-8")

    result_file = project / RESULT
    result_file.parent.mkdir(parents=True, exist_ok=True)
    result_file.write_text(
        "# Card Result\n"
        "- Card ID: M01-T04\n"
        "- Implementation subject: owner/repo@commit:" + ("a" * 40) + "\n"
        "- Evidence refs: implementation/workstreams/sample-workstream/evidence/M01-T04.md\n"
        "- Tests/readback summary: GREEN\n",
        encoding="utf-8",
    )


def install_review(
    project: Path,
    verdict: str,
    *,
    evidence_path: str = "implementation/workstreams/sample-workstream/evidence/review-R01.md",
    create_evidence: bool = True,
) -> None:
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
    if create_evidence and evidence_path:
        evidence = project / evidence_path
        evidence.parent.mkdir(parents=True, exist_ok=True)
        evidence.write_text("# Review evidence\n", encoding="utf-8")

    review = project / review_path
    review.parent.mkdir(parents=True, exist_ok=True)
    review.write_text(
        'workstream_id = "sample-workstream"\n'
        'card_id = "M01-T04"\n'
        'attempt = "R01"\n'
        f'verdict = "{verdict}"\n'
        f'evidence_path = "{evidence_path}"\n'
        "[subject]\n"
        'class = "git_blob"\n'
        'repository = "owner/router-fixture"\n'
        f'commit = "{"a" * 40}"\n'
        f'path = "{RESULT}"\n'
        f'blob = "{"b" * 40}"\n'
        "[acceptance]\n"
        'class = "task_card"\n'
        f'path = "{CARD}"\n'
        "[independence]\n"
        "materially_produced_or_repaired_subject = false\n"
        'basis = "Fresh semantic reviewer context."\n',
        encoding="utf-8",
    )


def route(project: Path):
    return select_route(project, [MANIFEST], package_root=ROOT)


def repro_done_bypasses_red_review() -> None:
    temp, project = copy_project()
    try:
        install_result(project, "required")
        install_review(project, "red")
        board = project / BOARD
        board.write_text(
            board.read_text(encoding="utf-8").replace('status = "in_progress"', 'status = "done"', 1),
            encoding="utf-8",
        )
        actual = route(project)
        print("F1", actual.disposition, actual.obligation, actual.read_set)
        assert (actual.disposition, actual.obligation) == ("route", "close")
        assert not any("/reviews/" in item for item in actual.read_set)
    finally:
        temp.cleanup()


def repro_same_path_result_mutation_reuses_green() -> None:
    temp, project = copy_project()
    try:
        install_result(project, "required")
        install_review(project, "green")
        result_file = project / RESULT
        result_file.write_text(
            result_file.read_text(encoding="utf-8").replace(
                "- Tests/readback summary: GREEN",
                "- Tests/readback summary: MUTATED-AFTER-GREEN-REVIEW",
            ),
            encoding="utf-8",
        )
        actual = route(project)
        print("F2", actual.disposition, actual.obligation)
        assert (actual.disposition, actual.obligation) == ("route", "post_review_finalization")
    finally:
        temp.cleanup()


def repro_missing_review_evidence_still_finalizes() -> None:
    temp, project = copy_project()
    try:
        install_result(project, "required")
        missing = "implementation/workstreams/sample-workstream/evidence/DOES-NOT-EXIST.md"
        install_review(project, "green", evidence_path=missing, create_evidence=False)
        assert not (project / missing).exists()
        actual = route(project)
        print("F3", actual.disposition, actual.obligation, actual.read_set)
        assert (actual.disposition, actual.obligation) == ("route", "post_review_finalization")
        assert f"project:{missing}" not in actual.read_set
    finally:
        temp.cleanup()


def repro_satisfied_jit_trigger_is_ignored_by_close() -> None:
    temp, project = copy_project()
    try:
        install_result(project, "none")
        board = project / BOARD
        board.write_text(
            board.read_text(encoding="utf-8")
            .replace('status = "in_progress"', 'status = "done"', 1)
            + "\n[[jit_triggers]]\n"
            + 'id = "downstream-after-M01-T04"\n'
            + 'after_card = "M01-T04"\n'
            + 'state = "satisfied"\n'
            + 'condition = "DONE predecessor result makes downstream Card boundary knowable."\n',
            encoding="utf-8",
        )
        actual = route(project)
        print("F4", actual.disposition, actual.obligation)
        assert (actual.disposition, actual.obligation) == ("route", "close")
    finally:
        temp.cleanup()


def main() -> int:
    assert_product_matches_subject()
    repro_done_bypasses_red_review()
    repro_same_path_result_mutation_reuses_green()
    repro_missing_review_evidence_still_finalizes()
    repro_satisfied_jit_trigger_is_ignored_by_close()
    print("All four defects reproduced.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
