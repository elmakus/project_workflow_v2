# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Malformed TOML escapes Recovery and crashes the selector

- Affected workflow contract/invariant: Invalid, missing, stale or contradictory durable state must fail closed to Recovery. The router is supposed to return a deterministic Recovery obligation rather than let malformed durable state become runtime behavior.
- Expected behavior: Syntax-corrupt TOML in PROJECT/workstream/pre-execution/Task Board/review state should produce `recovery / recovery_boundary`.
- Actual behavior: `read_toml()` and `read_project()` use `tomllib`, whose syntax failures raise `tomllib.TOMLDecodeError`. The main `select_route()` exception boundaries catch `OSError`, `ValidationError` and `KeyError`, but not `TOMLDecodeError`. The parse exception therefore escapes the selector.
- Minimal reproduction: Copy the normal router fixture, replace `TASK_BOARD.toml` with syntactically invalid TOML such as `revision = [`, then call `select_route(...)`. `tomllib.TOMLDecodeError` escapes instead of returning a Recovery `RouteResult`. The same defect class applies to malformed WORKSTREAM, planning, review and other TOML read through the selector.
- Why this is materially load-bearing: A partially written or corrupted durable state file destroys deterministic fail-closed recovery and hands control back to runtime/harness exception behavior.
- Defect class / likely siblings: Every selector-side `read_toml()`/`read_project()` parse site whose surrounding exception boundary omits `tomllib.TOMLDecodeError`.
- Existing tests that failed to catch it: Router tests cover semantically invalid bindings and missing state, but not syntactically malformed TOML. `state_contract.py`'s CLI does explicitly catch `tomllib.TOMLDecodeError`, making the selector/helper behavior inconsistent.
- Reproduction artifact, if any: none persisted; reproduction is direct from the production exception boundary.

### F2 — Result Git identity is declarative only and permits stale/unreviewed content

- Affected workflow contract/invariant: A durable Card result and review subject must bind exact immutable repository/commit/path/blob identity. Changed result content must not reuse a prior exact review.
- Expected behavior: The selector must verify that the result artifact being consumed is the exact object named by its commit/blob binding. Same-path content drift must fail closed or require a new review subject.
- Actual behavior: `validate_locator(..., "result", ...)` accepts a result locator with no `commit`/`blob` at all when both keys are omitted. When identity fields are present it validates only their 40-hex syntax. The router reads the current result path but never verifies its bytes against the claimed blob/commit. `exact_result_subject()` simply concatenates the locator's claimed strings. Consequently a result file can change in place while its locator and GREEN review remain unchanged, and the router still treats the old review as covering the current result.
- Minimal reproduction: Start with an active review-required Card whose result locator names commit A/blob B and whose GREEN attempt covers A/path/B. Change the result file contents at that same path without changing the Board locator or review TOML. Keep the result syntactically parseable. `select_route()` still reaches `post_review_finalization`. A no-review active result can additionally omit commit/blob completely and still reach `result_reconciliation`.
- Why this is materially load-bearing: Unreviewed result content can inherit a GREEN verdict for different bytes, defeating exact-subject review/recovery semantics.
- Defect class / likely siblings: Claimed immutable Git identities are syntactically checked rather than dereferenced/hashed. Dependency and planning identities deserve the same negative-space scrutiny.
- Existing tests that failed to catch it: `test_changed_result_after_terminal_review_requires_new_attempt` changes the locator blob itself. `test_ready_card_stale_dependency_fails_closed_before_launch` changes the Board's declared predecessor identity. Neither mutates bytes while leaving the claimed exact identity unchanged.
- Reproduction artifact, if any: none persisted; minimal state mutation is described above.

### F3 — DONE fast path can bypass result/review validity and enter Close

- Affected workflow contract/invariant: REQUIRED/activated RECOMMENDED review pending/in-progress/RED blocks terminal Card completion; invalid/missing result/review state must fail closed. Close must not be reached merely because mutable Board status says `done`.
- Expected behavior: Before a Card is accepted as terminal, its durable result and blocking review state must be consistent with terminal completion.
- Actual behavior: `validate_board()` requires a `done` Card only to contain a syntactically valid result locator. It does not read the result, Card contract or attempts and does not prove review completion. Once no active/blocked/ready Cards remain, the router checks only `all(card["status"] == "done")` and routes directly to Close without loading those artifacts.
- Minimal reproduction: Build a review-required Card with a durable result and a pending or RED review attempt, then mutate Board status to `done`. Alternatively delete the referenced result file after marking the Card `done`. The Board still validates structurally and the selector reaches `route / close` without reading the blocking/missing artifacts.
- Why this is materially load-bearing: Mutable status can bypass the independent-review gate and move malformed work into final integration/closure ownership.
- Defect class / likely siblings: Terminal-status trust without semantic terminal-state validation; missing/stale result files and unresolved review attempts share the same fast path.
- Existing tests that failed to catch it: `test_all_terminal_cards_route_to_close_not_directly_to_stop` exercises a Card whose review requirement is `none`; there is no negative terminal-state test with REQUIRED review pending/RED or a missing result artifact.
- Reproduction artifact, if any: none persisted; minimal state mutation is described above.

