from __future__ import annotations

import unittest

from tools.review_contract import (
    ADVISORY_CATEGORIES,
    FORBIDDEN_DOWNGRADE_BASES,
    LOAD_BEARING_SURFACES,
    OBSERVATION_DISPOSITIONS,
    OPEN_OBSERVATION_DISPOSITION,
    ReviewContractError,
    attempt_is_observation_aware,
    can_finalize_review_obligation,
    REVIEW_SCOPE_DISCOVERY_CEILINGS,
    derive_observation_state,
    finding_severity_records,
    observation_records,
    observation_update_records,
    required_closure_scope,
    remaining_closure_findings,
    review_convergence_state,
    select_review_realization,
    unreconciled_observations,
    validate_closure_surface,
    validate_discovery_surface,
    validate_finding_severity,
    validate_observation_provenance,
    validate_verdict_severity,
)


class ReviewContractTests(unittest.TestCase):
    def test_review_realization_is_capability_first_but_noncanonical(self) -> None:
        self.assertEqual(
            select_review_realization(
                current_context_produced_subject=False,
                independent_context_available=False,
            ),
            "current_context",
        )
        self.assertEqual(
            select_review_realization(
                current_context_produced_subject=True,
                independent_context_available=True,
            ),
            "internal_independent",
        )
        self.assertEqual(
            select_review_realization(
                current_context_produced_subject=True,
                independent_context_available=False,
            ),
            "fresh_context",
        )

    def test_discovery_requires_complete_acceptance_and_no_first_blocker_stop(self) -> None:
        evaluated = validate_discovery_surface(
            applicable_acceptance=["A1", "A2", "A3"],
            evaluated_acceptance=["A3", "A1", "A2"],
            stopped_at_first_blocker=False,
        )
        self.assertEqual(evaluated, frozenset({"A1", "A2", "A3"}))

        with self.assertRaisesRegex(ReviewContractError, "first blocker"):
            validate_discovery_surface(
                applicable_acceptance=["A1", "A2"],
                evaluated_acceptance=["A1"],
                stopped_at_first_blocker=True,
            )
        with self.assertRaisesRegex(ReviewContractError, "omitted applicable acceptance"):
            validate_discovery_surface(
                applicable_acceptance=["A1", "A2"],
                evaluated_acceptance=["A1"],
                stopped_at_first_blocker=False,
            )

    def test_closure_scope_requires_complete_causal_blast_radius(self) -> None:
        scope = {
            "known_findings": ["F1"],
            "defect_classes": ["review-state-bypass"],
            "root_cause_evidence": ["new attempts were indistinguishable from legacy history"],
            "repair_diff": ["tools/api.py"],
            "regression_evidence": ["test_api_contract"],
            "reachable_callers": ["tools/router.py"],
            "consumers": ["unchanged-consumer"],
            "providers": ["unchanged-provider"],
            "contracts": ["API-v2"],
            "sibling_representations": ["json-representation"],
            "negative_space": ["missing-optional-field"],
        }
        required = required_closure_scope(scope)
        self.assertIn("unchanged-consumer", required)
        self.assertIn("unchanged-provider", required)

        validate_closure_surface(scope=scope, evaluated_surface=required)
        with self.assertRaisesRegex(ReviewContractError, "omitted materially implicated surface"):
            validate_closure_surface(
                scope=scope,
                evaluated_surface=required - {"unchanged-consumer"},
            )

        incomplete = dict(scope)
        incomplete.pop("providers")
        with self.assertRaisesRegex(ReviewContractError, "omitted causal categories"):
            required_closure_scope(incomplete)

    def test_closure_rejects_literal_example_only_repair_evidence(self) -> None:
        scope = {
            "known_findings": ["F1"],
            "defect_classes": [],
            "root_cause_evidence": [],
            "repair_diff": ["tools/review_contract.py"],
            "regression_evidence": ["test_literal_example"],
            "reachable_callers": [],
            "consumers": [],
            "providers": [],
            "contracts": [],
            "sibling_representations": ["sibling-state-shape"],
            "negative_space": ["legacy-shaped-new-attempt"],
        }
        with self.assertRaisesRegex(ReviewContractError, "defect_classes.*must not be empty"):
            required_closure_scope(scope)

        scope["defect_classes"] = ["review-state-bypass"]
        with self.assertRaisesRegex(ReviewContractError, "root_cause_evidence.*must not be empty"):
            required_closure_scope(scope)

    def test_cumulative_closure_reports_remaining_source_findings(self) -> None:
        attempts = [
            {
                "attempt": "R01",
                "verdict": "red",
                "review_kind": "discovery",
                "material_finding_ids": ["F1", "F2"],
            },
            {
                "attempt": "R02",
                "verdict": "green",
                "review_kind": "closure_verification",
                "source_discovery_attempt": "R01",
                "material_finding_ids": ["F1"],
            },
        ]
        self.assertEqual(
            remaining_closure_findings(attempts, "R01"),
            frozenset({"F2"}),
        )
        attempts.append({
            "attempt": "R03",
            "verdict": "green",
            "review_kind": "closure_verification",
            "source_discovery_attempt": "R01",
            "material_finding_ids": ["F2"],
        })
        self.assertEqual(
            remaining_closure_findings(attempts, "R01"),
            frozenset(),
        )

    def test_discovery_epoch_ceiling_matrix_counts_only_new_classes(self) -> None:
        for scope, ceiling in REVIEW_SCOPE_DISCOVERY_CEILINGS.items():
            attempts = []
            for index in range(ceiling - 1):
                attempts.append({
                    "attempt": f"R{index + 1:02d}",
                    "verdict": "red",
                    "review_kind": "discovery",
                    "review_scope": scope,
                    "review_epoch": "E01",
                    "material_defect_class_ids": [f"class-{index}"],
                    "post_convergence_validation": False,
                })
            state = review_convergence_state(attempts)
            self.assertEqual(state.discovery_epochs, ceiling - 1)
            self.assertFalse(state.convergence_required, scope)

            attempts.append({
                "attempt": f"R{ceiling:02d}",
                "verdict": "red",
                "review_kind": "discovery",
                "review_scope": scope,
                "review_epoch": "E01",
                "material_defect_class_ids": [f"class-{ceiling - 1}"],
                "post_convergence_validation": False,
            })
            state = review_convergence_state(attempts)
            self.assertEqual(state.discovery_epochs, ceiling)
            self.assertTrue(state.convergence_required, scope)

    def test_known_class_recurrence_green_and_closure_do_not_consume_discovery_epoch(self) -> None:
        attempts = [
            {
                "attempt": "R01",
                "verdict": "red",
                "review_kind": "discovery",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": ["class-a"],
                "post_convergence_validation": False,
            },
            {
                "attempt": "R02",
                "verdict": "green",
                "review_kind": "closure_verification",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": ["class-a"],
                "post_convergence_validation": False,
            },
            {
                "attempt": "R03",
                "verdict": "red",
                "review_kind": "discovery",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": ["class-a"],
                "post_convergence_validation": False,
            },
            {
                "attempt": "R04",
                "verdict": "green",
                "review_kind": "discovery",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": [],
                "post_convergence_validation": False,
            },
        ]
        state = review_convergence_state(attempts)
        self.assertEqual(state.discovery_epochs, 1)
        self.assertFalse(state.convergence_required)

    def test_third_failed_closure_round_for_one_class_requires_convergence(self) -> None:
        attempts = [{
            "attempt": "R01",
            "verdict": "red",
            "review_kind": "discovery",
            "review_scope": "card",
            "review_epoch": "E01",
            "material_defect_class_ids": ["class-a"],
            "post_convergence_validation": False,
            "subject": {
                "repository": "owner/repo",
                "commit": "1" * 40,
                "path": "results/card.md",
                "blob": "2" * 40,
            },
        }]
        for number in range(2, 5):
            attempts.append({
                "attempt": f"R{number:02d}",
                "verdict": "red",
                "review_kind": "closure_verification",
                "source_discovery_attempt": "R01",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": ["class-a"],
                "failed_material_defect_class_ids": ["class-a"],
                "post_convergence_validation": False,
                "subject": {
                    "repository": "owner/repo",
                    "commit": f"{number}" * 40,
                    "path": "results/card.md",
                    "blob": f"{number + 3}" * 40,
                },
            })
            state = review_convergence_state(attempts)
            self.assertEqual(state.failed_closure_rounds["class-a"], number - 1)
            self.assertEqual(state.convergence_required, number == 4)

    def test_repeated_red_closure_of_same_repaired_subject_counts_one_round(self) -> None:
        repaired_subject = {
            "repository": "owner/repo",
            "commit": "4" * 40,
            "path": "results/card.md",
            "blob": "5" * 40,
        }
        attempts = [{
            "attempt": "R01",
            "verdict": "red",
            "review_kind": "discovery",
            "review_scope": "card",
            "review_epoch": "E01",
            "material_defect_class_ids": ["class-a"],
            "post_convergence_validation": False,
            "subject": {
                "repository": "owner/repo",
                "commit": "1" * 40,
                "path": "results/card.md",
                "blob": "2" * 40,
            },
        }]
        for number in range(2, 5):
            attempts.append({
                "attempt": f"R{number:02d}",
                "verdict": "red",
                "review_kind": "closure_verification",
                "source_discovery_attempt": "R01",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": ["class-a"],
                "failed_material_defect_class_ids": ["class-a"],
                "post_convergence_validation": False,
                "subject": repaired_subject,
            })
        state = review_convergence_state(attempts)
        self.assertEqual(state.failed_closure_rounds["class-a"], 1)
        self.assertFalse(state.convergence_required)


    def test_source_discovery_content_does_not_count_as_repair_round(self) -> None:
        source_subject = {
            "repository": "owner/repo",
            "commit": "1" * 40,
            "path": "results/card.md",
            "blob": "2" * 40,
        }
        attempts = [{
            "attempt": "R01",
            "verdict": "red",
            "review_kind": "discovery",
            "review_scope": "card",
            "review_epoch": "E01",
            "material_defect_class_ids": ["class-a"],
            "post_convergence_validation": False,
            "subject": source_subject,
        }]
        for attempt_id, commit, blob in (
            ("R02", "3" * 40, "4" * 40),
            ("R03", "5" * 40, "6" * 40),
            ("R04", "7" * 40, "2" * 40),
        ):
            attempts.append({
                "attempt": attempt_id,
                "verdict": "red",
                "review_kind": "closure_verification",
                "source_discovery_attempt": "R01",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": ["class-a"],
                "failed_material_defect_class_ids": ["class-a"],
                "post_convergence_validation": False,
                "subject": {
                    "repository": "owner/repo",
                    "commit": commit,
                    "path": "results/card.md",
                    "blob": blob,
                },
            })
        state = review_convergence_state(attempts)
        self.assertEqual(state.failed_closure_rounds["class-a"], 2)
        self.assertFalse(state.convergence_required)

    def test_same_content_different_commit_counts_one_repair_round(self) -> None:
        attempts = [{
            "attempt": "R01",
            "verdict": "red",
            "review_kind": "discovery",
            "review_scope": "card",
            "review_epoch": "E01",
            "material_defect_class_ids": ["class-a"],
            "post_convergence_validation": False,
            "subject": {
                "repository": "owner/repo",
                "commit": "1" * 40,
                "path": "results/card.md",
                "blob": "2" * 40,
            },
        }]
        for attempt_id, commit in (("R02", "3" * 40), ("R03", "4" * 40)):
            attempts.append({
                "attempt": attempt_id,
                "verdict": "red",
                "review_kind": "closure_verification",
                "source_discovery_attempt": "R01",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": ["class-a"],
                "failed_material_defect_class_ids": ["class-a"],
                "post_convergence_validation": False,
                "subject": {
                    "repository": "owner/repo",
                    "commit": commit,
                    "path": "results/card.md",
                    "blob": "5" * 40,
                },
            })
        state = review_convergence_state(attempts)
        self.assertEqual(state.failed_closure_rounds["class-a"], 1)
        self.assertFalse(state.convergence_required)

    def test_t01_adapted_class_recurrence_does_not_consume_discovery_epoch(self) -> None:
        attempts = [
            {
                "attempt": "R01",
                "verdict": "red",
                "review_kind": "discovery",
                "material_finding_ids": ["F1"],
            },
            {
                "attempt": "R02",
                "verdict": "green",
                "review_kind": "closure_verification",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": ["class-a"],
                "post_convergence_validation": False,
            },
            {
                "attempt": "R03",
                "verdict": "red",
                "review_kind": "discovery",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": ["class-a"],
                "post_convergence_validation": False,
            },
        ]
        state = review_convergence_state(attempts)
        self.assertEqual(state.discovery_epochs, 0)
        self.assertEqual(state.seen_defect_classes, frozenset({"class-a"}))
        self.assertFalse(state.convergence_required)

    def test_epoch_change_resets_derived_counts_and_post_convergence_is_single(self) -> None:
        attempts = [
            {
                "attempt": "R01",
                "verdict": "red",
                "review_kind": "discovery",
                "review_scope": "final",
                "review_epoch": "E01",
                "material_defect_class_ids": ["a"],
                "post_convergence_validation": False,
            },
            {
                "attempt": "R02",
                "verdict": "red",
                "review_kind": "discovery",
                "review_scope": "final",
                "review_epoch": "E02",
                "material_defect_class_ids": ["b"],
                "post_convergence_validation": False,
            },
        ]
        state = review_convergence_state(attempts)
        self.assertEqual(state.review_epoch, "E02")
        self.assertEqual(state.discovery_epochs, 1)
        self.assertEqual(state.seen_defect_classes, frozenset({"b"}))

        attempts.extend([
            {
                "attempt": "R03",
                "verdict": "green",
                "review_kind": "discovery",
                "review_scope": "final",
                "review_epoch": "E02",
                "material_defect_class_ids": [],
                "post_convergence_validation": True,
            },
            {
                "attempt": "R04",
                "verdict": "green",
                "review_kind": "discovery",
                "review_scope": "final",
                "review_epoch": "E02",
                "material_defect_class_ids": [],
                "post_convergence_validation": True,
            },
        ])
        with self.assertRaisesRegex(ReviewContractError, "only one post-convergence"):
            review_convergence_state(attempts)

    def test_revisited_repaired_content_counts_new_failed_round_after_transition(self) -> None:
        source = {
            "attempt": "R01",
            "verdict": "red",
            "review_kind": "discovery",
            "review_scope": "card",
            "review_epoch": "E01",
            "material_defect_class_ids": ["class-a"],
            "post_convergence_validation": False,
            "subject": {
                "repository": "owner/repo",
                "commit": "1" * 40,
                "path": "results/card.md",
                "blob": "2" * 40,
            },
        }
        attempts = [source]
        for attempt_id, commit, blob in (
            ("R02", "3" * 40, "4" * 40),
            ("R03", "5" * 40, "6" * 40),
            ("R04", "7" * 40, "4" * 40),
        ):
            attempts.append({
                "attempt": attempt_id,
                "verdict": "red",
                "review_kind": "closure_verification",
                "source_discovery_attempt": "R01",
                "review_scope": "card",
                "review_epoch": "E01",
                "material_defect_class_ids": ["class-a"],
                "failed_material_defect_class_ids": ["class-a"],
                "post_convergence_validation": False,
                "subject": {
                    "repository": "owner/repo",
                    "commit": commit,
                    "path": "results/card.md",
                    "blob": blob,
                },
            })

        state = review_convergence_state(attempts)
        self.assertEqual(state.failed_closure_rounds["class-a"], 3)
        self.assertTrue(state.convergence_required)


    def test_multi_class_red_closure_counts_only_classes_that_failed(self) -> None:
        source = {
            "attempt": "R01",
            "verdict": "red",
            "review_kind": "discovery",
            "review_scope": "card",
            "review_epoch": "E01",
            "material_defect_class_ids": ["class-a", "class-b"],
            "post_convergence_validation": False,
            "subject": {
                "repository": "owner/repo",
                "commit": "1" * 40,
                "path": "results/card.md",
                "blob": "2" * 40,
            },
        }
        closure = {
            "attempt": "R02",
            "verdict": "red",
            "review_kind": "closure_verification",
            "source_discovery_attempt": "R01",
            "review_scope": "card",
            "review_epoch": "E01",
            "material_defect_class_ids": ["class-a", "class-b"],
            "failed_material_defect_class_ids": ["class-b"],
            "post_convergence_validation": False,
            "subject": {
                "repository": "owner/repo",
                "commit": "3" * 40,
                "path": "results/card.md",
                "blob": "4" * 40,
            },
        }

        state = review_convergence_state([source, closure])
        self.assertNotIn("class-a", state.failed_closure_rounds)
        self.assertEqual(state.failed_closure_rounds["class-b"], 1)
        self.assertFalse(state.convergence_required)


    def test_closure_cannot_finalize_review_obligation(self) -> None:
        self.assertTrue(can_finalize_review_obligation({
            "verdict": "green",
            "review_kind": "discovery",
        }))
        self.assertFalse(can_finalize_review_obligation({
            "verdict": "green",
            "review_kind": "closure_verification",
        }))
        self.assertFalse(can_finalize_review_obligation({
            "verdict": "red",
            "review_kind": "discovery",
        }))
        self.assertTrue(can_finalize_review_obligation({"verdict": "green"}))

    def test_expected_review_scope_binds_convergence_owner(self) -> None:
        for scope, ceiling in REVIEW_SCOPE_DISCOVERY_CEILINGS.items():
            attempts = [
                {
                    "attempt": f"R{index + 1:02d}",
                    "verdict": "red",
                    "review_kind": "discovery",
                    "review_scope": scope,
                    "review_epoch": "E01",
                    "material_defect_class_ids": [f"class-{index}"],
                    "post_convergence_validation": False,
                }
                for index in range(ceiling)
            ]
            bound = review_convergence_state(attempts, expected_review_scope=scope)
            self.assertEqual(bound.discovery_ceiling, ceiling)
            self.assertTrue(bound.convergence_required, scope)
            other = "final" if scope == "card" else "card"
            with self.subTest(scope=scope):
                with self.assertRaisesRegex(ReviewContractError, "does not match expected"):
                    review_convergence_state(attempts, expected_review_scope=other)
        with self.assertRaisesRegex(ReviewContractError, "unsupported expected review scope"):
            review_convergence_state([], expected_review_scope="program")


