# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Durable explicit user stop can lose router precedence

- Affected workflow contract/invariant: `workflow/BRAINSTORMING.md` defines an explicit user stop as a real stop; `workflow/ROUTER.md` and `PRIORITY_FOUNDATION` place explicit human/premium boundaries ahead of lower-precedence continuation.
- Expected behavior: if the selected durable Brainstorming record carries `explicit_user_stop = true`, continuation must stop before Research return, Definition, Planning, or implementation-stage work can advance, or contradictory later state must fail closed to Recovery.
- Actual behavior: `tools/router.py` returns from active/completed Research before it reads Brainstorming, and after Brainstorming is read it may return from Definition/Planning before reaching the later `explicit_user_stop` check. The Brainstorming validator permits a promoted, exactly authorized revision with `explicit_user_stop = true`. A representative valid state with promoted Brainstorming + explicit stop + GREEN Definition therefore routes to Planning instead of stopping.
- Minimal reproduction: copy `tests/fixtures/router/valid-project`; install the existing test helper's GREEN Definition state; change only `explicit_user_stop = false` to `true` in its promoted Brainstorming record; call production `select_route`. The selected route is `route/planning`, not `stop/explicit_user_stop`.
- Why this is materially load-bearing: a durable human stop is a workflow authority boundary. Continuing past it can cause later planning/execution obligations to be selected after the user explicitly stopped the scope.
- Defect class / likely siblings: router-precedence defect plus contradictory-state acceptance. The same structural risk applies wherever a higher-precedence human boundary is stored in a record whose check occurs after an earlier-returning owner.
- Existing tests that failed to catch it: `tests/test_router.py` exercises Brainstorming promotion and premium stops but contains no `explicit_user_stop = true` router case.
- Reproduction artifact, if any: `audits/swarm/yc80f4r9jz0jn7b0vzdv424d/repros/repro_material_findings.py` (`f1_explicit_stop_loses_precedence`).

### F2 — Exact Git subjects are trusted as self-asserted strings instead of authenticated Git identity

- Affected workflow contract/invariant: `workflow/STATE.md`, `workflow/EXECUTION_PREP.md`, and `workflow/REVIEW.md` require immutable path + commit/blob binding, stale/same-path-changed inputs to fail closed, and review verdicts to apply only to the exact current Git content subject.
- Expected behavior: before an exact Git subject is used to authorize READY launch, Plan Review reuse, implementation review finalization, or another exact-subject gate, the declared repository/commit/path/blob tuple must resolve to the actual Git object being consumed; changed file bytes under unchanged declared metadata must not retain prior review/dependency authority.
- Actual behavior: `tools/state_contract.py` validates commit/blob only as 40-hex strings. `_git_blob_subject_key` does not resolve Git, bind the repository to `PROJECT.repository`, or prove `commit:path -> blob`. READY dependency refresh compares the Card tuple only to the Task Board's tuple and then reads the current filesystem path. Implementation review compares the review tuple only to the Task Board result tuple. Consequently a result file can change while its board/review metadata stays unchanged and production routing still returns `post_review_finalization`; similarly arbitrary syntactically valid hashes can authenticate READY dependencies. Planning subjects also accept a different repository string from the consumer PROJECT.
- Minimal reproduction: create an active REQUIRED-review Card using the existing test helper, add a GREEN attempt, verify `post_review_finalization`; then mutate only the result Markdown bytes while leaving the board result `commit/blob` and GREEN review subject untouched. The result remains parse-valid and `select_route` still returns `post_review_finalization`.
- Why this is materially load-bearing: immutable content identity is the mechanism that makes stale review, stale dependency and recovery truth safe. If the tuple is merely self-asserted metadata, reviewed or depended-on content can change without invalidating the authority that was supposed to cover the prior bytes.
- Defect class / likely siblings: stale-subject / trust-the-wrong-blob defect across READY dependencies, implementation reviews, frozen plan subjects, Plan Review, and any future consumer of the same syntactic Git-subject helpers.
- Existing tests that failed to catch it: router fixtures intentionally use synthetic `"a"*40` / `"b"*40` identities and consider them valid. The stale dependency/review tests change the metadata hashes themselves; they do not mutate same-path bytes while leaving the asserted hashes unchanged. Planning test data also uses `owner/repo` while the fixture PROJECT repository is `owner/router-fixture`.
- Reproduction artifact, if any: `audits/swarm/yc80f4r9jz0jn7b0vzdv424d/repros/repro_material_findings.py` (`f2_changed_result_bytes_keep_green_review`).
- Repair direction: centralize Git-subject resolution and authenticate repository + commit:path -> blob against repository truth before consuming any exact-subject gate.

