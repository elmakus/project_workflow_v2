from __future__ import annotations

import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.exact_locator import git_blob_sha
from tools.review_acceptance_provenance import (
    ReviewAcceptanceProvenanceError,
    validate_review_acceptance_migration_shape,
    verify_review_acceptance_migration,
)

WS = "sample-workstream"
REPO = "owner/repo"
CARD_ID = "M01-T01"
ATTEMPT_ID = "R01"
CARD = f"implementation/workstreams/{WS}/cards/{CARD_ID}.md"
REVIEW = f"implementation/workstreams/{WS}/reviews/{CARD_ID}-{ATTEMPT_ID}.toml"


class ReviewAcceptanceProvenanceTests(unittest.TestCase):
    def git(self, root: Path, *args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(root), *args],
            check=True, capture_output=True, text=True,
        ).stdout.strip()

    def fixture(self):
        temp = tempfile.TemporaryDirectory()
        root = Path(temp.name)
        self.git(root, "init", "-q")
        self.git(root, "config", "user.email", "fixture@example.invalid")
        self.git(root, "config", "user.name", "Fixture")
        card = root / CARD
        card.parent.mkdir(parents=True, exist_ok=True)
        card.write_text("# Stable Card\n")
        self.git(root, "add", CARD)
        self.git(root, "commit", "-q", "-m", "card")
        review = root / REVIEW
        review.parent.mkdir(parents=True, exist_ok=True)
        review.write_text(
            f'workstream_id = "{WS}"\n'
            f'card_id = "{CARD_ID}"\n'
            f'attempt = "{ATTEMPT_ID}"\n'
            'verdict = "green"\n'
            'review_kind = "discovery"\n'
            '[acceptance]\n'
            'class = "task_card"\n'
            f'path = "{CARD}"\n'
        )
        self.git(root, "add", REVIEW)
        self.git(root, "commit", "-q", "-m", "historical review")
        source_commit = self.git(root, "rev-parse", "HEAD")
        source_blob = self.git(root, "rev-parse", f"HEAD:{REVIEW}")
        acceptance_blob = self.git(root, "rev-parse", f"HEAD:{CARD}")
        attempt = {
            "workstream_id": WS, "card_id": CARD_ID, "attempt": ATTEMPT_ID,
            "verdict": "green", "review_kind": "discovery",
            "acceptance": {"class": "task_card", "path": CARD},
        }
        ref = {"class": "review_attempt", "path": REVIEW, "commit": source_commit, "blob": source_blob}
        card_state = {"id": CARD_ID, "status": "done"}
        proof = {
            "card_id": CARD_ID,
            "attempt_id": ATTEMPT_ID,
            "source_repository": REPO,
            "source_commit": source_commit,
            "source_path": REVIEW,
            "source_blob": source_blob,
            "source_workstream": WS,
            "source_card": CARD_ID,
            "acceptance_path": CARD,
            "acceptance_blob": acceptance_blob,
        }
        return temp, root, card_state, ref, attempt, proof

    def test_exact_historical_proof_passes(self):
        temp, root, card, ref, attempt, proof = self.fixture()
        try:
            read = verify_review_acceptance_migration(
                project_root=root, project_repository=REPO, workstream_id=WS,
                card=card, attempt_ref=ref, attempt=attempt, proof=proof,
            )
            self.assertIn(proof["source_commit"], read)
            self.assertIn(proof["acceptance_blob"], read)
        finally:
            temp.cleanup()

    def test_current_card_mutation_fails_closed(self):
        temp, root, card, ref, attempt, proof = self.fixture()
        try:
            (root / CARD).write_text("# changed Card\n")
            with self.assertRaises(ReviewAcceptanceProvenanceError):
                verify_review_acceptance_migration(
                    project_root=root, project_repository=REPO, workstream_id=WS,
                    card=card, attempt_ref=ref, attempt=attempt, proof=proof,
                )
        finally:
            temp.cleanup()

    def test_partially_exact_source_acceptance_is_not_migratable(self):
        temp, root, card, ref, attempt, proof = self.fixture()
        try:
            attempt["acceptance"]["commit"] = proof["source_commit"]
            with self.assertRaisesRegex(ReviewAcceptanceProvenanceError, "wholly path-only"):
                verify_review_acceptance_migration(
                    project_root=root, project_repository=REPO, workstream_id=WS,
                    card=card, attempt_ref=ref, attempt=attempt, proof=proof,
                )
        finally:
            temp.cleanup()

    def test_non_green_or_wrong_locator_fails_closed(self):
        temp, root, card, ref, attempt, proof = self.fixture()
        try:
            bad_attempt = dict(attempt)
            bad_attempt["verdict"] = "red"
            with self.assertRaises(ReviewAcceptanceProvenanceError):
                verify_review_acceptance_migration(
                    project_root=root, project_repository=REPO, workstream_id=WS,
                    card=card, attempt_ref=ref, attempt=bad_attempt, proof=proof,
                )
            bad_ref = dict(ref)
            bad_ref["blob"] = "f" * 40
            with self.assertRaises(ReviewAcceptanceProvenanceError):
                verify_review_acceptance_migration(
                    project_root=root, project_repository=REPO, workstream_id=WS,
                    card=card, attempt_ref=bad_ref, attempt=attempt, proof=proof,
                )
        finally:
            temp.cleanup()

    def test_shape_rejects_cross_card_and_extra_fields(self):
        temp, root, card, ref, attempt, proof = self.fixture()
        try:
            bad = dict(proof)
            bad["source_card"] = "M01-T99"
            with self.assertRaises(ReviewAcceptanceProvenanceError):
                validate_review_acceptance_migration_shape(
                    bad, workstream_id=WS, card_id=CARD_ID
                )
            bad = dict(proof)
            bad["attempt_id"] = "R99"
            with self.assertRaisesRegex(
                ReviewAcceptanceProvenanceError, "source_path does not match claimed Card/attempt identity"
            ):
                validate_review_acceptance_migration_shape(
                    bad, workstream_id=WS, card_id=CARD_ID
                )
            bad = dict(proof)
            bad["extra"] = "no"
            with self.assertRaises(ReviewAcceptanceProvenanceError):
                validate_review_acceptance_migration_shape(
                    bad, workstream_id=WS, card_id=CARD_ID
                )
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
