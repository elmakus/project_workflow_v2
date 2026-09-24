# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Declared immutable Git identities are never resolved against the bytes actually read

- Affected workflow contract/invariant: workflow/STATE.md requires exact immutable commit/blob identity for predecessor results and exact immutable review subjects; workflow/EXECUTION_PREP.md requires same-path-changed dependency inputs to fail closed; workflow/REVIEW.md requires one exact immutable Git content subject.
- Expected behavior: before launch, review reuse, result reconciliation or GREEN finalization, the selector must establish that repository + commit + path + blob identifies the artifact bytes being consumed. A same-path content change with stale declared commit/blob identity must fail closed or force a new exact subject.
- Actual behavior: tools/state_contract.py validates commit/blob only as 40-hex strings. tools/router.py refresh_ready_card compares the Task Card dependency tuple to the Task Board result locator tuple and then reads the current path, but never proves that the declared blob is the blob at that commit/path or that the bytes read match it. Active-result review uses exact_result_subject(), which only formats the Task Board strings; review_subject() likewise only formats stored strings. Therefore changing result/dependency file bytes while leaving the declared tuple unchanged preserves the old identity and still routes as if the exact subject were unchanged.
- Minimal reproduction: on the router valid-project fixture, add a DONE predecessor result with path@A:B, make the active Card READY with the same dependency, verify execution_prep, then rewrite only the predecessor result file without changing board/Card A:B. The selector still returns execution_prep. Sibling reproduction: create a required-review result with GREEN review, rewrite only the result artifact while preserving Card ID/shape, and the selector still returns post_review_finalization.
- Why this is materially load-bearing: stale or replaced implementation evidence can be launched against, treated as completed recovery truth, or finalized under a GREEN review that covered different bytes.
- Defect class / likely siblings: stale commit/blob/path identity; syntactic Git-subject validation without repository resolution. The same primitive is used by frozen Planning/Plan Review subjects.
- Existing tests that failed to catch it: test_ready_card_stale_dependency_fails_closed_before_launch changes the declared board commit/blob together with the file; test_changed_result_after_terminal_review_requires_new_attempt and test_active_review_for_changed_result_fails_closed change the declared result blob. None changes only the bytes at the same declared path/identity.
- Reproduction artifact, if any: repros/repro_router_counterexamples.py (cases F1_dependency_bytes and F1_reviewed_result_bytes).

### F2 — Co-bound implementation Research is shadowed by the pre-execution Research branch

- Affected workflow contract/invariant: workflow/RECOVERY.md says Task-Board-owned implementation/recovery Research must recover its exact return target before unrelated execution; workflow/ROUTER.md routes completed Research to its exact owner. tools/v1_migration.py emits the same implementation Research locator in both task_board.research_obligation and workstream.research.
- Expected behavior: a legal completed execution Research record co-bound exactly as migration emits must route to execution, execution_prep, or execution_resolution according to its exact return_target.
- Actual behavior: tools/router.py reads workstream.research before the Task Board. For state=complete it indexes a pre-execution-only owner map containing intake, brainstorming, and definition. A legal execution return_target such as execution_resolution:M01-T04 causes KeyError, which is caught and converted to Recovery. The later Task Board Research branch that correctly understands execution_* targets is unreachable in this co-bound state.
- Minimal reproduction: install a complete Task Board Research record with return_target=execution_resolution:M01-T04; it routes execution_resolution. Add workstream.research pointing to the same RESEARCH.toml, matching the binding emitted by tools/v1_migration.py; the same durable Research record now routes recovery_boundary.
- Why this is materially load-bearing: a legal migrated/recovered state cannot continue deterministically and is rejected solely because two canonical owners point at the same intended implementation Research record.
- Defect class / likely siblings: router precedence/shadowing plus producer-consumer parity drift between v1_migration.py and router.py.
- Existing tests that failed to catch it: test_task_board_research_return_is_recovered_before_execution installs only task_board.research_obligation and never co-binds workstream.research; migration tests do not feed the emitted co-bound state through the production router.
- Reproduction artifact, if any: repros/repro_router_counterexamples.py (case F2_cobound_execution_research).

