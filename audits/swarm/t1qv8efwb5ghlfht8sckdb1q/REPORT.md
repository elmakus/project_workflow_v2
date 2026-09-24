# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Exact Git identities are accepted without resolving commit/blob content

- Affected workflow contract/invariant: Exact immutable result/plan/review identities; READY launch refresh; fail-closed handling of stale or invalid bindings.
- Expected behavior: A declared path + commit + blob must resolve to the claimed Git content. Missing, forged, stale, or same-path-changed identities must fail closed before dependency launch, review reuse, or finalization.
- Actual behavior: `validate_locator`, `_git_blob_subject_key`, and `exact_result_subject` validate/format 40-hex strings but never resolve them. `refresh_ready_card` only compares the dependency tuple with the tuple stored on a DONE predecessor, then reads the current filesystem path. The active-result/review path likewise compares two state strings while parsing the current file at that path. Matching fabricated tuples therefore satisfy "exact" identity checks even when no Git object proves the binding.
- Minimal reproduction: Create a DONE predecessor result and a READY Card dependency that both claim `cccc...:dddd...`, in a copied fixture with no Git object database, while placing arbitrary current text at the result path. `select_route` reaches `execution_prep` because the two state tuples match. The same class applies to frozen plan subjects and result/review subjects.
- Why this is materially load-bearing: Exact Git identity is the mechanism that prevents stale content, result substitution, and review reuse over a changed artifact. Treating the locator as self-authenticating lets an internally consistent lie bypass freshness and review boundaries.
- Defect class / likely siblings: Syntax-only immutable locators. Likely siblings include Planning subject B/C binding, Plan Review subject reuse, implementation result reconciliation, and review subject comparison.
- Existing tests that failed to catch it: `test_ready_card_stale_dependency_fails_closed_before_launch` changes only one side of the tuple and therefore tests tuple disagreement, not Git resolution. Planning and implementation-review tests routinely use repeated synthetic 40-hex values and still assert successful routing.
- Reproduction artifact, if any: `repros/repro_router_semantic_defects.py` (F1).

### F2 — Promoted Brainstorming explicit user stop is bypassed by Definition/Planning precedence

- Affected workflow contract/invariant: Brainstorming real-stop semantics and router precedence for explicit human boundaries.
- Expected behavior: If the current Brainstorming revision carries `explicit_user_stop = true`, routing must stop before later Definition/Planning obligations continue.
- Actual behavior: Once a Definition locator exists, `select_route` processes Definition and Planning and can return from those branches before reaching the later Brainstorming block that checks `explicit_user_stop`. A promoted Brainstorming record with the stop flag set and a GREEN Definition can therefore route to Planning (or a premium stop) instead of `explicit_user_stop`.
- Minimal reproduction: Start from the router fixture, install the repository test helper's promoted Brainstorming + GREEN Definition state, then change only `explicit_user_stop = false` to `true`. With Definition A satisfied and no Planning record, the selector returns `route/planning`.
- Why this is materially load-bearing: A durable explicit human stop is a higher-precedence authority boundary. Continuing downstream work after that stop directly violates human control and the router's declared priority foundation.
- Defect class / likely siblings: Higher-precedence obligation hidden behind an earlier downstream-stage return; audit other durable stop flags that are validated only after derived-state branches.
- Existing tests that failed to catch it: Brainstorming/Definition tests always materialize downstream state with `explicit_user_stop = false`; there is no co-bound explicit-stop + Definition/Planning precedence case.
- Reproduction artifact, if any: `repros/repro_router_semantic_defects.py` (F2).

### F3 — DONE status bypasses required implementation review and reaches Close

- Affected workflow contract/invariant: REQUIRED/activated RECOMMENDED review blocks terminal Card completion until exact GREEN; DONE must represent a legally finalized Card.
- Expected behavior: A Card whose stable contract requires review cannot become terminal without an exact GREEN review attempt for the current result and acceptance surface. Contradictory `status = "done"` must fail closed or route back to review/finalization.
- Actual behavior: `validate_board` requires only that a DONE Card have a result locator. The router validates review requirements only for `in_progress` Cards. If a required-review Card is changed directly to DONE with a result but no review attempt (or a non-GREEN attempt), no Card-level review validation runs; when all Cards are DONE, the selector routes to `close`.
- Minimal reproduction: On the valid router fixture, make M01-T04's Task Card say `Review requirement: required`, attach a syntactically valid result, change its board status from `in_progress` to `done`, and leave `review_attempts` absent. `select_route` reaches `route/close`.
- Why this is materially load-bearing: This permits a single durable state mutation to skip the independent implementation review gate entirely and present an unreviewed result to Close as terminal work.
- Defect class / likely siblings: Terminal-state validation trusts status rather than reconstructing legality from the stable Card contract/result/review history; RED or pending review can be bypassed the same way.
- Existing tests that failed to catch it: `test_required_review_blocks_until_green_then_routes_finalization` keeps the Card `in_progress` for all review states. No test asserts that premature DONE with required review fails closed.
- Reproduction artifact, if any: `repros/repro_router_semantic_defects.py` (F3).

