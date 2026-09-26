#!/usr/bin/env python3
"""RF013 recovered-Execution contract regressions (H023/H024)."""

from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.execution_contract import (
    ExecutionContractError,
    is_accepted_success,
    parse_card_result,
)
from tools.router import select_route
from tools.state_contract import ValidationError, parse_task_card

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/router/valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"
RESULT = "implementation/workstreams/sample-workstream/results/M01-T04.md"
EVIDENCE = "implementation/workstreams/sample-workstream/evidence/M01-T04.md"

MINIMAL_CARD = (
    "# Fixture Card\n"
    "Exact current Card contract used only to prove progressive disclosure.\n"
)


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
        ["git", "-C", str(project), "config", "user.email", "rf013@example.invalid"],
        check=True,
    )
    subprocess.run(
        ["git", "-C", str(project), "config", "user.name", "RF013"], check=True
    )
    return temp, project


def card_content(*, review_requirement: str = "none") -> str:
    return (
        "# Fixture Card\n"
        "- Card ID: M01-T04\n"
        "- Included scope: prove recovered execution gates\n"
        "- Excluded scope: runtime-specific orchestration\n"
        "- Authority refs: requirements/REQUIREMENTS.md\n"
        "- Dependencies: none\n"
        "- Acceptance: route only after Card and accepted success are valid\n"
        "- Required tests/readback: rf013 regression\n"
        f"- Review requirement: {review_requirement}\n"
        "- Technical contract: none\n"
    )


def result_content(*, summary: str, status: str | None = "success") -> str:
    lines = (
        "# Card Result\n"
        "- Card ID: M01-T04\n"
        "- Implementation subject: owner/repo@commit:" + ("a" * 40) + "\n"
        f"- Evidence refs: {EVIDENCE}\n"
        f"- Tests/readback summary: {summary}\n"
    )
    if status is not None:
        lines += f"- Result status: {status}\n"
    return lines


def install_active_state(
    project: Path,
    *,
    card_text: str,
    result_text: str | None,
    commit_result: bool = True,
) -> None:
    (project / CARD).write_text(card_text)
    authority = project / "requirements/REQUIREMENTS.md"
    authority.parent.mkdir(parents=True, exist_ok=True)
    authority.write_text("# Accepted authority\n")
    evidence = project / EVIDENCE
    evidence.parent.mkdir(parents=True, exist_ok=True)
    evidence.write_text("# Verified evidence\n")
    if result_text is None:
        return
    target = project / RESULT
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(result_text)
    if commit_result:
        git(project, "add", "-A")
        git(project, "commit", "-qm", "rf013 result")
        commit = git(project, "rev-parse", "HEAD")
        blob = git(project, "rev-parse", f"HEAD:{RESULT}")
    else:
        commit, blob = "a" * 40, "b" * 40
    board = project / BOARD
    board.write_text(
        board.read_text()
        + '\n[cards.result]\nclass = "result"\n'
        + f'path = "{RESULT}"\ncommit = "{commit}"\nblob = "{blob}"\n'
    )


class AcceptedSuccessPredicateTests(unittest.TestCase):
    def test_exact_success_is_accepted(self) -> None:
        parsed = parse_card_result(
            result_content(summary="GREEN"), "M01-T04", "sample-workstream"
        )
        self.assertEqual(parsed["result_status"], "success")
        self.assertTrue(is_accepted_success(parsed))

    def test_missing_failed_and_blocked_are_not_accepted(self) -> None:
        legacy = parse_card_result(
            result_content(summary="GREEN", status=None),
            "M01-T04",
            "sample-workstream",
        )
        self.assertIsNone(legacy["result_status"])
        self.assertFalse(is_accepted_success(legacy))
        for status in ("failed", "blocked"):
            with self.subTest(status=status):
                parsed = parse_card_result(
                    result_content(summary="GREEN", status=status),
                    "M01-T04",
                    "sample-workstream",
                )
                self.assertFalse(is_accepted_success(parsed))

    def test_invalid_status_values_fail_closed(self) -> None:
        for status in ("GREEN", "Success", "successful", "success!", "none", "green"):
            with self.subTest(status=status):
                with self.assertRaisesRegex(ExecutionContractError, "invalid result status"):
                    parse_card_result(
                        result_content(summary="GREEN", status=status),
                        "M01-T04",
                        "sample-workstream",
                    )

    def test_summary_substring_never_authorizes(self) -> None:
        green_without_status = parse_card_result(
            result_content(
                summary="implementation and verification GREEN", status=None
            ),
            "M01-T04",
            "sample-workstream",
        )
        self.assertFalse(is_accepted_success(green_without_status))
        success_word_without_status = parse_card_result(
            result_content(summary="success achieved", status=None),
            "M01-T04",
            "sample-workstream",
        )
        self.assertFalse(is_accepted_success(success_word_without_status))
        failed_status_with_green_summary = parse_card_result(
            result_content(summary="GREEN", status="failed"),
            "M01-T04",
            "sample-workstream",
        )
        self.assertFalse(is_accepted_success(failed_status_with_green_summary))

    def test_success_with_failed_summary_is_not_accepted(self) -> None:
        for summary in (
            "FAILED: acceptance test failed",
            "failed: acceptance test failed",
            "  FAILED: acceptance test failed  ",
        ):
            with self.subTest(summary=summary):
                parsed = parse_card_result(
                    result_content(summary=summary, status="success"),
                    "M01-T04",
                    "sample-workstream",
                )
                self.assertFalse(is_accepted_success(parsed))

    def test_success_with_neutral_summary_still_accepted(self) -> None:
        for summary in ("GREEN", "implementation complete, see evidence"):
            with self.subTest(summary=summary):
                parsed = parse_card_result(
                    result_content(summary=summary, status="success"),
                    "M01-T04",
                    "sample-workstream",
                )
                self.assertTrue(is_accepted_success(parsed))

    def test_legacy_four_field_shape_still_parses_but_is_not_success(self) -> None:
        text = (
            "# Card Result\n"
            "- Card ID: M01-T04\n"
            "- Implementation subject: owner/repo@commit:" + ("a" * 40) + "\n"
            f"- Evidence refs: {EVIDENCE}\n"
            "- Tests/readback summary: implementation and verification GREEN\n"
        )
        parsed = parse_card_result(text, "M01-T04", "sample-workstream")
        self.assertEqual(parsed["card_id"], "M01-T04")
        self.assertFalse(is_accepted_success(parsed))


