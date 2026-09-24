# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

Four material defects were independently demonstrated by tracing the production selector/validators against the canonical workflow contracts at exact subject commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`.

## Material findings

### F1 — Immutable Git identities are syntactic labels, so same-path mutations bypass freshness and review checks

- **Affected workflow contract/invariant:** `workflow/STATE.md` requires READY launch refresh to verify each predecessor result by exact path + immutable commit/blob identity and explicitly says missing, stale, or same-path-changed dependency inputs fail closed. The same state/recovery contracts require implementation review attempts to bind the exact immutable current result subject before GREEN finalization.
- **Expected behavior:** A file at a dependency/result/plan path whose bytes no longer match the declared immutable Git blob must not be accepted merely because its TOML locator still contains the old 40-hex strings. READY launch should recover/fail closed for a same-path mutation, and a reviewed result changed after GREEN must require a new exact review subject.
- **Actual behavior:** `validate_locator`, `_git_blob_subject_key`, and `exact_result_subject` validate only the shape/presence of commit/blob strings. `refresh_ready_card` compares the Card's declared `(path, commit, blob)` tuple with the DONE predecessor's declared tuple and then reads the current path, but never verifies those bytes against the declared blob/commit. The implementation-result review path similarly compares the review's declared subject string with the Board result's declared subject string while reading/parsing the current result file independently. A same-path byte mutation with unchanged labels therefore remains launchable/review-finalizable.
- **Minimal reproduction:** Start with a READY Card depending on a DONE predecessor result whose Board and Card both declare `results/M01-T03.md@aaaa...:bbbb...`. Confirm the selector reaches `execution_prep`. Change only the bytes of `results/M01-T03.md`, leave both declared identities untouched, and select again: the production path still satisfies the tuple equality and reads the changed file without hashing/verifying it. Sibling reproduction: create an in-progress Card with a syntactically valid result plus exact GREEN review, mutate only the result file's tests/readback summary, leave the Board/review blob labels unchanged; the selector still reaches `post_review_finalization`.
- **Why this is materially load-bearing:** Exact Git identity is the mechanism that prevents stale predecessor inputs and stale GREEN review coverage. Treating immutable identity as an unauthenticated label allows unreviewed/mutated content to launch downstream work or pass deterministic finalization while claiming coverage for different bytes.
- **Defect class / likely siblings:** Missing dereference/verification of durable immutable identities. The same class applies wherever a `git_blob` or `path + commit + blob` subject is accepted by string equality without resolving the named Git object, including Planning/Plan Review and any future exact-result reuse path.
- **Existing tests that failed to catch it:** `test_ready_card_stale_dependency_fails_closed_before_launch` changes the Board's declared commit/blob as well as the file, so tuple inequality catches it before byte identity matters. `test_changed_result_after_terminal_review_requires_new_attempt` likewise changes the Board's declared blob string. Neither test mutates same-path bytes while keeping the declared immutable identity constant.
- **Reproduction artifact, if any:** `audits/swarm/6ugr6l0d6zsn8fgvpdj1cjsd/repros/repro_router_semantic_holes.py` — `f1_same_path_dependency_mutation` and `f1_same_path_reviewed_result_mutation`.

### F2 — Research short-circuit bypasses higher-precedence explicit and premium stops

- **Affected workflow contract/invariant:** `tools/router.py` declares `explicit_human_or_premium_boundary` above `research_return` in `PRIORITY_FOUNDATION`. `workflow/BRAINSTORMING.md` makes `explicit_user_stop` a real stop, and `workflow/USER_STOP.md` makes premium A/B/C real-stop boundaries.
- **Expected behavior:** When a valid durable state simultaneously carries an explicit human/premium boundary and a Research obligation, the higher-precedence boundary must win, or the combination must be rejected as contradictory. A lower-precedence Research route must not make the stop unreachable.
- **Actual behavior:** Immediately after validating the selected workstream, `select_route` loads its top-level Research record and returns for `active` or `complete` Research before it ever loads Brainstorming, Definition, or Planning. The relevant validators independently accept a valid active Research record alongside a valid Brainstorming `explicit_user_stop = true`, and they also accept active Definition-return Research alongside a GREEN Definition with premium A due. In both cases the selector's Research return happens before the higher-precedence stop can be observed.
- **Minimal reproduction:** Co-bind (1) a valid active `RESEARCH.toml` with `origin_role = "brainstorming"`, `return_target = "brainstorming"`, and (2) a valid active `BRAINSTORM.toml` with `explicit_user_stop = true`. The selector returns `route/research` before reading the stop. Sibling: promoted Brainstorming + GREEN Definition with `premium_a = "due"` + valid active Definition-return Research also returns `route/research` before the premium-A stop.
- **Why this is materially load-bearing:** A durable explicit user stop is human authority, and premium stops are mandatory workflow boundaries. Allowing fact-gathering state to hide either boundary violates both deterministic precedence and user-control semantics.
- **Defect class / likely siblings:** Early-return precedence inversion between independently valid state owners. Any higher-precedence obligation stored in a record loaded after the top-level Research short-circuit is exposed to the same class; premium B/C and other later explicit boundaries deserve sibling tests.
- **Existing tests that failed to catch it:** Router tests assert the priority tuple and test Research and premium/explicit routes separately, but do not construct co-bound Research + higher-precedence stop states. Thus the declarative precedence constant is not executable precedence for this interaction.
- **Reproduction artifact, if any:** `audits/swarm/6ugr6l0d6zsn8fgvpdj1cjsd/repros/repro_router_semantic_holes.py` — `f2_research_bypasses_explicit_user_stop` and `f2_research_bypasses_premium_a`.

### F3 — Card status/result contradictions can ignore durable completion evidence and replay work

- **Affected workflow contract/invariant:** `workflow/STATE.md` and `workflow/RECOVERY.md` say a durable valid semantic result is recovery truth and prevents implementation replay; invalid/stale/contradictory binding must fail closed. Mutable Task Board state is supposed to represent the single Card lifecycle coherently.
- **Expected behavior:** A Card that already carries a durable result must be reconciled/reviewed/finalized according to that result, or an impossible status/result combination must fail closed. A Card must not be simultaneously READY/planned/blocked and completed enough to carry a durable accepted result that the router then ignores.
- **Actual behavior:** `validate_board` permits a `result` locator on every Card status; it only requires one when status is `done`. The router inspects a result only inside the `in_progress` branch. A READY Card with a valid result passes `refresh_ready_card` and routes to `execution_prep`; planned cards with results fall to JIT preparation, and blocked cards route by blocker classification. The durable result is therefore not recovery truth for these accepted state combinations.
- **Minimal reproduction:** Use a valid in-progress Card/result with review requirement `none`, then change only its Task Board status to `ready` while retaining the result locator. `validate_board` accepts the record. The selector places the Card in the READY set, performs launch refresh, ignores `cards.result`, and returns `route/execution_prep` instead of result reconciliation or Recovery.
- **Why this is materially load-bearing:** Torn or partially persisted state can make already accepted implementation work execute again. For Cards with external effects, that turns a state-consistency bug into duplicate mutation risk; even for pure code it can overwrite or diverge from the durable accepted result.
- **Defect class / likely siblings:** Missing status/result state-machine invariants plus routing that conditions result authority on one mutable status. Siblings are `planned + result`, `ready + result`, and `blocked + result`; review-attempt/status coherence should be tested similarly.
- **Existing tests that failed to catch it:** State-contract tests require results for DONE Cards but do not reject results on non-result-bearing statuses. Router tests exercise a result on `in_progress` and DONE closure, but not READY/planned/blocked Cards that retain result evidence.
- **Reproduction artifact, if any:** `audits/swarm/6ugr6l0d6zsn8fgvpdj1cjsd/repros/repro_router_semantic_holes.py` — `f3_ready_result_is_ignored`.

### F4 — Active execution trusts Card existence rather than validating the stable Task Card contract

- **Affected workflow contract/invariant:** `workflow/EXECUTION_PREP.md` defines the stable Task Card contract as exact Card ID, bounded included/excluded scope, authority refs, dependency identities, observable acceptance, tests/readback, review requirement, and optional technical contract. `workflow/EXECUTION.md` requires launch refresh before implementation. `workflow/ROUTER.md` requires incomplete/invalid binding to fail closed.
- **Expected behavior:** On fresh recovery of an `in_progress` Card, the selector must establish that the durable Card still satisfies the stable Card contract before routing implementation. A missing/incomplete acceptance or authority contract should be Recovery, not Execution.
- **Actual behavior:** The active/no-result branch in `select_route` only reads the Card file to prove it exists and then returns `route/execution`. It invokes `parse_task_card` only if the Card already has a result. The repository's own default router fixture proves the gap: its active M01-T04 Card contains only a heading and one sentence, while `test_active_card_routes_to_runtime_neutral_execution` and the baseline route test expect Execution. The same text is rejected by `parse_task_card` for missing stable fields.
- **Minimal reproduction:** Run `select_route` on `tests/fixtures/router/valid-project`; it returns `route/execution` for M01-T04. Pass that exact fixture Card to `parse_task_card(..., "M01-T04", "sample-workstream")`; it raises `ValidationError` because the stable fields are absent.
- **Why this is materially load-bearing:** Recovery after a context/runtime transition can continue code mutation without durable bounded scope, authority, dependencies, acceptance, tests, or review requirements. The workflow therefore cannot prove that the recovered execution is still authorized or know how to validate/finalize it.
- **Defect class / likely siblings:** Validation asymmetry between READY/result-bearing Cards and active result-less Cards. Any recovery path that treats file existence as contract validity can accept truncated/stale Card authority.
- **Existing tests that failed to catch it:** This is not merely uncovered negative space: the shipped active-Card fixture and tests encode the fail-open route as the expected behavior, while READY tests replace the fixture with a complete Card before launch refresh.
- **Reproduction artifact, if any:** `audits/swarm/6ugr6l0d6zsn8fgvpdj1cjsd/repros/repro_router_semantic_holes.py` — `f4_active_malformed_card_executes`.

## Non-blocking observations

The Card-result parser validates evidence-reference path syntax but the recovery selector does not dereference those evidence files when deciding that a semantic result is valid. This looks adjacent to F1/F4, but this audit did not freeze it as a separate material finding because the contract may rely on acceptance-time evidence validation before durable result creation.

The plugin/bootstrap lens did not produce a material defect in this subject. The exact SessionStart implementation is intentionally thin; it binds to the package root containing the hook, rejects a configured-root mismatch, rejects a missing/malformed router, and rejects a router symlink escaping the package root. The corresponding delivery tests cover those boundaries.

## Coverage

The audit remained bound to `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045` for product semantics. It inspected canonical routing/state/authority/Brainstorming/Research/Planning/Plan Review/Execution Prep/Execution/Recovery/Close/user-stop contracts; the production router and state/execution/recovery/close helpers; router/state/execution/recovery/close test suites and fixtures; Task Board/Card/result templates; the state-envelope schema; Codex plugin metadata, Skill, SessionStart hook and delivery tests; ChatGPT bootstrap instructions; and the repository test entrypoint.

All four selected attack lenses were exercised:
- router precedence / conflicting obligations: F2, plus Board-precedence negative-space checks;
- Planning / Premium gates / Execution precedence: F2 premium-A sibling and review-subject checks;
- malformed/contradictory state / fail-closed behavior: F1, F3, F4;
- plugin / install / update / SessionStart / bootstrap drift: no material finding demonstrated.

The audit did not inspect any `audit/*` branch/report, GitHub Issue, or PR comment during blind discovery. Historical workstream evidence was inspected only after the four-finding set was frozen.

## Confidence and limitations

Confidence is high in the four semantic counterexamples because each follows a concrete production-code path and is anchored to explicit canonical invariants. F4 is additionally embodied by the repository's own executable router fixture/test expectation. F1's existing tests also expose the precise negative space: they detect changed declared labels, not changed bytes behind unchanged labels.

Ad-hoc execution of the preserved reproduction script was not available in this chat environment: the local container had no usable repository-network checkout path and the outer command harness was unavailable to this turn. The reproductions are therefore preserved as non-mutating scripts against the repository's existing disposable test helpers rather than claimed as locally executed results. This limitation does not alter the source-level actual behaviors described above, but an independent runner should execute the script on the exact subject commit as final confirmation.

No exhaustive historical search was performed after freeze; historical classification below is based only on directly relevant durable material already present at the exact subject.

## Post-freeze historical comparison

- **F1 — apparently new (limited comparison).** The inspected `DECISION_M07_L08_DURABLE_EVIDENCE_LIMITATION.md` is a narrowly accepted historical loss-of-disposable-evidence exception; it does not document or waive production failure to authenticate current files against declared Git blob identities.
- **F2 — apparently new (limited comparison).** The inspected historical `issue-router-board-precedence` diagnosis/fix concerned approved-plan/editorial routes returning Execution Prep before a co-bound Task Board. It does not cover top-level Research preempting explicit/premium stops.
- **F3 — apparently new (limited comparison).** The same historical Board-precedence repair ensures a co-bound Board is dispatched, but does not enforce internal Card status/result coherence or result precedence across READY/planned/blocked statuses.
- **F4 — apparently new (limited comparison).** No inspected historical item identified the active/no-result Card-validation asymmetry; current regression fixtures instead preserve that behavior.
