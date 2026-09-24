# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Planning can approve a foreign or nonexistent frozen plan subject

- Affected workflow contract/invariant: Planning must freeze one exact immutable Git-blob plan subject, Plan Review must judge that exact subject, stale/wrong-project bindings must fail closed, and only the reviewed plan may reach premium C / Execution Prep.
- Expected behavior: the frozen planning subject must resolve to the selected project's repository and to the actual `plan_path` content at the declared commit/blob. A missing plan artifact or a subject whose repository differs from `PROJECT.md.repository` must route Recovery before B/review/C can be consumed.
- Actual behavior: `validate_planning()` validates only syntactic repository/path/40-hex fields and `subject.path == plan_path`; it receives no project repository and never resolves the Git object. `validate_plan_review()` only compares the review subject to the planning record. The router then trusts that internally consistent key. The repository's own router tests hard-code planning/review subjects as `owner/repo` while the fixture PROJECT declares `owner/router-fixture`, and they do not create `planning/MASTER_PLAN.md`; successful planning routes are still asserted.
- Minimal reproduction: copy `tests/fixtures/router/valid-project`; install the existing GREEN Definition fixture; install an approved planning record with A/B/C satisfied and subject `owner/repo@aaaaaaaa...:planning/MASTER_PLAN.md@bbbbbbbb...`; install a matching GREEN `PLAN_REVIEW.toml`; remove the Task Board locator so the next route is visible. Do not create `planning/MASTER_PLAN.md`. `select_route(...)` routes to `execution_prep` instead of Recovery even though PROJECT.repository is `owner/router-fixture` and the plan file is absent.
- Why this is materially load-bearing: Stage-6 review and premium gates can authorize execution from an artifact that is neither the selected project's plan nor even present. That defeats exact-subject review authority rather than merely weakening diagnostics.
- Defect class / likely siblings: unverified Git-subject locators; any gate that only compares self-declared repository/commit/path/blob tuples without resolving the object is suspect.
- Existing tests that failed to catch it: planning helpers in `tests/test_router.py` normalize the mismatch by generating `owner/repo` subjects against an `owner/router-fixture` project and by never materializing the plan file; planning-route tests still expect success.
- Reproduction artifact, if any: `repros/f1_foreign_nonexistent_plan.py`

### F2 — Post-review result mutation is invisible when locator metadata is left unchanged

- Affected workflow contract/invariant: result locators and review attempts bind an immutable Git subject; GREEN may finalize only the exact still-current result; READY dependencies must match immutable predecessor result identity.
- Expected behavior: before result reconciliation/review finalization and before READY dependency launch, the declared commit/blob identity must be verified against the actual referenced object/content. Changing the result file after review must make the subject stale and require Recovery/new review.
- Actual behavior: `validate_locator(..., "result")` only checks that supplied commit/blob strings look like 40-hex. `refresh_ready_card()` compares dependency tuples copied from state and merely reads the path; it never checks the file's blob. Active-result routing parses current text but `exact_result_subject()` is built from the unchanged Task Board metadata. Therefore a syntactically valid result file can be materially changed after a GREEN review while board/result and review metadata retain the old tuple; the router still sees subject equality and returns `post_review_finalization`.
- Minimal reproduction: use the router fixture, install a REQUIRED reviewable result and GREEN attempt using the existing test helpers, then modify only `results/M01-T04.md` (for example change the implementation subject) while leaving the board `commit/blob` and review subject unchanged. `select_route(...)` still returns `route/post_review_finalization`.
- Why this is materially load-bearing: reviewed content can be replaced without invalidating GREEN. The same metadata-only comparison also lets a READY dependency file drift while its declared predecessor tuple remains unchanged.
- Defect class / likely siblings: claimed immutable identity is compared but never resolved/hashed. Planning subjects, result subjects, review subjects and dependency results should be audited for the same failure mode.
- Existing tests that failed to catch it: `test_changed_result_after_terminal_review_requires_new_attempt` changes the Task Board's declared blob, not the referenced file with metadata held constant. The result fixtures already use synthetic blob strings unrelated to file contents, so the suite does not prove object identity.
- Reproduction artifact, if any: `repros/f2_post_review_result_mutation.py`

### F3 — Research origin and return ownership can contradict each other and route to another Card/owner

