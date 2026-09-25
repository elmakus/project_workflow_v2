# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Path-only Card results can be accepted as durable completion truth

- Affected workflow contract/invariant: Durable Card results are supposed to carry exact immutable result identity, and recovery/finalization must fail closed on missing/stale binding.
- Expected behavior: A Card result without exact commit+blob identity is invalid for reconciliation/finalization/Close.
- Actual behavior: `validate_locator(..., "result")` requires commit+blob only if either field is present. With both omitted, the result locator validates. For an `in_progress` Card whose Task Card says `Review requirement: none`, `select_route` reads/parses the result and returns `result_reconciliation` without ever calling `exact_result_subject`. A `done` Card also needs only the presence of a result locator, so an all-DONE board can route directly to `close` with path-only results.
- Minimal reproduction: Use the valid router fixture; attach a syntactically valid result file and `[cards.result] class="result", path=...` but omit commit/blob. With review requirement `none`, route selection reaches `result_reconciliation`; if the Card is marked DONE, it reaches `close`.
- Why this is materially load-bearing: The immutable identity is the recovery/review anti-replay boundary. A path-only result can be changed in place while still being treated as durable completion evidence.
- Defect class / likely siblings: Missing-required-identity validation; likely affects no-review finalization and Close paths more broadly.
- Existing tests that failed to catch it: Result tests always include commit/blob. There is no negative test for a result locator with both fields absent.
- Reproduction artifact, if any: `audits/swarm/q7m2v9k4x1c8n5r0t6p3zjhw/repros/router_counterexamples.py` (F1).

### F2 — Exact-looking commit/blob tuples are never verified against the bytes being consumed

- Affected workflow contract/invariant: READY launch refresh and review/recovery claim exact Git subject identity; same-path-changed dependency inputs must fail closed.
- Expected behavior: The commit/blob recorded in a result/dependency/review subject must resolve to the content actually read, or routing must fail closed.
- Actual behavior: The validator checks only 40-hex syntax. `refresh_ready_card` compares the dependency tuple against the DONE predecessor's recorded tuple, then reads the current path, but it never computes/resolves the Git blob. If the result file is mutated in place while the recorded commit/blob tuple stays unchanged, launch refresh still succeeds. The same pattern exists for result/review/planning subject identity: strings are compared, not verified against Git object content.
- Minimal reproduction: Create a DONE predecessor with recorded tuple A and a READY Card depending on tuple A. Route once successfully. Modify only the predecessor result file bytes, leaving both durable tuples unchanged. The selector still returns `execution_prep`.
- Why this is materially load-bearing: A forged or stale tuple can bless different bytes than the supposedly exact subject, defeating stale-content detection and review/result identity.
- Defect class / likely siblings: Syntactic-vs-cryptographic identity confusion across result, dependency, review and planning subject bindings.
- Existing tests that failed to catch it: `test_ready_card_stale_dependency_fails_closed_before_launch` changes the board tuple as well as the file, so it proves tuple mismatch detection, not same-tuple/content-drift detection.
- Reproduction artifact, if any: `audits/swarm/q7m2v9k4x1c8n5r0t6p3zjhw/repros/router_counterexamples.py` (F2).

### F3 — Contradictory Card status + durable result is accepted and can replay work

- Affected workflow contract/invariant: A durable valid semantic result is recovery truth and must prevent implementation replay; contradictory state should fail closed.
- Expected behavior: A Card carrying a durable result must be in a status compatible with result reconciliation/finalization, or the state must route Recovery.
- Actual behavior: `validate_board` permits a `result` on `planned`, `ready`, or `blocked` Cards. The router only performs result reconciliation inside the `in_progress` branch. A `ready` Card with a valid result therefore bypasses that result and routes to `execution_prep`, which can relaunch already-completed work.
- Minimal reproduction: Start from a valid active Card with a valid durable result, then change only `status = "in_progress"` to `status = "ready"`. Validation succeeds and the selector returns `execution_prep` rather than Recovery/result reconciliation.
- Why this is materially load-bearing: Interrupted or partially reconciled durable state can cause duplicate execution, exactly the replay class the recovery contract is intended to prevent.
- Defect class / likely siblings: Cross-field state-coherence gap; planned/blocked/result and review-attempt/status combinations deserve sibling checks.
- Existing tests that failed to catch it: Tests cover in-progress+result and done+result, but not result-bearing READY/PLANNED/BLOCKED Cards.
- Reproduction artifact, if any: `audits/swarm/q7m2v9k4x1c8n5r0t6p3zjhw/repros/router_counterexamples.py` (F3).

### F4 — RECOMMENDED review has no activation state, so every recommendation becomes mandatory

