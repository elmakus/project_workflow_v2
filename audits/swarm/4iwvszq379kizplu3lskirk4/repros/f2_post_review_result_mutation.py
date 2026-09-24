#!/usr/bin/env python3
from tests.test_router import RouterTests, MANIFEST, ROOT
from tools.router import select_route

t = RouterTests()
temp, project = t.copy_fixture()
try:
    result_path = t.install_reviewable_result(project, "required")
    t.add_review_attempt(project, "green")

    before = select_route(project, [MANIFEST], package_root=ROOT)
    assert before.obligation == "post_review_finalization"

    result_file = project / result_path
    text = result_file.read_text()
    text = text.replace(
        "Implementation subject: owner/repo@commit:" + ("a" * 40),
        "Implementation subject: owner/repo@commit:" + ("c" * 40),
    )
    result_file.write_text(text)

    after = select_route(project, [MANIFEST], package_root=ROOT)
    print(after)
    assert after.disposition == "route"
    assert after.obligation == "post_review_finalization"
finally:
    temp.cleanup()