### F4 — Stale Planning cycle survives a changed Definition revision

- Affected workflow contract/invariant: Strategic Planning must be derived from the current GREEN Definition authority; material re-entry must use a new exact entry subject and repeat A/B/C.
- Expected behavior: If current Definition authority changes after a plan was approved, a plan whose `entry_subject` names the old Definition revision cannot continue to Execution Prep/Execution without reconciliation and a new material planning cycle where required.
- Actual behavior: `validate_planning` only checks that `premium_a_subject == entry_subject`; neither it nor the router compares `planning.entry_subject` with the current Definition record/revision. The Definition record can move from R1 to R2 while an approved R1-derived plan, prior GREEN Plan Review, and satisfied C remain accepted, and the router proceeds to the Task Board.
- Minimal reproduction: Install GREEN Definition R1, an approved P1 plan with entry subject `definition:R1|planning-cycle:1`, GREEN Plan Review, and satisfied C. Then mutate only `DEFINITION.toml revision = "R2"` while keeping it GREEN. The selector still routes the live board (in the fixture, `route/execution`) rather than failing closed or reopening Planning.
- Why this is materially load-bearing: Definition is the accepted requirements/decision authority. Executing a plan frozen against an obsolete Definition revision can silently implement superseded product authority and reuse stale premium/review gates.
- Defect class / likely siblings: Cross-record freshness is checked only within Planning's self-declared subjects, not against the current upstream authority owner. Definition premium-A satisfaction is also not revision-bound.
- Existing tests that failed to catch it: `test_stale_premium_cycle_and_wrong_review_subject_fail_closed` exercises planning-internal A/subject mismatches, not a changed upstream Definition with internally self-consistent stale Planning.
- Reproduction artifact, if any: `repros/repro_router_semantic_defects.py` (F4).

### F5 — GREEN implementation review is reused after its Task Card acceptance surface mutates

- Affected workflow contract/invariant: Each implementation review binds one exact subject to one exact acceptance surface; a changed acceptance contract cannot inherit an old GREEN verdict.
- Expected behavior: If the stable Task Card's scope, acceptance, tests, or other review-relevant authority changes after a GREEN review, the prior attempt must no longer authorize finalization; contradictory mutation must fail closed or require a fresh exact review.
- Actual behavior: A review attempt's Task Card acceptance identity is only `class = "task_card"` plus its path. No commit/blob/version is captured or resolved. During result review, the router rereads the current Card only to obtain its current review requirement, then accepts the old GREEN attempt as long as the result subject strings still match. Mutating the Card's Acceptance line at the same path leaves the old GREEN verdict valid.
- Minimal reproduction: Install a required-review result and GREEN attempt so the route is `post_review_finalization`. Change only the Task Card's `Acceptance:` text at the same path, leaving the result/review subject untouched. The selector still returns `post_review_finalization`.
- Why this is materially load-bearing: Review approval is meaningful only relative to the acceptance contract it evaluated. Path-only acceptance lets changed requirements/tests silently inherit a verdict issued against a different contract.
- Defect class / likely siblings: Mutable acceptance identity. Any same-path Task Card change (scope, tests, technical-contract selection, authority refs, review requirement) can escape the old attempt's provenance unless another independent check happens to reject it.
- Existing tests that failed to catch it: Review freshness tests mutate the result blob and verify subject mismatch behavior; they do not mutate the Task Card acceptance surface after GREEN.
- Reproduction artifact, if any: `repros/repro_router_semantic_defects.py` (F5).

## Non-blocking observations

No advisory/style-only item was promoted to a material finding. Post-freeze historical comparison was intentionally not performed; no `audit/*`, swarm report, GitHub Issue/PR defect discussion, or historical workstream evidence/review narrative was used as a discovery checklist.

## Coverage

The audit was bound to commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`. I inspected the canonical router and authority/state modules, Planning/Definition/Plan Review, Execution Prep/Execution/Review/Recovery/Close, the production selector and state/execution/recovery/review/close helpers, templates, and relevant router/state/close tests. The four selected lenses were all exercised: Planning/premium/execution precedence (F2/F4), review bypass/result mutation (F3/F5), stale exact identity (F1/F4/F5), and recovery/fail-closed behavior (F1/F3/F5). I also checked sibling/negative-space variants described in each finding.

## Confidence and limitations

Confidence is high in the five deterministic control-flow/state-validation defects because each follows directly from production selector/validator conditions at the exact subject commit, and the preserved reproduction invokes the repository's actual `select_route` plus its canonical test fixture/helpers. F1 is additionally exposed by existing tests that successfully route with synthetic 40-hex identities rather than resolved Git objects.

I could not execute the newly preserved reproduction script inside this chat: the available local process bridge had no remaining execution quota, and the alternate native execution bridge did not expose a valid current turn token. I therefore did not claim runtime output that was not observed. The reproduction script is non-mutating with respect to product code and operates only on temporary copies of the repository's existing router fixture.