class ObservationSeverityTests(unittest.TestCase):
    def test_load_bearing_surfaces_and_advisory_categories_are_exact(self) -> None:
        self.assertEqual(
            LOAD_BEARING_SURFACES,
            frozenset({
                "acceptance",
                "correctness",
                "safety",
                "security",
                "data_integrity",
                "dependency",
                "compatibility",
                "invariant",
                "contract",
                "required_evidence",
            }),
        )
        self.assertEqual(
            ADVISORY_CATEGORIES,
            frozenset({
                "advisory",
                "stylistic",
                "optional_cleanup",
                "preference",
                "speculative_hardening",
            }),
        )
        self.assertEqual(
            OBSERVATION_DISPOSITIONS,
            frozenset({"resolved", "cleanup_candidate", "deferred", "promoted", "tracked"}),
        )
        self.assertEqual(OPEN_OBSERVATION_DISPOSITION, "open")
        self.assertEqual(
            FORBIDDEN_DOWNGRADE_BASES,
            frozenset({"convenience", "repair_cost", "reviewer_fatigue", "desire_to_finish"}),
        )

    def test_red_discovery_requires_load_bearing_evidence_for_every_blocking_finding(self) -> None:
        for surface in sorted(LOAD_BEARING_SURFACES):
            with self.subTest(surface=surface):
                covered = validate_finding_severity(
                    material_finding_ids=["F1"],
                    severity={"F1": {"id": "F1", "surface": surface, "evidence": "evidence/review-R01.md#F1"}},
                    require_complete=True,
                )
                self.assertEqual(covered, frozenset({"F1"}))

        with self.assertRaisesRegex(ReviewContractError, "load-bearing evidence"):
            validate_finding_severity(
                material_finding_ids=["F1", "F2"],
                severity={"F1": {"id": "F1", "surface": "correctness", "evidence": "evidence/review-R01.md#F1"}},
                require_complete=True,
            )
        with self.assertRaisesRegex(ReviewContractError, "unknown load-bearing surface"):
            validate_finding_severity(
                material_finding_ids=["F1"],
                severity={"F1": {"id": "F1", "surface": "taste", "evidence": "evidence/review-R01.md#F1"}},
                require_complete=True,
            )
        with self.assertRaisesRegex(ReviewContractError, "concrete load-bearing evidence"):
            validate_finding_severity(
                material_finding_ids=["F1"],
                severity={"F1": {"id": "F1", "surface": "correctness", "evidence": "  "}},
                require_complete=True,
            )
        with self.assertRaisesRegex(ReviewContractError, "unknown blocking finding"):
            validate_finding_severity(
                material_finding_ids=["F1"],
                severity={
                    "F1": {"id": "F1", "surface": "correctness", "evidence": "evidence/review-R01.md#F1"},
                    "F9": {"id": "F9", "surface": "safety", "evidence": "evidence/review-R01.md#F9"},
                },
                require_complete=True,
            )

    def test_closure_inherits_source_severity_without_repeating_evidence(self) -> None:
        self.assertEqual(
            validate_finding_severity(
                material_finding_ids=["F1"],
                severity={},
                require_complete=False,
            ),
            frozenset({"F1"}),
        )

    def test_advisory_observations_alone_cannot_keep_subject_red(self) -> None:
        self.assertEqual(
            validate_verdict_severity(
                verdict="green", load_bearing_ids=[], advisory_ids=["O1", "O2"]
            ),
            frozenset(),
        )
        with self.assertRaisesRegex(ReviewContractError, "advisory.*cannot.*RED"):
            validate_verdict_severity(
                verdict="red", load_bearing_ids=[], advisory_ids=["O1", "O2"]
            )
        self.assertEqual(
            validate_verdict_severity(
                verdict="red", load_bearing_ids=["F1"], advisory_ids=["O1"]
            ),
            frozenset({"F1"}),
        )

    def test_observation_awareness_is_explicit_per_attempt(self) -> None:
        self.assertFalse(attempt_is_observation_aware({}))
        self.assertFalse(
            attempt_is_observation_aware({
                "finding_severity": [],
                "observations": [],
                "observation_updates": [],
            })
        )
        self.assertTrue(attempt_is_observation_aware({"observations": [{"id": "O1"}]}))
        self.assertTrue(attempt_is_observation_aware({"finding_severity": [{"id": "F1"}]}))
        self.assertTrue(attempt_is_observation_aware({"observation_updates": [{"id": "O1"}]}))

    def test_observation_introduction_requires_canonical_provenance_and_disposition(self) -> None:
        attempt = {
            "verdict": "green",
            "evidence_path": "evidence/review-R01.md",
            "observations": [
                {
                    "id": "O1",
                    "category": "stylistic",
                    "evidence": "evidence/review-R01.md#O1",
                    "disposition": "open",
                    "disposition_basis": "",
                }
            ]
        }
        records = observation_records(attempt)
        self.assertEqual([record["id"] for record in records], ["O1"])

        for category in sorted(ADVISORY_CATEGORIES):
            with self.subTest(category=category):
                attempt["observations"][0]["category"] = category
                self.assertEqual(observation_records(attempt)[0]["category"], category)

        bad_category = {"verdict": "green", "evidence_path": "evidence/review-R01.md", "observations": [{
            "id": "O1", "category": "load_bearing", "evidence": "evidence/review-R01.md#O1",
            "disposition": "open", "disposition_basis": "",
        }]}
        with self.assertRaisesRegex(ReviewContractError, "unknown advisory category"):
            observation_records(bad_category)

        for tracker_evidence in (
            "TRACKER.toml#7",
            "see issue #7 for details",
            "https://github.com/owner/repo/issues/7",
        ):
            with self.subTest(evidence=tracker_evidence):
                with self.assertRaisesRegex(ReviewContractError, "tracker"):
                    observation_records({"verdict": "green", "evidence_path": "evidence/review-R01.md", "observations": [{
                        "id": "O1", "category": "advisory", "evidence": tracker_evidence,
                        "disposition": "open", "disposition_basis": "",
                    }]})

        terminal_without_basis = {"verdict": "green", "evidence_path": "evidence/review-R01.md", "observations": [{
            "id": "O1", "category": "advisory", "evidence": "evidence/review-R01.md#O1",
            "disposition": "resolved", "disposition_basis": "",
        }]}
        with self.assertRaisesRegex(ReviewContractError, "disposition_basis"):
            observation_records(terminal_without_basis)

        open_with_basis = {"verdict": "green", "evidence_path": "evidence/review-R01.md", "observations": [{
            "id": "O1", "category": "advisory", "evidence": "evidence/review-R01.md#O1",
            "disposition": "open", "disposition_basis": "not yet triaged",
        }]}
        with self.assertRaisesRegex(ReviewContractError, "disposition_basis"):
            observation_records(open_with_basis)

        self.assertEqual(
            validate_observation_provenance(
                evidence="evidence/review-R01.md#O1",
                origin_evidence_path="evidence/review-R01.md",
            ),
            "evidence/review-R01.md#O1",
        )
        with self.assertRaisesRegex(ReviewContractError, "tracker"):
            validate_observation_provenance(
                evidence="evidence/review-R01.md#O1",
                origin_evidence_path="TRACKER.toml",
            )

    def test_observation_evidence_must_reference_originating_evidence_file(self) -> None:
        self.assertEqual(
            validate_observation_provenance(
                evidence="evidence/review-R01.md#O1",
                origin_evidence_path="evidence/review-R01.md",
            ),
            "evidence/review-R01.md#O1",
        )
        with self.assertRaisesRegex(ReviewContractError, "bind"):
            validate_observation_provenance(
                evidence="unrelated/R99.md#O1",
                origin_evidence_path="evidence/review-R01.md",
            )
        with self.assertRaisesRegex(ReviewContractError, "bind"):
            validate_observation_provenance(
                evidence="#O1",
                origin_evidence_path="evidence/review-R01.md",
            )

    def test_observation_without_source_evidence_path_is_rejected(self) -> None:
        with self.assertRaisesRegex(ReviewContractError, "originating review evidence path"):
            observation_records({
                "verdict": "green",
                "observations": [{
                    "id": "O1", "category": "advisory",
                    "evidence": "evidence/review-R01.md#O1",
                    "disposition": "open", "disposition_basis": "",
                }],
            })
        with self.assertRaisesRegex(ReviewContractError, "originating review evidence path"):
            validate_observation_provenance(
                evidence="evidence/review-R01.md#O1",
                origin_evidence_path="",
            )

    def test_derivation_rejects_observation_pointing_away_from_origin(self) -> None:
        attempt = {
            "attempt": "R01",
            "verdict": "green",
            "review_kind": "discovery",
            "review_epoch": "E01",
            "material_finding_ids": [],
            "evidence_path": "evidence/review-R01.md",
            "observations": [{
                "id": "O1", "category": "advisory",
                "evidence": "unrelated/R99.md#O1",
                "disposition": "open", "disposition_basis": "",
            }],
        }
        with self.assertRaisesRegex(ReviewContractError, "bind"):
            derive_observation_state([attempt])

    def test_derived_observations_stay_open_until_terminal_reconciliation(self) -> None:
        attempts = [
            {
                "attempt": "R01",
                "verdict": "red",
                "review_kind": "discovery",
                "review_epoch": "E01",
                "material_finding_ids": ["F1"],
                "evidence_path": "evidence/review-R01.md",
                "observations": [
                    {
                        "id": "O1", "category": "stylistic",
                        "evidence": "evidence/review-R01.md#O1",
                        "disposition": "open", "disposition_basis": "",
                    },
                    {
                        "id": "O2", "category": "optional_cleanup",
                        "evidence": "evidence/review-R01.md#O2",
                        "disposition": "open", "disposition_basis": "",
                    },
                ],
            },
            {
                "attempt": "R02",
                "verdict": "green",
                "review_kind": "closure_verification",
                "review_epoch": "E01",
                "material_finding_ids": ["F1"],
                "evidence_path": "evidence/review-R02.md",
            },
            {
                "attempt": "R03",
                "verdict": "green",
                "review_kind": "discovery",
                "review_epoch": "E01",
                "material_finding_ids": [],
                "evidence_path": "evidence/review-R03.md",
                "observation_updates": [
                    {"id": "O1", "disposition": "resolved", "basis": "Fixed alongside F1 repair."},
                ],
            },
        ]
        state = derive_observation_state(attempts)
        self.assertEqual(state["O1"]["disposition"], "resolved")
        self.assertEqual(state["O1"]["origin_attempt"], "R01")
        self.assertEqual(state["O1"]["origin_evidence_path"], "evidence/review-R01.md")
        self.assertEqual(state["O2"]["disposition"], "open")
        self.assertEqual(unreconciled_observations(state), frozenset({"O2"}))

        attempts.append({
            "attempt": "R04",
            "verdict": "green",
            "review_kind": "discovery",
            "review_epoch": "E01",
            "material_finding_ids": [],
            "evidence_path": "evidence/review-R04.md",
            "observation_updates": [
                {"id": "O2", "disposition": "tracked", "basis": "Exported as follow-up work item."},
            ],
        })
        self.assertEqual(unreconciled_observations(derive_observation_state(attempts)), frozenset())

    def test_observation_reconciliation_rejects_loss_and_rewrite_vectors(self) -> None:
        base = {
            "attempt": "R01",
            "verdict": "red",
            "review_kind": "discovery",
            "review_epoch": "E01",
            "material_finding_ids": ["F1"],
            "evidence_path": "evidence/review-R01.md",
            "observations": [{
                "id": "O1", "category": "advisory",
                "evidence": "evidence/review-R01.md#O1",
                "disposition": "open", "disposition_basis": "",
            }],
        }

        def updated(update: dict) -> list:
            followup = {
                "attempt": "R02",
                "verdict": "green",
                "review_kind": "discovery",
                "review_epoch": "E01",
                "material_finding_ids": [],
                "evidence_path": "evidence/review-R02.md",
                "observation_updates": [update],
            }
            return [base, followup]

        with self.assertRaisesRegex(ReviewContractError, "unknown observation"):
            derive_observation_state(updated({"id": "O9", "disposition": "resolved", "basis": "No such id."}))
        with self.assertRaisesRegex(ReviewContractError, "terminal disposition"):
            derive_observation_state(updated({"id": "O1", "disposition": "open", "basis": ""}))
        with self.assertRaisesRegex(ReviewContractError, "disposition basis"):
            derive_observation_state(updated({"id": "O1", "disposition": "resolved", "basis": "  "}))

        duplicate = {
            "attempt": "R02",
            "verdict": "green",
            "review_kind": "discovery",
            "review_epoch": "E01",
            "material_finding_ids": [],
            "evidence_path": "evidence/review-R02.md",
            "observations": [{
                "id": "O1", "category": "preference",
                "evidence": "evidence/review-R02.md#O1",
                "disposition": "open", "disposition_basis": "",
            }],
        }
        with self.assertRaisesRegex(ReviewContractError, "already recorded"):
            derive_observation_state([base, duplicate])

        reconciled = updated({"id": "O1", "disposition": "resolved", "basis": "Fixed."})
        reconciled.append({
            "attempt": "R03",
            "verdict": "green",
            "review_kind": "discovery",
            "review_epoch": "E01",
            "material_finding_ids": [],
            "evidence_path": "evidence/review-R03.md",
            "observation_updates": [
                {"id": "O1", "disposition": "deferred", "basis": "Second reconciliation."},
            ],
        })
        with self.assertRaisesRegex(ReviewContractError, "already reconciled"):
            derive_observation_state(reconciled)

    def test_observation_records_require_terminal_originating_attempt(self) -> None:
        pending = {
            "attempt": "R01",
            "verdict": "pending",
            "review_kind": "discovery",
            "review_epoch": "E01",
            "material_finding_ids": [],
            "evidence_path": "",
            "observations": [{
                "id": "O1", "category": "advisory",
                "evidence": "draft note",
                "disposition": "open", "disposition_basis": "",
            }],
        }
        with self.assertRaisesRegex(ReviewContractError, "terminal"):
            derive_observation_state([pending])
        with self.assertRaisesRegex(ReviewContractError, "terminal"):
            finding_severity_records({
                "verdict": "pending",
                "finding_severity": [{"id": "F1", "surface": "correctness", "evidence": "draft"}],
            })
        with self.assertRaisesRegex(ReviewContractError, "terminal"):
            observation_update_records({
                "verdict": "pending",
                "observation_updates": [{"id": "O1", "disposition": "resolved", "basis": "draft"}],
            })

    def test_material_finding_cannot_be_downgraded_to_advisory_within_epoch(self) -> None:
        discovery = {
            "attempt": "R01",
            "verdict": "red",
            "review_kind": "discovery",
            "review_epoch": "E01",
            "material_finding_ids": ["F1"],
            "evidence_path": "evidence/review-R01.md",
        }
        downgrade = {
            "attempt": "R02",
            "verdict": "green",
            "review_kind": "closure_verification",
            "review_epoch": "E01",
            "material_finding_ids": ["F1"],
            "evidence_path": "evidence/review-R02.md",
            "observations": [{
                "id": "F1", "category": "preference",
                "evidence": "evidence/review-R02.md#F1",
                "disposition": "open", "disposition_basis": "",
            }],
        }
        with self.assertRaisesRegex(ReviewContractError, "downgrade"):
            derive_observation_state([discovery, downgrade])

        redesigned = {
            "attempt": "R02",
            "verdict": "green",
            "review_kind": "discovery",
            "review_epoch": "E02",
            "material_finding_ids": [],
            "evidence_path": "evidence/review-R02.md",
            "observations": [{
                "id": "F1", "category": "preference",
                "evidence": "evidence/review-R02.md#F1",
                "disposition": "open", "disposition_basis": "",
            }],
        }
        state = derive_observation_state([discovery, redesigned])
        self.assertIn("F1", state)

        observation_first = {
            "attempt": "R01",
            "verdict": "green",
            "review_kind": "discovery",
            "review_epoch": "E01",
            "material_finding_ids": [],
            "evidence_path": "evidence/review-R01.md",
            "observations": [{
                "id": "O1", "category": "advisory",
                "evidence": "evidence/review-R01.md#O1",
                "disposition": "open", "disposition_basis": "",
            }],
        }
        promoted_reuse = {
            "attempt": "R02",
            "verdict": "red",
            "review_kind": "discovery",
            "review_epoch": "E01",
            "material_finding_ids": ["O1"],
            "evidence_path": "evidence/review-R02.md",
        }
        with self.assertRaisesRegex(ReviewContractError, "downgrade|promoted"):
            derive_observation_state([observation_first, promoted_reuse])


if __name__ == "__main__":
    unittest.main()
