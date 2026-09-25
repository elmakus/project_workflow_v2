# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — DONE Card can bypass required review and even a missing result artifact

- Affected workflow contract/invariant: `workflow/REVIEW.md` requires REQUIRED/activated RECOMMENDED review to block terminal Card completion until exact GREEN; `workflow/ROUTER.md` says invalid/missing/stale/contradictory bindings fail closed to Recovery; `workflow/CLOSE.md` says completion is not inferred merely from terminal-looking queue state.
- Expected behavior: a Card marked `done` must still prove that its stable Card contract permits terminal completion, its exact durable result exists and validates, and any required review history ends in exact current GREEN. Missing result content or absent/RED/pending required review must not route to Close.
- Actual behavior: `validate_board()` only requires a `done` Card to contain a syntactically shaped `result` locator. It does not read the Task Card, result artifact, or review attempts. After validation, `select_route()` sends an all-`done` board directly to `close`. Therefore a required-review Card with no review attempts and even a nonexistent result file reaches Close.
- Minimal reproduction: copy `tests/fixtures/router/valid-project`; replace the Card with a valid stable contract containing `Review requirement: required`; set its board status to `done`; add a 40-hex result locator; do not create the result file and do not add review attempts; call `select_route()`. The selector reaches `("route", "close")`.
- Why this is materially load-bearing: this permits finalization/integration ownership to be reached without the independent implementation review and durable result evidence that are supposed to be blocking integrity gates.
- Defect class / likely siblings: any terminal Card state whose contract/result/review/evidence is dangling, stale, RED, pending, or absent; review evidence paths are also not dereferenced during terminal-board validation.
- Existing tests that failed to catch it: `test_all_terminal_cards_route_to_close_not_directly_to_stop` uses a Card with review requirement `none`; the required-review tests keep the Card `in_progress` and therefore never exercise terminal-board revalidation.
- Reproduction artifact, if any: `audits/swarm/q7m2v9k4x1c8n5r0t6b3p2hz/repros/repro_router_invariants.py` (`repro_f1_done_bypasses_review_and_missing_result`).

### F2 — Exact result/dependency Git identity is trusted as metadata rather than verified content

- Affected workflow contract/invariant: `workflow/EXECUTION_PREP.md` requires dependency results to be bound by exact path + immutable commit/blob identity; `workflow/RECOVERY.md` requires review subject refresh against the exact current result; `workflow/REVIEW.md` allows GREEN finalization only for the exact current immutable subject.
- Expected behavior: if the artifact bytes at a result/dependency path no longer correspond to the declared commit/blob, the stale locator must fail closed before dependency launch, review reuse, or post-review finalization.
- Actual behavior: `refresh_ready_card()` compares the dependency's declared `(path, commit, blob)` tuple only to the predecessor Card's declared tuple, then merely reads the current path. Active-result recovery similarly parses the current file but constructs `current_subject` from the board's declared metadata without verifying that the bytes match the blob or that the commit contains that blob at that path. A GREEN attempt matching the unchanged metadata therefore still finalizes after the result file is materially changed.
- Minimal reproduction: create an `in_progress` required-review Card with a result locator `a.../b...` and GREEN attempt covering the same locator; first use valid result content A, then replace the result file with different but syntactically valid content B while leaving board and review metadata unchanged. `select_route()` still returns `post_review_finalization`. The analogous READY-dependency variant changes only the predecessor result file while leaving both dependency tuples unchanged; launch refresh cannot notice.
- Why this is materially load-bearing: the immutable Git tuple is the mechanism that prevents a verdict or downstream dependency from silently attaching to different content. Treating it as an unverified string defeats stale-result protection and permits one blob's review to authorize another blob's bytes.
- Defect class / likely siblings: result locators, DONE dependency locators, frozen planning subjects, and other exact Git-blob subjects whose repository/commit/blob fields are compared as strings but not resolved against Git object truth.
- Existing tests that failed to catch it: `test_changed_result_after_terminal_review_requires_new_attempt` changes the board's declared blob, not the result file under unchanged metadata; `test_ready_card_stale_dependency_fails_closed_before_launch` changes both predecessor content and predecessor locator, so it exercises tuple disagreement rather than content-vs-tuple disagreement.
- Reproduction artifact, if any: `audits/swarm/q7m2v9k4x1c8n5r0t6b3p2hz/repros/repro_router_invariants.py` (`repro_f2_mutated_result_keeps_green_review`).

### F3 — Approved Planning is not bound to the current Definition revision or authority surface

