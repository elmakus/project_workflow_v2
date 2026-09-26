"""RF006 review-attempt identity and legacy provenance (H008/H009).

H008: newly authored legacy-shaped attempts cannot be accepted as historical
from file shape alone; explicit uniquely derived migration provenance bound
to the exact immutable source attempt and source Git/workstream state allows
a valid historical attempt to remain inspectable without changing its
terminal verdict, while ambiguous provenance routes Recovery.

H009: same-ID RED-to-GREEN byte rewrite and bogus attempt commit/blob cannot
validate or route as stable review history. New/current exact attempt
identities and append-only attempts continue deterministically.

H018 Close completeness is out of scope for this Card.
"""

from __future__ import annotations

import copy
import re
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path

from tools.review_attempt_provenance import (
    ReviewAttemptProvenanceError,
    validate_legacy_migration_shape,
    validate_review_attempt_locator_shape,
    verify_history_append_only,
    verify_legacy_migration,
    verify_review_attempt_locator,
    verify_terminal_append_only_from_git,
)
from tools.router import select_route
from tools.state_contract import (
    ValidationError,
    read_toml,
    validate_review,
    validate_review_history,
)

ROOT = Path(__file__).resolve().parents[1]
VALID = ROOT / "tests" / "fixtures" / "state" / "valid"
FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"
REPOSITORY = "owner/router-fixture"


def _legacy_attempt(
    workstream_id: str = "sample-workstream",
    card_id: str = "M01-T01",
    attempt_id: str = "R01",
    verdict: str = "red",
) -> dict:
    base = read_toml(VALID / "REVIEW_ATTEMPT.toml")
    attempt = copy.deepcopy(base)
    attempt.update({
        "workstream_id": workstream_id,
        "card_id": card_id,
        "attempt": attempt_id,
        "verdict": verdict,
    })
    attempt.pop("review_kind", None)
    return attempt


def _provenance(
    workstream_id: str, card_id: str, attempt_id: str,
    commit: str | None = None, blob: str | None = None,
) -> dict[str, str]:
    return {
        "source_repository": "owner/fixture-project",
        "source_commit": commit or "a" * 40,
        "source_path": (
            f"implementation/workstreams/{workstream_id}/reviews/{card_id}-{attempt_id}.toml"
        ),
        "source_blob": blob or "b" * 40,
        "source_workstream": workstream_id,
        "source_card": card_id,
        "source_attempt": attempt_id,
    }


def _explicit_attempt(
    workstream_id: str = "sample-workstream",
    card_id: str = "M01-T01",
    attempt_id: str = "R02",
    verdict: str = "pending",
) -> dict:
    attempt = _legacy_attempt(workstream_id, card_id, attempt_id, "green")
    attempt.update({
        "attempt": attempt_id,
        "verdict": verdict,
        "evidence_path": "" if verdict in {"pending", "in_progress"} else attempt["evidence_path"],
        "review_kind": "discovery",
        "source_discovery_attempt": "",
        "discovery_complete": verdict in {"green", "red"},
        "material_finding_ids": [],
        "review_scope": "card",
        "review_epoch": "E01",
        "epoch_reset_basis": "",
        "material_defect_class_ids": [],
        "post_convergence_validation": False,
        "convergence_basis": "",
    })
    if verdict == "red":
        attempt.update({
            "material_finding_ids": ["F1"],
            "finding_severity": [
                {"id": "F1", "surface": "correctness", "evidence": "evidence/review-R01.md#F1"}
            ],
            "material_defect_class_ids": ["class-a"],
        })
    return attempt


class LegacyShapeTests(unittest.TestCase):
    def test_newly_authored_legacy_without_provenance_fails_history(self) -> None:
        legacy = _legacy_attempt(verdict="red")
        validate_review(legacy)
        with self.assertRaisesRegex(ValidationError, "explicit migration provenance"):
            validate_review_history([legacy])

    def test_legacy_with_valid_shape_passes_prefix(self) -> None:
        legacy = _legacy_attempt(verdict="red")
        legacy["legacy_migration"] = _provenance("sample-workstream", "M01-T01", "R01")
        validate_review(legacy)
        explicit = _explicit_attempt(attempt_id="R02", verdict="pending")
        validate_review_history([legacy, explicit])

    def test_legacy_provenance_must_match_exact_current_identity(self) -> None:
        legacy = _legacy_attempt(verdict="green")
        bad = _provenance("sample-workstream", "M01-T01", "R01")
        bad["source_workstream"] = "sibling-workstream"
        legacy["legacy_migration"] = bad
        with self.assertRaisesRegex(ValidationError, "source_workstream"):
            validate_review(legacy)

    def test_explicit_attempt_must_not_claim_legacy_provenance(self) -> None:
        explicit = _explicit_attempt(verdict="pending")
        explicit["legacy_migration"] = _provenance("sample-workstream", "M01-T01", "R02")
        with self.assertRaisesRegex(ValidationError, "must not claim legacy"):
            validate_review(explicit)
        with self.assertRaisesRegex(ValidationError, "must not claim legacy"):
            validate_review_history([explicit])

    def test_legacy_provenance_rejects_malformed_git_identity(self) -> None:
        with self.assertRaisesRegex(ReviewAttemptProvenanceError, "40-hex"):
            validate_legacy_migration_shape(
                {
                    "source_repository": "owner/fixture-project",
                    "source_commit": "short",
                    "source_path": "implementation/workstreams/sample-workstream/reviews/M01-T01-R01.toml",
                    "source_blob": "b" * 40,
                    "source_workstream": "sample-workstream",
                    "source_card": "M01-T01",
                    "source_attempt": "R01",
                },
                workstream_id="sample-workstream",
                card_id="M01-T01",
                attempt_id="R01",
            )


