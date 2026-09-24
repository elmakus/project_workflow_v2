# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Declared result Git identity is never verified against the result bytes

- Affected workflow contract/invariant: `workflow/STATE.md` READY dependency identity and durable-result recovery; `workflow/EXECUTION_PREP.md` launch refresh; `workflow/REVIEW.md` exact immutable review subject; PWV2-REQ-030/031/034/036.
- Expected behavior: A result/dependency locator carrying path + commit + blob must identify the bytes actually consumed. If the same path changes after review, or a dependency's bytes no longer match its immutable locator, routing must fail closed or freeze a new exact review subject before execution/finalization.
- Actual behavior: `tools/router.py` reads current result/dependency paths but never verifies the declared commit/blob against Git content. For an active reviewed Card, `current_subject` is built entirely from the Task Board locator. A result file can therefore be edited after GREEN while the Board locator and review attempt remain unchanged, and the selector still returns `route/post_review_finalization`. The same primitive exists in READY dependency refresh: tuple equality is checked only between Card text and Board metadata, then the current path is read without content-identity verification.
- Minimal reproduction: From the official router fixture, install a REQUIRED reviewable result and matching GREEN attempt; verify `post_review_finalization`; then edit only `results/M01-T04.md` while leaving the Board `commit/blob` and review subject unchanged. Calling the production selector again still yields `post_review_finalization`. Sibling: a READY Card whose dependency tuple still equals the DONE predecessor locator remains launchable after only the predecessor result file bytes are changed.
- Why this is materially load-bearing: Exact immutable subjects are the safety boundary that prevents stale review reuse and stale predecessor input. Self-asserted SHA fields without verification let changed content inherit prior GREEN/recovery authority.
- Defect class / likely siblings: Unverified immutable locator identity. Likely siblings include any path+commit+blob state that is compared as strings but consumed from the working tree without hashing/fetching the named Git object.
- Existing tests that failed to catch it: `test_changed_result_after_terminal_review_requires_new_attempt` changes the Board blob field rather than mutating bytes under an unchanged locator. `test_ready_card_stale_dependency_fails_closed_before_launch` changes both Board identity and file content rather than file content alone.
- Reproduction artifact, if any: `repros/repro_router_counterexamples.py --case F1`.

### F2 — GREEN review acceptance is not bound to the selected Card's actual contract locator

- Affected workflow contract/invariant: `workflow/REVIEW.md` exact acceptance surface; `workflow/STATE.md` review-attempt binding; PWV2-REQ-021/034/036.
- Expected behavior: An implementation review that permits finalization must cover the exact stable Task Card contract currently selected by the Task Board.
- Actual behavior: `validate_review()` accepts any workstream-local `cards/**/*.md` path whose filename stem equals `card_id`. `validate_review_history()` checks Card/workstream IDs, but `tools/router.py` never compares `review.acceptance.path` with `card.contract.path` and never reads the claimed acceptance artifact. A matching GREEN result review can therefore name a different or nonexistent nested Card path such as `cards/archive/M01-T04.md` and still route to `post_review_finalization`.
- Minimal reproduction: Install the official fixture's REQUIRED result and GREEN review, then change only the review acceptance path from the current `cards/M01-T04.md` to nonexistent `cards/archive/M01-T04.md`. Keep `card_id = "M01-T04"` and the exact result subject unchanged. The production selector accepts the attempt and finalizes.
- Why this is materially load-bearing: The review gate can be satisfied without reviewing the contract that defines current scope, acceptance and tests, bypassing the required exact acceptance surface.
- Defect class / likely siblings: Syntactic-locator validation substituted for referential binding. Plan/final review consumers should be checked for the same “valid-looking locator but wrong current authority” pattern.
- Existing tests that failed to catch it: `test_task_card_review_acceptance_is_exact_and_semantic` validates class/stem semantics but does not compare against a selected Board Card contract. `test_required_review_blocks_until_green_then_routes_finalization` always uses the matching current Card path.
- Reproduction artifact, if any: `repros/repro_router_counterexamples.py --case F2`.

### F3 — Terminal review verdicts can finalize with missing or arbitrary evidence locators

- Affected workflow contract/invariant: `workflow/REVIEW.md` durable terminal verdict evidence; `workflow/PLAN_REVIEW.md` terminal evidence locator; PWV2-REQ-034/036.
- Expected behavior: A terminal GREEN/RED attempt must have durable, readable evidence for that attempt before the verdict can authorize finalization/correction.
- Actual behavior: `validate_review()` requires terminal `evidence_path` to be merely non-empty and syntactically relative. It neither constrains implementation-review evidence to the workstream evidence root nor reads/verifies the target. `validate_plan_review()` repeats the same non-empty/path-safety check. The router never dereferences terminal review evidence before consuming GREEN.
- Minimal reproduction: Install a REQUIRED result and matching GREEN attempt, set `evidence_path` to `implementation/workstreams/sample-workstream/evidence/DOES-NOT-EXIST.md`, ensure that file does not exist, and run the production selector. It still returns `route/post_review_finalization`.
- Why this is materially load-bearing: Required review can become a bare verdict assertion with no durable evidence artifact, weakening recovery/audit truth exactly at the completion gate.
- Defect class / likely siblings: Existence/ownership validation missing from durable evidence locators. The same helper path affects Stage-6 Plan Review terminal evidence.
- Existing tests that failed to catch it: `test_review_terminal_evidence_and_append_only_history` rejects only an empty evidence string. The Plan Review test likewise checks empty versus non-empty, not existence or ownership.
- Reproduction artifact, if any: `repros/repro_router_counterexamples.py --case F3`.