- Affected workflow contract/invariant: `workflow/PLANNING.md` says Strategic Planning converts the current GREEN Definition authority into a revisioned executable strategy and that every material cycle has an exact entry subject; stale/contradictory binding must fail closed.
- Expected behavior: changing the accepted Definition revision or its requirements/decision authority must invalidate a plan whose entry subject, premium gates and GREEN Plan Review belong to the earlier Definition, requiring a new legal planning cycle/gates or Recovery.
- Actual behavior: `validate_planning()` only requires `entry_subject` to be nonempty and requires `premium_a_subject == entry_subject`; neither it nor `select_route()` compares that subject to the current `DEFINITION.toml` revision or requirements/decisions. A formerly approved R1 plan with satisfied A/B/C and GREEN Plan Review therefore remains accepted after Definition is changed to R2 with different requirement authority, and the co-bound Task Board can still dispatch Execution.
- Minimal reproduction: install promoted Brainstorming, GREEN Definition R1 pointing at `requirements/OLD.md`, approved Planning with `entry_subject = "definition:R1|planning-cycle:1"`, GREEN Plan Review and satisfied C; verify board Execution is selected; then change only Definition to revision R2 and `requirements/NEW.md`, leaving Planning/Plan Review untouched. The selector still dispatches Execution instead of invalidating the stale plan.
- Why this is materially load-bearing: accepted product/Definition authority can change while an old plan and its old review/gates continue authorizing implementation, violating the authority chain that Planning is supposed to derive from.
- Defect class / likely siblings: stale planning cycles after Definition revision/requirements/decisions changes; the initial Definition premium-A state is likewise not subject-bound, so stale satisfaction cannot be correlated to a specific Definition revision.
- Existing tests that failed to catch it: `test_stale_premium_cycle_and_wrong_review_subject_fail_closed` checks internal Planning A/subject consistency and plan-review subject consistency, but no test mutates Definition after Planning exists; `test_definition_source_mismatch_fails_closed` only binds Definition back to Brainstorming.
- Reproduction artifact, if any: `audits/swarm/q7m2v9k4x1c8n5r0t6b3p2hz/repros/repro_router_invariants.py` (`repro_f3_stale_plan_survives_definition_change`).

### F4 — Downstream Definition can bypass Brainstorming lifecycle and an explicit user stop

- Affected workflow contract/invariant: `workflow/BRAINSTORMING.md` states `explicit user stop -> real stop` and `exact promoted revision -> Definition owns continuation`; `workflow/DEFINITION.md` requires an exact promoted Brainstorming subject; router priority places explicit human boundaries above later stages.
- Expected behavior: a Brainstorming record with `explicit_user_stop = true` must stop; a Definition locator must not be accepted unless the durable Brainstorming lifecycle state is actually `promoted`.
- Actual behavior: when a Definition locator exists, `select_route()` validates only that Brainstorming `promotion_state == "authorized"` and that subject strings match. It does not require `brainstorm.state == "promoted"`, and it evaluates Definition routing before the later block that checks `explicit_user_stop`. `validate_brainstorm()` permits `state = "active"` together with exact authorized promotion. Thus an active Brainstorming record carrying an explicit stop plus matching Definition is routed to Definition.
- Minimal reproduction: use `BRAINSTORM.toml` with `state = "active"`, GREEN challenge, `explicit_user_stop = true`, `promotion_state = "authorized"`, exact promotion subject; add matching active `DEFINITION.toml`. `select_route()` returns `("route", "definition")` rather than a real stop/Recovery.
- Why this is materially load-bearing: a direct user stop and the durable promotion lifecycle are authorization boundaries. Bypassing either allows downstream work to continue without the required current human boundary.
- Defect class / likely siblings: `ready_for_definition` or `active` Brainstorming with authorized promotion plus pre-created Definition; any downstream state that causes the Brainstorming stop block to become unreachable.
- Existing tests that failed to catch it: Brainstorming tests cover ready+pending and promoted+authorized happy paths; Definition tests use `state = "promoted"`; no test combines non-promoted authorized Brainstorming or `explicit_user_stop = true` with a Definition locator.
- Reproduction artifact, if any: `audits/swarm/q7m2v9k4x1c8n5r0t6b3p2hz/repros/repro_router_invariants.py` (`repro_f4_nonpromoted_explicit_stop_enters_definition`).

### F5 — Plan Review acceptance is not bound to current Definition/requirements/decisions

