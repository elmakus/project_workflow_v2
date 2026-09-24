# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

Five material defects were independently demonstrated from the exact subject
`4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`.

## Material findings

### F1 — A JIT trigger can be consumed without materializing its downstream Card, allowing Close to absorb unfinished approved work

- Affected workflow contract/invariant:
  - `workflow/EXECUTION_PREP.md`: predecessor-dependent work remains a JIT trigger until its stable downstream Card can be materialized; lifecycle is `waiting -> satisfied -> consumed`.
  - `workflow/STATE.md`: Task Board owns bounded predecessor-dependent JIT triggers.
  - `workflow/CLOSE.md`: Close may stop only when no already-authorized obligation remains.
- Expected behavior:
  - `consumed` must prove that the trigger was actually consumed by durable downstream work (normally a materialized Card), or the trigger must remain non-terminal and route back to Execution Prep.
- Actual behavior:
  - `validate_board()` treats `satisfied` and `consumed` identically: both require only a DONE predecessor with a result.
  - A `consumed` trigger has no required downstream-Card binding or other consumption proof.
  - `tools/router.py` does not inspect `jit_triggers` after board validation. If all existing Cards are DONE, it routes to `close`.
  - `tools/close_contract.py` has no JIT/Task-Board input that can reconstruct the missing downstream materialization.
- Minimal reproduction:
  1. Start from the canonical router fixture.
  2. Mark the only Card DONE and give it a result.
  3. Add a JIT trigger with `after_card` equal to that DONE Card and `state = "consumed"`.
  4. Do not create any downstream Card.
  5. `validate_board()` accepts the state and `select_route()` returns `route/close`.
- Why this is materially load-bearing:
  - An authorized predecessor-dependent unit of work can disappear from durable state and the workflow can enter Close with no executable representation of that work.
- Defect class / likely siblings:
  - JIT lifecycle lacks a durable consumed-by/materialization invariant.
  - A `satisfied` trigger with no downstream Card is also invisible to the production selector and can be routed into Close when all current Cards are DONE.
- Existing tests that failed to catch it:
  - `tests/test_state_contract.py::test_jit_trigger_preserves_predecessor_boundary_without_placeholder_card` exercises `waiting` and `satisfied`, but not a `consumed` trigger without a downstream Card.
  - `tests/test_router.py` contains no `jit_triggers` case.
  - `tests/test_close_contract.py` contains no JIT/Task-Board case.
- Reproduction artifact, if any:
  - `audits/swarm/ze8eya3df1xsxsb7q93smiac/repros/jit_consumed_without_card.py`

### F2 — DONE status bypasses the REQUIRED review gate

- Affected workflow contract/invariant:
  - `workflow/REVIEW.md`: for REQUIRED/activated RECOMMENDED review, no attempt, pending, in-progress, or RED blocks terminal Card completion; only exact GREEN permits deterministic finalization.
  - `workflow/STATE.md`: the same blocking rule is part of durable-state semantics.
- Expected behavior:
  - A Card whose stable contract says `Review requirement: required` cannot be accepted as terminal DONE unless exact current GREEN review history is proven.
- Actual behavior:
  - `validate_board()` validates a DONE Card only by requiring a result locator. It does not read the stable Card to learn its review requirement and does not require/validate review history as a terminal invariant.
  - `select_route()` only runs result/review logic for `in_progress` Cards. When the same Card is already marked `done`, the router skips the Card contract, result, and review attempts entirely; if all Cards are DONE it returns `route/close`.
- Minimal reproduction:
  1. Use one Card with a complete stable contract containing `Review requirement: required`.
  2. Give the Card a valid-looking result locator/result.
  3. Provide no review attempt.
  4. Set Card status directly to `done`.
  5. `select_route()` returns `route/close` instead of Recovery/review.
- Why this is materially load-bearing:
  - A durable state mutation can bypass the independent implementation-review safety gate and advance directly toward Close.
- Defect class / likely siblings:
  - Terminal state is trusted as an assertion rather than re-derived from terminal invariants.
  - The same bypass applies to DONE Cards with pending, RED, stale, or otherwise insufficient review history because that history is not loaded on the DONE path.
- Existing tests that failed to catch it:
  - REQUIRED-review router tests keep the Card `in_progress`.
  - `test_all_terminal_cards_route_to_close_not_directly_to_stop` explicitly installs `review_requirement = "none"` before changing status to DONE.
