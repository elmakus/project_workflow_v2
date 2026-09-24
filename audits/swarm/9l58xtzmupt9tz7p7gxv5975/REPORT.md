# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Declared commit/blob identity is not verified against current result bytes

- Affected workflow contract/invariant: `workflow/STATE.md` requires READY dependencies to be bound by exact result path + immutable commit/blob identity and says missing, stale, or same-path-changed dependency inputs fail closed; `workflow/RECOVERY.md` requires review subject refresh against the exact current result; `workflow/REVIEW.md` permits GREEN finalization only for the exact current immutable subject.
- Expected behavior: if a dependency/result file changes at the same path while its Board-declared commit/blob values remain unchanged, launch or post-review finalization must fail closed or require a new exact subject/review.
- Actual behavior: `refresh_ready_card()` compares only the dependency tuple declared in the Task Card with the tuple declared in the Task Board, then reads the current path without checking that its bytes correspond to the declared blob/commit. The active-result path similarly parses the current file but derives `current_subject` only from Board strings; a GREEN review whose strings match those stale declarations still routes to `post_review_finalization`.
- Minimal reproduction: create a REQUIRED reviewed result with GREEN R01, then replace the result file at the same path with different but syntactically valid Card Result content while leaving Board/review commit/blob values unchanged. The selector reaches `route/post_review_finalization`. Sibling: mutate a DONE predecessor result file at the same path while leaving both Task Card dependency identity and Board identity unchanged; READY refresh still reaches `route/execution_prep`.
- Why this is materially load-bearing: immutable identity is the safety boundary that prevents changed implementation/dependency content from inheriting prior review or readiness. String agreement between two stale records is not proof of the referenced Git object.
- Defect class / likely siblings: stale immutable-identity trust / TOCTOU. Any path whose commit/blob identity is accepted without resolving the actual Git object is suspect; review acceptance is also path-only and therefore deserves the same class of scrutiny.
- Existing tests that failed to catch it: `test_ready_card_stale_dependency_fails_closed_before_launch` changes the Board commit/blob as well as the file, so it exercises metadata mismatch rather than same-path byte mutation. `test_changed_result_after_terminal_review_requires_new_attempt` changes the Board blob, not the reviewed file while metadata stays stale.
- Reproduction artifact, if any: `audits/swarm/9l58xtzmupt9tz7p7gxv5975/repros/repro_router_state_gaps.py` (`f1_same_path_result_mutation_keeps_green_review`).

### F2 — Terminal evidence locators are accepted without dereferencing durable evidence

- Affected workflow contract/invariant: `workflow/EXECUTION.md` requires an accepted semantic result to carry durable evidence; `workflow/REVIEW.md` requires durable verdict evidence for terminal attempts; `workflow/PLAN_REVIEW.md` requires terminal Plan Review evidence; `workflow/AUTHORITY.md` requires missing required references to fail closed.
- Expected behavior: a terminal result/review whose referenced evidence file is absent or unreadable must not be reconciled, approved, or finalized.
- Actual behavior: `parse_card_result()` validates only the syntax/root of Evidence refs. `validate_review()` and `validate_plan_review()` require a non-empty safe `evidence_path` for terminal verdicts but do not read it. The router does not dereference those evidence locators before result reconciliation, GREEN finalization, RED correction, or Plan Review consumption.
- Minimal reproduction: create a REQUIRED result plus GREEN review using the normal router fixture helpers, delete both the Card Result evidence file and GREEN review evidence file, then call the production selector. It still reaches `route/post_review_finalization`.
- Why this is materially load-bearing: a terminal verdict or accepted result can become durable authority with no durable proof behind its evidence locator, allowing lost/fabricated evidence to pass gates that are explicitly evidence-backed.
- Defect class / likely siblings: locator-existence / evidence-integrity fail-open. The same class applies to implementation result evidence, implementation review terminal evidence, and Plan Review terminal evidence.
- Existing tests that failed to catch it: implementation-result/review tests materialize evidence and never delete it. `test_green_plan_review_consumes_to_c_before_execution_prep` supplies a terminal Plan Review evidence path but does not materialize that file, yet expects Planning consumption, so the suite itself demonstrates the missing dereference without asserting against it.
- Reproduction artifact, if any: `audits/swarm/9l58xtzmupt9tz7p7gxv5975/repros/repro_router_state_gaps.py` (`f2_missing_terminal_evidence_is_not_dereferenced`).

### F3 — Active Research short-circuits a higher-precedence explicit user stop

