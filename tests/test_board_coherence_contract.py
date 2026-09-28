from __future__ import annotations

import copy
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.router import select_route
from tools.state_contract import ValidationError, read_toml, validate_board

ROOT = Path(__file__).resolve().parents[1]
STATE_VALID = ROOT / "tests" / "fixtures" / "state" / "valid"
ROUTER_FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"


def task_card_content(*, review_requirement: str = "required") -> str:
    return (
        "# Fixture Card\n"
        "- Card ID: M01-T04\n"
        "- Included scope: prove launch readiness\n"
        "- Excluded scope: runtime-specific orchestration\n"
        "- Authority refs: requirements/REQUIREMENTS.md\n"
        "- Dependencies: none\n"
        "- Acceptance: route only after current launch inputs are valid\n"
        "- Required tests/readback: production router fixture\n"
        f"- Review requirement: {review_requirement}\n"
        "- Technical contract: none\n"
    )


def result_content(*, card_id: str = "M01-T04", status: str = "success",
                   summary: str = "GREEN") -> str:
    return (
        "# Card Result\n"
        f"- Card ID: {card_id}\n"
        "- Implementation subject: owner/repo@commit:" + ("a" * 40) + "\n"
        "- Evidence refs: implementation/workstreams/sample-workstream/evidence/M01-T04.md\n"
        f"- Tests/readback summary: {summary}\n"
        f"- Result status: {status}\n"
    )


class BoardCoherenceValidatorTests(unittest.TestCase):
    """RF001 status/result/review/blocker coherence in the shared validator."""

    def setUp(self) -> None:
        self.workstream = read_toml(STATE_VALID / "WORKSTREAM.toml")

    def base_board(self) -> dict:
        board = read_toml(STATE_VALID / "TASK_BOARD.toml")
        # Normalize to a single in_progress Card without bindings.
        board["cards"] = [copy.deepcopy(board["cards"][1])]
        return board

    def test_premature_result_fails_for_planned_ready(self) -> None:
        for status in ("planned", "ready"):
            board = self.base_board()
            board["cards"][0]["status"] = status
            board["cards"][0]["result"] = {
                "class": "result",
                "path": "implementation/workstreams/sample-workstream/results/M01-T02.md",
            }
            with self.subTest(status=status):
                with self.assertRaisesRegex(ValidationError, "premature"):
                    validate_board(board, self.workstream)

    def test_blocked_may_preserve_result_from_prior_execution(self) -> None:
        board = self.base_board()
        board["cards"][0]["status"] = "blocked"
        board["cards"][0]["result"] = {
            "class": "result",
            "path": "implementation/workstreams/sample-workstream/results/M01-T02.md",
        }
        board["cards"][0]["blocker"] = {
            "class": "blocker",
            "path": "implementation/workstreams/sample-workstream/blockers/M01-T02.toml",
        }
        validate_board(board, self.workstream)

    def test_blocker_allowed_only_on_blocked_and_in_progress(self) -> None:
        blocker = {
            "class": "blocker",
            "path": "implementation/workstreams/sample-workstream/blockers/M01-T02.toml",
        }
        for status, allowed in (
            ("planned", False), ("ready", False), ("in_progress", True),
            ("blocked", True), ("done", False), ("returned", False),
        ):
            board = self.base_board()
            board["cards"][0]["status"] = status
            board["cards"][0]["blocker"] = copy.deepcopy(blocker)
            if status == "done":
                board["cards"][0]["result"] = {
                    "class": "result",
                    "path": "implementation/workstreams/sample-workstream/results/M01-T02.md",
                }
            with self.subTest(status=status):
                if allowed:
                    validate_board(board, self.workstream)
                else:
                    with self.assertRaisesRegex(ValidationError, "blocker"):
                        validate_board(board, self.workstream)

    def test_dangling_review_history_fails_closed(self) -> None:
        attempt = {
            "class": "review_attempt",
            "path": "implementation/workstreams/sample-workstream/reviews/M01-T02-R01.toml",
        }
        for status in ("planned", "ready"):
            board = self.base_board()
            board["cards"][0]["status"] = status
            board["cards"][0]["review_attempts"] = [copy.deepcopy(attempt)]
            with self.subTest(status=status):
                with self.assertRaisesRegex(ValidationError, "review"):
                    validate_board(board, self.workstream)
        board = self.base_board()
        board["cards"][0]["review_attempts"] = [copy.deepcopy(attempt)]
        with self.assertRaisesRegex(ValidationError, "dangling"):
            validate_board(board, self.workstream)

    def test_coherence_positives_stay_valid(self) -> None:
        board = self.base_board()
        validate_board(board, self.workstream)
        board["cards"][0]["status"] = "ready"
        validate_board(board, self.workstream)
        board["cards"][0]["status"] = "blocked"
        board["cards"][0]["blocker"] = {
            "class": "blocker",
            "path": "implementation/workstreams/sample-workstream/blockers/M01-T02.toml",
        }
        validate_board(board, self.workstream)
        board["cards"][0]["status"] = "in_progress"
        validate_board(board, self.workstream)
        board = read_toml(STATE_VALID / "TASK_BOARD.toml")
        validate_board(board, self.workstream)


