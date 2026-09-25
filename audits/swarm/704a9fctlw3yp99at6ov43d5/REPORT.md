# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Exact Git identities are declared but never verified against the bytes they name

- Affected workflow contract/invariant: EXECUTION_PREP and STATE require READY dependencies to be bound by exact result path + immutable commit/blob identity, and explicitly require same-path-changed inputs to fail closed. REVIEW/RECOVERY likewise require GREEN coverage of the exact still-current result subject.
- Expected behavior: launch/review/finalization must prove that the bytes read at a declared path are the bytes named by the recorded blob/commit, and recover when they are stale or nonexistent.
- Actual behavior: refresh_ready_card compares only the Card dependency tuple (path, commit, blob) with the tuple copied into a DONE predecessor on TASK_BOARD.toml, then merely reads the path. It never resolves the commit/blob or hashes the bytes. The same declaration-only pattern is used for current result/review subjects. Arbitrary 40-hex identities therefore act as authority, and changing file bytes while leaving metadata unchanged is invisible.
- Minimal reproduction: create a DONE predecessor with result path P, commit A and blob B; make a READY Card depend on P@A:B. The selector routes execution_prep. Change only the bytes at P while leaving the Board and Card tuple unchanged. The membership test still succeeds and the selector still routes execution_prep instead of Recovery. The preserved repro also demonstrates the declaration-only identity path.
- Why this is materially load-bearing: stale dependency content can launch downstream implementation, and a same-path mutation of an already-reviewed result can preserve a nominal GREEN subject even though the reviewed bytes changed.
- Defect class / likely siblings: identity-by-string rather than identity-by-Git-object; likely siblings include Planning immutable subjects, implementation result refs and implementation/plan review subjects.
- Existing tests that failed to catch it: test_ready_card_stale_dependency_fails_closed_before_launch changes both the Board commit/blob metadata and the file bytes, so it exercises tuple mismatch rather than same-metadata/same-path byte mutation. Changed-result review tests likewise mutate the recorded blob field.
- Reproduction artifact, if any: repros/repro_router_semantics.py (F1).

### F2 — A REQUIRED-review Card can be marked DONE and bypass review entirely

- Affected workflow contract/invariant: REVIEW and STATE say REQUIRED/activated RECOMMENDED review is blocking; no attempt, pending, in-progress or RED must block terminal Card completion.
- Expected behavior: a Card whose stable contract requires review cannot be accepted as DONE unless the exact current result has a qualifying GREEN attempt; contradictory DONE state must fail closed or route the outstanding review/finalization obligation.
- Actual behavior: validate_board requires only that a DONE Card have a result locator. The router reads review requirements/history only inside the in_progress branch. If the same Card is persisted as done, the review code is skipped and an all-DONE Board routes directly to Close.
- Minimal reproduction: start with one Card, give it a valid durable result, set its Task Card field Review requirement: required, leave review_attempts empty, and set Board status to done. validate_board accepts the state and select_route returns route/close.
- Why this is materially load-bearing: a single mutable status value can erase a mandatory independent-review gate and move the workstream into final integration/closure semantics.
- Defect class / likely siblings: lifecycle invariants enforced only on one router branch rather than in the durable state validator; pending or RED attempts on a DONE Card are sibling bypasses.
- Existing tests that failed to catch it: required-review router tests keep the Card in_progress. test_all_terminal_cards_route_to_close_not_directly_to_stop explicitly uses Review requirement: none.
- Reproduction artifact, if any: repros/repro_router_semantics.py (F2).

### F3 — Contradictory READY + durable-result state is accepted and routes toward launch instead of reconciliation

- Affected workflow contract/invariant: EXECUTION and RECOVERY state that a valid durable semantic result is recovery truth and prevents implementation replay; malformed/contradictory durable state must fail closed.
- Expected behavior: a Card carrying an accepted result cannot simultaneously behave as a not-yet-executed READY Card. The selector must reconcile the durable result or reject the contradiction.
- Actual behavior: validate_board permits result locators on planned, ready and blocked Cards. Result reconciliation is checked only for in_progress. A READY Card with a result passes launch refresh and routes execution_prep with the reason that it is ready for launch.
- Minimal reproduction: add a valid result locator/file to the fixture Card, change its status from in_progress to ready, provide its authority file, and call select_route. The result is route/execution_prep, not result_reconciliation or Recovery.
- Why this is materially load-bearing: interrupted or partially persisted state can cause already-completed implementation to be treated as launchable work, undermining the no-replay recovery invariant.
- Defect class / likely siblings: status/result cross-field invariants absent from Board validation; planned+result and blocked+result are neighboring contradictory states.
- Existing tests that failed to catch it: durable-result recovery is tested only with an in_progress Card; READY tests contain no result.
- Reproduction artifact, if any: repros/repro_router_semantics.py (F3).

### F4 — Result and terminal-review evidence may be nonexistent or unrelated while reconciliation/finalization proceeds

