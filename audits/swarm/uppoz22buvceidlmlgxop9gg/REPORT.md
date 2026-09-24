# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — DONE status bypasses result validity and required review before Close

- Affected workflow contract/invariant: `workflow/STATE.md` independent-review blocking and durable-result semantics; `workflow/REVIEW.md` blocking lifecycle; `workflow/CLOSE.md` durable approved-scope completion; router fail-closed rule for invalid/incomplete bindings.
- Expected behavior: A Card cannot become terminal when its durable result is missing/invalid or when REQUIRED/activated RECOMMENDED review has no exact GREEN attempt. Recovery from a contradictory `done` Board entry must validate the terminal package or fail closed before Close.
- Actual behavior: `validate_board()` only requires that a `done` Card contain a syntactically valid result locator. It does not require commit/blob identity, the result file to exist, the Card contract to be read, or the review requirement to be satisfied. `select_route()` performs result/review validation only for `in_progress` Cards. With all Cards marked `done`, it routes directly to `close` without reading the Card, result, or review attempts. A review-required Card can therefore be marked `done` with a nonexistent result path and zero review attempts and still reach Close.
- Minimal reproduction: Copy `tests/fixtures/router/valid-project`; make M01-T04's Card say `Review requirement: required`; change Board status from `in_progress` to `done`; add `[cards.result] class="result"` with a workstream-local path but do not create the file or any review attempt. `select_route(...)` reaches `("route", "close")` because the terminal branch never dereferences those artifacts.
- Why this is materially load-bearing: It turns mutable status into stronger authority than the required durable result/review evidence and can advance an unreviewed or nonexistent implementation into integration/finalization.
- Defect class / likely siblings: Terminal-state validation is not symmetric with active-state validation. Any stale/manual/partially-written transition to `done` can bypass result content, exact identity, review verdict and evidence checks.
- Existing tests that failed to catch it: `test_all_terminal_cards_route_to_close_not_directly_to_stop` covers only a happy-path Card with `review_requirement = none`. State fixtures also demonstrate that a DONE result locator may omit immutable identity, but there is no negative test for DONE + missing result, DONE + REQUIRED/no attempt, DONE + pending/RED, or DONE + stale subject.
- Reproduction artifact, if any: `repros/adversarial_repros.py::f1_done_bypasses_result_and_required_review`.

### F2 — Exact Git subjects are trusted as strings instead of verified Git objects

- Affected workflow contract/invariant: immutable Planning freeze/Plan Review subjects; exact implementation result/review subject binding; exact predecessor dependency identity; stale commit/blob/result/review fail-closed behavior.
- Expected behavior: Before an immutable `repository@commit:path@blob` identity authorizes Plan Review reuse, execution, dependency launch, implementation review or finalization, the repository/commit/path/blob tuple must resolve to the claimed bytes. Same-path changed content or forged/stale hashes must not be accepted.
- Actual behavior: Production validation generally checks only 40-hex syntax and string equality. `_git_blob_subject_key()`, result-locator validation, `exact_result_subject()` and `review_subject()` do not resolve Git objects. The router reads the current working-tree result file but then compares review coverage to the Board's declared commit/blob strings, so a Board and GREEN review can agree on arbitrary hashes and reach `post_review_finalization`. READY dependency refresh compares the Card dependency tuple only to the Board's DONE-result tuple and reads the working-tree path, without proving the commit/blob name those bytes. Planning is even weaker: the router does not read `plan_path` at all or verify the Planning subject repository against `PROJECT.md`; an approved plan and GREEN Plan Review with synthetic hashes and a different repository string can pass into Board execution.
- Minimal reproduction: The repository's own `RouterTests.install_reviewable_result()` and `add_review_attempt(..., "green")` construct a temporary non-Git project with synthetic `a*40/b*40` result/review identities; `select_route()` expects and returns `post_review_finalization`. Separately, `install_approved_plan()` uses Planning subject repository `owner/repo` while fixture `PROJECT.md` declares `owner/router-fixture`, does not create `planning/MASTER_PLAN.md`, and still routes through the approved plan to Board execution.
- Why this is materially load-bearing: Exact immutable identities are the anti-staleness boundary for review reuse, recovery truth and dependency launch. If they are self-asserted strings, stale or fabricated state can claim GREEN coverage for bytes that were never reviewed.
- Defect class / likely siblings: Missing Git dereference/rehash at trust boundaries. Confirmed surfaces are Planning/Plan Review, active Card result + implementation Review, and READY predecessor dependencies; terminal DONE handling in F1 compounds the same class.
- Existing tests that failed to catch it: Several router tests intentionally use synthetic `a*40/b*40` hashes in temporary non-Git fixtures and assert successful continuation, so they test tuple equality but not immutable identity resolution. The stale-dependency test changes the Board tuple and proves mismatch detection, but not whether either tuple names the actual result bytes.
- Reproduction artifact, if any: `repros/adversarial_repros.py::f2_forged_result_identity_can_finalize_green` and `::f2_forged_plan_identity_can_reach_execution`.

### F3 — Orphan implementation Research can preempt the Task Board without Board ownership

