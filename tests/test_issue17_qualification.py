from __future__ import annotations

from pathlib import Path
import unittest

from tools.receive_contract import (
    FreshContextLocator,
    ReceiveContractError,
    ReceiveExpectation,
    consume_handoff_and_classify,
    parse_fresh_context_locator,
)


ROOT = Path(__file__).resolve().parents[1]
FRESH = ROOT / "prompts" / "CHATGPT_FRESH_SESSION.md"
CHATGPT = ROOT / "prompts" / "CHATGPT_PROJECT_INSTRUCTIONS.md"
CODEX = ROOT / "skills" / "project_workflow_v2" / "SKILL.md"
ROUTER = ROOT / "workflow" / "ROUTER.md"
CONTINUATION = ROOT / "workflow" / "CONTINUATION.md"
USER_STOP = ROOT / "workflow" / "USER_STOP.md"


class Issue17QualificationTests(unittest.TestCase):
    def locator(self, entry: str = "Premium B", pointer: str = "state.toml") -> FreshContextLocator:
        rendered = (
            FRESH.read_text(encoding="utf-8")
            .replace("<owner/repository>", "elmakus/project_workflow_v2")
            .replace("<exact-branch>", "work/pwv2-handoff-receive-continuation")
            .replace("<route-or-obligation>", entry)
            .replace("<repository-relative-path>", pointer)
        )
        return parse_fresh_context_locator(rendered)

    def expectation(self, entry: str = "Premium B", pointer: str = "state.toml", **changes) -> ReceiveExpectation:
        values = dict(
            repository="elmakus/project_workflow_v2",
            branch="work/pwv2-handoff-receive-continuation",
            entry_obligation=entry,
            durable_start_pointer=pointer,
            disposition="stop",
            transferable=True,
            independence_required=entry == "Premium B",
        )
        values.update(changes)
        return ReceiveExpectation(**values)

    def test_producer_locator_receiver_continues_until_new_real_stop(self) -> None:
        locator = self.locator()
        entered = consume_handoff_and_classify(
            locator,
            self.expectation(),
            receiver_semantically_independent=True,
            freshly_routed_disposition="route",
            freshly_routed_obligation="plan_review",
        )
        self.assertEqual((entered.receive_action, entered.continuation_action, entered.restart_action),
                         ("consume_handoff", "continue", "execute_selected_obligation"))

        stopped = consume_handoff_and_classify(
            locator,
            self.expectation(),
            receiver_semantically_independent=True,
            freshly_routed_disposition="stop",
            freshly_routed_obligation="authorization_boundary",
        )
        self.assertEqual((stopped.continuation_action, stopped.restart_action), ("return", "no_replay"))

        end_of_scope = consume_handoff_and_classify(
            locator,
            self.expectation(),
            receiver_semantically_independent=True,
            freshly_routed_disposition="stop",
            freshly_routed_obligation="end_of_approved_scope",
        )
        self.assertEqual(
            (end_of_scope.continuation_action, end_of_scope.restart_action),
            ("return", "no_replay"),
        )

    def test_premium_transfer_and_independent_review_matrix(self) -> None:
        for entry in ("Premium A", "Premium B", "Premium C", "independent Review — M06-T04-R01"):
            independent = entry in ("Premium B", "independent Review — M06-T04-R01")
            locator = self.locator(entry)
            decision = consume_handoff_and_classify(
                locator,
                self.expectation(entry, independence_required=independent),
                receiver_semantically_independent=True,
                freshly_routed_disposition="route",
                freshly_routed_obligation="selected_obligation",
            )
            self.assertEqual(decision.receive_action, "consume_handoff")
            if independent:
                with self.assertRaises(ReceiveContractError):
                    consume_handoff_and_classify(
                        locator,
                        self.expectation(entry, independence_required=True),
                        receiver_semantically_independent=False,
                        freshly_routed_disposition="route",
                        freshly_routed_obligation="selected_obligation",
                    )

    def test_stale_wrong_forged_and_duplicate_receipt_fail_closed(self) -> None:
        locator = self.locator()
        for expected in (
            self.expectation(repository="wrong/repo"),
            self.expectation(branch="wrong"),
            self.expectation(entry_obligation="different"),
            self.expectation(durable_start_pointer="different.toml"),
            self.expectation(disposition="route", transferable=False),
        ):
            with self.assertRaises(ReceiveContractError):
                consume_handoff_and_classify(
                    locator,
                    expected,
                    receiver_semantically_independent=True,
                    freshly_routed_disposition="route",
                    freshly_routed_obligation="execution_prep",
                )

        first_receipt = consume_handoff_and_classify(
            locator,
            self.expectation(),
            receiver_semantically_independent=True,
            freshly_routed_disposition="route",
            freshly_routed_obligation="execution_prep",
        )
        self.assertEqual(first_receipt.receive_action, "consume_handoff")

        # Durable advancement changes the canonical route away from the handoff stop.
        # Re-submitting the old locator must fail before continuation/replay.
        with self.assertRaises(ReceiveContractError):
            consume_handoff_and_classify(
                locator,
                self.expectation(disposition="route"),
                receiver_semantically_independent=True,
                freshly_routed_disposition="route",
                freshly_routed_obligation="execution",
                durable_semantic_result=True,
            )

    def test_recovery_readback_and_durable_result_restart_safety(self) -> None:
        locator = self.locator()
        durable = consume_handoff_and_classify(
            locator, self.expectation(), receiver_semantically_independent=True,
            freshly_routed_disposition="route", freshly_routed_obligation="result_reconciliation",
            durable_semantic_result=True,
        )
        self.assertEqual(durable.restart_action, "reconcile_without_replay")
        uncertain = consume_handoff_and_classify(
            locator, self.expectation(), receiver_semantically_independent=True,
            freshly_routed_disposition="recovery", freshly_routed_obligation="recovery_boundary",
            external_effect_uncertain=True,
        )
        self.assertEqual((uncertain.continuation_action, uncertain.restart_action),
                         ("recover", "readback_external_effect_before_retry"))

    def test_supported_adapters_are_equivalent_thin_receive_bootstraps(self) -> None:
        for path in (CHATGPT, CODEX):
            text = path.read_text(encoding="utf-8")
            self.assertIn("four-field fresh-context locator", text)
            self.assertIn("untrusted bootstrap input", text)
            self.assertIn("canonical receive boundary", text)
            self.assertIn("real stop", text)
        template = FRESH.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(template), 4)
        self.assertTrue(all(":" in line for line in template))

    def test_no_parallel_continuation_authority_is_introduced(self) -> None:
        canonical = "\n".join(
            p.read_text(encoding="utf-8") for p in (ROUTER, CONTINUATION, USER_STOP, CHATGPT, CODEX)
        )
        for forbidden in ("provider catalog", "session ledger", "second router"):
            self.assertNotIn("create " + forbidden, canonical.lower())


if __name__ == "__main__":
    unittest.main()
