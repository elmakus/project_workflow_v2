#!/usr/bin/env python3
"""Reproduce immutable-identity and dangling-evidence failures on the exact subject."""
from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from tools.router import select_route

ROOT = Path(__file__).resolve().parents[4]
FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"
RESULT = "implementation/workstreams/sample-workstream/results/M01-T04.md"
REVIEW = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
DEP = "implementation/workstreams/sample-workstream/results/M01-T03.md"


def card_text(*, review: str = "none", dependency: str = "none") -> str:
    return (
        "# Probe Card\n"
        "- Card ID: M01-T04\n"
        "- Included scope: identity probe\n"
        "- Excluded scope: product changes\n"
        "- Authority refs: requirements/REQUIREMENTS.md\n"
        f"- Dependencies: {dependency}\n"
        "- Acceptance: exact durable subject must be current\n"
        "- Required tests/readback: this probe\n"
        f"- Review requirement: {review}\n"
        "- Technical contract: none\n"
    )


def result_text(summary: str) -> str:
    return (
        "# Card Result\n"
        "- Card ID: M01-T04\n"
        "- Implementation subject: owner/router-fixture@commit:" + ("a" * 40) + "\n"
        "- Evidence refs: implementation/workstreams/sample-workstream/evidence/MISSING-result.md\n"
        f"- Tests/readback summary: {summary}\n"
    )


def install_authority(project: Path) -> None:
    p = project / "requirements/REQUIREMENTS.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("# authority\n")


def ready_dependency_case() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp) / "project"
        shutil.copytree(FIXTURE, project)
        install_authority(project)
        dep_ref = f"{DEP}@{'a' * 40}:{'b' * 40}"
        (project / CARD).write_text(card_text(dependency=dep_ref))
        dep = project / DEP
        dep.parent.mkdir(parents=True, exist_ok=True)
        dep.write_text("version one\n")

        board = project / BOARD
        predecessor = (
            '[[cards]]\n'
            'id = "M01-T03"\n'
            'status = "done"\n'
            '[cards.contract]\n'
            'class = "task_card"\n'
            'path = "implementation/workstreams/sample-workstream/cards/M01-T03.md"\n'
            '[cards.result]\n'
            'class = "result"\n'
            f'path = "{DEP}"\n'
            f'commit = "{"a" * 40}"\n'
            f'blob = "{"b" * 40}"\n\n'
        )
        text = board.read_text()
        text = text.replace('[[cards]]\n', predecessor + '[[cards]]\n', 1)
        text = text.replace('status = "in_progress"', 'status = "ready"', 1)
        board.write_text(text)

        first = select_route(project, [MANIFEST], package_root=ROOT)
        dep.write_text("version two: same path, declared commit/blob unchanged\n")
        second = select_route(project, [MANIFEST], package_root=ROOT)
        print("ready dependency before mutation =>", first.disposition, first.obligation)
        print("ready dependency after mutation  =>", second.disposition, second.obligation)


def reviewed_result_case() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        project = Path(tmp) / "project"
        shutil.copytree(FIXTURE, project)
        install_authority(project)
        (project / CARD).write_text(card_text(review="required"))

        result = project / RESULT
        result.parent.mkdir(parents=True, exist_ok=True)
        result.write_text(result_text("version one"))
        board = project / BOARD
        board.write_text(
            board.read_text().replace(
                'status = "in_progress"\n',
                f'status = "in_progress"\nreview_attempts = [{{ class = "review_attempt", path = "{REVIEW}" }}]\n',
                1,
            )
            + '\n[cards.result]\nclass = "result"\n'
            + f'path = "{RESULT}"\ncommit = "{"a" * 40}"\nblob = "{"b" * 40}"\n'
        )
        review = project / REVIEW
        review.parent.mkdir(parents=True, exist_ok=True)
        review.write_text(
            'workstream_id = "sample-workstream"\n'
            'card_id = "M01-T04"\n'
            'attempt = "R01"\n'
            'verdict = "green"\n'
            'evidence_path = "implementation/workstreams/sample-workstream/evidence/MISSING-review.md"\n'
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
            'basis = "Independent probe reviewer."\n'
        )

        first = select_route(project, [MANIFEST], package_root=ROOT)
        result.write_text(result_text("version two: reviewed bytes changed"))
        second = select_route(project, [MANIFEST], package_root=ROOT)
        print("GREEN review before result mutation =>", first.disposition, first.obligation)
        print("GREEN review after result mutation  =>", second.disposition, second.obligation)
        print("Missing result evidence exists:", (project / "implementation/workstreams/sample-workstream/evidence/MISSING-result.md").exists())
        print("Missing review evidence exists:", (project / "implementation/workstreams/sample-workstream/evidence/MISSING-review.md").exists())


if __name__ == "__main__":
    ready_dependency_case()
    reviewed_result_case()
