# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Explicit user stop is bypassed after the planning gate reaches a live Task Board

- Affected workflow contract/invariant: PWV2-REQ-068 requires an explicit user stop to be a real stop; workflow/ROUTER.md places explicit human/premium boundaries above current-card work.
- Expected behavior: If durable Brainstorming carries explicit_user_stop = true, continuation must stop there, or fail closed to Recovery if the co-bound downstream state makes that combination contradictory. It must never continue into implementation.
- Actual behavior: tools/router.py checks brainstorm["explicit_user_stop"] only inside the branch guarded by not plan_gate_passed_with_board. An approved plan with satisfied C and a Task Board sets plan_gate_passed_with_board = true, so the explicit stop is never examined and the board can route directly to Execution, Review, or Close.
- Minimal reproduction: In the stock router fixture, install the normal promoted GREEN Definition, approved GREEN-reviewed plan with premium C satisfied, keep the fixture Task Board with M01-T04 in_progress, then change only BRAINSTORM.toml from explicit_user_stop = false to true. select_route still reaches the Task Board and returns route/execution rather than a stop or Recovery.
- Why this is materially load-bearing: A durable human-owned stop can be silently crossed into implementation. This is a direct authority/precedence violation, not merely a diagnostic inconsistency.
- Defect class / likely siblings: Any high-precedence pre-execution stop whose check is conditionally skipped once plan_gate_passed_with_board is true should be audited for the same precedence inversion.
- Existing tests that failed to catch it: tests/test_router.py exercises co-bound approved-plan/Task-Board precedence but its Brainstorming fixtures use explicit_user_stop = false; there is no explicit-user-stop=true co-bound downstream case.
- Reproduction artifact, if any: repros/router_adversarial_repros.py::repro_explicit_user_stop_bypass

### F2 — A DONE Card can bypass a REQUIRED review and route to Close

- Affected workflow contract/invariant: PWV2-REQ-036 and workflow/REVIEW.md require REQUIRED/activated RECOMMENDED review to block terminal Card completion until exact GREEN.
- Expected behavior: A Card marked done while its stable Task Card requires review but no exact GREEN attempt exists is contradictory durable state and must fail closed or recover the missing review/finalization obligation. It must not be accepted as terminal.
- Actual behavior: validate_board checks only that a done Card has a result locator. Review requirement/history is validated only inside the router's active in_progress Card branch. If every Card is marked done, the router skips all result/review validation and returns route/close.
- Minimal reproduction: Use install_reviewable_result(project, "required") on the stock fixture, verify the active state routes to review_freeze, then change only status = "in_progress" to status = "done". With no review attempt at all, select_route returns route/close.
- Why this is materially load-bearing: Canonical state can assert terminal completion without satisfying a mandatory independent review gate, allowing Close/integration to proceed from an illegally finalized Card.
- Defect class / likely siblings: DONE Cards with no attempts, pending attempts, RED attempts, stale GREEN subjects, malformed result contents, or path-only result identity are all outside the active-card validation path.
- Existing tests that failed to catch it: test_required_review_blocks_until_green_then_routes_finalization covers only an in_progress Card. test_all_terminal_cards_route_to_close_not_directly_to_stop uses Review requirement: none and therefore does not test the blocking invariant.
- Reproduction artifact, if any: repros/router_adversarial_repros.py::repro_done_required_review_bypass

### F3 — Claimed immutable result/dependency Git identity is compared as strings but never verified against bytes