- Affected workflow contract/invariant: EXECUTION requires accepted semantic results to carry durable evidence and verified tests/readback; REVIEW requires terminal attempts to retain durable verdict evidence.
- Expected behavior: evidence locators used to justify an accepted result or GREEN/RED terminal review must be class/workstream-bound as appropriate and dereference to durable evidence before reconciliation/finalization.
- Actual behavior: parse_card_result validates only the syntax/prefix of Evidence refs and never reads them. validate_review requires terminal evidence_path to be a nonempty safe relative string but does not bind it to the workstream evidence directory or verify that it exists. The router therefore accepts a result whose evidence file is absent, and can finalize a GREEN attempt whose evidence_path is absent or unrelated.
- Minimal reproduction: (a) active Card with Review requirement: none, valid result text, but a nonexistent workstream evidence ref -> route/result_reconciliation; (b) REQUIRED review with valid result and GREEN attempt whose evidence_path names a nonexistent file -> route/post_review_finalization.
- Why this is materially load-bearing: the durable evidence chain can be fabricated by path strings while the workflow proceeds as though implementation and independent verdict evidence were preserved.
- Defect class / likely siblings: locator syntax accepted without object existence/class validation; Plan Review terminal evidence_path uses the same pattern.
- Existing tests that failed to catch it: execution_contract tests parse evidence paths without creating those evidence files; state tests check terminal evidence_path is nonempty, not that it exists or belongs to the expected evidence class.
- Reproduction artifact, if any: repros/repro_router_semantics.py (F4).

### F5 — Task-Board Research can return execution to a nonexistent or wrong Card

- Affected workflow contract/invariant: RESEARCH says the exact record owns one exact return target and never selects a different target by itself; RECOVERY gives implementation Research precedence but must return to the exact durable owner.
- Expected behavior: Board-owned implementation Research must be bound to the actual originating/current Card and exact owner role; a stale or fabricated return Card must fail closed.
- Actual behavior: validate_research treats any string beginning execution:, execution_prep: or execution_resolution: as a valid execution return target. The Board router checks origin_role but never verifies that origin_subject/return-target Card identity exists in the Board or matches the originating Card. It then routes using the arbitrary suffix as subject.
- Minimal reproduction: keep active Card M01-T04, point Board research_obligation at a complete Research record with origin_subject M01-T04 but return_target = execution:M99-T99. The selector returns route/execution with subject M99-T99 even though that Card does not exist.
- Why this is materially load-bearing: a stale or malformed Research record can redirect deterministic continuation across Card authority boundaries instead of failing closed.
- Defect class / likely siblings: free-form role:subject strings without owner-object referential integrity; empty execution: suffix is also accepted by the validator.
- Existing tests that failed to catch it: Task-Board Research tests use matching origin_subject and return_target for M01-T04 only.
- Reproduction artifact, if any: repros/repro_router_semantics.py (F5).

### F6 — Backslash traversal bypasses workstream-local locator checks on Windows

- Affected workflow contract/invariant: path traversal is forbidden; every locator must be exact, class-checked and workstream-bound across supported runtimes.
- Expected behavior: path validation must reject traversal using any separator semantics that the host filesystem will interpret, so a sample-workstream Task Card cannot resolve into another workstream.
- Actual behavior: _safe_relative_path and Reads first tokenize with PurePosixPath and raw-string prefix checks, but Reads later constructs a host-native Path. A component such as ..\..\other contains no POSIX '..' part and the raw path still starts with the required sample-workstream prefix. On Windows, host path normalization interprets the backslashes and resolves into implementation\workstreams\other\....
- Minimal reproduction: validate a task_card locator with path implementation/workstreams/sample-workstream/cards/..\..\other/cards/M01-T99.md. The production string/Posix checks accept its shape. Python ntpath normalization of that exact raw path under C:\repo yields C:\repo\implementation\workstreams\other\cards\M01-T99.md.
- Why this is materially load-bearing: on Windows a supposedly workstream-bound locator can read another workstream's Card while still passing the intended cross-workstream/path-traversal checks.
- Defect class / likely siblings: mixed POSIX validation with host-native filesystem interpretation; applies to other prefix-bound locators and authority/technical-contract reads.
- Existing tests that failed to catch it: locator tests cover forward-slash ../ escape and explicit other-workstream paths, not backslash traversal.
- Reproduction artifact, if any: repros/repro_windows_locator.py (F6).

## Non-blocking observations

No additional advisory/style items are promoted. The audit intentionally kept speculative redesign ideas out of the material set.

## Coverage

Inspected the exact subject's workflow router/state/execution-prep/execution/recovery/review/research/planning/plan-review/close/workstream contracts; production router, state, execution, recovery, review and close helpers; router/state/execution/review/close tests; templates/schema inventory; test runner/workflow configuration.

Selected lens coverage:
- path traversal / locator safety / cross-workstream binding: F5, F6 and locator validation review;
- malformed or contradictory state / fail-closed behavior: F2, F3, F4, F5;
- router precedence / unreachable branches / conflicting obligations: F2, F3, F5;
- review independence / review bypass / result mutation: F1, F2, F4.

Negative-space testing focused on interactions the existing suite does not combine: unchanged declared identity with changed bytes, terminal status with mandatory review, READY plus a durable result, absent evidence objects, mismatched Research return owners, and Windows separator semantics. GitHub Actions check runs visible for the exact subject_commit report success, confirming the repository's ordinary suite did not reject these states.

No audit/* branch/report, GitHub Issue/PR defect discussion, or historical workstream evidence/review narrative was consulted before freezing the finding set. No post-freeze historical comparison was performed.

## Confidence and limitations

Confidence is high for F1-F5 because each follows directly through the production validator/router branches and preserved minimal fixture mutations. F6 is high for the validator/path-normalization mismatch and platform-conditional in impact; direct Python normalization confirmed the same raw path that lacks a PurePosix '..' part normalizes across workstreams under Windows path semantics.

A detached local execution of the full exact commit could not be completed in this session: direct container Git fetch lacked network name resolution and the connected remote-command service had exhausted its current usage allowance. I did not retry that unavailable service. The exact-subject GitHub Actions test check is green, and the non-mutating repro scripts are persisted for execution in any checkout pinned to the subject commit.
