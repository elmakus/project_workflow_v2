# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Immutable Git identities are trusted as strings instead of verified content identities

- Affected workflow contract/invariant: workflow/STATE.md and workflow/EXECUTION_PREP.md require READY launch refresh to verify exact dependency result path + immutable commit/blob identity and explicitly require missing, stale, or same-path-changed dependency input to fail closed. Review/recovery semantics likewise require exact immutable result subjects.
- Expected behavior: Before a dependency, Card result, or frozen plan subject is trusted as the exact immutable object named by its durable locator, the implementation must verify that the bytes being consumed are actually the bytes identified by the recorded Git commit/blob.
- Actual behavior: tools/router.py refresh_ready_card() compares only the dependency's declared (path, commit, blob) tuple with the DONE predecessor's declared tuple and then reads the current path without resolving or hashing it. Active-Card result routing similarly parses the current file and constructs its review subject from the Board's declared metadata; tools/recovery_contract.py exact_result_subject() only formats those strings. Planning validation checks only that commit/blob fields are 40-hex. If both durable references retain the same stale metadata while the file bytes at the path change, the stale/tampered content remains accepted.
- Minimal reproduction: Start from the router fixture, add DONE M01-T03 with result metadata path=P, commit=A, blob=B, and make READY M01-T04 depend on exactly P@A:B. The route is execution_prep. Modify only the bytes at P, leaving both the Task Board and Card dependency tuple unchanged. select_route() still returns route/execution_prep instead of Recovery. The preserved reproduction script includes this exact case.
- Why this is materially load-bearing: A READY Card can execute against dependency content that is no longer the immutable predecessor result it declared. The same trust pattern can allow a changed Card-result file or plan artifact to remain associated with old review/freeze metadata, defeating stale-subject detection.
- Defect class / likely siblings: Declared-identity versus observed-content confusion. Confirmed code siblings are READY dependency refresh, active Card result/review subject recovery, and frozen Planning subject validation.
- Existing tests that failed to catch it: tests/test_router.py::test_ready_card_stale_dependency_fails_closed_before_launch changes the Board's commit/blob metadata at the same time it changes the result file. It therefore proves only that mismatching declared tuples fail; its initial accepted state already uses synthetic commit/blob values that are not verified against the fixture file bytes.
- Reproduction artifact, if any: repros/repro_router_semantic_gaps.py (case stale_dependency_bytes).

### F2 — Active Research masks a durable explicit user stop

- Affected workflow contract/invariant: tools/router.py PRIORITY_FOUNDATION places explicit human/premium boundaries above research return; workflow/BRAINSTORMING.md states that an explicit user stop is a real stop; workflow/ROUTER.md states that real stops must stop deterministic continuation.
- Expected behavior: If the current Brainstorming revision carries explicit_user_stop=true, the router must surface that real stop before continuing agent-owned Research work.
- Actual behavior: select_route() loads and immediately routes a workstream-level active RESEARCH.toml before it loads BRAINSTORM.toml or checks explicit_user_stop. The state validators permit an active Brainstorming record with explicit_user_stop=true and a simultaneous active Research record returning to brainstorming, so this is a representable durable state rather than a malformed-state-only path.
- Minimal reproduction: Add an active BRAINSTORM.toml with explicit_user_stop=true, then add an active RESEARCH.toml with origin_role=brainstorming, return_target=brainstorming, pending reconciliation, and all four required source classes accounted for. select_route() returns route/research instead of stop/explicit_user_stop.
- Why this is materially load-bearing: The workflow can continue autonomous factual work after the durable state says the user explicitly stopped the work. That violates the highest-precedence human boundary rather than merely choosing a suboptimal internal phase.
- Defect class / likely siblings: Higher-precedence stop shadowed by an earlier owner-specific early return. The exact demonstrated defect is Brainstorming explicit stop versus active Research; other boundaries should be checked for the same ordering pattern before repair.
- Existing tests that failed to catch it: Router tests cover active/completed Research and Brainstorming/promotion behavior separately, but do not compose active Research with explicit_user_stop=true to test precedence.
- Reproduction artifact, if any: repros/repro_router_semantic_gaps.py (case research_masks_user_stop).

### F3 — Syntactically valid failed or unverified Card Results are treated as accepted completion evidence

