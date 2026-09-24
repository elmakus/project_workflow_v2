# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — DONE status bypasses result validity and blocking review gates

- Affected workflow contract/invariant: `workflow/STATE.md` and `workflow/REVIEW.md` require a valid durable result for terminal work and require REQUIRED/activated RECOMMENDED review with no attempt, pending/in-progress, or RED to block terminal Card completion. `workflow/ROUTER.md` says invalid/missing/stale bindings fail closed to Recovery and only then may all terminal Cards route to Close.
- Expected behavior: A Card cannot be accepted as terminal merely because `TASK_BOARD.toml` says `status = "done"`. Its result must be valid/current, and any blocking review lifecycle must be satisfied by exact GREEN coverage before Close becomes reachable.
- Actual behavior: `tools/state_contract.validate_board()` only requires that a DONE Card contain a syntactically valid `result` locator. `tools/router.select_route()` validates result/review semantics only for an `in_progress` Card. Once every Card is marked `done`, it routes directly to `close` without reading the result file, Task Card review requirement, or review attempts. Therefore a nonexistent result, a REQUIRED review with no attempt, or a RED review can all be hidden behind DONE and reach Close.
- Minimal reproduction: Run `python3 audits/swarm/luba8a4q8jb2nbtv2i2mra8w/repros/repro_terminal_review_bypass.py`. Its first three cases construct: (1) DONE + nonexistent result path, (2) DONE + REQUIRED review with no attempt, and (3) DONE + RED review. The production branch structure routes each all-DONE board to `route/close`.
- Why this is materially load-bearing: This permits terminal-state forgery to bypass the exact result, review, and RED-recovery gates that protect acceptance before integration/finalization.
- Defect class / likely siblings: Terminal-state trust without semantic revalidation. Siblings include pending/in-progress review hidden behind DONE, stale result locator hidden behind DONE, and mixed all-terminal boards whose individual terminal proofs are invalid.
- Existing tests that failed to catch it: `test_all_terminal_cards_route_to_close_not_directly_to_stop` covers only a positive path after installing a valid result with review requirement `none`; there are no negative all-DONE tests for missing result artifacts or blocking review states.
- Reproduction artifact, if any: `repros/repro_terminal_review_bypass.py`.

### F2 — Immutable Git identities are declarative and do not protect same-path content changes

- Affected workflow contract/invariant: `workflow/STATE.md` and `workflow/EXECUTION_PREP.md` require exact dependency result path + immutable commit/blob identity and explicitly require missing/stale or same-path-changed dependency inputs to fail closed. Recovery/review similarly relies on the current exact result subject.
- Expected behavior: A declared `commit`/`blob` identity must be verified against the referenced Git object/content before it can authorize launch, review reuse, finalization, or recovery.
- Actual behavior: `tools/state_contract.py` checks only that declared commit/blob strings are 40 lowercase hex characters. `refresh_ready_card()` compares dependency tuples in Card vs Board, then reads the current path but never verifies that its bytes equal the declared blob at the declared commit. Active-result routing likewise parses the current path but computes the review subject from self-declared Board metadata without Git-object/content verification. Keeping the tuple unchanged while changing the current file therefore remains accepted.
- Minimal reproduction: Run `python3 audits/swarm/luba8a4q8jb2nbtv2i2mra8w/repros/repro_git_identity.py`. Case 1 mutates a reviewed result file at the same path while leaving Board/review commit+blob metadata unchanged; the selector still reaches `post_review_finalization`. Case 2 mutates a READY dependency result file while keeping the matching Card/Board tuple unchanged; launch refresh still reaches `execution_prep`.
- Why this is materially load-bearing: Exact immutable identity is the anti-staleness boundary for dependency launch, result recovery, and review coverage. If it is only self-asserted metadata, same-path mutation can silently reuse authority/evidence for different bytes.
- Defect class / likely siblings: Unverified immutable-object identity / TOCTOU on repository content. Likely siblings include Planning/Plan Review Git-blob subjects and any result locator whose commit/blob is trusted without object readback.
- Existing tests that failed to catch it: `test_ready_card_stale_dependency_fails_closed_before_launch` changes the declared Board tuple, so tuple inequality catches it; it never tests changed bytes with the same tuple. Router review tests deliberately use synthetic `"a"*40`/`"b"*40` identities for temporary uncommitted files, demonstrating that Git existence/content is not checked.
- Reproduction artifact, if any: `repros/repro_git_identity.py`.

