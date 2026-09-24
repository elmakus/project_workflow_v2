# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Declared Git identities are trusted without dereferencing current bytes

- Affected workflow contract/invariant: PWV2-REQ-030, PWV2-REQ-034, PWV2-REQ-036; `workflow/STATE.md` exact dependency/result identity; `workflow/RECOVERY.md` exact current review subject; router rule that stale bindings fail closed.
- Expected behavior: A dependency/result/review subject expressed as path + immutable commit/blob must be verified against Git truth before launch, review reuse, or GREEN finalization. Same-path changed bytes, an impossible commit/path/blob tuple, or a result no longer matching the declared immutable subject must fail closed or require a new exact review subject.
- Actual behavior: `validate_locator`, `_git_blob_subject_key`, and `validate_review` only validate 40-hex syntax. `refresh_ready_card` compares dependency metadata tuples from the Card and Board and then reads the current path, but never proves that current bytes are the declared blob or that commit:path resolves to it. The active-result route parses the current result file, then `exact_result_subject` and `review_subject` merely stringify Board/review metadata. Consequently a GREEN review continues to authorize `post_review_finalization` after the result file is mutated at the same path while the declared commit/blob are left unchanged. The same trust defect applies to predecessor dependency refresh; planning/Plan Review subjects use the same syntactic identity pattern.
- Minimal reproduction: Start from the valid router fixture. Materialize a REQUIRED result whose Board locator declares commit `aaaa…`/blob `bbbb…`, add a GREEN review declaring the same tuple, and observe `post_review_finalization`. Mutate the result file bytes at the same path without changing Board/review metadata. The selector still reaches `post_review_finalization` because no Git identity is dereferenced. Preserved in `repros/adversarial_router_cases.py::case_f1_same_path_result_mutation_keeps_green`.
- Why this is materially load-bearing: Exact immutable subjects are the safety boundary that permits review reuse, finalization, recovery without replay, and predecessor-dependent launch. Trusting caller-authored hex strings instead of Git truth allows unreviewed content to inherit a prior GREEN verdict and allows downstream execution to consume altered predecessor results.
- Defect class / likely siblings: Declared-identity-vs-observed-identity confusion. Likely siblings include READY dependency result tuples, planning frozen subjects, Plan Review subjects, and acceptance artifacts that are represented by a mutable path rather than a verified immutable identity.
- Existing tests that failed to catch it: `test_changed_result_after_terminal_review_requires_new_attempt` changes Board blob metadata rather than same-path file bytes. `test_ready_card_stale_dependency_fails_closed_before_launch` changes Board dependency metadata so tuple comparison detects it. Fixture tests intentionally use synthetic `a*40`/`b*40` identities unrelated to actual fixture blobs, so they prove syntactic equality rather than immutable Git binding.
- Reproduction artifact, if any: `audits/swarm/jyxmfic5ggkl2cok7gu7ng4w/repros/adversarial_router_cases.py` (F1).

### F2 — DONE status bypasses REQUIRED/RED review and reaches Close

- Affected workflow contract/invariant: PWV2-REQ-034, PWV2-REQ-036, `workflow/REVIEW.md` blocking lifecycle, and `workflow/STATE.md` rule that REQUIRED/activated RECOMMENDED pending/in-progress/RED blocks terminal Card completion.
- Expected behavior: A Card whose stable contract requires review cannot become terminal DONE, and cannot enter Close, until the exact current result has a valid GREEN attempt. Missing, pending/in-progress, RED, stale, or otherwise invalid review state must keep terminal completion blocked or route recovery/correction.
- Actual behavior: `validate_board` requires a DONE Card to have a result locator but does not read its Card contract, result, review requirement, or review attempts. `select_route` performs those checks only for `in_progress` Cards. If every Card is marked `done`, the selector routes directly to `close` without reading the Card contract/result/review history. A Card with `Review requirement: required` and no attempt therefore reaches Close; the same structural bypass can hide a lingering RED/pending attempt on a DONE Card.
- Minimal reproduction: Materialize a valid semantic result and a stable Card with `Review requirement: required`, create no review attempt, then change only the Board status from `in_progress` to `done`. The selector returns `route/close`. Preserved in `repros/adversarial_router_cases.py::case_f2_done_required_without_green_routes_close`.
- Why this is materially load-bearing: This converts mutable Board status into a bypass around the mandatory independent review gate and can advance an unreviewed or explicitly failed implementation into final integration/Close.
- Defect class / likely siblings: Terminal-state validation that trusts status before validating the obligations required to make that status legal. Siblings are DONE Cards with pending/in-progress/RED/stale review attempts or malformed result/review content that is never read on the all-DONE branch.
- Existing tests that failed to catch it: `test_required_review_blocks_until_green_then_routes_finalization` covers only an `in_progress` Card. `test_all_terminal_cards_route_to_close_not_directly_to_stop` deliberately uses `review_requirement="none"` before setting DONE. There is no DONE + REQUIRED/non-GREEN negative-space test.
- Reproduction artifact, if any: `audits/swarm/jyxmfic5ggkl2cok7gu7ng4w/repros/adversarial_router_cases.py` (F2).

