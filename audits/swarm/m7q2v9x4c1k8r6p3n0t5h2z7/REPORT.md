# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Explicit Brainstorming user stop is bypassed once Definition exists

- Affected workflow contract/invariant: `workflow/ROUTER.md` priority foundation and implemented route for explicit user stop; `workflow/BRAINSTORMING.md`; `workflow/USER_STOP.md`.
- Expected behavior: A durable `explicit_user_stop = true` is a highest-precedence real stop. If downstream Definition/Planning state is simultaneously present, the contradiction must not silently authorize continuation; the router should stop or fail closed.
- Actual behavior: `validate_brainstorm()` permits `explicit_user_stop = true` together with `state = "promoted"` and exact promotion authorization. In `select_route()`, Definition is loaded and an active Definition returns `route/definition` before the later Brainstorming branch ever checks `explicit_user_stop`. A GREEN Definition/Planning path can similarly outrun that stop.
- Minimal reproduction: Copy `tests/fixtures/router/valid-project`; add a promoted GREEN Brainstorm with `explicit_user_stop = true`, then add an exact source-bound active Definition. Call `select_route(..., entry="continue")`. The selector returns `route / definition` instead of a real explicit-user-stop boundary. See `repros/router_counterexamples.py::probe_f1_explicit_stop_bypass`.
- Why this is materially load-bearing: An explicit user stop is human authority and is explicitly listed above ordinary stage continuation. Missing it can continue managed work after the user durably asked the workflow to stop.
- Defect class / likely siblings: Cross-module precedence checked only in a fallback branch. Any higher-precedence Brainstorming obligation represented by a state combination that is still validator-legal can be shadowed by Definition/Planning returns.
- Existing tests that failed to catch it: Inspected tests cover Brainstorming promotion and Definition/Premium routing separately, but do not combine `explicit_user_stop = true` with a co-bound Definition/Planning record.
- Reproduction artifact, if any: `repros/router_counterexamples.py`.

### F2 — Implementation Research can return to an unrelated or nonexistent Card

- Affected workflow contract/invariant: `workflow/RESEARCH.md` exact durable return ownership; `workflow/RECOVERY.md` implementation Research handoff; router fail-closed rule for stale/contradictory binding.
- Expected behavior: Task-Board-owned Research must return once to the exact implementation/recovery owner that originated the factual obligation. A return target naming another or nonexistent Card must fail closed.
- Actual behavior: `validate_research()` accepts any string prefixed with `execution:`, `execution_prep:`, or `execution_resolution:` and does not bind the suffix to `origin_subject`, an existing Card, or the origin role. The Task Board check only verifies that `origin_role` is one of the three execution roles. For a complete record with `origin_subject = "M01-T04"` and `return_target = "execution:M99-T99"`, the router returns `route / execution` with subject `M99-T99` before normal Card routing, even though that Card does not exist.
- Minimal reproduction: Add a Board `research_obligation` whose complete Research record uses `origin_role = "execution_resolution"`, `origin_subject = "M01-T04"`, and `return_target = "execution:M99-T99"`. The record validates and routes to execution of `M99-T99`. See `probe_f2_research_return_to_nonexistent_card`.
- Why this is materially load-bearing: The return target can select a workflow owner/Card that has no durable authority, bypassing the actual current Card and corrective owner.
- Defect class / likely siblings: Missing origin-to-return binding. The same validator shape also permits pre-execution origin/return stage mismatches because `origin_role` and `return_target` are independently validated.
- Existing tests that failed to catch it: `test_task_board_research_return_is_recovered_before_execution` uses matching `execution_resolution:M01-T04`; `test_research_requires_all_source_classes_and_once_only_return_state` uses matching Brainstorming origin/return. No inspected negative test changes only the return owner/Card.
- Reproduction artifact, if any: `repros/router_counterexamples.py`.

### F3 — Satisfied Planning gates are not bound to the current Definition revision