- Affected workflow contract/invariant: `workflow/STATE.md` implementation/recovery Research ownership; `workflow/RECOVERY.md` recovery precedence requiring the Task Board to point to exact implementation Research; interrupted-runtime continuation.
- Expected behavior: Research with `origin_role = execution_prep|execution|execution_resolution` is owned by the selected Task Board through its exact `research_obligation` locator. If the workstream Research slot contains implementation Research but the Board does not point to it, the state is stale/contradictory and must fail closed rather than letting that record seize control.
- Actual behavior: `select_route()` reads the workstream-level Research locator before Intake, Planning or the Task Board. If that record is `state = active`, it immediately routes to Research for every allowed origin role, including execution roles. `validate_research()` accepts execution origins/return targets, but this early branch never verifies a Board `research_obligation` pointer. The Board is not read at all. Therefore a stale/orphan active execution Research record can hijack an otherwise active Card.
- Minimal reproduction: Start from the router fixture with M01-T04 `in_progress`; add a workstream `[research]` locator to RESEARCH.toml; write valid active Research with `origin_role="execution"`, `origin_subject="M01-T04"`, `return_target="execution:M01-T04"`; leave Task Board without `research_obligation`. The early Research branch returns `("route", "research")` before Board validation.
- Why this is materially load-bearing: The Board pointer is the durable ownership/recovery binding that prevents stale Research-slot reuse from replaying or diverting implementation work. Bypassing it makes a reused singleton Research record hidden authority over current execution.
- Defect class / likely siblings: Phase/origin-insensitive early Research dispatch. Active execution-origin Research needs Board binding before it may preempt; completed execution-origin Research without the pointer also enters the wrong top-level branch and can degrade into generic Recovery rather than exact Board-owned return semantics.
- Existing tests that failed to catch it: Generic workstream Research tests cover Brainstorming-origin Research; Board Research tests add only the Board `research_obligation` and read the same RESEARCH.toml directly. There is no negative-space case with an execution-origin workstream Research locator and no Board pointer.
- Reproduction artifact, if any: `repros/adversarial_repros.py::f3_orphan_execution_research_preempts_board`.

### F4 — A human-authority blocker can coexist with in_progress and be ignored

- Affected workflow contract/invariant: Execution returned-result/blocker classification; Recovery blocker semantics; explicit human/authorization boundary precedence; fail-closed contradictory Task Board state.
- Expected behavior: Persisting a real unresolved blocker and marking the Card `blocked` are one semantic transition. A blocker locator on any non-`blocked` Card is contradictory durable state and must fail closed; in particular `human_authority` must not be bypassed by Execution.
- Actual behavior: `validate_board()` enforces only one direction: status `blocked` requires a blocker locator. It also validates a blocker locator when present on any status, but never requires status `blocked` when the locator exists. Thus `in_progress + blocker` is accepted. The router processes `in_progress` before the blocked-card branch and never reads that blocker record, so an `in_progress` Card carrying a valid `human_authority` blocker routes to ordinary `execution` instead of a user stop or Recovery.
- Minimal reproduction: Keep fixture M01-T04 status `in_progress`; attach a workstream-local blocker locator and a valid blocker record with `class="human_authority"`; call `select_route()`. Board validation succeeds and the active-card branch returns `("route", "execution")` without reading the blocker file.
- Why this is materially load-bearing: A partially-written or contradictory blocker transition can silently cross a human authority boundary and continue implementation.
- Defect class / likely siblings: Status/owned-artifact bidirectional invariants are incomplete. The same accepted contradiction can exist with `ready` or `done` plus blocker locators, producing preparation or Close behavior while blocker evidence is ignored.
- Existing tests that failed to catch it: `install_blocker()` always changes `in_progress -> blocked` before attaching the blocker, and blocker tests cover only internally consistent states. No negative test attaches blocker state to a non-blocked Card.
- Reproduction artifact, if any: `repros/adversarial_repros.py::f4_nonblocked_human_blocker_is_ignored`.

## Non-blocking observations

No additional advisory/style items were promoted. The audit intentionally kept speculative redesign ideas out of the material set.

## Coverage

The audit was bound to commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045` and inspected canonical `workflow/**` contracts for Router, State, Planning/Plan Review, Execution/Execution Prep, Review, Recovery and Close; production `tools/router.py`, `tools/state_contract.py`, `tools/execution_contract.py`, `tools/recovery_contract.py`, `tools/close_contract.py`; relevant templates; router/state/recovery/close/review tests and fixtures; and the repository test workflow.

The four selected attack lenses were exercised as follows: RED/recovery/blocker continuation (F3, F4); Planning/Premium/Execution precedence (F2 Planning surface and Board handoff); Close/finalization/end-of-scope (F1); stale commit/blob/path/result/review identity (F1, F2).

Negative-space cases were constructed around DONE-without-terminal-proof, synthetic Git identities, execution-origin Research without Board ownership, and blocker/status contradictions. Existing tests were compared specifically for omitted negative cases rather than treated as proof of correctness.

## Confidence and limitations

Confidence is high in the four control-flow defects because each follows directly from production validation/selector branches at the immutable target, and F2's synthetic-identity behavior is already exercised by existing router test helpers in temporary non-Git projects.

I could not execute the preserved repro script in this chat's local container: direct Git network access is disabled, and the connected Desktop Commander device reported its monthly remote-call allowance exhausted. The repros therefore remain executable artifacts for a normal checkout rather than claimed local run output. GitHub source/readback was used against the exact commit throughout.

Blindness note: I did not inspect `audit/*` branches/reports, GitHub Issues, or PR comments. An initial GitHub commit fetch unexpectedly returned the merge commit's diff, which included implementation-workstream evidence files from that commit; I did not use those conclusions as a defect checklist. The finding set above was independently frozen from canonical workflow/tool/test behavior. No post-freeze historical comparison was performed.

## Post-freeze historical comparison

Not performed.
