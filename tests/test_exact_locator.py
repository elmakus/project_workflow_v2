#!/usr/bin/env python3
"""RF007 exact locator/readback regressions (H010/H020/H029)."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.exact_locator import (
    ExactLocatorError,
    git_blob_sha,
    normalize_locator_path,
    verify_exact_git_locator,
    verify_worktree_freshness,
)
from tools.router import select_route

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/router/valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"
RESULT = "implementation/workstreams/sample-workstream/results/M01-T04.md"
EVIDENCE = "implementation/workstreams/sample-workstream/evidence/M01-T04.md"
REPOSITORY = "owner/router-fixture"


def git(project: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(project), *args],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def fresh_git_project() -> tuple[tempfile.TemporaryDirectory, Path]:
    temp = tempfile.TemporaryDirectory()
    project = Path(temp.name) / "project"
    shutil.copytree(FIXTURE, project)
    subprocess.run(["git", "init", "-q", str(project)], check=True)
    subprocess.run(
        ["git", "-C", str(project), "config", "user.email", "rf007@example.invalid"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(project), "config", "user.name", "RF007"], check=True
    )
    return temp, project


def commit_file(project: Path, rel: str, content: str) -> tuple[str, str]:
    target = project / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content)
    git(project, "add", rel)
    git(project, "commit", "-qm", f"rf007 {rel}")
    commit = git(project, "rev-parse", "HEAD")
    blob = git(project, "rev-parse", f"HEAD:{rel}")
    return commit, blob


def card_content(*, dependencies: str = "none", review_requirement: str = "none") -> str:
    return (
        "# Fixture Card\n"
        "- Card ID: M01-T04\n"
        "- Included scope: prove exact locator readback\n"
        "- Excluded scope: runtime-specific orchestration\n"
        "- Authority refs: requirements/REQUIREMENTS.md\n"
        f"- Dependencies: {dependencies}\n"
        "- Acceptance: route only after current launch inputs are valid\n"
        "- Required tests/readback: rf007 regression\n"
        f"- Review requirement: {review_requirement}\n"
        "- Technical contract: none\n"
    )


class NormalizeLocatorPathTests(unittest.TestCase):
    def test_accepts_canonical_repo_relative_paths(self) -> None:
        for raw in (
            "PROJECT.md",
            "requirements/REQUIREMENTS.md",
            "implementation/workstreams/w/evidence/x.md",
            "implementation/workstreams/w/planning_classifications/P2-E01.toml",
            "workflow/ROUTER.md",
            "contracts/sample-api.md",
        ):
            self.assertEqual(normalize_locator_path(raw, "probe"), raw)

    def test_rejects_separator_traversal_and_alias_paths(self) -> None:
        bad = (
            "",
            "   ",
            " a.md",
            "a.md ",
            "/absolute.md",
            "a/../b.md",
            "../outside.md",
            "a/./b.md",
            "./a.md",
            "a//b.md",
            "a/b.md/",
            ".",
            "..",
            "evidence\\x.md",
            "evidence\\..\\x.md",
            "C:/evidence/x.md",
            "C:evidence/x.md",
            "\\\\server\\share\\x.md",
            "a\x00b.md",
            "a\nb.md",
        )
        for raw in bad:
            with self.subTest(path=raw):
                with self.assertRaises(ExactLocatorError):
                    normalize_locator_path(raw, "probe")
        for raw in (None, 42, b"a.md", ["a.md"]):
            with self.subTest(path=raw):
                with self.assertRaises(ExactLocatorError):
                    normalize_locator_path(raw, "probe")  # type: ignore[arg-type]

    def test_error_names_label_and_offending_value(self) -> None:
        with self.assertRaises(ExactLocatorError) as caught:
            normalize_locator_path("a\\b.md", "probe.label")
        self.assertIn("probe.label", str(caught.exception))


class GitBlobShaTests(unittest.TestCase):
    def test_matches_git_hash_object_oracle(self) -> None:
        temp, project = fresh_git_project()
        try:
            for payload in (b"", b"# evidence\n", b"\x00\x01binary", b"x" * 5000):
                expected = subprocess.run(
                    ["git", "-C", str(project), "hash-object", "--stdin"],
                    input=payload, capture_output=True, check=True,
                ).stdout.decode().strip()
                self.assertEqual(git_blob_sha(payload), expected)
        finally:
            temp.cleanup()


class VerifyExactGitLocatorTests(unittest.TestCase):
    def test_valid_locator_passes_with_exact_key(self) -> None:
        temp, project = fresh_git_project()
        try:
            commit, blob = commit_file(project, EVIDENCE, "# evidence\n")
            verified = verify_exact_git_locator(
                project_root=project, repository=REPOSITORY,
                expected_repository=REPOSITORY, commit=commit,
                path=EVIDENCE, blob=blob, label="probe",
            )
            self.assertEqual(verified.key, f"{REPOSITORY}@{commit}:{EVIDENCE}@{blob}")
        finally:
            temp.cleanup()

    def test_dangling_commit_path_and_blob_fail_closed(self) -> None:
        temp, project = fresh_git_project()
        try:
            commit, blob = commit_file(project, EVIDENCE, "# evidence\n")
            with self.assertRaises(ExactLocatorError) as dangling_commit:
                verify_exact_git_locator(
                    project_root=project, repository=REPOSITORY,
                    expected_repository=REPOSITORY, commit="a" * 40,
                    path=EVIDENCE, blob=blob, label="probe",
                )
            self.assertEqual(dangling_commit.exception.kind, "dangling")
            with self.assertRaises(ExactLocatorError) as dangling_path:
                verify_exact_git_locator(
                    project_root=project, repository=REPOSITORY,
                    expected_repository=REPOSITORY, commit=commit,
                    path="implementation/workstreams/sample-workstream/evidence/missing.md",
                    blob=blob, label="probe",
                )
            self.assertEqual(dangling_path.exception.kind, "dangling")
            with self.assertRaises(ExactLocatorError) as mismatch:
                verify_exact_git_locator(
                    project_root=project, repository=REPOSITORY,
                    expected_repository=REPOSITORY, commit=commit,
                    path=EVIDENCE, blob="b" * 40, label="probe",
                )
            self.assertEqual(mismatch.exception.kind, "blob_mismatch")
        finally:
            temp.cleanup()

    def test_wrong_repository_identity_and_shape_fail_closed(self) -> None:
        temp, project = fresh_git_project()
        try:
            commit, blob = commit_file(project, EVIDENCE, "# evidence\n")
            with self.assertRaises(ExactLocatorError) as wrong_repo:
                verify_exact_git_locator(
                    project_root=project, repository="owner/other",
                    expected_repository=REPOSITORY, commit=commit,
                    path=EVIDENCE, blob=blob, label="probe",
                )
            self.assertEqual(wrong_repo.exception.kind, "repository")
            with self.assertRaises(ExactLocatorError) as bad_hex:
                verify_exact_git_locator(
                    project_root=project, repository=REPOSITORY,
                    expected_repository=REPOSITORY, commit="short",
                    path=EVIDENCE, blob=blob, label="probe",
                )
            self.assertEqual(bad_hex.exception.kind, "identity")
            with self.assertRaises(ExactLocatorError) as unsafe:
                verify_exact_git_locator(
                    project_root=project, repository=REPOSITORY,
                    expected_repository=REPOSITORY, commit=commit,
                    path="evidence\\..\\x.md", blob=blob, label="probe",
                )
            self.assertEqual(unsafe.exception.kind, "unsafe_path")
        finally:
            temp.cleanup()

    def test_non_blob_object_fails_closed(self) -> None:
        temp, project = fresh_git_project()
        try:
            commit, _ = commit_file(project, EVIDENCE, "# evidence\n")
            tree = git(project, "rev-parse", f"{commit}:implementation")
            with self.assertRaises(ExactLocatorError) as caught:
                verify_exact_git_locator(
                    project_root=project, repository=REPOSITORY,
                    expected_repository=REPOSITORY, commit=commit,
                    path="implementation", blob=tree, label="probe",
                )
            self.assertEqual(caught.exception.kind, "not_blob")
        finally:
            temp.cleanup()


class VerifyWorktreeFreshnessTests(unittest.TestCase):
    def test_fresh_bytes_pass_and_mutated_bytes_fail(self) -> None:
        temp, project = fresh_git_project()
        try:
            _, blob = commit_file(project, EVIDENCE, "# v1\n")
            content = verify_worktree_freshness(
                project_root=project, path=EVIDENCE, blob=blob, label="probe"
            )
            self.assertEqual(content, b"# v1\n")
            (project / EVIDENCE).write_text("# v2 mutated\n")
            with self.assertRaises(ExactLocatorError) as caught:
                verify_worktree_freshness(
                    project_root=project, path=EVIDENCE, blob=blob, label="probe"
                )
            self.assertEqual(caught.exception.kind, "mutated")
        finally:
            temp.cleanup()

    def test_missing_file_and_symlink_escape_fail_closed(self) -> None:
        temp, project = fresh_git_project()
        try:
            outside = Path(temp.name) / "outside.md"
            outside.write_text("# outside\n")
            link = project / EVIDENCE
            link.parent.mkdir(parents=True, exist_ok=True)
            link.symlink_to(outside)
            with self.assertRaises(ExactLocatorError) as escaped:
                verify_worktree_freshness(
                    project_root=project, path=EVIDENCE,
                    blob=git_blob_sha(b"# outside\n"), label="probe",
                )
            self.assertEqual(escaped.exception.kind, "escape")
            link.unlink()
            with self.assertRaises(ExactLocatorError) as missing:
                verify_worktree_freshness(
                    project_root=project, path=EVIDENCE,
                    blob=git_blob_sha(b"# outside\n"), label="probe",
                )
            self.assertEqual(missing.exception.kind, "missing")
        finally:
            temp.cleanup()


class RF007ServingBoundaryTests(unittest.TestCase):
    def install_result(
        self, project: Path, commit: str, blob: str, *,
        evidence_ref: str = EVIDENCE, evidence_exists: bool = True,
    ) -> None:
        (project / CARD).write_text(card_content())
        authority = project / "requirements/REQUIREMENTS.md"
        authority.parent.mkdir(parents=True, exist_ok=True)
        authority.write_text("# Accepted authority\n")
        board = project / BOARD
        board.write_text(
            board.read_text()
            + '\n[cards.result]\nclass = "result"\n'
            + f'path = "{RESULT}"\ncommit = "{commit}"\nblob = "{blob}"\n'
        )
        if evidence_exists:
            target = project / evidence_ref
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# Verified evidence\n")
        result_file = project / RESULT
        result_file.parent.mkdir(parents=True, exist_ok=True)
        result_file.write_text(
            "# Card Result\n"
            "- Card ID: M01-T04\n"
            "- Implementation subject: owner/repo@commit:" + ("a" * 40) + "\n"
            f"- Evidence refs: {evidence_ref}\n"
            "- Tests/readback summary: GREEN\n"
        )

    def install_ready_dependency(
        self, project: Path, *, path: str, commit: str, blob: str,
    ) -> None:
        board = project / BOARD
        board.write_text(board.read_text().replace('status = "in_progress"', 'status = "ready"'))
        predecessor = (
            '[[cards]]\n'
            'id = "M01-T03"\n'
            'status = "done"\n'
            '[cards.contract]\n'
            'class = "task_card"\n'
            'path = "implementation/workstreams/sample-workstream/cards/M01-T03.md"\n'
            '[cards.result]\n'
            'class = "result"\n'
            f'path = "{path}"\n'
            f'commit = "{commit}"\n'
            f'blob = "{blob}"\n\n'
        )
        board.write_text(board.read_text().replace("[[cards]]\n", predecessor + "[[cards]]\n", 1))
        (project / "implementation/workstreams/sample-workstream/cards/M01-T03.md").write_text(
            "# predecessor Card\n"
        )
        (project / CARD).write_text(
            card_content(dependencies=f"{path}@{commit}:{blob}")
        )
        authority = project / "requirements/REQUIREMENTS.md"
        authority.parent.mkdir(parents=True, exist_ok=True)
        authority.write_text("# Accepted authority\n")

    def assert_recovery(self, project: Path) -> None:
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        self.assertEqual(
            (routed.disposition, routed.obligation),
            ("recovery", "recovery_boundary"),
            routed.reason,
        )

    def test_h010_dangling_result_identity_cannot_authorize(self) -> None:
        temp, project = fresh_git_project()
        try:
            self.install_result(project, "a" * 40, "b" * 40)
            git(project, "add", "-A")
            git(project, "commit", "-qm", "dangling")
            self.assert_recovery(project)
        finally:
            temp.cleanup()

    def test_h010_missing_result_evidence_cannot_authorize(self) -> None:
        temp, project = fresh_git_project()
        try:
            self.install_result(project, "a" * 40, "b" * 40, evidence_exists=False)
            self.assert_recovery(project)
        finally:
            temp.cleanup()

    def test_h010_dangling_ready_dependency_cannot_launch(self) -> None:
        temp, project = fresh_git_project()
        try:
            (project / RESULT).parent.mkdir(parents=True, exist_ok=True)
            (project / RESULT).write_text("# predecessor result\n")
            self.install_ready_dependency(
                project, path=RESULT, commit="a" * 40, blob="b" * 40
            )
            git(project, "add", "-A")
            git(project, "commit", "-qm", "dangling dep")
            self.assert_recovery(project)
        finally:
            temp.cleanup()

    def test_h020_mutated_ready_dependency_cannot_launch(self) -> None:
        temp, project = fresh_git_project()
        try:
            commit, blob = commit_file(project, RESULT, "# v1 predecessor bytes\n")
            self.install_ready_dependency(project, path=RESULT, commit=commit, blob=blob)
            (project / RESULT).write_text("# v2 mutated bytes at the same path\n")
            self.assert_recovery(project)
        finally:
            temp.cleanup()

    def test_h020_mutated_result_bytes_cannot_authorize(self) -> None:
        temp, project = fresh_git_project()
        try:
            self.install_result(project, "0" * 40, "0" * 40)
            git(project, "add", "-A")
            git(project, "commit", "-qm", "result v1")
            commit = git(project, "rev-parse", "HEAD")
            blob = git(project, "rev-parse", f"HEAD:{RESULT}")
            board = project / BOARD
            board.write_text(
                board.read_text()
                .replace(f'commit = "{"0" * 40}"', f'commit = "{commit}"')
                .replace(f'blob = "{"0" * 40}"', f'blob = "{blob}"')
            )
            (project / RESULT).write_text(
                "# Card Result\n"
                "- Card ID: M01-T04\n"
                "- Implementation subject: mutated bytes\n"
                f"- Evidence refs: {EVIDENCE}\n"
                "- Tests/readback summary: GREEN\n"
            )
            self.assert_recovery(project)
        finally:
            temp.cleanup()

    def test_h029_backslash_evidence_alias_cannot_authorize(self) -> None:
        temp, project = fresh_git_project()
        try:
            evil = "implementation/workstreams/sample-workstream/evidence/sub\\..\\evil.md"
            self.install_result(project, "a" * 40, "b" * 40, evidence_ref=evil,
                                evidence_exists=False)
            self.assert_recovery(project)
        finally:
            temp.cleanup()

    def test_h029_evidence_symlink_escape_cannot_authorize(self) -> None:
        temp, project = fresh_git_project()
        try:
            self.install_result(project, "a" * 40, "b" * 40, evidence_exists=False)
            outside = Path(temp.name) / "outside.md"
            outside.write_text("# outside\n")
            (project / EVIDENCE).parent.mkdir(parents=True, exist_ok=True)
            (project / EVIDENCE).symlink_to(outside)
            self.assert_recovery(project)
        finally:
            temp.cleanup()

    def test_h029_backslash_authority_alias_cannot_launch(self) -> None:
        temp, project = fresh_git_project()
        try:
            board = project / BOARD
            board.write_text(board.read_text().replace('status = "in_progress"', 'status = "ready"'))
            (project / CARD).write_text(card_content().replace(
                "- Authority refs: requirements/REQUIREMENTS.md",
                "- Authority refs: requirements/sub\\..\\REQUIREMENTS.md",
            ))
            authority = project / "requirements/REQUIREMENTS.md"
            authority.parent.mkdir(parents=True, exist_ok=True)
            authority.write_text("# Accepted authority\n")
            self.assert_recovery(project)
        finally:
            temp.cleanup()

    def test_valid_result_with_exact_identity_authorizes(self) -> None:
        temp, project = fresh_git_project()
        try:
            self.install_result(project, "0" * 40, "0" * 40)
            git(project, "add", "-A")
            git(project, "commit", "-qm", "result v1")
            commit = git(project, "rev-parse", "HEAD")
            blob = git(project, "rev-parse", f"HEAD:{RESULT}")
            board = project / BOARD
            board.write_text(
                board.read_text()
                .replace(f'commit = "{"0" * 40}"', f'commit = "{commit}"')
                .replace(f'blob = "{"0" * 40}"', f'blob = "{blob}"')
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "result_reconciliation"),
                routed.reason,
            )
            self.assertIn(f"project:{RESULT}", routed.read_set)
        finally:
            temp.cleanup()

    def test_valid_ready_dependency_with_exact_identity_launches(self) -> None:
        temp, project = fresh_git_project()
        try:
            commit, blob = commit_file(project, RESULT, "# v1 predecessor bytes\n")
            self.install_ready_dependency(project, path=RESULT, commit=commit, blob=blob)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "execution_prep"),
                routed.reason,
            )
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