- Affected workflow contract/invariant: the router priority foundation puts `explicit_human_or_premium_boundary` before `research_return`; `workflow/BRAINSTORMING.md` says an explicit user stop is a real stop; `workflow/ROUTER.md` says real stops must be honored rather than bypassed by lower-precedence work.
- Expected behavior: when the current Brainstorm record carries `explicit_user_stop = true`, an independently valid co-bound active Research record must not cause Research continuation ahead of that stop.
- Actual behavior: `select_route()` loads the workstream-level Research record immediately after the manifest and returns `route/research` for `state = active` before it reads the Brainstorm record at all. Therefore the explicit stop is unreachable on that state combination.
- Minimal reproduction: add a valid active Brainstorm record with `explicit_user_stop = true` and a valid active Brainstorm-origin Research record. The selector returns `route/research`, and the read set does not contain `BRAINSTORM.toml`.
- Why this is materially load-bearing: a durable human stop is an authority boundary. Allowing lower-precedence factual work to bypass it violates the router's own precedence contract and can continue work the user explicitly stopped.
- Defect class / likely siblings: premature return / unread higher-precedence state. Any higher-precedence stop stored in a record that is read after the unconditional Research return is a sibling risk; premium gates warrant the same negative-space test.
- Existing tests that failed to catch it: `test_active_and_completed_research_route_to_exact_owner` has no competing stop. `test_priority_and_real_stop_foundations_are_runtime_neutral` asserts the precedence constants but does not test that control flow implements their ordering.
- Reproduction artifact, if any: `audits/swarm/9l58xtzmupt9tz7p7gxv5975/repros/repro_router_state_gaps.py` (`f3_research_short_circuits_explicit_user_stop`).

### F4 — Definition can bind to a Brainstorm revision whose lifecycle is not promoted

- Affected workflow contract/invariant: `workflow/BRAINSTORMING.md` defines `active -> ready_for_definition -> promoted` lifecycle semantics and says the exact promoted revision enters Definition; `workflow/DEFINITION.md` states Definition requires the exact promoted Brainstorming subject; `workflow/ROUTER.md` requires stale/contradictory binding to fail closed.
- Expected behavior: a Definition locator is legal only when the referenced Brainstorm record is actually in `state = promoted` for the exact authorized subject.
- Actual behavior: `validate_brainstorm()` allows `state = active` together with `promotion_state = authorized` and exact `promotion_subject`. The router's Definition cross-record check verifies only promotion_state/subject/source_subject, not `brainstorm.state == "promoted"`. A GREEN Definition attached to such an active Brainstorm can route onward to Planning.
- Minimal reproduction: install the normal GREEN Definition fixture, change only `BRAINSTORM.toml` from `state = "promoted"` to `state = "active"`, leaving exact promotion authorization intact. Both records validate and the selector returns `route/planning`.
- Why this is materially load-bearing: the lifecycle transition itself is part of durable promotion authority. Accepting a downstream Definition while the upstream scope is still active permits contradictory state to skip the owner that is supposed to control exploration/promotion.
- Defect class / likely siblings: cross-record lifecycle binding omission. Variants include `ready_for_definition` with authorized promotion and an active record additionally carrying an explicit stop.
- Existing tests that failed to catch it: `test_brainstorming_requires_challenge_and_exact_definition_promotion` tests clean pending/promoted cases; `test_definition_source_mismatch_fails_closed` tests only subject mismatch, not lifecycle mismatch with matching subject.
- Reproduction artifact, if any: `audits/swarm/9l58xtzmupt9tz7p7gxv5975/repros/repro_router_state_gaps.py` (`f4_definition_accepts_non_promoted_brainstorm_state`).

### F5 — `done` Card status can enter Close without validating result or required review

- Affected workflow contract/invariant: `workflow/STATE.md` says REQUIRED/activated RECOMMENDED review blocks terminal Card completion until exact GREEN; `workflow/REVIEW.md` says no attempt/pending/in-progress/RED blocks terminal completion; `workflow/CLOSE.md` requires result/review/evidence recovery artifacts before terminal integration; invalid/missing/contradictory bindings must fail closed.
- Expected behavior: a Card persisted as `done` must be rejected or recovered unless its result exists/validates and its stable Card review requirement is terminally satisfied.
- Actual behavior: `validate_board()` requires a `result` locator for `done` but does not read the result, parse the Card contract, or validate review history/requirement. After active/blocked/READY dispatch, the router checks only `all(card["status"] == "done")` and routes directly to Close.
- Minimal reproduction: create a Card contract with `Review requirement: required` and a result locator, add no review attempt, change status from `in_progress` to `done`, delete the result file, and select a route. The selector still returns `route/close`.
- Why this is materially load-bearing: a contradictory terminal bit can bypass both recovery truth and the blocking independent-review gate, moving invalid execution state into finalization.
- Defect class / likely siblings: terminal-state trust / incomplete cross-record validation. Any DONE Card with a missing/stale result, unsatisfied review, stale acceptance, or missing evidence can be misclassified as terminal.
- Existing tests that failed to catch it: `test_all_terminal_cards_route_to_close_not_directly_to_stop` uses a present result and `Review requirement: none`; there is no negative terminal test with REQUIRED review absent or result target missing.
- Reproduction artifact, if any: `audits/swarm/9l58xtzmupt9tz7p7gxv5975/repros/repro_router_state_gaps.py` (`f5_done_card_bypasses_result_and_review_validation`).

