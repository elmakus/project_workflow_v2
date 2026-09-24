#!/usr/bin/env python3
from tests.test_router import MANIFEST, ROOT, RouterTests
from tools.router import select_route

t = RouterTests("test_active_card_routes_to_runtime_neutral_execution")
temp, project = t.copy_fixture()
try:
    t.install_reviewable_result(project, "required")
    review_rel = t.add_review_attempt(project, "green")
    review_path = project / review_rel
    original = 'evidence_path = "implementation/workstreams/sample-workstream/evidence/review-R01.md"'
    review_path.write_text(
        review_path.read_text(encoding="utf-8").replace(original, 'evidence_path = "ghost-review-evidence.md"'),
        encoding="utf-8",
    )
    assert not (project / "ghost-review-evidence.md").exists()
    routed = select_route(project, [MANIFEST], package_root=ROOT)
    print(routed.disposition, routed.obligation)
    # Bug: a nonexistent evidence artifact still supports terminal GREEN.
    assert (routed.disposition, routed.obligation) == ("route", "post_review_finalization")
finally:
    temp.cleanup()