class BoardCoherenceRouterTests(unittest.TestCase):
    """RF001 blocker/result/review-first routing in the production selector."""

    def copy_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(ROUTER_FIXTURE, project)
        return temp, project

    @staticmethod
    def git_identity_for(project: Path, relpath: str) -> tuple[str, str]:
        if not (project / ".git").exists():
            subprocess.run(["git", "init", "-q", str(project)], check=True)
            subprocess.run(["git", "-C", str(project), "config", "user.email",
                            "fixture@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(project), "config", "user.name",
                            "Fixture"], check=True)
        subprocess.run(["git", "-C", str(project), "add", relpath], check=True)
        subprocess.run(["git", "-C", str(project), "commit", "-q", "-m",
                        f"fixture {relpath}"], check=True)
        commit = subprocess.run(
            ["git", "-C", str(project), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True).stdout.strip()
        blob = subprocess.run(
            ["git", "-C", str(project), "rev-parse", f"HEAD:{relpath}"],
            check=True, capture_output=True, text=True).stdout.strip()
        return commit, blob

    def install_result(self, project: Path, review: str = "required",
                       content: str | None = None) -> tuple[str, str, str]:
        result_path = "implementation/workstreams/sample-workstream/results/M01-T04.md"
        (project / CARD).write_text(task_card_content(review_requirement=review))
        authority = project / "requirements" / "REQUIREMENTS.md"
        authority.parent.mkdir(parents=True, exist_ok=True)
        authority.write_text("# Accepted authority\n")
        evidence = project / "implementation/workstreams/sample-workstream/evidence"
        evidence.mkdir(parents=True, exist_ok=True)
        (evidence / "M01-T04.md").write_text("# Verified evidence\n")
        target = project / result_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content or result_content())
        commit, blob = self.git_identity_for(project, result_path)
        board = project / BOARD
        board.write_text(
            board.read_text()
            + '\n[cards.result]\nclass = "result"\n'
            + f'path = "{result_path}"\ncommit = "{commit}"\nblob = "{blob}"\n')
        return result_path, commit, blob

    def install_blocker(self, project: Path, blocker_class: str,
                        status: str = "blocked") -> None:
        blocker_path = "implementation/workstreams/sample-workstream/blockers/M01-T04.toml"
        board = project / BOARD
        board.write_text(
            board.read_text()
            .replace('status = "in_progress"', f'status = "{status}"', 1)
            .replace('[cards.contract]\n',
                     f'[cards.blocker]\nclass = "blocker"\npath = "{blocker_path}"\n\n'
                     '[cards.contract]\n', 1))
        path = project / blocker_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            'workstream_id = "sample-workstream"\ncard_id = "M01-T04"\n'
            f'class = "{blocker_class}"\nsummary = "Exact blocker."\nevidence_path = ""\n')

    def card_acceptance_identity(self, project: Path) -> tuple[str, str]:
        try:
            in_head = subprocess.run(
                ["git", "-C", str(project), "rev-parse", "--verify", f"HEAD:{CARD}"],
                capture_output=True, text=True, check=False)
            matches = in_head.returncode == 0 and subprocess.run(
                ["git", "-C", str(project), "diff", "--quiet", "HEAD", "--", CARD],
                capture_output=True, check=False).returncode == 0
        except (OSError, subprocess.SubprocessError):
            matches = False
        if not matches:
            self.git_identity_for(project, CARD)
        commit = subprocess.run(
            ["git", "-C", str(project), "log", "--format=%H", "-1", "HEAD", "--", CARD],
            check=True, capture_output=True, text=True).stdout.strip()
        blob = subprocess.run(
            ["git", "-C", str(project), "rev-parse", f"{commit}:{CARD}"],
            check=True, capture_output=True, text=True).stdout.strip()
        return commit, blob

    def board_result_identity(self, project: Path) -> tuple[str, str]:
        section = (project / BOARD).read_text().split("[cards.result]", 1)[1]
        commit = re.search(r'commit = "([0-9a-f]{40})"', section).group(1)  # type: ignore[union-attr]
        blob = re.search(r'blob = "([0-9a-f]{40})"', section).group(1)  # type: ignore[union-attr]
        return commit, blob

    def add_review_attempt(self, project: Path, verdict: str, attempt: str = "R01",
                           *, subject_commit: str | None = None,
                           subject_blob: str | None = None,
                           acceptance_path: str = CARD,
                           omit_acceptance_identity: bool = False,
                           independent: bool = True,
                           finding_ids: tuple[str, ...] = (),
                           defect_class_ids: tuple[str, ...] = ()) -> str:
        review_path = f"implementation/workstreams/sample-workstream/reviews/M01-T04-{attempt}.toml"
        path = project / review_path
        path.parent.mkdir(parents=True, exist_ok=True)
        evidence = "" if verdict in {"pending", "in_progress"} else \
            f"implementation/workstreams/sample-workstream/evidence/review-{attempt}.md"
        if evidence:
            target = project / evidence
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("# Review evidence\n")
        board_commit, board_blob = self.board_result_identity(project)
        real_commit, real_blob = self.card_acceptance_identity(project)
        stanza = ('[acceptance]\nclass = "task_card"\n' f'path = "{acceptance_path}"\n')
        if not omit_acceptance_identity:
            stanza += f'commit = "{real_commit}"\nblob = "{real_blob}"\n'
        if verdict == "red" and not finding_ids:
            finding_ids = ("F1",)
        if verdict == "red" and not defect_class_ids:
            defect_class_ids = ("class-a",)
        findings = ", ".join(f'"{item}"' for item in finding_ids)
        classes = ", ".join(f'"{item}"' for item in defect_class_ids)
        severity = ""
        if verdict == "red":
            for finding_id in finding_ids:
                severity += ('[[finding_severity]]\n' f'id = "{finding_id}"\n'
                             'surface = "correctness"\n'
                             f'evidence = "{evidence}#{finding_id}"\n')
        path.write_text(
            'workstream_id = "sample-workstream"\ncard_id = "M01-T04"\n'
            f'attempt = "{attempt}"\nverdict = "{verdict}"\nevidence_path = "{evidence}"\n'
            'review_kind = "discovery"\nsource_discovery_attempt = ""\n'
            f'discovery_complete = {"true" if verdict != "pending" else "false"}\n'
            f'material_finding_ids = [{findings}]\n'
            'review_scope = "card"\nreview_epoch = "E01"\nepoch_reset_basis = ""\n'
            f'material_defect_class_ids = [{classes}]\nfailed_material_defect_class_ids = []\n'
            'post_convergence_validation = false\nconvergence_basis = ""\n'
            '[subject]\nclass = "git_blob"\nrepository = "owner/router-fixture"\n'
            f'commit = "{subject_commit or board_commit}"\n'
            'path = "implementation/workstreams/sample-workstream/results/M01-T04.md"\n'
            f'blob = "{subject_blob or board_blob}"\n' + stanza
            + '[independence]\n'
            f'materially_produced_or_repaired_subject = {"false" if independent else "true"}\n'
            'basis = "Fresh semantic reviewer context."\n' + severity)
        attempt_commit, attempt_blob = self.git_identity_for(project, review_path)
        locator = (f'{{ class = "review_attempt", path = "{review_path}", '
                   f'commit = "{attempt_commit}", blob = "{attempt_blob}" }}')
        board = project / BOARD
        text = board.read_text()
        if "review_attempts = [" in text:
            text = re.sub(r"review_attempts = \[(.*?)\]",
                          lambda m: f"review_attempts = [{m.group(1)}, {locator}]",
                          text, count=1, flags=re.DOTALL)
        else:
            text = text.replace('status = "in_progress"\n',
                                'status = "in_progress"\n' f"review_attempts = [{locator}]\n", 1)
        board.write_text(text)
        return review_path

    def flip_status(self, project: Path, old: str, new: str) -> None:
        board = project / BOARD
        board.write_text(board.read_text().replace(f'status = "{old}"', f'status = "{new}"', 1))

    def test_h001_in_progress_blocker_routes_to_exact_owner(self) -> None:
        for blocker_class, disposition, obligation in (
                ("missing_evidence", "route", "research_handoff"),
                ("human_authority", "stop", "user_stop"),
                ("runtime_access_input", "stop", "blocker_stop")):
            temp, project = self.copy_fixture()
            try:
                self.install_blocker(project, blocker_class, status="in_progress")
                routed = select_route(project, [MANIFEST], package_root=ROOT)
                with self.subTest(blocker=blocker_class):
                    self.assertEqual((routed.disposition, routed.obligation),
                                     (disposition, obligation))
                    self.assertEqual(routed.subject, "M01-T04")
            finally:
                temp.cleanup()

    def test_h001_in_progress_blocker_wins_over_result(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_result(project, "required")
            self.install_blocker(project, "human_authority", status="in_progress")
            # install_blocker rewrote in_progress already carrying a result; the
            # blocker locator is added while the result stanza is preserved.
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("stop", "user_stop"))
        finally:
            temp.cleanup()

    def test_h004_done_without_review_routes_review_never_close(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_result(project, "required")
            self.flip_status(project, "in_progress", "done")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "review_freeze"))
            self.assertEqual(routed.subject, "M01-T04")
        finally:
            temp.cleanup()

    def test_h004_done_pending_and_red_route_review_never_close(self) -> None:
        for verdict, obligation in (("pending", "review"), ("red", "execution_resolution")):
            temp, project = self.copy_fixture()
            try:
                self.install_result(project, "required")
                self.add_review_attempt(project, verdict)
                self.flip_status(project, "in_progress", "done")
                routed = select_route(project, [MANIFEST], package_root=ROOT)
                with self.subTest(verdict=verdict):
                    self.assertEqual((routed.disposition, routed.obligation),
                                     ("route", obligation))
            finally:
                temp.cleanup()

    def test_h004_done_green_bound_review_closes(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_result(project, "required")
            self.add_review_attempt(project, "green")
            self.flip_status(project, "in_progress", "done")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "close"))
        finally:
            temp.cleanup()

    def test_h004_done_review_free_positive_closes_without_review(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_result(project, "none")
            self.flip_status(project, "in_progress", "done")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "close"))
        finally:
            temp.cleanup()

    def test_h004_done_review_free_path_only_result_cannot_close(self) -> None:
        temp, project = self.copy_fixture()
        try:
            result_path, commit, blob = self.install_result(project, "none")
            board = project / BOARD
            text = board.read_text()
            text = text.replace(
                f'commit = "{commit}"\nblob = "{blob}"\n', ""
            )
            self.assertNotIn(f'commit = "{commit}"', text)
            board.write_text(text)
            self.flip_status(project, "in_progress", "done")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation),
                             ("recovery", "recovery_boundary"))
            self.assertIn("exact result locator", routed.reason)
        finally:
            temp.cleanup()

    def test_h004_done_dangling_stale_sibling_result_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            result_path, commit, blob = self.install_result(project, "required")
            board = project / BOARD
            board.write_text(board.read_text().replace(commit, "f" * 40).replace(blob, "e" * 40))
            (project / result_path).write_text("# changed\n")
            self.flip_status(project, "in_progress", "done")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation),
                             ("recovery", "recovery_boundary"))
            self.assertIn("dangling", routed.reason)
        finally:
            temp.cleanup()
        temp, project = self.copy_fixture()
        try:
            result_path, _, _ = self.install_result(project, "required")
            (project / result_path).write_text(result_content(summary="MUTATED"))
            self.flip_status(project, "in_progress", "done")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation),
                             ("recovery", "recovery_boundary"))
            self.assertIn("stale", routed.reason)
        finally:
            temp.cleanup()
        temp, project = self.copy_fixture()
        try:
            self.install_result(project, "required",
                                content=result_content(card_id="M01-T99"))
            self.flip_status(project, "in_progress", "done")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation),
                             ("recovery", "recovery_boundary"))
            self.assertIn("M01-T04", routed.reason)
        finally:
            temp.cleanup()

    def test_h004_done_unbound_and_non_green_review_never_close(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_result(project, "required")
            self.add_review_attempt(project, "green", subject_blob="f" * 40)
            self.flip_status(project, "in_progress", "done")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "review_freeze"))
        finally:
            temp.cleanup()
        temp, project = self.copy_fixture()
        try:
            self.install_result(project, "required")
            self.add_review_attempt(
                project, "green",
                acceptance_path="implementation/workstreams/sample-workstream/cards/M01-T99.md")
            self.flip_status(project, "in_progress", "done")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertNotEqual((routed.disposition, routed.obligation), ("route", "close"))
        finally:
            temp.cleanup()
        temp, project = self.copy_fixture()
        try:
            self.install_result(project, "required")
            self.add_review_attempt(project, "green", independent=False)
            self.flip_status(project, "in_progress", "done")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation),
                             ("recovery", "recovery_boundary"))
        finally:
            temp.cleanup()

    def test_h004_done_path_only_review_fails_closed_without_rewrite(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_result(project, "required")
            review_path = self.add_review_attempt(project, "green")
            board = project / BOARD
            text = board.read_text()
            text = re.sub(
                r'\{ class = "review_attempt", path = "' + re.escape(review_path) +
                r'", commit = "[0-9a-f]{40}", blob = "[0-9a-f]{40}" \}',
                f'{{ class = "review_attempt", path = "{review_path}" }}', text, count=1)
            board.write_text(text)
            before = (project / review_path).read_bytes()
            self.flip_status(project, "in_progress", "done")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation),
                             ("recovery", "recovery_boundary"))
            self.assertIn("path-only", routed.reason)
            self.assertEqual((project / review_path).read_bytes(), before)
        finally:
            temp.cleanup()

    def test_h025_premature_result_never_launches_or_dispatches(self) -> None:
        for status in ("ready", "planned"):
            temp, project = self.copy_fixture()
            try:
                self.install_result(project, "none")
                self.flip_status(project, "in_progress", status)
                routed = select_route(project, [MANIFEST], package_root=ROOT)
                with self.subTest(status=status):
                    self.assertEqual((routed.disposition, routed.obligation),
                                     ("recovery", "recovery_boundary"))
                    self.assertIn("premature", routed.reason)
            finally:
                temp.cleanup()

    def test_h025_blocked_preserved_result_reaches_owner_dangling_fails(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_result(project, "none")
            board = project / BOARD
            text = board.read_text().replace('status = "in_progress"', 'status = "blocked"', 1)
            text = text.replace('[cards.contract]\n',
                                '[cards.blocker]\nclass = "blocker"\n'
                                'path = "implementation/workstreams/sample-workstream/blockers/M01-T04.toml"\n\n'
                                '[cards.contract]\n', 1)
            board.write_text(text)
            blocker = project / "implementation/workstreams/sample-workstream/blockers/M01-T04.toml"
            blocker.parent.mkdir(parents=True, exist_ok=True)
            blocker.write_text('workstream_id = "sample-workstream"\ncard_id = "M01-T04"\n'
                               'class = "missing_evidence"\nsummary = "Exact blocker."\n'
                               'evidence_path = ""\n')
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation),
                             ("route", "research_handoff"))
        finally:
            temp.cleanup()
        temp, project = self.copy_fixture()
        try:
            result_path, commit, blob = self.install_result(project, "none")
            board = project / BOARD
            text = board.read_text().replace('status = "in_progress"', 'status = "blocked"', 1)
            text = text.replace('[cards.contract]\n',
                                '[cards.blocker]\nclass = "blocker"\n'
                                'path = "implementation/workstreams/sample-workstream/blockers/M01-T04.toml"\n\n'
                                '[cards.contract]\n', 1)
            text = text.replace(commit, "f" * 40).replace(blob, "e" * 40)
            board.write_text(text)
            (project / result_path).write_text("# changed\n")
            blocker = project / "implementation/workstreams/sample-workstream/blockers/M01-T04.toml"
            blocker.parent.mkdir(parents=True, exist_ok=True)
            blocker.write_text('workstream_id = "sample-workstream"\ncard_id = "M01-T04"\n'
                               'class = "missing_evidence"\nsummary = "Exact blocker."\n'
                               'evidence_path = ""\n')
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation),
                             ("recovery", "recovery_boundary"))
            self.assertIn("dangling", routed.reason)
        finally:
            temp.cleanup()

    def test_h025_blocked_without_result_still_reaches_exact_owner(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_blocker(project, "missing_evidence", status="blocked")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation),
                             ("route", "research_handoff"))
        finally:
            temp.cleanup()

    def test_positives_in_progress_no_blocker_and_ready_no_result(self) -> None:
        temp, project = self.copy_fixture()
        try:
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
        finally:
            temp.cleanup()
        temp, project = self.copy_fixture()
        try:
            board = project / BOARD
            board.write_text(board.read_text().replace('status = "in_progress"',
                                                       'status = "ready"', 1))
            (project / CARD).write_text(task_card_content(review_requirement="none"))
            authority = project / "requirements" / "REQUIREMENTS.md"
            authority.parent.mkdir(parents=True, exist_ok=True)
            authority.write_text("# Accepted authority\n")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation),
                             ("route", "execution_prep"))
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
