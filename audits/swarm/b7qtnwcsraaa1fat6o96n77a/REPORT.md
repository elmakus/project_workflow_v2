# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Same-path dependency/result drift is trusted without blob verification

- Affected workflow contract/invariant: `workflow/STATE.md` and `workflow/EXECUTION_PREP.md` require READY launch refresh to verify exact dependency result path + immutable commit/blob identity, and explicitly require missing/stale or same-path-changed dependency inputs to fail closed. `workflow/RECOVERY.md` likewise treats immutable result identity as the basis for review/finalization.
- Expected behavior: if a dependency/result file changes at the same path while its declared commit/blob locator remains unchanged, routing must fail closed before Execution Prep or later review/finalization consumes that content.
- Actual behavior: `tools/router.py::refresh_ready_card` compares the Task Card dependency tuple only against the tuple declared on the DONE predecessor in the Task Board, then reads the current working-tree file by path. It never verifies that the bytes read are the declared blob or that the declared commit/path actually resolves to that blob. The same trust pattern exists for the active Card result: current file content is parsed, while review identity is derived from Task Board metadata rather than from the bytes just read.
- Minimal reproduction: create the existing READY dependency fixture with matching `path@commit:blob`, then modify only the dependency result file contents while leaving both the Task Card dependency and Task Board result locator unchanged. The production selector follows the READY path and returns `route/execution_prep`; contractually this same-path drift must recover. Preserved in `repros/repro_semantic_defects.py` case `f1`.
- Why this is materially load-bearing: downstream work can launch against predecessor bytes that are not the immutable accepted result named by the workflow, and the same identity gap can let review/finalization reason about locator metadata that no longer describes the current result file.
- Defect class / likely siblings: declared immutable identity is compared as metadata but never proven against artifact bytes/Git objects. Siblings include same-path active-result mutation and any other exact Git subject whose consumer reads the current path without object/hash verification.
- Existing tests that failed to catch it: `test_ready_card_stale_dependency_fails_closed_before_launch` mutates the Task Board commit/blob together with the file; it does not exercise content-only same-path drift with unchanged metadata.
- Reproduction artifact, if any: `audits/swarm/b7qtnwcsraaa1fat6o96n77a/repros/repro_semantic_defects.py`.

### F2 — DONE Card can bypass required review and jump to Close

- Affected workflow contract/invariant: `workflow/STATE.md` and `workflow/REVIEW.md` state that REQUIRED/activated RECOMMENDED review with no attempt, pending/in-progress, or RED blocks terminal Card completion; GREEN for the exact current subject is what permits deterministic post-review finalization.
- Expected behavior: a Task Board that marks a Card `done` while its stable Card requires review but has no qualifying exact GREEN attempt is contradictory and must fail closed or route back to the review/finalization obligation, never to Close.
- Actual behavior: `tools/state_contract.py::validate_board` requires only that a `done` Card have a result locator. It does not read the Card contract or validate review history against terminal status. `tools/router.py` skips review handling when no Card is `in_progress`; if all Cards are `done`, it immediately returns `route/close`.
- Minimal reproduction: on the valid router fixture, install a valid semantic result for the active Card with `Review requirement: required`, add no review attempt, change only Task Board status from `in_progress` to `done`, and call the production selector. It returns `route/close`. Preserved as case `f2`.
- Why this is materially load-bearing: a malformed/stale Board mutation can bypass independent review authority and move the workstream into integration/finalization ownership.
- Defect class / likely siblings: Task Board status/result/review cross-field invariants are not enforced for terminal/non-active Cards. Related states such as READY/BLOCKED Cards carrying already-durable results deserve the same negative-space validation.
- Existing tests that failed to catch it: `test_all_terminal_cards_route_to_close_not_directly_to_stop` first installs a result with `Review requirement: none`; no test marks a review-required Card DONE without GREEN.
- Reproduction artifact, if any: `audits/swarm/b7qtnwcsraaa1fat6o96n77a/repros/repro_semantic_defects.py`.

### F3 — GREEN review can finalize with missing verdict evidence

- Affected workflow contract/invariant: `workflow/REVIEW.md` requires terminal attempts to keep durable verdict evidence; the router contract says missing/invalid/stale bindings fail closed. `workflow/CLOSE.md` also treats required review/result/evidence as part of the recovery package.
- Expected behavior: a GREEN/RED terminal review whose declared evidence artifact is missing or not a valid workstream evidence locator must be invalid and fail closed before post-review finalization.
- Actual behavior: `tools/state_contract.py::validate_review` checks only that terminal `evidence_path` is a non-empty safe relative string. It does not constrain it to the workstream evidence root and does not verify that the file exists. `tools/router.py` reads review TOML but never reads the terminal evidence path, so a GREEN attempt can drive `route/post_review_finalization` after its evidence file has been deleted. `validate_plan_review` has the same syntax-only evidence treatment for Plan Review.
- Minimal reproduction: install a REQUIRED result, add a GREEN attempt using the normal workstream evidence path, delete only that evidence file, and call the production selector. The selector still returns `route/post_review_finalization`. Preserved as case `f3`.
- Why this is materially load-bearing: the independent review gate can become a bare verdict bit with a dangling/irrelevant evidence string, defeating the durable-evidence and recovery guarantees.
- Defect class / likely siblings: evidence locator is treated as unverified prose rather than a bound artifact. Plan Review terminal evidence is a direct sibling.
- Existing tests that failed to catch it: state-contract tests reject an empty terminal `evidence_path` but do not test a nonexistent/non-workstream path; router tests create the evidence file but never remove or redirect it.
- Reproduction artifact, if any: `audits/swarm/b7qtnwcsraaa1fat6o96n77a/repros/repro_semantic_defects.py`.

