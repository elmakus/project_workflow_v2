# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Card status can bypass result/review precedence, causing replay or premature Close

- Affected workflow contract/invariant: `workflow/ROUTER.md` priority foundation; `workflow/STATE.md` result/review lifecycle; `workflow/EXECUTION.md` accepted-result recovery truth.
- Expected behavior: once a durable result exists, result/review reconciliation must outrank launch/status; a review-required Card cannot become terminal without exact GREEN review.
- Actual behavior: `validate_board` permits `result` on any Card status and only requires a result locator for `done`. `select_route` inspects a Card result only inside the `in_progress` branch. Therefore a `ready` Card carrying a valid result routes to `execution_prep` (replay path), while a `done` Card with a required-review result and zero review attempts routes directly to `close`.
- Minimal reproduction: from the router valid fixture, call the existing `install_reviewable_result(project, "required")`, change the Card status from `in_progress` to `done`, leave `review_attempts` absent, then call `select_route`; the selected obligation is `close`. Sibling: change status to `ready` while keeping the result; the selected obligation is `execution_prep`.
- Why this is materially load-bearing: one mutable status edit can skip a blocking review gate or replay implementation despite durable recovery truth.
- Defect class / likely siblings: missing cross-field state invariants and result precedence for `planned|ready|blocked|done`.
- Existing tests that failed to catch it: `test_all_terminal_cards_route_to_close_not_directly_to_stop` only uses `review_requirement = none`; result/review tests keep the Card `in_progress`.
- Reproduction artifact, if any: `repros/repro_router_semantic_gaps.py`.

### F2 — Same-path dependency changes are not checked against declared commit/blob identity

- Affected workflow contract/invariant: `workflow/STATE.md` and `workflow/EXECUTION_PREP.md` require exact dependency result path + immutable commit/blob identity and explicitly say same-path-changed dependency inputs fail closed.
- Expected behavior: launch refresh must prove the dependency file being consumed is the declared blob at the declared commit.
- Actual behavior: `refresh_ready_card` compares the Card's dependency tuple only with the DONE predecessor tuple stored in the same Task Board, then reads the current filesystem path. It never hashes/dereferences the declared blob or reads the file at the declared commit. If the dependency file changes in place while both tuples remain unchanged, launch still routes to `execution_prep`.
- Minimal reproduction: install a DONE predecessor with dependency tuple A/B, make the current Card READY with the same tuple, then change only the predecessor result file contents and leave Task Board/Card identities unchanged. The selector has no check capable of observing the mismatch.
- Why this is materially load-bearing: downstream execution can consume content different from the immutable dependency it claims to trust.
- Defect class / likely siblings: syntactic Git identity without object verification; similar risk exists for other commit/blob subjects.
- Existing tests that failed to catch it: `test_ready_card_stale_dependency_fails_closed_before_launch` changes the Task Board commit/blob together with the file, so it tests tuple disagreement rather than same-path content drift.
- Reproduction artifact, if any: `repros/repro_router_semantic_gaps.py`.

### F3 — Terminal evidence is accepted by pathname, not by durable existence/content

- Affected workflow contract/invariant: `workflow/REVIEW.md`, `workflow/PLAN_REVIEW.md`, and `workflow/EXECUTION.md` require durable verdict/result evidence.
- Expected behavior: a terminal GREEN/RED attempt (and an accepted Card result) must have evidence that is actually durable and readable under the required evidence authority.
- Actual behavior: `validate_review` and `validate_plan_review` require only a non-empty safe-relative `evidence_path`; the selector never reads that path. `parse_card_result` likewise validates evidence-ref syntax but does not read the referenced evidence. A GREEN attempt whose evidence file has been deleted still permits `post_review_finalization`; a Plan Review can use an arbitrary/nonexistent safe relative path and still be consumed.
- Minimal reproduction: create a normal GREEN review using the existing router helper, delete its evidence Markdown file, then call `select_route`; the review record still validates and the selector routes to `post_review_finalization`.
- Why this is materially load-bearing: the blocking review gate can be satisfied by evidence that is not durable at all.
- Defect class / likely siblings: locator-shape validation substituted for evidence readback; Card-result evidence refs and Plan Review evidence share the same gap.
- Existing tests that failed to catch it: tests reject only an empty terminal `evidence_path`; helper-generated GREEN reviews create the evidence file and never remove/substitute it.
- Reproduction artifact, if any: `repros/repro_router_semantic_gaps.py`.

### F4 — Approved Planning is not bound to the current Definition revision

