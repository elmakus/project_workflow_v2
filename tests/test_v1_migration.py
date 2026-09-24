from __future__ import annotations

import copy
import hashlib
import tomllib
import unittest
from pathlib import Path

from tools.v1_migration import MigrationInputError, convert_dry_run, dry_run, parse_bounded_yaml
from tools.state_contract import validate_board, validate_review_history, validate_workstream

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "tests" / "fixtures" / "migration"
REPO = "elmakus/chatgpt-codex-project-workflow"
SHA = "a" * 40


class V1MigrationDryRunTests(unittest.TestCase):
    def texts(self, stem: str) -> tuple[str, str | None]:
        board = (FIX / f"{stem}-board.yaml").read_text()
        manifest_path = FIX / f"{stem}-workstream.yaml"
        return board, manifest_path.read_text() if manifest_path.exists() else None

    def plan(self, source_class: str, stem: str):
        board, manifest = self.texts(stem)
        return dry_run(
            source_class=source_class,
            repository=REPO,
            expected_commit=SHA,
            observed_commit=SHA,
            board_text=board,
            manifest_text=manifest,
            destination_workstream=f"migrated-{stem}",
        )

    def test_real_source_origins_are_exact_and_finite(self) -> None:
        with (FIX / "ORIGINS.toml").open("rb") as handle:
            origins = tomllib.load(handle)
        self.assertEqual(
            set(origins),
            {
                "chatgpt_workstream_yaml_v1",
                "codex_workstream_yaml_v1",
                "legacy_root_yaml_v1",
            },
        )
        for value in origins.values():
            self.assertRegex(value["commit"], r"^[0-9a-f]{40}$")
            self.assertRegex(value["board_blob"], r"^[0-9a-f]{40}$")
            if "manifest_blob" in value:
                self.assertRegex(value["manifest_blob"], r"^[0-9a-f]{40}$")

    def test_three_real_derived_classes_have_deterministic_mutation_free_dry_run(self) -> None:
        cases = (
            ("chatgpt_workstream_yaml_v1", "chatgpt"),
            ("codex_workstream_yaml_v1", "codex"),
            ("legacy_root_yaml_v1", "legacy-root"),
        )
        for source_class, stem in cases:
            with self.subTest(source_class=source_class):
                before = {
                    p: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in FIX.iterdir()
                    if p.is_file()
                }
                first = self.plan(source_class, stem)
                second = self.plan(source_class, stem)
                after = {
                    p: hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in FIX.iterdir()
                    if p.is_file()
                }
                self.assertEqual(first, second)
                if source_class == "codex_workstream_yaml_v1":
                    self.assertFalse(first["valid"])
                    self.assertIn(
                        "workstream_review_reconciliation_required",
                        first["blockers"],
                    )
                else:
                    self.assertTrue(first["valid"])
                self.assertEqual(first["destination"]["root"], f"implementation/workstreams/migrated-{stem}")
                self.assertEqual(before, after)

    def test_legacy_root_never_becomes_root_v2_destination(self) -> None:
        plan = self.plan("legacy_root_yaml_v1", "legacy-root")
        self.assertTrue(plan["destination"]["manifest"].startswith("implementation/workstreams/"))
        self.assertTrue(plan["destination"]["task_board"].startswith("implementation/workstreams/"))
        self.assertNotEqual(plan["destination"]["task_board"], "implementation/TASK_BOARD.toml")

    def test_unknown_source_class_and_unknown_semantic_field_fail_closed(self) -> None:
        board, manifest = self.texts("chatgpt")
        with self.assertRaisesRegex(MigrationInputError, "unsupported source class"):
            dry_run(
                source_class="hypothetical_v0",
                repository=REPO,
                expected_commit=SHA,
                observed_commit=SHA,
                board_text=board,
                manifest_text=manifest,
                destination_workstream="migrated-chatgpt",
            )
        parsed = parse_bounded_yaml(board)
        self.assertIn("cards", parsed)
        changed = board.replace('research_obligation: null', 'research_obligation: null\nsemantic_surprise: true')
        with self.assertRaisesRegex(MigrationInputError, "unsupported fields"):
            dry_run(
                source_class="chatgpt_workstream_yaml_v1",
                repository=REPO,
                expected_commit=SHA,
                observed_commit=SHA,
                board_text=changed,
                manifest_text=manifest,
                destination_workstream="migrated-chatgpt",
            )

    def test_racing_source_identity_fails_closed(self) -> None:
        board, manifest = self.texts("chatgpt")
        with self.assertRaisesRegex(MigrationInputError, "source moved"):
            dry_run(
                source_class="chatgpt_workstream_yaml_v1",
                repository=REPO,
                expected_commit="a" * 40,
                observed_commit="b" * 40,
                board_text=board,
                manifest_text=manifest,
                destination_workstream="migrated-chatgpt",
            )

    def test_parallel_active_cards_are_reported_as_blocker_without_choosing_winner(self) -> None:
        board, manifest = self.texts("chatgpt")
        parsed = parse_bounded_yaml(board)
        card = copy.deepcopy(parsed["cards"][0])
        card["id"] = "M05-T06"
        card["execution_status"] = "in_progress"
        first = board.replace("execution_status: done", "execution_status: in_progress", 2)
        extra = (
            '\n  - id: "M05-T06"\n'
            '    title: "Competing active card"\n'
            '    milestone: "M05"\n'
            '    decision_state: accepted\n'
            '    execution_status: in_progress\n'
            '    executor: chatgpt\n'
            '    depends_on: []\n'
            '    openspec_change: null\n'
            '    contract: "implementation/workstreams/feature-common-preexecution-core/cards/M05-T06.md"\n'
            '    review_state: null\n'
            '    review_subject: null\n'
            '    review_evidence: null\n'
            '    result_commit: null\n'
            '    result_pr: null\n'
            '    evidence: null\n'
            '    tests_summary: null\n'
        )
        plan = dry_run(
            source_class="chatgpt_workstream_yaml_v1",
            repository=REPO,
            expected_commit=SHA,
            observed_commit=SHA,
            board_text=first.rstrip() + extra,
            manifest_text=manifest,
            destination_workstream="migrated-chatgpt",
        )
        self.assertFalse(plan["valid"])
        self.assertEqual(plan["blockers"], ["parallel_active_cards:M05-T05,M05-T06"])
        self.assertIn("card:M05-T05:in_progress", plan["outstanding_obligations"])
        self.assertIn("card:M05-T06:in_progress", plan["outstanding_obligations"])

    def test_terminal_review_without_exact_subject_fails_closed(self) -> None:
        board, manifest = self.texts("chatgpt")
        changed = board.replace('review_subject: "exact-subject"', "review_subject: null")
        with self.assertRaisesRegex(MigrationInputError, "terminal V1 review lacks exact review_subject"):
            dry_run(
                source_class="chatgpt_workstream_yaml_v1",
                repository=REPO,
                expected_commit=SHA,
                observed_commit=SHA,
                board_text=changed,
                manifest_text=manifest,
                destination_workstream="migrated-chatgpt",
            )


    def exact_review_proof(self, verdict: str = "green", *, subject_suffix: str = "1", attempt: str = "R01"):
        return {
            "attempt": attempt,
            "verdict": verdict,
            "source_review_subject": "exact-subject",
            "subject": {
                "repository": REPO,
                "commit": ("b" if subject_suffix == "1" else "d") * 40,
                "path": "implementation/workstreams/feature-common-preexecution-core/evidence/reviewed.md",
                "blob": ("c" if subject_suffix == "1" else "e") * 40,
            },
            "materially_produced_or_repaired_subject": False,
            "independence_basis": "Exact V1 evidence proves the reviewer did not materially produce or repair this subject.",
            "evidence_path": (
                "implementation/workstreams/feature-common-preexecution-core/evidence/"
                f"source-{attempt}.md"
            ) if verdict in {"green", "red"} else "",
        }

    def test_safe_conversion_validates_as_common_v2_state_when_review_proof_is_exact(self) -> None:
        board, manifest = self.texts("chatgpt")
        plan = self.plan("chatgpt_workstream_yaml_v1", "chatgpt")
        bundle = convert_dry_run(
            plan=plan,
            board_text=board,
            manifest_text=manifest,
            review_proofs={"M05-T05": [self.exact_review_proof()]},
        )
        validate_workstream(bundle["workstream"])
        validate_board(bundle["task_board"], bundle["workstream"])
        validate_review_history(
            bundle["review_attempts"]["M05-T05"],
            expected_card_id="M05-T05",
            workstream_id="migrated-chatgpt",
        )
        card = bundle["task_board"]["cards"][0]
        self.assertEqual(card["status"], "done")
        self.assertIn("result", card)
        self.assertEqual(bundle["review_obligations"], [])
        self.assertEqual(bundle["provenance"]["source_branch"], "feat/common-preexecution-core")
        self.assertEqual(bundle["provenance"]["source_base_ref"], "fd2dc95f539d982e1009d71bbf1301f3098900f6")
        self.assertEqual(bundle["provenance"]["source_integration_target"], "main")

    def test_repeated_conversion_is_byte_semantically_idempotent(self) -> None:
        board, manifest = self.texts("chatgpt")
        plan = self.plan("chatgpt_workstream_yaml_v1", "chatgpt")
        proof = {"M05-T05": [self.exact_review_proof()]}
        first = convert_dry_run(
            plan=plan,
            board_text=board,
            manifest_text=manifest,
            review_proofs=proof,
        )
        second = convert_dry_run(
            plan=plan,
            board_text=board,
            manifest_text=manifest,
            review_proofs=proof,
        )
        self.assertEqual(first, second)
        self.assertEqual(first["output_fingerprint"], second["output_fingerprint"])

    def test_conversion_rejects_inputs_that_do_not_match_green_dry_run(self) -> None:
        board, manifest = self.texts("chatgpt")
        plan = self.plan("chatgpt_workstream_yaml_v1", "chatgpt")
        changed = board.replace(
            "execution_status: done",
            "execution_status: in_progress",
            1,
        )
        with self.assertRaisesRegex(
            MigrationInputError, "conversion board diverges from GREEN dry-run source"
        ):
            convert_dry_run(
                plan=plan,
                board_text=changed,
                manifest_text=manifest,
            )

    def test_unproven_terminal_review_becomes_blocking_review_obligation_not_invented_green(self) -> None:
        board, manifest = self.texts("chatgpt")
        bundle = convert_dry_run(
            plan=self.plan("chatgpt_workstream_yaml_v1", "chatgpt"),
            board_text=board,
            manifest_text=manifest,
        )
        validate_workstream(bundle["workstream"])
        validate_board(bundle["task_board"], bundle["workstream"])
        card = bundle["task_board"]["cards"][0]
        self.assertEqual(card["status"], "blocked")
        self.assertNotIn("review_attempts", card)
        self.assertEqual(len(bundle["review_obligations"]), 1)
        self.assertIn("cannot be reused", bundle["review_obligations"][0]["reason"])
        self.assertEqual(bundle["review_obligations"][0]["source_review_state"], "green")
        self.assertIn("result", card)

    def test_review_proof_must_bind_current_v1_subject(self) -> None:
        board, manifest = self.texts("chatgpt")
        bad = self.exact_review_proof()
        bad["source_review_subject"] = "different-subject"
        bundle = convert_dry_run(
            plan=self.plan("chatgpt_workstream_yaml_v1", "chatgpt"),
            board_text=board,
            manifest_text=manifest,
            review_proofs={"M05-T05": [bad]},
        )
        self.assertEqual(bundle["task_board"]["cards"][0]["status"], "blocked")
        self.assertIn("not bound", bundle["review_obligations"][0]["reason"])

    def test_exact_red_to_green_history_is_append_only_and_current_green_is_reused(self) -> None:
        board, manifest = self.texts("chatgpt")
        red = self.exact_review_proof("red", subject_suffix="1", attempt="R01")
        red["source_review_subject"] = "older-red-subject"
        green = self.exact_review_proof("green", subject_suffix="2", attempt="R02")
        bundle = convert_dry_run(
            plan=self.plan("chatgpt_workstream_yaml_v1", "chatgpt"),
            board_text=board,
            manifest_text=manifest,
            review_proofs={"M05-T05": [red, green]},
        )
        attempts = bundle["review_attempts"]["M05-T05"]
        self.assertEqual([a["verdict"] for a in attempts], ["red", "green"])
        self.assertNotEqual(attempts[0]["subject"], attempts[1]["subject"])
        validate_review_history(
            attempts, expected_card_id="M05-T05", workstream_id="migrated-chatgpt"
        )
        self.assertEqual(bundle["task_board"]["cards"][0]["status"], "done")

    def test_exact_red_remains_blocked_for_correction(self) -> None:
        board, manifest = self.texts("chatgpt")
        red_board = board.replace("review_state: green", "review_state: red")
        red = self.exact_review_proof("red")
        plan = dry_run(
            source_class="chatgpt_workstream_yaml_v1",
            repository=REPO,
            expected_commit=SHA,
            observed_commit=SHA,
            board_text=red_board,
            manifest_text=manifest,
            destination_workstream="migrated-chatgpt",
        )
        bundle = convert_dry_run(
            plan=plan,
            board_text=red_board,
            manifest_text=manifest,
            review_proofs={"M05-T05": [red]},
        )
        validate_review_history(
            bundle["review_attempts"]["M05-T05"],
            expected_card_id="M05-T05",
            workstream_id="migrated-chatgpt",
        )
        self.assertEqual(bundle["task_board"]["cards"][0]["status"], "blocked")
        self.assertIn("corrective review", bundle["review_obligations"][0]["reason"])

    def test_exact_pending_review_remains_blocking_until_green(self) -> None:
        board, manifest = self.texts("chatgpt")
        pending_board = board.replace("review_state: green", "review_state: pending")
        pending = self.exact_review_proof("pending")
        plan = dry_run(
            source_class="chatgpt_workstream_yaml_v1",
            repository=REPO,
            expected_commit=SHA,
            observed_commit=SHA,
            board_text=pending_board,
            manifest_text=manifest,
            destination_workstream="migrated-chatgpt",
        )
        bundle = convert_dry_run(
            plan=plan,
            board_text=pending_board,
            manifest_text=manifest,
            review_proofs={"M05-T05": [pending]},
        )
        attempts = bundle["review_attempts"]["M05-T05"]
        validate_review_history(
            attempts,
            expected_card_id="M05-T05",
            workstream_id="migrated-chatgpt",
        )
        self.assertEqual(attempts[-1]["verdict"], "pending")
        self.assertEqual(attempts[-1]["review_kind"], "discovery")
        self.assertFalse(attempts[-1]["discovery_complete"])
        self.assertEqual(attempts[-1]["material_finding_ids"], [])
        self.assertEqual(bundle["task_board"]["cards"][0]["status"], "blocked")
        self.assertIn("pending review remains outstanding", bundle["review_obligations"][0]["reason"])

    def test_legacy_root_maps_to_branch_local_v2_owner_while_preserving_source_branch(self) -> None:
        board, _ = self.texts("legacy-root")
        plan = self.plan("legacy_root_yaml_v1", "legacy-root")
        bundle = convert_dry_run(plan=plan, board_text=board, manifest_text=None)
        self.assertEqual(bundle["provenance"]["source_branch"], "main")
        self.assertEqual(bundle["workstream"]["branch"], "migration/migrated-legacy-root")
        self.assertEqual(bundle["task_board"]["execution_ref"]["branch"], "migration/migrated-legacy-root")
        self.assertTrue(
            bundle["workstream"]["task_board"]["path"].startswith(
                "implementation/workstreams/migrated-legacy-root/"
            )
        )

    def test_conversion_output_drops_runtime_policy_scheduler_keys_from_canonical_state(self) -> None:
        board, manifest = self.texts("codex")
        manifest = manifest.replace("  state: green", "  state: null", 1)
        manifest = manifest.replace('  subject: "feature@subject"', "  subject: null", 1)
        manifest = manifest.replace(
            '  evidence: "implementation/workstreams/feature-codex-only-policy/evidence/M05-final-integration-review-02.md"',
            "  evidence: null",
            1,
        )
        plan = dry_run(
            source_class="codex_workstream_yaml_v1",
            repository=REPO,
            expected_commit=SHA,
            observed_commit=SHA,
            board_text=board,
            manifest_text=manifest,
            destination_workstream="migrated-codex",
        )
        self.assertTrue(plan["valid"])
        bundle = convert_dry_run(
            plan=plan,
            board_text=board,
            manifest_text=manifest,
        )
        forbidden = {
            "execution_policy", "runtime", "model", "session", "worker",
            "active_execution", "returned", "transfer_ready", "batch",
            "lane", "lanes", "scheduler", "context_health",
        }

        def keys(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    yield key
                    yield from keys(child)
            elif isinstance(value, list):
                for child in value:
                    yield from keys(child)

        canonical_keys = set(keys(bundle["workstream"])) | set(keys(bundle["task_board"]))
        self.assertTrue(forbidden.isdisjoint(canonical_keys))
        validate_workstream(bundle["workstream"])
        validate_board(bundle["task_board"], bundle["workstream"])



if __name__ == "__main__":
    unittest.main()
