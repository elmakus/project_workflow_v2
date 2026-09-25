# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

Five material defects were independently demonstrated against the exact immutable subject `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`. Findings were frozen before reading any prior `audit/*` report; no historical-audit comparison was used to discover them.

## Material findings

### F1 — GREEN review can finalize content that no longer matches the declared reviewed blob

Affected workflow contract/invariant:
PWV2-REQ-034; `workflow/REVIEW.md` exact immutable review subject; `workflow/ROUTER.md` exact-GREEN and stale-binding fail-closed rules; `workflow/STATE.md` current exact result/dependency identity.

Expected behavior:
Before a GREEN attempt authorizes post-review finalization, the production router must establish that the current durable result bytes are the exact Git blob identified by the Card result locator and review subject. A same-path content change after review must require a new exact attempt or fail closed.

Actual behavior:
`tools/router.py` reads and parses the current result file, but constructs `current_subject` only from the Task Board's declared `path/commit/blob`. It never hashes the current file or verifies the declared commit/blob against repository content. If the result file changes while the locator remains unchanged, `review_subject(attempt) == current_subject` still holds and GREEN routes to `post_review_finalization`.

Minimal reproduction:
Create an in-progress Card with REQUIRED review, a result locator declaring blob B, and a GREEN review attempt for blob B. Then edit only the result file at the same path while leaving the Board locator and review subject untouched. `select_route(...)` still returns `route/post_review_finalization`.

Why this is materially load-bearing:
The exact-subject review gate can authorize terminal finalization of implementation content that was never reviewed. This is a direct review bypass, not merely stale metadata display.

Defect class / likely siblings:
Stale immutable-identity trust / fail-open on declared locator metadata. The same pattern is present in READY dependency refresh: dependency equality is checked against Board metadata, but the current predecessor result bytes are not verified against the declared blob.

Existing tests that failed to catch it:
`test_changed_result_after_terminal_review_requires_new_attempt` changes the Board's declared blob, so the mismatch is visible. `test_ready_card_stale_dependency_fails_closed_before_launch` changes both Board identity and file content. Neither covers content-only drift with unchanged locator metadata.

Reproduction artifact, if any:
`audits/swarm/k7m2v9q4x1n8c5r0t6p3b2d9/repros/repro_findings.py::f01_result_content_swap_after_green`

### F2 — GREEN review does not bind an immutable acceptance surface

Affected workflow contract/invariant:
PWV2-REQ-021, PWV2-REQ-038; `workflow/REVIEW.md` requirement that each attempt bind one exact acceptance surface; exact final subject/acceptance coverage semantics.

Expected behavior:
Changing the Task Card acceptance/tests after a GREEN implementation review must invalidate that review coverage or require a new exact attempt for the changed acceptance surface.

Actual behavior:
A Card review stores `[acceptance] class = "task_card", path = "..."` with no commit/blob identity. During routing the current Task Card is reparsed, but no immutable acceptance key is compared with the attempt. The same GREEN attempt therefore remains valid after material acceptance or required-test changes at the same Task Card path.

Minimal reproduction:
Create a REQUIRED-review Card result plus GREEN attempt. After GREEN, edit only the Task Card's `Acceptance` or `Required tests/readback` field, keeping its path unchanged. `select_route(...)` still returns `route/post_review_finalization`.

Why this is materially load-bearing:
A reviewer may approve one acceptance contract while finalization occurs under a different one. The gate therefore does not prove the result satisfies the acceptance surface that is current at completion time.

Defect class / likely siblings:
Stale acceptance identity / path-only mutable locator. Similar risk applies anywhere review coverage is represented by a mutable path without immutable content identity.

Existing tests that failed to catch it:
Review lifecycle tests keep the Task Card unchanged across review and finalization. There is no regression that mutates acceptance after GREEN while preserving the acceptance path.

Reproduction artifact, if any:
`audits/swarm/k7m2v9q4x1n8c5r0t6p3b2d9/repros/repro_findings.py::f02_acceptance_surface_changes_after_green`