- Affected workflow contract/invariant: `workflow/DEFINITION.md`, `workflow/PLANNING.md`, `workflow/PLAN_REVIEW.md`; exact premium-cycle authority and stale-state fail-closed behavior.
- Expected behavior: Strategic Planning and its A/B/C/review approvals must derive from the current GREEN Definition authority. If Definition materially changes from revision R1 to R2, an R1 planning cycle cannot continue to authorize Execution.
- Actual behavior: `validate_planning()` only requires a non-empty `entry_subject` and checks Premium A against that self-declared string. `select_route()` never compares `planning.entry_subject` with the currently loaded Definition revision. A workstream with Definition `revision = "R2"` and a fully approved Planning record whose `entry_subject` and Premium A still say `definition:R1|planning-cycle:1` passes validation; with GREEN Plan Review and satisfied C, the router proceeds into the co-bound active Board/Card and returns Execution.
- Minimal reproduction: Use an exact promoted Brainstorm, GREEN Definition R2, stale approved Planning entered from R1, matching GREEN Plan Review, and the fixture active Board. The selector reaches `route / execution / M01-T04`. See `probe_f3_stale_planning_after_definition_revision`.
- Why this is materially load-bearing: A superseded Definition can leave old plan/review/premium approvals in force, allowing implementation under stale product/requirement authority.
- Defect class / likely siblings: Missing cross-record generation/subject binding. Definition's `premium_a = "satisfied"` also carries no exact Definition-gate subject of its own, increasing reliance on the missing Planning cross-check.
- Existing tests that failed to catch it: `test_planning_cycle_rejects_stale_premium_a_and_orders_b_c` tests stale Premium A inside Planning when the planning cycle changes; router planning tests keep Definition at R1 throughout. No inspected test changes Definition revision while retaining an older satisfied Planning cycle.
- Reproduction artifact, if any: `repros/router_counterexamples.py`.

### F4 — Setting a Card to DONE bypasses REQUIRED review and contradictory blocker state

- Affected workflow contract/invariant: `workflow/REVIEW.md` blocking lifecycle; `workflow/RECOVERY.md`; router rule that invalid/contradictory state fails closed; Close entry semantics.
- Expected behavior: A Card whose stable contract requires review cannot be terminal without exact GREEN review. A terminal Card retaining a blocker is contradictory and must not be treated as cleanly complete.
- Actual behavior: `validate_board()` requires a DONE Card to have a result locator but never parses its Task Card, never requires review attempts/GREEN, and does not forbid a blocker on DONE. After board validation, `select_route()` only performs review/blocker logic for `in_progress` or `blocked` statuses. If all cards are marked DONE, it returns `route / close` without reading the Card contract or review history.
- Minimal reproduction: Write a valid Task Card with `Review requirement: required`, add a durable result, set status directly to `done`, and leave `review_attempts` empty. The router returns Close. See `probe_f4_done_bypasses_required_review`.
- Why this is materially load-bearing: A single board-state edit can bypass the independent review gate entirely and move the workstream into integration/finalization.
- Defect class / likely siblings: Terminal-state validation trusts the status label rather than proving terminal preconditions. DONE + pending/RED review or DONE + human/runtime blocker are sibling contradictory states that are not routed through the active review/blocker checks.
- Existing tests that failed to catch it: `test_required_review_blocks_until_green_then_routes_finalization` keeps the Card `in_progress`; `test_all_terminal_cards_route_to_close_not_directly_to_stop` explicitly uses `Review requirement: none`.
- Reproduction artifact, if any: `repros/router_counterexamples.py`.

### F5 — Commit/blob identity is compared as metadata but never verified against actual bytes