- Affected workflow contract/invariant: workflow/STATE.md says READY dependency inputs are bound by path + immutable commit/blob identity and that missing, stale, or same-path-changed inputs fail closed; workflow/REVIEW.md requires exact immutable review subjects; PWV2-REQ-034 and PWV2-REQ-063 depend on exact subject freshness.
- Expected behavior: Before launch or GREEN reuse/finalization, the implementation must prove that the bytes being consumed are the bytes identified by the claimed commit/blob. Changing the file at the same path without changing the persisted identity must not preserve validity.
- Actual behavior: refresh_ready_card checks only that the dependency's persisted (path, commit, blob) tuple equals the DONE predecessor's persisted tuple, then reads the current path without hashing/resolving it. Active-result recovery similarly parses the current result file but constructs current_subject only from the unchanged locator strings. A changed current file therefore inherits the old immutable identity and a prior GREEN review can still match.
- Minimal reproduction: (a) create a REQUIRED result plus GREEN review, then change only the result file contents while leaving its board commit/blob and review subject unchanged; select_route still returns post_review_finalization. (b) create a READY Card with an exact predecessor dependency, then change only the predecessor result file contents while leaving both exact tuples untouched; select_route still returns execution_prep.
- Why this is materially load-bearing: Stale or replaced content can be executed/finalized under review/dependency proof belonging to different bytes. This defeats the principal safety property of exact immutable subjects.
- Defect class / likely siblings: Planning and Plan Review subject keys also validate only syntactic 40-hex identity; result locators may even omit commit/blob entirely when both fields are absent. Every consumer that treats persisted Git strings as proof without resolving the Git object is in the same class.
- Existing tests that failed to catch it: test_changed_result_after_terminal_review_requires_new_attempt changes the board blob string; test_ready_card_stale_dependency_fails_closed_before_launch changes the predecessor commit/blob strings as well as the file. Neither tests same-path byte mutation with unchanged claimed identity.
- Reproduction artifact, if any: repros/router_adversarial_repros.py::repro_result_bytes_change_under_green and repro_ready_dependency_bytes_change

### F4 — Mutable path-only Task Card acceptance can rewrite the review gate after implementation

- Affected workflow contract/invariant: workflow/EXECUTION_PREP.md defines the Task Card as stable authority; workflow/REVIEW.md says each attempt binds the exact acceptance surface; workflow/EXECUTION_PREP.md forbids silently rewriting an in-progress Card through refinement.
- Expected behavior: Once an in-progress/result-bearing Card's stable acceptance/review contract is established, changing its scope, acceptance, tests, or review requirement must invalidate the old execution/review state unless the change is explicitly reconciled as a new exact acceptance subject.
- Actual behavior: Task Board Card contracts and review acceptance identities carry only a Task Card path. They have no commit/blob identity. The active-result router reparses whatever bytes are currently at that path. Rewriting Review requirement: required to none at the same path immediately changes routing from review_freeze to result_reconciliation without any durable authority transition; a previous GREEN review likewise has no immutable Card-acceptance identity to compare.
- Minimal reproduction: Install a result whose Task Card says Review requirement: required and observe review_freeze. Modify only that same Card file to Review requirement: none, leaving Board/result state unchanged. select_route now returns result_reconciliation.
- Why this is materially load-bearing: A mutable file rewrite can downgrade or alter the gate that controls acceptance of already-produced implementation, bypassing independent review without changing canonical Card identity.
- Defect class / likely siblings: Any post-start mutation of Included scope, Excluded scope, Acceptance, Required tests/readback, authority refs, dependencies, or review requirement at the same Card path is not cryptographically distinguishable by review acceptance.
- Existing tests that failed to catch it: test_task_card_review_acceptance_is_exact_and_semantic validates a path-only Task Card acceptance as sufficient; active-review router tests assume the Card file does not change after the result is produced.
- Reproduction artifact, if any: repros/router_adversarial_repros.py::repro_task_card_review_downgrade

### F5 — Implementation Research can return to a nonexistent or wrong Card subject

- Affected workflow contract/invariant: workflow/RECOVERY.md requires Task-Board-owned Research to recover an exact Research obligation and return target before unrelated execution, with the Research record owning the exact origin and once-only return owner; workflow/ROUTER.md requires stale/contradictory bindings to fail closed.
- Expected behavior: An execution_* Research return target must be bound to the originating/current workstream Card and compatible owner. A stale or nonexistent Card subject must route Recovery rather than manufacture a deterministic continuation.
- Actual behavior: validate_research accepts any nonempty suffix after execution_resolution:, execution_prep:, or execution:. The router maps the prefix to an obligation and returns the suffix as subject without checking that it equals origin_subject, identifies any Card on the selected Task Board, or is compatible with origin_role/current Card.
- Minimal reproduction: On the stock active M01-T04 board, install a complete Task-Board Research record, then change only return_target from execution_resolution:M01-T04 to execution_resolution:M99-T99. select_route returns route/execution_resolution with subject M99-T99 instead of Recovery.
- Why this is materially load-bearing: Recovery can abandon the real active Card and select a fabricated/stale owner, violating deterministic durable recovery and potentially skipping the actual corrective obligation.
- Defect class / likely siblings: Mismatches between origin_role and return-target prefix, origin_subject and return-target suffix, or suffix and Task Board membership are all accepted by the same loose prefix check.
- Existing tests that failed to catch it: test_task_board_research_return_is_recovered_before_execution uses only the matching execution_resolution:M01-T04 target and has no wrong/nonexistent-owner variant.
- Reproduction artifact, if any: repros/router_adversarial_repros.py::repro_research_return_to_nonexistent_card

