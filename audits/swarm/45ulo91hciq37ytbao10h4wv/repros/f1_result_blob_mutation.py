#!/usr/bin/env python3
import hashlib

from tests.test_router import BOARD, MANIFEST, ROOT, RouterTests
from tools.router import select_route

t = RouterTests("test_active_card_routes_to_runtime_neutral_execution")
temp, project = t.copy_fixture()
try:
    result_rel = t.install_reviewable_result(project, "required")
    review_rel = t.add_review_attempt(project, "green")
    result_path = project / result_rel
    original = result_path.read_bytes()
    old_blob = hashlib.sha1(f"blob {len(original)}\0".encode() + original).hexdigest()

    board_path = project / BOARD
    board_path.write_text(board_path.read_text().replace("b" * 40, old_blob), encoding="utf-8")
    review_path = project / review_rel
    review_path.write_text(review_path.read_text().replace("b" * 40, old_blob), encoding="utf-8")

    result_path.write_bytes(original + b"\n<!-- post-review mutation -->\n")
    routed = select_route(project, [MANIFEST], package_root=ROOT)
    print(routed.disposition, routed.obligation)
    # Bug: changed bytes are still authorized by the stale declared blob.
    assert (routed.disposition, routed.obligation) == ("route", "post_review_finalization")
finally:
    temp.cleanup()