### F4 — JIT-trigger lifecycle is ignored by routing and can lose approved downstream scope

- Affected workflow contract/invariant: Predecessor-dependent downstream work remains a Task Board JIT trigger until its stable Card becomes knowable. A `satisfied` trigger means downstream materialization is now due; `consumed` must represent successful consumption rather than disappearance of scope. End-of-scope/Close must not preempt an already-authorized downstream obligation.
- Expected behavior: A satisfied JIT trigger with a DONE predecessor should route to Execution Prep for downstream Card materialization. A trigger must not become `consumed` without durable evidence that its downstream Card contract was materialized.
- Actual behavior: `validate_board()` checks only that `satisfied` or `consumed` triggers name a DONE predecessor with a result. It does not bind `consumed` to any downstream Card. `select_route()` does not inspect `jit_triggers` at all. Therefore a Board whose existing Cards are all DONE and which contains a `satisfied` trigger routes to Close; a trigger may also be marked `consumed` with no downstream Card and produce the same result.
- Minimal reproduction: Create one DONE predecessor Card with a result and add a JIT trigger `after_card=<that Card>, state="satisfied"`. Leave no active/ready downstream Card. The Board validates, then the router reaches the all-DONE branch and selects Close instead of Execution Prep. Changing the trigger to `consumed` with no materialized downstream Card is also accepted.
- Why this is materially load-bearing: Accepted downstream scope can disappear from deterministic routing and the workstream can enter finalization prematurely.
- Defect class / likely siblings: Task Board JIT state is validated locally but never participates in selector precedence/terminal completeness; `consumed` has no durable downstream binding.
- Existing tests that failed to catch it: `test_jit_trigger_preserves_predecessor_boundary_without_placeholder_card` validates `waiting` and `satisfied` schema state but never routes it. Router tests contain JIT refinement classification tests but no JIT-trigger lifecycle/Close interaction.
- Reproduction artifact, if any: none persisted; minimal state mutation is described above.

### F5 — GREEN review can finalize without durable evidence or exact current acceptance binding

- Affected workflow contract/invariant: Terminal review attempts require durable verdict evidence and bind the exact current acceptance surface of the Card.
- Expected behavior: GREEN finalization should require the referenced evidence to exist and the review acceptance identity to match the active Card's exact acceptance contract.
- Actual behavior: `validate_review()` requires a terminal `evidence_path` only to be a non-empty safe relative string; neither the validator nor the router reads that path. A nonexistent evidence file therefore satisfies the review gate. For task-card acceptance, validation checks only that the path is inside the workstream's cards directory and its basename stem equals `card_id`; the router does not compare it to `card["contract"]["path"]` and does not read the acceptance artifact identified by the review.
- Minimal reproduction: Use a review-required active Card/result and a GREEN review whose result subject matches but whose `evidence_path` points to a nonexistent file. `select_route()` still reaches `post_review_finalization`. As a sibling, point review acceptance at `cards/archive/M01-T04.md` while the Board's actual contract is `cards/M01-T04.md`; the same Card-ID stem is enough for validation even if the acceptance path is absent or different.
- Why this is materially load-bearing: An exact independent review gate can become a self-declared GREEN flag with no durable verdict evidence and potentially no binding to the actual acceptance contract being finalized.
- Defect class / likely siblings: Undereferenced review locators; Plan Review terminal evidence uses the same non-empty-path-only pattern.
- Existing tests that failed to catch it: Review tests prove only that terminal `evidence_path` is non-empty. Router fixtures happen to create an evidence file, but no test removes it or varies acceptance independently from the active Card contract.
- Reproduction artifact, if any: none persisted; minimal state mutation is described above.

### F6 — Task-Board Research can route to a fabricated/stale Card subject