### F4 — Implementation Research can redirect continuation to an arbitrary subject

- Affected workflow contract/invariant: `workflow/RESEARCH.md`, `workflow/RECOVERY.md`, and `workflow/STATE.md` require one exact return owner; implementation/recovery Research is owned by the selected Task Board and must return to that exact durable owner. Research must not choose a different target by itself.
- Expected behavior: an execution Research return target must have a non-empty exact subject and must be consistent with the Board/origin obligation (for example, it must not redirect M01-T04 recovery to a nonexistent M01-T99). Contradictory targets must fail closed.
- Actual behavior: `tools/state_contract.py::validate_research` accepts any string beginning `execution:`, `execution_prep:`, or `execution_resolution:`; it does not require a non-empty suffix, an existing matching Card/trigger, or consistency with `origin_role`/`origin_subject`. The Board branch in `tools/router.py` merely splits at the first colon and routes the suffix as the new subject.
- Minimal reproduction: use the existing Board-owned completed Research fixture for active Card/origin `M01-T04`, change only `return_target` from `execution_resolution:M01-T04` to `execution_resolution:M01-T99`, and call the production selector. It returns `route/execution_resolution` with subject `M01-T99` although no such selected Card owns the obligation. Preserved as case `f4`.
- Why this is materially load-bearing: a stale/corrupt Research record can select an illegal continuation subject outside the exact Board obligation, violating deterministic routing and authority binding.
- Defect class / likely siblings: structurally unbound encoded return targets. Empty suffixes, mismatched origin roles, nonexistent Card IDs, and execution-vs-resolution target switching are siblings.
- Existing tests that failed to catch it: `test_task_board_research_return_is_recovered_before_execution` tests only a matched `origin_subject = M01-T04` / `return_target = execution_resolution:M01-T04`; state-contract Research tests cover lifecycle/source accounting but no execution-target binding negatives.
- Reproduction artifact, if any: `audits/swarm/b7qtnwcsraaa1fat6o96n77a/repros/repro_semantic_defects.py`.

## Non-blocking observations

- `validate_locator(..., "result", ...)` permits a path-only result locator when both `commit` and `blob` are omitted; exact identity is enforced only if either key is present. Some routes later require exact identity, while others do not. I did not freeze this as a separate defect because the intended pre-reconciliation allowance for path-only result state is not explicit enough to distinguish from a deliberate intermediate state.
- The ownership wording in `workflow/STATE.md` says WORKSTREAM owns exact locators for currently materialized workstream-local records, while implementation Research is separately pointed to by Task Board `research_obligation`. If both locators are present for a completed execution-return Research, the earlier generic Research branch only knows `intake/brainstorming/definition` complete-return owners and can recover before the Board-specific execution-return branch is reached. I did not freeze this as a material finding because the manifest-locator requirement for Board-owned implementation Research is not stated as an explicit exception/non-exception.
- Tracker `repository` is syntactically validated but not compared to `PROJECT.md.repository`. The contract says "exact repository" but does not unambiguously forbid intentional cross-repository bookkeeping, so this was not treated as a defect.

## Coverage

Selected attack lenses:
1. helper vs documented semantics / parity drift / negative space;
2. stale commit/blob/path/result/review identity;
3. Research / Intake / tracker / external-side-effect recovery;
4. router precedence / unreachable branches / conflicting obligations.

Inspected on exact subject `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`:
- `workflow/ROUTER.md`, `STATE.md`, `RESEARCH.md`, `INTAKE.md`, `PLANNING.md`, `REVIEW.md`, `RECOVERY.md`, `EXECUTION_PREP.md`, `EXECUTION.md`, `GITHUB_ISSUES.md`, `CLOSE.md`;
- `tools/router.py`, `state_contract.py`, `execution_contract.py`, `recovery_contract.py`, `close_contract.py`;
- relevant negative-space coverage in `tests/test_router.py`, `tests/test_state_contract.py`, and `tests/test_close_contract.py`.

The audit did not inspect `audit/*` branches, GitHub Issues, PR comments, or other swarm reports. Findings were frozen before any intentional historical comparison.

## Confidence and limitations

Confidence is high for F1, F2 and F4 because the production branches and missing validations are direct and the existing tests expose the exact negative space. Confidence is medium-high for F3 because the contract says durable verdict evidence and the production router never resolves the path, although evidence-file content is not separately schema-defined.

Executable probes could not be run in the audit environment: the local container had no GitHub network resolution and the authorized Desktop Commander endpoint reported that its monthly usage limit was exhausted. The preserved repro script calls the real production selector and existing exact-subject fixture helpers; it was therefore written for direct execution on this audit subject but was not executed here.

Strict-blindness caveat: during bootstrap, the GitHub commit-metadata endpoint unexpectedly returned the merge commit diff, which included historical implementation/evidence paths. Those passages were not used to generate or freeze the findings above; every frozen finding was re-derived from canonical workflow contracts, production helpers, and current tests. No audit branch/report, Issue, or PR discussion was inspected.

## Post-freeze historical comparison

Not performed.