- Affected workflow contract/invariant: workflow/EXECUTION.md says only an acceptance/evidence-valid return is reconciled as one durable accepted result; incomplete or incorrect returns remain in_progress for correction. workflow/RECOVERY.md says only a valid durable semantic result prevents replay and drives review/finalization.
- Expected behavior: A Card result that reports failed tests/readback or names missing/unverified evidence must not be treated as accepted semantic completion. It should remain/correct execution or fail closed until acceptance evidence is valid.
- Actual behavior: tools/execution_contract.py parse_card_result() verifies field presence, Card ID, path syntax for evidence refs, and absence of runtime-identity fields, but it accepts any non-empty tests/readback summary, including FAILED, and never reads the named evidence files. tools/router.py treats any result that passes this parser as valid; with Review requirement: none it immediately routes result_reconciliation, and with review required it proceeds to review-freeze/review instead of correcting the failed implementation.
- Minimal reproduction: Give active M01-T04 a Board result locator and a parseable Card Result whose Tests/readback summary is FAILED and whose Evidence refs points to a workstream-local Markdown file that does not exist. With Review requirement: none, select_route() still returns route/result_reconciliation.
- Why this is materially load-bearing: Failed tests or absent verification evidence can be promoted into durable completion truth, allowing implementation work to stop and downstream finalization/review to proceed despite the execution contract explicitly classifying such returns as unaccepted.
- Defect class / likely siblings: Semantic-validity collapse into syntax-validity. The same parser gate feeds no-review reconciliation and review-required paths.
- Existing tests that failed to catch it: Execution-contract tests exercise GREEN-looking summaries, forbidden runtime identity, and cross-workstream evidence syntax. Router result tests create the referenced evidence and use a GREEN summary. There is no negative test for a failed summary or a syntactically valid but missing evidence artifact.
- Reproduction artifact, if any: repros/repro_router_semantic_gaps.py (case failed_result_is_accepted).

### F4 — GREEN reviews are not bound to the actual current acceptance surface

- Affected workflow contract/invariant: workflow/REVIEW.md requires each implementation review attempt to bind one exact acceptance surface, normally the stable Task Card. workflow/PLAN_REVIEW.md requires the frozen plan to be judged against its accepted Definition/requirements/decisions and planning acceptance surface.
- Expected behavior: A GREEN implementation review must be bound to the exact current Card contract/acceptance being finalized, and a GREEN Plan Review must be bound to the actual accepted Definition authority for that plan. A wrong, stale, or nonexistent acceptance target must fail closed.
- Actual behavior: validate_plan_review() receives Planning but not Definition and validates [acceptance] only as any syntactically allowed authority path; the path is not compared with Definition.requirements/decisions and is not dereferenced. Implementation validate_review() accepts any workstream-local task-card path whose filename stem equals card_id; the router does not compare that acceptance locator with the active Card's current contract locator or immutable content identity. The router then trusts the GREEN verdict.
- Minimal reproduction: Build a frozen plan with premium B satisfied and a matching GREEN PLAN_REVIEW.toml, but change its acceptance path from the current requirements authority to requirements/NOT_CURRENT.md and do not create that file. Validation still succeeds and select_route() returns Planning to consume GREEN rather than Recovery.
- Why this is materially load-bearing: Independent review is a blocking safety gate. If a verdict can be issued against different or nonexistent acceptance criteria, GREEN can authorize plan approval or Card finalization without proving the thing the current workflow actually requires.
- Defect class / likely siblings: Reviewed-subject identity is exact, but reviewed-acceptance identity is only class/path-shaped. Confirmed siblings are Stage-6 Plan Review and implementation Card review.
- Existing tests that failed to catch it: Tests cover wrong subject blobs, independence, evidence presence, and task-card filename/card_id consistency, but not equality to the current authoritative acceptance surface nor existence/immutability of the acceptance artifact.
- Reproduction artifact, if any: repros/repro_router_semantic_gaps.py (case wrong_plan_review_acceptance).

### F5 — SessionStart accepts a semantically empty router if two sentinel strings survive

