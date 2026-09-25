# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — DONE status bypasses required review and RED/pending review blockers

- Affected workflow contract/invariant: `workflow/STATE.md` independent-review lifecycle; `workflow/REVIEW.md` blocking lifecycle; `workflow/ROUTER.md` requirement that contradictory state fail closed and that GREEN on the exact current subject + acceptance is what permits deterministic post-review finalization.
- Expected behavior: A Card whose stable contract requires review must not become terminal while review is absent, pending, in-progress, RED, stale, or otherwise non-GREEN. Such a contradictory `done` Board state must fail closed or return to the exact review/recovery owner before Close.
- Actual behavior: `validate_board()` only requires a `result` locator when `status = "done"`; it does not read the Card contract or enforce review completion. `select_route()` processes review state only for `in_progress` Cards. If every current Card is marked `done`, it routes directly to `close` without checking the Card's review requirement or attempts.
- Minimal reproduction: Starting from the router fixture, install a valid result and a Task Card with `Review requirement: required`, create no review attempt, then change the Board status from `in_progress` to `done`. The production selector reaches `route/close` rather than Recovery/review.
- Why this is materially load-bearing: This is a direct bypass of the independent-review gate and can permit Close/integration of work that never received the required GREEN review, or that still has pending/in-progress/RED review state.
- Defect class / likely siblings: Any terminal Card state whose review obligation is inconsistent with its attempt history; especially `done` with no attempt, pending/in-progress/RED attempt, stale subject, or stale acceptance.
- Existing tests that failed to catch it: `test_all_terminal_cards_route_to_close_not_directly_to_stop` covers only a Card whose review requirement is `none`; state-contract tests do not exercise `done` + required review coherence.
- Reproduction artifact, if any: `repros/repro_findings.py` (F1).

### F2 — GREEN review can finalize a different current Task Card acceptance surface

- Affected workflow contract/invariant: `workflow/REVIEW.md` exact acceptance identity and `workflow/RECOVERY.md` review-subject refresh; GREEN is valid only for the exact current subject plus exact acceptance surface.
- Expected behavior: If the selected Card's stable Task Card/acceptance surface changes, an older review bound to another Task Card artifact must not authorize finalization; the router must require a new exact attempt or fail closed.
- Actual behavior: `validate_review()` only requires a Task-Card acceptance path under the workstream and checks that the path stem equals `card_id`. `validate_review_history()` checks Card/workstream identity. `select_route()` compares only the review's result subject with the current result subject; it never compares `review.acceptance.path` with the selected Board Card's current `contract.path`. Therefore the Board can move the Card contract to another valid path with the same Card ID and changed acceptance criteria while an older GREEN review still routes to `post_review_finalization`.
- Minimal reproduction: Create a valid REQUIRED result and GREEN review bound to `cards/M01-T04.md`; then point the Board contract at `cards/archive/M01-T04.md` containing the same Card ID but changed acceptance text. Keep the result subject unchanged. The production selector still reaches `route/post_review_finalization`.
- Why this is materially load-bearing: A GREEN verdict can be reused after the acceptance contract it was supposed to review has changed, bypassing exact acceptance coverage.
- Defect class / likely siblings: Any same-Card-ID contract relocation or replacement where the review acceptance locator differs from the selected Card contract locator; stale acceptance can survive while result subject remains unchanged.
- Existing tests that failed to catch it: Router tests cover stale result subject changes but do not mutate the selected Card contract/acceptance locator after GREEN review; state tests validate only acceptance class/path/card-id shape.
- Reproduction artifact, if any: `repros/repro_findings.py` (F2).

### F3 — commit/blob identity is not verified against file bytes, so same-path mutations pass

- Affected workflow contract/invariant: `workflow/EXECUTION_PREP.md` launch refresh requires exact dependency result path + immutable commit/blob identity and explicitly says same-path-changed inputs fail closed; `workflow/RECOVERY.md` requires GREEN to cover the exact still-current result.
- Expected behavior: If a dependency/result file at a bound path changes while the stored `commit/blob` locator remains unchanged, the selector must detect the mismatch and route Recovery/new review rather than treating the old immutable identity as still valid.
- Actual behavior: `validate_locator()` validates result commit/blob only syntactically as 40-hex. `refresh_ready_card()` compares the dependency tuple against the DONE predecessor's stored tuple, then merely reads the current dependency path; it never verifies the current bytes against the stored blob/commit. For active reviewed results, the router parses current file bytes but derives the exact review subject solely from the Board's stored result locator, so unchanged locator fields can continue matching an old GREEN review after the file content changes in place.
- Minimal reproduction: (a) Create a DONE predecessor with result tuple `path@A:B`, make the READY Card depend on exactly `path@A:B`, then modify only the dependency file contents; the selector still reaches `route/execution_prep`. (b) Create a REQUIRED result + GREEN review, then modify only the result file's implementation-subject text while leaving its Board locator untouched; the selector still reaches `route/post_review_finalization`.
- Why this is materially load-bearing: The workflow claims immutable identity and same-path-change protection, but current filesystem content can be consumed or finalized under stale Git identity, defeating stale-input detection and exact review coverage.
- Defect class / likely siblings: Any semantic path that mixes current working-tree bytes with stored Git `commit/blob` strings without content-addressed readback; dependency launch and reviewed-result finalization are directly demonstrated.
- Existing tests that failed to catch it: The stale-dependency test changes both the Board tuple and file content; stale-result review tests change the Board blob identity. Neither tests a content-only same-path mutation with the locator left unchanged.
- Reproduction artifact, if any: `repros/repro_findings.py` (F3).

