from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.router import PRIORITY_FOUNDATION, REAL_STOP_FOUNDATION, classify_jit_refinement, select_route

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"

# RF012 fixture authority: deterministic blobs for "# Accepted authority\n" and
# "# Accepted decision\n" via git_blob_sha; key binds R1 plus exact identities.
RF012_REQ_PATH = "requirements/REQUIREMENTS.md"
RF012_REQ_CONTENT = "# Accepted authority\n"
RF012_REQ_BLOB = "6ba7e7db1e09b041d121590adebdd9fa68e9a5bd"
RF012_DEC_PATH = "decisions/ADR-001.md"
RF012_DEC_CONTENT = "# Accepted decision\n"
RF012_DEC_BLOB = "f8b3e92564546b7f0192f648013c4c0951f45309"
RF012_REPOSITORY = "owner/router-fixture"
RF012_KEY = (
    f"rf012-v1:repository:{RF012_REPOSITORY}|definition:R1|"
    f"requirements:{RF012_REQ_PATH}@{RF012_REQ_BLOB}|"
    f"decisions:{RF012_DEC_PATH}@{RF012_DEC_BLOB}"
)
RF012_PLAN_PATH = "planning/MASTER_PLAN.md"
RF012_PLAN_CONTENT = "# Master plan\n"

# RF009 fixture provenance: the consumed intake Research blob committed under
# this path, bound by the fixture PROJECT.md repository below.
RF009_RESEARCH = "implementation/workstreams/sample-workstream/RESEARCH.toml"
RF009_PROOF_REPOSITORY = "owner/router-fixture"