class H023FailedResultTests(unittest.TestCase):
    def assert_recovery(self, project: Path, fragment: str) -> None:
        routed = select_route(project, [MANIFEST], package_root=ROOT)
        self.assertEqual(
            (routed.disposition, routed.obligation),
            ("recovery", "recovery_boundary"),
            routed.reason,
        )
        self.assertIn(fragment, routed.reason)

    def test_failed_summary_without_success_cannot_reconcile(self) -> None:
        temp, project = fresh_git_project()
        try:
            install_active_state(
                project,
                card_text=card_content(review_requirement="none"),
                result_text=result_content(
                    summary="FAILED: acceptance test failed", status=None
                ),
            )
            self.assert_recovery(project, "not accepted success")
        finally:
            temp.cleanup()

    def test_failed_and_blocked_status_cannot_reconcile(self) -> None:
        for status in ("failed", "blocked"):
            temp, project = fresh_git_project()
            try:
                with self.subTest(status=status):
                    install_active_state(
                        project,
                        card_text=card_content(review_requirement="none"),
                        result_text=result_content(
                            summary="FAILED: acceptance test failed", status=status
                        ),
                    )
                    self.assert_recovery(project, "not accepted success")
            finally:
                temp.cleanup()

    def test_invalid_status_cannot_reconcile(self) -> None:
        temp, project = fresh_git_project()
        try:
            install_active_state(
                project,
                card_text=card_content(review_requirement="none"),
                result_text=result_content(summary="GREEN", status="GREEN"),
            )
            self.assert_recovery(project, "invalid result status")
        finally:
            temp.cleanup()

    def test_green_summary_without_status_cannot_reconcile(self) -> None:
        temp, project = fresh_git_project()
        try:
            install_active_state(
                project,
                card_text=card_content(review_requirement="none"),
                result_text=result_content(
                    summary="implementation and verification GREEN", status=None
                ),
            )
            self.assert_recovery(project, "not accepted success")
        finally:
            temp.cleanup()

    def test_review_freeze_requires_accepted_success(self) -> None:
        temp, project = fresh_git_project()
        try:
            install_active_state(
                project,
                card_text=card_content(review_requirement="required"),
                result_text=result_content(
                    summary="FAILED: acceptance test failed", status=None
                ),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
                routed.reason,
            )
            self.assertNotEqual(routed.obligation, "review_freeze")
        finally:
            temp.cleanup()

    def test_accepted_success_with_review_none_reconciles_without_replay(self) -> None:
        temp, project = fresh_git_project()
        try:
            install_active_state(
                project,
                card_text=card_content(review_requirement="none"),
                result_text=result_content(summary="GREEN", status="success"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "result_reconciliation"),
                routed.reason,
            )
            self.assertIn("do not replay", routed.reason)
            self.assertIn(f"project:{RESULT}", routed.read_set)
        finally:
            temp.cleanup()

    def test_accepted_success_with_review_required_freezes_review(self) -> None:
        temp, project = fresh_git_project()
        try:
            install_active_state(
                project,
                card_text=card_content(review_requirement="required"),
                result_text=result_content(summary="GREEN", status="success"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "review_freeze"),
                routed.reason,
            )
        finally:
            temp.cleanup()

    def test_contradictory_success_with_failed_summary_cannot_reconcile(self) -> None:
        temp, project = fresh_git_project()
        try:
            install_active_state(
                project,
                card_text=card_content(review_requirement="none"),
                result_text=result_content(
                    summary="FAILED: acceptance test failed", status="success"
                ),
            )
            self.assert_recovery(project, "not accepted success")
        finally:
            temp.cleanup()

    def test_contradictory_success_with_failed_summary_cannot_freeze_review(self) -> None:
        temp, project = fresh_git_project()
        try:
            install_active_state(
                project,
                card_text=card_content(review_requirement="required"),
                result_text=result_content(
                    summary="FAILED: acceptance test failed", status="success"
                ),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
                routed.reason,
            )
            self.assertNotEqual(routed.obligation, "review_freeze")
        finally:
            temp.cleanup()


