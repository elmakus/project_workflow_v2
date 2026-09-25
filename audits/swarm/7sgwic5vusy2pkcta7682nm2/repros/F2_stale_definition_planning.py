from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from tests.test_router import RouterTests, MANIFEST, CARD
from tools.router import select_route

rt = RouterTests()
temp, project = rt.copy_fixture()
try:
    rt.install_green_definition(project)
    definition = project / "implementation/workstreams/sample-workstream/DEFINITION.toml"
    definition.write_text(definition.read_text().replace('revision = "R1"', 'revision = "R2"'))

    rt.install_state_record(
        project, "planning", "planning", "PLANNING.toml",
        rt.planning_content(state="approved", premium_b="satisfied", premium_c="satisfied"),
    )
    rt.install_state_record(
        project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
        rt.plan_review_content("green"),
    )

    routed = select_route(project, [MANIFEST], package_root=ROOT)
    print(routed)
    assert (routed.disposition, routed.obligation) == ("route", "execution")
    print("BUG REPRODUCED: Definition R2 reused the old Definition-R1 Planning/premium cycle.")
finally:
    temp.cleanup()