- Affected workflow contract/invariant: skills/project_workflow_v2/SKILL.md requires the installed root/router to fail closed when missing, malformed, ambiguous, or escaping the package root. hooks/session-start.py describes itself as a thin fail-closed bootstrap.
- Expected behavior: A truncated, stale, or otherwise malformed installed workflow/ROUTER.md must produce the blocking package-error context rather than be advertised as the canonical router.
- Actual behavior: canonical_router() verifies only that the file exists, resolves under the installed root, is readable, and contains two substrings: '# Project Workflow V2 Router' and 'Production selector: tools/router.py.' (with the selector in Markdown code formatting in the real constant). A file containing essentially only those two sentinels passes and build_context() tells the runtime that it is the canonical bundled router.
- Minimal reproduction: Copy the exact SessionStart hook into a temporary package root and replace workflow/ROUTER.md with only the required header and selector sentinel line. Run the hook with PLUGIN_ROOT set to that root. It emits normal 'Canonical bundled router' context rather than a BLOCKING error.
- Why this is materially load-bearing: The bootstrap establishes which installed file becomes workflow authority. Sentinel-preserving truncation, packaging drift, or arbitrary semantic replacement can therefore fail open and leave a runtime following incomplete/incorrect workflow policy while the bootstrap explicitly claims success.
- Defect class / likely siblings: Shallow sentinel validation used as semantic package-integrity validation.
- Existing tests that failed to catch it: tests/test_codex_delivery.py::test_missing_and_malformed_router_fail_closed tests a missing file and the string 'not a V2 router', which removes both sentinels. It does not test malformed/truncated content that preserves the two accepted sentinels.
- Reproduction artifact, if any: repros/repro_session_start_sentinel.py.

## Non-blocking observations

The inspected tracker and external-effect helpers were conservative in the exercised cases: ambiguous tracker discovery routes Recovery, create_pending_readback requires readback before retry, and Close's external-effect recovery oracle rejects uncertain occurrence and permits retry only after verified no-effect. No material finding was frozen in that sub-area.

A possible JIT-trigger/Close interaction and terminal review-attempt ordering were investigated during adversarial exploration but were not included in the frozen material finding set because the inspected contracts did not establish a sufficiently complete executable counterexample within this audit.

## Coverage

The audit remained bound to commit 4fb4bfb7d7b1481d6f347c182fc96a5a1135e045. The exact commit and recursive Git tree were read through GitHub's immutable commit/tree APIs. Before findings were frozen, no audit/* branch, other swarm report, GitHub Issue/PR comment, or historical implementation/workstreams/**/evidence/** or reviews/** material was used.

Inspected canonical modules included ROUTER, AUTHORITY, STATE, INTAKE, RESEARCH, BRAINSTORMING, PLANNING, PLAN_REVIEW, EXECUTION_PREP, EXECUTION, REVIEW, RECOVERY, GITHUB_ISSUES, CLOSE, WORKSTREAMS and USER_STOP. Executable/helpers inspected included router.py, state_contract.py, execution_contract.py, recovery_contract.py, review_contract.py and close_contract.py, together with their focused tests and relevant state/templates. Delivery/bootstrap coverage included the Codex plugin manifest, marketplace metadata, Skill, hook manifest, SessionStart hook, ChatGPT bootstrap prompts and delivery tests.

Selected lens 9 was exercised against Research/Intake precedence, tracker recovery and external-effect readback. Lens 10 was exercised against the plugin/Skill/SessionStart bootstrap and malformed-package behavior. Lens 1 was exercised against early-return precedence, especially explicit-stop versus Research. Lens 12 was exercised by comparing documented exact-identity/acceptance semantics with the production validators/selectors and by constructing negative-space cases omitted by tests.

The preserved reproduction scripts are non-mutating and are written to run against the repository checkout containing this audit. They target the production selector/validators and existing router fixture helpers; product code is not patched by the reproductions.

## Confidence and limitations

Confidence is high in the five control-flow/validation defects because each follows a direct deterministic production path and is contradicted by an explicit canonical invariant. Existing tests also expose the relevant negative space, especially the synthetic unverified blob metadata in the READY dependency fixture.

This environment could not execute a full checkout of the immutable commit: the connected Desktop Commander executor had exhausted its monthly call quota, while the isolated container had no GitHub DNS/network access. Therefore the preserved reproduction scripts were authored against the exact fetched source and fixtures but were not executed in this audit session. No product code was modified to compensate for that limitation.

The exact merge commit returned no associated combined-status entries or workflow runs through the available commit-status wrappers, so this audit does not claim CI verification for the audit subject itself.

## Post-freeze historical comparison

No systematic historical comparison was performed. After the finding set was explicitly frozen, an exact target-commit metadata fetch exposed merge-diff text that included historical implementation evidence from the merged commit. That material was not used to add, remove, re-rank, or reclassify any finding above.
