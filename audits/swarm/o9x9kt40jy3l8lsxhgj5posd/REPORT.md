# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — DONE can bypass durable-result validation and mandatory review

- Affected workflow contract/invariant: `workflow/STATE.md` and `workflow/REVIEW.md` require a valid durable semantic result and require REQUIRED/activated RECOMMENDED review to block terminal Card completion until exact GREEN; `workflow/CLOSE.md` permits completion only from durable truth.
- Expected behavior: A Card marked `done` whose result artifact is missing/invalid, or whose stable Card requires review without an exact current GREEN attempt, must fail closed or return to result/review reconciliation. It must not become terminal input to Close.
- Actual behavior: `tools/state_contract.py::validate_board` requires only that a DONE Card contain a syntactically valid `result` locator. It does not read/validate the result, parse the Card review requirement, or validate review attempts. `tools/router.py` only performs those checks for `status = "in_progress"`; when all Cards are `done` it routes directly to `close`. A non-existent result path plus a REQUIRED-review Card and no review attempt is therefore accepted as terminal state.
- Minimal reproduction: Copy `tests/fixtures/router/valid-project`; replace M01-T04's Card contract with a complete contract declaring `Review requirement: required`; change the Board Card from `in_progress` to `done`; add a result locator with valid-looking 40-hex commit/blob but do not create the result file or any review attempt. `select_route(...)` reaches `("route", "close")` because the DONE branch never dereferences the result or review state.
- Why this is materially load-bearing: It permits a canonical terminal state and Close handoff without implementation evidence and bypasses an explicit blocking review gate.
- Defect class / likely siblings: Cross-field terminal-state validation gap. Siblings include DONE with pending/RED/nonexistent review attempts and DONE whose result locator points at stale or absent content.
- Existing tests that failed to catch it: `test_all_terminal_cards_route_to_close_not_directly_to_stop` first installs a real result with `review_requirement="none"`; REQUIRED-review tests keep the Card `in_progress`. No test combines DONE with missing/invalid result or unsatisfied required review.
- Reproduction artifact, if any: `repros/repro_counterexamples.py` (`repro_done_review_bypass`).

### F2 — Immutable Git subjects are only syntactically checked, so GREEN review can cover mutated content

- Affected workflow contract/invariant: `workflow/REVIEW.md`, `workflow/RECOVERY.md`, and PWV2-REQ-034 require exact immutable Git subjects; changed current result content requires a new exact review attempt and stale/mismatched bindings must fail closed.
- Expected behavior: The claimed repository/commit/path/blob tuple must resolve to the content being consumed. If the current result content changes while the stored blob identity and GREEN review stay unchanged, the selector must detect the mismatch and freeze a new review or enter Recovery.
- Actual behavior: Result locators and review subjects are validated only as non-empty paths plus 40-hex strings. `exact_result_subject` formats the claimed tuple; the router separately reads the current working-tree result file and parses its fields, but never verifies that its bytes equal the claimed blob or that the commit contains that path/blob. After a GREEN attempt, the result file can be materially changed while leaving the Board and review tuple untouched; tuple equality still succeeds and the router selects `post_review_finalization`.
- Minimal reproduction: Keep an `in_progress` REQUIRED-review Card with a valid result file, Board result tuple `a…a/b…b`, and GREEN R01 over the same tuple. Route once, then change only the result file's tests/readback summary to a materially different value while leaving the tuple unchanged. The second route still selects `post_review_finalization`.
- Why this is materially load-bearing: Exact immutable identity is the safety boundary for review reuse and recovery. Treating identity as caller-supplied metadata allows reviewed bytes and consumed bytes to diverge without detection.
- Defect class / likely siblings: Stale/fabricated Git-object identity. The same helper pattern affects frozen/approved planning subjects and review subjects: validators prove 40-hex shape and string equality, not Git object existence or content binding.
- Existing tests that failed to catch it: Router/state tests deliberately use fake `"a"*40` commit and `"b"*40` blob values in non-Git temporary fixtures. The stale-result test changes the Board's blob string and correctly freezes a new review, but there is no negative-space test that changes file bytes while preserving the claimed tuple.
- Reproduction artifact, if any: `repros/repro_counterexamples.py` (`repro_mutated_result_reuses_green`).

### F3 — editorial_exempt is self-attested and can suppress Plan Review for an arbitrary changed plan

