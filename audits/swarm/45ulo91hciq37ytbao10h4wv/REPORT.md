# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Router trusts declared Git-blob metadata instead of the reviewed bytes

- Affected workflow contract/invariant: `workflow/REVIEW.md` exact immutable Git content subject; `workflow/STATE.md` exact-current-result review/finalization and recovery truth.
- Expected behavior: if the bytes at the current Card result change after the GREEN attempt was frozen, the old review must not authorize finalization. The current result must be proven to be the declared immutable `path + commit + blob` subject, otherwise a new attempt or Recovery is required.
- Actual behavior: `tools/router.py` reads the current filesystem result text and parses it, but computes `current_subject` only from the Board-declared result locator through `exact_result_subject()`. Neither the router nor `parse_card_result()` verifies the actual result bytes against the declared blob/commit. A post-review content mutation with unchanged Board/review metadata therefore still reaches `post_review_finalization`.
- Minimal reproduction: `repros/f1_result_blob_mutation.py` first binds Board and GREEN review metadata to the Git-blob SHA of the original result bytes, then mutates the result file without changing those locators. The production control path still compares the two unchanged declarations and selects finalization.
- Why this is materially load-bearing: an exact-subject independent review can be reused for bytes it never reviewed, defeating the integrity boundary between durable result, review, and terminal Card completion.
- Defect class / likely siblings: declared immutable identities are treated as self-authenticating metadata. The same class is relevant to frozen/approved planning subjects because Plan Review compares declared Git identities rather than re-hashing or reading the exact Git object.
- Existing tests that failed to catch it: router stale-result tests mutate the Board `blob` field and therefore exercise metadata mismatch, not same-locator content mutation.
- Reproduction artifact, if any: `repros/f1_result_blob_mutation.py`.

### F2 — Terminal review evidence is neither bound to the workstream nor dereferenced

- Affected workflow contract/invariant: `workflow/REVIEW.md` requires durable verdict evidence for terminal attempts; `workflow/STATE.md` makes terminal review history part of the exact blocking gate.
- Expected behavior: GREEN/RED terminal evidence must identify an allowed durable evidence artifact that actually exists; missing or unrelated evidence must fail closed and cannot authorize post-review finalization.
- Actual behavior: `validate_review()` requires only a non-empty safe-relative `evidence_path` for GREEN/RED. It does not require the path to be workstream-local and the router never reads that path. A GREEN review whose evidence is changed to a nonexistent `ghost-review-evidence.md` remains valid and reaches `post_review_finalization`.
- Minimal reproduction: create the existing required-review fixture and GREEN attempt, replace only its evidence path with `ghost-review-evidence.md`, then run `select_route()`; the review TOML still validates and GREEN remains finalizable.
- Why this is materially load-bearing: durable evidence is the audit trail for the independent verdict. A terminal gate can currently be satisfied by an arbitrary string naming no artifact at all.
- Defect class / likely siblings: non-empty locator syntax is accepted without existence/binding verification. Card-result evidence refs are similarly parsed as workstream-local strings without being dereferenced by `parse_card_result()`.
- Existing tests that failed to catch it: `test_review_terminal_evidence_and_append_only_history` rejects only an empty terminal evidence path; it does not test nonexistent or out-of-workstream paths.
- Reproduction artifact, if any: `repros/f2_review_evidence_missing.py`.

### F3 — `done` Board state bypasses REQUIRED review and RED correction

- Affected workflow contract/invariant: `workflow/REVIEW.md` blocking lifecycle; `workflow/STATE.md` requires no-attempt/pending/in-progress/RED to block terminal completion and only exact GREEN to permit deterministic finalization.
- Expected behavior: a Card marked `done` while a REQUIRED review is absent, pending, in-progress, or RED is contradictory durable state and must fail closed (or be routed back to the unresolved review/correction owner), never proceed to Close.
- Actual behavior: `validate_board()` requires a `done` Card only to have a result locator. It does not read the stable Task Card or review history. When no Card is active/READY/blocked, `tools/router.py` routes an all-`done` Board directly to `close`, without reading the Card, result, or review attempts. Thus both `done + pending REQUIRED review` and `done + RED REQUIRED review` bypass their blocking gates.
- Minimal reproduction: materialize a required-review result and pending/RED attempt with existing test helpers, change only Card status from `in_progress` to `done`, then select a route. The all-terminal branch selects `route/close`.
- Why this is materially load-bearing: a single Board status mutation can erase the precedence of independent review or RED correction and prematurely enter final integration/closure.
- Defect class / likely siblings: cross-record state invariants are enforced only while a Card is `in_progress`; terminal status is trusted without proving the prerequisites that make it legal.
- Existing tests that failed to catch it: `test_all_terminal_cards_route_to_close_not_directly_to_stop` deliberately uses a Card whose review requirement is `none`; required-review terminal contradictions are not covered.
- Reproduction artifact, if any: `repros/f3_done_bypasses_review.py`.

