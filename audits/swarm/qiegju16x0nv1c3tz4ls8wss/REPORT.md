# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Terminal `done` Card state bypasses REQUIRED/RED review gates

- Affected workflow contract/invariant: PWV2-REQ-034/036; `workflow/STATE.md` independent-review gate; router rule that REQUIRED/activated RECOMMENDED review blocks terminal Card completion until exact GREEN.
- Expected behavior: A Card whose stable contract requires review must not be accepted as terminal merely because mutable Board status says `done`. Missing, pending, in-progress, stale, or RED required review state must fail closed or route to its review/recovery owner before Close.
- Actual behavior: `validate_board()` requires only a result locator for `status = "done"`; it does not read the Task Card review requirement or validate its review history. `select_route()` only evaluates review state for `in_progress` Cards. With all Cards marked `done`, it routes directly to `close`, even when the Card requires review and its referenced current attempt is RED or pending.
- Minimal reproduction: Start from the valid router fixture, install a valid result, set the Card contract to `Review requirement: required`, append a RED review attempt, then change only Board status from `in_progress` to `done`. The Board validator accepts it and the router reaches `route/close`.
- Why this is materially load-bearing: Mutable status can erase a mandatory safety gate. Recovery from contradictory or partially written durable state therefore fails open and can advance to final integration despite an unresolved RED or nonterminal required review.
- Defect class / likely siblings: Terminal-state trust without terminal-proof validation; any writer/interrupted reconciliation that sets `done` early can bypass review. Sibling risk exists for other completion prerequisites represented outside the status scalar.
- Existing tests that failed to catch it: `test_required_review_blocks_until_green_then_routes_finalization` keeps the Card `in_progress`; `test_all_terminal_cards_route_to_close_not_directly_to_stop` uses `Review requirement: none`. No test combines `done` with REQUIRED + missing/pending/RED review.
- Reproduction artifact, if any: `repros/repro_router_state_holes.py` (`f1_done_bypasses_required_red_review`).

### F2 — A satisfied JIT trigger can be skipped by all-DONE Close routing

- Affected workflow contract/invariant: PWV2-REQ-028; `workflow/EXECUTION_PREP.md` JIT lifecycle; `workflow/CLOSE.md` end-of-approved-scope rule.
- Expected behavior: When a predecessor-dependent JIT trigger is `satisfied`, its DONE predecessor result has made the downstream Card boundary knowable. Execution Prep must materialize/refine that accepted downstream work before the workstream can be treated as complete.
- Actual behavior: `validate_board()` accepts a `satisfied` trigger when its predecessor is DONE with a result. The router never dispatches on JIT trigger state after Board validation. If all currently materialized Cards are DONE, it returns `route/close` before the satisfied trigger is consumed/materialized.
- Minimal reproduction: Mark the fixture Card DONE with a valid result and add one top-level JIT trigger with `after_card` pointing to that Card and `state = "satisfied"`. Validation succeeds; `select_route()` routes Close.
- Why this is materially load-bearing: The current Card queue is not the approved scope. This path can finalize a workstream while an already-authorized downstream obligation is explicitly present in durable state.
- Defect class / likely siblings: Queue-emptiness/terminal-Card inference outruns Task Board latent obligations. Waiting/satisfied/consumed trigger combinations near terminal milestones are the sibling space.
- Existing tests that failed to catch it: `test_jit_trigger_preserves_predecessor_boundary_without_placeholder_card` exercises only `validate_board()`; `test_all_terminal_cards_route_to_close_not_directly_to_stop` has no JIT trigger. There is no router assertion for DONE Cards plus satisfied trigger.
- Reproduction artifact, if any: `repros/repro_router_state_holes.py` (`f2_satisfied_jit_trigger_is_skipped_by_close`).

### F3 — Declared commit/blob identities are trusted without verifying repository bytes

- Affected workflow contract/invariant: PWV2-REQ-030/031/034; `workflow/STATE.md` exact dependency-result launch refresh and immutable result/review identity.
- Expected behavior: A declared `path + commit + blob` identity must bind to the actual Git object/bytes it claims. Same-path byte changes under an unchanged durable identity must fail closed before launch, reconciliation, or review reuse.
- Actual behavior: READY dependency refresh compares the Card dependency tuple only against the Board's declared DONE-result tuple, then reads the current filesystem path without verifying its Git blob. Active result handling likewise parses current file bytes but constructs the immutable review subject solely from the Board-declared commit/blob. No production path shown verifies that the bytes read are the blob named by the durable locator.
- Minimal reproduction: Install a valid semantic result, set the Board's declared blob to the actual initial Git-blob digest, route once, then modify the result bytes while leaving the Board locator untouched. The selector still accepts the result and returns the same reconciliation route even though the current bytes have a different Git-blob digest. The same trust pattern exists for READY predecessor dependencies.
- Why this is materially load-bearing: Exact immutable identity is the recovery/review authority boundary. If bytes can drift independently of the recorded identity, stale review coverage and stale dependency proofs can silently attach to different content.
- Defect class / likely siblings: Locator-string equality substituted for object verification. Likely siblings include Task Card/authority/technical-contract freshness where only path readability is checked.
- Existing tests that failed to catch it: `test_ready_card_stale_dependency_fails_closed_before_launch` changes the Board's declared commit/blob so tuple equality fails; it does not change bytes while leaving the declared identity unchanged. Result tests use fabricated 40-hex identities and assert successful routing without verifying them against repository objects.
- Reproduction artifact, if any: `repros/repro_router_state_holes.py` (`f3_changed_result_bytes_keep_stale_declared_blob_valid`).

