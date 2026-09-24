#!/usr/bin/env python3
"""Non-mutating reproductions for unverified immutable Git identities."""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO))

from tests.test_router import MANIFEST, ROOT, RouterTests  # noqa: E402
from tools.router import select_route  # noqa: E402


def route(project: Path):
    return select_route(project, [MANIFEST], package_root=ROOT)


def case_reviewed_result_changes_without_identity_change() -> None:
    helper = RouterTests()
    temp, project = helper.copy_fixture()
    try:
        result_path = helper.install_reviewable_result(project, "required")
        helper.add_review_attempt(project, "green")

        before = (project / result_path).read_text()
        after = before.replace(
            "- Implementation subject: owner/repo@commit:" + ("a" * 40),
            "- Implementation subject: owner/repo@commit:" + ("c" * 40),
        )
        assert before != after
        (project / result_path).write_text(after)

        # Board + review still self-assert the original a*40/b*40 exact identity.
        routed = route(project)
        print((routed.disposition, routed.obligation), routed.reason)
        assert (routed.disposition, routed.obligation) == ("route", "post_review_finalization")
    finally:
        temp.cleanup()


def case_ready_dependency_same_tuple_changed_file_launches() -> None:
    helper = RouterTests()
    temp, project = helper.copy_fixture()
    try:
        dependency_path = "implementation/workstreams/sample-workstream/results/M01-T03.md"
        commit = "a" * 40
        blob = "b" * 40
        dependency = f"{dependency_path}@{commit}:{blob}"

        helper.install_done_predecessor(
            project, path=dependency_path, commit=commit, blob=blob
        )
        helper.make_ready_card(project, dependencies=dependency)

        # Same declared commit/blob tuple, but current path content changes.
        (project / dependency_path).write_text("# changed dependency content\n")

        routed = route(project)
        print((routed.disposition, routed.obligation), routed.reason)
        assert (routed.disposition, routed.obligation) == ("route", "execution_prep")
    finally:
        temp.cleanup()


if __name__ == "__main__":
    case_reviewed_result_changes_without_identity_change()
    case_ready_dependency_same_tuple_changed_file_launches()
    print("reproduced unverified Git-identity defects")
