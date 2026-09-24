# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Satisfied JIT trigger is ignored and terminal Cards route to Close

- Affected workflow contract/invariant: `workflow/EXECUTION_PREP.md` requires predecessor-dependent JIT triggers to survive until the downstream Card becomes knowable, with lifecycle `waiting -> satisfied -> consumed`; `workflow/CLOSE.md` forbids inferring end-of-scope merely from an empty current Card queue; `PWV2-REQ-028` requires preservation of predecessor-dependent JIT triggers.
- Expected behavior: A Board whose only Card is DONE but whose JIT trigger is `satisfied` still has an already-authorized execution-prep obligation. The selector must route to Execution Prep to materialize/consume that trigger (or fail closed if the state is inconsistent), not enter Close.
- Actual behavior: `validate_board()` accepts a `satisfied` trigger when its predecessor is DONE with a result. `select_route()` never consults JIT triggers after Board validation; with no active/blocked/READY Card it reaches `all(card["status"] == "done")` and returns `route/close`.
- Minimal reproduction: Start from the router fixture, attach a valid result to M01-T04, set M01-T04 to `done`, and add `jit_triggers = [{ after_card = "M01-T04", state = "satisfied", ... }]`. Call `select_route(...)`. The production branches deterministically select Close instead of Execution Prep.
- Why this is materially load-bearing: Close/integration can begin while approved downstream work is explicitly waiting to be materialized, permitting premature finalization or an incorrect end-of-scope decision.
- Defect class / likely siblings: Router negative-space drift: Board validation recognizes lifecycle state that routing ignores. The same risk applies to any future Board-owned obligation admitted by validation but omitted from the post-Board priority chain.
- Existing tests that failed to catch it: `test_jit_trigger_preserves_predecessor_boundary_without_placeholder_card` validates trigger syntax/lifecycle but never calls the router. `test_all_terminal_cards_route_to_close_not_directly_to_stop` has no JIT trigger.
- Reproduction artifact, if any: `audits/swarm/s06uaj47ohetuymvwvo8x0da/repros/repro_findings.py::test_F1_satisfied_jit_trigger_preempts_close`.

### F2 — DONE status bypasses REQUIRED/RED review gates

- Affected workflow contract/invariant: `workflow/REVIEW.md` and `PWV2-REQ-036` require REQUIRED/activated RECOMMENDED review to block terminal Card completion until exact GREEN; RED must route correction. `workflow/ROUTER.md` requires contradictory state to fail closed.
- Expected behavior: A Card marked `done` while its stable Card requires review and its latest review is pending/in-progress/RED is contradictory terminal state. It must fail closed (or be routed back to the exact blocking review/correction owner after reconciliation), never route to Close.
- Actual behavior: `validate_board()` requires only a result locator for a DONE Card; it does not parse the Card contract or inspect review-attempt verdicts. The router evaluates review gates only inside the `in_progress` branch. A DONE Card with a result plus pending or RED review therefore skips all review logic and, when all Cards are DONE, returns `route/close`.
- Minimal reproduction: Give M01-T04 a stable Card with `Review requirement: required`, a valid durable result, and a pending R01 review attempt; then set Board status to `done`. `validate_board()` accepts the state and `select_route(...)` selects Close.
- Why this is materially load-bearing: A single stale/incorrect Board status mutation can bypass the mandatory independent review barrier and allow integration/finalization of unapproved or explicitly failed work.
- Defect class / likely siblings: Cross-field lifecycle coherence is missing between Card status, result, stable review requirement, and attempt history. Siblings include DONE+no required attempt, DONE+RED, DONE+stale terminal review, and non-active Cards carrying execution/result state that is only checked in the active path.
- Existing tests that failed to catch it: Required-review router tests keep the Card `in_progress`; the all-terminal Close test uses `Review requirement: none`. State validation tests do not combine DONE with non-GREEN REQUIRED review history.
- Reproduction artifact, if any: `audits/swarm/s06uaj47ohetuymvwvo8x0da/repros/repro_findings.py::test_F2_done_cannot_bypass_required_pending_review`.

### F3 — Claimed Git commit/blob identity is never verified against the bytes being finalized

