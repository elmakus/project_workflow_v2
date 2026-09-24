# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — DONE status bypasses required/RED review and routes Close

- Affected workflow contract/invariant: `workflow/STATE.md` and `workflow/REVIEW.md` require REQUIRED/activated RECOMMENDED review to block terminal Card completion while there is no attempt, a pending/in-progress attempt, or a RED attempt. Contradictory/stale state must fail closed.
- Expected behavior: A Card whose stable contract requires review must not become terminal while review is absent, non-terminal, or RED. In particular, a RED review must remain load-bearing and route corrective classification (or contradictory DONE state must fail closed), not disappear behind Close.
- Actual behavior: `validate_board()` accepts any `status = "done"` Card with a result locator and does not inspect its stable Card review requirement or review attempts. `select_route()` loads review state only for `in_progress` Cards; with no active Card, an all-DONE Board routes directly to `close`. A DONE Card with an exact RED attempt is therefore accepted and its review record is not even read.
- Minimal reproduction: Run `repro_done_bypasses_red_review()` in `audits/swarm/novka0hlkl74xbxwtotil5iz/repros/repro_router_review_jit.py`. It builds a REQUIRED-review Card with a result and RED attempt, changes only Card status to DONE, and demonstrates that the selector returns `route/close` while the read set omits the review artifact.
- Why this is materially load-bearing: The independent implementation-review gate can be bypassed by durable Board state alone, allowing failed or not-yet-reviewed implementation state to enter Close/finalization.
- Defect class / likely siblings: Terminal-status consistency is not cross-validated against the stable Card/review lifecycle. The same bypass applies to DONE + no required attempt, DONE + pending/in-progress attempt, and activated RECOMMENDED review.
- Existing tests that failed to catch it: `test_required_review_blocks_until_green_then_routes_finalization` exercises only an `in_progress` Card. `test_all_terminal_cards_route_to_close_not_directly_to_stop` uses `Review requirement: none`, so it never tests a contradictory terminal Card.
- Reproduction artifact, if any: `repros/repro_router_review_jit.py` (`repro_done_bypasses_red_review`).

### F2 — Same-path result mutation can reuse stale GREEN because Git identity is not verified

- Affected workflow contract/invariant: `workflow/STATE.md`, `workflow/RECOVERY.md`, and `workflow/REVIEW.md` require immutable Git result identity, exact-subject review coverage, and fail-closed handling for stale or same-path-changed inputs.
- Expected behavior: Before reusing a GREEN verdict, the current result artifact must be proven to be the exact Git object named by its `repository/commit/path/blob` identity. Changing bytes at the same path without changing the exact identity must be detected as stale/contradictory state and cannot inherit prior review.
- Actual behavior: Result/review commit and blob fields are validated only as 40-hex strings. The router reads the current workspace result bytes, but `exact_result_subject()` is built only from the Board's declared strings and `review_subject()` only from the review's declared strings. No Git object is resolved and no current bytes are hashed/compared. If the result file changes at the same path while Board/review identity strings remain unchanged, the old GREEN still compares equal and routes `post_review_finalization`.
- Minimal reproduction: Run `repro_same_path_result_mutation_reuses_green()`. It installs a REQUIRED-review result and matching GREEN attempt, then changes the result file's tests/readback content only. The Board and review retain the original declared identity, yet the selector returns `route/post_review_finalization`.
- Why this is materially load-bearing: Review authority can be transferred from the reviewed bytes to different bytes at the same path, defeating the exact immutable subject that makes independent review and recovery trustworthy.
- Defect class / likely siblings: Declared Git identity is treated as self-authenticating metadata rather than verified object identity. The same pattern exists in READY dependency refresh (tuple equality followed by reading the current path), and frozen-plan/Plan Review validators likewise validate identity syntax/binding without resolving the claimed Git object.
- Existing tests that failed to catch it: `test_changed_result_after_terminal_review_requires_new_attempt` changes the Board's blob string, so string comparison catches it. `test_ready_card_stale_dependency_fails_closed_before_launch` changes the Board dependency/result tuple too. Neither mutates same-path bytes while leaving declared identity unchanged.
- Reproduction artifact, if any: `repros/repro_router_review_jit.py` (`repro_same_path_result_mutation_reuses_green`).

### F3 — Missing terminal review evidence still permits finalization