- Affected workflow contract/invariant: `workflow/PLANNING.md`, `workflow/PLAN_REVIEW.md`, and PWV2-REQ-039 allow omission of a new Plan Review only for mechanical/editorial changes that do not alter strategy, milestone structure, requirement coverage, or gates.
- Expected behavior: A changed plan subject may reuse prior GREEN/C only when the change is actually bounded to the editorial/mechanical exception; a materially changed plan must start a new material planning/review cycle and cannot self-authorize the exemption.
- Actual behavior: `validate_planning` accepts `review_mode = "editorial_exempt"` whenever the new subject string differs from the old subject, the old B/C subjects remain marked satisfied, and `review_exemption_basis` is merely non-empty. No plan bytes, structured milestone/coverage/gate surface, or independent classification is compared. `validate_plan_review` then only requires the retained prior GREEN subject. Therefore any changed plan can claim “wording only” and pass validation regardless of its actual semantic changes.
- Minimal reproduction: Construct an approved planning record with a new blob `c…c`, `review_mode="editorial_exempt"`, prior reviewed base `b…b`, B/C satisfied on the base, and any non-empty exemption basis; pair it with the prior GREEN review. Both production validators accept it even though no changed plan content is supplied to either validator, so materially different plan bytes are indistinguishable from a wording-only edit.
- Why this is materially load-bearing: This is a direct bypass of the mandatory independent Stage-6 review for materially revised plans and therefore can authorize Execution Prep under changed strategy without the required A/B/review/C cycle.
- Defect class / likely siblings: Unverified semantic exemption/classification. Any policy exception whose legality depends on content semantics but is represented only by a self-authored non-empty basis is vulnerable to the same class.
- Existing tests that failed to catch it: `test_editorial_plan_exemption_preserves_prior_green_subject` changes the plan blob and supplies a prose “wording only” basis; it asserts acceptance without comparing old/new plan semantics. Router editorial-exemption tests likewise exercise only metadata.
- Reproduction artifact, if any: `repros/repro_counterexamples.py` (`repro_editorial_exemption_is_content_blind`).

### F4 — Blocked Card state outranks a durable result, allowing replay despite recovery truth

- Affected workflow contract/invariant: `workflow/RECOVERY.md` recovery precedence requires durable result reconciliation before execution/correction/blocker routing; `workflow/STATE.md` says a valid durable result is recovery truth and prevents replay solely from runtime state.
- Expected behavior: A Card state that simultaneously claims `blocked` and carries a valid durable result must either reconcile the result first or fail closed as contradictory. A blocker must not cause implementation replay before the result is considered.
- Actual behavior: `validate_board` permits `status = "blocked"` together with a result locator. The router only runs durable-result logic for Cards in the `in_progress` list. It then handles `blocked` Cards by reading the blocker and applying `classify_resolution`, completely ignoring the result. With a `bounded_correction` blocker, the selector routes to `execution` even when a valid durable result is already present.
- Minimal reproduction: Change the fixture Card to `blocked`, add a valid workstream-local blocker with class `bounded_correction`, and add a valid result locator/result file. `select_route(...)` enters the blocker branch and returns `("route", "execution")` without reading or reconciling the durable result.
- Why this is materially load-bearing: It violates the stated recovery precedence and can repeat implementation work or apply correction against a state whose durable result should be the recovery source of truth.
- Defect class / likely siblings: Contradictory Card-state combinations are under-constrained and router precedence is status-driven rather than evidence-driven.
- Existing tests that failed to catch it: Blocker-routing tests construct blocked Cards without results; result-recovery tests keep Cards `in_progress`. No test combines `blocked` with a durable result.
- Reproduction artifact, if any: `repros/repro_counterexamples.py` (`repro_blocked_result_is_ignored`).

## Non-blocking observations

A satisfied but unconsumed JIT trigger can coexist with all currently materialized Cards DONE. The router's all-DONE branch ignores JIT state and hands control to Close. `EXECUTION_PREP.md` says a satisfied trigger is the point at which the downstream Card may be materialized, while `CLOSE.md` says terminal role/Card state is not itself end-of-scope. I did not freeze this as a material finding because the canonical text also explicitly routes all-current-Cards-terminal through Close, so an end-to-end Close driver could intentionally bounce back to Execution Prep; the current deterministic helper does not by itself prove premature completion.

The SessionStart/plugin bootstrap was inspected for package-root ambiguity, remote-policy fallback, router path escape, and bootstrap semantic duplication. The hook fails closed for missing/malformed/escaping router and enforces the configured package root; no material bootstrap defect was independently demonstrated in this audit.

## Coverage

The audit remained bound to commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`. I inspected canonical `workflow/ROUTER.md`, `STATE.md`, `AUTHORITY.md`, `WORKSTREAMS.md`, `PLANNING.md`, `PLAN_REVIEW.md`, `EXECUTION_PREP.md`, `REVIEW.md`, `RECOVERY.md`, and `CLOSE.md`; production helpers `tools/router.py`, `state_contract.py`, `execution_contract.py`, `recovery_contract.py`, `review_contract.py`, and `close_contract.py`; delivery bootstrap files and their tests; router/state/recovery/review tests and fixtures.

The selected lenses exercised were bootstrap drift (no frozen finding), Planning/Premium/Execution precedence (F2/F3), RED/recovery/blocker continuation (F4), and helper/documented-semantics parity plus negative space (F1/F2 and the JIT observation). I intentionally did not inspect `audit/*`, other swarm reports, GitHub Issues/PR comments for known defects, or historical workstream evidence/review narratives before freezing the finding set. No post-freeze historical comparison was performed.

## Confidence and limitations

Confidence is high for F1, F2, and F4 because the selector and validators expose the failing branches directly and existing tests demonstrate the complementary covered cases. Confidence is high-to-moderate for F3 because the production exemption validator is explicitly content-blind, although determining whether a real edit is semantically “editorial” necessarily involves semantic classification outside the current schema.

Executable falsification was attempted against the exact commit. The local container could not resolve GitHub, and the authorized Remote Desktop Commander endpoint reported its monthly command quota exhausted and instructed not to retry. I therefore could not execute the preserved repro script in this chat. The repro uses the repository's real production `select_route`, `validate_planning`, and `validate_plan_review` functions and the repository's own router fixture; no product-code modification is required.
