#!/usr/bin/env python3
"""F3 focused repro: same-path-changed DONE dependency passes launch refresh."""

from __future__ import annotations
import shutil
import tempfile
from pathlib import Path
from tools.router import select_route

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "tests/fixtures/router/valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"
DEP_RESULT = "implementation/workstreams/sample-workstream/results/M01-T03.md"
COMMIT = "a" * 40
BLOB = "b" * 40

with tempfile.TemporaryDirectory() as td:
    project = Path(td) / "project"
    shutil.copytree(FIXTURE, project)

    board = project / BOARD
    original = board.read_text(encoding="utf-8")
    predecessor = (
        '[[cards]]\n'
        'id = "M01-T03"\n'
        'status = "done"\n'
        '[cards.contract]\n'
        'class = "task_card"\n'
        'path = "implementation/workstreams/sample-workstream/cards/M01-T03.md"\n'
        '[cards.result]\n'
        'class = "result"\n'
        f'path = "{DEP_RESULT}"\n'
        f'commit = "{COMMIT}"\n'
        f'blob = "{BLOB}"\n\n'
    )
    board.write_text(
        original.replace('[[cards]]\n', predecessor + '[[cards]]\n', 1)
        .replace('status = "in_progress"', 'status = "ready"', 1),
        encoding="utf-8",
    )

    dependency = f"{DEP_RESULT}@{COMMIT}:{BLOB}"
    (project / CARD).write_text(
        "# Fixture Card\n"
        "- Card ID: M01-T04\n"
        "- Included scope: consume exact predecessor truth\n"
        "- Excluded scope: unrelated work\n"
        "- Authority refs: requirements/REQUIREMENTS.md\n"
        f"- Dependencies: {dependency}\n"
        "- Acceptance: launch only on exact predecessor result\n"
        "- Required tests/readback: launch refresh\n"
        "- Review requirement: none\n"
        "- Technical contract: none\n",
        encoding="utf-8",
    )
    auth = project / "requirements/REQUIREMENTS.md"
    auth.parent.mkdir(parents=True, exist_ok=True)
    auth.write_text("# authority\n", encoding="utf-8")

    dep = project / DEP_RESULT
    dep.parent.mkdir(parents=True, exist_ok=True)
    dep.write_text("# predecessor result v1\n", encoding="utf-8")

    before = select_route(project, [MANIFEST], package_root=ROOT)
    assert before.obligation == "execution_prep", before

    # Change the dependency bytes while leaving both declared commit/blob tuples stale.
    dep.write_text("# materially changed predecessor result v2\n", encoding="utf-8")
    after = select_route(project, [MANIFEST], package_root=ROOT)
    print(after)
    assert after.obligation == "execution_prep", after
