#!/usr/bin/env python3
"""Non-mutating reproduction for contradictory Research owner/return binding."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from tests.test_router import MANIFEST, ROOT, RouterTests  # noqa: E402
from tools.router import select_route  # noqa: E402


def mismatched_research() -> str:
    return (
        'state = "complete"\n'
        'workstream_id = "sample-workstream"\n'
        'origin_role = "intake"\n'
        'origin_subject = "repair:v1"\n'
        'return_target = "definition"\n'
        'return_reconciliation = "pending"\n'
        'return_result = ""\n'
        'finding = "bounded finding"\n'
        'limitations = "none"\n'
        'conflicts = "none"\n'
        '[[sources]]\nclass = "official_upstream"\nstatus = "checked"\nweight = "primary"\n'
        '[[sources]]\nclass = "project_runtime"\nstatus = "checked"\nweight = "direct"\n'
        '[[sources]]\nclass = "tracker_discussion"\nstatus = "not_relevant"\nweight = "supporting"\n'
        '[[sources]]\nclass = "practitioner_community"\nstatus = "not_relevant"\nweight = "supporting"\n'
    )


if __name__ == "__main__":
    helper = RouterTests()
    temp, project = helper.copy_fixture()
    try:
        helper.install_state_record(
            project, "research", "research", "RESEARCH.toml", mismatched_research()
        )
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        print((routed.disposition, routed.obligation), routed.subject, routed.reason)
        assert (routed.disposition, routed.obligation) == ("route", "definition")
        print("reproduced Research origin/return owner contradiction")
    finally:
        temp.cleanup()
