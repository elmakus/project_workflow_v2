#!/usr/bin/env python3
"""F1 focused repro: a consumed JIT trigger has no required downstream Card binding."""

from __future__ import annotations
import shutil
import tempfile
from pathlib import Path
from tools.router import select_route

ROOT = Path(__file__).resolve().parents[3]
FIXTURE = ROOT / "tests/fixtures/router/valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
RESULT = "implementation/workstreams/sample-workstream/results/M01-T04.md"

with tempfile.TemporaryDirectory() as td:
    project = Path(td) / "project"
    shutil.copytree(FIXTURE, project)
    board = project / BOARD
    board.write_text(
        board.read_text(encoding="utf-8").replace('status = "in_progress"', 'status = "done"', 1)
        + "\n[cards.result]\n"
        + 'class = "result"\n'
        + f'path = "{RESULT}"\n'
        + "\n[[jit_triggers]]\n"
        + 'id = "after-M01-T04"\n'
        + 'after_card = "M01-T04"\n'
        + 'state = "consumed"\n'
        + 'condition = "Materialize the downstream Card after predecessor truth exists."\n',
        encoding="utf-8",
    )
    result = project / RESULT
    result.parent.mkdir(parents=True, exist_ok=True)
    result.write_text("# predecessor result\n", encoding="utf-8")

    routed = select_route(project, [MANIFEST], package_root=ROOT)
    print(routed)
    assert (routed.disposition, routed.obligation) == ("route", "close")