### F3 — Research can return to a different semantic owner and bypass issue alignment

Affected workflow contract/invariant:
PWV2-REQ-049; `workflow/RESEARCH.md` exact durable return ownership and “Research never selects a different target by itself”; `workflow/INTAKE.md` issue-alignment boundary; `workflow/ROUTER.md` active/completed Research -> exact return owner and issue-without-response -> alignment stop.

Expected behavior:
`origin_role` and `return_target` must be mutually consistent. In particular, Intake-origin diagnosis Research must return to Intake before any later stage can run.

Actual behavior:
`validate_research` validates `origin_role` and `return_target` independently but never requires their pairing. A record with `origin_role = "intake"` and `return_target = "definition"` is valid. Because `tools/router.py` processes completed Research before Intake, it immediately routes that record to Definition and never evaluates the pending issue-alignment obligation.

Minimal reproduction:
Attach an active/pending issue Intake record and a completed Research record with the same repair subject, `origin_role = "intake"`, but `return_target = "definition"`. The production selector returns `route/definition` rather than the Intake-owned prior-art/alignment obligation.

Why this is materially load-bearing:
A schema-valid contradictory Research record can jump across a mandatory human repair-authorization boundary and select an illegal workflow transition.

Defect class / likely siblings:
Contradictory state accepted / return-owner integrity gap. Execution-owned Research has the same structural weakness because execution origin roles and execution return-target prefixes are not paired.

Existing tests that failed to catch it:
`test_active_and_completed_research_route_to_exact_owner` exercises only matching origin/return pairs. State-contract tests validate legal values and source accounting, not role-target consistency.

Reproduction artifact, if any:
`audits/swarm/k7m2v9q4x1n8c5r0t6p3b2d9/repros/repro_findings.py::f03_research_owner_mismatch_bypasses_intake`

### F4 — The documented Close -> end_of_scope_stop transition is unreachable through the production router

Affected workflow contract/invariant:
PWV2-REQ-070; `workflow/ROUTER.md` implemented route “Close -> ... then end-of-scope stop”; `workflow/CLOSE.md` true-end semantics; requirement that every real stop load `workflow/USER_STOP.md`.

Expected behavior:
Once Close proves durable approved-scope completion with no authorized obligation remaining, the production routing path must be able to emit a real `end_of_scope_stop` and load the stop formatter.

Actual behavior:
`tools/router.py` routes an all-DONE Board to `route/close` unconditionally. It does not import or call `close_continuation`, read any durable Close-completion state, or expose an input by which Close completion can become a `RouteResult` stop. Re-running the selector on the same terminal durable state returns `close` again. `tools/close_contract.py` can independently return the string `end_of_scope_stop`, but that helper is not connected to the production selector or USER_STOP loading.

Minimal reproduction:
Make the fixture Card DONE with a valid result. Call `select_route(...)` twice without changing state: both calls return `route/close`. Separately, `close_continuation(approved_scope_durably_complete=True, next_authorized_obligation=False, explicit_authorization_gate_due=False)` returns `end_of_scope_stop`, demonstrating the disconnected semantic branch.

Why this is materially load-bearing:
The canonical selector cannot represent the documented terminal transition. Completion must therefore be inferred manually/out-of-band or Close repeats indefinitely, allowing runtime behavior to become hidden authority over when the workflow actually ends.

Defect class / likely siblings:
Unreachable documented transition / helper-router parity gap / finalization state integration gap.

Existing tests that failed to catch it:
`test_all_terminal_cards_route_to_close_not_directly_to_stop` proves only the first half. `test_end_of_scope_requires_durable_completion` tests the helper in isolation. No end-to-end test proves a terminal durable state can progress through the production selector to a real stop.

Reproduction artifact, if any:
`audits/swarm/k7m2v9q4x1n8c5r0t6p3b2d9/repros/repro_findings.py::f04_close_stop_is_disconnected`