### F3 — A terminal GREEN review can finalize with nonexistent verdict evidence

- Affected workflow contract/invariant: `workflow/REVIEW.md` requires terminal attempts to retain durable verdict evidence; `workflow/STATE.md` describes review attempts as durable exact-subject records and invalid/missing bindings as fail-closed.
- Expected behavior: Before GREEN can authorize post-review finalization, the attempt's required terminal evidence must resolve to durable evidence appropriate to the workstream/review.
- Actual behavior: `validate_review()` requires only a non-empty, traversal-safe `evidence_path` string for GREEN/RED. It does not require a workstream-local evidence locator, check that the file exists, or read it. The router validates the review record but never reads `evidence_path`, so a GREEN attempt pointing to `missing/review-evidence.md` can still route to `post_review_finalization`.
- Minimal reproduction: Run the `case_green_missing_evidence_finalizes()` case in `repro_terminal_review_bypass.py`; it rewrites a GREEN attempt to a nonexistent relative evidence path and preserves an otherwise valid exact subject.
- Why this is materially load-bearing: A verdict whose durable evidence is absent is indistinguishable from an unsupported terminal assertion, yet it can cross the blocking review gate and finalize implementation.
- Defect class / likely siblings: Evidence locator existence/binding is not validated before terminal authority is consumed. The same pattern is present in terminal Plan Review evidence validation, which likewise checks only non-empty safe path syntax.
- Existing tests that failed to catch it: State tests reject an empty terminal `evidence_path` but do not test nonexistent, wrong-root, or unreadable evidence; router review tests always create the referenced evidence file.
- Reproduction artifact, if any: `repros/repro_terminal_review_bypass.py`.

### F4 — Research may redirect its own return owner by contradicting origin_role

- Affected workflow contract/invariant: `workflow/RESEARCH.md` says Research owns an origin role + exact subject + exact return owner, Intake-origin issue Research returns to Intake, and “Research never selects a different target by itself.” Router semantics require deterministic return to the exact owner.
- Expected behavior: `origin_role` and `return_target` must be coherent. For example, `origin_role = "intake"` must return to `intake`; implementation Research must return to the exact implementation/recovery owner that created it.
- Actual behavior: `validate_research()` validates `origin_role` and `return_target` independently but never checks their relationship. Pre-execution routing reads a completed Research record before Intake and directly routes to the self-declared `return_target`. Thus a syntactically valid record with `origin_role = "intake"` and `return_target = "definition"` routes to Definition instead of Intake.
- Minimal reproduction: Run `python3 audits/swarm/luba8a4q8jb2nbtv2i2mra8w/repros/repro_research_owner.py`; it creates a complete Intake-origin Research record whose return target is Definition. The selector's completed-Research branch returns `route/definition`.
- Why this is materially load-bearing: Research is explicitly non-authoritative and must not choose a new workflow destination. This mismatch can skip the Intake reconciliation/alignment owner and create an illegal transition from durable contradictory state.
- Defect class / likely siblings: Cross-field ownership coherence not enforced. Siblings include Brainstorming/Definition origin-target swaps and Task-Board implementation Research where an allowed execution origin role can name a different allowed execution-prefixed return target.
- Existing tests that failed to catch it: Research validation and router tests use only matching origin/return pairs; no negative matrix tests contradictory role/target combinations.
- Reproduction artifact, if any: `repros/repro_research_owner.py`.

### F5 — Review acceptance identity is path-only, so changed active Card acceptance can reuse stale GREEN