### F3 — Unrelated active Research preempts unresolved issue authorization

- Affected workflow contract/invariant: PWV2-REQ-053, PWV2-REQ-054, PWV2-REQ-067/068; `workflow/INTAKE.md` exact issue alignment; `workflow/RESEARCH.md` durable return ownership; router precedence foundation placing explicit human/premium boundaries above research return.
- Expected behavior: An unresolved issue repair boundary remains authoritative: after exact diagnosis prior art is bound, no post-diagnosis response must route to the real `issue_alignment` stop. Before that binding exists, exact Intake-origin prior-art Research for the current repair subject owns the obligation. A contradictory later-stage Research record must not silently preempt that higher-precedence boundary; malformed ordering should fail closed if it cannot be reconciled.
- Actual behavior: `select_route` reads the workstream-level `research` locator before `intake` and immediately returns for Research state `active` or `complete`. It therefore never validates or routes the unresolved Intake state in those cases. A valid issue Intake that would independently produce `stop/issue_alignment` changes to `route/research` simply by adding an unrelated active Brainstorming Research record.
- Minimal reproduction: With the valid fixture, add an active issue Intake for `repair:v1`, an exact persisted diagnosis-prior-art binding, and no user response. Without Research the router returns `stop/issue_alignment`. Add a valid active Research record with `origin_role="brainstorming"`, `origin_subject="unrelated-scope@1"`, and `return_target="brainstorming"`. The router now returns `route/research` for the unrelated subject before reading Intake. Preserved in `repros/adversarial_router_cases.py::case_f3_unrelated_research_preempts_alignment_stop`.
- Why this is materially load-bearing: The issue-repair authorization boundary is explicitly human-owned. A stale/later-stage Research slot can make the router miss that stop and select an obligation from contradictory durable state, violating both human-control and deterministic-precedence guarantees.
- Defect class / likely siblings: Cross-stage precedence without phase/owner compatibility validation. Any active/complete workstream Research can preempt unresolved Intake because the early Research return occurs before Intake validation.
- Existing tests that failed to catch it: `test_issue_without_post_diagnosis_response_is_real_alignment_stop` uses consumed exact Intake Research, which does not early-return. `test_later_brainstorming_research_does_not_erase_issue_diagnosis_prior_art` also uses `state="consumed"`. No test combines unresolved Intake with unrelated active/complete Research.
- Reproduction artifact, if any: `audits/swarm/jyxmfic5ggkl2cok7gu7ng4w/repros/adversarial_router_cases.py` (F3).

### F4 — Implementation Research can return to a nonexistent or empty Card subject

