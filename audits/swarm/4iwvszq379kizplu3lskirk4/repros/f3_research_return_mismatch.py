#!/usr/bin/env python3
from tests.test_router import RouterTests, MANIFEST, ROOT
from tools.router import select_route

t = RouterTests()
temp, project = t.copy_fixture()
try:
    t.install_board_research(project, state="complete", reconciliation="pending")
    research = project / "implementation/workstreams/sample-workstream/RESEARCH.toml"
    text = research.read_text().replace(
        'return_target = "execution_resolution:M01-T04"',
        'return_target = "execution_resolution:M99"',
    )
    research.write_text(text)

    routed = select_route(project, [MANIFEST], package_root=ROOT)
    print(routed)
    assert routed.disposition == "route"
    assert routed.obligation == "execution_resolution"
    assert routed.subject == "M99"
finally:
    temp.cleanup()
