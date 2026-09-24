# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Immutable Git identities are trusted as declarations instead of verified against repository content

- Affected workflow contract/invariant: exact immutable result/dependency/review/plan identities; READY launch refresh; review subject refresh; fail-closed stale binding.
- Expected behavior: whenever a durable locator claims `path + commit + blob`, the selector must establish that the claimed commit contains that path at that blob (and, where current worktree content is being consumed, that the consumed artifact is the exact claimed subject). A same-path content change under an unchanged stale locator must fail closed before launch/finalization.
- Actual behavior: `validate_locator` and `_git_blob_subject_key` validate only shape/40-hex syntax. `refresh_ready_card` compares Card dependency tuples only to Board-declared tuples, then reads the current file without hashing it. Active-result review refresh similarly builds `current_subject` only from Board-declared commit/blob and compares that string to the review record; it parses the current result file but never proves those bytes equal the declared blob. Consequently, materially changing a reviewed result file while leaving the Board locator unchanged still reaches `post_review_finalization`. The same trust model also affects declared Planning Git subjects.
- Minimal reproduction: run `python3 audits/swarm/1nf66pps8yiv44rk65rdcv5g/repros/router_counterexamples.py F1`. It creates a REQUIRED-review result, records GREEN against the declared exact subject, then changes the result bytes without changing the Board `commit/blob`; the production selector still returns `route/post_review_finalization`.
- Why this is materially load-bearing: immutable Git identity is the core anti-staleness boundary for recovery and independent review. If identity is not checked against Git content, a stale or contradictory durable locator can authorize finalization of bytes that were never reviewed.
- Defect class / likely siblings: declarative Git-identity trust without object verification. Confirmed code paths include active Card result/review and READY dependency refresh; Planning subject validation uses the same syntax-only pattern and is a likely sibling.
- Existing tests that failed to catch it: `test_changed_result_after_terminal_review_requires_new_attempt` changes the Board blob itself, and `test_ready_card_stale_dependency_fails_closed_before_launch` changes the Board commit/blob tuple as well as the file. Neither mutates artifact bytes while leaving the claimed immutable locator stale.
- Reproduction artifact, if any: `repros/router_counterexamples.py` (F1).

### F2 — A `done` Card can bypass REQUIRED review and force Close

- Affected workflow contract/invariant: REQUIRED/activated RECOMMENDED review must block terminal Card completion until exact GREEN; Close only follows legally terminal Cards.
- Expected behavior: a Card whose stable contract requires review cannot be accepted as `done` unless its exact current result has a valid GREEN attempt. Contradictory `done` state must fail closed rather than advance to Close.
- Actual behavior: `validate_board` requires only that a `done` Card have a result locator. It does not parse the Card review requirement, validate its result subject, or require a GREEN attempt. The router then returns `route/close` whenever all Cards are `done`, without revalidating result/review terminality. A REQUIRED-review Card with no attempt (or stale/RED history) can therefore be made terminal by Board status alone.
- Minimal reproduction: run `python3 audits/swarm/1nf66pps8yiv44rk65rdcv5g/repros/router_counterexamples.py F2`. It creates a REQUIRED-review result with no review attempt, changes only Card status to `done`, and the production selector returns `route/close`.
- Why this is materially load-bearing: Board corruption, interrupted reconciliation, or an incorrect writer can bypass the independent-review safety gate and enter final integration/closure.
- Defect class / likely siblings: terminal-state validation that trusts lifecycle status without reconstructing the terminal proof it semantically implies.
- Existing tests that failed to catch it: `test_all_terminal_cards_route_to_close_not_directly_to_stop` uses `Review requirement: none`; there is no negative all-DONE case for REQUIRED/RECOMMENDED review or RED/stale review history.
- Reproduction artifact, if any: `repros/router_counterexamples.py` (F2).

### F3 — Plan Review `in_progress` is accepted and misclassified as RED

