from __future__ import annotations
import unittest
from tools.review_contract import review_delivery_policy
from tools.user_stop_contract import (
    DeliveryContractError, DeliveryRequirement, HANDOFF_NONE, HANDOFF_OFFERED,
    HANDOFF_REQUIRED, router_stop_handoff_policy, validate_user_stop_delivery,
)

VALID_LOCATOR = """NEW CHAT START PROMPT

Repository: elmakus/project_workflow_v2
Branch: work/pwv2-handoff-determinism
Entry obligation: independent review M01-T01-R01
Durable start pointer: implementation/workstreams/issue-handoff-determinism/TASK_BOARD.toml
"""

class UserStopContractTests(unittest.TestCase):
    def test_router_premium_policies_are_downstream_only(self):
        self.assertEqual(router_stop_handoff_policy(disposition="stop", obligation="premium_A"), HANDOFF_OFFERED)
        self.assertEqual(router_stop_handoff_policy(disposition="stop", obligation="premium_B"), HANDOFF_REQUIRED)
        self.assertEqual(router_stop_handoff_policy(disposition="stop", obligation="premium_C"), HANDOFF_OFFERED)
        self.assertEqual(router_stop_handoff_policy(disposition="stop", obligation="end_of_scope"), HANDOFF_NONE)
        self.assertEqual(router_stop_handoff_policy(disposition="route", obligation="premium_B"), HANDOFF_NONE)

    def test_producer_without_internal_independent_context_requires_fresh_handoff(self):
        policy = review_delivery_policy(current_context_produced_subject=True, independent_context_available=False)
        self.assertEqual(policy, HANDOFF_REQUIRED)
        requirement = DeliveryRequirement(True, policy)
        with self.assertRaises(DeliveryContractError):
            validate_user_stop_delivery(requirement, "Review is pending.")
        with self.assertRaises(DeliveryContractError):
            validate_user_stop_delivery(requirement, VALID_LOCATOR)
        validate_user_stop_delivery(requirement, "USER ACTION REQUIRED: start fresh.\n" + VALID_LOCATOR)

    def test_repairer_re_review_has_same_required_postcondition(self):
        policy = review_delivery_policy(current_context_produced_subject=True, independent_context_available=False)
        repaired = VALID_LOCATOR.replace("M01-T01-R01", "M01-T01-R02")
        validate_user_stop_delivery(DeliveryRequirement(True, policy), "USER ACTION REQUIRED: start fresh.\n" + repaired)

    def test_nonproducer_or_internal_independent_review_needs_no_external_handoff(self):
        self.assertEqual(review_delivery_policy(current_context_produced_subject=False, independent_context_available=False), HANDOFF_NONE)
        self.assertEqual(review_delivery_policy(current_context_produced_subject=True, independent_context_available=True), HANDOFF_NONE)

    def test_non_boundary_cannot_acquire_handoff_policy(self):
        for policy in (HANDOFF_OFFERED, HANDOFF_REQUIRED):
            with self.assertRaises(DeliveryContractError):
                DeliveryRequirement(False, policy)
        validate_user_stop_delivery(DeliveryRequirement(False, HANDOFF_NONE), "GREEN / RED / Card completion")

    def test_offered_requires_locator_but_not_user_action(self):
        requirement = DeliveryRequirement(True, HANDOFF_OFFERED)
        with self.assertRaises(DeliveryContractError):
            validate_user_stop_delivery(requirement, "Premium A stop")
        validate_user_stop_delivery(requirement, VALID_LOCATOR)

    def test_required_rejects_placeholder_or_incomplete_locator(self):
        requirement = DeliveryRequirement(True, HANDOFF_REQUIRED)
        bad = VALID_LOCATOR.replace("work/pwv2-handoff-determinism", "<exact-branch>")
        with self.assertRaises(DeliveryContractError):
            validate_user_stop_delivery(requirement, "USER ACTION REQUIRED: fresh.\n" + bad)
        incomplete = VALID_LOCATOR.replace("Durable start pointer:", "Pointer:")
        with self.assertRaises(DeliveryContractError):
            validate_user_stop_delivery(requirement, "USER ACTION REQUIRED: fresh.\n" + incomplete)

if __name__ == "__main__":
    unittest.main()
