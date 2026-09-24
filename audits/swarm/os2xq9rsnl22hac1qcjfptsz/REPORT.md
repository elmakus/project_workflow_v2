# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — READY dependency content can drift behind an unchanged exact locator

- Affected workflow contract/invariant: workflow/STATE.md and workflow/EXECUTION_PREP.md require READY launch refresh to bind predecessor dependencies to exact path + commit + blob identity and to fail closed on missing/stale or same-path-changed dependency inputs.
- Expected behavior: if the current result file at a dependency path no longer has the content identified by the Card's recorded commit/blob, launch refresh must reject the Card and route Recovery.
- Actual behavior: tools/router.py:refresh_ready_card compares only the Task Card's path/commit/blob tuple to the tuple copied from TASK_BOARD.toml, then reads the current path without hashing it or verifying that the declared commit contains that blob at that path. If the file content changes while both metadata copies remain unchanged, the selector still routes execution_prep.
- Minimal reproduction: create DONE predecessor result path P with metadata commit=A/blob=B; make READY Card depend on P@A:B; confirm launch is ready; change only the bytes at P while leaving both Task Card dependency and Board result locator at A:B. The vulnerable selector still accepts launch.
- Why this is materially load-bearing: the immutable dependency identity is the safety boundary that prevents executing against a result different from the one the Card was prepared against.
- Defect class / likely siblings: declared immutable Git identity is compared to another declaration rather than verified against current durable content. Similar declared commit/blob fields deserve audit wherever runtime behavior trusts them without object/path verification.
- Existing tests that failed to catch it: tests/test_router.py::test_ready_card_stale_dependency_fails_closed_before_launch changes Board commit/blob metadata together with file content; it does not exercise content-only drift behind unchanged metadata.
- Reproduction artifact, if any: audits/swarm/os2xq9rsnl22hac1qcjfptsz/repros/repro_router_semantic_gaps.py::repro_dependency_content_drift

### F2 — GREEN implementation review survives mutation of its Task Card acceptance surface

- Affected workflow contract/invariant: workflow/REVIEW.md and workflow/STATE.md require review to bind the exact immutable implementation subject to its exact acceptance surface; GREEN permits finalization only for the exact current subject and acceptance.
- Expected behavior: materially changing Included scope, Acceptance, Required tests/readback, authority refs, or review requirement after GREEN must invalidate that review coverage or fail closed.
- Actual behavior: review acceptance stores only a Task Card path. validate_review_history checks that path/Card ID, while the active-Card router compares only the review's implementation subject to the current result subject. It reparses the current Task Card but never compares its content identity to the reviewed acceptance. The same path can therefore contain changed acceptance while the old GREEN still routes post_review_finalization.
- Minimal reproduction: create an in_progress Card requiring review, durable result, and GREEN attempt for the result; then edit only the Task Card's Acceptance text at the same path. The result subject remains unchanged and the selector still routes post_review_finalization.
- Why this is materially load-bearing: review can authorize finalization against criteria that are no longer the criteria governing the Card.
- Defect class / likely siblings: mutable path used as an exact acceptance identity. Any review gate whose acceptance is path-only is susceptible to same-path mutation.
- Existing tests that failed to catch it: tests/test_state_contract.py::test_task_card_review_acceptance_is_exact_and_semantic checks only class/path/Card ID; tests/test_router.py::test_changed_result_after_terminal_review_requires_new_attempt mutates the result blob, not the Task Card acceptance.
- Reproduction artifact, if any: audits/swarm/os2xq9rsnl22hac1qcjfptsz/repros/repro_router_semantic_gaps.py::repro_green_review_acceptance_mutation

### F3 — Unrelated Research can preempt the mandatory Intake diagnosis prior-art binding

- Affected workflow contract/invariant: workflow/INTAKE.md, workflow/RESEARCH.md, workflow/STATE.md and router precedence require concrete issue diagnosis Research to be consumed and its exact subject/result binding persisted by Intake before the single current Research slot may be reused.
- Expected behavior: an issue Intake with a current repair_subject but no exact diagnosis_prior_art_subject/result must own the next obligation, or contradictory premature reuse of Research must fail closed.
- Actual behavior: tools/router.py loads and dispatches workstream.research before it loads Intake. A syntactically valid unrelated active Research record, for example origin_role=brainstorming, is routed immediately even when the co-bound issue Intake lacks its mandatory diagnosis prior-art binding. Per-record validators do not reject that cross-record contradiction.
- Minimal reproduction: co-bind issue INTAKE.toml with repair_subject=repair:v2 and empty diagnosis prior-art binding, plus active RESEARCH.toml for brainstorming/later-fact. The selector returns route/research for the unrelated subject instead of Intake/Recovery.
- Why this is materially load-bearing: the mandatory prior-art gate for issue repair can be hidden by illegal premature reuse of the singleton Research slot, defeating a user-repair safety boundary.
- Defect class / likely siblings: precedence plus per-record validation accepts a globally contradictory combination because the higher-level prerequisite is checked only after an earlier-returning record.
- Existing tests that failed to catch it: tests/test_router.py::test_issue_diagnosis_requires_exact_consumed_prior_art_research covers absent, stale Intake-origin, exact consumed, and persisted-binding cases; test_later_brainstorming_research_does_not_erase_issue_diagnosis_prior_art reuses Research only after the binding is already persisted. No test reuses the slot before that persistence.
- Reproduction artifact, if any: audits/swarm/os2xq9rsnl22hac1qcjfptsz/repros/repro_router_semantic_gaps.py::repro_premature_research_slot_reuse

