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
    brainstorm = project / "implementation/workstreams/sample-workstream/BRAINSTORM.toml"
    brainstorm.write_text(
        brainstorm.read_text().replace(
            "explicit_user_stop = false",
            "explicit_user_stop = true",
        )
    )
    routed = select_route(project, [MANIFEST], package_root=ROOT)
    print(routed)
    assert (routed.disposition, routed.obligation) == ("route", "planning")
    print("BUG REPRODUCED: durable explicit user stop was bypassed by Definition/Planning precedence.")
finally:
    temp.cleanup()
