from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.exact_locator import git_blob_sha
from tools.legacy_result_provenance import (
    LegacyResultProvenanceError,
    derive_path_only_review_acceptance,
    validate_legacy_result_migration_shape,
    verify_legacy_result_migration,
)

WS = "sample-workstream"
REPO = "owner/repo"
RESULT = f"implementation/workstreams/{WS}/results/M01-T01.md"
BOARD = f"implementation/workstreams/{WS}/TASK_BOARD.toml"
CARD = f"implementation/workstreams/{WS}/cards/M01-T01.md"


class LegacyResultProvenanceTests(unittest.TestCase):
    def git(self, root: Path, *args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            check=True, capture_output=True, text=True,
        ).stdout.strip()

    def fixture(self, *, same_commit: bool = False) -> tuple[tempfile.TemporaryDirectory[str], Path, dict, dict]:
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        self.git(root, "init", "-q")
        self.git(root, "config", "user.email", "fixture@example.invalid")
        self.git(root, "config", "user.name", "Fixture")
        for rel, text in (
            (CARD, "# Card\n"),
            (f"implementation/workstreams/{WS}/evidence/a.md", "# a\n"),
            (f"implementation/workstreams/{WS}/evidence/b.md", "# b\n"),
        ):
            p = root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(text)
        result = root / RESULT
        result.parent.mkdir(parents=True, exist_ok=True)
        result.write_text(
            "# Card Result\n"
            "- Card ID: M01-T01\n"
            "- Implementation subject: owner/product@commit:" + ("a" * 40) + "\n"
            f"- Evidence refs: implementation/workstreams/{WS}/evidence/a.md; "
            f"implementation/workstreams/{WS}/evidence/b.md\n"
            "- Tests/readback summary: GREEN\n"
        )
        if not same_commit:
            self.git(root, "add", CARD, RESULT, f"implementation/workstreams/{WS}/evidence")
            self.git(root, "commit", "-q", "-m", "legacy result")
            result_commit = self.git(root, "rev-parse", "HEAD")
        else:
            result_commit = "0" * 40
        result_blob = git_blob_sha(result.read_bytes())
        board = root / BOARD
        board.parent.mkdir(parents=True, exist_ok=True)
        if same_commit:
            result_commit = "1" * 40  # shape only; same-commit fixture rewrites after commit below
        board.write_text(
            f'workstream_id = "{WS}"\nrevision = 1\n'
            '[[cards]]\nid = "M01-T01"\nstatus = "done"\n'
            '[cards.result]\nclass = "result"\n'
            f'path = "{RESULT}"\ncommit = "{result_commit}"\nblob = "{result_blob}"\n'
        )
        self.git(root, "add", ".")
        self.git(root, "commit", "-q", "-m", "source board")
        source_commit = self.git(root, "rev-parse", "HEAD")
        if same_commit:
            # Rebuild source Board with its actual same snapshot commit impossible without
            # self-reference; the verifier reaches prior-durability before relying on
            # result_ref.commit semantics, so point it at any exact-shaped historical commit.
            pass
        proof = {
            "card_id": "M01-T01",
            "source_repository": REPO,
            "source_commit": source_commit,
            "source_path": RESULT,
            "source_blob": result_blob,
            "source_workstream": WS,
            "source_card": "M01-T01",
        }
        card = {
            "id": "M01-T01",
            "status": "done",
            "result": {
                "class": "result",
                "path": RESULT,
                "commit": (result_commit if not same_commit else source_commit),
                "blob": result_blob,
            },
        }
        return temp, root, card, proof

    def test_valid_proof_normalizes_semicolon_evidence(self) -> None:
        temp, root, card, proof = self.fixture()
        try:
            parsed, reads = verify_legacy_result_migration(
                project_root=root, project_repository=REPO,
                workstream_id=WS, card=card, proof=proof,
            )
            self.assertIsNone(parsed["result_status"])
            self.assertEqual(len(parsed["evidence_refs"]), 2)
            self.assertEqual(len(reads), 2)
        finally:
            temp.cleanup()

    def test_source_blob_mismatch_fails_closed(self) -> None:
        temp, root, card, proof = self.fixture()
        try:
            bad = dict(proof)
            bad["source_blob"] = "f" * 40
            with self.assertRaises(LegacyResultProvenanceError):
                verify_legacy_result_migration(
                    project_root=root, project_repository=REPO,
                    workstream_id=WS, card=card, proof=bad,
                )
        finally:
            temp.cleanup()

    def test_source_board_result_commit_must_be_exact_and_ancestral(self) -> None:
        for case in ("dangling", "off_history"):
            with self.subTest(case=case):
                temp, root, card, proof = self.fixture()
                try:
                    board = root / BOARD
                    original = card["result"]["commit"]
                    if case == "dangling":
                        bad_commit = "f" * 40
                    else:
                        self.git(root, "checkout", "-q", "-b", "off-history", original)
                        marker = root / "off-history.txt"
                        marker.write_text("sibling\n")
                        self.git(root, "add", marker.name)
                        self.git(root, "commit", "-q", "-m", "off-history sibling")
                        bad_commit = self.git(root, "rev-parse", "HEAD")
                        self.git(root, "checkout", "-q", "-")
                    board.write_text(board.read_text().replace(original, bad_commit, 1))
                    self.git(root, "add", BOARD)
                    self.git(root, "commit", "-q", "-m", f"source board {case} result commit")
                    bad_proof = dict(proof)
                    bad_proof["source_commit"] = self.git(root, "rev-parse", "HEAD")
                    with self.assertRaises(LegacyResultProvenanceError):
                        verify_legacy_result_migration(
                            project_root=root,
                            project_repository=REPO,
                            workstream_id=WS,
                            card=card,
                            proof=bad_proof,
                        )
                finally:
                    temp.cleanup()

    def test_source_board_must_prove_done_card(self) -> None:
        temp, root, card, proof = self.fixture()
        try:
            board = root / BOARD
            board.write_text(board.read_text().replace('status = "done"', 'status = "in_progress"'))
            self.git(root, "add", BOARD)
            self.git(root, "commit", "-q", "-m", "not done source")
            bad = dict(proof)
            bad["source_commit"] = self.git(root, "rev-parse", "HEAD")
            with self.assertRaisesRegex(LegacyResultProvenanceError, "already DONE"):
                verify_legacy_result_migration(
                    project_root=root, project_repository=REPO,
                    workstream_id=WS, card=card, proof=bad,
                )
        finally:
            temp.cleanup()

    def test_shape_rejects_extra_and_cross_card_identity(self) -> None:
        temp, root, card, proof = self.fixture()
        try:
            bad = dict(proof)
            bad["extra"] = "nope"
            with self.assertRaises(LegacyResultProvenanceError):
                validate_legacy_result_migration_shape(
                    bad, workstream_id=WS, card_id="M01-T01"
                )
            bad = dict(proof)
            bad["source_card"] = "M01-T99"
            with self.assertRaises(LegacyResultProvenanceError):
                validate_legacy_result_migration_shape(
                    bad, workstream_id=WS, card_id="M01-T01"
                )
        finally:
            temp.cleanup()

    def test_path_only_acceptance_is_derived_from_exact_attempt_commit(self) -> None:
        temp, root, card, proof = self.fixture()
        try:
            read = derive_path_only_review_acceptance(
                project_root=root, project_repository=REPO,
                attempt_ref={"commit": proof["source_commit"]},
                acceptance={"class": "task_card", "path": CARD},
                current_card_path=CARD,
            )
            self.assertIn(proof["source_commit"], read)
            (root / CARD).write_text("# mutated\n")
            with self.assertRaises(LegacyResultProvenanceError):
                derive_path_only_review_acceptance(
                    project_root=root, project_repository=REPO,
                    attempt_ref={"commit": proof["source_commit"]},
                    acceptance={"class": "task_card", "path": CARD},
                    current_card_path=CARD,
                )
        finally:
            temp.cleanup()


    def test_current_result_commit_must_match_source_board_identity(self) -> None:
        temp, root, card, proof = self.fixture()
        try:
            marker = root / "later.txt"
            marker.write_text("same Result bytes, later commit\n")
            self.git(root, "add", marker.name)
            self.git(root, "commit", "-q", "-m", "later same-result commit")
            card["result"]["commit"] = self.git(root, "rev-parse", "HEAD")
            with self.assertRaisesRegex(LegacyResultProvenanceError, "current Result commit differs"):
                verify_legacy_result_migration(
                    project_root=root, project_repository=REPO,
                    workstream_id=WS, card=card, proof=proof,
                )
        finally:
            temp.cleanup()

    def test_source_board_semantics_must_be_unambiguous(self) -> None:
        for case in ("wrong_workstream", "wrong_class", "duplicate_card"):
            with self.subTest(case=case):
                temp, root, card, proof = self.fixture()
                try:
                    board = root / BOARD
                    text = board.read_text()
                    if case == "wrong_workstream":
                        text = text.replace(
                            f'workstream_id = "{WS}"',
                            'workstream_id = "other-workstream"',
                            1,
                        )
                    elif case == "wrong_class":
                        text = text.replace('class = "result"', 'class = "authority"', 1)
                    else:
                        text += (
                            '\n[[cards]]\n'
                            'id = "M01-T01"\n'
                            'status = "in_progress"\n'
                        )
                    board.write_text(text)
                    self.git(root, "add", BOARD)
                    self.git(root, "commit", "-q", "-m", f"ambiguous source board {case}")
                    proof["source_commit"] = self.git(root, "rev-parse", "HEAD")
                    with self.assertRaises(LegacyResultProvenanceError):
                        verify_legacy_result_migration(
                            project_root=root, project_repository=REPO,
                            workstream_id=WS, card=card, proof=proof,
                        )
                finally:
                    temp.cleanup()

    def test_source_result_must_predate_source_board_snapshot(self) -> None:
        temp, root, card, proof = self.fixture()
        try:
            result = root / RESULT
            original = result.read_text()
            result.write_text(
                original.replace(
                    "- Tests/readback summary: GREEN",
                    "- Tests/readback summary: OTHER",
                )
            )
            self.git(root, "add", RESULT)
            self.git(root, "commit", "-q", "-m", "intervening Result bytes")
            result.write_text(original)
            self.git(root, "add", RESULT)
            self.git(root, "commit", "-q", "-m", "restore Result in source snapshot")
            proof["source_commit"] = self.git(root, "rev-parse", "HEAD")
            with self.assertRaisesRegex(LegacyResultProvenanceError, "source Result bytes changed"):
                verify_legacy_result_migration(
                    project_root=root, project_repository=REPO,
                    workstream_id=WS, card=card, proof=proof,
                )
        finally:
            temp.cleanup()

    def test_current_result_worktree_mutation_fails_closed(self) -> None:
        temp, root, card, proof = self.fixture()
        try:
            (root / RESULT).write_text((root / RESULT).read_text() + "\nmutated\n")
            with self.assertRaises(LegacyResultProvenanceError):
                verify_legacy_result_migration(
                    project_root=root, project_repository=REPO,
                    workstream_id=WS, card=card, proof=proof,
                )
        finally:
            temp.cleanup()

    def test_semicolon_adapter_rejects_cross_workstream_evidence(self) -> None:
        temp, root, card, proof = self.fixture()
        try:
            result = root / RESULT
            text = result.read_text().replace(
                f"implementation/workstreams/{WS}/evidence/a.md; "
                f"implementation/workstreams/{WS}/evidence/b.md",
                f"implementation/workstreams/{WS}/evidence/a.md; "
                "implementation/workstreams/other/evidence/x.md",
            )
            result.write_text(text)
            self.git(root, "add", RESULT)
            self.git(root, "commit", "-q", "-m", "legacy malformed evidence")
            new_result_commit = self.git(root, "rev-parse", "HEAD")
            new_blob = git_blob_sha(result.read_bytes())
            board = root / BOARD
            old_commit = card["result"]["commit"]
            old_blob = card["result"]["blob"]
            board.write_text(
                board.read_text()
                .replace(old_commit, new_result_commit, 1)
                .replace(old_blob, new_blob, 1)
            )
            self.git(root, "add", BOARD)
            self.git(root, "commit", "-q", "-m", "source board malformed evidence")
            proof["source_commit"] = self.git(root, "rev-parse", "HEAD")
            proof["source_blob"] = new_blob
            card["result"]["commit"] = new_result_commit
            card["result"]["blob"] = new_blob
            with self.assertRaisesRegex(LegacyResultProvenanceError, "outside workstream evidence"):
                verify_legacy_result_migration(
                    project_root=root, project_repository=REPO,
                    workstream_id=WS, card=card, proof=proof,
                )
        finally:
            temp.cleanup()

    def test_path_only_acceptance_rejects_other_card_and_partial_identity(self) -> None:
        temp, root, card, proof = self.fixture()
        try:
            with self.assertRaises(LegacyResultProvenanceError):
                derive_path_only_review_acceptance(
                    project_root=root, project_repository=REPO,
                    attempt_ref={"commit": proof["source_commit"]},
                    acceptance={
                        "class": "task_card",
                        "path": CARD.replace("M01-T01", "M01-T99"),
                    },
                    current_card_path=CARD,
                )
            with self.assertRaisesRegex(LegacyResultProvenanceError, "partially exact"):
                derive_path_only_review_acceptance(
                    project_root=root, project_repository=REPO,
                    attempt_ref={"commit": proof["source_commit"]},
                    acceptance={
                        "class": "task_card",
                        "path": CARD,
                        "commit": proof["source_commit"],
                    },
                    current_card_path=CARD,
                )
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()