- Reproduction artifact, if any:
  - `audits/swarm/ze8eya3df1xsxsb7q93smiac/repros/router_adversarial_repros.py` (`repro_done_bypasses_required_review`)

### F3 — READY dependency refresh trusts declared commit/blob tuples without verifying the actual dependency bytes

- Affected workflow contract/invariant:
  - `workflow/EXECUTION_PREP.md`: READY launch refresh must verify exact dependency result path + immutable commit/blob identity.
  - `workflow/STATE.md`: missing/stale or same-path-changed dependency inputs fail closed before execution.
- Expected behavior:
  - If a DONE predecessor result changes at the same path while the Task Board/Card still claim the old commit/blob identity, launch refresh must detect the mismatch and fail closed.
- Actual behavior:
  - `refresh_ready_card()` compares the dependency tuple declared in the Task Card against the tuple declared in DONE Board state.
  - After tuple equality, it merely `read_text()`s the dependency path. It never resolves the claimed commit, hashes the file, or verifies that the bytes at the path equal the claimed blob.
  - Therefore both durable records can retain the same stale tuple while the dependency file changes, and the READY Card still routes to `execution_prep`.
- Minimal reproduction:
  1. Create a DONE predecessor with result `path=P, commit=A, blob=B`.
  2. Create a READY Card whose dependency is exactly `P@A:B`.
  3. Initial launch refresh returns `execution_prep`.
  4. Change the bytes at `P` while leaving both declared tuples unchanged.
  5. Launch refresh still returns `execution_prep`.
- Why this is materially load-bearing:
  - A downstream Card can execute against dependency content that is not the immutable result it was authorized to consume.
- Defect class / likely siblings:
  - Git identity is treated as self-declared metadata rather than verified identity.
  - The same structural risk exists anywhere the selector compares claimed commit/blob strings without resolving the Git object, including current result/review and planning subjects.
- Existing tests that failed to catch it:
  - `test_ready_card_stale_dependency_fails_closed_before_launch` changes the predecessor's declared Board commit/blob, creating a tuple mismatch. It does not test same-path changed bytes while both declared tuples stay stale.
- Reproduction artifact, if any:
  - `audits/swarm/ze8eya3df1xsxsb7q93smiac/repros/stale_dependency_blob.py`

### F4 — A GREEN implementation review remains valid after its Task Card acceptance surface changes

- Affected workflow contract/invariant:
  - `workflow/REVIEW.md`: each review attempt binds one exact acceptance surface, normally the stable Task Card.
  - `workflow/EXECUTION_PREP.md`: an in-progress Card must not be silently rewritten through JIT refinement.
- Expected behavior:
  - If the acceptance/tests/scope of the Task Card change after a GREEN attempt, the old attempt no longer proves the current acceptance surface; the state must fail closed or require a new exact review.
- Actual behavior:
  - `validate_review()` represents task-card acceptance only as `class + path`; it has no immutable commit/blob/content identity.
  - On the active-result path the router reparses the current Card, but uses it only to obtain `review_requirement`.
  - Review freshness compares only the result subject. If the result tuple is unchanged and the last verdict is GREEN, the router returns `post_review_finalization` even when the Card's acceptance text changed after review.
- Minimal reproduction:
  1. Create an in-progress review-required Card, a result, and exact GREEN attempt.
  2. Confirm route is `post_review_finalization`.
  3. Change only the Task Card's `Acceptance` (or required tests/readback) text at the same path.
  4. Route remains `post_review_finalization`.
- Why this is materially load-bearing:
  - Finalization can rely on a review whose reviewer never evaluated the currently binding acceptance criteria.
- Defect class / likely siblings:
  - Path-only acceptance identity is not exact content identity.
  - Any post-review mutation of scope/acceptance/tests at the same Task Card path is invisible to review freshness.
- Existing tests that failed to catch it:
  - Review freshness tests change the result blob tuple, not the Task Card acceptance content.
  - No router test mutates the Task Card after GREEN.
- Reproduction artifact, if any:
  - `audits/swarm/ze8eya3df1xsxsb7q93smiac/repros/router_adversarial_repros.py` (`repro_changed_acceptance_reuses_green_review`)

### F5 — Missing result and terminal-review evidence files do not block GREEN finalization