- Affected workflow contract/invariant: Independent review is blocking for REQUIRED review and for RECOMMENDED review only when the recommendation has been activated by the stable Card/workstream contract.
- Expected behavior: An unactivated `recommended` review may legally proceed without being forced through the blocking review lifecycle; an activated recommendation must block exactly like REQUIRED.
- Actual behavior: The durable schema/parser has only `none|required|recommended` and no activation bit/record. In `select_route`, every requirement other than `none` is treated as blocking: with `recommended` and no attempt, it always returns `review_freeze`.
- Minimal reproduction: Use a valid result-bearing active Card whose Task Card says `Review requirement: recommended` and carries no review attempt. The selector routes `review_freeze`.
- Why this is materially load-bearing: The implementation cannot represent one of the documented legal states and therefore rejects legal continuation by silently promoting recommendation into requirement.
- Defect class / likely siblings: Documented-state vs executable-state parity drift / missing state dimension.
- Existing tests that failed to catch it: Router review tests exercise `none` and `required`; no test covers `recommended` activation/non-activation.
- Reproduction artifact, if any: `audits/swarm/q7m2v9k4x1c8n5r0t6p3zjhw/repros/router_counterexamples.py` (F4).

### F5 — Declared stop precedence is not enforced when pre-execution Research is present

- Affected workflow contract/invariant: `PRIORITY_FOUNDATION` places `explicit_human_or_premium_boundary` ahead of Research return/current work; invalid/contradictory bindings must fail closed.
- Expected behavior: If durable state simultaneously carries a real explicit user stop (or an already-due premium boundary) and a Research locator, routing must honor the higher-precedence stop or reject the contradictory state.
- Actual behavior: `select_route` loads and immediately routes top-level workstream Research before it loads Brainstorming, Definition or Planning state. A valid active Research record can therefore return `research` without even reading a concurrently valid Brainstorming record with `explicit_user_stop = true`. The priority constant is tested as data, but not enforced by this route order.
- Minimal reproduction: Add valid `research` and `brainstorm` locators to the valid fixture; set Research active with return target brainstorming and set Brainstorming `explicit_user_stop = true`. The selector returns `research` before reading the stop-bearing Brainstorming record.
- Why this is materially load-bearing: A real human boundary can be bypassed by a lower-precedence durable obligation; alternatively, contradictory state that should fail closed is silently accepted.
- Defect class / likely siblings: Router precedence drift between declarative priority and progressive-read early returns; premium A/B/C co-bound states are likely siblings.
- Existing tests that failed to catch it: The suite asserts the literal `PRIORITY_FOUNDATION` tuple and separately tests Research and stops, but does not combine them adversarially.
- Reproduction artifact, if any: `audits/swarm/q7m2v9k4x1c8n5r0t6p3zjhw/repros/router_counterexamples.py` (F5).

## Non-blocking observations

The Close helper functions are narrow deterministic oracles over caller-supplied facts. Within the inspected surface I did not independently demonstrate a second Close-specific semantic break distinct from the identity/coherence defects above.

## Coverage

Inspected at the exact subject commit: `workflow/ROUTER.md`, `STATE.md`, `REVIEW.md`, `RECOVERY.md`, `CLOSE.md`, `EXECUTION.md`, `RESEARCH.md`, `BRAINSTORMING.md`, `DEFINITION.md`, `PLANNING.md`, `AUTHORITY.md`, `WORKSTREAMS.md`, `USER_STOP.md`; production helpers `tools/router.py`, `state_contract.py`, `execution_contract.py`, `review_contract.py`, `recovery_contract.py`, `close_contract.py`; Task Card/Board/review templates and state schema; and the router/state/review/recovery/Close regression suites.

Selected lenses exercised:
- stale commit/blob/path/result/review identity — directly exercised by F1/F2;
- RED/recovery/blocker/interrupted-runtime continuation — directly exercised by F1/F3 and inspected RED/research/blocker routing;
- Close/finalization/end-of-approved-scope — inspected Close contract/oracles and the all-DONE route; F1 reaches Close with incomplete result identity;
- helper vs documented semantics/parity drift/negative space — directly exercised by F4/F5 and negative-space mutations absent from existing tests.

No `audit/*` branch other than this audit branch, no swarm report, and no Issues/PR comments were inspected during discovery.

## Confidence and limitations

Confidence is high for F1-F4 because each follows a short production-code path with a minimal fixture mutation. F5 is high-confidence as a route-order defect because the selector returns from Research before loading the stop-bearing record and the declared priority puts human/premium boundaries first.

The environment available to this chat could read/write GitHub but could not execute the checkout locally: the local container had no GitHub network access and the connected Desktop Commander had exhausted its monthly command quota. The executable reproductions were therefore preserved but not run in this session. Existing repository tests were inspected at the exact immutable commit; passing them would not cover the negative-space cases above.