### F4 — Planning remains executable after the current Definition revision changes

- Affected workflow contract/invariant: PWV2-REQ-040/044 and the Planning exact-cycle/entry-subject contract; `workflow/PLANNING.md` material re-entry must repeat A -> Planning -> B -> Plan Review -> C.
- Expected behavior: Existing Planning authority must be proven to originate from the current accepted Definition revision. A materially changed Definition cannot continue using a prior Definition's approved Plan and satisfied premium gates.
- Actual behavior: `validate_planning()` only requires a nonempty `entry_subject` and binds `premium_a_subject` to that same string. The router validates Definition and Planning independently but never checks that Planning's entry subject names the current Definition revision. A current GREEN Definition `R2` can therefore coexist with an approved, GREEN-reviewed, C-satisfied Planning record whose entry remains `definition:R1|planning-cycle:1`; routing can proceed directly to the live Board/Execution.
- Minimal reproduction: Install the test helper's approved R1 Plan, then change only `DEFINITION.toml revision = "R1"` to `"R2"`, preserving an otherwise valid GREEN Definition. The stale R1 Planning record still validates and the router reaches `route/execution`.
- Why this is materially load-bearing: This permits execution under a stale strategy/acceptance basis after current Definition authority changed, bypassing the new premium/planning/review sequence intended to protect material re-entry.
- Defect class / likely siblings: Missing cross-record subject binding between adjacent lifecycle owners; revision strings are locally valid but globally contradictory.
- Existing tests that failed to catch it: Planning tests mutate `cycle`/`entry_subject` inside the Planning record and correctly catch stale Premium A there; they do not vary current Definition revision while retaining stale Planning.
- Reproduction artifact, if any: `repros/repro_router_state_holes.py` (`f4_stale_planning_survives_definition_revision_change`).

### F5 — Close review reuse treats an acceptance-surface shrink as unchanged coverage

- Affected workflow contract/invariant: PWV2-REQ-038/063; `workflow/CLOSE.md` refresh/review-reuse rule requiring a new immutable subject when required acceptance materially changes.
- Expected behavior: Material change to the required acceptance surface must create a new review subject. Reuse is safe only when the current final subject/acceptance surface is unchanged and fully covered.
- Actual behavior: `classify_review_coverage()` flags acceptance change only when `current.acceptance` is not a subset of `reviewed.acceptance`. Removing a required acceptance item therefore counts as reusable GREEN if content/behavior fingerprints match and compatibility verification is GREEN. The repository test `test_stronger_review_coverage_may_be_reused` explicitly locks in this one-way subset behavior.
- Minimal reproduction: Reviewed acceptance `{required-A, required-B, removed-required-C}`; current acceptance `{required-A, required-B}`; same content/behavior; affected compatibility GREEN. Helper returns `reuse_green_review` although the acceptance set changed.
- Why this is materially load-bearing: Acceptance requirements are review authority, not optional test decoration. A changed final acceptance contract can be finalized under a review frozen against a different exact acceptance surface, contrary to the documented exact-subject rule.
- Defect class / likely siblings: Coverage-superset logic conflates "old review was stricter" with "current acceptance is the same immutable review surface." Any removal/renaming/reclassification of acceptance obligations is exposed.
- Existing tests that failed to catch it: The relevant test does not merely miss the case; it asserts the conflicting behavior as correct, creating executable-vs-requirements parity drift.
- Reproduction artifact, if any: `repros/repro_close_acceptance_shrink.py`.

### F6 — SessionStart accepts a semantically destroyed router when two marker strings survive

- Affected workflow contract/invariant: PWV2-REQ-008/010/013; Skill/SessionStart fail-closed bootstrap contract.
- Expected behavior: Missing, malformed, ambiguous, or corrupted installed canonical router authority must block bootstrap rather than tell Codex the V2 package is enabled.
- Actual behavior: `canonical_router()` accepts any readable in-root `workflow/ROUTER.md` containing only two literal substrings: the header and the production-selector sentence. A router reduced to those markers plus arbitrary text is declared canonical/enabled even though all routing semantics are absent.
- Minimal reproduction: Install an otherwise normal temporary hook package whose `ROUTER.md` contains `# Project Workflow V2 Router`, a sentence saying no semantics exist, and `Production selector: \`tools/router.py\`.`. SessionStart emits `Project Workflow V2 package is enabled` rather than the BLOCKING fail-closed context.
- Why this is materially load-bearing: Codex ordinary authority comes from the installed bundle. Marker-preserving truncation, partial update, or corruption can silently leave the runtime with no canonical policy while bootstrap positively asserts authority is valid.
- Defect class / likely siblings: Sentinel-presence validation used as integrity validation; package payload skew that preserves markers can fail open.
- Existing tests that failed to catch it: `test_missing_and_malformed_router_fail_closed` tests a missing router and content `not a V2 router`, which removes the sentinels. No negative test preserves the sentinels while destroying semantics.
- Reproduction artifact, if any: `repros/repro_session_start_marker_failopen.py`.