- Affected workflow contract/invariant:
  - `workflow/EXECUTION.md`: an accepted semantic result records one or more durable evidence refs and verified tests/readback.
  - `workflow/REVIEW.md`: terminal attempts keep durable verdict evidence.
- Expected behavior:
  - Before result reconciliation/review finalization, evidence referenced as durable proof must exist and be readable/bound to the selected workstream; missing proof is incomplete state and must fail closed.
- Actual behavior:
  - `parse_card_result()` validates only the syntax/location of result evidence refs.
  - `validate_review()` validates only that terminal `evidence_path` is non-empty and syntactically safe.
  - `select_route()` never opens either the result evidence refs or terminal review evidence before returning `post_review_finalization`.
  - Deleting both referenced evidence files leaves routing unchanged.
- Minimal reproduction:
  1. Build a valid in-progress review-required Card with a result, result evidence, GREEN review attempt, and review evidence.
  2. Confirm `post_review_finalization`.
  3. Delete the result-evidence file and terminal-review-evidence file while retaining their references.
  4. Route still returns `post_review_finalization`.
- Why this is materially load-bearing:
  - A terminal GREEN path can proceed after its durable proof has disappeared, defeating recovery/audit integrity and turning evidence into an unchecked string assertion.
- Defect class / likely siblings:
  - Referenced proof is syntax-checked but not dereferenced.
  - Similar string-only terminal proof patterns should be checked in Plan Review and Research/return reconciliation.
- Existing tests that failed to catch it:
  - Router helpers create evidence files for the happy path.
  - No router test removes or omits referenced evidence before reconciliation/finalization.
- Reproduction artifact, if any:
  - `audits/swarm/ze8eya3df1xsxsb7q93smiac/repros/router_adversarial_repros.py` (`repro_missing_evidence_still_finalizes`)

## Non-blocking observations

- Close semantics are split between `tools/router.py` and `tools/close_contract.py`. I did not promote the mere absence of a direct `end_of_scope_stop` branch in the router to a material finding because the module boundary could be intentional; F1 is narrower and demonstrates a concrete durable obligation that neither the board validator nor the executable Close oracle binds to downstream materialization.
- Several state records use path/string evidence bindings rather than immutable content identity. Only cases above with a concrete routing/finalization consequence were promoted to material findings.

## Coverage

The audit remained bound to subject commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045` for product semantics.

Inspected/test-designed surfaces included:

- `workflow/ROUTER.md`
- `workflow/STATE.md`
- `workflow/EXECUTION_PREP.md`
- `workflow/EXECUTION.md`
- `workflow/REVIEW.md`
- `workflow/RECOVERY.md`
- `workflow/CLOSE.md`
- `tools/router.py`
- `tools/state_contract.py`
- `tools/execution_contract.py`
- `tools/recovery_contract.py`
- `tools/close_contract.py`
- `tests/test_router.py`
- `tests/test_state_contract.py`
- `tests/test_execution_contract.py`
- `tests/test_recovery_contract.py`
- `tests/test_close_contract.py`
- exact router/state fixtures needed to construct negative-space reproductions.

Selected attack lenses exercised:

1. helper vs documented semantics / parity drift / negative space — F1, F2, F5;
2. Close / finalization / end-of-approved-scope — F1, F2;
3. stale commit/blob/path/result/review identity — F3, F4, F5;
4. Task Board / READY / active / DONE / JIT-trigger lifecycle — F1, F2, F3.

Sibling/negative-space variants were checked in code against the existing tests, especially DONE-vs-in-progress review handling, declared-tuple-vs-actual-content dependency changes, and evidence existence.

## Confidence and limitations

Confidence is high in the code-path demonstrations: each finding follows directly from the production selector/validator behavior at the exact subject and is paired with a non-mutating reproduction script that imports the real production helpers.

Execution limitations:

- I attempted to run the exact checkout on the connected Tower, but the Desktop Commander monthly usage limit prevented execution.
- I then attempted a temporary container checkout of the exact public commit, but the container cannot resolve external network hosts.
- Therefore the preserved reproduction scripts were not executed inside this session. They are designed to run from the exact subject checkout (or this audit branch) and invoke `tools.router.select_route` directly.
- No product code was modified to construct a reproduction.

## Post-freeze historical comparison

Not performed. The independently frozen finding set was kept blind; no `audit/*` branches, swarm reports, Issues/PR diagnosis threads, or historical workstream evidence/review narratives were inspected for known-issue comparison.