### F6 — Terminal GREEN/RED review evidence may point to a nonexistent artifact

- Affected workflow contract/invariant: workflow/REVIEW.md requires durable verdict evidence for terminal attempts; workflow/ROUTER.md says invalid/missing bindings fail closed.
- Expected behavior: A terminal attempt's evidence locator must resolve to durable evidence of the correct class/scope before GREEN can authorize finalization.
- Actual behavior: validate_review requires terminal evidence_path to be merely a nonempty safe relative string. It does not require the path to exist, be workstream-local, or reside under the evidence root, and the router never reads that evidence before post_review_finalization. The same structural issue exists in Plan Review validation.
- Minimal reproduction: Create a REQUIRED result plus GREEN implementation review, then change only evidence_path in the review record to missing/review.md and ensure that path does not exist. select_route still returns post_review_finalization.
- Why this is materially load-bearing: A terminal verdict can authorize finalization without the durable evidence the review contract explicitly requires, weakening recovery/audit integrity and allowing fabricated evidence locators.
- Defect class / likely siblings: RED implementation attempts and terminal Plan Review attempts use the same nonempty-path pattern; cross-workstream or unrelated existing paths are also not semantically constrained.
- Existing tests that failed to catch it: state-contract tests check that terminal evidence_path is nonempty but do not require existence/class binding. Router helper add_review_attempt normally creates the referenced evidence, so routing tests do not exercise a missing target.
- Reproduction artifact, if any: repros/router_adversarial_repros.py::repro_missing_green_review_evidence

## Non-blocking observations

The accepted Card-result parser treats Implementation subject as an arbitrary nonempty string even though the template and execution contract describe it as an exact immutable implementation subject. This is likely another surface of F3's identity-verification class, but it is not counted separately here to avoid double-counting the same root failure.

The stock valid state fixture contains a DONE result locator with only a path and no commit/blob. validate_locator explicitly accepts that shape when both identity fields are absent. This increases the blast radius of F2/F3 but is not counted as a separate finding.

## Coverage

The audit remained bound to commit 4fb4bfb7d7b1481d6f347c182fc96a5a1135e045. I inspected the canonical router/recovery/review/state/execution/execution-prep/planning/plan-review/close contracts, accepted requirements, production router/state/recovery/execution/close helpers, templates, bootstrap Skill/SessionStart/plugin metadata, and the relevant router/state/execution/recovery/close tests and fixtures.

The selected attack lenses were exercised as follows:
- router precedence / unreachable branches / conflicting obligations: F1, F2;
- stale commit/blob/path/result/review identity: F3, F4, F6;
- RED / recovery / blocker / interrupted-runtime continuation: F2, F5, F6;
- helper vs documented semantics / parity drift / negative space: all findings, especially F2-F6.

I intentionally did not inspect audit/* branches, swarm reports, GitHub Issues/PR comments, or historical workstream evidence/review diagnosis narratives before freezing the finding set.

## Confidence and limitations

Confidence is high for F1-F6 because each follows a concrete accepted contract invariant and a direct reachable branch in the exact production selector/validator at the audit commit, with negative-space coverage identified in the exact test suite.

A runnable checkout was not available in the audit environment: the local container could not resolve github.com, the authorized Remote Desktop Commander had exhausted its monthly execution allowance, and the outer command bridge was unavailable to this turn. I therefore could not execute pytest or the preserved reproduction script in this session. The reproduction artifact calls the real tools.router.select_route against the repository's existing router fixtures/helpers and is intended for deterministic execution in any checkout of the audited commit; no product code changes are required.

## Post-freeze historical comparison

Not performed. The independent finding set above was frozen without reading historical audit/reviewer conclusions.