class LocatorShapeTests(unittest.TestCase):
    def test_path_only_locator_stays_shape_valid_for_terminal_preservation(self) -> None:
        shape = validate_review_attempt_locator_shape(
            {"class": "review_attempt", "path": "implementation/workstreams/sample-workstream/reviews/M01-T01-R01.toml"},
            "sample-workstream",
            "review_attempts[0]",
        )
        self.assertIsNone(shape["commit"])
        self.assertIsNone(shape["blob"])

    def test_exact_locator_requires_commit_and_blob_together(self) -> None:
        with self.assertRaisesRegex(ReviewAttemptProvenanceError, "commit \\+ blob"):
            validate_review_attempt_locator_shape(
                {
                    "class": "review_attempt",
                    "path": "implementation/workstreams/sample-workstream/reviews/M01-T01-R01.toml",
                    "commit": "a" * 40,
                },
                "sample-workstream",
                "review_attempts[0]",
            )

    def test_bogus_locator_keys_fail_closed(self) -> None:
        with self.assertRaisesRegex(ReviewAttemptProvenanceError, "unknown field"):
            validate_review_attempt_locator_shape(
                {
                    "class": "review_attempt",
                    "path": "implementation/workstreams/sample-workstream/reviews/M01-T01-R01.toml",
                    "commit": "a" * 40,
                    "blob": "b" * 40,
                    "bogus": "ignored-before-rf006",
                },
                "sample-workstream",
                "review_attempts[0]",
            )

    def test_malformed_commit_blob_fail_shape(self) -> None:
        with self.assertRaisesRegex(ReviewAttemptProvenanceError, "40-hex"):
            validate_review_attempt_locator_shape(
                {
                    "class": "review_attempt",
                    "path": "implementation/workstreams/sample-workstream/reviews/M01-T01-R01.toml",
                    "commit": "not-hex",
                    "blob": "b" * 40,
                },
                "sample-workstream",
                "review_attempts[0]",
            )


class AppendOnlyTests(unittest.TestCase):
    def test_same_id_red_to_green_rewrite_fails_with_prior(self) -> None:
        prior = _explicit_attempt(attempt_id="R01", verdict="red")
        rewritten = copy.deepcopy(prior)
        rewritten["verdict"] = "green"
        rewritten["material_finding_ids"] = []
        rewritten["material_defect_class_ids"] = []
        rewritten.pop("finding_severity", None)
        rewritten["discovery_complete"] = True
        with self.assertRaisesRegex(ReviewAttemptProvenanceError, "silently rewritten"):
            verify_history_append_only([prior], [rewritten])
        with self.assertRaisesRegex(ValidationError, "silently rewritten"):
            validate_review_history([rewritten], prior_attempts=[prior])

    def test_append_only_extension_passes(self) -> None:
        first = _explicit_attempt(attempt_id="R01", verdict="red")
        # Close R01 findings before fresh R02 discovery.
        closure = copy.deepcopy(first)
        closure.update({
            "attempt": "R02",
            "review_kind": "closure_verification",
            "source_discovery_attempt": "R01",
            "discovery_complete": False,
            "verdict": "green",
        })
        closure["subject"]["blob"] = "4" * 40
        validate_review_history([first, closure])
        verify_history_append_only([first], [first, closure])

    def test_missing_prior_attempt_fails(self) -> None:
        first = _explicit_attempt(attempt_id="R01", verdict="red")
        closure = copy.deepcopy(first)
        closure.update({
            "attempt": "R02",
            "review_kind": "closure_verification",
            "source_discovery_attempt": "R01",
            "discovery_complete": False,
            "verdict": "green",
        })
        with self.assertRaisesRegex(ReviewAttemptProvenanceError, "missing from current"):
            verify_history_append_only([first, closure], [closure])


