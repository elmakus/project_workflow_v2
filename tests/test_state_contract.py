from __future__ import annotations

import copy
import unittest
from pathlib import Path

from tools.state_contract import (
    ValidationError,
    _read_toml,
    read_project,
    reject_prohibited_keys,
    validate_board,
    validate_bundle,
    validate_project,
    validate_review,
    validate_workstream,
)

ROOT = Path(__file__).resolve().parents[1]
VALID = ROOT / "tests" / "fixtures" / "state" / "valid"
INVALID = ROOT / "tests" / "fixtures" / "state" / "invalid"


class StateEnvelopeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.workstream = _read_toml(VALID / "WORKSTREAM.toml")

    def test_valid_bundle_and_expected_revision(self) -> None:
        validate_bundle(
            VALID / "PROJECT.md",
            VALID / "WORKSTREAM.toml",
            VALID / "TASK_BOARD.toml",
            VALID / "REVIEW_ATTEMPT.toml",
            VALID / "EXTERNAL_EFFECT.toml",
            expected_revision=7,
        )

    def test_stale_revision_fails_closed(self) -> None:
        board = _read_toml(VALID / "TASK_BOARD.toml")
        with self.assertRaisesRegex(ValidationError, "stale expected revision"):
            validate_board(board, self.workstream, expected_revision=6)

    def test_wrong_workstream_and_branch_fail_closed(self) -> None:
        for name in ("wrong-workstream-board.toml", "wrong-branch-board.toml"):
            with self.subTest(name=name), self.assertRaises(ValidationError):
                validate_board(_read_toml(INVALID / name), self.workstream)

    def test_one_card_in_progress_is_enforced(self) -> None:
        with self.assertRaisesRegex(ValidationError, "more than one"):
            validate_board(_read_toml(INVALID / "two-active-board.toml"), self.workstream)

    def test_prohibited_policy_runtime_scheduler_keys_fail(self) -> None:
        with self.assertRaisesRegex(ValidationError, "execution_policy"):
            validate_board(_read_toml(INVALID / "prohibited-policy-board.toml"), self.workstream)
        value = _read_toml(VALID / "TASK_BOARD.toml")
        for key in ("runtime", "runtime_id", "model_id", "session_id", "worker", "worker_id", "active_execution", "lane", "lane_id", "context_health"):
            candidate = copy.deepcopy(value)
            candidate[key] = "forbidden"
            with self.subTest(key=key), self.assertRaises(ValidationError):
                validate_board(candidate, self.workstream)

    def test_locator_class_missing_and_cross_workstream_path_fail(self) -> None:
        for name in ("wrong-class-workstream.toml", "missing-locator-workstream.toml", "cross-workstream-path.toml"):
            with self.subTest(name=name), self.assertRaises(ValidationError):
                validate_workstream(_read_toml(INVALID / name))

    def test_review_is_exact_subject_and_semantic_only(self) -> None:
        validate_review(_read_toml(VALID / "REVIEW_ATTEMPT.toml"))
        with self.assertRaisesRegex(ValidationError, "session"):
            validate_review(_read_toml(INVALID / "review-runtime-identity.toml"))
        with self.assertRaisesRegex(ValidationError, "not semantically independent"):
            validate_review(_read_toml(INVALID / "review-not-independent.toml"))

    def test_project_contract_is_common_v2_only(self) -> None:
        project = read_project(VALID / "PROJECT.md")
        validate_project(project)
        reject_prohibited_keys(project)


if __name__ == "__main__":
    unittest.main()
