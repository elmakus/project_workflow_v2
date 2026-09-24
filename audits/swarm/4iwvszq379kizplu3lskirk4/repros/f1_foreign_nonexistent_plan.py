#!/usr/bin/env python3
from pathlib import Path
from tests.test_router import RouterTests, MANIFEST, ROOT
from tools.router import select_route

t = RouterTests()
temp, project = t.copy_fixture()
try:
    t.install_green_definition(project)
    t.install_state_record(
        project, "planning", "planning", "PLANNING.toml",
        t.planning_content(state="approved", premium_b="satisfied", premium_c="satisfied"),
    )
    t.install_state_record(
        project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
        t.plan_review_content("green"),
    )
    t.remove_board_locator(project)

    assert "repository = \"owner/router-fixture\"" in (project / "PROJECT.md").read_text()
    assert not (project / "planning/MASTER_PLAN.md").exists()

    routed = select_route(project, [MANIFEST], package_root=ROOT)
    print(routed)
    assert routed.disposition == "route"
    assert routed.obligation == "execution_prep"
    assert routed.subject.startswith("owner/repo@")
finally:
    temp.cleanup()
