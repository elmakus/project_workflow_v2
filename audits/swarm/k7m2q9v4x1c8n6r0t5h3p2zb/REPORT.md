# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — DONE state bypasses result and required-review validation before Close

- Affected workflow contract/invariant: workflow/STATE.md and workflow/REVIEW.md require REQUIRED/activated RECOMMENDED review to block terminal completion until exact GREEN, while workflow/ROUTER.md requires invalid/missing/stale/contradictory binding to fail closed and workflow/CLOSE.md assumes accepted terminal truth.
- Expected behavior: A Card may reach Close only after its durable result and all required review state are validated. A done Card with no review attempt, a pending/RED review, or an unreadable/stale result must route to review/recovery rather than Close.
- Actual behavior: validate_board() only requires a result locator when status = "done"; it does not read the Task Card, result artifact, or review attempts. After active/blocked/READY checks, select_route() returns route/close when every Card is done, again without reading those artifacts. Merely flipping the Board status to done can therefore bypass required review and result integrity.
- Minimal reproduction: Start from the router fixture, install a valid Task Card with Review requirement: required and a result locator, leave review_attempts empty, change the Card status from in_progress to done, then call select_route(). The production path returns route/close.
- Why this is materially load-bearing: It permits workflow finalization/integration entry without the blocking independent-review gate and without proving the terminal result is valid.
- Defect class / likely siblings: Terminal-state trust without semantic validation; siblings include done plus pending/RED review, path-only/missing result identity, or a result file that disappeared after Board mutation.
- Existing tests that failed to catch it: test_all_terminal_cards_route_to_close_not_directly_to_stop uses a no-review result. Required-review lifecycle tests keep the Card in_progress, so no test combines done with an unsatisfied review obligation.
- Reproduction artifact, if any: repros/reproduce_findings.py (F1).

### F2 — Immutable result/dependency blob identities are trusted as metadata, not verified against bytes

- Affected workflow contract/invariant: workflow/STATE.md, workflow/EXECUTION_PREP.md, and workflow/RECOVERY.md require exact path+commit+blob identity and explicitly require same-path-changed dependency inputs to fail closed; GREEN finalization must cover the exact still-current result.
- Expected behavior: Before launch or GREEN finalization, the selector must establish that the current artifact bytes at the named path are the bytes identified by the claimed immutable Git blob/commit.
- Actual behavior: READY dependency refresh checks only that the Card's (path, commit, blob) tuple equals metadata stored on a DONE predecessor, then merely reads the current path. Active-result recovery similarly reads/parses the current result but derives the current review subject from Board metadata; no code hashes or resolves the current artifact against the claimed blob/commit. If bytes change in place while metadata remains unchanged, launch/finalization still proceeds.
- Minimal reproduction: (a) Create a READY Card whose dependency tuple matches a DONE predecessor; mutate only the dependency result file bytes, leaving both locators unchanged; select_route() still returns execution_prep. (b) Create an in_progress result with exact GREEN review; mutate only the result file bytes while keeping Board and review subject metadata unchanged; the selector still returns post_review_finalization.
- Why this is materially load-bearing: Exact immutable identity is the basis for stale-input rejection, review coverage, recovery truth, and no-replay semantics. Metadata-only equality lets changed content masquerade as the reviewed/depended-on blob.
- Defect class / likely siblings: Unverified Git-object identity. Likely siblings are every transition that compares commit/blob strings without resolving the named Git object/path bytes.
- Existing tests that failed to catch it: test_ready_card_stale_dependency_fails_closed_before_launch changes the Board commit/blob metadata together with file content, so it tests locator disagreement rather than same-path byte drift. test_changed_result_after_terminal_review_requires_new_attempt likewise changes Board blob metadata instead of current result bytes.
- Reproduction artifact, if any: repros/reproduce_findings.py (F2a/F2b).

### F3 — READY Card with a durable result is relaunched instead of recovered from result truth

- Affected workflow contract/invariant: workflow/STATE.md, workflow/EXECUTION.md, and workflow/RECOVERY.md say a durable valid semantic result is recovery truth and prevents implementation replay solely because runtime state disappeared.
- Expected behavior: If a selected Card already carries a valid durable result, continuation must start from result reconciliation/review/finalization, regardless of stale mutable execution status; it must not prepare the implementation for launch again.
- Actual behavior: validate_board() permits a result locator on a ready Card. select_route() considers durable results only inside the in_progress branch. The later single-READY branch calls refresh_ready_card() and returns route/execution_prep without checking card["result"].
- Minimal reproduction: Convert the fixture Card to ready, give it a valid stable Card/authority plus a valid durable result locator/artifact, and invoke select_route(). It returns route/execution_prep, not result_reconciliation.
- Why this is materially load-bearing: A stale status bit can cause already-completed implementation to be replayed, violating the durable-recovery guarantee and potentially duplicating mutations.
- Defect class / likely siblings: Result-recovery precedence is conditional on mutable Card status. planned/blocked result-bearing states deserve the same negative-space scrutiny.
- Existing tests that failed to catch it: Result-reconciliation tests use in_progress; READY tests use Cards without durable results. No test crosses the two state dimensions.
- Reproduction artifact, if any: repros/reproduce_findings.py (F3).

### F4 — GREEN review acceptance is path-only, so same-path Task Card changes retain stale approval