### F6 — SessionStart treats marker-preserving corrupted/stale router text as canonical

- Affected workflow contract/invariant: `skills/project_workflow_v2/SKILL.md` says a missing, malformed, ambiguous, or escaping installed router must fail closed; `hooks/session-start.py` describes itself as a fail-closed bootstrap and must not silently accept bootstrap drift.
- Expected behavior: a truncated/corrupted or incompatible stale router must emit the blocking plugin-package error rather than assert that PWv2 is enabled.
- Actual behavior: `canonical_router()` accepts any readable in-root file containing only two sentinel substrings: the router heading and `Production selector: tools/router.py`. A file containing those two lines plus arbitrary corrupted/truncated body is accepted as canonical. An exact-copy execution of the subject hook with such a router emitted normal `Project Workflow V2 package is enabled` context.
- Minimal reproduction: copy the production SessionStart hook into a temporary package, replace `workflow/ROUTER.md` with the two required sentinel lines plus `CORRUPTED/TRUNCATED POLICY BODY`, set `PLUGIN_ROOT` to that package, and execute the hook. It returns normal enabled bootstrap context, not a BLOCKING error.
- Why this is materially load-bearing: SessionStart is the authority-root bootstrap. Marker-preserving corruption or an older incompatible router can be trusted as current policy, after which missing semantics may be supplied by runtime behavior or memory—the exact drift the bootstrap contract is intended to prevent.
- Defect class / likely siblings: weak package-content identity / update drift. Any stale router version retaining the two sentinels is accepted; the hook also does not bind router bytes to plugin/package version or a manifest digest.
- Existing tests that failed to catch it: `test_missing_and_malformed_router_fail_closed` uses `not a V2 router`, which removes both sentinels. Delivery tests verify package metadata separately but never make SessionStart verify router content/version identity.
- Reproduction artifact, if any: `audits/swarm/9l58xtzmupt9tz7p7gxv5975/repros/repro_sessionstart_marker_corruption.py`.

## Non-blocking observations

- No additional style-only or speculative redesign items are promoted to findings.
- The router's precedence constants are useful executable documentation, but tests that assert only their tuple contents do not prove the selector's return ordering.

## Coverage

The audit stayed bound to subject commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`. Inspection covered canonical routing/state/planning/plan-review/recovery/execution-prep/execution/review/Close/Research/Brainstorming/Definition/authority contracts; production router, state, execution, review, recovery and Close helpers; SessionStart/Skill/plugin packaging; relevant templates; router/state/execution/review/recovery/Close/delivery tests; and the current router fixture.

The selected lenses were exercised as follows:

- plugin / install / update / SessionStart / bootstrap drift: F6;
- stale commit/blob/path/result/review identity: F1, F2, F5;
- Planning / Premium gates / Execution precedence: F2, F3, F4;
- RED / recovery / blocker / interrupted-runtime continuation: F1, F2, F5, plus inspection of RED/blocker/Research-return dispatch.

Negative-space cases were derived against the production selector/validators rather than treating existing GREEN tests as proof. The preserved repro scripts mutate only temporary fixture/package copies and do not modify product code.

## Confidence and limitations

Confidence is high on the demonstrated control-flow/state-contract mismatches because each finding follows a direct production branch that lacks the required cross-record/content check, and F6 was executed with an exact copy of the subject hook source: marker-preserving corruption produced normal enabled bootstrap context.

A full local execution of F1-F5 against the immutable checkout could not be completed in this chat environment. The ordinary shell could not resolve GitHub for cloning; the connected Desktop Commander device reported its monthly tool-call allowance exhausted and explicitly requested no retry; the available native Codex command bridge required an unavailable valid outer turn token. The GitHub commit-run lookup returned no PR-triggered workflow run for the exact merge subject. The checked-in repro script is designed to run directly from an exact checkout and imports the production selector plus the repository's own router fixture helpers.

Blindness limitation: the first immutable-commit metadata fetch unexpectedly embedded changed-file patches, including historical `implementation/workstreams/**/evidence/**` material, before finding freeze. No `audit/*` branch/report, GitHub Issue, or PR discussion was inspected, and the frozen findings above were derived from canonical workflow/tools/tests rather than using that embedded historical material as a checklist. No post-freeze historical comparison was performed.

## Post-freeze historical comparison

Not performed.
