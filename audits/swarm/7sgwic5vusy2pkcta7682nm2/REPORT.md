# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Research return ownership is not bound to its origin, allowing an illegal owner jump

- Affected workflow contract/invariant: `workflow/RESEARCH.md` durable return ownership; `workflow/INTAKE.md` issue prior-art/alignment boundary; `workflow/ROUTER.md` fail-closed routing.
- Expected behavior: Intake-origin Research for an issue repair must return to Intake for once-only reconciliation, and a contradictory origin/return pair must fail closed before any later phase is reachable.
- Actual behavior: `validate_research()` validates `origin_role` and `return_target` independently. A syntactically valid record with `origin_role = "intake"`, the current repair subject, `state = "complete"`, but `return_target = "definition"` is accepted. `select_route()` handles completed Research before Intake and routes directly to Definition from the untrusted `return_target`.
- Minimal reproduction: Start from the valid router fixture; add active issue Intake for `repair:v2` with no diagnosis-prior-art binding and pending alignment; add completed Research with `origin_role = "intake"`, `origin_subject = "repair:v2"`, `return_target = "definition"`, pending reconciliation, and otherwise valid source accounting. The selector reaches `route/definition` instead of Intake/Recovery.
- Why this is materially load-bearing: This can skip the mandatory Intake reconciliation and post-diagnosis user-alignment/authorization boundary and therefore select an illegal later workflow owner.
- Defect class / likely siblings: Missing cross-field authority binding. The same validator also permits Brainstorming/Definition origin-return swaps and execution-origin records whose return prefix/suffix is unrelated to the origin subject.
- Existing tests that failed to catch it: `test_active_and_completed_research_route_to_exact_owner` exercises only matching origin/return pairs; `test_issue_diagnosis_requires_exact_consumed_prior_art_research` uses the expected Intake return.
- Reproduction artifact, if any: `repros/F1_research_return_bypass.py`.

### F2 — Premium A / Planning state is not bound to the current Definition revision

- Affected workflow contract/invariant: `workflow/PLANNING.md` exact planning-cycle entry and full A→Planning→B→Plan Review→C replay on material re-entry; PWV2-REQ-044; stale/contradictory state fail-closed behavior.
- Expected behavior: A changed current Definition must not be able to reuse a Planning cycle and premium-gate satisfaction belonging to an older Definition entry. The exact current Definition-to-Planning handoff must be provable.
- Actual behavior: `validate_definition()` stores only `premium_a = due|satisfied` and has no exact premium-A subject. `validate_planning()` requires only that its self-declared `premium_a_subject` equal its self-declared `entry_subject`; neither is compared with the current Definition revision. `select_route()` performs no such cross-record comparison. A current GREEN Definition R2 can therefore coexist with an approved R1 Planning cycle, GREEN plan review, satisfied B/C, and an active Board, and downstream execution remains selectable.
- Minimal reproduction: Install the normal GREEN Definition/approved-plan fixture, change only the current Definition revision from R1 to R2 while leaving the old Planning entry `definition:R1|planning-cycle:1` and its satisfied gates intact, then route. The stale plan is accepted and the active Board is dispatched.
- Why this is materially load-bearing: A material Definition change can alter accepted authority while execution continues under strategy and premium approvals from the previous Definition, bypassing the required planning/review gate sequence.
- Defect class / likely siblings: Missing cross-record epoch/subject binding between Definition completion, premium A, and Planning entry. Any state writer that accidentally or maliciously retains old Planning state across a Definition revision can pass validation.
- Existing tests that failed to catch it: `test_stale_premium_cycle_and_wrong_review_subject_fail_closed` checks inconsistencies inside Planning/Plan Review but does not vary the current Definition revision against an older Planning entry; planning helpers consistently use Definition R1.
- Reproduction artifact, if any: `repros/F2_stale_definition_planning.py`.

### F3 — “Exact” Git commit/blob identities are trusted without verifying the bytes read