- Affected workflow contract/invariant: immutable result identity in `workflow/RECOVERY.md`; exact dependency refresh in `workflow/EXECUTION_PREP.md`; exact Git-blob subjects in Planning/Review.
- Expected behavior: If a locator claims `path + commit + blob`, the selected artifact must actually be that Git object. Changing the file bytes without changing the locator must make the binding stale and force Recovery/new review.
- Actual behavior: `validate_locator()` checks only that commit/blob strings are 40 lowercase hex. `refresh_ready_card()` compares dependency tuples from Board and Card, then merely reads the current path; it does not resolve the commit or hash the file. For reviewed implementation results, the router parses the current result file but constructs `current_subject` only from the unchanged Board metadata. If the result bytes change after GREEN review while the Board's commit/blob stay unchanged, the old review still matches and the router returns `post_review_finalization`.
- Minimal reproduction: Create an in-progress review-required result and matching GREEN review; verify the route is finalization; mutate only the result file's `Tests/readback summary` while keeping Board/review commit/blob unchanged; route again. It is still `post_review_finalization`. See `probe_f5_file_drift_without_metadata_change`.
- Why this is materially load-bearing: The system's central stale-subject protection can be defeated without changing any claimed identity. Review reuse, dependency launch, and Planning subject integrity can all trust content that is not the immutable object named by canonical state.
- Defect class / likely siblings: Syntactic SHA identity without Git-object resolution. Likely siblings include fabricated/nonexistent SHA tuples and frozen Planning subjects whose path/blob is never resolved.
- Existing tests that failed to catch it: `test_changed_result_after_terminal_review_requires_new_attempt` changes the Board blob metadata; `test_ready_card_stale_dependency_fails_closed_before_launch` changes dependency metadata too. Neither mutates bytes while leaving the claimed immutable tuple unchanged.
- Reproduction artifact, if any: `repros/router_counterexamples.py`.

### F6 — A satisfied JIT trigger is ignored by all-DONE routing to Close

- Affected workflow contract/invariant: `workflow/EXECUTION_PREP.md` JIT lifecycle; router Close/end-of-approved-scope semantics.
- Expected behavior: `jit_trigger.state = "satisfied"` means the predecessor result exists and the downstream Card contract is now due to be materialized. That is an already-authorized obligation, so the workstream cannot be treated as having no executable/remaining work and handed to Close solely because current Cards are DONE.
- Actual behavior: `validate_board()` accepts a satisfied trigger once its predecessor is DONE with a result. The router never inspects trigger state after validation. With every current Card DONE, it returns `route / close` even while a satisfied JIT trigger remains unconsumed.
- Minimal reproduction: Mark fixture M01-T04 DONE with a result and add one `[[jit_triggers]]` entry with `after_card = "M01-T04"`, `state = "satisfied"`. Validation passes; selector routes Close. See `probe_f6_satisfied_jit_ignored_by_close`.
- Why this is materially load-bearing: Close can begin while deterministic in-scope execution materialization is still due, contradicting the rule that completion of current Cards is not itself end of approved scope.
- Defect class / likely siblings: Task Board lifecycle state validated locally but omitted from routing precedence. A malformed `consumed` trigger without the promised downstream Card is another state the current validator cannot correlate.
- Existing tests that failed to catch it: `test_jit_trigger_preserves_predecessor_boundary_without_placeholder_card` validates `waiting -> satisfied` but does not route it; the inspected Close router test has all Cards DONE but no JIT trigger.
- Reproduction artifact, if any: `repros/router_counterexamples.py`.

### F7 — GREEN review can finalize with a nonexistent durable evidence artifact