- Affected workflow contract/invariant: `workflow/REVIEW.md` requires terminal attempts to keep durable verdict evidence, and recovery must be reconstructible from durable repository state.
- Expected behavior: A terminal GREEN/RED attempt whose evidence artifact is missing/unreadable must fail closed before its verdict can authorize finalization or correction.
- Actual behavior: `validate_review()` requires only a non-empty, syntactically safe `evidence_path` for GREEN/RED. The router never reads or otherwise verifies that evidence path. A GREEN attempt naming a nonexistent evidence artifact passes validation and routes `post_review_finalization`.
- Minimal reproduction: Run `repro_missing_review_evidence_still_finalizes()`. It creates a required-review result and GREEN attempt whose `evidence_path` names `evidence/DOES-NOT-EXIST.md`, deliberately does not create that file, and demonstrates finalization; the missing evidence path is absent from the selector read set.
- Why this is materially load-bearing: A blocking review verdict can become durable workflow authority without the durable evidence required to audit or recover that verdict.
- Defect class / likely siblings: Terminal evidence is validated as locator text rather than durable readable evidence. `validate_plan_review()` has the same non-empty-safe-path pattern for terminal Plan Review evidence.
- Existing tests that failed to catch it: `test_review_terminal_evidence_and_append_only_history` checks empty versus non-empty evidence strings, not file existence/readability. Router helpers used by review lifecycle tests create the evidence file, so the negative space is untested.
- Reproduction artifact, if any: `repros/repro_router_review_jit.py` (`repro_missing_review_evidence_still_finalizes`).

### F4 — Satisfied JIT trigger is ignored when all Cards are DONE, routing Close

- Affected workflow contract/invariant: `workflow/EXECUTION_PREP.md` defines `waiting -> satisfied -> consumed` JIT lifecycle, where a satisfied predecessor trigger means the downstream stable Card can now be materialized. `workflow/CLOSE.md` forbids treating an empty/currently-terminal Card queue as end of approved scope while an already-authorized obligation remains.
- Expected behavior: A valid `satisfied` JIT trigger must remain an Execution Prep/materialization obligation and must prevent the Board from being treated as ready for Close until that trigger is consumed through the required downstream materialization/reconciliation.
- Actual behavior: `validate_board()` accepts a `satisfied` trigger when its predecessor Card is DONE with a result, but `select_route()` never inspects trigger state after validation. If all currently materialized Cards are DONE, the selector routes directly to `close`, ignoring the satisfied downstream trigger.
- Minimal reproduction: Run `repro_satisfied_jit_trigger_is_ignored_by_close()`. It creates one DONE predecessor with a durable result and a top-level satisfied JIT trigger whose condition says that result makes the downstream Card boundary knowable. The selector returns `route/close` instead of Execution Prep/JIT materialization.
- Why this is materially load-bearing: Authorized downstream scope represented precisely by the JIT mechanism can be skipped, allowing premature Close/integration and possible false completion.
- Defect class / likely siblings: Router/validator parity gap: JIT state is validated but omitted from routing precedence. A consumed trigger also has weak linkage to proof of downstream materialization, though that sibling was not frozen as a separate finding.
- Existing tests that failed to catch it: `test_jit_trigger_preserves_predecessor_boundary_without_placeholder_card` validates trigger states but never runs the selector. `test_all_terminal_cards_route_to_close_not_directly_to_stop` contains no JIT trigger.
- Reproduction artifact, if any: `repros/repro_router_review_jit.py` (`repro_satisfied_jit_trigger_is_ignored_by_close`).

## Non-blocking observations

The four findings above arise from interactions between individually plausible local validators and selector branches rather than ordinary style concerns. No additional advisory-only defect was promoted to the material finding set.

A one-sentence repair direction for the shared defect class would be to make terminal routing consume verified durable invariants rather than self-declared locator metadata: cross-check DONE against Card/review state, cryptographically/Git-verify exact subjects, require readable terminal evidence, and give unconsumed satisfied JIT obligations precedence over Close.

## Coverage

The audit remained bound to exact subject commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045` for product analysis. It inspected canonical routing/state/review/recovery/execution/JIT/Close contracts, the production router and state/recovery/execution/Close helpers, relevant router/state tests, and the existing valid router fixture.

All four selected lenses were exercised: review bypass/result mutation (F1-F3), contradictory/fail-closed state (F1/F3/F4), stale exact identity (F2), and Task Board/DONE/JIT lifecycle (F1/F4). Negative-space comparison included existing tests for changed result metadata, stale READY dependencies, active review lifecycle, terminal Cards, and JIT validation.

The preserved reproduction script is non-mutating: it copies the repository fixture into temporary directories, mutates only those copies, and first asserts that `workflow/`, `tools/`, `tests/`, `hooks/`, `skills/`, `templates/`, and `schemas/` still match the exact audit subject.

## Confidence and limitations

Confidence in the four semantic findings is high from direct production control-flow/validator inspection and the concrete fixture-based reproductions. However, the preserved reproduction script could not be executed in this audit environment: the normal container could not reach GitHub, Remote Desktop Commander had exhausted its monthly tool quota, and the available native command bridge did not accept the current turn token. The script is therefore preserved for deterministic execution/readback rather than claimed as an executed run here.

The GitHub commit-metadata endpoint unexpectedly over-returned historical `implementation/workstreams/**` review/evidence diff content before findings were frozen. Those passages were not used as finding sources, and no `audit/*` branches, swarm reports, GitHub Issues, or PR comments were inspected. Because the over-return occurred before freeze, perfect historical blindness cannot be claimed despite the audit's independent finding derivation.