- Affected workflow contract/invariant: Implementation/recovery Research must be owned by the selected Task Board with an exact origin and return owner; recovery must resume the exact durable Card obligation rather than an unrelated/fabricated subject.
- Expected behavior: Board-owned Research origin/return subject must be coherent and bound to an existing applicable Card on that Board.
- Actual behavior: `validate_research()` requires only a non-empty `origin_subject` and a prefix-shaped execution return target. The Board-specific handler verifies that `origin_role` is an implementation/recovery role but does not require the return-target suffix to equal `origin_subject`, does not require either value to name a Board Card, and does not require the Card to be the applicable current/blocked Card.
- Minimal reproduction: Point the Board at completed Research with `origin_role="execution_resolution"`, `origin_subject="M01-T04"` and `return_target="execution_resolution:PHANTOM"`. Validation succeeds and the router selects `execution_resolution` with subject `PHANTOM`.
- Why this is materially load-bearing: Corrupt/stale Research state can redirect recovery or execution ownership away from the actual Card rather than fail closed.
- Defect class / likely siblings: Missing origin/return/card coherence validation in Research bindings.
- Existing tests that failed to catch it: `test_task_board_research_return_is_recovered_before_execution` exercises only matching `M01-T04` origin/return subjects and does not include mismatched/nonexistent Card cases.
- Reproduction artifact, if any: none persisted; minimal state mutation is described above.

### F7 — SessionStart accepts a sentinel-preserving truncated router as valid

- Affected workflow contract/invariant: The installed Codex bootstrap must fail closed when its canonical router is missing or malformed. Missing workflow policy must not be reconstructed from runtime/chat state.
- Expected behavior: A truncated router lacking the actual routing contract should produce the blocking plugin-package error.
- Actual behavior: `hooks/session-start.py::canonical_router()` considers a router valid if the file exists inside the package root and contains two substrings: `# Project Workflow V2 Router` and `Production selector: \`tools/router.py\`.`. It performs no stronger structural/integrity validation.
- Minimal reproduction: Replace installed `workflow/ROUTER.md` with only the expected header and selector sentinel. The two sentinels pass `canonical_router()` and `build_context()` reports `Project Workflow V2 package is enabled` rather than a blocking package error.
- Why this is materially load-bearing: SessionStart can certify an installation whose canonical workflow semantics are effectively absent, undermining the package's fail-closed bootstrap boundary.
- Defect class / likely siblings: Sentinel-presence validation used as policy-integrity validation; partial/truncated install/update states containing both markers are accepted.
- Existing tests that failed to catch it: `test_missing_and_malformed_router_fail_closed` uses `not a V2 router`, which removes both sentinels. No test preserves the sentinels while deleting the semantic body.
- Reproduction artifact, if any: none persisted; the two-line replacement is the complete reproducer.

## Non-blocking observations

- `tools/close_contract.py` represents several commit/head identities as merely non-empty strings rather than validating SHA-shaped identities. This was not promoted to a material finding because callers may be contractually responsible for resolving exact Git identities before invoking the helper.
- SessionStart also does not prove cross-file package integrity/version consistency between the bundled Router, production selector and other package payload. This may permit partial-update drift, but without an inspected installer/update atomicity contract it remains advisory rather than an independently demonstrated material defect.

## Coverage

The audit remained bound to repository `elmakus/project_workflow_v2` commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`.

Inspected canonical/product surfaces included `workflow/ROUTER.md`, `workflow/STATE.md`, `workflow/PLANNING.md`, `workflow/EXECUTION_PREP.md`, `workflow/EXECUTION.md`, `workflow/REVIEW.md`, `workflow/RECOVERY.md`, `workflow/CLOSE.md`, `workflow/USER_STOP.md`, `tools/router.py`, `tools/state_contract.py`, `tools/execution_contract.py`, `tools/recovery_contract.py`, `tools/close_contract.py`, router/state/Close/ChatGPT/Codex delivery tests, package manifests, Skill/SessionStart hook and ChatGPT bootstrap templates.

Selected attack lenses exercised:

1. stale commit/blob/path/result/review identity — result and review binding paths;
2. Close/finalization/end-of-approved-scope — DONE fast path, JIT terminal interaction and Close helpers;
3. router precedence/conflicting obligations — Task Board Research, review/finalization, JIT and pre-execution/Board dispatch;
4. plugin/install/update/SessionStart/bootstrap drift — installed-root, router validation, Skill/hook and delivery tests.

No `audit/*` branches, other swarm reports, GitHub Issues or PR comments were inspected before freezing the finding set.

## Confidence and limitations

Confidence is high for the source-level counterexamples because each follows a direct accepted validation/routing path in the exact audited code.

Full execution of newly invented selector probes could not be completed in the available remote runtime: the connected Desktop Commander host had exhausted its monthly execution quota. Findings therefore rely on exact-commit source/contract falsification plus limited local exception-class reasoning rather than an executed fresh clone.

During immutable-commit verification, the GitHub commit connector returned the merge commit's diff, including snippets from historical implementation evidence/review paths. Those unsolicited snippets were not used as an audit checklist and did not supply any of the seven findings. The independent finding set was frozen before any optional historical comparison.

## Post-freeze historical comparison

Not performed.