- Affected workflow contract/invariant: `workflow/REVIEW.md` durable terminal verdict evidence; `workflow/PLAN_REVIEW.md` terminal evidence locator; recovery integrity.
- Expected behavior: A terminal GREEN/RED attempt must have durable, readable evidence. A missing/stale evidence artifact must fail closed rather than authorize finalization/approval.
- Actual behavior: `validate_review()` and `validate_plan_review()` require only a non-empty safe relative `evidence_path`; neither validates the locator class/root nor reads the target. The implementation router reads review attempt TOML files but never reads terminal evidence. Thus a GREEN implementation review whose evidence path does not exist still routes `post_review_finalization`. The same shape is accepted by Plan Review before Planning consumes GREEN.
- Minimal reproduction: Install a valid review-required result and GREEN review attempt, set `evidence_path` to a workstream-local path but do not create that file. The router still returns `post_review_finalization`. See `probe_f7_missing_review_evidence_still_green`.
- Why this is materially load-bearing: Terminal approval becomes unrecoverable/unverifiable while still authorizing state transition. This undermines the durable review gate rather than merely losing optional documentation.
- Defect class / likely siblings: Locator-shaped proof is trusted without existence/currentness verification. Result evidence refs are similarly parsed for path shape without being read by result reconciliation.
- Existing tests that failed to catch it: `test_review_terminal_evidence_and_append_only_history` checks that terminal `evidence_path` is non-empty, not that it exists. Router review tests create evidence for GREEN/RED and therefore do not exercise the missing-artifact case.
- Reproduction artifact, if any: `repros/router_counterexamples.py`.

## Non-blocking observations

No advisory/style items were retained as findings. The inspected external-effect recovery oracle itself correctly fails closed for uncertain occurrence and requires verified `no_effect` before retry; tracker `create_pending_readback` routing likewise preserves readback-before-retry semantics in the inspected paths.

## Coverage

The audit remained bound to subject commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045` for source inspection.

Inspected canonical/runtime code included:
- `workflow/ROUTER.md`, `INTAKE.md`, `RESEARCH.md`, `BRAINSTORMING.md`, `DEFINITION.md`, `PLANNING.md`, `PLAN_REVIEW.md`, `EXECUTION_PREP.md`, `EXECUTION.md`, `REVIEW.md`, `RECOVERY.md`, `CLOSE.md`, `GITHUB_ISSUES.md`, and `USER_STOP.md`;
- `tools/router.py`, `state_contract.py`, `execution_contract.py`, `recovery_contract.py`, and `close_contract.py`;
- `tests/test_router.py`, `test_state_contract.py`, `test_execution_contract.py`, `test_recovery_contract.py`, `test_close_contract.py`, plus exact router/state fixtures used by inspected tests.

Selected attack lenses exercised:
- Planning / Premium gates / Execution precedence: F1, F3.
- malformed or contradictory state / fail-closed behavior: F1, F4, F6, F7.
- Research / Intake / tracker / external-side-effect recovery: F2; tracker/external-effect negative paths were also inspected without retaining an additional defect.
- review independence / review bypass / result mutation: F4, F5, F7.

Additional negative-space coverage included READY dependency refresh, all-DONE Close entry, JIT trigger lifecycle, result subject refresh, Plan Review acceptance/evidence shape, blocker routing, tracker ambiguity/readback, and end-of-approved-scope helper behavior.

## Confidence and limitations

Confidence is high on the seven reported code-path defects because each follows a short deterministic path through the exact frozen selector/validators and has a minimal executable reproduction preserved in `repros/router_counterexamples.py`.

The available local execution environment did not contain an exact repository checkout, network cloning was unavailable, and the connected remote terminal had exhausted its monthly command quota. Therefore the preserved repro script was syntax-checked locally with `python3 -m py_compile`, but the real `tools.router.select_route` probes could not be executed in this chat environment. Actual routes stated above are derived directly from the exact target source and the same fixture-construction patterns used by the repository's tests.

No `audit/*` branches, swarm reports, GitHub Issues, or PR comments were inspected. Historical workstream evidence/review trees were not intentionally inspected or used for discovery. A commit-metadata request made only to prepare persistence unexpectedly included part of the target commit diff, including one historical implementation evidence snippet unrelated to these seven findings; it was not used to add, remove, rank, or reclassify the frozen finding set.

No post-freeze historical comparison was performed.