- Affected workflow contract/invariant: `workflow/PLAN_REVIEW.md` says Plan Review judges the exact frozen plan against its accepted Definition/requirements/decisions and planning acceptance surface; the review gate is intended to be an independent exact-subject authorization check.
- Expected behavior: Plan Review acceptance must identify and still match the current accepted Definition authority surface. An unrelated or stale authority locator must fail validation/Recovery and must not be consumable as GREEN.
- Actual behavior: generic `validate_review()` accepts any `acceptance.class = "authority"` path under `requirements/`, `decisions/`, `planning/`, or `workflow/`. `validate_plan_review()` checks plan revision, cycle and reviewed plan subject, but receives no Definition object and performs no comparison between the review acceptance locator and current Definition requirements/decisions. Consequently a GREEN Plan Review whose acceptance points at an unrelated `workflow/ROUTER.md` locator still routes to Planning for GREEN consumption.
- Minimal reproduction: create a valid frozen plan with premium B satisfied and a GREEN Plan Review whose exact plan subject/cycle/revision match, but set `[acceptance] class = "authority", path = "workflow/ROUTER.md"` while Definition points at `requirements/ACCEPTED.md`. The selector returns `("route", "planning")`.
- Why this is materially load-bearing: Stage-6 review can become GREEN without being bound to the authority it is supposed to review against, so the independent review gate can approve the right plan blob against the wrong acceptance surface.
- Defect class / likely siblings: stale old requirements locator, a single unrelated decision file, or any accepted authority-root path can stand in for the current complete Definition surface.
- Existing tests that failed to catch it: Plan Review fixtures consistently use `requirements/REQUIREMENTS.md` and test subject/cycle/revision mismatch, but there is no negative test that changes the acceptance locator away from current Definition authority.
- Reproduction artifact, if any: `audits/swarm/q7m2v9k4x1c8n5r0t6b3p2hz/repros/repro_router_invariants.py` (`repro_f5_plan_review_accepts_unrelated_authority`).

## Non-blocking observations

A board with all current Cards `done` and a `satisfied` JIT trigger still selects Close because the selector never consults JIT trigger state after board validation. This was not promoted to a material finding because the current Close contract says Close may continue already-authorized obligations, so ownership of the immediate redispatch is not unambiguous from the inspected contracts. A dedicated negative-space test would make the intended owner explicit.

Terminal review `evidence_path` values and several authority locators are syntactically validated without existence/content readback. This is potentially related to F1/F5, but the five findings above already demonstrate the concrete authorization failures without relying on that broader concern.

## Coverage

The audit remained bound to commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045` and did not inspect `audit/*` branches, GitHub Issues, PR comments, prior swarm reports, or historical workstream evidence/review narratives before freezing findings.

Inspected exact-commit production contracts and helpers included:

- `workflow/ROUTER.md`, `BRAINSTORMING.md`, `DEFINITION.md`, `PLANNING.md`, `PLAN_REVIEW.md`, `EXECUTION_PREP.md`, `EXECUTION.md`, `REVIEW.md`, `RECOVERY.md`, `CLOSE.md`, and `USER_STOP.md`;
- `tools/router.py`, `state_contract.py`, `execution_contract.py`, `recovery_contract.py`, and `close_contract.py`;
- `tests/test_router.py`, `test_state_contract.py`, `test_execution_contract.py`, `test_recovery_contract.py`, `test_close_contract.py`, plus the exact router fixture used by the preserved repro.

Selected lenses exercised:

1. malformed/contradictory state and fail-closed behavior: F1, F3, F4;
2. review independence/bypass/result mutation: F1, F2, F5;
3. Close/finalization/end-of-approved-scope: F1 and JIT negative-space observation;
4. helper/documented-semantics parity/negative space: F2, F3, F4, F5 and test-gap comparison.

## Confidence and limitations

Confidence is high in the control-flow/validation counterexamples because each is a direct composition of states accepted by the exact validators and branches visible in the exact production selector. The preserved reproduction script uses the repository's own router fixture and mutates only temporary copies.

I could not execute the preserved Python repro against a full local checkout in this audit environment: the local container had no repository checkout and network DNS access to GitHub was unavailable, while the GitHub connector provides repository object/file operations rather than a shell. Therefore the findings are source-level deterministic reproductions plus runnable repro artifacts, not locally captured stdout from the target checkout.

## Post-freeze historical comparison

Not performed. The independently frozen finding set was left unmodified and no historical audit/evidence comparison was needed for this report.