- Affected workflow contract/invariant: `workflow/REVIEW.md` requires every implementation review attempt to bind the exact acceptance surface; `workflow/STATE.md` repeats that requirement. `workflow/EXECUTION_PREP.md` calls the Task Card stable authority and forbids silently rewriting an in-progress Card through refinement.
- Expected behavior: If the active Card's acceptance/scope contract changes after review, the old GREEN attempt must become stale or the mutation must fail closed; finalization must require review against the changed acceptance surface.
- Actual behavior: A review attempt's Task-Card acceptance identity contains only `class = "task_card"` plus its path. `validate_review()` checks that the path is workstream-local and its filename stem matches `card_id`, but no immutable Card commit/blob/fingerprint is stored or compared. During active-result routing the current Card is reparsed only to obtain review requirement; its current acceptance text is not compared with the review attempt. Changing `Acceptance:` at the same Card path after GREEN can therefore retain `post_review_finalization`.
- Minimal reproduction: Run the `case_changed_active_card_acceptance_reuses_green()` case in `repro_terminal_review_bypass.py`; it freezes a GREEN review, materially changes the active Card's Acceptance line at the same path, then invokes the production selector.
- Why this is materially load-bearing: A GREEN verdict is meaningful only relative to what was accepted/reviewed. Path-only acceptance permits review reuse across changed acceptance, defeating the exact-acceptance gate even when result subject identity itself is unchanged.
- Defect class / likely siblings: Mutable acceptance surface with no immutable binding. Plan Review acceptance authority is also path-only and warrants the same negative-space treatment.
- Existing tests that failed to catch it: `test_task_card_review_acceptance_is_exact_and_semantic` checks path/workstream/Card-ID binding but does not mutate the Card after review; router tests do not check changed acceptance content under a still-matching path.
- Reproduction artifact, if any: `repros/repro_terminal_review_bypass.py`.

## Non-blocking observations

The selected bootstrap/install lens did not yield a material defect in the inspected subject. The Codex SessionStart hook fails closed on missing/malformed/out-of-root bundled router and rejects a mismatched `PLUGIN_ROOT`; delivery tests intentionally distinguish its installed-local bootstrap from ChatGPT's current-default-branch locator model. I did not classify that intentional cross-harness update model as a bug.

Path traversal and workstream-local locator checks are generally strong for canonical locator classes: absolute paths and `.`/`..` components are rejected and most workstream-owned locator classes are exact-prefix/exact-path bound. The material identity defects above arise after those syntactic/path checks, at content/owner/terminal-proof binding boundaries.

## Coverage

Independent inspection remained bound to commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`. I inspected the canonical router/state/review/recovery/intake/research/planning/plan-review/execution/execution-prep/Close/GitHub-Issues/authority contracts; production router, state, review, recovery, execution, Close and adoption helpers; SessionStart/plugin/ChatGPT bootstrap surfaces; state/router/Close/delivery tests and representative fixtures.

Selected attack lenses exercised:
- Research / Intake / tracker / external-side-effect recovery: contradictory Research owner/return binding, tracker lifecycle, external-effect/readback helpers.
- plugin / install / update / SessionStart / bootstrap drift: local-root validation, router marker/bootstrap behavior, ChatGPT vs installed-package delivery tests.
- path traversal / locator safety / cross-workstream binding: locator class/path binding, safe-relative handling, immutable-result/dependency identity verification gap, acceptance binding.
- review independence / review bypass / result mutation: DONE bypass, result mutation, evidence durability, exact subject reuse, acceptance mutation.

The preserved reproduction scripts use production `select_route` and the repository's existing RouterTests fixture builders; they do not modify product code.

## Confidence and limitations

Confidence is high in the five code-path findings because each is a direct missing invariant or unconditional routing consequence visible in the exact production selector/validator and is separated from style/design preferences.

I could not execute the preserved repro scripts in this audit harness: the local container had no GitHub network access, the connected Desktop Commander environment reported its monthly tool-call quota exhausted, and the target commit had no available workflow run to reuse. Therefore the report does not claim a fresh runtime execution that did not occur. The repros are constructed to run in an exact checkout and assert the production outcomes described above.

A GitHub commit-metadata fetch unexpectedly expanded the merge commit diff and exposed text from historical implementation evidence/review artifacts before the finding set was frozen. I did not inspect `audit/*` branches, other swarm reports, Issues, or PR comments, and I did not use the accidentally exposed historical narratives to select, validate, remove, or de-duplicate findings. The five-finding set above was independently frozen from canonical workflow contracts plus production tools/tests.
