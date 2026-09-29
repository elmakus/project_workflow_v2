# Issue #28 — execution Research return owner precedence plan P1

## 1. Subject and authority

Workstream `issue-execution-research-return-shadow`, cycle `1`, entry Definition `D1`, revision `P1`. Premium A is satisfied for D1.

Accepted authority: `requirements/ISSUE_28_EXECUTION_RESEARCH_RETURN_PRECEDENCE.md` I28-R1–R9 and `decisions/ISSUE_28_EXECUTION_RESEARCH_RETURN_PRECEDENCE.md` I28-D1–D7, sourced from promoted `execution-research-return-owner-precedence@1`.

This plan is only for repair subject `repair:execution-research-return-owner-precedence:v1`. It does not integrate other stabilization constituents, mutate `main`, close Issue #28, or transfer acceptance from #23/#32/#33/#36.

## 2. Baseline and exact defect

Baseline is `main@d3ab917f02e4de91b7dbb17915c2287c2387333e` plus this workstream's authority-only commits.

Fresh executable diagnosis proves:
- a schema-valid completed execution-owned Research record co-bound by manifest `[research]` and Task Board `[research_obligation]` returns generic Recovery from the early manifest branch;
- the failure reason contains the valid target `execution_resolution:M01-T04` because the early owner map contains only Intake/Brainstorming/Definition;
- the existing Task-Board-only execution Research positive control passes and already maps execution-resolution/prep/execution prefixes correctly.

The defect is semantic divergence between two legal locators for one Research record, not schema invalidity.

## 3. Production strategy

Implement one small production return-target classifier/resolver adjacent to the router selector. It accepts a validated Research `return_target` and returns the canonical obligation, exact subject, and owner module for:
- `execution_resolution:<subject>` -> `execution_resolution`, subject suffix, `workflow/RECOVERY.md`;
- `execution_prep:<subject>` -> `execution_prep`, subject suffix, `workflow/EXECUTION_PREP.md`;
- `execution:<subject>` -> `execution`, subject suffix, `workflow/EXECUTION.md`.

Pre-execution exact targets `intake`, `brainstorming`, and `definition` retain their current direct mapping.

For manifest-level Research:
- active remains `research`;
- complete pre-execution returns remain unchanged;
- complete execution-owned returns use the shared classifier and route to the same owner semantics as the Task Board path;
- consumed Research remains historical and does not replay from the manifest path.

For Task-Board Research:
- preserve the current active, complete, and consumed/cleanup behaviors;
- replace duplicated prefix parsing only if doing so reduces semantic divergence without broadening scope;
- consumed/applied with a stale Board pointer still routes only to existing `research_cleanup`.

No new durable state, owner registry, generic phase DAG, second Research record, or lifecycle is introduced.

## 4. Single implementation Card

After B/independent Plan Review/C, Execution Prep materializes one Card:

**M01-T01 — Unify execution Research return-owner resolution across manifest and Task Board paths**

Included:
- production router owner-resolution logic;
- all three execution return prefixes;
- dual-locator complete/pending and complete/applied cases;
- consumed/applied cleanup preservation;
- positive pre-execution Research controls;
- focused router tests and cumulative qualification.

Excluded:
- Research schema/lifecycle redesign;
- Task Board redesign;
- Execution/Recovery policy changes;
- #23/#26/#27/#29/#31/#40 scopes;
- integration, tracker closure, deployment.

Review requirement: REQUIRED independent review. Technical contract: none.

## 5. Acceptance and tests

Extend `tests/test_router.py` through production `select_route`.

Required negative/positive matrix:
1. co-bound manifest + Board execution-resolution, complete/pending -> exact `execution_resolution`, no generic Recovery;
2. co-bound execution-prep and execution equivalents -> exact owners and exact subject suffix;
3. complete/applied returns to the same exact owner without Research replay;
4. consumed/applied with Board pointer -> existing `research_cleanup`, not execution replay;
5. Task-Board-only execution Research controls remain GREEN;
6. manifest-only Intake/Brainstorming/Definition complete returns remain unchanged;
7. active Research remains `research`;
8. unsupported/malformed targets retain existing fail-closed validation;
9. dual locator does not produce duplicate return/cleanup behavior.

Run at least:
- `python3 -m unittest tests.test_router tests.test_state_contract`;
- `python3 -m unittest tests.test_continuation_contract tests.test_user_stop_contract`;
- `python3 -m unittest discover -s tests -v`;
- `git diff --check`.

Commit implementation bytes first, then run focused and full tests from a clean detached exact implementation commit. Result evidence records exact commit/blob identity and readback.

## 6. Review and completion

Main/coordinator records one semantic Result for M01-T01. Freeze R01 against the exact immutable Result and stable Card acceptance. A context that implemented or repaired the subject cannot verdict R01.

GREEN permits deterministic Card finalization and branch-local Close. RED preserves failed-attempt evidence and routes correction under existing workflow rules.

Branch-scope Close must explicitly distinguish a completed #28 constituent from later stabilization composition/integration. No merge to `main` or Issue closure occurs in this Card.

## 7. Coverage

- R1–R3 / D1–D4: shared exact execution owner semantics, dual-locator safety, once-only reconciliation and cleanup.
- R4 / D5: unchanged pre-execution and active Research behavior.
- R5–R6: full prefix/state matrix, regression and cumulative production tests.
- R7 / D6: minimal router repair, no generic architecture.
- R8: exact Result plus independent review.
- R9 / D7: dedicated constituent and integration isolation.

## 8. Planner challenge audit

GREEN for P1.

Rejected alternatives:
- deleting the manifest Research locator when a Board pointer exists — it mutates ownership rather than fixing semantic composition;
- teaching only the early branch about one `execution_resolution` string — incomplete for the schema-valid execution-prep/execution targets and preserves duplicate semantics;
- moving all manifest Research handling below Task Board routing — broader precedence change with unnecessary risk to Intake/Brainstorming/Definition Research;
- adding a generic routing registry/phase graph — unnecessary for this bounded defect;
- treating current generic Recovery as safe fail-closed behavior — it rejects a valid canonical return and loses the exact owner route.

No unresolved product or technical strategy choice remains. Freeze this P1 as the immutable Premium B subject. The planning context must not perform its own Stage-6 Plan Review.