### F4 — Plan Review accepts an unrelated authority path as the plan acceptance surface

- Affected workflow contract/invariant: workflow/PLAN_REVIEW.md says each attempt owns the exact acceptance authority and judges the frozen plan against accepted Definition/requirements/decisions plus the planning acceptance surface.
- Expected behavior: PLAN_REVIEW.toml acceptance must be bound to the current accepted Definition/requirements/decisions for that workstream/cycle, not merely any path in a broad authority root.
- Actual behavior: validate_plan_review receives only planning, not Definition or its authority set. Its underlying validate_review accepts any syntactically safe authority locator under requirements/, decisions/, planning/, or workflow/. A GREEN review of the exact plan subject with acceptance=workflow/ROUTER.md passes validation even though that path is not the accepted product Definition surface.
- Minimal reproduction: validate a frozen planning record with a GREEN plan review whose subject exactly matches the plan but whose acceptance locator is {class="authority", path="workflow/ROUTER.md"}. Production validate_plan_review accepts it.
- Why this is materially load-bearing: premium B/Plan Review can be recorded GREEN without proving review against the authority it is supposed to cover, and Planning can then consume that GREEN toward C/Execution Prep.
- Defect class / likely siblings: exact subject binding without exact acceptance-authority binding.
- Existing tests that failed to catch it: tests/test_state_contract.py plan-review tests check plan subject/revision/cycle/evidence and always use a generic requirements/REQUIREMENTS.md locator; there is no negative test for an unrelated but syntactically allowed authority path.
- Reproduction artifact, if any: audits/swarm/os2xq9rsnl22hac1qcjfptsz/repros/repro_plan_review_acceptance.py

### F5 — Semantically failed or unverifiable Card Results are accepted as durable recovery truth

- Affected workflow contract/invariant: workflow/EXECUTION.md and workflow/STATE.md say Main reconciles an accepted implementation result containing semantic implementation subject, evidence, and verified tests/readback; durable valid result prevents replay.
- Expected behavior: the result-validity gate must reject malformed/non-immutable implementation subject, missing evidence, or an explicitly failed tests/readback summary before routing result reconciliation/review.
- Actual behavior: tools/execution_contract.py::parse_card_result requires only non-empty strings, Card ID equality, and evidence path shape. It does not validate implementation subject identity, read evidence files, or require a successful tests/readback semantic. The exact target blob was executed locally and accepted Implementation subject: banana, a nonexistent evidence path, and Tests/readback summary: FAILED: acceptance test failed.
- Minimal reproduction: parse or route a Card Result with those three values. parse_card_result returns a normal parsed result; with review_requirement=none the router treats it as a valid semantic result and routes result_reconciliation.
- Why this is materially load-bearing: corrupted or explicitly failed output can become no-replay recovery truth and advance workflow state rather than correction/recovery.
- Defect class / likely siblings: shape validation is being used as semantic acceptance validation.
- Existing tests that failed to catch it: tests/test_execution_contract.py tests runtime-identity fields and cross-workstream evidence path shape, but not malformed implementation subjects, absent evidence objects, or negative/failed test summaries.
- Reproduction artifact, if any: audits/swarm/os2xq9rsnl22hac1qcjfptsz/repros/repro_router_semantic_gaps.py::repro_invalid_result_is_treated_as_valid; direct parser counterexample was also executed during this audit.

### F6 — A satisfied JIT trigger is dropped behind the all-DONE route to Close