### F3 — Task Board status can bypass required review and can replay an already durable result

- Affected workflow contract/invariant: `workflow/STATE.md`, `workflow/EXECUTION.md`, and `workflow/REVIEW.md` require REQUIRED/activated RECOMMENDED review to block terminal Card completion until exact GREEN, and require a valid durable semantic result to prevent implementation replay.
- Expected behavior: Task Board lifecycle validation must reject terminal `done` for a Card whose stable contract requires review unless its exact current result has completed the required GREEN/finalization path. Likewise a Card with an accepted durable result must not be treated as an ordinary READY implementation launch.
- Actual behavior: `validate_board` checks only that a `done` Card has a result locator; it does not parse the Card contract, validate review requirement/history/verdict, or bind terminal status to post-review finalization. Review history is evaluated only inside the router's `active` branch. Therefore an otherwise valid REQUIRED-review Card with a pending (or RED/no) attempt can be changed from `in_progress` to `done`; the router skips review and routes `close`. The sibling state `status = ready` plus a valid result locator is also accepted; READY routing ignores that result and routes Execution Prep, allowing accepted work to be replayed.
- Minimal reproduction: use the existing test helper to install a REQUIRED-review result and a pending review attempt, then change only the Task Board status from `in_progress` to `done`. `validate_board` accepts the state and `select_route` returns `route/close` without reading or enforcing the pending review.
- Why this is materially load-bearing: Task Board status is the control surface deciding whether review/finalization remains blocking. Accepting contradictory cross-field lifecycle state permits required independent review to be bypassed and can also replay already accepted implementation work.
- Defect class / likely siblings: malformed/contradictory cross-record state not validated fail-closed. Siblings include `done + pending/RED/stale/no review`, `ready + result`, and other statuses carrying result/review fields whose legality depends on the stable Card.
- Existing tests that failed to catch it: required-review lifecycle tests keep the Card `in_progress`; the all-terminal-to-Close test uses review requirement `none`. State-contract tests validate fields mostly in isolation and do not assert the cross-record terminal-review invariant.
- Reproduction artifact, if any: `audits/swarm/yc80f4r9jz0jn7b0vzdv424d/repros/repro_material_findings.py` (`f3_done_card_bypasses_pending_required_review`).

## Non-blocking observations

A satisfied JIT trigger can coexist with all currently materialized Cards being DONE. The router validates the trigger but then selects Close solely because all Cards are DONE, rather than selecting Execution Prep to materialize the now-knowable downstream Card. `workflow/CLOSE.md` says Close must continue any already-authorized obligation, so this may be intended as a Close-mediated bounce rather than an illegal transition; however, the inspected production helper does not derive `next_authorized_obligation` from the Task Board. I did not freeze this as a material finding because the ownership boundary is not explicit enough to prove the Close route itself is forbidden.

The SessionStart bootstrap checks local package-root containment plus two router marker strings and has good negative tests for missing/malformed/path-escape/root mismatch cases. It does not cryptographically authenticate the bundled router, but no material authority violation was demonstrated under the documented installed-package trust model.

## Coverage

The audit remained bound to exact commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`. Before freezing findings I did not inspect `audit/*` branches, swarm reports, GitHub Issues/PR comments, or historical workstream evidence/review narratives.

Inspected and cross-checked the canonical router/state/authority modules and selected stage modules, production selectors/validators/helpers, Task Board/Card/review contracts, Close helpers, SessionStart/plugin/Skill/bootstrap code, repository test entrypoint, and focused router/state/delivery tests. The four selected attack lenses were exercised as follows:

- router precedence: explicit user-stop ordering against Research/Definition/Planning early returns;
- stale identity: result/review/dependency/plan Git-subject binding and same-path mutation negative space;
- plugin/bootstrap drift: package-root resolution, router marker validation, fail-closed tests and ChatGPT/Codex authority-source split;
- Task Board/JIT lifecycle: READY launch refresh, result/review state, DONE finalization, and JIT-to-Close interaction.

The material finding set was frozen as F1-F3 before any historical comparison.

## Confidence and limitations

Confidence is high for F1-F3 because each follows directly from production control flow plus accepted validator state, and each has a minimal preserved reproduction using the repository's own fixture/helpers and production selector.

I could not execute those reproduction scripts inside this ChatGPT session: the local container could not resolve `github.com`, and the connected Remote Desktop Commander device reported its monthly tool-call quota paused and instructed not to retry. I therefore inspected exact-commit source through the connected GitHub repository API and preserved executable non-mutating repros on the audit branch. The subject commit had no GitHub Actions workflow run returned by the repository API at audit time.

## Post-freeze historical comparison

Not performed. The finding set remains independently derived.