### F4 — A satisfied JIT trigger is ignored when current Cards are DONE

- Affected workflow contract/invariant: `workflow/EXECUTION_PREP.md` JIT lifecycle (`waiting -> satisfied -> consumed`) and the rule that a satisfied predecessor-dependent trigger materializes the newly knowable downstream Card; `workflow/CLOSE.md` forbids completion while an already-authorized obligation remains.
- Expected behavior: once a JIT trigger is `satisfied` by its DONE predecessor/result, the router must keep Execution Prep/JIT materialization ahead of Close until that trigger is consumed into the downstream stable Card.
- Actual behavior: `validate_board()` accepts a `satisfied` trigger when its predecessor is DONE with a result, but the selector never consults `jit_triggers` after validation. With all current Cards `done`, the router takes the all-terminal branch and returns `route/close` even though a satisfied, unconsumed JIT obligation remains.
- Minimal reproduction: make the fixture Card `done` with a durable result and append a `satisfied` trigger whose `after_card` is that Card. Board validation succeeds; route selection reaches Close.
- Why this is materially load-bearing: approved predecessor-dependent work can disappear from executable routing exactly when its contract becomes knowable, allowing premature Close/end-of-scope reconciliation.
- Defect class / likely siblings: Task Board trigger state is validated structurally but absent from obligation precedence/selection.
- Existing tests that failed to catch it: the state-contract trigger test checks that `satisfied` requires a DONE predecessor result, but there is no router test asserting that a satisfied trigger preempts Close.
- Reproduction artifact, if any: `repros/f4_satisfied_jit_routes_close.py`.

### F5 — SessionStart accepts a marker-preserving truncated router as canonical authority

- Affected workflow contract/invariant: `skills/project_workflow_v2/SKILL.md` requires missing, malformed, ambiguous, or escaping installed router authority to fail closed; the SessionStart hook is the thin Codex bootstrap for bundled canonical semantics.
- Expected behavior: an installed `workflow/ROUTER.md` that has lost its routing semantics must be classified malformed and emit the blocking package-error context rather than advertise valid workflow authority.
- Actual behavior: `canonical_router()` validates router content only by requiring two substrings: the router heading and `Production selector: tools/router.py`. A two-line file containing just those markers passes and `build_context()` says the package is enabled with a canonical bundled router.
- Minimal reproduction: replace only the temporary copied router with the two accepted marker lines and invoke the real hook with matching `PLUGIN_ROOT`; the non-blocking enabled context is emitted.
- Why this is materially load-bearing: silent package truncation/corruption can remove all routing precedence and safety semantics while the bootstrap explicitly tells the runtime that canonical authority is healthy.
- Defect class / likely siblings: integrity is inferred from sentinel presence rather than structural or manifest-bound package integrity.
- Existing tests that failed to catch it: `test_missing_and_malformed_router_fail_closed` uses `not a V2 router`, which removes both sentinels; marker-preserving corruption is not tested.
- Reproduction artifact, if any: `repros/f5_sessionstart_truncated_router.py`.

## Non-blocking observations

No additional advisory item was promoted. The Close helper surface was inspected directly; the material Close-related counterexample retained in the frozen set is F4, where router precedence enters Close despite a satisfied JIT obligation.

## Coverage

All repository reads used the immutable subject `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`. Inspection covered canonical router/state/review/execution-prep/Close contracts; production router, state, execution, review, recovery and Close helpers; Task Board and router fixtures; relevant router/state/Close/delivery tests; Codex plugin manifest/marketplace, Skill, SessionStart hook and bootstrap test; and ChatGPT bootstrap prompts/requirements needed for parity context.

The four selected attack lenses were all exercised: bootstrap integrity (F5), Close/end-of-scope interaction (F4), review/result integrity and bypass (F1-F3), and Task Board/JIT lifecycle (F3-F4). Negative-space tests were inspected specifically for same-locator mutation, nonexistent evidence, terminal contradictory review state, satisfied-trigger routing, and marker-preserving router corruption.

## Confidence and limitations

Confidence is high in the demonstrated control-flow defects because each counterexample follows production validation/selector branches directly and is preserved as a non-mutating repro script against existing test helpers. However, this audit environment could not execute the scripts: the local container could not resolve GitHub for checkout, and the authorized Desktop Commander reported its monthly quota exhausted and explicitly instructed not to retry. Existing tests were therefore inspected rather than rerun here.

Blind-discovery limitation: an exact-commit metadata fetch unexpectedly returned diff snippets that included historical workstream evidence/review text before the finding set was frozen. Those snippets were not used to generate, validate, add, remove, or rank any finding. No `audit/*` branch, swarm report, GitHub Issue/PR comment, or post-freeze historical comparison was inspected.