- Affected workflow contract/invariant: `workflow/STATE.md`, `workflow/REVIEW.md`, `workflow/RECOVERY.md`, and `PWV2-REQ-034` require exact immutable result/review subjects; changed current results require fresh review or Recovery. Execution Prep likewise requires exact dependency result commit/blob identity and same-path changes to fail closed.
- Expected behavior: Before GREEN finalization/review reuse, the selector must establish that the bytes it reads for the result are the bytes identified by the claimed commit/path/blob (or read the immutable Git object itself). If current bytes differ, the old GREEN cannot finalize them.
- Actual behavior: `validate_locator()` checks only 40-hex shape when commit/blob fields are present (and even accepts path-only result locators when neither is present). `parse_card_result()` structurally parses the working-tree file. `exact_result_subject()` and `review_subject()` simply concatenate the Board/review strings. No production router/state/execution/recovery helper resolves or hashes the claimed Git object. Thus a result file can be materially changed in place while Board and GREEN review keep the same claimed A/B identity, and the router still returns `route/post_review_finalization`.
- Minimal reproduction: Start from an active review-required Card with result locator `commit=A, blob=B` and exact GREEN review covering A/B. Confirm the valid result is finalizable, then change the result file's implementation-subject bytes without changing the locator or review record. The selector still compares A/B to A/B and finalizes the changed file.
- Why this is materially load-bearing: The exact-subject review barrier becomes self-asserted metadata rather than an integrity binding. Stale GREEN evidence can authorize bytes it never reviewed.
- Defect class / likely siblings: Trusting locator claims without object verification. The READY dependency path has the same shape: `refresh_ready_card()` compares Task Card dependency identity only to Board identity, then merely reads the dependency path; same-locator content drift is invisible. Task-Card acceptance is also path-bound rather than immutable-content-bound.
- Existing tests that failed to catch it: The changed-result test changes the Board's blob field, so the string mismatch is detected. The stale-dependency test changes both Board commit/blob and file contents, so it only proves tuple mismatch detection. Neither mutates bytes while leaving the claimed immutable identity unchanged.
- Reproduction artifact, if any: `audits/swarm/s06uaj47ohetuymvwvo8x0da/repros/repro_findings.py::test_F3_changed_result_bytes_cannot_reuse_green_subject`.

### F4 — Active Research masks an explicit user stop

- Affected workflow contract/invariant: `workflow/BRAINSTORMING.md` defines `explicit_user_stop` as a real stop; `PWV2-REQ-068` requires explicit user stop among real stops; the router's own `PRIORITY_FOUNDATION` declares explicit human/premium boundaries above Research return/work.
- Expected behavior: If the current Brainstorming revision carries `explicit_user_stop = true`, continuation must stop before doing more Research, even when a valid active Research record exists for that Brainstorming subject.
- Actual behavior: `select_route()` loads and immediately returns active/completed Research before it loads `BRAINSTORM.toml`. Therefore the explicit stop bit is never observed and the selector returns `route/research`.
- Minimal reproduction: Add valid active Brainstorming state for `scope-a@1` with `explicit_user_stop = true`, plus valid active Research with `origin_role = "brainstorming"`, `origin_subject = "scope-a@1"`, and `return_target = "brainstorming"`. Call `select_route(...)`; the Research early return wins.
- Why this is materially load-bearing: The workflow can continue agent work after the user explicitly instructed it to stop, violating the human-control boundary and the router's declared precedence.
- Defect class / likely siblings: Precedence mismatch between durable stop-bearing owner state and an earlier-returning subordinate obligation. Any subordinate slot read before its parent stop signal can create the same hidden-authority inversion.
- Existing tests that failed to catch it: Research route tests do not combine active Research with an explicit Brainstorming stop. The priority-foundation test asserts only the constant tuple, not cross-state selector behavior.
- Reproduction artifact, if any: `audits/swarm/s06uaj47ohetuymvwvo8x0da/repros/repro_findings.py::test_F4_explicit_user_stop_preempts_active_research`.

## Non-blocking observations

- `validate_research()` validates execution-origin roles and execution return-target syntax independently rather than coupling the two. I did not promote this to a material finding because I did not execute a sufficiently distinct counterexample beyond the four frozen findings.
- The valid state fixture intentionally demonstrates that a DONE result locator may be path-only; this reinforces F3's identity-integrity class but is not counted separately.

## Coverage

Blind discovery inspected the exact target-ref versions of the canonical router, state envelope, Brainstorming, Research, Execution Prep, Execution, Review, Recovery, Close, requirements, templates, bootstrap hook/Skill, and production helpers under `tools/`. I also inspected the relevant router/state/review tests and negative-space coverage.

The selected lenses were exercised as follows:
- malformed/contradictory fail-closed behavior: F2 and F3;
- helper/documented parity and negative space: F1 and F3;
- Task Board/JIT lifecycle: F1 and F2;
- router precedence/conflicting obligations: F4, plus F1's Close precedence.

The preserved reproduction file contains four non-mutating regression tests using the production selector and the repository's disposable router fixture. No product code is modified.

## Confidence and limitations

Confidence is high in the four code-path counterexamples because each follows a short deterministic production branch and is directly contradicted by canonical contracts. Exact source and tests were read by immutable commit ref `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`, not moving `main`.

I could not execute the preserved regression script in this chat environment: the local container had no checkout and could not reach GitHub, while the connected remote command bridge had exhausted its monthly quota. The reproduction artifact is therefore marked as preserved-but-not-executed here; this report does not claim runtime output that was not observed.

During initial immutable-commit verification, the GitHub commit-fetch response unexpectedly included the target merge commit's own `implementation/workstreams/**` diff, including historical evidence/review text. I did not search for it, did not inspect any `audit/*` branch/report, and did not use that accidental material as a discovery checklist. The four finding set was frozen from canonical code/docs/tests before any optional historical comparison. No post-freeze historical comparison was performed.
