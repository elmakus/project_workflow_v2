from __future__ import annotations

import unittest

from tools.adoption_contract import AdoptionContractError, custody_transfer_action


PACKAGE = "owner/project_workflow_v2@commit:" + ("a" * 40)


class AdoptionContractTests(unittest.TestCase):
    def test_explicit_authorization_is_required_before_transfer(self) -> None:
        self.assertEqual(
            custody_transfer_action(
                explicit_authorization=False,
                package_verified=True,
                terminal_handoff_present=False,
                source_owner_active=True,
                destination_owner_active=False,
                package_subject=PACKAGE,
            ),
            "authorization_stop",
        )

    def test_verified_package_keeps_v1_as_sole_owner_until_terminal_handoff(self) -> None:
        self.assertEqual(
            custody_transfer_action(
                explicit_authorization=True,
                package_verified=False,
                terminal_handoff_present=False,
                source_owner_active=True,
                destination_owner_active=False,
                package_subject=PACKAGE,
            ),
            "stage_and_verify_package",
        )
        self.assertEqual(
            custody_transfer_action(
                explicit_authorization=True,
                package_verified=True,
                terminal_handoff_present=False,
                source_owner_active=True,
                destination_owner_active=False,
                package_subject=PACKAGE,
            ),
            "record_terminal_transfer",
        )

    def test_interruption_after_terminal_handoff_resumes_destination_without_reactivating_v1(self) -> None:
        self.assertEqual(
            custody_transfer_action(
                explicit_authorization=True,
                package_verified=True,
                terminal_handoff_present=True,
                source_owner_active=False,
                destination_owner_active=False,
                package_subject=PACKAGE,
                handoff_package_subject=PACKAGE,
            ),
            "activate_destination_from_terminal_handoff",
        )

    def test_completed_transfer_has_exactly_one_live_owner(self) -> None:
        self.assertEqual(
            custody_transfer_action(
                explicit_authorization=True,
                package_verified=True,
                terminal_handoff_present=True,
                source_owner_active=False,
                destination_owner_active=True,
                package_subject=PACKAGE,
                handoff_package_subject=PACKAGE,
            ),
            "transferred_verified",
        )

    def test_dual_mutable_ownership_fails_closed(self) -> None:
        with self.assertRaisesRegex(AdoptionContractError, "both source and destination"):
            custody_transfer_action(
                explicit_authorization=True,
                package_verified=True,
                terminal_handoff_present=True,
                source_owner_active=True,
                destination_owner_active=True,
                package_subject=PACKAGE,
                handoff_package_subject=PACKAGE,
            )

    def test_destination_activation_before_terminal_handoff_fails_closed(self) -> None:
        with self.assertRaisesRegex(AdoptionContractError, "before the terminal source handoff"):
            custody_transfer_action(
                explicit_authorization=True,
                package_verified=True,
                terminal_handoff_present=False,
                source_owner_active=False,
                destination_owner_active=True,
                package_subject=PACKAGE,
            )

    def test_terminal_handoff_is_bound_to_exact_verified_package(self) -> None:
        with self.assertRaisesRegex(AdoptionContractError, "does not match"):
            custody_transfer_action(
                explicit_authorization=True,
                package_verified=True,
                terminal_handoff_present=True,
                source_owner_active=False,
                destination_owner_active=False,
                package_subject=PACKAGE,
                handoff_package_subject="owner/project_workflow_v2@commit:" + ("b" * 40),
            )


if __name__ == "__main__":
    unittest.main()