- Affected workflow contract/invariant: `workflow/RESEARCH.md` exact return ownership, `workflow/RECOVERY.md` implementation Research handoff, router rule that stale/contradictory bindings fail closed.
- Expected behavior: Task-Board-owned implementation/recovery Research must return once to the exact durable owner that initiated it. The execution return subject must be non-empty and bound to the initiating/current Card (or another explicitly valid durable execution owner); a stale, nonexistent, or contradictory target must route Recovery.
- Actual behavior: `validate_research` treats any string beginning with `execution_resolution:`, `execution_prep:`, or `execution:` as a valid execution return target. It does not require a non-empty suffix and does not bind that suffix to `origin_subject` or a Card on the selected Board. For complete Board Research, the router derives both obligation and subject solely from that prefix/suffix. Thus `origin_subject="M01-T04"` + `return_target="execution:M99-T99"` routes to Execution for nonexistent `M99-T99`; `return_target="execution:"` routes to Execution with an empty subject.
- Minimal reproduction: Point the valid Board's `research_obligation` at a complete Research record with `origin_role="execution_resolution"`, `origin_subject="M01-T04"`, and first `return_target="execution:M99-T99"`, then `return_target="execution:"`. Both records validate and route to `execution`, with subject `M99-T99` and `""` respectively. Preserved in `repros/adversarial_router_cases.py::case_f4_execution_research_accepts_wrong_or_empty_card_subject`.
- Why this is materially load-bearing: Recovery can resume work under the wrong or nonexistent Card after a factual handoff, breaking exact return ownership and potentially escaping the authority/acceptance surface of the blocked/current Card.
- Defect class / likely siblings: Prefix-only typed locator validation without referential integrity. Siblings are stale execution return targets after Card evolution and mismatches among `origin_role`, `origin_subject`, return obligation, and Board membership.
- Existing tests that failed to catch it: `test_task_board_research_return_is_recovered_before_execution` only supplies matching `execution_resolution:M01-T04`. State-contract Research tests cover non-execution return owners and do not exercise empty/nonexistent/mismatched execution suffixes.
- Reproduction artifact, if any: `audits/swarm/jyxmfic5ggkl2cok7gu7ng4w/repros/adversarial_router_cases.py` (F4).

## Non-blocking observations

- When every current Card is DONE, the router routes to Close without consulting JIT-trigger state. A satisfied-but-unconsumed trigger may therefore be invisible to the selector at that point. I did not classify this as material because the canonical router explicitly routes all-current-Cards-terminal through Close and Close is allowed to discover further authorized obligations.
- Review acceptance identity for Task Cards is path-bound rather than blob-bound. This is a likely sibling of F1, but I kept it inside the declared-identity defect class instead of double-counting it without a separate end-to-end falsification.

## Coverage

The audit remained bound to `elmakus/project_workflow_v2@4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`. I inspected the canonical router/state/review/recovery/execution/Execution Prep/Close/Intake/Research/GitHub-Issues modules; the approved V2 requirements; production `router.py`, `state_contract.py`, `execution_contract.py`, `recovery_contract.py`, `review_contract.py`, and `close_contract.py`; router/state/Close tests; and the exact router/state fixtures needed for negative-space construction.

The four selected attack lenses were all exercised:
- review independence / review bypass / result mutation: F1, F2;
- Close / finalization / end-of-approved-scope: F2 plus all-DONE/JIT negative space;
- stale commit/blob/path/result/review identity: F1;
- Research / Intake / tracker / external-side-effect recovery: F3, F4, plus tracker/external-effect contract inspection.

I did not inspect `audit/*` branches, swarm reports, GitHub Issues, or PR comments before freezing the finding set. The finding set was frozen as F1–F4 before any historical-comparison step.

## Confidence and limitations

Confidence is high in the source-level counterexamples: each follows a concrete selector/validator branch and the existing tests demonstrate the omitted negative-space dimension. The preserved repro script imports the production selector and mutates only temporary copies of the repository's own valid fixture.

I could not execute the preserved repro script in this session. The sandbox could not resolve GitHub for an exact checkout, and the connected remote-command environment reported its monthly command quota exhausted and explicitly prohibited retries. I therefore did not claim an executed PASS/FAIL transcript; the reproductions are source-mechanical and ready to run against the exact subject/audit branch.

A GitHub commit-metadata fetch for the exact audit subject returned the merge commit's own diff, which included workstream bookkeeping/evidence text. That material was not used as a defect checklist, and no audit reports, tracker discussions, Issues, or PR comments were consulted. Findings F1–F4 were derived from canonical workflow contracts, production helpers/selectors, tests, and fixtures.

## Post-freeze historical comparison

Not performed. The independently frozen F1–F4 set is left unclassified as new/known to preserve the strongest practical separation from historical diagnosis material.