class H024CardValidationTests(unittest.TestCase):
    def test_minimal_card_without_result_cannot_execute(self) -> None:
        with self.assertRaises(ValidationError):
            parse_task_card(MINIMAL_CARD, "M01-T04", "sample-workstream")
        temp, project = fresh_git_project()
        try:
            install_active_state(project, card_text=MINIMAL_CARD, result_text=None)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
                routed.reason,
            )
            self.assertIn("task_card", routed.reason)
        finally:
            temp.cleanup()

    def test_minimal_card_with_success_result_still_fails_closed(self) -> None:
        temp, project = fresh_git_project()
        try:
            install_active_state(
                project,
                card_text=MINIMAL_CARD,
                result_text=result_content(summary="GREEN", status="success"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
                routed.reason,
            )
            self.assertIn("task_card", routed.reason)
        finally:
            temp.cleanup()

    def test_card_missing_stable_field_cannot_execute(self) -> None:
        broken = card_content().replace("- Review requirement: none\n", "")
        with self.assertRaises(ValidationError):
            parse_task_card(broken, "M01-T04", "sample-workstream")
        temp, project = fresh_git_project()
        try:
            install_active_state(project, card_text=broken, result_text=None)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
                routed.reason,
            )
        finally:
            temp.cleanup()

    def test_valid_card_without_result_routes_execution(self) -> None:
        temp, project = fresh_git_project()
        try:
            install_active_state(
                project, card_text=card_content(), result_text=None
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation, routed.subject),
                ("route", "execution", "M01-T04"),
            )
        finally:
            temp.cleanup()


class RF007LocatorWithSuccessTests(unittest.TestCase):
    def test_dangling_result_identity_cannot_reconcile_with_success(self) -> None:
        temp, project = fresh_git_project()
        try:
            install_active_state(
                project,
                card_text=card_content(review_requirement="none"),
                result_text=result_content(summary="GREEN", status="success"),
                commit_result=False,
            )
            git(project, "add", "-A")
            git(project, "commit", "-qm", "dangling")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
                routed.reason,
            )
        finally:
            temp.cleanup()

    def test_mutated_result_bytes_cannot_reconcile_with_success(self) -> None:
        temp, project = fresh_git_project()
        try:
            install_active_state(
                project,
                card_text=card_content(review_requirement="none"),
                result_text=result_content(summary="GREEN", status="success"),
            )
            (project / RESULT).write_text(
                result_content(summary="mutated bytes", status="success")
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
                routed.reason,
            )
        finally:
            temp.cleanup()

    def test_backslash_evidence_alias_cannot_reconcile_with_success(self) -> None:
        temp, project = fresh_git_project()
        try:
            evil = "implementation/workstreams/sample-workstream/evidence/sub\\..\\evil.md"
            (project / CARD).write_text(card_content(review_requirement="none"))
            authority = project / "requirements/REQUIREMENTS.md"
            authority.parent.mkdir(parents=True, exist_ok=True)
            authority.write_text("# Accepted authority\n")
            target = project / RESULT
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                "# Card Result\n"
                "- Card ID: M01-T04\n"
                "- Implementation subject: owner/repo@commit:" + ("a" * 40) + "\n"
                f"- Evidence refs: {evil}\n"
                "- Tests/readback summary: GREEN\n"
                "- Result status: success\n"
            )
            git(project, "add", "-A")
            git(project, "commit", "-qm", "evil evidence")
            commit = git(project, "rev-parse", "HEAD")
            blob = git(project, "rev-parse", f"HEAD:{RESULT}")
            board = project / BOARD
            board.write_text(
                board.read_text()
                + '\n[cards.result]\nclass = "result"\n'
                + f'path = "{RESULT}"\ncommit = "{commit}"\nblob = "{blob}"\n'
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
                routed.reason,
            )
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