### F4 — READY Card with an already durable result is accepted and routed toward replay

- Affected workflow contract/invariant: `workflow/STATE.md` and `workflow/EXECUTION.md` durable semantic result as recovery truth that prevents replay; `workflow/ROUTER.md` contradictory state must fail closed.
- Expected behavior: A Card carrying a durable result cannot simultaneously be a fresh READY launch candidate. Such status/result contradiction must fail closed or reconcile from the existing result, never re-enter Execution Prep as if implementation had not happened.
- Actual behavior: `validate_board()` permits a `result` locator on `ready` Cards. `select_route()` only consumes result state in the `in_progress` branch; for a READY Card it calls `refresh_ready_card()`, ignores the existing result, and routes to `execution_prep`.
- Minimal reproduction: Install a valid semantic result on the fixture Card, then change only its Board status from `in_progress` to `ready`. The production selector reaches `route/execution_prep`.
- Why this is materially load-bearing: It can replay or relaunch implementation despite durable completion evidence, contrary to the recovery/no-replay invariant.
- Defect class / likely siblings: Missing status/result coherence for `planned`, `ready`, and potentially `blocked` Cards; only `done -> requires result` is currently enforced.
- Existing tests that failed to catch it: READY tests do not attach a result; result-reconciliation tests keep the Card `in_progress`.
- Reproduction artifact, if any: `repros/repro_findings.py` (F4).

### F5 — terminal implementation review attempts can be rewritten in place

- Affected workflow contract/invariant: `workflow/REVIEW.md` append-only attempt history; changed subject/new verdict must create a new attempt and terminal attempts remain immutable history.
- Expected behavior: After an attempt becomes GREEN or RED, changing its verdict/subject/acceptance must not mutate the same attempt record into a different terminal fact; a new attempt must be appended and the prior terminal record preserved.
- Actual behavior: Task Board `review_attempts` locators contain only class + mutable path. `validate_review_history()` validates the current contents and ordering but has no immutable commit/blob identity or historical check for each attempt. Rewriting the same R01 file from `verdict = "red"` to `verdict = "green"` leaves the locator and attempt ID unchanged and causes the router to switch from `execution_resolution` to `post_review_finalization`.
- Minimal reproduction: Create REQUIRED result + terminal R01 RED, confirm the selector's RED resolution route, then edit only the same review file's verdict to GREEN while keeping the same path, attempt ID, subject, acceptance and evidence path. The selector accepts the rewritten record as GREEN.
- Why this is materially load-bearing: Failed independent-review evidence can be erased semantically and replaced by success without an append-only new attempt, defeating durable audit/recovery truth.
- Defect class / likely siblings: In-place mutation of terminal verdict, subject, acceptance or independence fields in any existing attempt record.
- Existing tests that failed to catch it: Review tests enforce latest-nonterminal ordering, duplicate attempt IDs, evidence presence and semantic independence, but not terminal-record immutability across repository history.
- Reproduction artifact, if any: `repros/repro_findings.py` (F5).

## Non-blocking observations

- The production contracts contain useful fail-closed path and workstream-binding checks, and the selected attack lenses found several positive controls (single in-progress Card enforcement, exact workstream Task Board path, current-result subject mismatch handling when the locator itself changes).
- The current test suite often mutates stored locator values together with content. That catches stale metadata changes but leaves negative-space coverage for content-only mutations.

## Coverage

The audit was bound to subject commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`.

Inspected/test-traced:
- canonical modules: `workflow/ROUTER.md`, `STATE.md`, `REVIEW.md`, `RECOVERY.md`, `EXECUTION_PREP.md`, `EXECUTION.md`, `CLOSE.md`, `WORKSTREAMS.md`, `AUTHORITY.md`;
- production helpers: `tools/router.py`, `state_contract.py`, `review_contract.py`, `recovery_contract.py`, `execution_contract.py`, `close_contract.py`;
- focused tests/fixtures/templates: `tests/test_router.py`, `test_state_contract.py`, `test_review_contract.py`, `test_close_contract.py`, router/state fixtures and Task Board template.

Selected lenses exercised:
- review independence / review bypass / result mutation: F1, F2, F5;
- Task Board / READY / active / DONE / JIT-trigger lifecycle: F1, F4;
- malformed or contradictory state / fail-closed behavior: F1, F4;
- stale commit/blob/path/result/review identity: F2, F3, F5.

## Confidence and limitations

Confidence is high in the source-level control-flow findings because each route follows directly from the production validator/selector branches at the immutable subject and the repro script invokes those production functions through the repository's existing router fixture helpers.

Direct execution of the repro script was not available in this audit environment: the local container could not reach GitHub, and the connected remote terminal had exhausted its monthly execution allowance. The preserved repro therefore remains unexecuted in this run; this is explicitly not represented as a successful runtime test.

The first exact-commit GitHub API response unexpectedly included changed-file patches under historical `implementation/workstreams/**/evidence/**` and `reviews/**` as part of commit metadata before the finding set was frozen. No historical narrative was intentionally queried, and the material findings above were frozen from canonical workflow, production helper, fixture and test inspection rather than from those historical narratives.

## Post-freeze historical comparison

Not performed. The finding set above is left unchanged and unclassified against historical audit/reviewer material.