class RouterProvenanceTests(unittest.TestCase):
    def copy_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(FIXTURE, project)
        return temp, project

    @staticmethod
    def git_identity_for(project: Path, relpath: str) -> tuple[str, str]:
        if not (project / ".git").exists():
            subprocess.run(["git", "init", "-q", str(project)], check=True)
            subprocess.run(["git", "-C", str(project), "config", "user.email", "fixture@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(project), "config", "user.name", "Fixture"], check=True)
        subprocess.run(["git", "-C", str(project), "add", relpath], check=True)
        subprocess.run(["git", "-C", str(project), "commit", "-q", "-m", f"fixture {relpath}"], check=True)
        commit = subprocess.run(
            ["git", "-C", str(project), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        blob = subprocess.run(
            ["git", "-C", str(project), "rev-parse", f"HEAD:{relpath}"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        return commit, blob

    def task_card_content(self, review_requirement: str = "required") -> str:
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

    def install_reviewable_result(self, project: Path) -> str:
        result_path = "implementation/workstreams/sample-workstream/results/M01-T04.md"
        (project / CARD).write_text(self.task_card_content())
        authority = project / "requirements" / "REQUIREMENTS.md"
        authority.parent.mkdir(parents=True, exist_ok=True)
        authority.write_text("# Accepted authority\n")
        evidence_dir = project / "implementation/workstreams/sample-workstream/evidence"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        (evidence_dir / "M01-T04.md").write_text("# Verified evidence\n")
        result_file = project / result_path
        result_file.parent.mkdir(parents=True, exist_ok=True)
        result_file.write_text(
            "# Fixture Result\n"
            "- Card ID: M01-T04\n"
            "- Implementation subject: owner/repo@commit:" + "a" * 40 + "\n"
            "- Evidence refs: implementation/workstreams/sample-workstream/evidence/M01-T04.md\n"
            "- Tests/readback summary: GREEN\n"
            "- Result status: success\n"
        )
        commit, blob = self.git_identity_for(project, result_path)
        board = project / BOARD
        board.write_text(
            board.read_text()
            + '\n[cards.result]\nclass = "result"\n'
            + f'path = "{result_path}"\n'
            + f'commit = "{commit}"\n'
            + f'blob = "{blob}"\n'
        )
        return result_path

    def board_result_identity(self, project: Path) -> tuple[str, str]:
        section = (project / BOARD).read_text().split("[cards.result]", 1)[1]
        commit = re.search(r'commit = "([0-9a-f]{40})"', section).group(1)  # type: ignore[union-attr]
        blob = re.search(r'blob = "([0-9a-f]{40})"', section).group(1)  # type: ignore[union-attr]
        return commit, blob

    def write_legacy_file(
        self, project: Path, review_path: str, verdict: str,
        commit: str, blob: str, provenance: dict[str, str] | None,
    ) -> None:
        path = project / review_path
        path.parent.mkdir(parents=True, exist_ok=True)
        evidence = f"implementation/workstreams/sample-workstream/evidence/review-R01.md"
        evidence_file = project / evidence
        evidence_file.parent.mkdir(parents=True, exist_ok=True)
        evidence_file.write_text("# Review evidence\n")
        provenance_stanza = ""
        if provenance is not None:
            provenance_stanza = (
                "[legacy_migration]\n"
                f'source_repository = "{provenance["source_repository"]}"\n'
                f'source_commit = "{provenance["source_commit"]}"\n'
                f'source_path = "{provenance["source_path"]}"\n'
                f'source_blob = "{provenance["source_blob"]}"\n'
                f'source_workstream = "{provenance["source_workstream"]}"\n'
                f'source_card = "{provenance["source_card"]}"\n'
                f'source_attempt = "{provenance["source_attempt"]}"\n'
            )
        path.write_text(
            'workstream_id = "sample-workstream"\n'
            'card_id = "M01-T04"\n'
            'attempt = "R01"\n'
            f'verdict = "{verdict}"\n'
            f'evidence_path = "{evidence}"\n'
            + provenance_stanza
            + '[subject]\n'
            'class = "git_blob"\n'
            f'repository = "{REPOSITORY}"\n'
            f'commit = "{commit}"\n'
            'path = "implementation/workstreams/sample-workstream/results/M01-T04.md"\n'
            f'blob = "{blob}"\n'
            '[acceptance]\n'
            'class = "task_card"\n'
            f'path = "{CARD}"\n'
            '[independence]\n'
            'materially_produced_or_repaired_subject = false\n'
            'basis = "Fresh semantic reviewer context."\n'
        )

    def rebind_board_locator(
        self, project: Path, review_path: str, old_commit: str, old_blob: str,
    ) -> tuple[str, str]:
        commit, blob = self.git_identity_for(project, review_path)
        board = project / BOARD
        old = (
            f'{{ class = "review_attempt", path = "{review_path}", '
            f'commit = "{old_commit}", blob = "{old_blob}" }}'
        )
        new = (
            f'{{ class = "review_attempt", path = "{review_path}", '
            f'commit = "{commit}", blob = "{blob}" }}'
        )
        text = board.read_text()
        self.assertIn(old, text)
        board.write_text(text.replace(old, new, 1))
        return commit, blob

    def write_explicit_file(
        self, project: Path, review_path: str, verdict: str,
        commit: str, blob: str,
    ) -> None:
        path = project / review_path
        path.parent.mkdir(parents=True, exist_ok=True)
        evidence = "implementation/workstreams/sample-workstream/evidence/review-R01.md"
        evidence_file = project / evidence
        evidence_file.parent.mkdir(parents=True, exist_ok=True)
        evidence_file.write_text("# Review evidence\n")
        is_terminal = verdict in {"green", "red"}
        findings = '["F1"]' if verdict == "red" else "[]"
        defect_classes = '["class-a"]' if verdict == "red" else "[]"
        severity = ""
        if verdict == "red":
            severity = (
                '[[finding_severity]]\n'
                'id = "F1"\n'
                'surface = "correctness"\n'
                f'evidence = "{evidence}#F1"\n'
            )
        path.write_text(
            'workstream_id = "sample-workstream"\n'
            'card_id = "M01-T04"\n'
            'attempt = "R01"\n'
            f'verdict = "{verdict}"\n'
            f'evidence_path = "{evidence if is_terminal else ""}"\n'
            'review_kind = "discovery"\n'
            'source_discovery_attempt = ""\n'
            f'discovery_complete = {"true" if is_terminal else "false"}\n'
            f'material_finding_ids = {findings}\n'
            'review_scope = "card"\n'
            'review_epoch = "E01"\n'
            'epoch_reset_basis = ""\n'
            f'material_defect_class_ids = {defect_classes}\n'
            'failed_material_defect_class_ids = []\n'
            'post_convergence_validation = false\n'
            'convergence_basis = ""\n'
            + severity
            + '[subject]\n'
            'class = "git_blob"\n'
            f'repository = "{REPOSITORY}"\n'
            f'commit = "{commit}"\n'
            'path = "implementation/workstreams/sample-workstream/results/M01-T04.md"\n'
            f'blob = "{blob}"\n'
            '[acceptance]\n'
            'class = "task_card"\n'
            f'path = "{CARD}"\n'
            '[independence]\n'
            'materially_produced_or_repaired_subject = false\n'
            'basis = "Fresh semantic reviewer context."\n'
        )

    def bind_board_locator(self, project: Path, review_path: str, commit: str, blob: str) -> None:
        locator = (
            f'{{ class = "review_attempt", path = "{review_path}", '
            f'commit = "{commit}", blob = "{blob}" }}'
        )
        board = project / BOARD
        board_text = board.read_text()
        if "review_attempts = [" in board_text:
            lines = board_text.splitlines()
            for index, line in enumerate(lines):
                if line.startswith("review_attempts = ["):
                    existing = line.removeprefix("review_attempts = [").removesuffix("]")
                    lines[index] = f"review_attempts = [{existing}, {locator}]"
                    break
            board.write_text("\n".join(lines) + "\n")
        else:
            board.write_text(board_text.replace(
                'status = "in_progress"\n',
                'status = "in_progress"\n' + f'review_attempts = [{locator}]\n',
                1,
            ))

    def test_valid_exact_current_attempt_routes_deterministically(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project)
            review_path = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
            path = project / review_path
            path.parent.mkdir(parents=True, exist_ok=True)
            evidence = "implementation/workstreams/sample-workstream/evidence/review-R01.md"
            (project / evidence).parent.mkdir(parents=True, exist_ok=True)
            (project / evidence).write_text("# Review evidence\n")
            board_commit, board_blob = self.board_result_identity(project)
            path.write_text(
                'workstream_id = "sample-workstream"\n'
                'card_id = "M01-T04"\n'
                'attempt = "R01"\n'
                'verdict = "green"\n'
                f'evidence_path = "{evidence}"\n'
                'review_kind = "discovery"\n'
                'source_discovery_attempt = ""\n'
                'discovery_complete = true\n'
                'material_finding_ids = []\n'
                'review_scope = "card"\n'
                'review_epoch = "E01"\n'
                'epoch_reset_basis = ""\n'
                'material_defect_class_ids = []\n'
                'failed_material_defect_class_ids = []\n'
                'post_convergence_validation = false\n'
                'convergence_basis = ""\n'
                '[subject]\n'
                'class = "git_blob"\n'
                f'repository = "{REPOSITORY}"\n'
                f'commit = "{board_commit}"\n'
                'path = "implementation/workstreams/sample-workstream/results/M01-T04.md"\n'
                f'blob = "{board_blob}"\n'
                '[acceptance]\n'
                'class = "task_card"\n'
                f'path = "{CARD}"\n'
                '[independence]\n'
                'materially_produced_or_repaired_subject = false\n'
                'basis = "Fresh semantic reviewer context."\n'
            )
            commit, blob = self.git_identity_for(project, review_path)
            self.bind_board_locator(project, review_path, commit, blob)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "post_review_finalization"))
        finally:
            temp.cleanup()

    def test_newly_authored_legacy_without_provenance_routes_recovery(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project)
            review_path = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
            board_commit, board_blob = self.board_result_identity(project)
            self.write_legacy_file(project, review_path, "red", board_commit, board_blob, None)
            commit, blob = self.git_identity_for(project, review_path)
            self.bind_board_locator(project, review_path, commit, blob)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("provenance", routed.reason)
        finally:
            temp.cleanup()

    def test_unique_legacy_provenance_stays_inspectable_without_verdict_change(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project)
            review_path = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
            board_commit, board_blob = self.board_result_identity(project)
            # Historical source: legacy file without provenance, Board lists it path-only.
            self.write_legacy_file(project, review_path, "red", board_commit, board_blob, None)
            board = project / BOARD
            board_text = board.read_text()
            board.write_text(board_text.replace(
                'status = "in_progress"\n',
                'status = "in_progress"\n'
                f'review_attempts = [{{ class = "review_attempt", path = "{review_path}" }}]\n',
                1,
            ))
            source_commit, source_blob = self.git_identity_for(project, review_path)
            # Commit the source Board listing as well so the source Board readback works.
            subprocess.run(["git", "-C", str(project), "add", BOARD], check=True)
            subprocess.run(["git", "-C", str(project), "commit", "-q", "-m", "source board"], check=True)
            source_commit = subprocess.run(
                ["git", "-C", str(project), "rev-parse", "HEAD"],
                check=True, capture_output=True, text=True,
            ).stdout.strip()
            # Migration: add uniquely derived provenance, keep verdict/bytes otherwise identical.
            provenance = {
                "source_repository": REPOSITORY,
                "source_commit": source_commit,
                "source_path": review_path,
                "source_blob": source_blob,
                "source_workstream": "sample-workstream",
                "source_card": "M01-T04",
                "source_attempt": "R01",
            }
            self.write_legacy_file(project, review_path, "red", board_commit, board_blob, provenance)
            current_commit, current_blob = self.git_identity_for(project, review_path)
            # Rebind Board locator to the exact current (migrated) identity.
            board.write_text(
                (project / BOARD).read_text().replace(
                    f'{{ class = "review_attempt", path = "{review_path}" }}',
                    f'{{ class = "review_attempt", path = "{review_path}", '
                    f'commit = "{current_commit}", blob = "{current_blob}" }}',
                    1,
                )
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            # Terminal RED legacy stays inspectable as RED correction, without flipping to GREEN.
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution_resolution"))
        finally:
            temp.cleanup()

    def test_ambiguous_legacy_provenance_routes_recovery(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project)
            review_path = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
            board_commit, board_blob = self.board_result_identity(project)
            self.write_legacy_file(project, review_path, "red", board_commit, board_blob, None)
            source_commit, source_blob = self.git_identity_for(project, review_path)
            # Ambiguous: provenance claims a blob that never matched the source bytes.
            provenance = {
                "source_repository": REPOSITORY,
                "source_commit": source_commit,
                "source_path": review_path,
                "source_blob": "f" * 40,
                "source_workstream": "sample-workstream",
                "source_card": "M01-T04",
                "source_attempt": "R01",
            }
            _ = source_blob
            self.write_legacy_file(project, review_path, "red", board_commit, board_blob, provenance)
            current_commit, current_blob = self.git_identity_for(project, review_path)
            self.bind_board_locator(project, review_path, current_commit, current_blob)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("provenance", routed.reason)
        finally:
            temp.cleanup()

    def test_same_id_red_to_green_worktree_rewrite_routes_recovery(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project)
            review_path = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
            path = project / review_path
            path.parent.mkdir(parents=True, exist_ok=True)
            evidence = "implementation/workstreams/sample-workstream/evidence/review-R01.md"
            (project / evidence).parent.mkdir(parents=True, exist_ok=True)
            (project / evidence).write_text("# Review evidence\n")
            board_commit, board_blob = self.board_result_identity(project)
            path.write_text(
                'workstream_id = "sample-workstream"\n'
                'card_id = "M01-T04"\n'
                'attempt = "R01"\n'
                'verdict = "red"\n'
                f'evidence_path = "{evidence}"\n'
                'review_kind = "discovery"\n'
                'source_discovery_attempt = ""\n'
                'discovery_complete = true\n'
                'material_finding_ids = ["F1"]\n'
                'review_scope = "card"\n'
                'review_epoch = "E01"\n'
                'epoch_reset_basis = ""\n'
                'material_defect_class_ids = ["class-a"]\n'
                'failed_material_defect_class_ids = []\n'
                'post_convergence_validation = false\n'
                'convergence_basis = ""\n'
                '[[finding_severity]]\n'
                'id = "F1"\n'
                'surface = "correctness"\n'
                f'evidence = "{evidence}#F1"\n'
                '[subject]\n'
                'class = "git_blob"\n'
                f'repository = "{REPOSITORY}"\n'
                f'commit = "{board_commit}"\n'
                'path = "implementation/workstreams/sample-workstream/results/M01-T04.md"\n'
                f'blob = "{board_blob}"\n'
                '[acceptance]\n'
                'class = "task_card"\n'
                f'path = "{CARD}"\n'
                '[independence]\n'
                'materially_produced_or_repaired_subject = false\n'
                'basis = "Fresh semantic reviewer context."\n'
            )
            commit, blob = self.git_identity_for(project, review_path)
            self.bind_board_locator(project, review_path, commit, blob)
            # Stable RED route before the rewrite.
            before = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((before.disposition, before.obligation), ("route", "execution_resolution"))
            # Same-ID rewrite: flip verdict bytes without updating the Board locator.
            rewritten = path.read_text().replace('verdict = "red"', 'verdict = "green"', 1)
            path.write_text(rewritten)
            after = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((after.disposition, after.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("review attempt identity failed", after.reason)
        finally:
            temp.cleanup()

    def test_committed_red_to_green_rewrite_with_rebound_locator_routes_recovery(self) -> None:
        # H009 end-to-end: a terminal RED rewritten to GREEN, recommitted, and
        # rebound in the Board locator must still fail: the router re-derives
        # prior terminal state from actual Git history, not from the locator.
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project)
            review_path = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
            path = project / review_path
            path.parent.mkdir(parents=True, exist_ok=True)
            evidence = "implementation/workstreams/sample-workstream/evidence/review-R01.md"
            (project / evidence).parent.mkdir(parents=True, exist_ok=True)
            (project / evidence).write_text("# Review evidence\n")
            board_commit, board_blob = self.board_result_identity(project)
            path.write_text(
                'workstream_id = "sample-workstream"\n'
                'card_id = "M01-T04"\n'
                'attempt = "R01"\n'
                'verdict = "red"\n'
                f'evidence_path = "{evidence}"\n'
                'review_kind = "discovery"\n'
                'source_discovery_attempt = ""\n'
                'discovery_complete = true\n'
                'material_finding_ids = ["F1"]\n'
                'review_scope = "card"\n'
                'review_epoch = "E01"\n'
                'epoch_reset_basis = ""\n'
                'material_defect_class_ids = ["class-a"]\n'
                'failed_material_defect_class_ids = []\n'
                'post_convergence_validation = false\n'
                'convergence_basis = ""\n'
                '[[finding_severity]]\n'
                'id = "F1"\n'
                'surface = "correctness"\n'
                f'evidence = "{evidence}#F1"\n'
                '[subject]\n'
                'class = "git_blob"\n'
                f'repository = "{REPOSITORY}"\n'
                f'commit = "{board_commit}"\n'
                'path = "implementation/workstreams/sample-workstream/results/M01-T04.md"\n'
                f'blob = "{board_blob}"\n'
                '[acceptance]\n'
                'class = "task_card"\n'
                f'path = "{CARD}"\n'
                '[independence]\n'
                'materially_produced_or_repaired_subject = false\n'
                'basis = "Fresh semantic reviewer context."\n'
            )
            commit, blob = self.git_identity_for(project, review_path)
            self.bind_board_locator(project, review_path, commit, blob)
            before = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((before.disposition, before.obligation), ("route", "execution_resolution"))
            # Same-ID rewrite to a valid GREEN, recommitted and rebound.
            rewritten = (
                path.read_text()
                .replace('verdict = "red"', 'verdict = "green"', 1)
                .replace('material_finding_ids = ["F1"]', "material_finding_ids = []", 1)
                .replace(
                    'material_defect_class_ids = ["class-a"]',
                    "material_defect_class_ids = []",
                    1,
                )
            )
            kept: list[str] = []
            skipping = False
            for line in rewritten.splitlines(keepends=True):
                if line.startswith("[[finding_severity]]"):
                    skipping = True
                    continue
                if skipping:
                    if line.startswith("[subject]"):
                        skipping = False
                    else:
                        continue
                kept.append(line)
            path.write_text("".join(kept))
            self.rebind_board_locator(project, review_path, commit, blob)
            after = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((after.disposition, after.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("append-only", after.reason)
            self.assertIn("silently rewritten", after.reason)
        finally:
            temp.cleanup()

    def test_pending_to_terminal_transition_with_rebind_still_routes(self) -> None:
        # The Git-history freeze must preserve the legitimate lifecycle: a
        # pending attempt finalized to terminal GREEN routes normally.
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project)
            review_path = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
            path = project / review_path
            path.parent.mkdir(parents=True, exist_ok=True)
            evidence = "implementation/workstreams/sample-workstream/evidence/review-R01.md"
            (project / evidence).parent.mkdir(parents=True, exist_ok=True)
            (project / evidence).write_text("# Review evidence\n")
            board_commit, board_blob = self.board_result_identity(project)
            subject_stanza = (
                '[subject]\n'
                'class = "git_blob"\n'
                f'repository = "{REPOSITORY}"\n'
                f'commit = "{board_commit}"\n'
                'path = "implementation/workstreams/sample-workstream/results/M01-T04.md"\n'
                f'blob = "{board_blob}"\n'
                '[acceptance]\n'
                'class = "task_card"\n'
                f'path = "{CARD}"\n'
                '[independence]\n'
                'materially_produced_or_repaired_subject = false\n'
                'basis = "Fresh semantic reviewer context."\n'
            )
            path.write_text(
                'workstream_id = "sample-workstream"\n'
                'card_id = "M01-T04"\n'
                'attempt = "R01"\n'
                'verdict = "pending"\n'
                'evidence_path = ""\n'
                'review_kind = "discovery"\n'
                'source_discovery_attempt = ""\n'
                'discovery_complete = false\n'
                'material_finding_ids = []\n'
                'review_scope = "card"\n'
                'review_epoch = "E01"\n'
                'epoch_reset_basis = ""\n'
                'material_defect_class_ids = []\n'
                'failed_material_defect_class_ids = []\n'
                'post_convergence_validation = false\n'
                'convergence_basis = ""\n'
                + subject_stanza
            )
            commit, blob = self.git_identity_for(project, review_path)
            self.bind_board_locator(project, review_path, commit, blob)
            pending_routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((pending_routed.disposition, pending_routed.obligation), ("route", "review"))
            path.write_text(
                'workstream_id = "sample-workstream"\n'
                'card_id = "M01-T04"\n'
                'attempt = "R01"\n'
                'verdict = "green"\n'
                f'evidence_path = "{evidence}"\n'
                'review_kind = "discovery"\n'
                'source_discovery_attempt = ""\n'
                'discovery_complete = true\n'
                'material_finding_ids = []\n'
                'review_scope = "card"\n'
                'review_epoch = "E01"\n'
                'epoch_reset_basis = ""\n'
                'material_defect_class_ids = []\n'
                'failed_material_defect_class_ids = []\n'
                'post_convergence_validation = false\n'
                'convergence_basis = ""\n'
                + subject_stanza
            )
            self.rebind_board_locator(project, review_path, commit, blob)
            final = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((final.disposition, final.obligation), ("route", "post_review_finalization"))
        finally:
            temp.cleanup()

    def test_same_commit_legacy_file_and_board_listing_cannot_self_certify(self) -> None:
        # H008: a legacy file introduced together with its Board listing in
        # one source commit was never historically listed, so provenance
        # pointing at that commit is ambiguous, not unique.
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project)
            review_path = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
            board_commit, board_blob = self.board_result_identity(project)
            self.write_legacy_file(project, review_path, "red", board_commit, board_blob, None)
            board = project / BOARD
            board.write_text(board.read_text().replace(
                'status = "in_progress"\n',
                'status = "in_progress"\n'
                f'review_attempts = [{{ class = "review_attempt", path = "{review_path}" }}]\n',
                1,
            ))
            subprocess.run(["git", "-C", str(project), "add", review_path, BOARD], check=True)
            subprocess.run(["git", "-C", str(project), "commit", "-q", "-m", "same-commit file+listing"], check=True)
            source_commit = subprocess.run(
                ["git", "-C", str(project), "rev-parse", "HEAD"],
                check=True, capture_output=True, text=True,
            ).stdout.strip()
            source_blob = subprocess.run(
                ["git", "-C", str(project), "rev-parse", f"HEAD:{review_path}"],
                check=True, capture_output=True, text=True,
            ).stdout.strip()
            provenance = {
                "source_repository": REPOSITORY,
                "source_commit": source_commit,
                "source_path": review_path,
                "source_blob": source_blob,
                "source_workstream": "sample-workstream",
                "source_card": "M01-T04",
                "source_attempt": "R01",
            }
            self.write_legacy_file(project, review_path, "red", board_commit, board_blob, provenance)
            current_commit, current_blob = self.git_identity_for(project, review_path)
            board.write_text(
                (project / BOARD).read_text().replace(
                    f'{{ class = "review_attempt", path = "{review_path}" }}',
                    f'{{ class = "review_attempt", path = "{review_path}", '
                    f'commit = "{current_commit}", blob = "{current_blob}" }}',
                    1,
                )
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("provenance", routed.reason)
            self.assertIn("same-commit", routed.reason)
        finally:
            temp.cleanup()

    def test_off_head_alternate_branch_rewrite_cannot_route(self) -> None:
        # H009: a relied-upon locator commit outside HEAD ancestry would hide
        # its own prior terminal state from the HEAD-history freeze, so both
        # the off-HEAD RED and its rebound off-HEAD GREEN flip must fail.
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project)
            review_path = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
            board_commit, board_blob = self.board_result_identity(project)
            # Phase 1: RED committed only on an alternate branch; HEAD has no
            # history for the path, so the HEAD walk alone would be blind.
            subprocess.run(
                ["git", "-C", str(project), "checkout", "-q", "-b", "rf006-alt"], check=True,
            )
            self.write_explicit_file(project, review_path, "red", board_commit, board_blob)
            subprocess.run(["git", "-C", str(project), "add", review_path], check=True)
            subprocess.run(["git", "-C", str(project), "commit", "-q", "-m", "alt red"], check=True)
            red_commit = subprocess.run(
                ["git", "-C", str(project), "rev-parse", "HEAD"],
                check=True, capture_output=True, text=True,
            ).stdout.strip()
            red_blob = subprocess.run(
                ["git", "-C", str(project), "rev-parse", f"HEAD:{review_path}"],
                check=True, capture_output=True, text=True,
            ).stdout.strip()
            subprocess.run(["git", "-C", str(project), "checkout", "-q", "-"], check=True)
            self.write_explicit_file(project, review_path, "red", board_commit, board_blob)
            self.bind_board_locator(project, review_path, red_commit, red_blob)
            red_routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (red_routed.disposition, red_routed.obligation), ("recovery", "recovery_boundary"),
            )
            self.assertIn("review attempt identity failed", red_routed.reason)
            self.assertIn("HEAD ancestry", red_routed.reason)
            # Phase 2: same-ID GREEN flip on a second alternate branch, with
            # rebound locator and current worktree bytes.
            subprocess.run(
                ["git", "-C", str(project), "checkout", "-q", "-b", "rf006-alt2"], check=True,
            )
            self.write_explicit_file(project, review_path, "green", board_commit, board_blob)
            subprocess.run(["git", "-C", str(project), "add", review_path], check=True)
            subprocess.run(["git", "-C", str(project), "commit", "-q", "-m", "alt2 green"], check=True)
            green_blob = subprocess.run(
                ["git", "-C", str(project), "rev-parse", f"HEAD:{review_path}"],
                check=True, capture_output=True, text=True,
            ).stdout.strip()
            green_commit = subprocess.run(
                ["git", "-C", str(project), "rev-parse", "HEAD"],
                check=True, capture_output=True, text=True,
            ).stdout.strip()
            subprocess.run(["git", "-C", str(project), "checkout", "-q", "-"], check=True)
            self.write_explicit_file(project, review_path, "green", board_commit, board_blob)
            # Rebind the locator to the alt2 commit without committing on
            # HEAD: identity resolves and worktree bytes are fresh, but the
            # commit is outside HEAD ancestry.
            board = project / BOARD
            old = (
                f'{{ class = "review_attempt", path = "{review_path}", '
                f'commit = "{red_commit}", blob = "{red_blob}" }}'
            )
            new = (
                f'{{ class = "review_attempt", path = "{review_path}", '
                f'commit = "{green_commit}", blob = "{green_blob}" }}'
            )
            text = board.read_text()
            self.assertIn(old, text)
            board.write_text(text.replace(old, new, 1))
            green_routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (green_routed.disposition, green_routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("review attempt identity failed", green_routed.reason)
            self.assertIn("HEAD ancestry", green_routed.reason)
        finally:
            temp.cleanup()

    def test_strict_ancestor_locator_commit_still_routes(self) -> None:
        # Positive control: a locator commit that is a strict HEAD ancestor
        # (HEAD advanced past it by an unrelated commit) still routes.
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project)
            review_path = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
            board_commit, board_blob = self.board_result_identity(project)
            self.write_explicit_file(project, review_path, "green", board_commit, board_blob)
            commit, blob = self.git_identity_for(project, review_path)
            self.bind_board_locator(project, review_path, commit, blob)
            scratch_rel = "implementation/workstreams/sample-workstream/evidence/review-note.md"
            (project / scratch_rel).write_text("# Unrelated note\n")
            self.git_identity_for(project, scratch_rel)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation), ("route", "post_review_finalization"),
            )
        finally:
            temp.cleanup()

    def test_bogus_attempt_identity_routes_recovery(self) -> None:
        for commit, blob, _label in (
            ("c" * 40, "d" * 40, "dangling"),
            ("a" * 40, "b" * 40, "fabricated"),
        ):
            with self.subTest(identity=_label):
                temp, project = self.copy_fixture()
                try:
                    self.install_reviewable_result(project)
                    review_path = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
                    path = project / review_path
                    path.parent.mkdir(parents=True, exist_ok=True)
                    evidence = "implementation/workstreams/sample-workstream/evidence/review-R01.md"
                    (project / evidence).parent.mkdir(parents=True, exist_ok=True)
                    (project / evidence).write_text("# Review evidence\n")
                    board_commit, board_blob = self.board_result_identity(project)
                    path.write_text(
                        'workstream_id = "sample-workstream"\n'
                        'card_id = "M01-T04"\n'
                        'attempt = "R01"\n'
                        'verdict = "green"\n'
                        f'evidence_path = "{evidence}"\n'
                        'review_kind = "discovery"\n'
                        'source_discovery_attempt = ""\n'
                        'discovery_complete = true\n'
                        'material_finding_ids = []\n'
                        'review_scope = "card"\n'
                        'review_epoch = "E01"\n'
                        'epoch_reset_basis = ""\n'
                        'material_defect_class_ids = []\n'
                        'failed_material_defect_class_ids = []\n'
                        'post_convergence_validation = false\n'
                        'convergence_basis = ""\n'
                        '[subject]\n'
                        'class = "git_blob"\n'
                        f'repository = "{REPOSITORY}"\n'
                        f'commit = "{board_commit}"\n'
                        'path = "implementation/workstreams/sample-workstream/results/M01-T04.md"\n'
                        f'blob = "{board_blob}"\n'
                        '[acceptance]\n'
                        'class = "task_card"\n'
                        f'path = "{CARD}"\n'
                        '[independence]\n'
                        'materially_produced_or_repaired_subject = false\n'
                        'basis = "Fresh semantic reviewer context."\n'
                    )
                    # Bind a bogus locator without committing the file under that identity.
                    self.bind_board_locator(project, review_path, commit, blob)
                    routed = select_route(project, [MANIFEST], package_root=ROOT)
                    self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
                    self.assertIn("review attempt identity failed", routed.reason)
                finally:
                    temp.cleanup()

    def test_missing_dangling_mismatched_sibling_identities_route_recovery(self) -> None:
        # Missing: path-only locator for an active Card cannot prove history.
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project)
            review_path = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
            path = project / review_path
            path.parent.mkdir(parents=True, exist_ok=True)
            evidence = "implementation/workstreams/sample-workstream/evidence/review-R01.md"
            (project / evidence).parent.mkdir(parents=True, exist_ok=True)
            (project / evidence).write_text("# Review evidence\n")
            board_commit, board_blob = self.board_result_identity(project)
            path.write_text(
                'workstream_id = "sample-workstream"\n'
                'card_id = "M01-T04"\n'
                'attempt = "R01"\n'
                'verdict = "green"\n'
                f'evidence_path = "{evidence}"\n'
                'review_kind = "discovery"\n'
                'source_discovery_attempt = ""\n'
                'discovery_complete = true\n'
                'material_finding_ids = []\n'
                'review_scope = "card"\n'
                'review_epoch = "E01"\n'
                'epoch_reset_basis = ""\n'
                'material_defect_class_ids = []\n'
                'failed_material_defect_class_ids = []\n'
                'post_convergence_validation = false\n'
                'convergence_basis = ""\n'
                '[subject]\n'
                'class = "git_blob"\n'
                f'repository = "{REPOSITORY}"\n'
                f'commit = "{board_commit}"\n'
                'path = "implementation/workstreams/sample-workstream/results/M01-T04.md"\n'
                f'blob = "{board_blob}"\n'
                '[acceptance]\n'
                'class = "task_card"\n'
                f'path = "{CARD}"\n'
                '[independence]\n'
                'materially_produced_or_repaired_subject = false\n'
                'basis = "Fresh semantic reviewer context."\n'
            )
            commit, blob = self.git_identity_for(project, review_path)
            _ = (commit, blob)
            board = project / BOARD
            board.write_text(board.read_text().replace(
                'status = "in_progress"\n',
                'status = "in_progress"\n'
                f'review_attempts = [{{ class = "review_attempt", path = "{review_path}" }}]\n',
                1,
            ))
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("commit + blob", routed.reason)
        finally:
            temp.cleanup()

        # Sibling: locator path names another Card's attempt identity.
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project)
            sibling_path = "implementation/workstreams/sample-workstream/reviews/M01-T99-R01.toml"
            sibling = project / sibling_path
            sibling.parent.mkdir(parents=True, exist_ok=True)
            evidence = "implementation/workstreams/sample-workstream/evidence/review-R01.md"
            (project / evidence).parent.mkdir(parents=True, exist_ok=True)
            (project / evidence).write_text("# Review evidence\n")
            board_commit, board_blob = self.board_result_identity(project)
            sibling.write_text(
                'workstream_id = "sample-workstream"\n'
                'card_id = "M01-T04"\n'
                'attempt = "R01"\n'
                'verdict = "green"\n'
                f'evidence_path = "{evidence}"\n'
                'review_kind = "discovery"\n'
                'source_discovery_attempt = ""\n'
                'discovery_complete = true\n'
                'material_finding_ids = []\n'
                'review_scope = "card"\n'
                'review_epoch = "E01"\n'
                'epoch_reset_basis = ""\n'
                'material_defect_class_ids = []\n'
                'failed_material_defect_class_ids = []\n'
                'post_convergence_validation = false\n'
                'convergence_basis = ""\n'
                '[subject]\n'
                'class = "git_blob"\n'
                f'repository = "{REPOSITORY}"\n'
                f'commit = "{board_commit}"\n'
                'path = "implementation/workstreams/sample-workstream/results/M01-T04.md"\n'
                f'blob = "{board_blob}"\n'
                '[acceptance]\n'
                'class = "task_card"\n'
                f'path = "{CARD}"\n'
                '[independence]\n'
                'materially_produced_or_repaired_subject = false\n'
                'basis = "Fresh semantic reviewer context."\n'
            )
            commit, blob = self.git_identity_for(project, sibling_path)
            self.bind_board_locator(project, sibling_path, commit, blob)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
        finally:
            temp.cleanup()

    def test_direct_locator_verifier_rejects_sibling_binding(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project)
            review_path = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
            path = project / review_path
            path.parent.mkdir(parents=True, exist_ok=True)
            evidence = "implementation/workstreams/sample-workstream/evidence/review-R01.md"
            (project / evidence).parent.mkdir(parents=True, exist_ok=True)
            (project / evidence).write_text("# Review evidence\n")
            board_commit, board_blob = self.board_result_identity(project)
            path.write_text(
                'workstream_id = "sample-workstream"\n'
                'card_id = "M01-T99"\n'
                'attempt = "R01"\n'
                'verdict = "green"\n'
                f'evidence_path = "{evidence}"\n'
                'review_kind = "discovery"\n'
                'source_discovery_attempt = ""\n'
                'discovery_complete = true\n'
                'material_finding_ids = []\n'
                'review_scope = "card"\n'
                'review_epoch = "E01"\n'
                'epoch_reset_basis = ""\n'
                'material_defect_class_ids = []\n'
                'failed_material_defect_class_ids = []\n'
                'post_convergence_validation = false\n'
                'convergence_basis = ""\n'
                '[subject]\n'
                'class = "git_blob"\n'
                f'repository = "{REPOSITORY}"\n'
                f'commit = "{board_commit}"\n'
                'path = "implementation/workstreams/sample-workstream/results/M01-T04.md"\n'
                f'blob = "{board_blob}"\n'
                '[acceptance]\n'
                'class = "authority"\n'
                'path = "requirements/REQUIREMENTS.md"\n'
                '[independence]\n'
                'materially_produced_or_repaired_subject = false\n'
                'basis = "Fresh semantic reviewer context."\n'
            )
            commit, blob = self.git_identity_for(project, review_path)
            with self.assertRaisesRegex(ReviewAttemptProvenanceError, "another Card"):
                verify_review_attempt_locator(
                    project_root=project,
                    project_repository=REPOSITORY,
                    workstream_id="sample-workstream",
                    card_id="M01-T04",
                    ref={"class": "review_attempt", "path": review_path, "commit": commit, "blob": blob},
                    label="review_attempts[0]",
                )
        finally:
            temp.cleanup()

    def test_direct_legacy_verifier_requires_listed_source_board(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project)
            review_path = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"
            board_commit, board_blob = self.board_result_identity(project)
            # Source commit exists but its Board never listed the attempt path.
            self.write_legacy_file(project, review_path, "red", board_commit, board_blob, None)
            source_commit, source_blob = self.git_identity_for(project, review_path)
            attempt = {
                "workstream_id": "sample-workstream",
                "card_id": "M01-T04",
                "attempt": "R01",
                "verdict": "red",
                "evidence_path": "implementation/workstreams/sample-workstream/evidence/review-R01.md",
                "subject": {
                    "class": "git_blob",
                    "repository": REPOSITORY,
                    "commit": board_commit,
                    "path": "implementation/workstreams/sample-workstream/results/M01-T04.md",
                    "blob": board_blob,
                },
                "acceptance": {"class": "task_card", "path": CARD},
                "independence": {
                    "materially_produced_or_repaired_subject": False,
                    "basis": "Fresh semantic reviewer context.",
                },
                "legacy_migration": {
                    "source_repository": REPOSITORY,
                    "source_commit": source_commit,
                    "source_path": review_path,
                    "source_blob": source_blob,
                    "source_workstream": "sample-workstream",
                    "source_card": "M01-T04",
                    "source_attempt": "R01",
                },
            }
            # The source Board at source_commit is the fixture Board without any
            # review_attempts listing, so provenance is ambiguous, not unique.
            with self.assertRaisesRegex(ReviewAttemptProvenanceError, "never listed|ambiguous"):
                verify_legacy_migration(
                    project_root=project,
                    project_repository=REPOSITORY,
                    workstream_id="sample-workstream",
                    card_id="M01-T04",
                    attempt=attempt,
                )
        finally:
            temp.cleanup()


class TerminalFreezeMergeTests(unittest.TestCase):
    WORKSTREAM = "sample-workstream"
    CARD = "M01-T04"
    REVIEW = "implementation/workstreams/sample-workstream/reviews/M01-T04-R01.toml"

    def _init_repo(self, project: Path) -> None:
        subprocess.run(["git", "init", "-q", str(project)], check=True)
        subprocess.run(
            ["git", "-C", str(project), "config", "user.email", "fixture@example.invalid"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(project), "config", "user.name", "Fixture"],
            check=True,
        )
        subprocess.run(["git", "-C", str(project), "branch", "-M", "main"], check=True)

    def _commit(self, project: Path, relpath: str, message: str) -> None:
        subprocess.run(["git", "-C", str(project), "add", relpath], check=True)
        subprocess.run(
            ["git", "-C", str(project), "commit", "-q", "-m", message], check=True
        )

    def _write_attempt(self, project: Path, verdict: str) -> dict:
        path = project / self.REVIEW
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            f'workstream_id = "{self.WORKSTREAM}"\n'
            f'card_id = "{self.CARD}"\n'
            'attempt = "R01"\n'
            f'verdict = "{verdict}"\n'
            'evidence_path = "implementation/workstreams/sample-workstream/evidence/review-R01.md"\n'
            '[subject]\n'
            'class = "git_blob"\n'
            'repository = "owner/fixture"\n'
            f'commit = "{"a" * 40}"\n'
            'path = "implementation/workstreams/sample-workstream/results/M01-T04.md"\n'
            f'blob = "{"b" * 40}"\n',
            encoding="utf-8",
        )
        with path.open("rb") as handle:
            return tomllib.load(handle)

    def _merge_fixture(self, project: Path, side_verdict: str) -> dict:
        self._init_repo(project)
        (project / "base.txt").write_text("base\n", encoding="utf-8")
        self._commit(project, "base.txt", "base")
        subprocess.run(
            ["git", "-C", str(project), "checkout", "-qb", "side"], check=True
        )
        self._write_attempt(project, side_verdict)
        self._commit(project, self.REVIEW, f"side {side_verdict}")
        subprocess.run(
            ["git", "-C", str(project), "checkout", "-q", "main"], check=True
        )
        self._write_attempt(project, "green")
        self._commit(project, self.REVIEW, "main green")
        subprocess.run(
            ["git", "-C", str(project), "merge", "--no-commit", "side"],
            check=False,
        )
        current = self._write_attempt(project, "green")
        subprocess.run(["git", "-C", str(project), "add", "-A"], check=True)
        subprocess.run(
            ["git", "-C", str(project), "commit", "-q", "-m", "merge resolving green"],
            check=True,
        )
        return current

    def test_merge_side_branch_terminal_red_is_visited(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            current = self._merge_fixture(project, "red")
            with self.assertRaisesRegex(
                ReviewAttemptProvenanceError, "silently rewritten"
            ):
                verify_terminal_append_only_from_git(
                    project_root=project,
                    workstream_id=self.WORKSTREAM,
                    card_id=self.CARD,
                    attempts=[current],
                )

    def test_merge_side_branch_pending_still_finalizes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = Path(raw)
            current = self._merge_fixture(project, "pending")
            reads = verify_terminal_append_only_from_git(
                project_root=project,
                workstream_id=self.WORKSTREAM,
                card_id=self.CARD,
                attempts=[current],
            )
            self.assertEqual(reads, [f"project-git-log:{self.REVIEW}"])


if __name__ == "__main__":
    unittest.main()