- Affected workflow contract/invariant: `workflow/STATE.md` exact immutable result/dependency identity and same-path-change fail-closed rule; `workflow/EXECUTION_PREP.md` READY launch refresh; `workflow/REVIEW.md` exact reviewed subject + acceptance; `workflow/RECOVERY.md` exact current result refresh.
- Expected behavior: A dependency/result/acceptance that changes at the same path without matching its declared immutable identity must fail closed. GREEN may finalize only the exact bytes and acceptance surface actually reviewed.
- Actual behavior: Result/dependency commit/blob fields are only checked as 40-hex strings. READY refresh compares a Card dependency tuple to the Board’s declared tuple, then reads the current path without hashing or resolving the declared commit/blob. Active-result recovery likewise parses the current result file but constructs `current_subject` solely from the Board’s declared commit/blob. Review acceptance is only a mutable Task Card path. Thus current dependency/result/Card bytes can change while the stale metadata remains unchanged, and the selector still treats the old identity as current.
- Minimal reproduction: (1) Build a READY Card whose dependency tuple exactly matches a DONE predecessor, then change only the predecessor result file contents while leaving both declared tuples unchanged; launch still routes to `execution_prep`. (2) Create a REQUIRED GREEN review for an active result, then mutate the result file and the Task Card acceptance at the same paths without changing the Board/review metadata; routing still reaches `post_review_finalization`.
- Why this is materially load-bearing: This permits execution on stale predecessor evidence and, more seriously, deterministic finalization of result/acceptance bytes that the GREEN review did not cover.
- Defect class / likely siblings: Syntactic identity instead of object verification. The same pattern applies to frozen Planning/Plan Review Git-blob subjects and other locators that claim immutable Git identity without resolving it.
- Existing tests that failed to catch it: `test_ready_card_stale_dependency_fails_closed_before_launch` changes the Board’s declared commit/blob as well as the file, so it tests tuple mismatch rather than same-path content drift. `test_changed_result_after_terminal_review_requires_new_attempt` changes the Board blob, not the underlying result bytes while retaining the old declared identity.
- Reproduction artifact, if any: `repros/F3_unverified_git_identity.py`.

### F4 — A durable explicit user stop can be bypassed once Definition exists

- Affected workflow contract/invariant: `workflow/BRAINSTORMING.md` explicit-user-stop semantics; PWV2-REQ-068; router precedence for real human-owned stops.
- Expected behavior: A durable `explicit_user_stop = true` is a real stop, or a contradictory promoted/downstream state containing that stop must fail closed until the stop is explicitly cleared/reconciled.
- Actual behavior: `validate_brainstorm()` permits `explicit_user_stop = true` together with `state = "promoted"` and authorized promotion. In `select_route()`, Definition/Planning handling occurs before the Brainstorming stop check; with a Definition locator present, the selector can route Planning (and, with an approved plan/Board, execution) without ever honoring the explicit stop.
- Minimal reproduction: Start from the normal promoted GREEN Definition fixture, flip only `explicit_user_stop` from false to true in the promoted Brainstorm record, and route. The selector returns `route/planning`, not a real stop or Recovery.
- Why this is materially load-bearing: The implementation can continue authorized work despite durable state explicitly recording that the user stopped it.
- Defect class / likely siblings: Higher-precedence human stop is checked too late and contradictory state is not rejected. Downstream Definition/Planning/Board routes all sit ahead of the stop check.
- Existing tests that failed to catch it: Brainstorming/Definition router tests use `explicit_user_stop = false`; state-contract tests validate the boolean but do not exercise promoted/downstream state with it set true.
- Reproduction artifact, if any: `repros/F4_explicit_stop_bypass.py`.

## Non-blocking observations

The existing regression suite has useful positive coverage for router precedence, stale metadata tuple changes, RED/review routing, and external-effect recovery. However, several “exact identity” tests use synthetic 40-hex values and prove metadata equality rather than Git-object/content equality. The inspected Close external-effect helper itself appeared fail-closed for pending/uncertain readback cases; no separate material finding was frozen there.

## Coverage

Audit subject remained the immutable commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`. I inspected canonical `workflow/ROUTER.md`, `STATE.md`, `PLANNING.md`, `PLAN_REVIEW.md`, `INTAKE.md`, `RESEARCH.md`, `RECOVERY.md`, `BRAINSTORMING.md`, `EXECUTION_PREP.md`, `REVIEW.md`, and `CLOSE.md`; the accepted requirements; `tools/router.py`, `state_contract.py`, `execution_contract.py`, `recovery_contract.py`, `review_contract.py`, and `close_contract.py`; relevant router/state tests, fixture helpers, schema notes, and the repository test runner. The selected Planning/Premium, Research/Intake, RED/recovery, and router-precedence lenses were all exercised. No `audit/*` branch/report, GitHub Issue, or PR discussion was intentionally inspected.

## Confidence and limitations

Confidence is high in the control-flow/validation counterexamples because they follow directly from the exact production validator and selector and use the repository’s own fixture-building helpers. A fresh command-execution environment was not available during this audit: network cloning was unavailable and the connected remote command service had exhausted its usage quota, so the newly preserved repro scripts could not be executed in-session. They are non-mutating scripts intended to run from a checkout of the exact subject and assert the observed unsafe routes.

Blindness limitation: an early exact-commit metadata fetch unexpectedly returned the merge diff, including historical evidence/review text under `implementation/workstreams/**`, before the independent finding set was frozen. I did not intentionally open those historical files, did not inspect audit branches/reports or tracker discussions, and did not use that material as a checklist; subsequent discovery was confined to the allowed canonical workflow, production tools, tests, schemas/scripts, and fixtures. No post-freeze historical comparison was performed.