class RouterTests(unittest.TestCase):
    def copy_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(FIXTURE, project)
        return temp, project

    def test_valid_state_selects_same_route_independent_of_runtime_noise(self) -> None:
        expected = None
        for noise in (
            {},
            {"RUNTIME": "chatgpt", "MODEL_ID": "one", "SESSION_ID": "alpha"},
            {"RUNTIME": "codex", "MODEL_ID": "two", "SESSION_ID": "beta"},
        ):
            with patch.dict(os.environ, noise, clear=False):
                routed = select_route(FIXTURE, [MANIFEST], package_root=ROOT)
            semantic = (routed.disposition, routed.obligation, routed.subject, routed.owner_module)
            expected = expected or semantic
            self.assertEqual(semantic, expected)
        self.assertEqual(expected, ("route", "execution", "M01-T04", "workflow/EXECUTION.md"))

    def test_progressive_disclosure_read_set_is_exact(self) -> None:
        routed = select_route(FIXTURE, [MANIFEST], package_root=ROOT)
        self.assertEqual(
            routed.read_set,
            (
                "package:workflow/ROUTER.md",
                "project:PROJECT.md",
                f"project:{MANIFEST}",
                "package:policy/mechanical_policy.json",
                "package:workflow/POLICY_KERNEL.md",
                f"project:{BOARD}",
                f"project:{CARD}",
            ),
        )
        joined = "\n".join(routed.read_set)
        self.assertNotIn("migration/UNRELATED.md", joined)
        self.assertNotIn("untrusted/ISSUE_TEXT.md", joined)
        self.assertNotIn("templates/", joined)

    def task_card_content(
        self, *, dependencies: str = "none", technical_contract: str = "none",
        review_requirement: str = "none",
    ) -> str:
        return (
            "# Fixture Card\n"
            "- Card ID: M01-T04\n"
            "- Included scope: prove launch readiness\n"
            "- Excluded scope: runtime-specific orchestration\n"
            "- Authority refs: requirements/REQUIREMENTS.md\n"
            f"- Dependencies: {dependencies}\n"
            "- Acceptance: route only after current launch inputs are valid\n"
            "- Required tests/readback: production router fixture\n"
            f"- Review requirement: {review_requirement}\n"
            f"- Technical contract: {technical_contract}\n"
        )

    def make_ready_card(self, project: Path, *, dependencies: str = "none",
                        technical_contract: str = "none") -> None:
        board = project / BOARD
        board.write_text(board.read_text().replace('status = "in_progress"', 'status = "ready"'))
        card = project / CARD
        card.write_text(self.task_card_content(
            dependencies=dependencies,
            technical_contract=technical_contract,
        ))
        authority = project / "requirements" / "REQUIREMENTS.md"
        authority.parent.mkdir(parents=True, exist_ok=True)
        authority.write_text("# Accepted authority\n")

    def test_ready_card_launch_refresh_is_runtime_neutral_and_progressive(self) -> None:
        for noise in (
            {"RUNTIME": "codex", "MODEL_ID": "one", "WORKER_ID": "alpha"},
            {"RUNTIME": "pi", "MODEL_ID": "two", "WORKER_ID": "beta"},
        ):
            temp, project = self.copy_fixture()
            try:
                self.make_ready_card(project)
                with patch.dict(os.environ, noise, clear=False):
                    routed = select_route(project, [MANIFEST], package_root=ROOT)
                self.assertEqual((routed.disposition, routed.obligation), ("route", "execution_prep"))
                self.assertEqual(routed.subject, "M01-T04")
                self.assertIn("project:requirements/REQUIREMENTS.md", routed.read_set)
                self.assertFalse(any("openspec/" in item or "contracts/" in item for item in routed.read_set))
            finally:
                temp.cleanup()

    @staticmethod
    def git_identity_for(project: Path, relpath: str) -> tuple[str, str]:
        """Commit one fixture file and return its real (commit, blob) identity."""
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

    def prior_art_proof(self, project: Path) -> str:
        """Commit the live consumed intake Research; return its INTAKE proof stanza."""
        commit, blob = self.git_identity_for(project, RF009_RESEARCH)
        return (
            "[diagnosis_prior_art_proof]\n"
            'class = "research"\n'
            f'repository = "{RF009_PROOF_REPOSITORY}"\n'
            f'commit = "{commit}"\n'
            f'path = "{RF009_RESEARCH}"\n'
            f'blob = "{blob}"\n'
        )

    @staticmethod
    def board_result_identity(project: Path) -> tuple[str, str]:
        """Return the current board result (commit, blob) for the active Card."""
        section = (project / BOARD).read_text().split("[cards.result]", 1)[1]
        commit = re.search(r'commit = "([0-9a-f]{40})"', section).group(1)  # type: ignore[union-attr]
        blob = re.search(r'blob = "([0-9a-f]{40})"', section).group(1)  # type: ignore[union-attr]
        return commit, blob

    @classmethod
    def card_acceptance_identity(cls, project: Path, relpath: str) -> tuple[str, str]:
        """Return the exact (commit, blob) for a Task Card acceptance binding.

        H005: Card Review acceptance carries exact Git identity. Commits the
        Card when it is new or mutated; the commit is the latest commit
        touching the Card so unrelated commits do not churn the binding and
        repeated helper calls stay stable.
        """
        if not cls._card_matches_head(project, relpath):
            cls.git_identity_for(project, relpath)
        commit = subprocess.run(
            ["git", "-C", str(project), "log", "--format=%H", "-1", "HEAD", "--", relpath],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        blob = subprocess.run(
            ["git", "-C", str(project), "rev-parse", f"{commit}:{relpath}"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        return commit, blob

    @staticmethod
    def _card_matches_head(project: Path, relpath: str) -> bool:
        try:
            in_head = subprocess.run(
                ["git", "-C", str(project), "rev-parse", "--verify", f"HEAD:{relpath}"],
                capture_output=True, text=True, check=False,
            )
            if in_head.returncode != 0:
                return False
            diff = subprocess.run(
                ["git", "-C", str(project), "diff", "--quiet", "HEAD", "--", relpath],
                capture_output=True, check=False,
            )
            return diff.returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False

    def commit_result_version(self, project: Path, result_path: str, content: str) -> tuple[str, str]:
        """Write new result bytes, commit them, and rebind the board locator."""
        old_commit, old_blob = self.board_result_identity(project)
        (project / result_path).write_text(content)
        commit, blob = self.git_identity_for(project, result_path)
        board = project / BOARD
        board.write_text(
            board.read_text()
            .replace(f'commit = "{old_commit}"', f'commit = "{commit}"', 1)
            .replace(f'blob = "{old_blob}"', f'blob = "{blob}"', 1)
        )
        return commit, blob

    def rebind_review_attempt(self, project: Path, review_path: str) -> tuple[str, str]:
        """Recommit a modified review file and rebind its Board locator identity."""
        board = project / BOARD
        text = board.read_text()
        # Find the locator for this path and replace its commit/blob with the
        # new Git identity after recommitting the modified file.
        commit, blob = self.git_identity_for(project, review_path)
        # Locate the locator substring for this path; Board locators are inline
        # tables with class/path/commit/blob for RF006 exact identity.
        pattern = re.compile(
            r'\{\s*class\s*=\s*"review_attempt",\s*path\s*=\s*"'
            + re.escape(review_path)
            + r'",\s*commit\s*=\s*"[0-9a-f]{40}",\s*blob\s*=\s*"[0-9a-f]{40}"\s*\}'
        )
        replacement = (
            f'{{ class = "review_attempt", path = "{review_path}", '
            f'commit = "{commit}", blob = "{blob}" }}'
        )
        updated, count = pattern.subn(replacement, text, count=1)
        if count != 1:
            # Path-only legacy locator (negative control) stays untouched.
            return commit, blob
        board.write_text(updated)
        return commit, blob

    def install_done_predecessor(
        self, project: Path, *, path: str,
    ) -> tuple[str, str]:
        result_path = project / path
        result_path.parent.mkdir(parents=True, exist_ok=True)
        result_path.write_text("# predecessor result\n")
        commit, blob = self.git_identity_for(project, path)
        board = project / BOARD
        existing = board.read_text()
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
        board.write_text(existing.replace('[[cards]]\n', predecessor + '[[cards]]\n', 1))
        predecessor_card = project / "implementation/workstreams/sample-workstream/cards/M01-T03.md"
        predecessor_card.write_text("# predecessor Card\n")
        return commit, blob

    def test_ready_card_stale_dependency_fails_closed_before_launch(self) -> None:
        temp, project = self.copy_fixture()
        try:
            dependency_path = "implementation/workstreams/sample-workstream/results/M01-T03.md"
            commit, blob = self.install_done_predecessor(project, path=dependency_path)
            dependency = f"{dependency_path}@{commit}:{blob}"
            self.make_ready_card(project, dependencies=dependency)

            current = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((current.disposition, current.obligation), ("route", "execution_prep"))

            new_commit = "c" * 40
            new_blob = "d" * 40
            board = project / BOARD
            board.write_text(
                board.read_text()
                .replace(f'commit = "{commit}"', f'commit = "{new_commit}"')
                .replace(f'blob = "{blob}"', f'blob = "{new_blob}"')
            )
            (project / dependency_path).write_text("# materially changed predecessor result\n")

            stale = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((stale.disposition, stale.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("no longer matches the exact current DONE predecessor result", stale.reason)
        finally:
            temp.cleanup()

    def test_technical_contract_is_loaded_only_when_card_selects_it(self) -> None:
        temp, project = self.copy_fixture()
        try:
            contract = "contracts/sample-api.md"
            self.make_ready_card(project, technical_contract=contract)
            contract_path = project / contract
            contract_path.parent.mkdir(parents=True, exist_ok=True)
            contract_path.write_text("# Material API contract\n")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution_prep"))
            self.assertIn(f"project:{contract}", routed.read_set)
        finally:
            temp.cleanup()

    def test_jit_refinement_classification_separates_authority_layers(self) -> None:
        self.assertEqual(classify_jit_refinement("bounded_execution_detail")[0], "execution_prep")
        self.assertEqual(classify_jit_refinement("strategy")[0], "planning")
        self.assertEqual(classify_jit_refinement("product_or_global_intent")[0], "definition")
        self.assertEqual(classify_jit_refinement("missing_facts")[0], "research")
        with self.assertRaisesRegex(Exception, "unknown JIT"):
            classify_jit_refinement("runtime_model_missing")

    def test_new_managed_intent_routes_to_common_intake_without_board(self) -> None:
        for entry, subject in (
            ("new_managed_intent", "change"),
            ("new_issue", "issue"),
            ("new_feature", "feature"),
        ):
            with self.subTest(entry=entry):
                routed = select_route(FIXTURE, [MANIFEST], package_root=ROOT, entry=entry)
                self.assertEqual((routed.disposition, routed.obligation, routed.subject), ("route", "intake", subject))
                self.assertEqual(routed.owner_module, "workflow/INTAKE.md")
                self.assertEqual(routed.read_set, ("package:workflow/ROUTER.md", "project:PROJECT.md"))


    def install_intake(self, project: Path, content: str) -> None:
        workstream = project / MANIFEST
        original = workstream.read_text()
        workstream.write_text(original + '\n[intake]\nclass = "intake"\npath = "implementation/workstreams/sample-workstream/INTAKE.toml"\n')
        intake = project / "implementation/workstreams/sample-workstream/INTAKE.toml"
        intake.write_text(content)


    def install_state_record(self, project: Path, key: str, klass: str, filename: str, content: str) -> None:
        workstream = project / MANIFEST
        workstream.write_text(
            workstream.read_text()
            + f'\n[{key}]\nclass = "{klass}"\npath = "implementation/workstreams/sample-workstream/{filename}"\n'
        )
        record = project / f"implementation/workstreams/sample-workstream/{filename}"
        record.write_text(content)
        if key == "definition" and 'state = "green"' in content:
            req = project / RF012_REQ_PATH
            req.parent.mkdir(parents=True, exist_ok=True)
            if not req.exists():
                req.write_text(RF012_REQ_CONTENT)
            dec = project / RF012_DEC_PATH
            dec.parent.mkdir(parents=True, exist_ok=True)
            if not dec.exists():
                dec.write_text(RF012_DEC_CONTENT)
        if key == "planning":
            self._fixup_planning_snapshot(project)
        elif key == "plan_review":
            self._fixup_review_snapshot(project)

    @staticmethod
    def _ensure_git_repo(project: Path) -> None:
        if not (project / ".git").exists():
            subprocess.run(["git", "init", "-q", str(project)], check=True)
            subprocess.run(
                ["git", "-C", str(project), "config", "user.email", "fixture@example.invalid"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(project), "config", "user.name", "Fixture"], check=True
            )

    def _fixup_planning_snapshot(self, project: Path) -> None:
        """Bind frozen/approved fixture planning to a real Git snapshot.

        Existing routing fixtures use fake a*40 subjects with no Git history.
        RF012 explicit keys must match the freeze-time snapshot at the immutable
        subject commit, so materialize that snapshot (authority files +
        DEFINITION + plan) and rewrite the fake subject to the real commit/blob.
        Independent premiums follow the new subject; editorial premiums/base
        stay bound to the prior reviewed base. Draft and malformed records pass
        through because the router never proves them here.
        """
        path = project / "implementation/workstreams/sample-workstream/PLANNING.toml"
        try:
            data = tomllib.loads(path.read_bytes().decode("utf-8"))
        except (OSError, ValueError):
            return
        if data.get("state") not in {"frozen", "approved"}:
            return
        subject = data.get("subject")
        if not isinstance(subject, dict) or subject.get("commit") != "a" * 40:
            return
        definition_path = project / "implementation/workstreams/sample-workstream/DEFINITION.toml"
        if not definition_path.is_file():
            return
        old_blob = subject.get("blob", "")
        old_key = f"owner/repo@{'a' * 40}:planning/MASTER_PLAN.md@{old_blob}"
        self._ensure_git_repo(project)
        for rel, content in (
            (RF012_REQ_PATH, RF012_REQ_CONTENT),
            (RF012_DEC_PATH, RF012_DEC_CONTENT),
            (RF012_PLAN_PATH, RF012_PLAN_CONTENT),
        ):
            target = project / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.exists():
                target.write_text(content)
        definition_rel = "implementation/workstreams/sample-workstream/DEFINITION.toml"
        subprocess.run(["git", "-C", str(project), "add",
                        RF012_REQ_PATH, RF012_DEC_PATH, RF012_PLAN_PATH, definition_rel],
                       check=True)
        subprocess.run(["git", "-C", str(project), "commit", "-q", "-m", "rf012 planning snapshot"],
                       check=False, capture_output=True)
        commit = subprocess.run(["git", "-C", str(project), "rev-parse", "HEAD"],
                                check=True, capture_output=True, text=True).stdout.strip()
        blob = subprocess.run(["git", "-C", str(project), "rev-parse", f"HEAD:{RF012_PLAN_PATH}"],
                              check=True, capture_output=True, text=True).stdout.strip()
        new_key = f"{RF012_REPOSITORY}@{commit}:{RF012_PLAN_PATH}@{blob}"
        text = path.read_text()
        text = text.replace('repository = "owner/repo"', f'repository = "{RF012_REPOSITORY}"', 1)
        text = text.replace(f'commit = "{"a" * 40}"', f'commit = "{commit}"', 1)
        if isinstance(old_blob, str) and old_blob:
            text = text.replace(f'blob = "{old_blob}"', f'blob = "{blob}"', 1)
        if data.get("review_mode") != "editorial_exempt" and isinstance(old_blob, str) and old_blob:
            text = text.replace(old_key, new_key)
        path.write_text(text)
        if data.get("review_mode") == "editorial_exempt":
            self._fixup_editorial_classification(project, commit, blob, old_blob, data)

    def _fixup_editorial_classification(self, project: Path, commit: str, blob: str,
                                          old_blob: object, data: dict) -> None:
        """Rebind fixture editorial proof changed_subject to the fixed plan subject.

        The proof base stays bound to the prior fake reviewed base; only the
        changed side follows the new real subject, with the locator refreshed
        to the recommitted proof. Intentionally corrupted locators (negative
        controls) and missing proofs pass through for the router to reject.
        """
        locator = data.get("review_exemption_classification")
        if not isinstance(locator, dict):
            return
        loc_path = locator.get("path")
        loc_commit = locator.get("commit")
        loc_blob = locator.get("blob")
        if not isinstance(loc_path, str) or not loc_path:
            return
        target = project / loc_path
        if not target.is_file():
            return
        if isinstance(loc_commit, str) and isinstance(loc_blob, str):
            try:
                actual = subprocess.run(
                    ["git", "-C", str(project), "rev-parse", "--verify",
                     f"{loc_commit}:{loc_path}"],
                    capture_output=True, text=True, check=False, timeout=5,
                )
                if actual.returncode != 0 or actual.stdout.strip() != loc_blob:
                    return
            except (OSError, subprocess.SubprocessError):
                return
        try:
            text = target.read_text()
        except OSError:
            return
        parts = text.split("[changed_subject]\n", 1)
        if len(parts) != 2:
            return
        head, tail = parts
        tail = tail.replace('repository = "owner/repo"',
                            f'repository = "{RF012_REPOSITORY}"', 1)
        tail = tail.replace(f'commit = "{"a" * 40}"', f'commit = "{commit}"', 1)
        if isinstance(old_blob, str) and old_blob:
            tail = tail.replace(f'blob = "{old_blob}"', f'blob = "{blob}"', 1)
        target.write_text(head + "[changed_subject]\n" + tail)
        subprocess.run(["git", "-C", str(project), "add", loc_path], check=True)
        subprocess.run(["git", "-C", str(project), "commit", "-q", "-m",
                        "rf012 editorial proof rebind"], check=False, capture_output=True)
        new_commit = subprocess.run(
            ["git", "-C", str(project), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True).stdout.strip()
        new_blob = subprocess.run(
            ["git", "-C", str(project), "rev-parse", f"HEAD:{loc_path}"],
            check=True, capture_output=True, text=True).stdout.strip()
        planning_path = project / "implementation/workstreams/sample-workstream/PLANNING.toml"
        try:
            planning_text = planning_path.read_text()
        except OSError:
            return
        pieces = planning_text.split("[review_exemption_classification]\n", 1)
        if len(pieces) != 2:
            return
        phead, ptail = pieces
        if isinstance(loc_commit, str) and loc_commit:
            ptail = ptail.replace(f'commit = "{loc_commit}"', f'commit = "{new_commit}"', 1)
        if isinstance(loc_blob, str) and loc_blob:
            ptail = ptail.replace(f'blob = "{loc_blob}"', f'blob = "{new_blob}"', 1)
        planning_path.write_text(phead + "[review_exemption_classification]\n" + ptail)

    def _fixup_review_snapshot(self, project: Path) -> None:
        """Align default fixture review subjects with the fixed planning subject.

        Only the default fake a*40/b*40 independent subject is rewritten; an
        intentionally mismatched blob (negative control) and editorial base
        subjects pass through untouched.
        """
        path = project / "implementation/workstreams/sample-workstream/PLAN_REVIEW.toml"
        try:
            data = tomllib.loads(path.read_bytes().decode("utf-8"))
        except (OSError, ValueError):
            return
        subject = data.get("subject")
        if isinstance(subject, dict):
            if subject.get("commit") == "a" * 40 and subject.get("blob") == "b" * 40:
                planning_path = project / "implementation/workstreams/sample-workstream/PLANNING.toml"
                try:
                    planning = tomllib.loads(planning_path.read_bytes().decode("utf-8"))
                except (OSError, ValueError):
                    planning = None
                if planning is not None and planning.get("review_mode") != "editorial_exempt":
                    planned = planning.get("subject")
                    if isinstance(planned, dict):
                        text = path.read_text()
                        text = text.replace('repository = "owner/repo"',
                                            f'repository = "{planned.get("repository", RF012_REPOSITORY)}"', 1)
                        text = text.replace(f'commit = "{"a" * 40}"', f'commit = "{planned.get("commit", "")}"', 1)
                        text = text.replace(f'blob = "{"b" * 40}"', f'blob = "{planned.get("blob", "")}"', 1)
                        path.write_text(text)
        self._fixup_review_acceptance_identity(project)

    def _fixup_review_acceptance_identity(self, project: Path) -> None:
        """Bind default keyed fixture acceptance to its exact Git identity.

        H006: explicit-key Plan Review attempts require exact commit + blob
        acceptance identity. Only the default path-only requirements
        acceptance is bound to the real snapshot identity; custom paths,
        pre-declared identity (positive/negative controls) and keyless
        legacy attempts pass through untouched.
        """
        path = project / "implementation/workstreams/sample-workstream/PLAN_REVIEW.toml"
        try:
            data = tomllib.loads(path.read_bytes().decode("utf-8"))
        except (OSError, ValueError):
            return
        key = data.get("definition_authority_key", "")
        if not (isinstance(key, str) and key):
            return
        acceptance = data.get("acceptance")
        if not isinstance(acceptance, dict):
            return
        if acceptance.get("class") != "authority" or acceptance.get("path") != RF012_REQ_PATH:
            return
        if "commit" in acceptance or "blob" in acceptance:
            return
        try:
            commit = subprocess.run(
                ["git", "-C", str(project), "rev-parse", "HEAD"],
                capture_output=True, text=True, check=False, timeout=5,
            )
            blob = subprocess.run(
                ["git", "-C", str(project), "rev-parse", f"HEAD:{RF012_REQ_PATH}"],
                capture_output=True, text=True, check=False, timeout=5,
            )
        except (OSError, subprocess.SubprocessError):
            return
        if commit.returncode != 0 or blob.returncode != 0:
            return
        commit_sha, blob_sha = commit.stdout.strip(), blob.stdout.strip()
        if re.fullmatch(r"[0-9a-f]{40}", commit_sha) is None:
            return
        if re.fullmatch(r"[0-9a-f]{40}", blob_sha) is None:
            return
        try:
            text = path.read_text()
        except OSError:
            return
        anchor = '[acceptance]\nclass = "authority"\npath = "requirements/REQUIREMENTS.md"\n'
        if anchor not in text:
            return
        path.write_text(
            text.replace(
                anchor,
                anchor + f'commit = "{commit_sha}"\nblob = "{blob_sha}"\n',
                1,
            )
        )


    def install_green_definition(self, project: Path) -> None:
        self.install_state_record(project, "brainstorm", "brainstorm", "BRAINSTORM.toml", (
            'workstream_id = "sample-workstream"\n'
            'scope_id = "scope-plan"\n'
            'revision = 1\n'
            'state = "promoted"\n'
            'challenge_audit = "green"\n'
            'explicit_user_stop = false\n'
            'promotion_state = "authorized"\n'
            'promotion_subject = "scope-plan@1"\n'
        ))
        self.install_state_record(project, "definition", "definition", "DEFINITION.toml", (
            'workstream_id = "sample-workstream"\n'
            'source_scope_subject = "scope-plan@1"\n'
            'revision = "R1"\n'
            'state = "green"\n'
            'completeness_audit = "green"\n'
            'premium_a = "satisfied"\n'
            'decisions = [{ class = "authority", path = "decisions/ADR-001.md" }]\n'
            '[requirements]\nclass = "authority"\npath = "requirements/REQUIREMENTS.md"\n'
        ))

    def planning_content(
        self, *, state: str, premium_b: str = "not_due", premium_c: str = "not_due",
        cycle: int = 1, premium_a: str = "satisfied", premium_a_subject: str | None = None,
        revision: str = "P1", blob: str | None = None, gate_subject: str | None = None,
        review_mode: str = "independent", exemption_basis: str = "",
        exemption_base_subject: str = "",
        exemption_classification: tuple[str, str, str, str] | None = None,
        include_authority_key: bool = True, authority_key: str = RF012_KEY,
    ) -> str:
        blob = blob or ("b" * 40)
        premium_a_subject = premium_a_subject or f"definition:R1|planning-cycle:{cycle}"
        key = f"owner/repo@{'a' * 40}:planning/MASTER_PLAN.md@{blob}"
        gate_key = gate_subject or key
        frozen = state in {"frozen", "approved"}
        authority_line = (
            f'definition_authority_key = "{authority_key}"\n'
            if include_authority_key
            else ""
        )
        return (
            'workstream_id = "sample-workstream"\n'
            f'cycle = {cycle}\n'
            f'entry_subject = "definition:R1|planning-cycle:{cycle}"\n'
            f'revision = "{revision}"\n'
            f'state = "{state}"\n'
            f'planner_audit = "{"green" if frozen else "pending"}"\n'
            'plan_path = "planning/MASTER_PLAN.md"\n'
            f'review_mode = "{review_mode}"\n'
            f'review_exemption_basis = "{exemption_basis}"\n'
            f'review_exemption_base_subject = "{exemption_base_subject}"\n'
            f'premium_a = "{premium_a}"\n'
            f'premium_a_subject = "{premium_a_subject}"\n'
            f'premium_b = "{premium_b}"\n'
            f'premium_b_subject = "{gate_key if premium_b != "not_due" else ""}"\n'
            f'premium_c = "{premium_c}"\n'
            f'premium_c_subject = "{gate_key if premium_c != "not_due" else ""}"\n'
            f'{authority_line}'
            '[subject]\n'
            f'repository = "{"owner/repo" if frozen else ""}"\n'
            f'commit = "{"a" * 40 if frozen else ""}"\n'
            f'path = "{"planning/MASTER_PLAN.md" if frozen else ""}"\n'
            f'blob = "{blob if frozen else ""}"\n'
            + (
                (
                    '[review_exemption_classification]\n'
                    'class = "git_blob"\n'
                    f'repository = "{exemption_classification[0]}"\n'
                    f'commit = "{exemption_classification[1]}"\n'
                    f'path = "{exemption_classification[2]}"\n'
                    f'blob = "{exemption_classification[3]}"\n'
                )
                if exemption_classification is not None
                else ""
            )
        )

    def plan_review_content(
        self, verdict: str = "pending", *, blob: str | None = None,
        cycle: int = 1, revision: str = "P1", evidence: str | None = None,
        include_authority_key: bool = True, authority_key: str = RF012_KEY,
    ) -> str:
        blob = blob or ("b" * 40)
        if evidence is None:
            evidence = "" if verdict == "pending" else "evidence/plan-review-R01.md"
        authority_line = (
            f'definition_authority_key = "{authority_key}"\n'
            if include_authority_key
            else ""
        )
        return (
            'workstream_id = "sample-workstream"\n'
            f'plan_revision = "{revision}"\n'
            f'planning_cycle = {cycle}\n'
            'attempt = "R01"\n'
            f'verdict = "{verdict}"\n'
            f'evidence_path = "{evidence}"\n'
            f'{authority_line}'
            '[subject]\n'
            'class = "git_blob"\n'
            'repository = "owner/repo"\n'
            f'commit = "{"a" * 40}"\n'
            'path = "planning/MASTER_PLAN.md"\n'
            f'blob = "{blob}"\n'
            '[acceptance]\n'
            'class = "authority"\n'
            'path = "requirements/REQUIREMENTS.md"\n'
            '[independence]\n'
            'materially_produced_or_repaired_subject = false\n'
            'basis = "Fresh semantic review context."\n'
        )

    def tracker_content(self, state: str) -> str:
        issue = 7 if state == "linked" else 0
        candidates = "[7, 8]" if state == "ambiguous" else "[]"
        readback = {
            "discovery": "pending",
            "create_pending_readback": "uncertain",
            "linked": "verified",
            "ambiguous": "uncertain",
            "unavailable": "not_applicable",
        }[state]
        return (
            'workstream_id = "sample-workstream"\n'
            'provider = "github"\n'
            'repository = "owner/repo"\n'
            'dedup_key = "project-workflow:sample-workstream"\n'
            f'state = "{state}"\n'
            f'issue_number = {issue}\n'
            f'candidate_issue_numbers = {candidates}\n'
            f'readback_state = "{readback}"\n'
            'final_pr = 0\n'
        )

    def issue_research_content(self, subject: str) -> str:
        return (
            'state = "consumed"\n'
            'workstream_id = "sample-workstream"\n'
            'origin_role = "intake"\n'
            f'origin_subject = "{subject}"\n'
            'return_target = "intake"\n'
            'return_reconciliation = "applied"\n'
            'return_result = "evidence/intake-prior-art.md"\n'
            'finding = "Proportional issue-diagnosis prior art checked."\n'
            'limitations = "none"\n'
            'conflicts = "No material conflicts observed."\n'
            '[[sources]]\nclass = "official_upstream"\nstatus = "checked"\nweight = "primary"\n'
            '[[sources]]\nclass = "project_runtime"\nstatus = "checked"\nweight = "direct"\n'
            '[[sources]]\nclass = "tracker_discussion"\nstatus = "not_relevant"\nweight = "supporting"\n'
            '[[sources]]\nclass = "practitioner_community"\nstatus = "unavailable"\nweight = "supporting"\n'
        )

    def test_issue_diagnosis_requires_exact_consumed_prior_art_research(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_intake(project, (
                'workstream_id = "sample-workstream"\n'
                'kind = "issue"\n'
                'state = "active"\n'
                'diagnosis_revision = 2\n'
                'repair_subject = "repair:v2"\n'
                'diagnosis_prior_art_subject = ""\n'
                'diagnosis_prior_art_result = ""\n'
                'response_kind = "none"\n'
                'response_observed = false\n'
                'alignment_state = "pending"\n'
                'alignment_subject = ""\n'
                'micro_fix_candidate = false\n'
            ))
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "intake"))
            self.assertIn("prior-art Research", routed.reason)

            self.install_state_record(
                project, "research", "research", "RESEARCH.toml",
                self.issue_research_content("repair:v1"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "intake"))
            self.assertIn("exact current repair subject", routed.reason)

            research_path = project / "implementation/workstreams/sample-workstream/RESEARCH.toml"
            research_path.write_text(self.issue_research_content("repair:v2"))
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "intake"))
            self.assertIn("persist its exact subject/result binding", routed.reason)

            proof = self.prior_art_proof(project)
            intake_path = project / "implementation/workstreams/sample-workstream/INTAKE.toml"
            intake_path.write_text(
                intake_path.read_text().replace(
                    'diagnosis_prior_art_subject = ""\n'
                    'diagnosis_prior_art_result = ""\n',
                    'diagnosis_prior_art_subject = "repair:v2"\n'
                    'diagnosis_prior_art_result = "evidence/intake-prior-art.md"\n',
                )
                + proof
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("stop", "issue_alignment"))
        finally:
            temp.cleanup()

    def test_issue_without_post_diagnosis_response_is_real_alignment_stop(self) -> None:
        temp, project = self.copy_fixture()
        try:
            (project / RF009_RESEARCH).write_text(self.issue_research_content("repair:v1"))
            proof = self.prior_art_proof(project)
            self.install_intake(project, (
                'workstream_id = "sample-workstream"\n'
                'kind = "issue"\n'
                'state = "active"\n'
                'diagnosis_revision = 1\n'
                'repair_subject = "repair:v1"\n'
                'diagnosis_prior_art_subject = "repair:v1"\n'
                'diagnosis_prior_art_result = "evidence/intake-prior-art.md"\n'
                'response_kind = "none"\n'
                'response_observed = false\n'
                'alignment_state = "pending"\n'
                'alignment_subject = ""\n'
                'micro_fix_candidate = false\n'
                + proof
            ))
            self.install_state_record(
                project, "research", "research", "RESEARCH.toml",
                self.issue_research_content("repair:v1"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("stop", "issue_alignment"))
            self.assertEqual(routed.owner_module, "workflow/INTAKE.md")
            self.assertNotIn(f"project:{BOARD}", routed.read_set)
        finally:
            temp.cleanup()

    def test_issue_question_continues_alignment_without_authorizing_repair(self) -> None:
        temp, project = self.copy_fixture()
        try:
            (project / RF009_RESEARCH).write_text(self.issue_research_content("repair:v1"))
            proof = self.prior_art_proof(project)
            self.install_intake(project, (
                'workstream_id = "sample-workstream"\n'
                'kind = "issue"\n'
                'state = "active"\n'
                'diagnosis_revision = 1\n'
                'repair_subject = "repair:v1"\n'
                'diagnosis_prior_art_subject = "repair:v1"\n'
                'diagnosis_prior_art_result = "evidence/intake-prior-art.md"\n'
                'response_kind = "question"\n'
                'response_observed = true\n'
                'alignment_state = "pending"\n'
                'alignment_subject = ""\n'
                'micro_fix_candidate = false\n'
                + proof
            ))
            self.install_state_record(
                project, "research", "research", "RESEARCH.toml",
                self.issue_research_content("repair:v1"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "brainstorming"))
            self.assertEqual(routed.owner_module, "workflow/BRAINSTORMING.md")
            self.assertNotIn(f"project:{BOARD}", routed.read_set)
        finally:
            temp.cleanup()

    def test_later_brainstorming_research_does_not_erase_issue_diagnosis_prior_art(self) -> None:
        temp, project = self.copy_fixture()
        try:
            (project / RF009_RESEARCH).write_text(self.issue_research_content("repair:v2"))
            proof = self.prior_art_proof(project)
            self.install_intake(project, (
                'workstream_id = "sample-workstream"\n'
                'kind = "issue"\n'
                'state = "active"\n'
                'diagnosis_revision = 2\n'
                'repair_subject = "repair:v2"\n'
                'diagnosis_prior_art_subject = "repair:v2"\n'
                'diagnosis_prior_art_result = "evidence/intake-prior-art.md"\n'
                'response_kind = "question"\n'
                'response_observed = true\n'
                'alignment_state = "pending"\n'
                'alignment_subject = ""\n'
                'micro_fix_candidate = false\n'
                + proof
            ))
            later_research = (
                'state = "consumed"\n'
                'workstream_id = "sample-workstream"\n'
                'origin_role = "brainstorming"\n'
                'origin_subject = "repair:v2:question"\n'
                'return_target = "brainstorming"\n'
                'return_reconciliation = "applied"\n'
                'return_result = "evidence/brainstorm-followup.md"\n'
                'finding = "Follow-up fact checked."\n'
                'limitations = "none"\n'
                'conflicts = "No material conflicts observed."\n'
                '[[sources]]\nclass = "official_upstream"\nstatus = "checked"\nweight = "primary"\n'
                '[[sources]]\nclass = "project_runtime"\nstatus = "checked"\nweight = "direct"\n'
                '[[sources]]\nclass = "tracker_discussion"\nstatus = "not_relevant"\nweight = "supporting"\n'
                '[[sources]]\nclass = "practitioner_community"\nstatus = "unavailable"\nweight = "supporting"\n'
            )
            self.install_state_record(
                project, "research", "research", "RESEARCH.toml", later_research,
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "brainstorming"))
            self.assertNotIn("diagnosis prior-art Research", routed.reason)
        finally:
            temp.cleanup()


    def test_completed_authorized_issue_continues_to_existing_board(self) -> None:
        temp, project = self.copy_fixture()
        try:
            (project / RF009_RESEARCH).write_text(self.issue_research_content("repair:v2"))
            proof = self.prior_art_proof(project)
            self.install_intake(project, (
                'workstream_id = "sample-workstream"\n'
                'kind = "issue"\n'
                'state = "complete"\n'
                'diagnosis_revision = 2\n'
                'repair_subject = "repair:v2"\n'
                'diagnosis_prior_art_subject = "repair:v2"\n'
                'diagnosis_prior_art_result = "evidence/intake-prior-art.md"\n'
                'response_kind = "authorization"\n'
                'response_observed = true\n'
                'alignment_state = "authorized"\n'
                'alignment_subject = "repair:v2"\n'
                'micro_fix_candidate = true\n'
                + proof
            ))
            self.install_state_record(
                project, "research", "research", "RESEARCH.toml",
                self.issue_research_content("repair:v2"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
            self.assertIn("project:implementation/workstreams/sample-workstream/INTAKE.toml", routed.read_set)
            self.assertIn(f"project:{BOARD}", routed.read_set)
        finally:
            temp.cleanup()


    def test_completed_preboard_intake_routes_without_manufacturing_board(self) -> None:
        cases = (
            (
                'workstream_id = "sample-workstream"\n'
                'kind = "feature"\n'
                'state = "complete"\n'
                'diagnosis_revision = 0\n'
                'repair_subject = ""\n'
                'diagnosis_prior_art_subject = ""\n'
                'diagnosis_prior_art_result = ""\n'
                'response_kind = "none"\n'
                'response_observed = false\n'
                'alignment_state = "not_required"\n'
                'alignment_subject = ""\n'
                'micro_fix_candidate = false\n',
                ("route", "brainstorming"),
            ),
            (
                'workstream_id = "sample-workstream"\n'
                'kind = "issue"\n'
                'state = "complete"\n'
                'diagnosis_revision = 2\n'
                'repair_subject = "repair:v2"\n'
                'diagnosis_prior_art_subject = "repair:v2"\n'
                'diagnosis_prior_art_result = "evidence/intake-prior-art.md"\n'
                'response_kind = "authorization"\n'
                'response_observed = true\n'
                'alignment_state = "authorized"\n'
                'alignment_subject = "repair:v2"\n'
                'micro_fix_candidate = true\n',
                ("route", "execution_prep"),
            ),
        )
        for intake_content, expected in cases:
            temp, project = self.copy_fixture()
            try:
                if 'kind = "issue"' in intake_content:
                    (project / RF009_RESEARCH).write_text(
                        self.issue_research_content("repair:v2")
                    )
                    proof = self.prior_art_proof(project)
                    intake_content = intake_content + proof
                self.install_intake(project, intake_content)
                if 'kind = "issue"' in intake_content:
                    self.install_state_record(
                        project, "research", "research", "RESEARCH.toml",
                        self.issue_research_content("repair:v2"),
                    )
                workstream = project / MANIFEST
                text = workstream.read_text()
                text = text.replace(
                    '\n[task_board]\nclass = "task_board"\npath = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"\n',
                    '\n',
                )
                workstream.write_text(text)
                routed = select_route(project, [MANIFEST], package_root=ROOT)
                self.assertEqual((routed.disposition, routed.obligation), expected)
                self.assertNotIn(f"project:{BOARD}", routed.read_set)
            finally:
                temp.cleanup()

    def test_stale_issue_alignment_fails_closed_to_recovery(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_intake(project, (
                'workstream_id = "sample-workstream"\n'
                'kind = "issue"\n'
                'state = "complete"\n'
                'diagnosis_revision = 3\n'
                'repair_subject = "repair:v3"\n'
                'diagnosis_prior_art_subject = "repair:v3"\n'
                'diagnosis_prior_art_result = "evidence/intake-prior-art.md"\n'
                'response_kind = "authorization"\n'
                'response_observed = true\n'
                'alignment_state = "authorized"\n'
                'alignment_subject = "repair:v2"\n'
                'micro_fix_candidate = true\n'
            ))
            self.install_state_record(
                project, "research", "research", "RESEARCH.toml",
                self.issue_research_content("repair:v3"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
        finally:
            temp.cleanup()


    def test_active_and_completed_research_route_to_exact_owner(self) -> None:
        base = (
            'workstream_id = "sample-workstream"\n'
            'origin_role = "brainstorming"\n'
            'origin_subject = "scope-a@1"\n'
            'return_target = "brainstorming"\n'
            'return_reconciliation = "pending"\n'
            'return_result = ""\n'
            'finding = ""\n'
            'limitations = ""\n'
            'conflicts = ""\n'
            '[[sources]]\nclass = "official_upstream"\nstatus = "pending"\nweight = "primary"\n'
            '[[sources]]\nclass = "project_runtime"\nstatus = "pending"\nweight = "direct"\n'
            '[[sources]]\nclass = "tracker_discussion"\nstatus = "pending"\nweight = "supporting"\n'
            '[[sources]]\nclass = "practitioner_community"\nstatus = "pending"\nweight = "supporting"\n'
        )
        temp, project = self.copy_fixture()
        try:
            # RF003: Board-coupled workstream active Research now yields to
            # Board owning/result/continuation evaluation, so the lone
            # workstream positive uses the no-Board path (Task Board read
            # still excluded from the progressive-disclosure bound).
            self.remove_board_locator(project)
            self.install_state_record(project, "research", "research", "RESEARCH.toml", 'state = "active"\n' + base)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "research"))
            self.assertNotIn(f"project:{BOARD}", routed.read_set)
        finally:
            temp.cleanup()

        complete = (
            'state = "complete"\n'
            'workstream_id = "sample-workstream"\n'
            'origin_role = "brainstorming"\n'
            'origin_subject = "scope-a@1"\n'
            'return_target = "brainstorming"\n'
            'return_reconciliation = "pending"\n'
            'return_result = ""\n'
            'finding = "bounded finding"\n'
            'limitations = "none"\n'
            'conflicts = "No material conflicts observed."\n'
            '[[sources]]\nclass = "official_upstream"\nstatus = "checked"\nweight = "primary"\n'
            '[[sources]]\nclass = "project_runtime"\nstatus = "checked"\nweight = "direct"\n'
            '[[sources]]\nclass = "tracker_discussion"\nstatus = "not_relevant"\nweight = "supporting"\n'
            '[[sources]]\nclass = "practitioner_community"\nstatus = "unavailable"\nweight = "supporting"\n'
        )
        temp, project = self.copy_fixture()
        try:
            self.install_state_record(project, "brainstorm", "brainstorm", "BRAINSTORM.toml", (
                'workstream_id = "sample-workstream"\n'
                'scope_id = "scope-a"\n'
                'revision = 1\n'
                'state = "active"\n'
                'challenge_audit = "pending"\n'
                'explicit_user_stop = false\n'
                'promotion_state = "pending"\n'
                'promotion_subject = ""\n'
            ))
            self.install_state_record(project, "research", "research", "RESEARCH.toml", complete)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "brainstorming"))
            self.assertIn("reconciled", routed.reason)
        finally:
            temp.cleanup()

    def rf003_active_research_content(self, *, origin_role: str, origin_subject: str,
                                      return_target: str) -> str:
        return (
            'state = "active"\n'
            'workstream_id = "sample-workstream"\n'
            f'origin_role = "{origin_role}"\n'
            f'origin_subject = "{origin_subject}"\n'
            f'return_target = "{return_target}"\n'
            'return_reconciliation = "pending"\n'
            'return_result = ""\n'
            'finding = ""\n'
            'limitations = ""\n'
            'conflicts = ""\n'
            '[[sources]]\nclass = "official_upstream"\nstatus = "pending"\nweight = "primary"\n'
            '[[sources]]\nclass = "project_runtime"\nstatus = "pending"\nweight = "direct"\n'
            '[[sources]]\nclass = "tracker_discussion"\nstatus = "pending"\nweight = "supporting"\n'
            '[[sources]]\nclass = "practitioner_community"\nstatus = "pending"\nweight = "supporting"\n'
        )

    def test_rf003_a_active_research_yields_to_explicit_stop(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_state_record(
                project, "brainstorm", "brainstorm", "BRAINSTORM.toml",
                self.rf002_brainstorm_content(
                    state="promoted", promotion_state="authorized",
                    promotion_subject="scope-a@2", explicit_user_stop=True,
                ),
            )
            self.install_state_record(
                project, "research", "research", "RESEARCH.toml",
                self.rf003_active_research_content(
                    origin_role="brainstorming", origin_subject="scope-a@2",
                    return_target="brainstorming",
                ),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation), ("stop", "explicit_user_stop")
            )
            self.assertEqual(routed.subject, "scope-a@2")
            self.assertEqual(routed.owner_module, "workflow/BRAINSTORMING.md")
        finally:
            temp.cleanup()

    def test_rf003_b_active_unrelated_research_yields_to_intake_diagnosis(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_intake(project, (
                'workstream_id = "sample-workstream"\n'
                'kind = "issue"\n'
                'state = "active"\n'
                'diagnosis_revision = 2\n'
                'repair_subject = "repair:v2"\n'
                'diagnosis_prior_art_subject = ""\n'
                'diagnosis_prior_art_result = ""\n'
                'response_kind = "none"\n'
                'response_observed = false\n'
                'alignment_state = "pending"\n'
                'alignment_subject = ""\n'
                'micro_fix_candidate = false\n'
            ))
            self.install_state_record(
                project, "research", "research", "RESEARCH.toml",
                self.rf003_active_research_content(
                    origin_role="brainstorming", origin_subject="scope-a@1",
                    return_target="brainstorming",
                ),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "intake"))
            self.assertEqual(routed.subject, "repair:v2")
            self.assertIn("prior-art Research", routed.reason)
        finally:
            temp.cleanup()

    def test_rf003_c_active_research_yields_to_premium_a(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_state_record(
                project, "brainstorm", "brainstorm", "BRAINSTORM.toml",
                self.rf002_brainstorm_content(
                    state="promoted", promotion_state="authorized",
                    promotion_subject="scope-a@2",
                ),
            )
            self.install_state_record(
                project, "definition", "definition", "DEFINITION.toml",
                self.rf002_definition_green_content(premium_a="due"),
            )
            self.install_state_record(
                project, "research", "research", "RESEARCH.toml",
                self.rf003_active_research_content(
                    origin_role="definition", origin_subject="R1",
                    return_target="definition",
                ),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation), ("stop", "premium_A")
            )
            self.assertEqual(routed.subject, "R1")
            self.assertEqual(routed.owner_module, "workflow/DEFINITION.md")
        finally:
            temp.cleanup()

    def test_rf003_board_active_yields_to_result_review(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            self.install_board_research(project, state="active")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation), ("route", "review_freeze")
            )
            self.assertEqual(routed.subject, "M01-T04")
        finally:
            temp.cleanup()

    def test_rf003_board_active_yields_to_board_continuation(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_board_research(project, state="active")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation), ("route", "execution")
            )
            self.assertEqual(routed.subject, "M01-T04")
        finally:
            temp.cleanup()

    def test_rf003_board_lone_active_routes_research(self) -> None:
        temp, project = self.copy_fixture()
        try:
            board = project / BOARD
            board.write_text(
                'workstream_id = "sample-workstream"\n'
                'revision = 3\n'
                'cards = []\n'
                '\n[execution_ref]\n'
                'branch = "feat/sample-workstream"\n'
                '\n[research_obligation]\nclass = "research"\n'
                'path = "implementation/workstreams/sample-workstream/RESEARCH.toml"\n'
            )
            research = project / "implementation/workstreams/sample-workstream/RESEARCH.toml"
            research.write_text(
                'state = "active"\n'
                'workstream_id = "sample-workstream"\n'
                'origin_role = "execution"\n'
                'origin_subject = "M01-T04"\n'
                'return_target = "execution:M01-T04"\n'
                'return_reconciliation = "pending"\n'
                'return_result = ""\n'
                'finding = ""\n'
                'limitations = ""\n'
                'conflicts = ""\n'
                '[[sources]]\nclass = "official_upstream"\nstatus = "pending"\nweight = "primary"\n'
                '[[sources]]\nclass = "project_runtime"\nstatus = "pending"\nweight = "direct"\n'
                '[[sources]]\nclass = "tracker_discussion"\nstatus = "pending"\nweight = "supporting"\n'
                '[[sources]]\nclass = "practitioner_community"\nstatus = "pending"\nweight = "supporting"\n'
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "research"))
            self.assertEqual(routed.subject, "M01-T04")
        finally:
            temp.cleanup()

    def test_rf003_d_active_research_yields_to_premium_b(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(state="frozen", premium_b="due"),
            )
            self.install_state_record(
                project, "research", "research", "RESEARCH.toml",
                self.rf003_active_research_content(
                    origin_role="definition", origin_subject="R1",
                    return_target="definition",
                ),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation), ("stop", "premium_B")
            )
            self.assertIn("best-available", routed.reason)
        finally:
            temp.cleanup()

    def test_rf003_e_active_research_yields_to_plan_review_consumption(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(state="frozen", premium_b="satisfied"),
            )
            self.install_state_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.plan_review_content("green"),
            )
            self.install_state_record(
                project, "research", "research", "RESEARCH.toml",
                self.rf003_active_research_content(
                    origin_role="definition", origin_subject="R1",
                    return_target="definition",
                ),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "planning"))
            self.assertIn("consumed", routed.reason)
        finally:
            temp.cleanup()

    def test_rf003_f_active_research_yields_to_premium_c(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(
                    state="approved", premium_b="satisfied", premium_c="due"
                ),
            )
            self.install_state_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.plan_review_content("green"),
            )
            self.install_state_record(
                project, "research", "research", "RESEARCH.toml",
                self.rf003_active_research_content(
                    origin_role="definition", origin_subject="R1",
                    return_target="definition",
                ),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation), ("stop", "premium_C")
            )
            self.assertIn("lighter/cheaper", routed.reason)
        finally:
            temp.cleanup()

    def test_rf003_workstream_active_yields_to_board_result_review(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            self.install_state_record(
                project, "research", "research", "RESEARCH.toml",
                self.rf003_active_research_content(
                    origin_role="brainstorming", origin_subject="scope-a@1",
                    return_target="brainstorming",
                ),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation), ("route", "review_freeze")
            )
            self.assertEqual(routed.subject, "M01-T04")
        finally:
            temp.cleanup()

    def test_rf003_workstream_active_yields_to_ready_board_owner(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.make_ready_card(project)
            self.install_state_record(
                project, "research", "research", "RESEARCH.toml",
                self.rf003_active_research_content(
                    origin_role="brainstorming", origin_subject="scope-a@1",
                    return_target="brainstorming",
                ),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation), ("route", "execution_prep")
            )
            self.assertEqual(routed.subject, "M01-T04")
        finally:
            temp.cleanup()

    def test_rf003_workstream_lone_active_on_empty_board_routes_research(self) -> None:
        temp, project = self.copy_fixture()
        try:
            board = project / BOARD
            board.write_text(
                'workstream_id = "sample-workstream"\n'
                'revision = 3\n'
                'cards = []\n'
                '\n[execution_ref]\n'
                'branch = "feat/sample-workstream"\n'
            )
            self.install_state_record(
                project, "research", "research", "RESEARCH.toml",
                self.rf003_active_research_content(
                    origin_role="brainstorming", origin_subject="scope-a@1",
                    return_target="brainstorming",
                ),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "research"))
            self.assertEqual(routed.subject, "scope-a@1")
        finally:
            temp.cleanup()

    def test_brainstorming_requires_challenge_and_exact_definition_promotion(self) -> None:
        temp, project = self.copy_fixture()
        try:
            ready = (
                'workstream_id = "sample-workstream"\n'
                'scope_id = "scope-a"\n'
                'revision = 2\n'
                'state = "ready_for_definition"\n'
                'challenge_audit = "green"\n'
                'explicit_user_stop = false\n'
                'promotion_state = "pending"\n'
                'promotion_subject = ""\n'
            )
            self.install_state_record(project, "brainstorm", "brainstorm", "BRAINSTORM.toml", ready)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("stop", "definition_promotion"))
            self.assertEqual(routed.subject, "scope-a@2")
        finally:
            temp.cleanup()

        temp, project = self.copy_fixture()
        try:
            promoted = (
                'workstream_id = "sample-workstream"\n'
                'scope_id = "scope-a"\n'
                'revision = 2\n'
                'state = "promoted"\n'
                'challenge_audit = "green"\n'
                'explicit_user_stop = false\n'
                'promotion_state = "authorized"\n'
                'promotion_subject = "scope-a@2"\n'
            )
            self.install_state_record(project, "brainstorm", "brainstorm", "BRAINSTORM.toml", promoted)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "definition"))
        finally:
            temp.cleanup()

    def test_definition_green_stops_at_premium_a_before_planning(self) -> None:
        temp, project = self.copy_fixture()
        try:
            promoted = (
                'workstream_id = "sample-workstream"\n'
                'scope_id = "scope-a"\n'
                'revision = 2\n'
                'state = "promoted"\n'
                'challenge_audit = "green"\n'
                'explicit_user_stop = false\n'
                'promotion_state = "authorized"\n'
                'promotion_subject = "scope-a@2"\n'
            )
            self.install_state_record(project, "brainstorm", "brainstorm", "BRAINSTORM.toml", promoted)
            definition = (
                'workstream_id = "sample-workstream"\n'
                'source_scope_subject = "scope-a@2"\n'
                'revision = "R1"\n'
                'state = "green"\n'
                'completeness_audit = "green"\n'
                'premium_a = "due"\n'
                'decisions = [{ class = "authority", path = "decisions/ADR-001.md" }]\n'
                '[requirements]\nclass = "authority"\npath = "requirements/REQUIREMENTS.md"\n'
            )
            self.install_state_record(project, "definition", "definition", "DEFINITION.toml", definition)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("stop", "premium_A"))
            self.assertEqual(routed.owner_module, "workflow/DEFINITION.md")
            self.assertIn("best available model/context", routed.reason)
            self.assertIn("package:workflow/USER_STOP.md", routed.read_set)
        finally:
            temp.cleanup()

    def test_definition_source_mismatch_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            promoted = (
                'workstream_id = "sample-workstream"\n'
                'scope_id = "scope-a"\n'
                'revision = 2\n'
                'state = "promoted"\n'
                'challenge_audit = "green"\n'
                'explicit_user_stop = false\n'
                'promotion_state = "authorized"\n'
                'promotion_subject = "scope-a@2"\n'
            )
            self.install_state_record(project, "brainstorm", "brainstorm", "BRAINSTORM.toml", promoted)
            definition = (
                'workstream_id = "sample-workstream"\n'
                'source_scope_subject = "scope-a@1"\n'
                'revision = "R1"\n'
                'state = "active"\n'
                'completeness_audit = "pending"\n'
                'premium_a = "not_due"\n'
                'decisions = []\n'
                '[requirements]\nclass = "authority"\npath = "requirements/REQUIREMENTS.md"\n'
            )
            self.install_state_record(project, "definition", "definition", "DEFINITION.toml", definition)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
        finally:
            temp.cleanup()

    @staticmethod
    def rf002_brainstorm_content(
        *,
        scope_id: str = "scope-a",
        revision: int = 2,
        state: str,
        challenge_audit: str = "green",
        explicit_user_stop: bool = False,
        promotion_state: str,
        promotion_subject: str,
    ) -> str:
        stop = "true" if explicit_user_stop else "false"
        return (
            'workstream_id = "sample-workstream"\n'
            f'scope_id = "{scope_id}"\n'
            f"revision = {revision}\n"
            f'state = "{state}"\n'
            f'challenge_audit = "{challenge_audit}"\n'
            f"explicit_user_stop = {stop}\n"
            f'promotion_state = "{promotion_state}"\n'
            f'promotion_subject = "{promotion_subject}"\n'
        )

    @staticmethod
    def rf002_definition_content(*, source_scope_subject: str = "scope-a@2") -> str:
        return (
            'workstream_id = "sample-workstream"\n'
            f'source_scope_subject = "{source_scope_subject}"\n'
            'revision = "R1"\n'
            'state = "active"\n'
            'completeness_audit = "pending"\n'
            'premium_a = "not_due"\n'
            "decisions = []\n"
            '[requirements]\nclass = "authority"\npath = "requirements/REQUIREMENTS.md"\n'
        )

    @staticmethod
    def rf002_definition_green_content(*, premium_a: str = "satisfied") -> str:
        return (
            'workstream_id = "sample-workstream"\n'
            'source_scope_subject = "scope-a@2"\n'
            'revision = "R1"\n'
            'state = "green"\n'
            'completeness_audit = "green"\n'
            f'premium_a = "{premium_a}"\n'
            'decisions = [{ class = "authority", path = "decisions/ADR-001.md" }]\n'
            '[requirements]\nclass = "authority"\npath = "requirements/REQUIREMENTS.md"\n'
        )

    def test_rf002_b1_active_brainstorming_with_exact_authorization_cannot_enter_definition(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_state_record(
                project, "brainstorm", "brainstorm", "BRAINSTORM.toml",
                self.rf002_brainstorm_content(
                    state="active", promotion_state="authorized", promotion_subject="scope-a@2",
                ),
            )
            self.install_state_record(
                project, "definition", "definition", "DEFINITION.toml",
                self.rf002_definition_content(),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("promoted", routed.reason)
        finally:
            temp.cleanup()

    def test_rf002_b2_ready_brainstorming_with_exact_authorization_cannot_enter_definition(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_state_record(
                project, "brainstorm", "brainstorm", "BRAINSTORM.toml",
                self.rf002_brainstorm_content(
                    state="ready_for_definition", promotion_state="authorized",
                    promotion_subject="scope-a@2",
                ),
            )
            self.install_state_record(
                project, "definition", "definition", "DEFINITION.toml",
                self.rf002_definition_content(),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("promoted", routed.reason)
        finally:
            temp.cleanup()

    def test_rf002_ready_authorized_without_definition_record_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_state_record(
                project, "brainstorm", "brainstorm", "BRAINSTORM.toml",
                self.rf002_brainstorm_content(
                    state="ready_for_definition", promotion_state="authorized",
                    promotion_subject="scope-a@2",
                ),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("promoted", routed.reason)
        finally:
            temp.cleanup()

    def test_rf002_promoted_exact_authorized_definition_active_routes_definition(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_state_record(
                project, "brainstorm", "brainstorm", "BRAINSTORM.toml",
                self.rf002_brainstorm_content(
                    state="promoted", promotion_state="authorized", promotion_subject="scope-a@2",
                ),
            )
            self.install_state_record(
                project, "definition", "definition", "DEFINITION.toml",
                self.rf002_definition_content(),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "definition"))
            self.assertEqual(routed.subject, "scope-a@2")
            self.assertEqual(routed.owner_module, "workflow/DEFINITION.md")
        finally:
            temp.cleanup()

    def test_rf002_missing_authorization_with_definition_record_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_state_record(
                project, "brainstorm", "brainstorm", "BRAINSTORM.toml",
                self.rf002_brainstorm_content(
                    state="ready_for_definition", promotion_state="pending", promotion_subject="",
                ),
            )
            self.install_state_record(
                project, "definition", "definition", "DEFINITION.toml",
                self.rf002_definition_content(),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
        finally:
            temp.cleanup()

    def test_rf002_stale_promotion_with_definition_record_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_state_record(
                project, "brainstorm", "brainstorm", "BRAINSTORM.toml",
                self.rf002_brainstorm_content(
                    revision=3, state="ready_for_definition", promotion_state="authorized",
                    promotion_subject="scope-a@2",
                ),
            )
            self.install_state_record(
                project, "definition", "definition", "DEFINITION.toml",
                self.rf002_definition_content(source_scope_subject="scope-a@3"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("stale", routed.reason)
        finally:
            temp.cleanup()

    def test_rf002_cross_scope_definition_source_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_state_record(
                project, "brainstorm", "brainstorm", "BRAINSTORM.toml",
                self.rf002_brainstorm_content(
                    state="promoted", promotion_state="authorized", promotion_subject="scope-a@2",
                ),
            )
            self.install_state_record(
                project, "definition", "definition", "DEFINITION.toml",
                self.rf002_definition_content(source_scope_subject="scope-b@2"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
        finally:
            temp.cleanup()

    def test_rf002_active_brainstorming_without_definition_retains_owner_route(self) -> None:
        for promotion_state, promotion_subject in (
            ("pending", ""),
            ("authorized", "scope-a@2"),
        ):
            with self.subTest(promotion_state=promotion_state):
                temp, project = self.copy_fixture()
                try:
                    self.install_state_record(
                        project, "brainstorm", "brainstorm", "BRAINSTORM.toml",
                        self.rf002_brainstorm_content(
                            state="active", promotion_state=promotion_state,
                            promotion_subject=promotion_subject,
                        ),
                    )
                    routed = select_route(project, [MANIFEST], package_root=ROOT)
                    self.assertEqual((routed.disposition, routed.obligation), ("route", "brainstorming"))
                    self.assertEqual(routed.subject, "scope-a@2")
                finally:
                    temp.cleanup()


    def test_rf002_a1_promoted_stop_with_definition_active_returns_explicit_stop(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.remove_board_locator(project)
            self.install_state_record(
                project, "brainstorm", "brainstorm", "BRAINSTORM.toml",
                self.rf002_brainstorm_content(
                    state="promoted", promotion_state="authorized",
                    promotion_subject="scope-a@2", explicit_user_stop=True,
                ),
            )
            self.install_state_record(
                project, "definition", "definition", "DEFINITION.toml",
                self.rf002_definition_content(),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation), ("stop", "explicit_user_stop")
            )
            self.assertEqual(routed.subject, "scope-a@2")
            self.assertEqual(routed.owner_module, "workflow/BRAINSTORMING.md")
            self.assertIn("package:workflow/USER_STOP.md", routed.read_set)
        finally:
            temp.cleanup()

    def test_rf002_a2_promoted_stop_with_definition_green_a_due_returns_explicit_stop(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.remove_board_locator(project)
            self.install_state_record(
                project, "brainstorm", "brainstorm", "BRAINSTORM.toml",
                self.rf002_brainstorm_content(
                    state="promoted", promotion_state="authorized",
                    promotion_subject="scope-a@2", explicit_user_stop=True,
                ),
            )
            self.install_state_record(
                project, "definition", "definition", "DEFINITION.toml",
                self.rf002_definition_green_content(premium_a="due"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation), ("stop", "explicit_user_stop")
            )
            self.assertEqual(routed.subject, "scope-a@2")
            self.assertEqual(routed.owner_module, "workflow/BRAINSTORMING.md")
            self.assertIn("package:workflow/USER_STOP.md", routed.read_set)
        finally:
            temp.cleanup()

    def test_rf002_promoted_stop_persists_across_planning_branches(self) -> None:
        cases: list[tuple[str, str | None, str | None]] = [
            ("no_planning_record", None, None),
            ("draft_cycle", self.planning_content(state="draft"), None),
            (
                "material_reentry_a_due",
                self.planning_content(
                    state="draft", cycle=2, revision="P2", premium_a="due"
                ),
                None,
            ),
            (
                "frozen_b_due",
                self.planning_content(state="frozen", premium_b="due"),
                None,
            ),
            (
                "review_pending",
                self.planning_content(state="frozen", premium_b="satisfied"),
                self.plan_review_content("pending"),
            ),
            (
                "review_green",
                self.planning_content(state="frozen", premium_b="satisfied"),
                self.plan_review_content("green"),
            ),
            (
                "review_red",
                self.planning_content(state="frozen", premium_b="satisfied"),
                self.plan_review_content("red"),
            ),
            (
                "approved_c_due",
                self.planning_content(
                    state="approved", premium_b="satisfied", premium_c="due"
                ),
                self.plan_review_content("green"),
            ),
            (
                "approved_c_satisfied",
                self.planning_content(
                    state="approved", premium_b="satisfied", premium_c="satisfied"
                ),
                self.plan_review_content("green"),
            ),
        ]
        for label, planning_text, review_text in cases:
            with self.subTest(branch=label):
                temp, project = self.copy_fixture()
                try:
                    self.remove_board_locator(project)
                    self.install_state_record(
                        project, "brainstorm", "brainstorm", "BRAINSTORM.toml",
                        self.rf002_brainstorm_content(
                            state="promoted", promotion_state="authorized",
                            promotion_subject="scope-a@2", explicit_user_stop=True,
                        ),
                    )
                    self.install_state_record(
                        project, "definition", "definition", "DEFINITION.toml",
                        self.rf002_definition_green_content(premium_a="satisfied"),
                    )
                    if planning_text is not None:
                        self.install_state_record(
                            project, "planning", "planning", "PLANNING.toml", planning_text
                        )
                    if review_text is not None:
                        self.install_state_record(
                            project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                            review_text,
                        )
                    routed = select_route(project, [MANIFEST], package_root=ROOT)
                    self.assertEqual(
                        (routed.disposition, routed.obligation),
                        ("stop", "explicit_user_stop"),
                    )
                    self.assertEqual(routed.subject, "scope-a@2")
                    self.assertEqual(routed.owner_module, "workflow/BRAINSTORMING.md")
                    self.assertIn("package:workflow/USER_STOP.md", routed.read_set)
                finally:
                    temp.cleanup()

    def test_rf002_board_coupled_routes_preserve_parent_despite_stop(self) -> None:
        # RF002 stop precedence is pre-execution only: with a Task Board
        # locator and a Definition record, Board-coupled dispatch stays exactly
        # as on parent 9077fe8 even when explicit_user_stop is true.
        temp, project = self.copy_fixture()
        try:
            self.install_state_record(
                project, "brainstorm", "brainstorm", "BRAINSTORM.toml",
                self.rf002_brainstorm_content(
                    state="promoted", promotion_state="authorized",
                    promotion_subject="scope-a@2", explicit_user_stop=True,
                ),
            )
            self.install_state_record(
                project, "definition", "definition", "DEFINITION.toml",
                self.rf002_definition_green_content(premium_a="satisfied"),
            )
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(
                    state="approved", premium_b="satisfied", premium_c="satisfied"
                ),
            )
            self.install_state_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.plan_review_content("green"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
            self.assertEqual(routed.subject, "M01-T04")
            self.assertEqual(routed.owner_module, "workflow/EXECUTION.md")
            self.assertIn(f"project:{BOARD}", routed.read_set)
        finally:
            temp.cleanup()

        temp, project = self.copy_fixture()
        try:
            self.install_editorial_plan(project)
            brainstorm_path = (
                project / "implementation/workstreams/sample-workstream/BRAINSTORM.toml"
            )
            brainstorm_path.write_text(
                'workstream_id = "sample-workstream"\n'
                'scope_id = "scope-plan"\n'
                "revision = 1\n"
                'state = "promoted"\n'
                'challenge_audit = "green"\n'
                "explicit_user_stop = true\n"
                'promotion_state = "authorized"\n'
                'promotion_subject = "scope-plan@1"\n'
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
            self.assertEqual(routed.subject, "M01-T04")
            self.assertEqual(routed.owner_module, "workflow/EXECUTION.md")
            self.assertIn(f"project:{BOARD}", routed.read_set)
        finally:
            temp.cleanup()

    def test_rf002_stop_with_contradictory_binding_stays_recovery(self) -> None:
        cases = (
            (
                "stale_promotion",
                {"revision": 3, "state": "ready_for_definition",
                 "promotion_state": "authorized", "promotion_subject": "scope-a@2"},
                "scope-a@3",
            ),
            (
                "cross_scope_source",
                {"state": "promoted", "promotion_state": "authorized",
                 "promotion_subject": "scope-a@2"},
                "scope-b@2",
            ),
            (
                "pending_promotion",
                {"state": "ready_for_definition", "promotion_state": "pending",
                 "promotion_subject": ""},
                "scope-a@2",
            ),
        )
        for label, brainstorm_kwargs, definition_source in cases:
            with self.subTest(binding=label):
                temp, project = self.copy_fixture()
                try:
                    self.install_state_record(
                        project, "brainstorm", "brainstorm", "BRAINSTORM.toml",
                        self.rf002_brainstorm_content(
                            explicit_user_stop=True, **brainstorm_kwargs
                        ),
                    )
                    self.install_state_record(
                        project, "definition", "definition", "DEFINITION.toml",
                        self.rf002_definition_content(
                            source_scope_subject=definition_source
                        ),
                    )
                    routed = select_route(project, [MANIFEST], package_root=ROOT)
                    self.assertEqual(
                        (routed.disposition, routed.obligation),
                        ("recovery", "recovery_boundary"),
                    )
                finally:
                    temp.cleanup()

    def test_rf002_brainstorm_only_stop_retains_explicit_stop(self) -> None:
        for state, promotion_state, promotion_subject in (
            ("promoted", "authorized", "scope-a@2"),
            ("active", "pending", ""),
        ):
            with self.subTest(state=state):
                temp, project = self.copy_fixture()
                try:
                    self.install_state_record(
                        project, "brainstorm", "brainstorm", "BRAINSTORM.toml",
                        self.rf002_brainstorm_content(
                            state=state, promotion_state=promotion_state,
                            promotion_subject=promotion_subject,
                            explicit_user_stop=True,
                        ),
                    )
                    routed = select_route(project, [MANIFEST], package_root=ROOT)
                    self.assertEqual(
                        (routed.disposition, routed.obligation),
                        ("stop", "explicit_user_stop"),
                    )
                    self.assertEqual(routed.subject, "scope-a@2")
                    self.assertEqual(routed.owner_module, "workflow/BRAINSTORMING.md")
                    self.assertIn("package:workflow/USER_STOP.md", routed.read_set)
                finally:
                    temp.cleanup()

    def test_rf002_promoted_no_stop_planning_branches_keep_legal_routes(self) -> None:
        cases: list[
            tuple[str, str | None, str | None, tuple[str, str], str | None]
        ] = [
            ("no_planning_record", None, None, ("route", "planning"), "R1"),
            (
                "draft_cycle",
                self.planning_content(state="draft"),
                None,
                ("route", "planning"),
                "definition:R1|planning-cycle:1",
            ),
            (
                "material_reentry_a_due",
                self.planning_content(
                    state="draft", cycle=2, revision="P2", premium_a="due"
                ),
                None,
                ("stop", "premium_A"),
                "definition:R1|planning-cycle:2",
            ),
            (
                "frozen_b_due",
                self.planning_content(state="frozen", premium_b="due"),
                None,
                ("stop", "premium_B"),
                None,
            ),
            (
                "review_pending",
                self.planning_content(state="frozen", premium_b="satisfied"),
                self.plan_review_content("pending"),
                ("route", "plan_review"),
                None,
            ),
            (
                "approved_c_due",
                self.planning_content(
                    state="approved", premium_b="satisfied", premium_c="due"
                ),
                self.plan_review_content("green"),
                ("stop", "premium_C"),
                None,
            ),
        ]
        for label, planning_text, review_text, expected, subject in cases:
            with self.subTest(branch=label):
                temp, project = self.copy_fixture()
                try:
                    self.install_state_record(
                        project, "brainstorm", "brainstorm", "BRAINSTORM.toml",
                        self.rf002_brainstorm_content(
                            state="promoted", promotion_state="authorized",
                            promotion_subject="scope-a@2",
                        ),
                    )
                    self.install_state_record(
                        project, "definition", "definition", "DEFINITION.toml",
                        self.rf002_definition_green_content(premium_a="satisfied"),
                    )
                    if planning_text is not None:
                        self.install_state_record(
                            project, "planning", "planning", "PLANNING.toml", planning_text
                        )
                    if review_text is not None:
                        self.install_state_record(
                            project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                            review_text,
                        )
                    routed = select_route(project, [MANIFEST], package_root=ROOT)
                    self.assertEqual(
                        (routed.disposition, routed.obligation), expected
                    )
                    if subject is not None:
                        self.assertEqual(routed.subject, subject)
                finally:
                    temp.cleanup()

    def test_planning_routes_after_exact_premium_a_satisfaction(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "planning"))

            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(state="draft"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "planning"))
        finally:
            temp.cleanup()

    def test_frozen_plan_stops_at_b_then_routes_fresh_plan_review(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(state="frozen", premium_b="due"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("stop", "premium_B"))
            self.assertIn("best-available", routed.reason)
            self.assertIn("package:workflow/USER_STOP.md", routed.read_set)
        finally:
            temp.cleanup()

        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(state="frozen", premium_b="satisfied"),
            )
            self.install_state_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.plan_review_content("pending"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "plan_review"))
            self.assertEqual(routed.owner_module, "workflow/PLAN_REVIEW.md")
        finally:
            temp.cleanup()

    def test_green_plan_review_consumes_to_c_before_execution_prep(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(state="frozen", premium_b="satisfied"),
            )
            self.install_state_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.plan_review_content("green"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "planning"))
            self.assertIn("consumed", routed.reason)
        finally:
            temp.cleanup()

        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(state="approved", premium_b="satisfied", premium_c="due"),
            )
            self.install_state_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.plan_review_content("green"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("stop", "premium_C"))
            self.assertIn("lighter/cheaper", routed.reason)
            self.assertIn("package:workflow/USER_STOP.md", routed.read_set)
        finally:
            temp.cleanup()

        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(state="approved", premium_b="satisfied", premium_c="satisfied"),
            )
            self.install_state_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.plan_review_content("green"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            # Co-bound live Board takes precedence over plan JIT: fixture Board
            # holds M01-T04 in_progress without a result, so Execution owns it.
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
            self.assertEqual(routed.subject, "M01-T04")
            self.assertIn(f"project:{BOARD}", routed.read_set)
        finally:
            temp.cleanup()

    def test_material_replan_repeats_a_b_review_c_and_editorial_exemption_skips_new_review(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            planning_path = project / "implementation/workstreams/sample-workstream/PLANNING.toml"
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(state="draft", cycle=2, revision="P2", premium_a="due"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("stop", "premium_A"))
            self.assertEqual(routed.subject, "definition:R1|planning-cycle:2")
            self.assertIn("best available model/context", routed.reason)
            self.assertIn("package:workflow/USER_STOP.md", routed.read_set)

            planning_path.write_text(
                self.planning_content(state="draft", cycle=2, revision="P2", premium_a="satisfied")
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "planning"))

            planning_path.write_text(
                self.planning_content(
                    state="frozen", cycle=2, revision="P2",
                    premium_a="satisfied", premium_b="due",
                )
            )
            self._fixup_planning_snapshot(project)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("stop", "premium_B"))
            self.assertIn("package:workflow/USER_STOP.md", routed.read_set)

            planning_path.write_text(
                self.planning_content(
                    state="frozen", cycle=2, revision="P2",
                    premium_a="satisfied", premium_b="satisfied",
                )
            )
            self._fixup_planning_snapshot(project)
            self.install_state_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.plan_review_content("green", cycle=2, revision="P2"),
            )
            review_path = project / "implementation/workstreams/sample-workstream/PLAN_REVIEW.toml"
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "planning"))

            planning_path.write_text(
                self.planning_content(
                    state="approved", cycle=2, revision="P2",
                    premium_a="satisfied", premium_b="satisfied", premium_c="due",
                )
            )
            self._fixup_planning_snapshot(project)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("stop", "premium_C"))
            self.assertIn("package:workflow/USER_STOP.md", routed.read_set)

            planning_path.write_text(
                self.planning_content(
                    state="approved", cycle=2, revision="P2",
                    premium_a="satisfied", premium_b="satisfied", premium_c="satisfied",
                )
            )
            self._fixup_planning_snapshot(project)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            # Co-bound live Board preempts plan JIT; M01-T04 is in_progress.
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
            self.assertIn(f"project:{BOARD}", routed.read_set)

            base = f"owner/repo@{'a' * 40}:planning/MASTER_PLAN.md@{'b' * 40}"
            exemption_classification = self.install_editorial_classification(
                project, cycle=2, revision="P2"
            )
            planning_path.write_text(
                self.planning_content(
                    state="approved", cycle=2, revision="P2", blob="c" * 40,
                    premium_a="satisfied", premium_b="satisfied", premium_c="satisfied",
                    gate_subject=base, review_mode="editorial_exempt",
                    exemption_basis="Wording only; strategy, milestones, coverage and gates unchanged.",
                    exemption_base_subject=base,
                    exemption_classification=exemption_classification,
                )
            )
            self._fixup_planning_snapshot(project)
            review_path.write_text(self.plan_review_content("green", cycle=2, revision="P2"))
            self._fixup_review_snapshot(project)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            # Valid editorial exemption still dispatches the co-bound live Board.
            self.assertNotEqual(routed.disposition, "recovery", routed.reason)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
            self.assertEqual(routed.subject, "M01-T04")
            self.assertIn(f"project:{BOARD}", routed.read_set)
        finally:
            temp.cleanup()

    def test_editorial_basis_without_immutable_classification_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            base = f"owner/repo@{'a' * 40}:planning/MASTER_PLAN.md@{'b' * 40}"
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(
                    state="approved", cycle=2, revision="P2", blob="c" * 40,
                    premium_b="satisfied", premium_c="satisfied",
                    gate_subject=base, review_mode="editorial_exempt",
                    exemption_basis="wording only",
                    exemption_base_subject=base,
                ),
            )
            self.install_state_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.plan_review_content("green", cycle=2, revision="P2"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("classification", routed.reason)
        finally:
            temp.cleanup()

    def test_editorial_classification_wrong_blob_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            base = f"owner/repo@{'a' * 40}:planning/MASTER_PLAN.md@{'b' * 40}"
            proof = list(self.install_editorial_classification(
                project, cycle=2, revision="P2"
            ))
            proof[3] = "d" * 40
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(
                    state="approved", cycle=2, revision="P2", blob="c" * 40,
                    premium_b="satisfied", premium_c="satisfied",
                    gate_subject=base, review_mode="editorial_exempt",
                    exemption_basis="wording only",
                    exemption_base_subject=base,
                    exemption_classification=tuple(proof),
                ),
            )
            self.install_state_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.plan_review_content("green", cycle=2, revision="P2"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("blob does not match", routed.reason)
        finally:
            temp.cleanup()

    def test_stale_premium_cycle_and_wrong_review_subject_fail_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(
                    state="draft", cycle=2,
                    premium_a_subject="definition:R1|planning-cycle:1",
                ),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
        finally:
            temp.cleanup()

        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(state="frozen", premium_b="satisfied"),
            )
            self.install_state_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.plan_review_content("pending", blob="c" * 40),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
        finally:
            temp.cleanup()

    def test_premium_b_satisfied_without_plan_review_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(state="frozen", premium_b="satisfied"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
        finally:
            temp.cleanup()

    def test_frozen_plan_review_verdict_domain_is_exhaustive_and_fail_closed(self) -> None:
        # H007/RF005: frozen plan + satisfied B routes only pending/green/red,
        # each to its owning step; any other verdict fails closed to Recovery
        # and never acquires the RED-correction route through fallthrough.
        for verdict, expected, reason_part in (
            ("pending", ("route", "plan_review"), "independent Plan Review"),
            ("green", ("route", "planning"), "consumed"),
            ("red", ("route", "planning"), "correction classification"),
        ):
            temp, project = self.copy_fixture()
            try:
                self.install_green_definition(project)
                self.install_state_record(
                    project, "planning", "planning", "PLANNING.toml",
                    self.planning_content(state="frozen", premium_b="satisfied"),
                )
                self.install_state_record(
                    project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                    self.plan_review_content(verdict),
                )
                routed = select_route(project, [MANIFEST], package_root=ROOT)
                self.assertEqual((routed.disposition, routed.obligation), expected)
                self.assertIn(reason_part, routed.reason)
            finally:
                temp.cleanup()

        for verdict in ("in_progress", "deferred"):
            temp, project = self.copy_fixture()
            try:
                self.install_green_definition(project)
                self.install_state_record(
                    project, "planning", "planning", "PLANNING.toml",
                    self.planning_content(state="frozen", premium_b="satisfied"),
                )
                self.install_state_record(
                    project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                    self.plan_review_content(verdict, evidence=""),
                )
                routed = select_route(project, [MANIFEST], package_root=ROOT)
                self.assertEqual(
                    (routed.disposition, routed.obligation),
                    ("recovery", "recovery_boundary"),
                )
                self.assertNotIn("correction classification", routed.reason)
            finally:
                temp.cleanup()

    def install_editorial_classification(
        self,
        project: Path,
        *,
        cycle: int = 1,
        revision: str = "P1",
        base_blob: str = "b" * 40,
        changed_blob: str = "c" * 40,
    ) -> tuple[str, str, str, str]:
        path = (
            "implementation/workstreams/sample-workstream/"
            f"planning_classifications/{revision}-E01.toml"
        )
        target = project / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(
            'workstream_id = "sample-workstream"\n'
            f'planning_cycle = {cycle}\n'
            f'plan_revision = "{revision}"\n'
            'verdict = "green"\n'
            'classification = "editorial_only"\n'
            'inspected_diff_evidence = "Exact immutable old/new plan blobs were semantically compared; only editorial wording changed."\n'
            '[base_subject]\n'
            'class = "git_blob"\n'
            'repository = "owner/repo"\n'
            f'commit = "{"a" * 40}"\n'
            'path = "planning/MASTER_PLAN.md"\n'
            f'blob = "{base_blob}"\n'
            '[changed_subject]\n'
            'class = "git_blob"\n'
            'repository = "owner/repo"\n'
            f'commit = "{"a" * 40}"\n'
            'path = "planning/MASTER_PLAN.md"\n'
            f'blob = "{changed_blob}"\n'
            '[unchanged]\n'
            'strategy = true\n'
            'milestone_topology = true\n'
            'requirement_coverage = true\n'
            'gates = true\n'
            'acceptance_semantics = true\n'
            '[independence]\n'
            'materially_produced_or_repaired_changed_subject = false\n'
            'basis = "Fresh semantic classifier did not author or repair the changed subject."\n'
        )
        if not (project / ".git").exists():
            subprocess.run(["git", "init", "-q", str(project)], check=True)
            subprocess.run(["git", "-C", str(project), "config", "user.email", "fixture@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(project), "config", "user.name", "Fixture"], check=True)
        subprocess.run(["git", "-C", str(project), "add", path], check=True)
        subprocess.run(["git", "-C", str(project), "commit", "-q", "-m", f"fixture {revision} editorial proof"], check=True)
        commit = subprocess.run(
            ["git", "-C", str(project), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        blob = subprocess.run(
            ["git", "-C", str(project), "rev-parse", f"HEAD:{path}"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        return ("owner/router-fixture", commit, path, blob)

    def install_approved_plan(self, project: Path) -> None:
        self.install_green_definition(project)
        self.install_state_record(
            project, "planning", "planning", "PLANNING.toml",
            self.planning_content(state="approved", premium_b="satisfied", premium_c="satisfied"),
        )
        self.install_state_record(
            project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
            self.plan_review_content("green"),
        )

    def install_editorial_plan(self, project: Path) -> None:
        self.install_green_definition(project)
        base = f"owner/repo@{'a' * 40}:planning/MASTER_PLAN.md@{'b' * 40}"
        exemption_classification = self.install_editorial_classification(project)
        self.install_state_record(
            project, "planning", "planning", "PLANNING.toml",
            self.planning_content(
                state="approved", blob="c" * 40,
                premium_b="satisfied", premium_c="satisfied",
                gate_subject=base, review_mode="editorial_exempt",
                exemption_basis="Wording only; strategy, milestones, coverage and gates unchanged.",
                exemption_base_subject=base,
                exemption_classification=exemption_classification,
            ),
        )
        self.install_state_record(
            project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
            self.plan_review_content("green"),
        )

    def remove_board_locator(self, project: Path) -> None:
        workstream = project / MANIFEST
        text = workstream.read_text()
        text = text.replace(
            '\n[task_board]\nclass = "task_board"\npath = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"\n',
            '\n',
        )
        workstream.write_text(text)

    def test_approved_plan_with_live_board_dispatches_board_precedence(self) -> None:
        cases = (
            ("no_result", None, "none", ("route", "execution")),
            ("result_no_review", None, "none_result", ("route", "result_reconciliation")),
            ("pending", "pending", "required", ("route", "review")),
            ("green", "green", "required", ("route", "post_review_finalization")),
            ("red", "red", "required", ("route", "execution_resolution")),
        )
        for name, verdict, requirement, expected in cases:
            temp, project = self.copy_fixture()
            try:
                with self.subTest(case=name):
                    self.install_approved_plan(project)
                    if name != "no_result":
                        review_requirement = "none" if requirement == "none_result" else requirement
                        self.install_reviewable_result(project, review_requirement)
                        if verdict is not None:
                            self.add_review_attempt(project, verdict)
                    routed = select_route(project, [MANIFEST], package_root=ROOT)
                    self.assertEqual((routed.disposition, routed.obligation), expected)
                    self.assertEqual(routed.subject, "M01-T04")
                    self.assertIn(f"project:{BOARD}", routed.read_set)
                    if verdict == "red":
                        self.assertEqual(routed.owner_module, "workflow/RECOVERY.md")
            finally:
                temp.cleanup()

    def test_editorial_exempt_with_live_board_dispatches_board_precedence(self) -> None:
        for verdict, expected, owner in (
            (None, ("route", "execution"), "workflow/EXECUTION.md"),
            ("red", ("route", "execution_resolution"), "workflow/RECOVERY.md"),
        ):
            temp, project = self.copy_fixture()
            try:
                with self.subTest(verdict=verdict):
                    self.install_editorial_plan(project)
                    if verdict is not None:
                        self.install_reviewable_result(project, "required")
                        self.add_review_attempt(project, verdict)
                    routed = select_route(project, [MANIFEST], package_root=ROOT)
                    self.assertNotEqual(routed.disposition, "recovery", routed.reason)
                    self.assertEqual((routed.disposition, routed.obligation), expected)
                    self.assertEqual(routed.owner_module, owner)
                    self.assertEqual(routed.subject, "M01-T04")
                    self.assertIn(f"project:{BOARD}", routed.read_set)
            finally:
                temp.cleanup()

    def test_cobound_invalid_board_fails_closed(self) -> None:
        for plan in ("approved", "editorial"):
            temp, project = self.copy_fixture()
            try:
                with self.subTest(plan=plan):
                    if plan == "approved":
                        self.install_approved_plan(project)
                    else:
                        self.install_editorial_plan(project)
                    board = project / BOARD
                    board.write_text(board.read_text().replace(
                        'branch = "feat/sample-workstream"', 'branch = "feat/other"',
                    ))
                    routed = select_route(project, [MANIFEST], package_root=ROOT)
                    self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            finally:
                temp.cleanup()

    def test_approved_plan_with_seams_validates_cobound_board_decisions(self) -> None:
        seams = (
            '[[seams]]\n'
            'id = "BOOT-A"\n'
            'class = "required_seam"\n'
            'intent = "Review closure stays standalone."\n'
            '[[seams]]\n'
            'id = "helper-less-derivation"\n'
            'class = "preferred_seam"\n'
            'intent = "Helper-less derivation is its own outcome."\n'
        )
        preserved = (
            '[[seam_decisions]]\n'
            'seam_id = "BOOT-A"\n'
            'decision = "preserved"\n'
            '[[seam_decisions]]\n'
            'seam_id = "helper-less-derivation"\n'
            'decision = "preserved"\n'
        )
        merged_required = preserved.replace(
            'seam_id = "BOOT-A"\ndecision = "preserved"',
            'seam_id = "BOOT-A"\ndecision = "merged"',
        )
        cases = (
            ("valid", preserved, ("route", "execution"), None),
            ("required_merge", merged_required, ("recovery", "recovery_boundary"),
             "must not merge a required_seam"),
            ("missing_decision", "", ("recovery", "recovery_boundary"),
             "require durable per-seam JIT decisions"),
        )
        for name, decisions, expected, reason in cases:
            temp, project = self.copy_fixture()
            try:
                with self.subTest(case=name):
                    self.install_approved_plan(project)
                    planning = project / "implementation/workstreams/sample-workstream/PLANNING.toml"
                    planning.write_text(planning.read_text() + seams)
                    if decisions:
                        board = project / BOARD
                        board.write_text(board.read_text() + decisions)
                    routed = select_route(project, [MANIFEST], package_root=ROOT)
                    self.assertEqual((routed.disposition, routed.obligation), expected)
                    if reason is None:
                        self.assertEqual(routed.subject, "M01-T04")
                    else:
                        self.assertIn(reason, routed.reason)
                    self.assertIn(f"project:{BOARD}", routed.read_set)
            finally:
                temp.cleanup()

    def test_plan_gate_without_board_owns_plan_jit(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_approved_plan(project)
            self.remove_board_locator(project)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution_prep"))
            self.assertEqual(routed.owner_module, "workflow/EXECUTION_PREP.md")
            self.assertNotIn(f"project:{BOARD}", routed.read_set)
        finally:
            temp.cleanup()

        temp, project = self.copy_fixture()
        try:
            self.install_editorial_plan(project)
            self.remove_board_locator(project)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertNotEqual(routed.disposition, "recovery", routed.reason)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution_prep"))
            self.assertIn("Exact independent GREEN editorial-only classification", routed.reason)
            self.assertNotIn(f"project:{BOARD}", routed.read_set)
        finally:
            temp.cleanup()


    def test_tracker_discovery_and_pending_create_route_to_github_issues(self) -> None:
        for state, expected_reason in (
            ("discovery", "discovery/dedup"),
            ("create_pending_readback", "readback before any retry"),
        ):
            temp, project = self.copy_fixture()
            try:
                self.install_state_record(
                    project, "tracker", "tracker", "TRACKER.toml",
                    self.tracker_content(state),
                )
                routed = select_route(project, [MANIFEST], package_root=ROOT)
                self.assertEqual((routed.disposition, routed.obligation), ("route", "github_issues"))
                self.assertEqual(routed.owner_module, "workflow/GITHUB_ISSUES.md")
                self.assertIn(expected_reason, routed.reason)
                self.assertNotIn(f"project:{BOARD}", routed.read_set)
            finally:
                temp.cleanup()

    def test_tracker_ambiguity_fails_closed_without_duplicate_create(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_state_record(
                project, "tracker", "tracker", "TRACKER.toml",
                self.tracker_content("ambiguous"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("creating another tracker is forbidden", routed.reason)
        finally:
            temp.cleanup()

    def test_linked_or_unavailable_tracker_does_not_become_authority(self) -> None:
        for state in ("linked", "unavailable"):
            temp, project = self.copy_fixture()
            try:
                self.install_state_record(
                    project, "tracker", "tracker", "TRACKER.toml",
                    self.tracker_content(state),
                )
                routed = select_route(project, [MANIFEST], package_root=ROOT)
                self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
                self.assertIn(f"project:{BOARD}", routed.read_set)
            finally:
                temp.cleanup()

    def test_missing_or_ambiguous_selection_routes_to_recovery(self) -> None:
        for selected in ([], [MANIFEST, MANIFEST]):
            with self.subTest(selected=selected):
                routed = select_route(FIXTURE, selected, package_root=ROOT)
                self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
                self.assertIn("package:workflow/RECOVERY.md", routed.read_set)

    def test_invalid_binding_and_legacy_policy_fail_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            board = project / BOARD
            original = board.read_text()
            board.write_text(original.replace('branch = "feat/sample-workstream"', 'branch = "feat/other"'))
            self.assertEqual(select_route(project, [MANIFEST], package_root=ROOT).disposition, "recovery")

            board.write_text(original.replace("revision = 3", 'revision = 3\nexecution_policy = "chatgpt_only"'))
            self.assertEqual(select_route(project, [MANIFEST], package_root=ROOT).disposition, "recovery")
        finally:
            temp.cleanup()

    def test_missing_cross_workstream_and_escape_locators_fail_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            workstream = project / MANIFEST
            original = workstream.read_text()
            workstream.write_text(original.replace(
                "implementation/workstreams/sample-workstream/TASK_BOARD.toml",
                "implementation/workstreams/other/TASK_BOARD.toml",
            ))
            self.assertEqual(select_route(project, [MANIFEST], package_root=ROOT).disposition, "recovery")
            self.assertEqual(select_route(project, ["../outside.toml"], package_root=ROOT).disposition, "recovery")
        finally:
            temp.cleanup()

    def test_active_card_routes_to_runtime_neutral_execution(self) -> None:
        routed = select_route(FIXTURE, [MANIFEST], package_root=ROOT)
        self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
        self.assertIn("runtime-neutral implementation", routed.reason)
        self.assertNotEqual(routed.disposition, "real_stop")

    def test_durable_semantic_result_routes_to_reconciliation_without_replay(self) -> None:
        temp, project = self.copy_fixture()
        try:
            result_path = self.install_reviewable_result(project, "none")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "result_reconciliation"))
            self.assertIn("do not replay", routed.reason)
            self.assertIn(f"project:{result_path}", routed.read_set)
        finally:
            temp.cleanup()

    def result_version_content(self, *, subject: str) -> str:
        return (
            "# Card Result\n"
            "- Card ID: M01-T04\n"
            f"- Implementation subject: {subject}\n"
            "- Evidence refs: implementation/workstreams/sample-workstream/evidence/M01-T04.md\n"
            "- Tests/readback summary: GREEN\n"
            "- Result status: success\n"
        )

    def install_reviewable_result(self, project: Path, review_requirement: str) -> str:
        result_path = "implementation/workstreams/sample-workstream/results/M01-T04.md"
        (project / CARD).write_text(self.task_card_content(review_requirement=review_requirement))
        authority = project / "requirements" / "REQUIREMENTS.md"
        authority.parent.mkdir(parents=True, exist_ok=True)
        authority.write_text("# Accepted authority\n")
        evidence_dir = project / "implementation/workstreams/sample-workstream/evidence"
        evidence_dir.mkdir(parents=True, exist_ok=True)
        (evidence_dir / "M01-T04.md").write_text("# Verified evidence\n")
        result_file = project / result_path
        result_file.parent.mkdir(parents=True, exist_ok=True)
        result_file.write_text(
            self.result_version_content(subject="owner/repo@commit:" + ("a" * 40))
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

    def add_review_attempt(
        self,
        project: Path,
        verdict: str,
        attempt: str = "R01",
        *,
        review_kind: str | None = "discovery",
        source_discovery_attempt: str = "",
        discovery_complete: bool = False,
        finding_ids: tuple[str, ...] = (),
        defect_class_ids: tuple[str, ...] = (),
        failed_defect_class_ids: tuple[str, ...] = (),
        review_scope: str = "card",
        review_epoch: str = "E01",
        epoch_reset_basis: str = "",
        post_convergence_validation: bool = False,
        convergence_basis: str = "",
        subject_commit: str | None = None,
        subject_blob: str | None = None,
        acceptance_path: str = CARD,
        acceptance_commit_override: str | None = None,
        acceptance_blob_override: str | None = None,
        omit_acceptance_identity: bool = False,
    ) -> str:
        review_path = f"implementation/workstreams/sample-workstream/reviews/M01-T04-{attempt}.toml"
        path = project / review_path
        path.parent.mkdir(parents=True, exist_ok=True)
        evidence = "" if verdict in {"pending", "in_progress"} else f"implementation/workstreams/sample-workstream/evidence/review-{attempt}.md"
        if evidence:
            evidence_path = project / evidence
            evidence_path.parent.mkdir(parents=True, exist_ok=True)
            evidence_path.write_text("# Review evidence\n")
        board_commit, board_blob = self.board_result_identity(project)
        commit = subject_commit or board_commit
        blob = subject_blob or board_blob
        real_acceptance_commit, real_acceptance_blob = self.card_acceptance_identity(
            project, acceptance_path
        )
        acceptance_commit = acceptance_commit_override or real_acceptance_commit
        acceptance_blob = acceptance_blob_override or real_acceptance_blob
        extra = ""
        if review_kind == "discovery" and verdict in {"green", "red"}:
            discovery_complete = True
            if verdict == "red":
                if not finding_ids:
                    finding_ids = ("F-default",)
                if not defect_class_ids:
                    defect_class_ids = ("class-default",)
        if review_kind == "closure_verification" and not defect_class_ids:
            defect_class_ids = ("class-default",)
        if review_kind == "closure_verification" and verdict == "red" and not failed_defect_class_ids:
            failed_defect_class_ids = defect_class_ids
        if review_kind is not None:
            ids = ", ".join(f'"{item}"' for item in finding_ids)
            classes = ", ".join(f'"{item}"' for item in defect_class_ids)
            failed_classes = ", ".join(f'"{item}"' for item in failed_defect_class_ids)
            extra = (
                f'review_kind = "{review_kind}"\n'
                f'source_discovery_attempt = "{source_discovery_attempt}"\n'
                f'discovery_complete = {"true" if discovery_complete else "false"}\n'
                f'material_finding_ids = [{ids}]\n'
                f'review_scope = "{review_scope}"\n'
                f'review_epoch = "{review_epoch}"\n'
                f'epoch_reset_basis = "{epoch_reset_basis}"\n'
                f'material_defect_class_ids = [{classes}]\n'
                f'failed_material_defect_class_ids = [{failed_classes}]\n'
                f'post_convergence_validation = {"true" if post_convergence_validation else "false"}\n'
                f'convergence_basis = "{convergence_basis}"\n'
            )
            if review_kind == "discovery" and verdict == "red":
                for finding_id in finding_ids:
                    extra += (
                        "[[finding_severity]]\n"
                        f'id = "{finding_id}"\n'
                        'surface = "correctness"\n'
                        f'evidence = "{evidence}#{finding_id}"\n'
                    )
        if omit_acceptance_identity:
            acceptance_stanza = (
                '[acceptance]\n'
                'class = "task_card"\n'
                f'path = "{acceptance_path}"\n'
            )
        else:
            acceptance_stanza = (
                '[acceptance]\n'
                'class = "task_card"\n'
                f'path = "{acceptance_path}"\n'
                f'commit = "{acceptance_commit}"\n'
                f'blob = "{acceptance_blob}"\n'
            )
        path.write_text(
            'workstream_id = "sample-workstream"\n'
            'card_id = "M01-T04"\n'
            f'attempt = "{attempt}"\n'
            f'verdict = "{verdict}"\n'
            f'evidence_path = "{evidence}"\n'
            + extra
            + '[subject]\n'
            'class = "git_blob"\n'
            'repository = "owner/router-fixture"\n'
            f'commit = "{commit}"\n'
            'path = "implementation/workstreams/sample-workstream/results/M01-T04.md"\n'
            f'blob = "{blob}"\n'
            + acceptance_stanza
            + '[independence]\n'
            'materially_produced_or_repaired_subject = false\n'
            'basis = "Fresh semantic reviewer context."\n'
        )
        # RF006: Board review_attempt locators carry exact Git identity. Commit
        # the attempt file and bind its real (commit, blob) so the router can
        # prove immutable history through the shared RF007 resolver.
        attempt_commit, attempt_blob = self.git_identity_for(project, review_path)
        locator = (
            f'{{ class = "review_attempt", path = "{review_path}", '
            f'commit = "{attempt_commit}", blob = "{attempt_blob}" }}'
        )
        board = project / BOARD
        board_text = board.read_text()
        lines = board_text.splitlines()
        for index, line in enumerate(lines):
            if line.startswith("review_attempts = ["):
                existing = line.removeprefix("review_attempts = [").removesuffix("]")
                lines[index] = f"review_attempts = [{existing}, {locator}]"
                break
        else:
            board_text = board_text.replace(
                'status = "in_progress"\n',
                'status = "in_progress"\n'
                f'review_attempts = [{locator}]\n',
                1,
            )
            lines = board_text.splitlines()
        board.write_text("\n".join(lines) + "\n")
        return review_path

    def test_required_review_blocks_until_green_then_routes_finalization(self) -> None:
        for verdict, expected in (
            (None, "review_freeze"),
            ("pending", "review"),
            ("in_progress", "review"),
            ("green", "post_review_finalization"),
            ("red", "execution_resolution"),
        ):
            temp, project = self.copy_fixture()
            try:
                self.install_reviewable_result(project, "required")
                if verdict is not None:
                    self.add_review_attempt(project, verdict)
                routed = select_route(project, [MANIFEST], package_root=ROOT)
                self.assertEqual((routed.disposition, routed.obligation), ("route", expected))
            finally:
                temp.cleanup()

    def test_epoch_reset_rejects_unaccepted_authority_root_in_router(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            self.add_review_attempt(
                project,
                "red",
                "R01",
                finding_ids=("F1",),
                defect_class_ids=("class-a",),
            )
            review_path = self.add_review_attempt(
                project,
                "pending",
                "R02",
                review_epoch="E02",
                epoch_reset_basis="Claimed accepted redesign",
            )
            path = project / review_path
            text = path.read_text()
            text = text.replace(
                "[subject]\n",
                '[epoch_reset_subject]\n'
                'class = "accepted_redesign"\n'
                'repository = "owner/router-fixture"\n'
                f'commit = "{"c" * 40}"\n'
                'path = "requirements/UNACCEPTED_DRAFT.md"\n'
                f'blob = "{"d" * 40}"\n'
                "\n[subject]\n",
                1,
            )
            path.write_text(text)
            self.rebind_review_attempt(project, review_path)

            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("exact accepted authority", routed.reason)
        finally:
            temp.cleanup()

    def test_epoch_reset_rejects_fabricated_exact_accepted_subject(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            self.add_review_attempt(
                project,
                "red",
                "R01",
                finding_ids=("F1",),
                defect_class_ids=("class-a",),
            )
            review_path = self.add_review_attempt(
                project,
                "pending",
                "R02",
                review_epoch="E02",
                epoch_reset_basis="Claimed accepted redesign",
            )
            path = project / review_path
            text = path.read_text()
            text = text.replace(
                "[subject]\n",
                '[epoch_reset_subject]\n'
                'class = "accepted_redesign"\n'
                'repository = "owner/router-fixture"\n'
                f'commit = "{"c" * 40}"\n'
                f'path = "{CARD}"\n'
                f'blob = "{"d" * 40}"\n'
                "\n[subject]\n",
                1,
            )
            path.write_text(text)
            self.rebind_review_attempt(project, review_path)

            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("exact Git readback", routed.reason)
        finally:
            temp.cleanup()

    def test_preconvergence_closure_after_epoch_reset_fails_closed_in_router(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")

            source_path = self.add_review_attempt(
                project,
                "red",
                "R01",
                finding_ids=("F1",),
                defect_class_ids=("class-a",),
            )
            source = project / source_path
            source_lines = source.read_text().splitlines()
            convergence_prefixes = (
                "review_scope = ",
                "review_epoch = ",
                "epoch_reset_basis = ",
                "material_defect_class_ids = ",
                "failed_material_defect_class_ids = ",
                "post_convergence_validation = ",
                "convergence_basis = ",
            )
            source.write_text(
                "\n".join(
                    line for line in source_lines
                    if not line.startswith(convergence_prefixes)
                )
                + "\n"
            )
            self.rebind_review_attempt(project, source_path)

            self.add_review_attempt(
                project,
                "green",
                "R02",
                review_kind="closure_verification",
                source_discovery_attempt="R01",
                finding_ids=("F1",),
                defect_class_ids=("class-a",),
            )
            reset_path = self.add_review_attempt(
                project,
                "red",
                "R03",
                review_kind="closure_verification",
                source_discovery_attempt="R01",
                finding_ids=("F1",),
                defect_class_ids=("class-a",),
                failed_defect_class_ids=("class-a",),
                review_epoch="E02",
                epoch_reset_basis="Accepted Task Card redesign establishes E02.",
                subject_blob="e" * 40,
            )
            reset = project / reset_path
            board_commit, _ = self.board_result_identity(project)
            reset_text = reset.read_text().replace(
                f'commit = "{board_commit}"',
                f'commit = "{"c" * 40}"',
                1,
            )
            reset_text = reset_text.replace(
                "[subject]\n",
                '[epoch_reset_subject]\n'
                'class = "accepted_redesign"\n'
                'repository = "owner/router-fixture"\n'
                f'commit = "{"c" * 40}"\n'
                f'path = "{CARD}"\n'
                f'blob = "{"d" * 40}"\n'
                "\n[subject]\n",
                1,
            )
            reset.write_text(reset_text)
            self.rebind_review_attempt(project, reset_path)

            reset_blobs = {
                ("owner/router-fixture", "c" * 40, CARD): "d" * 40,
                ("owner/router-fixture", "a" * 40, CARD): "f" * 40,
            }
            with patch(
                "tools.router.project_git_blob_reader",
                return_value=lambda repository, commit, path: reset_blobs.get(
                    (repository, commit, path)
                ),
            ):
                routed = select_route(project, [MANIFEST], package_root=ROOT)

            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("initial convergence-aware epoch", routed.reason)
        finally:
            temp.cleanup()

    def test_active_legacy_shaped_review_attempt_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            self.add_review_attempt(project, "pending", review_kind=None)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("explicit review_kind", routed.reason)
        finally:
            temp.cleanup()

    def test_green_closure_requires_all_known_findings_before_fresh_discovery(self) -> None:
        temp, project = self.copy_fixture()
        try:
            result_path = self.install_reviewable_result(project, "required")
            self.add_review_attempt(
                project,
                "red",
                "R01",
                review_kind="discovery",
                discovery_complete=True,
                finding_ids=("F1", "F2"),
            )

            _, repaired_blob = self.commit_result_version(
                project, result_path,
                self.result_version_content(subject="repaired implementation v2"),
            )
            self.add_review_attempt(
                project,
                "green",
                "R02",
                review_kind="closure_verification",
                source_discovery_attempt="R01",
                finding_ids=("F1",),
                subject_blob=repaired_blob,
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "review_freeze"))
            self.assertIn("another closure-verification", routed.reason)

            self.add_review_attempt(
                project,
                "green",
                "R03",
                review_kind="closure_verification",
                source_discovery_attempt="R01",
                finding_ids=("F2",),
                subject_blob=repaired_blob,
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "review_freeze"))
            self.assertIn("fresh full-scope discovery", routed.reason)

            self.add_review_attempt(
                project,
                "green",
                "R04",
                review_kind="discovery",
                discovery_complete=True,
                finding_ids=(),
                subject_blob=repaired_blob,
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "post_review_finalization"),
            )
        finally:
            temp.cleanup()

    def test_fifth_new_card_defect_class_routes_review_convergence(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            for index in range(5):
                discovery_id = f"R{index * 2 + 1:02d}"
                self.add_review_attempt(
                    project,
                    "red",
                    discovery_id,
                    finding_ids=(f"F{index}",),
                    defect_class_ids=(f"class-{index}",),
                )
                if index < 4:
                    self.add_review_attempt(
                        project,
                        "green",
                        f"R{index * 2 + 2:02d}",
                        review_kind="closure_verification",
                        source_discovery_attempt=discovery_id,
                        finding_ids=(f"F{index}",),
                        defect_class_ids=(f"class-{index}",),
                    )

            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "review_convergence"))
            self.assertIn("ceiling", routed.reason)
        finally:
            temp.cleanup()

    def test_card_scope_mismatch_cannot_trigger_milestone_or_final_ceiling(self) -> None:
        for scope, discoveries in (("final", 3), ("milestone", 4)):
            with self.subTest(review_scope=scope):
                temp, project = self.copy_fixture()
                try:
                    self.install_reviewable_result(project, "required")
                    for index in range(discoveries):
                        discovery_id = f"R{index * 2 + 1:02d}"
                        self.add_review_attempt(
                            project,
                            "red",
                            discovery_id,
                            finding_ids=(f"F{index}",),
                            defect_class_ids=(f"class-{index}",),
                            review_scope=scope,
                        )
                        if index < discoveries - 1:
                            self.add_review_attempt(
                                project,
                                "green",
                                f"R{index * 2 + 2:02d}",
                                review_kind="closure_verification",
                                source_discovery_attempt=discovery_id,
                                finding_ids=(f"F{index}",),
                                defect_class_ids=(f"class-{index}",),
                                review_scope=scope,
                            )
                    routed = select_route(project, [MANIFEST], package_root=ROOT)
                    self.assertEqual(
                        (routed.disposition, routed.obligation),
                        ("recovery", "recovery_boundary"),
                    )
                    self.assertIn("expected", routed.reason)
                finally:
                    temp.cleanup()
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            for index in range(3):
                discovery_id = f"R{index * 2 + 1:02d}"
                self.add_review_attempt(
                    project,
                    "red",
                    discovery_id,
                    finding_ids=(f"F{index}",),
                    defect_class_ids=(f"class-{index}",),
                )
                if index < 2:
                    self.add_review_attempt(
                        project,
                        "green",
                        f"R{index * 2 + 2:02d}",
                        review_kind="closure_verification",
                        source_discovery_attempt=discovery_id,
                        finding_ids=(f"F{index}",),
                        defect_class_ids=(f"class-{index}",),
                    )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "execution_resolution"),
            )
        finally:
            temp.cleanup()

    def test_known_class_recurrence_does_not_consume_new_discovery_epoch(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            self.add_review_attempt(
                project, "red", "R01",
                finding_ids=("F1",), defect_class_ids=("class-a",),
            )
            self.add_review_attempt(
                project, "green", "R02",
                review_kind="closure_verification",
                source_discovery_attempt="R01",
                finding_ids=("F1",), defect_class_ids=("class-a",),
            )
            self.add_review_attempt(
                project, "red", "R03",
                finding_ids=("F2",), defect_class_ids=("class-a",),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution_resolution"))
        finally:
            temp.cleanup()

    def test_third_failed_closure_round_routes_review_convergence(self) -> None:
        temp, project = self.copy_fixture()
        try:
            result_path = self.install_reviewable_result(project, "required")
            self.add_review_attempt(
                project, "red", "R01",
                finding_ids=("F1",), defect_class_ids=("class-a",),
            )
            for attempt, version in (
                ("R02", "v2"),
                ("R03", "v3"),
                ("R04", "v4"),
            ):
                _, subject_blob = self.commit_result_version(
                    project, result_path,
                    self.result_version_content(subject=f"repair attempt {version}"),
                )
                self.add_review_attempt(
                    project,
                    "red",
                    attempt,
                    review_kind="closure_verification",
                    source_discovery_attempt="R01",
                    finding_ids=("F1",),
                    defect_class_ids=("class-a",),
                    subject_blob=subject_blob,
                )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "review_convergence"))
        finally:
            temp.cleanup()

    def test_repeated_red_closure_same_subject_does_not_consume_repair_rounds(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            self.add_review_attempt(
                project, "red", "R01",
                finding_ids=("F1",), defect_class_ids=("class-a",),
            )
            for attempt in ("R02", "R03", "R04"):
                self.add_review_attempt(
                    project,
                    "red",
                    attempt,
                    review_kind="closure_verification",
                    source_discovery_attempt="R01",
                    finding_ids=("F1",),
                    defect_class_ids=("class-a",),
                )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution_resolution"))
        finally:
            temp.cleanup()

    def test_convergence_closure_freezes_one_post_validation_and_red_routes_structural(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            for index in range(5):
                discovery_id = f"R{index * 2 + 1:02d}"
                finding = f"F{index}"
                defect = f"class-{index}"
                self.add_review_attempt(
                    project, "red", discovery_id,
                    finding_ids=(finding,), defect_class_ids=(defect,),
                )
                self.add_review_attempt(
                    project, "green", f"R{index * 2 + 2:02d}",
                    review_kind="closure_verification",
                    source_discovery_attempt=discovery_id,
                    finding_ids=(finding,), defect_class_ids=(defect,),
                )

            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "review_freeze"))
            self.assertIn("post-convergence", routed.reason)

            self.add_review_attempt(
                project,
                "red",
                "R11",
                finding_ids=("F-post",),
                defect_class_ids=("class-post",),
                post_convergence_validation=True,
                convergence_basis="Main convergence/root-cause analysis C01",
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "review_structural_resolution"),
            )
            self.assertIn("post-convergence", routed.reason)
        finally:
            temp.cleanup()

    def test_changed_result_after_terminal_review_requires_new_attempt(self) -> None:
        temp, project = self.copy_fixture()
        try:
            result_path = self.install_reviewable_result(project, "required")
            self.add_review_attempt(project, "green")
            self.commit_result_version(
                project, result_path,
                self.result_version_content(subject="changed implementation v2"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "review_freeze"))
            self.assertIn("changed", routed.reason)
        finally:
            temp.cleanup()

    def test_active_review_for_changed_result_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            result_path = self.install_reviewable_result(project, "required")
            self.add_review_attempt(project, "pending")
            self.commit_result_version(
                project, result_path,
                self.result_version_content(subject="changed implementation v2"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("stale", routed.reason)
        finally:
            temp.cleanup()

    def test_h005_exact_acceptance_green_finalizes(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            self.add_review_attempt(project, "green")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "post_review_finalization"),
            )
            self.assertIn("project-git:", "\n".join(routed.read_set))
        finally:
            temp.cleanup()

    def test_h005_alternate_same_stem_acceptance_cannot_finalize(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            alternate = "implementation/workstreams/sample-workstream/cards/archive/M01-T04.md"
            (project / alternate).parent.mkdir(parents=True, exist_ok=True)
            (project / alternate).write_text(
                self.task_card_content().replace(
                    "route only after current launch inputs are valid",
                    "ALTERNATE same-stem acceptance",
                )
            )
            self.add_review_attempt(project, "green", acceptance_path=alternate)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertNotEqual(routed.obligation, "post_review_finalization")
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("exact Card path", routed.reason)
        finally:
            temp.cleanup()

    def test_h005_same_path_mutated_acceptance_freezes_terminal(self) -> None:
        for committed in (False, True):
            temp, project = self.copy_fixture()
            try:
                with self.subTest(committed=committed):
                    self.install_reviewable_result(project, "required")
                    self.add_review_attempt(project, "green")
                    (project / CARD).write_text(
                        self.task_card_content(review_requirement="required").replace(
                            "route only after current launch inputs are valid",
                            "MUTATED acceptance content",
                        )
                    )
                    if committed:
                        self.git_identity_for(project, CARD)
                    routed = select_route(project, [MANIFEST], package_root=ROOT)
                    self.assertNotEqual(routed.obligation, "post_review_finalization")
                    self.assertEqual(
                        (routed.disposition, routed.obligation),
                        ("route", "review_freeze"),
                    )
                    self.assertIn("acceptance changed", routed.reason)
            finally:
                temp.cleanup()

    def test_h005_active_stale_acceptance_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            self.add_review_attempt(project, "pending")
            (project / CARD).write_text(
                self.task_card_content(review_requirement="required").replace(
                    "route only after current launch inputs are valid",
                    "MUTATED acceptance for active attempt",
                )
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("stale", routed.reason)
            self.assertIn("acceptance", routed.reason)
        finally:
            temp.cleanup()

    def test_h005_missing_sibling_mismatch_acceptance_fails_closed(self) -> None:
        # Missing identity is authored without commit/blob from the start so the
        # RF006 append-only freeze does not mask the H005 missing-identity reason.
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            self.add_review_attempt(project, "green", omit_acceptance_identity=True)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("exact commit + blob", routed.reason)
            self.assertNotIn("post_review_finalization", routed.obligation)
        finally:
            temp.cleanup()

        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            sibling = "implementation/workstreams/sample-workstream/cards/M01-T99.md"
            (project / sibling).write_text(
                self.task_card_content().replace("M01-T04", "M01-T99", 1)
            )
            self.add_review_attempt(project, "green", acceptance_path=sibling)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertNotEqual(routed.obligation, "post_review_finalization")
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("exact Card path", routed.reason)
        finally:
            temp.cleanup()

        for name, kwargs, reason in (
            ("blob_mismatch", {"acceptance_blob_override": "f" * 40}, "proof failed"),
            ("dangling", {"acceptance_commit_override": "0" * 40}, "proof failed"),
        ):
            temp, project = self.copy_fixture()
            try:
                with self.subTest(case=name):
                    self.install_reviewable_result(project, "required")
                    self.add_review_attempt(project, "green", **kwargs)  # type: ignore[arg-type]
                    routed = select_route(project, [MANIFEST], package_root=ROOT)
                    self.assertNotEqual(routed.obligation, "post_review_finalization")
                    self.assertEqual(
                        (routed.disposition, routed.obligation),
                        ("recovery", "recovery_boundary"),
                    )
                    self.assertIn(reason, routed.reason)
            finally:
                temp.cleanup()

    def test_h005_result_mismatch_freeze_preserved_with_exact_acceptance(self) -> None:
        temp, project = self.copy_fixture()
        try:
            result_path = self.install_reviewable_result(project, "required")
            self.add_review_attempt(project, "green")
            self.commit_result_version(
                project, result_path,
                self.result_version_content(subject="changed implementation v2"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "review_freeze"))
            self.assertIn("Current durable result changed", routed.reason)
        finally:
            temp.cleanup()

    def test_h005_off_head_acceptance_with_identical_bytes_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            _, card_blob = self.card_acceptance_identity(project, CARD)
            subprocess.run(
                ["git", "-C", str(project), "checkout", "-q", "-b", "h005-alt-accept"],
                check=True,
            )
            (project / "unrelated-alt.txt").write_text("alt\n")
            alt_commit, _ = self.git_identity_for(project, "unrelated-alt.txt")
            alt_blob = subprocess.run(
                ["git", "-C", str(project), "rev-parse", f"{alt_commit}:{CARD}"],
                check=True, capture_output=True, text=True,
            ).stdout.strip()
            self.assertEqual(alt_blob, card_blob)
            subprocess.run(["git", "-C", str(project), "checkout", "-q", "-"], check=True)
            ancestry = subprocess.run(
                ["git", "-C", str(project), "merge-base", "--is-ancestor", alt_commit, "HEAD"],
                capture_output=True, check=False,
            )
            self.assertNotEqual(ancestry.returncode, 0)
            self.add_review_attempt(
                project, "green",
                acceptance_commit_override=alt_commit,
                acceptance_blob_override=alt_blob,
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertNotEqual(routed.obligation, "post_review_finalization")
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("HEAD ancestry", routed.reason)
            self.assertIn("outside HEAD ancestry", routed.reason)
        finally:
            temp.cleanup()

    def test_h005_strict_ancestor_acceptance_commit_still_finalizes(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            self.add_review_attempt(project, "green")
            (project / "unrelated-note.txt").write_text("# Unrelated note\n")
            self.git_identity_for(project, "unrelated-note.txt")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("route", "post_review_finalization"),
            )
        finally:
            temp.cleanup()

    def install_h006_approved(self, project: Path) -> None:
        """Approved plan + GREEN review with fixup-bound exact acceptance."""
        self.install_green_definition(project)
        self.install_state_record(
            project, "planning", "planning", "PLANNING.toml",
            self.planning_content(
                state="approved", premium_b="satisfied", premium_c="satisfied"
            ),
        )
        self.install_state_record(
            project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
            self.plan_review_content("green"),
        )

    @staticmethod
    def plan_acceptance_identity(project: Path, relpath: str) -> tuple[str, str]:
        commit = subprocess.run(
            ["git", "-C", str(project), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        blob = subprocess.run(
            ["git", "-C", str(project), "rev-parse", f"HEAD:{relpath}"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        return commit, blob

    @staticmethod
    def rewrite_plan_review_acceptance(
        project: Path, *, path: str,
        commit: str | None = None, blob: str | None = None,
    ) -> None:
        review_path = project / "implementation/workstreams/sample-workstream/PLAN_REVIEW.toml"
        text = review_path.read_text()
        head, sep, tail = text.partition("[acceptance]\n")
        assert sep, "plan review fixture must carry an [acceptance] stanza"
        _, sep2, rest = tail.partition("[independence]\n")
        assert sep2, "plan review fixture must carry [independence] after [acceptance]"
        stanza = f'[acceptance]\nclass = "authority"\npath = "{path}"\n'
        if commit is not None or blob is not None:
            assert commit is not None and blob is not None
            stanza += f'commit = "{commit}"\nblob = "{blob}"\n'
        review_path.write_text(head + stanza + "[independence]\n" + rest)

    def test_h006_unrelated_router_acceptance_green_cannot_consume(self) -> None:
        # Headline RED-before/GREEN-after: unrelated workflow/ROUTER.md GREEN
        # consumed identically to the Definition baseline before H006.
        temp, project = self.copy_fixture()
        try:
            self.install_h006_approved(project)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
            self.assertIn("project-git:", "\n".join(routed.read_set))
            self.rewrite_plan_review_acceptance(project, path="workflow/ROUTER.md")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("unrelated", routed.reason)
            self.assertIn("exact current Definition authority", routed.reason)
        finally:
            temp.cleanup()

    def test_h006_exact_requirements_and_decisions_green_consume(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_h006_approved(project)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
            commit, blob = self.plan_acceptance_identity(project, RF012_DEC_PATH)
            self.rewrite_plan_review_acceptance(
                project, path=RF012_DEC_PATH, commit=commit, blob=blob
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
            self.assertIn("project-git:", "\n".join(routed.read_set))
        finally:
            temp.cleanup()

    def test_h006_sibling_acceptance_with_valid_identity_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_h006_approved(project)
            sibling = "decisions/ADR-002.md"
            (project / sibling).write_text("# Sibling decision\n")
            subprocess.run(["git", "-C", str(project), "add", sibling], check=True)
            subprocess.run(
                ["git", "-C", str(project), "commit", "-q", "-m", "h006 sibling"],
                check=True,
            )
            commit, blob = self.plan_acceptance_identity(project, sibling)
            self.rewrite_plan_review_acceptance(
                project, path=sibling, commit=commit, blob=blob
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("unrelated", routed.reason)
        finally:
            temp.cleanup()

    def test_h006_missing_identity_for_explicit_key_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_h006_approved(project)
            self.rewrite_plan_review_acceptance(project, path=RF012_REQ_PATH)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("exact commit + blob", routed.reason)
        finally:
            temp.cleanup()

    def test_h006_mismatched_identity_fails_closed(self) -> None:
        for name, kwargs, reason in (
            ("blob_mismatch", {"blob": "f" * 40}, "proof failed"),
            ("dangling", {"commit": "0" * 40}, "proof failed"),
        ):
            temp, project = self.copy_fixture()
            try:
                with self.subTest(case=name):
                    self.install_h006_approved(project)
                    commit, blob = self.plan_acceptance_identity(project, RF012_REQ_PATH)
                    if "commit" in kwargs:
                        commit = kwargs["commit"]  # type: ignore[typeddict-item]
                    if "blob" in kwargs:
                        blob = kwargs["blob"]  # type: ignore[typeddict-item]
                    self.rewrite_plan_review_acceptance(
                        project, path=RF012_REQ_PATH, commit=commit, blob=blob
                    )
                    routed = select_route(project, [MANIFEST], package_root=ROOT)
                    self.assertEqual(
                        (routed.disposition, routed.obligation),
                        ("recovery", "recovery_boundary"),
                    )
                    self.assertIn(reason, routed.reason)
            finally:
                temp.cleanup()

    def test_h006_off_head_acceptance_with_identical_bytes_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_h006_approved(project)
            _, req_blob = self.plan_acceptance_identity(project, RF012_REQ_PATH)
            subprocess.run(
                ["git", "-C", str(project), "checkout", "-q", "-b", "h006-alt-accept"],
                check=True,
            )
            (project / "unrelated-alt.txt").write_text("alt\n")
            subprocess.run(["git", "-C", str(project), "add", "unrelated-alt.txt"], check=True)
            subprocess.run(
                ["git", "-C", str(project), "commit", "-q", "-m", "h006 alt"],
                check=True,
            )
            alt_commit = subprocess.run(
                ["git", "-C", str(project), "rev-parse", "HEAD"],
                check=True, capture_output=True, text=True,
            ).stdout.strip()
            alt_blob = subprocess.run(
                ["git", "-C", str(project), "rev-parse", f"{alt_commit}:{RF012_REQ_PATH}"],
                check=True, capture_output=True, text=True,
            ).stdout.strip()
            self.assertEqual(alt_blob, req_blob)
            subprocess.run(["git", "-C", str(project), "checkout", "-q", "-"], check=True)
            ancestry = subprocess.run(
                ["git", "-C", str(project), "merge-base", "--is-ancestor", alt_commit, "HEAD"],
                capture_output=True, check=False,
            )
            self.assertNotEqual(ancestry.returncode, 0)
            self.rewrite_plan_review_acceptance(
                project, path=RF012_REQ_PATH, commit=alt_commit, blob=alt_blob
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("HEAD ancestry", routed.reason)
        finally:
            temp.cleanup()

    def test_h006_stale_and_changed_authority_fail_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_h006_approved(project)
            (project / RF012_REQ_PATH).write_text("# Mutated requirements bytes\n")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("stale", routed.reason)
        finally:
            temp.cleanup()

        temp, project = self.copy_fixture()
        try:
            self.install_h006_approved(project)
            definition_path = project / "implementation/workstreams/sample-workstream/DEFINITION.toml"
            definition_path.write_text(
                definition_path.read_text().replace('revision = "R1"', 'revision = "R2"')
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("stale", routed.reason)
        finally:
            temp.cleanup()

    def test_h006_pending_unrelated_acceptance_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(state="frozen", premium_b="satisfied"),
            )
            self.install_state_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.plan_review_content("pending"),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "plan_review"))
            self.rewrite_plan_review_acceptance(project, path="workflow/ROUTER.md")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("unrelated", routed.reason)
        finally:
            temp.cleanup()

    def test_h006_keyless_legacy_exact_valid_but_unrelated_fails(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_green_definition(project)
            self.install_state_record(
                project, "planning", "planning", "PLANNING.toml",
                self.planning_content(
                    state="approved", premium_b="satisfied", premium_c="satisfied",
                    include_authority_key=False,
                ),
            )
            self.install_state_record(
                project, "plan_review", "plan_review", "PLAN_REVIEW.toml",
                self.plan_review_content("green", include_authority_key=False),
            )
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))
            self.rewrite_plan_review_acceptance(project, path="workflow/ROUTER.md")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual(
                (routed.disposition, routed.obligation),
                ("recovery", "recovery_boundary"),
            )
            self.assertIn("unrelated", routed.reason)
        finally:
            temp.cleanup()

    def install_board_research(self, project: Path, *, state: str, reconciliation: str = "pending") -> None:
        board = project / BOARD
        board.write_text(
            board.read_text()
            + '\n[research_obligation]\nclass = "research"\n'
            + 'path = "implementation/workstreams/sample-workstream/RESEARCH.toml"\n'
        )
        result = "" if reconciliation == "pending" else "implementation/workstreams/sample-workstream/evidence/research-return.md"
        research = project / "implementation/workstreams/sample-workstream/RESEARCH.toml"
        research.write_text(
            f'state = "{state}"\n'
            'workstream_id = "sample-workstream"\n'
            'origin_role = "execution_resolution"\n'
            'origin_subject = "M01-T04"\n'
            'return_target = "execution_resolution:M01-T04"\n'
            f'return_reconciliation = "{reconciliation}"\n'
            f'return_result = "{result}"\n'
            'finding = "Recovered exact evidence."\n'
            'limitations = "none"\n'
            'conflicts = "none"\n'
            '[[sources]]\nclass = "official_upstream"\nstatus = "not_relevant"\nweight = "primary"\n'
            '[[sources]]\nclass = "project_runtime"\nstatus = "checked"\nweight = "direct"\n'
            '[[sources]]\nclass = "tracker_discussion"\nstatus = "not_relevant"\nweight = "supporting"\n'
            '[[sources]]\nclass = "practitioner_community"\nstatus = "not_relevant"\nweight = "supporting"\n'
        )

    def test_task_board_research_return_is_recovered_before_execution(self) -> None:
        # RF003: exact complete/cleanup returns still precede Board
        # continuation, but generic active dispatch no longer preempts the
        # active Card's execution obligation (see test_rf003_board_active_*).
        for state, reconciliation, expected in (
            ("active", "pending", "execution"),
            ("complete", "pending", "execution_resolution"),
            ("complete", "applied", "execution_resolution"),
            ("consumed", "applied", "research_cleanup"),
        ):
            temp, project = self.copy_fixture()
            try:
                self.install_board_research(project, state=state, reconciliation=reconciliation)
                routed = select_route(project, [MANIFEST], package_root=ROOT)
                self.assertEqual((routed.disposition, routed.obligation), ("route", expected))
            finally:
                temp.cleanup()

    def install_blocker(self, project: Path, blocker_class: str) -> None:
        blocker_path = "implementation/workstreams/sample-workstream/blockers/M01-T04.toml"
        board = project / BOARD
        board.write_text(
            board.read_text()
            .replace('status = "in_progress"', 'status = "blocked"', 1)
            .replace(
                '[cards.contract]\n',
                f'[cards.blocker]\nclass = "blocker"\npath = "{blocker_path}"\n\n[cards.contract]\n',
                1,
            )
        )
        path = project / blocker_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            'workstream_id = "sample-workstream"\n'
            'card_id = "M01-T04"\n'
            f'class = "{blocker_class}"\n'
            'summary = "Exact blocker."\n'
            'evidence_path = ""\n'
        )

    def test_blocker_classification_does_not_turn_every_blocker_into_user_stop(self) -> None:
        for blocker_class, expected_disposition, expected_obligation in (
            ("missing_evidence", "route", "research_handoff"),
            ("human_authority", "stop", "user_stop"),
            ("runtime_access_input", "stop", "blocker_stop"),
        ):
            temp, project = self.copy_fixture()
            try:
                self.install_blocker(project, blocker_class)
                routed = select_route(project, [MANIFEST], package_root=ROOT)
                self.assertEqual(
                    (routed.disposition, routed.obligation),
                    (expected_disposition, expected_obligation),
                )
            finally:
                temp.cleanup()

    def test_all_terminal_cards_route_to_close_not_directly_to_stop(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "none")
            board = project / BOARD
            board.write_text(board.read_text().replace('status = "in_progress"', 'status = "done"', 1))
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "close"))
            self.assertEqual(routed.owner_module, "workflow/CLOSE.md")
            self.assertIn("decides whether approved scope is durably complete", routed.reason)
            self.assertNotIn("package:workflow/FORK_RELEASE_VERSIONING.md", routed.read_set)
        finally:
            temp.cleanup()

    def test_priority_and_real_stop_foundations_are_runtime_neutral(self) -> None:
        self.assertEqual(
            PRIORITY_FOUNDATION,
            (
                "explicit_human_or_premium_boundary",
                "independent_review_or_red_correction",
                "research_return",
                "result_reconciliation",
                "current_card",
                "next_legal_stage",
            ),
        )
        self.assertIn("premium_gate", REAL_STOP_FOUNDATION)
        self.assertIn("independence_boundary", REAL_STOP_FOUNDATION)
        combined = " ".join(PRIORITY_FOUNDATION + REAL_STOP_FOUNDATION)
        for forbidden in ("chatgpt", "codex", "model_id", "session_id", "worker_id"):
            self.assertNotIn(forbidden, combined)

    def test_malformed_board_and_workstream_route_to_recovery(self) -> None:
        """RF017/H030: malformed Board/Workstream TOML routes Recovery without a parser leak."""
        for target in (MANIFEST, BOARD):
            temp, project = self.copy_fixture()
            try:
                path = project / target
                before = path.read_text()
                path.write_text(before + "\nrevision = [\n")
                routed = select_route(project, [MANIFEST], package_root=ROOT)
                self.assertEqual(
                    (routed.disposition, routed.obligation),
                    ("recovery", "recovery_boundary"),
                    msg=f"malformed {target} must fail closed",
                )
                self.assertIn("malformed TOML", routed.reason)
                self.assertIn(target, routed.reason)
                self.assertEqual(path.read_text(), before + "\nrevision = [\n")
            finally:
                temp.cleanup()

    def test_malformed_project_front_matter_routes_to_recovery(self) -> None:
        temp, project = self.copy_fixture()
        try:
            path = project / "PROJECT.md"
            path.write_text(path.read_text().replace(
                'workstream_root = "implementation/workstreams"\n+++',
                'workstream_root = "implementation/workstreams"\nrevision = [\n+++',
                1,
            ))
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("bootstrap project identity invalid", routed.reason)
            self.assertIn("malformed TOML front matter", routed.reason)
        finally:
            temp.cleanup()

    def install_malformed_planning(self, project: Path) -> None:
        self.install_green_definition(project)
        self.install_state_record(
            project, "planning", "planning", "PLANNING.toml",
            'workstream_id = "sample-workstream"\ncycle = [\n',
        )

    def install_malformed_board_research(self, project: Path) -> None:
        self.install_board_research(project, state="active")
        research = project / "implementation/workstreams/sample-workstream/RESEARCH.toml"
        research.write_text(research.read_text() + "\nrevision = [\n")

    def test_malformed_preboard_and_board_records_route_to_recovery(self) -> None:
        """RF017: representative selector-owned TOML surfaces fail closed the same way."""
        cases = (
            ("INTAKE.toml", lambda project: self.install_intake(
                project, 'workstream_id = "sample-workstream"\nkind = [\n')),
            ("RESEARCH.toml", lambda project: self.install_state_record(
                project, "research", "research", "RESEARCH.toml",
                'workstream_id = "sample-workstream"\nstate = [\n')),
            ("TRACKER.toml", lambda project: self.install_state_record(
                project, "tracker", "tracker", "TRACKER.toml",
                'workstream_id = "sample-workstream"\nstate = [\n')),
            ("PLANNING.toml", self.install_malformed_planning),
            ("RESEARCH.toml", self.install_malformed_board_research),
        )
        for filename, install in cases:
            temp, project = self.copy_fixture()
            try:
                install(project)
                routed = select_route(project, [MANIFEST], package_root=ROOT)
                with self.subTest(surface=filename):
                    self.assertEqual(
                        (routed.disposition, routed.obligation),
                        ("recovery", "recovery_boundary"),
                    )
                    self.assertIn("selected workstream identity invalid", routed.reason)
                    self.assertIn("malformed TOML", routed.reason)
                    self.assertIn(filename, routed.reason)
            finally:
                temp.cleanup()

    def test_malformed_review_attempt_and_blocker_route_to_recovery(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_reviewable_result(project, "required")
            review_path = self.add_review_attempt(project, "pending")
            attempt = project / review_path
            attempt.write_text(attempt.read_text() + "\nrevision = [\n")
            # Commit the malformed bytes so the exact locator still proves Git
            # identity and freshness; the verified TOML parse must then fail.
            self.rebind_review_attempt(project, review_path)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("current Card execution state invalid", routed.reason)
            self.assertIn("malformed TOML", routed.reason)
            self.assertIn(review_path, routed.reason)
        finally:
            temp.cleanup()

        temp, project = self.copy_fixture()
        try:
            self.install_blocker(project, "missing_evidence")
            blocker = project / "implementation/workstreams/sample-workstream/blockers/M01-T04.toml"
            blocker.write_text(blocker.read_text() + "\nrevision = [\n")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("blocked Card recovery invalid", routed.reason)
            self.assertIn("malformed TOML", routed.reason)
            self.assertIn("blockers/M01-T04.toml", routed.reason)
        finally:
            temp.cleanup()

    def test_valid_and_semantic_invalid_controls_keep_existing_treatment(self) -> None:
        routed = select_route(FIXTURE, [MANIFEST], package_root=ROOT)
        self.assertEqual((routed.disposition, routed.obligation), ("route", "execution"))

        temp, project = self.copy_fixture()
        try:
            board = project / BOARD
            board.write_text(board.read_text().replace(
                'status = "in_progress"', 'status = "bogus"', 1))
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("recovery", "recovery_boundary"))
            self.assertIn("invalid status", routed.reason)
            self.assertNotIn("malformed TOML", routed.reason)
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