### F5 — Terminal GREEN review can reference nonexistent verdict evidence and still unblock completion

Affected workflow contract/invariant:
PWV2-REQ-036; `workflow/REVIEW.md` durable verdict evidence for terminal attempts; `workflow/AUTHORITY.md` fail-closed rule for missing required references.

Expected behavior:
A terminal GREEN/RED attempt must point to durable, readable, correctly scoped evidence. Missing evidence must fail closed before a verdict can affect Card completion.

Actual behavior:
`validate_review` requires only that `evidence_path` be a non-empty safe relative string for terminal verdicts. It neither constrains the path to the workstream evidence root nor verifies that the file exists. `tools/router.py` reads the attempt but never dereferences `evidence_path`. A GREEN attempt naming a nonexistent file therefore routes to `post_review_finalization`.

Minimal reproduction:
Create a valid REQUIRED-review result and GREEN attempt whose `evidence_path` is a nonexistent relative file. Do not create that evidence file. `select_route(...)` still returns `route/post_review_finalization`.

Why this is materially load-bearing:
The blocking review gate can become terminal without the durable evidence the workflow requires for recovery/auditability, and missing required evidence does not fail closed.

Defect class / likely siblings:
Missing reference dereference / under-validated evidence locator. Review-attempt locators themselves are also path-only and rely on writer discipline for append-only immutability.

Existing tests that failed to catch it:
Terminal review tests create the evidence file when constructing GREEN/RED attempts. State validation tests check only non-empty terminal `evidence_path`; no test removes the referenced file or points it outside the workstream evidence directory.

Reproduction artifact, if any:
`audits/swarm/k7m2v9q4x1n8c5r0t6p3b2d9/repros/repro_findings.py::f05_missing_terminal_review_evidence`

## Non-blocking observations

- Intake's `diagnosis_prior_art_result` is an opaque string and is not structurally tied to a retained Research artifact. The intended “binding survives Research-slot reuse” model may justify an opaque token, but recovery currently depends on transition discipline rather than a validator-verifiable evidence identity.
- Review-attempt locators in the Task Board are path-only. Git history can preserve old content, but current-state validation alone cannot prove append-only attempt immutability if an attempt file is rewritten in place.
- The result/dependency identity defect in F1 is broader than implementation review: launch refresh reads current predecessor result files but checks exactness only against duplicated locator metadata.

## Coverage

The audit remained bound to `elmakus/project_workflow_v2@4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`; moving `main` was not used as the audit subject. The exact commit tree was enumerated while excluding `audits/*` during blind discovery.

Inspected production semantics included `tools/router.py`, `tools/state_contract.py`, `tools/recovery_contract.py`, `tools/review_contract.py`, `tools/close_contract.py`, `tools/execution_contract.py`, and the matching workflow modules for Router, State, Authority, Intake, Research, Review, GitHub Issues and Close. Relevant requirements, templates, fixtures and regression tests were inspected to establish intended invariants and missing cases.

Selected attack lenses exercised:
- review independence/bypass/result mutation: F1, F2, F5;
- Close/finalization/end-of-approved-scope: F4;
- Research/Intake/tracker/external-side-effect recovery: F3 plus tracker/close contract inspection;
- path traversal/locator safety/cross-workstream binding: F1, F2, F5 and locator validation review.

The repository's existing tests were inspected, including router, state, review, recovery and Close tests. No prior audit report was read before findings were frozen.

## Confidence and limitations

Confidence is high for F1, F2, F3 and F5 because each follows a direct production validation/routing path with no semantic inference beyond the documented invariant. Confidence is high-to-moderate for F4: the helper clearly implements the terminal decision, but the production selector has no executable or durable integration path to surface that decision as a real stop.

The reproduction script was constructed against the exact repository fixture/API exposed by the audited commit, but an isolated execution runner for the exact checkout was unavailable during this audit session, so the new repro script itself was not executed here. Existing repository tests were inspected but not rerun locally. No post-freeze historical audit comparison was performed.