- Affected workflow contract/invariant: `workflow/DEFINITION.md`, `workflow/PLANNING.md`, and router Planning/Premium gate precedence.
- Expected behavior: Planning must consume the exact current accepted Definition authority; a changed Definition must invalidate stale Planning authority and require appropriate re-entry/gates.
- Actual behavior: `validate_planning` only requires a non-empty `entry_subject` and self-consistency with `premium_a_subject`. `select_route` never compares that entry subject with the loaded Definition revision. Changing `DEFINITION.toml` from revision R1 to R2 while retaining an approved R1 plan/review/C state still dispatches the live Task Board.
- Minimal reproduction: install the fixture's approved plan (entry subject `definition:R1|planning-cycle:1`), change only `DEFINITION.toml revision = "R2"`, and call `select_route`; stale R1 Planning remains accepted and execution is selected.
- Why this is materially load-bearing: downstream execution may proceed under superseded product authority without a new Planning/Premium cycle.
- Defect class / likely siblings: missing cross-record subject binding between adjacent authority stages.
- Existing tests that failed to catch it: stale-cycle tests mutate Planning's own A subject; Definition-source tests cover Brainstorming→Definition, not Definition→Planning.
- Reproduction artifact, if any: `repros/repro_router_semantic_gaps.py`.

### F5 — A durable explicit user stop is masked once Definition/Planning state exists

- Affected workflow contract/invariant: `PRIORITY_FOUNDATION` places explicit human boundaries first; `workflow/BRAINSTORMING.md` states `explicit user stop -> real stop`.
- Expected behavior: a valid durable `explicit_user_stop = true` must stop before downstream semantic work.
- Actual behavior: the router loads Brainstorming, then processes Definition and Planning first. The explicit-user-stop branch is reached only later under the fallback Brainstorming block. The validator permits a promoted Brainstorming record with `explicit_user_stop = true`, so downstream state can mask the stop.
- Minimal reproduction: use a promoted Brainstorming + GREEN Definition fixture and flip only `explicit_user_stop` from false to true. With no Planning record the selector routes to `planning` instead of `stop/explicit_user_stop`.
- Why this is materially load-bearing: explicit human stop authority is lower precedence in executable routing than the documented priority foundation.
- Defect class / likely siblings: unreachable/higher-precedence obligation masked by downstream-state branches.
- Existing tests that failed to catch it: router tests contain no positive `explicit_user_stop` case with downstream Definition state.
- Reproduction artifact, if any: `repros/repro_router_semantic_gaps.py`.

### F6 — A satisfied JIT trigger is ignored and can be closed over

- Affected workflow contract/invariant: `workflow/EXECUTION_PREP.md` defines `waiting -> satisfied -> consumed`; `workflow/CLOSE.md` forbids end-of-scope conclusions while an authorized in-scope obligation remains.
- Expected behavior: a `satisfied` trigger backed by a DONE predecessor result must route to Execution Prep to materialize/consume the downstream Card before Close can treat the current scope as terminal.
- Actual behavior: `validate_board` validates JIT triggers, but `select_route` never reads `board["jit_triggers"]`. When all current Cards are `done`, the selector routes to `close` even if a trigger remains `satisfied`.
- Minimal reproduction: mark the fixture Card DONE with a valid result and add a valid `satisfied` trigger whose `after_card` is that Card. The all-DONE branch is selected; no trigger-consumption obligation is considered.
- Why this is materially load-bearing: known downstream approved work can be skipped by the routing boundary that hands control to Close.
- Defect class / likely siblings: validated lifecycle state omitted from executable routing/precedence.
- Existing tests that failed to catch it: state-contract tests validate trigger shape/lifecycle, while router tests contain no `jit_triggers` cases.
- Reproduction artifact, if any: `repros/repro_router_semantic_gaps.py`.

## Non-blocking observations

The SessionStart/bootstrap lens was exercised. The hook correctly rejects a missing/malformed/escaping router and PLUGIN_ROOT mismatch. No independent material bootstrap defect was frozen from that lens.

## Coverage

Inspected exact subject-commit versions of `workflow/ROUTER.md`, `STATE.md`, `PLANNING.md`, `PLAN_REVIEW.md`, `BRAINSTORMING.md`, `DEFINITION.md`, `EXECUTION_PREP.md`, `EXECUTION.md`, `REVIEW.md`, `CLOSE.md`, `AUTHORITY.md`, `WORKSTREAMS.md`; `tools/router.py`, `state_contract.py`, `execution_contract.py`, `recovery_contract.py`, `review_contract.py`, `close_contract.py`; relevant templates, fixtures, SessionStart/Skill delivery files, and focused router/state/close/delivery tests.

Selected lenses exercised:
- malformed or contradictory state / fail-closed behavior: F1, F3;
- helper vs documented semantics / parity drift / negative space: F2, F6;
- Planning / Premium gates / Execution precedence: F4, F5;
- plugin / install / update / SessionStart / bootstrap drift: inspected; no material finding frozen.

Additional Task Board/JIT and router-precedence interactions were tested by counterexample construction.

## Confidence and limitations

Confidence is high in the six static/executable-path counterexamples because each follows directly through production validator/selector branches at the immutable subject commit and is contrasted with explicit canonical contract text.

The available remote terminal was connected but its monthly command quota was exhausted, and the local container has no GitHub network access. Therefore the preserved repro script was not executed against a checkout during this chat. Existing production tests were inspected at the exact commit to identify the negative-space cases they omit. No historical audit reports, `audit/*` branches, Issues/PR defect discussions, or historical evidence/review narratives were inspected before freezing this finding set.

## Post-freeze historical comparison

Not performed.