- Affected workflow contract/invariant: workflow/EXECUTION_PREP.md makes a satisfied predecessor-dependent JIT trigger an obligation to materialize/refine the downstream Card; workflow/CLOSE.md forbids treating terminal current Cards as end of approved scope when another authorized obligation remains.
- Expected behavior: when all materialized Cards are DONE but a JIT trigger is satisfied and unconsumed, Execution Prep must consume/materialize that obligation before Close can become the next owner.
- Actual behavior: validate_board accepts state=satisfied when its predecessor is DONE with a result, but tools/router.py ignores jit_triggers during dispatch. After active/blocked/ready checks it sees all current Cards DONE and returns route/close.
- Minimal reproduction: one DONE Card with result plus [[jit_triggers]] after_card=<that Card>, state=satisfied, valid condition. The board validates and the selector routes close rather than execution_prep.
- Why this is materially load-bearing: accepted downstream work can disappear from deterministic execution merely because it has not yet been materialized as a Card.
- Defect class / likely siblings: terminality computed from materialized Cards only, excluding durable non-Card obligations.
- Existing tests that failed to catch it: state-contract tests validate JIT lifecycle separately; tests/test_router.py::test_all_terminal_cards_route_to_close_not_directly_to_stop uses an all-DONE Board with no JIT trigger.
- Reproduction artifact, if any: audits/swarm/os2xq9rsnl22hac1qcjfptsz/repros/repro_router_semantic_gaps.py::repro_satisfied_jit_routes_close

### F7 — DONE status bypasses REQUIRED review, including pending review

- Affected workflow contract/invariant: workflow/REVIEW.md, workflow/STATE.md, and PWV2-REQ-036 require REQUIRED/activated RECOMMENDED review to block terminal Card completion until GREEN; contradictory state must fail closed.
- Expected behavior: a Card marked DONE whose Task Card requires review but has no exact GREEN current attempt must be rejected/recovered, not treated as terminal.
- Actual behavior: validate_board requires a result for DONE but does not load the Task Card or validate review state. Review enforcement in tools/router.py runs only inside the in_progress branch. A DONE Card with review_requirement=required and a pending attempt bypasses all review checks and, if all Cards are DONE, routes Close.
- Minimal reproduction: create valid required-review Card + result + pending review attempt, then set Board status to done. Board validation succeeds; selector routes close without reading or enforcing the pending review.
- Why this is materially load-bearing: a single mutable status field can bypass a mandatory independent safety gate and move the workstream toward final integration.
- Defect class / likely siblings: lifecycle terminal state is trusted without revalidating the prerequisite gate that makes terminality legal.
- Existing tests that failed to catch it: tests/test_router.py::test_required_review_blocks_until_green_then_routes_finalization keeps the Card in_progress; test_all_terminal_cards_route_to_close_not_directly_to_stop uses review_requirement=none.
- Reproduction artifact, if any: audits/swarm/os2xq9rsnl22hac1qcjfptsz/repros/repro_router_semantic_gaps.py::repro_done_bypasses_pending_required_review

## Non-blocking observations

The immutable Git identifiers used by several validators are frequently checked syntactically or against another durable declaration rather than dereferenced to Git objects. F1 is the concrete demonstrated consequence in READY launch refresh; broader object-existence/path-at-commit verification was not promoted to a separate finding without another independently demonstrated route defect.

TRACKER.toml repository binding is syntactic owner/name validation and is not cross-checked here against PROJECT.md.repository. This may be intentional support for tracker placement and is therefore not classified as a material defect in this audit.

## Coverage

The audit remained bound to subject commit 4fb4bfb7d7b1481d6f347c182fc96a5a1135e045. Before detailed inspection the selected attack lenses were frozen as: malformed/contradictory state fail-closed behavior; stale identity; helper/documented parity and negative space; Research/Intake/tracker/external-effect recovery.

Inspected canonical contracts included workflow/ROUTER.md, STATE.md, INTAKE.md, RESEARCH.md, EXECUTION_PREP.md, EXECUTION.md, REVIEW.md, PLANNING.md, PLAN_REVIEW.md, RECOVERY.md, CLOSE.md, BRAINSTORMING.md, DEFINITION.md, USER_STOP.md, and the approved requirement surface. Executable surfaces inspected included tools/router.py, state_contract.py, execution_contract.py, recovery_contract.py, close_contract.py plus relevant templates and tests.

Adversarial cases exercised the READY dependency launch boundary, issue Intake/Research cross-record precedence, semantic result recovery, required review finalization, all-DONE/JIT routing, and Plan Review acceptance binding. Existing negative-space tests were inspected specifically to distinguish covered stale-metadata cases from uncovered content-only and cross-record contradictions.

## Confidence and limitations

Confidence is high in the seven source-level counterexamples because each follows a deterministic production branch with validator-accepted inputs. F5 was additionally executed locally from the exact execution_contract.py blob at the target commit and reproduced acceptance of malformed/failed data.

A full immutable checkout could not be executed in the local runtime: outbound Git network resolution is disabled, and the connected remote command environment was unavailable due its usage quota. The preserved repro scripts are designed to run directly from the audit branch and invoke the repository's real production selector/validators and existing fixture builders; they were not used to modify product code.

The finding set was frozen before any historical material surfaced. No GitHub Issues/PR comments, audit/* branches, or other swarm reports were inspected, and no post-freeze historical classification was used to change the finding set.