### F3 — Execution Research can route to a nonexistent or unrelated Card

- Affected workflow contract/invariant: workflow/RESEARCH.md gives every Research record one exact return owner; workflow/RECOVERY.md requires recovery of the exact Task-Board-owned Research obligation and return target; malformed/stale/contradictory bindings must fail closed.
- Expected behavior: an execution_* return_target must be structurally complete and bound to an actual compatible Card/owner in the selected Task Board. A nonexistent Card target must route Recovery.
- Actual behavior: validate_research accepts any string beginning execution:, execution_prep:, or execution_resolution:. It does not validate the suffix, bind it to origin_subject, or require that a matching Card exists. The Task Board router branch strips the prefix and returns that arbitrary suffix as the subject.
- Minimal reproduction: with a Task Board Research pointer, set origin_role=execution, origin_subject=M99-T99 and return_target=execution:M99-T99 while the board contains only M01-T04. Validation succeeds and the selector returns route/execution with subject M99-T99 instead of Recovery.
- Why this is materially load-bearing: a stale/corrupt Research record can redirect continuation away from the canonical Card and create an execution obligation for work that does not exist in durable Task Board state.
- Defect class / likely siblings: missing cross-record owner binding; prefix-only validation of exact return identity.
- Existing tests that failed to catch it: test_task_board_research_return_is_recovered_before_execution covers only a matching M01-T04 target and has no nonexistent/mismatched target negative case.
- Reproduction artifact, if any: repros/repro_router_counterexamples.py (case F3_unbound_research_target).

### F4 — DONE status bypasses REQUIRED review and can route directly to Close

- Affected workflow contract/invariant: PWV2-REQ-036 and workflow/REVIEW.md require REQUIRED and activated RECOMMENDED review to block completion until GREEN; pending/in-progress/RED attempts block terminal Card completion.
- Expected behavior: a Card marked done while its stable contract requires review and no exact GREEN attempt exists is contradictory durable state and must fail closed or resume the review/correction obligation before Close.
- Actual behavior: validate_board requires a result locator for done Cards but does not load the Task Card contract or review-attempt verdicts. router.py loads review history only for an in_progress Card. When every Card is done it routes Close without checking review requirement or pending/RED/no-review state.
- Minimal reproduction: create a required-review result, add a pending review attempt, then change only Card status from in_progress to done. The state passes board validation and the selector returns route/close.
- Why this is materially load-bearing: a single status edit/corruption can bypass the independent-review gate and place unreviewed or RED work on the finalization path.
- Defect class / likely siblings: terminal-state trust without revalidating blocking obligations.
- Existing tests that failed to catch it: test_required_review_blocks_until_green_then_routes_finalization keeps the Card in_progress; test_all_terminal_cards_route_to_close_not_directly_to_stop uses Review requirement: none.
- Reproduction artifact, if any: repros/repro_router_counterexamples.py (case F4_done_bypasses_pending_review).

### F5 — Missing result/review evidence is accepted as durable completion evidence

- Affected workflow contract/invariant: workflow/EXECUTION.md requires accepted results to carry durable evidence refs; workflow/REVIEW.md requires durable verdict evidence for terminal attempts; recovery treats a valid durable result as authoritative completion evidence.
- Expected behavior: evidence locators used to justify accepted result or terminal GREEN/RED review must resolve to readable durable evidence. Missing evidence must invalidate the state before reconciliation/finalization.
- Actual behavior: parse_card_result validates evidence refs only lexically and router.py never reads them. validate_review requires terminal evidence_path to be non-empty and lexically relative, but router.py never dereferences it. A deleted/nonexistent evidence file therefore does not invalidate the result or terminal review.
- Minimal reproduction: create a valid no-review result and delete its evidence file; the selector still returns result_reconciliation. Separately, create a required result plus GREEN review, delete the review evidence file, and the selector still returns post_review_finalization.
- Why this is materially load-bearing: completion and GREEN finalization can survive loss or fabrication of the very durable evidence claimed to justify them.
- Defect class / likely siblings: existence/readback gap for durable evidence locators.
- Existing tests that failed to catch it: router result/review helpers always materialize evidence files; state-contract tests reject empty evidence_path but do not test a non-empty path whose artifact is absent.
- Reproduction artifact, if any: repros/repro_router_counterexamples.py (cases F5_missing_result_evidence and F5_missing_review_evidence).