- Affected workflow contract/invariant: Research owns one exact origin subject and one exact return owner; it never selects a different target by itself. Recovery must return completed implementation Research to the exact originating obligation.
- Expected behavior: role/subject and return target must be cross-validated. Examples: `origin_role = intake` must return to `intake`; `origin_role = execution_resolution`, `origin_subject = M01-T04` must return to `execution_resolution:M01-T04`. Contradictory bindings must fail closed.
- Actual behavior: `validate_research()` validates `origin_role`, `origin_subject`, and `return_target` independently. The Task Board router checks only that the role is one of the execution roles and then trusts the target suffix. A complete record with origin `execution_resolution/M01-T04` and return target `execution_resolution:M99` validates and routes `execution_resolution` with subject `M99`. Likewise a top-level intake-origin Research record may name a different pre-execution return owner.
- Minimal reproduction: attach a Task-Board `research_obligation` for the sample workstream, set state complete, origin_role `execution_resolution`, origin_subject `M01-T04`, return_target `execution_resolution:M99`, with otherwise valid source accounting. `select_route(...)` routes to `execution_resolution` for `M99` instead of Recovery.
- Why this is materially load-bearing: stale or contradictory Research can redirect the deterministic recovery path away from the Card/owner that requested the facts, bypassing exact return ownership and potentially mutating the wrong durable state.
- Defect class / likely siblings: missing cross-field owner/subject invariants between origin and return references.
- Existing tests that failed to catch it: Research validator/router tests exercise only matching origin/return pairs and do not include cross-owner or cross-Card mismatches.
- Reproduction artifact, if any: `repros/f3_research_return_mismatch.py`

### F4 — Close can certify source-ref-independent recovery with an empty recovery package

- Affected workflow contract/invariant: before final merge/cleanup, target-side recovery must contain the mandatory durable recovery package (workstream identity/provenance, selected board, stable Card contracts, required result/review/evidence and relevant checkpoint/handoff refs); source-branch deletion is allowed only after recovery is independent of that ref.
- Expected behavior: the Close verifier itself must reject a recovery claim that omits mandatory core artifact classes. An empty or caller-underdeclared required set cannot prove package completeness.
- Actual behavior: `verify_target_side_recovery()` checks only `required_artifacts - present_artifacts`, where both sets are entirely caller-supplied. With both empty, matching non-empty head labels and `immutable_merge_evidence=True`, it returns `source_ref_independent_recovery`. Feeding that conclusion into `cleanup_branch_action(... cleanup_state="safe_to_delete" ...)` permits `delete_exact_ref`.
- Minimal reproduction: call `verify_target_side_recovery(source_branch="feat/x", source_head="h", merged_source_head="h", target_package_subject_head="h", immutable_merge_evidence=True, required_artifacts=frozenset(), present_artifacts=frozenset())`; it returns success. Then call `cleanup_branch_action(terminal_package_independent=True, source_ref_exists=True, current_head="h", cleanup_state="safe_to_delete", verified_head="h")`; it returns `delete_exact_ref`.
- Why this is materially load-bearing: Close can authorize destructive source-ref cleanup without proving that any of the recovery artifacts mandated by the canonical Close contract are present, risking unrecoverable terminal state.
- Defect class / likely siblings: completeness delegated to unvalidated caller assertions instead of encoded mandatory invariants.
- Existing tests that failed to catch it: Close tests use caller-supplied non-empty sets and test subtraction/missing members, but never the empty/underdeclared mandatory-set case.
- Reproduction artifact, if any: `repros/f4_empty_close_recovery_package.py`

## Non-blocking observations

None frozen. Items that were merely style choices, documentation wording, or speculative redesigns were not promoted to findings.

## Coverage

The audit remained bound to commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`. Before freezing findings, inspection was limited to permitted canonical/product surfaces: `workflow/ROUTER.md`, `AUTHORITY.md`, `STATE.md`, `PLANNING.md`, `PLAN_REVIEW.md`, `EXECUTION_PREP.md`, `EXECUTION.md`, `REVIEW.md`, `RECOVERY.md`, `RESEARCH.md`, `INTAKE.md`, `GITHUB_ISSUES.md`, `CLOSE.md`; production helpers `tools/router.py`, `state_contract.py`, `execution_contract.py`, `recovery_contract.py`, `close_contract.py`; relevant templates; router/state/close tests and fixtures; and CI test entry configuration.

Selected lens 3 was exercised against planning/result/review/dependency Git identity. Lens 8 was exercised against Close continuation, external-effect handling, target-side recovery and cleanup. Lens 5 was exercised against durable results, RED/review subject refresh, blocker precedence and implementation Research return. Lens 9 was exercised against Intake prior-art handling, Research return ownership, tracker recovery and external-effect recovery.

No `audit/*` branch, swarm report, GitHub Issue/PR defect discussion, or historical workstream evidence/review narrative was inspected before findings were frozen. No post-freeze historical comparison was performed.

## Confidence and limitations

Confidence is high for the four reported semantic paths because each follows directly from the exact production validators/selectors/helpers and is corroborated by the shape of existing tests. The current execution environment could read/write GitHub but did not provide a usable local checkout: the local container had no GitHub network access and the connected remote command service had exhausted its command quota. Therefore the preserved repro scripts were not executed in this session. They are non-mutating and import the production modules/fixtures directly so they can be run from the audited commit/branch without modifying product code.