### F7 — Active Research outranks a durable explicit user stop

- Affected workflow contract/invariant: PWV2-REQ-067/068; `workflow/BRAINSTORMING.md` explicit-user-stop contract; router priority foundation putting explicit human/premium boundaries ahead of lower obligations.
- Expected behavior: Once the current Brainstorming record carries `explicit_user_stop = true`, the next route is a real stop. An already active fact-gathering obligation must not silently continue past that human-owned boundary.
- Actual behavior: The router loads and dispatches workstream-level Research before it reads Brainstorming. Any valid `RESEARCH.toml state = "active"` therefore returns `route/research` immediately, making a co-bound Brainstorming explicit stop unreachable.
- Minimal reproduction: Add a valid active Brainstorming record with `explicit_user_stop = true` and a valid active Research record returning to that Brainstorming subject. Both records validate; `select_route()` returns `route/research`, not `stop/explicit_user_stop`.
- Why this is materially load-bearing: A durable human stop is a top-level authority boundary. Continuing autonomous work after it is recorded violates the workflow's human-control semantics and its own declared precedence foundation.
- Defect class / likely siblings: Progressive-read ordering preempts higher-priority state stored in a later owner; other human/premium boundaries coexisting with active lower-level records deserve sibling probes.
- Existing tests that failed to catch it: Research return/ownership tests and explicit-stop behavior are not combined into one contradictory-but-validator-legal durable state. No precedence test exercises active Research plus explicit Brainstorming stop.
- Reproduction artifact, if any: `repros/repro_router_state_holes.py` (`f7_active_research_preempts_explicit_user_stop`).

## Non-blocking observations

- The exact target's deterministic helpers are generally small and make useful negative-space testing possible; the main defects above arise where individually valid local records are combined without a cross-record invariant.
- Several existing tests use synthetic 40-hex commit/blob strings. That is useful for parser tests but can mask the distinction between "well-shaped identity" and "identity verified against Git truth."

## Coverage

The audit remained bound to commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`.

Inspected canonical workflow/authority surfaces included `workflow/ROUTER.md`, `STATE.md`, `CLOSE.md`, `PLANNING.md`, `PLAN_REVIEW.md`, `EXECUTION_PREP.md`, `BRAINSTORMING.md`, `RESEARCH.md`, `DEFINITION.md`, `USER_STOP.md`, and `requirements/PROJECT_WORKFLOW_V2.md`.

Inspected executable/helper surfaces included `tools/router.py`, `state_contract.py`, `close_contract.py`, `execution_contract.py`, `recovery_contract.py`, and `review_contract.py`. Negative-space test coverage was compared against `tests/test_router.py`, `test_state_contract.py`, `test_close_contract.py`, `test_codex_delivery.py`, and `test_chatgpt_delivery.py`, plus the allowed router/state fixtures.

Bootstrap/package inspection covered `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, `hooks/hooks.json`, `hooks/session-start.py`, `skills/project_workflow_v2/SKILL.md`, and `scripts/test-plugin-probe.sh`.

Selected lens exercise:
- Close/finalization: F1, F2, F5.
- Helper/document parity and negative space: F1-F7, especially F5.
- Planning/Premium/Execution precedence: F2, F4, F7.
- Plugin/install/SessionStart/bootstrap drift: F6.

## Confidence and limitations

Confidence is high for the demonstrated control-flow/state-validation defects: they follow directly from exact target blobs, and the preserved repros instantiate the smallest validator-legal combinations using the repository's own fixture helpers. The SessionStart marker-preserving failure was also reproduced independently in a temporary package using the target hook logic.

A full local `scripts/test.sh` plus all preserved repro scripts could not be executed in this audit environment: the authorized remote Desktop Commander had exhausted its monthly execution quota, and the local sandbox had no network checkout path. Exact source blobs and branch writes were therefore performed through the GitHub connector. The repro artifacts are designed to run without product-code modification from an exact checkout of the subject.

Blindness limitation: the initial GitHub exact-commit metadata fetch automatically included the merge commit's diff, which exposed some historical workstream/evidence text before the finding set was frozen. That exposure was incidental, was not used as a defect checklist or finding source, and no audit branches, swarm reports, Issues, PR comments, or further historical evidence/reviews were inspected. The seven findings above were derived independently from the allowed canonical contracts, production helpers, tests, and fresh adversarial combinations. No post-freeze historical comparison was performed.
