#!/usr/bin/env python3
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tools.router import select_route

FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"
RESULT = "implementation/workstreams/sample-workstream/results/M01-T04.md"

with tempfile.TemporaryDirectory() as tmp:
    project = Path(tmp) / "project"
    shutil.copytree(FIXTURE, project)

    authority = project / "requirements" / "REQUIREMENTS.md"
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("# accepted authority\n")

    card = project / CARD
    card.write_text(
        "# Fixture Card\n"
        "- Card ID: M01-T04\n"
        "- Included scope: terminal integrity probe\n"
        "- Excluded scope: none\n"
        "- Authority refs: requirements/REQUIREMENTS.md\n"
        "- Dependencies: none\n"
        "- Acceptance: exact result and GREEN review are durable\n"
        "- Required tests/readback: terminal integrity probe\n"
        "- Review requirement: required\n"
        "- Technical contract: none\n"
    )

    board = project / BOARD
    board.write_text(
        board.read_text().replace('status = "in_progress"', 'status = "done"', 1)
        + '\n[cards.result]\n'
        + 'class = "result"\n'
        + f'path = "{RESULT}"\n'
        + 'commit = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"\n'
        + 'blob = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"\n'
    )
    assert not (project / RESULT).exists()

    routed = select_route(project, [MANIFEST], package_root=ROOT)
    print(routed)
    print("Card requires review, has zero attempts, and its result file does not exist.")
    assert (routed.disposition, routed.obligation) == ("route", "close")
    assert f"project:{CARD}" not in routed.read_set
    assert f"project:{RESULT}" not in routed.read_set