- Affected workflow contract/invariant: workflow/REVIEW.md requires each attempt to bind one exact acceptance surface and says GREEN finalization is only for the exact current subject plus acceptance; workflow/ROUTER.md requires stale bindings to fail closed.
- Expected behavior: If the stable Task Card acceptance changes after a review attempt was frozen/GREEN, that review cannot authorize finalization of the changed acceptance surface.
- Actual behavior: validate_review() validates Task Card acceptance only as a workstream-local path whose filename matches card_id; no immutable acceptance commit/blob is stored or checked. During active-result routing, select_route() validates review history and exact result subject but never verifies that current Task Card bytes still equal the acceptance reviewed by the attempt. Same-path acceptance edits leave GREEN reusable.
- Minimal reproduction: Create an in_progress required-review result and GREEN attempt, confirm post_review_finalization, edit only the Task Card's Acceptance: text at the same path while retaining a valid Card, and route again. The selector still returns post_review_finalization.
- Why this is materially load-bearing: It allows an independent GREEN verdict to authorize materially different acceptance criteria than the reviewer evaluated.
- Defect class / likely siblings: Mutable path-only acceptance identity / review bypass.
- Existing tests that failed to catch it: Review tests bind and compare result subject identity but do not mutate the acceptance Card at the same path after review.
- Reproduction artifact, if any: repros/reproduce_findings.py (F4).

### F5 — Accepted Card results do not prove an exact implementation subject or durable evidence

- Affected workflow contract/invariant: workflow/EXECUTION.md defines an accepted semantic result as carrying an exact implementation subject plus durable evidence refs and verified tests/readback; workflow/STATE.md treats a valid result as recovery truth.
- Expected behavior: A malformed/non-immutable implementation subject or evidence locator that does not resolve to durable evidence must not be accepted as semantic completion.
- Actual behavior: parse_card_result() requires only that Implementation subject be a non-empty string. Evidence refs are checked only for a syntactically workstream-local .md path; neither the parser nor result-routing path requires that those evidence files exist. A result with Implementation subject: definitely-not-an-immutable-git-subject and a nonexistent evidence path parses successfully and an in_progress, no-review Card advances to result_reconciliation.
- Minimal reproduction: Replace the fixture's result text with a valid Card ID, arbitrary nonempty implementation-subject text, a workstream-local but nonexistent evidence .md path, and nonempty tests summary; call select_route().
- Why this is materially load-bearing: Such a record can become durable no-replay/recovery truth without identifying what was implemented or preserving the evidence claimed to justify acceptance.
- Defect class / likely siblings: Semantic result validation is syntactic rather than identity/evidence validating.
- Existing tests that failed to catch it: test_result_rejects_runtime_identity_and_cross_workstream_evidence covers forbidden field names and cross-workstream paths, but not implementation-subject grammar/identity or evidence existence.
- Reproduction artifact, if any: repros/reproduce_findings.py (F5). An isolated execution of the exact parse_card_result() logic from the audited blob accepted this malformed subject and nonexistent evidence locator.

## Non-blocking observations

- validate_external_effect() does not call the general prohibited-key rejection used by other canonical state validators, so runtime/session-style extra keys appear able to survive that record validator. This was not promoted to the frozen material finding set because the inspected continuation helper does not consume those keys as authority.
- Planning/Plan Review Git subjects are internally cross-checked but the planning validator does not receive PROJECT.repository; existing router fixtures exercise a project repository string different from the planning subject repository. The canonical text inspected was not explicit enough about cross-repository plans to freeze this as a material defect.

## Coverage

The audit remained bound to commit 4fb4bfb7d7b1481d6f347c182fc96a5a1135e045. Inspected canonical modules included workflow/ROUTER.md, STATE.md, EXECUTION_PREP.md, EXECUTION.md, REVIEW.md, RECOVERY.md, PLANNING.md, PLAN_REVIEW.md, CLOSE.md, BRAINSTORMING.md, and USER_STOP.md; executable code included tools/router.py, state_contract.py, execution_contract.py, review_contract.py, recovery_contract.py, and close_contract.py; test coverage included router, state, execution, review/recovery and Close tests/fixtures plus schemas/STATE_ENVELOPE.md.

The selected lenses were exercised as follows: malformed/contradictory fail-closed behavior (F1, F3, F5); stale commit/blob/path/result/review identity (F2, F4); Close/finalization/end-of-scope (F1, F2, F4); helper/documented-semantics parity and negative space (all findings, with emphasis on test cases that mutate a dimension the existing test keeps constant).

No audit/* branch/report, GitHub Issue, or PR-comment corpus was intentionally inspected. No historical comparison was performed after freeze.

## Confidence and limitations

Confidence is high in the five code-path defects because each is a direct mismatch between canonical contracts and reachable production branches/validators, and the supplied reproduction script uses the repository's real selector plus existing fixture helpers without modifying product code.

A full exact-checkout selector run was not available in this session: container Git access could not resolve GitHub, and the connected remote terminal reported its monthly command quota exhausted. The exact parse_card_result() implementation was separately executed in isolation and accepted the F5 malformed subject/nonexistent evidence case. The remaining selector reproductions are preserved for direct execution from an exact checkout but were not run here.

During initial target-SHA verification, the GitHub commit-metadata response automatically included the merge diff, which itself contained historical workstream evidence/review text. That disclosure occurred before the finding set was frozen despite the intended blindness boundary. I did not inspect audit/*, Issues/PR comments, or use those historical conclusions as a defect checklist; the five frozen findings above were derived from canonical workflow/code/test behavior. This transport-level disclosure is the principal independence limitation.

## Post-freeze historical comparison

Not performed.