### F4 — Execution-origin Research can preempt the Task Board without Board ownership

- Affected workflow contract/invariant: `workflow/RECOVERY.md` implementation/recovery Research ownership; `workflow/STATE.md` Task Board research obligation; router precedence/fail-closed owner binding.
- Expected behavior: Implementation/recovery Research exists only when the selected Task Board points to the exact `research_obligation`; otherwise an execution-origin Research record must not seize routing from the current Board/Card.
- Actual behavior: `validate_research()` permits execution origins/targets for any Workstream `[research]` locator. `tools/router.py` processes the Workstream research locator before reading the Task Board, and an `active` execution-origin record immediately returns `route/research`. No Board `research_obligation` pointer is required. The later Board-specific Research path does enforce execution ownership, so the two individually-valid mechanisms disagree when combined.
- Minimal reproduction: Starting from the official fixture with active Card `M01-T04`, add a Workstream `[research]` locator to an active `RESEARCH.toml` whose `origin_role = "execution_resolution"` and `return_target = "execution_resolution:M01-T04"`; do not add `task_board.research_obligation`. The selector returns `route/research` before reading the Board instead of failing closed or continuing the Board-owned obligation.
- Why this is materially load-bearing: A stale or contradictory manifest-level record can bypass the authoritative implementation owner and redirect the deterministic next obligation, defeating recovery precedence.
- Defect class / likely siblings: Cross-owner state accepted by a shared schema plus higher-precedence generic routing. Completed execution-origin Workstream Research also exposes an inconsistent path because the pre-execution owner map cannot resolve execution-prefixed return targets.
- Existing tests that failed to catch it: `test_active_and_completed_research_route_to_exact_owner` exercises manifest-level pre-execution Research only. `test_task_board_research_return_is_recovered_before_execution` exercises execution Research only when the Board pointer is present. No negative-space test combines execution-origin Research with a missing Board pointer.
- Reproduction artifact, if any: `repros/repro_router_counterexamples.py --case F4`.

## Non-blocking observations

- A satisfied JIT trigger with all currently materialized Cards DONE routes to Close because the selector does not inspect trigger state after Board validation. The published contracts also assign Close responsibility for deciding whether approved scope is actually complete, so this audit did not classify that interaction as a material defect without a stronger unambiguous owner/precedence counterexample.
- Active-Card recovery reads but does not re-parse a Card contract until a result exists. This may be intentional reliance on the earlier launch refresh; no material route violation was claimed here.

## Coverage

The audit remained bound to `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045` for substantive inspection. It inspected the canonical router/state/authority/workstream, Research, Planning/Plan Review, Execution Prep/Execution, Review/Recovery and Close contracts; `tools/router.py`, `tools/state_contract.py`, `tools/execution_contract.py`, `tools/recovery_contract.py`, `tools/review_contract.py`, `tools/close_contract.py`; Task Card/Workstream/Task Board templates; exact router/state/execution/review/close tests and router fixtures.

All four selected attack lenses were exercised:
- path traversal / locator safety / cross-workstream binding: exact locator checks plus F2/F3 ownership gaps;
- malformed or contradictory state / fail-closed behavior: F1 and F4 negative-space states;
- review independence / review bypass / result mutation: F1-F3;
- router precedence / unreachable branches / conflicting obligations: F4 and the non-blocking JIT/Close interaction.

Existing tests were treated as hypotheses to attack rather than proof. No `audit/*` branch, swarm report, GitHub Issue/PR comment, or historical finding database was intentionally inspected before freezing the finding set. No post-freeze historical comparison was performed.

## Confidence and limitations

Confidence is high in the demonstrated control-flow defects because each finding follows a direct production-code path and has a preserved selector-level reproduction against the repository's own fixture/helpers. The current environment could not execute those reproductions against a local checkout: outbound Git from the local container was unavailable, and the connected remote desktop execution service had reached its usage limit. The reproduction script is therefore preserved but was not executed during this audit; this is the main limitation.

While resolving the immutable target commit, the GitHub connector unexpectedly expanded the merge commit response with its diff, including historical implementation/evidence/review paths that were outside the intended blind-read set. Those historical conclusions were not used to generate, add, remove, or prioritize the frozen findings above. Intentional inspection remained on the permitted canonical workflow/tools/tests/templates surfaces.