### F6 — GREEN implementation review is not bound to immutable acceptance criteria

- Affected workflow contract/invariant: workflow/STATE.md and workflow/REVIEW.md say each implementation review attempt binds the exact immutable subject to its exact acceptance surface; material acceptance change requires renewed coverage rather than reuse of stale GREEN.
- Expected behavior: if the stable Task Card acceptance/tests surface changes after GREEN, the old attempt must no longer authorize finalization; the selector must require a new exact review or fail closed.
- Actual behavior: REVIEW_ATTEMPT acceptance stores only class=task_card plus a mutable path. validate_review checks that the path stem matches card_id, but stores no commit/blob identity for the acceptance surface. router.py rereads the current Task Card only to parse fields/review requirement; it compares the review only to the result subject. Editing Acceptance or Required tests/readback in the same Task Card path after GREEN leaves the old review accepted and still routes post_review_finalization.
- Minimal reproduction: create a required result plus GREEN review, then change only the Task Card Acceptance line at the same path. The selector still returns post_review_finalization.
- Why this is materially load-bearing: reviewed code can be finalized against materially different acceptance criteria that the independent reviewer never evaluated.
- Defect class / likely siblings: mutable-path acceptance identity; review coverage not cryptographically/version bound.
- Existing tests that failed to catch it: implementation-review tests mutate result blob identity but never mutate the Task Card acceptance surface after GREEN.
- Reproduction artifact, if any: repros/repro_router_counterexamples.py (case F6_mutable_acceptance_surface).

## Non-blocking observations

The locator layer performs lexical class/workstream checks and Reads._read_path resolves paths with project-root containment. A resolved symlink can still move within the project root across an authority/workstream class boundary because the containment check is project-wide rather than class-root-specific. I did not freeze this as a material finding because I could not execute a symlink probe in the available environment and the exact intended symlink policy is not stated explicitly enough in the inspected contracts.

## Coverage

Inspected only the exact subject commit 4fb4bfb7d7b1481d6f347c182fc96a5a1135e045 through GitHub Git/tree/file reads. No audit/* branch, swarm report, GitHub Issue, PR comment, or historical defect narrative was used during discovery.

Canonical/production surfaces inspected include workflow/ROUTER.md, STATE.md, INTAKE.md, RESEARCH.md, GITHUB_ISSUES.md, RECOVERY.md, EXECUTION_PREP.md, EXECUTION.md, REVIEW.md, CLOSE.md; requirements/PROJECT_WORKFLOW_V2.md; relevant templates; tools/router.py, state_contract.py, execution_contract.py, recovery_contract.py, close_contract.py, migration_apply.py and v1_migration.py; and targeted router/state/close tests and fixtures.

Selected attack lenses exercised:
- Research / Intake / tracker / external-side-effect recovery: execution Research ownership/return routing, tracker validation and external-effect helper semantics.
- helper vs documented semantics / parity drift / negative space: migration-to-router co-binding parity and missing negative tests around evidence, terminal review and exact identities.
- path traversal / locator safety / cross-workstream binding: lexical path validation, project-root containment and class/workstream locator binding; symlink aliasing retained only as a non-blocking observation.
- stale commit/blob/path/result/review identity: dependency/result Git identity, review subject identity and acceptance-surface binding.

## Confidence and limitations

Confidence is high in the six code-path findings because each follows deterministic production selector/validator branches and is paired with a minimal repro harness that calls tools.router.select_route against the repository's existing valid fixture.

I could not execute the repository test suite or repro harness in this audit session: the local container has no GitHub network access, and the connected Desktop Commander device reported its monthly usage limit before command execution. Consequently, Actual behavior above is derived from exact production code at the immutable subject rather than a captured runtime transcript. The repro harness is non-mutating and uses temporary fixture copies so it can be executed directly from this audit branch later.

## Post-freeze historical comparison

Not performed. The six findings above were frozen before any historical comparison, and no historical evidence/review narratives were inspected afterward.