- Affected workflow contract/invariant: Plan Review attempt lifecycle and deterministic Planning/Review precedence.
- Expected behavior: canonical `workflow/PLAN_REVIEW.md` defines Plan Review verdicts as `pending / green / red`. An `in_progress` Plan Review record is therefore contradictory and should fail closed (or be normalized by an explicitly documented lifecycle before routing), never be treated as RED.
- Actual behavior: the shared `validate_review` accepts `in_progress`, and `validate_plan_review` does not narrow that set. In the frozen-plan router branch, only `pending` and `green` are handled explicitly; every other accepted value takes the unconditional RED return to Planning. Thus a syntactically valid `in_progress` Plan Review is routed as if RED evidence existed.
- Minimal reproduction: run `python3 audits/swarm/1nf66pps8yiv44rk65rdcv5g/repros/router_counterexamples.py F3`. It changes an otherwise valid pending Plan Review to `in_progress` with no terminal evidence; the production selector returns `route/planning` with the RED-correction reason.
- Why this is materially load-bearing: an unfinished independent review can be converted into correction authority, bypassing the actual review obligation and fabricating a RED semantic transition.
- Defect class / likely siblings: shared-validator state widening combined with router fall-through that assumes the remaining value is a specific terminal verdict.
- Existing tests that failed to catch it: `test_plan_review_must_match_frozen_subject_and_terminal_evidence` covers pending and GREEN but not `in_progress`; router tests contain no `plan_review_content("in_progress")` case.
- Reproduction artifact, if any: `repros/router_counterexamples.py` (F3).

### F4 — A durable explicit Brainstorming user stop is bypassed by downstream Definition state

- Affected workflow contract/invariant: explicit human stop precedence; contradictory state must fail closed; runtime/router priority foundation places explicit human boundaries first.
- Expected behavior: `explicit_user_stop = true` is a real stop. If combined with already-promoted/downstream state, the router must either honor the stop before deterministic continuation or reject the contradiction to Recovery.
- Actual behavior: `validate_brainstorm` permits `state = "promoted"`, exact promotion authorization, and `explicit_user_stop = true` simultaneously. The router loads that record but evaluates Definition/Planning first and can return from those branches before reaching the later explicit-user-stop check. With a GREEN Definition and satisfied A, it returns `route/planning`, silently bypassing the durable user stop.
- Minimal reproduction: run `python3 audits/swarm/1nf66pps8yiv44rk65rdcv5g/repros/router_counterexamples.py F4`. It installs the valid promoted+GREEN Definition fixture, flips only `explicit_user_stop` to true, and the production selector still returns `route/planning`.
- Why this is materially load-bearing: an explicit human stop is one of the workflow's highest-precedence authority boundaries. Allowing downstream state to override it violates human control and makes contradictory recovery state fail open.
- Defect class / likely siblings: high-precedence stop state validated independently but checked only after lower-precedence early returns.
- Existing tests that failed to catch it: Brainstorming/Definition router fixtures set `explicit_user_stop = false`; there is no promoted/downstream state case with the flag true.
- Reproduction artifact, if any: `repros/router_counterexamples.py` (F4).

## Non-blocking observations

No advisory-only items are promoted from this audit. The report intentionally separates the four demonstrated semantic defects from speculative redesign ideas.

## Coverage

The audit remained bound to commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`. It inspected canonical routing/state/Planning/Plan Review/Recovery/Execution Prep/Execution/Close/Brainstorming/Research/workstream contracts, the approved requirements, production selector and state/recovery/execution/close helpers, and targeted existing router/state tests.

The selected attack lenses were exercised as follows:
- RED/recovery/blocker/interrupted continuation: reviewed durable result recovery, review refresh, blocker classification, and Task-Board Research return paths; F1 is directly recovery/review-reuse relevant.
- path/locator safety/cross-workstream binding: inspected `Reads._read_path`, `_safe_relative_path`, workstream-local locator validation, result/dependency binding, and negative-path tests; F1 exposes identity verification beyond lexical path safety.
- Planning/Premium/Execution precedence: traced A/B/Plan Review/C and co-bound Board precedence; F3 and F4 are precedence/state-domain failures.
- Close/finalization: traced DONE terminal routing and Close helpers; F2 demonstrates a review-gate bypass into Close.

Existing passing tests were treated as evidence of covered positive cases, not proof against the negative-space counterexamples above.

## Confidence and limitations

Confidence is high in the four code-path counterexamples because each follows accepted validator states directly through the production selector and contradicts an explicit canonical invariant. A runnable non-mutating reproduction script is preserved for each case.

The audit environment could not execute the repository Python suite: the local container could not resolve GitHub for cloning, the connected Desktop Commander device had exhausted its monthly execution allowance, and no valid outer-Codex execution token was available. Therefore the reproduction script was not executed in this chat; actual routes are derived from the exact production source at the immutable subject and the existing fixture/helper semantics.

A GitHub commit-metadata request unexpectedly returned the merge diff, which included historical evidence/review text for the router-board-precedence hotfix before this finding set was frozen. No `audit/*` branch or swarm report was inspected, no GitHub Issues/PR-comment defect search was performed, and the exposed hotfix narrative was not used to derive or modify F1-F4. No post-freeze historical comparison was performed.
