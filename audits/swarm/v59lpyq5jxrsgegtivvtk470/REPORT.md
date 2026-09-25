# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Immutable Git identities are self-attested instead of verified against artifact bytes

- Affected workflow contract/invariant: `workflow/STATE.md` and `workflow/EXECUTION_PREP.md` require launch refresh to verify each dependency result by exact path + commit/blob identity and to fail closed on same-path-changed inputs. Planning and review contracts likewise describe immutable Git-blob subjects.
- Expected behavior: If a dependency/result/plan/review subject claims `path@commit:blob`, the production path that consumes it must verify that the actual artifact corresponds to that immutable identity; changing bytes at the same path while retaining old identifiers must fail closed.
- Actual behavior: `refresh_ready_card()` only compares the dependency tuple in the Task Card with the tuple already present in `TASK_BOARD.toml`, then reads the current path without hashing/resolving it against `blob` or `commit`. `validate_planning()`, `validate_review()` and `exact_result_subject()` likewise validate 40-hex syntax/equality but do not resolve the subject to Git content. Therefore same-path changed bytes remain launchable, and frozen/review subjects can be syntactically exact without being proven to name the bytes consumed.
- Minimal reproduction: Create a DONE predecessor result with commit `a*40` and blob `b*40`; make a READY Card depend on that exact tuple; route once (Execution Prep); modify only the predecessor result file contents while leaving the Card and board tuple unchanged; route again. The selector still returns `route/execution_prep` instead of Recovery.
- Why this is materially load-bearing: Exact immutable identity is the mechanism that prevents stale or mutated predecessor/result/review inputs from being consumed after state recovery. Trusting two self-consistent strings rather than the artifact lets stale content cross an execution/review boundary.
- Defect class / likely siblings: Any durable `git_blob` or result locator whose SHA fields are only syntax/equality checked rather than resolved to repository content; planning frozen subject, implementation review subject and result locators are likely siblings.
- Existing tests that failed to catch it: `test_ready_card_stale_dependency_fails_closed_before_launch` changes both the file and the board commit/blob, so tuple inequality is detected; it does not test changed bytes with unchanged identity. Planning/review tests use synthetic 40-hex values without proving them against Git objects.
- Reproduction artifact, if any: `repros/repro_adversarial.py` (`repro_f1_same_path_changed_dependency_still_launches`).

### F2 — Approved Planning is not bound to the current Definition revision/authority

- Affected workflow contract/invariant: `workflow/DEFINITION.md`, `workflow/PLANNING.md`, and `workflow/STATE.md` require Strategic Planning to derive from current accepted Definition authority and require stale planning/premium authorization to be invalidated by material re-entry/change.
- Expected behavior: Changing the current Definition revision or accepted requirements/decisions after a plan was approved must make the old Planning/Plan Review chain stale, forcing Recovery or a new Planning/premium cycle before execution.
- Actual behavior: `validate_definition()` validates Definition internally, and `validate_planning()` validates Planning internally, but no validator/router check binds `planning.entry_subject`, the approved plan, or the Plan Review to the current Definition revision/authority. After changing Definition from R1 to R2 and changing its requirements locator, an old approved R1 Planning/Plan Review record can remain valid and the router proceeds to the live Task Board/Execution.
- Minimal reproduction: Install the normal approved-plan fixture; mutate only `DEFINITION.toml` from revision `R1` to `R2` and point requirements at a new accepted requirements file; leave Planning and Plan Review unchanged. `select_route()` still returns `route/execution` for the active Card.
- Why this is materially load-bearing: Execution can continue under a plan reviewed against superseded product authority, bypassing the intended new Planning and A/B/C sequence after a material Definition change.
- Defect class / likely siblings: Missing cross-record freshness bindings between phase records; any later-stage record validated only internally can remain live after an upstream authority record changes.
- Existing tests that failed to catch it: `test_stale_premium_cycle_and_wrong_review_subject_fail_closed` checks `premium_a_subject` against the Planning record's own `entry_subject` and checks Plan Review against the Planning subject, but never mutates the current Definition beneath an otherwise self-consistent Planning chain.
- Reproduction artifact, if any: `repros/repro_adversarial.py` (`repro_f2_stale_plan_survives_definition_change`).

### F3 — Card-result “exact implementation subject” accepts arbitrary non-exact text

- Affected workflow contract/invariant: `workflow/EXECUTION.md` defines an accepted semantic Card result as recording an exact implementation subject; durable valid results are recovery truth and prevent replay.
- Expected behavior: `parse_card_result()` must reject a result whose implementation subject is not a well-formed exact immutable implementation identity.
- Actual behavior: The parser only requires the `Implementation subject` field to be non-empty and free of `<`/`>` placeholders. Values such as `banana` are accepted and returned as `implementation_subject`.
- Minimal reproduction: Call `parse_card_result()` with all required fields but `- Implementation subject: banana`; parsing succeeds.
- Why this is materially load-bearing: A result can become durable recovery truth and advance into reconciliation/review without identifying what implementation was actually accepted, defeating exact-subject recovery and later auditability.
- Defect class / likely siblings: Semantic identifiers represented as unconstrained strings where the workflow contract requires exact immutable identity.
- Existing tests that failed to catch it: `test_delegated_and_direct_realizations_share_semantic_result_contract` uses an exact-looking example but does not test malformed/non-exact implementation subjects; the remaining result tests focus on runtime-identity fields and evidence path locality.
- Reproduction artifact, if any: `repros/repro_adversarial.py` (`repro_f3_non_exact_implementation_subject_is_accepted`).

### F4 — Missing result/review evidence is treated as durable proof

- Affected workflow contract/invariant: `workflow/EXECUTION.md`, `workflow/REVIEW.md`, and `workflow/STATE.md` require durable evidence for accepted results and terminal review attempts, with invalid/missing bindings failing closed.
- Expected behavior: Before treating a result as recovery truth or a GREEN review as finalization authority, the router must at least establish that every required durable evidence locator resolves to an existing permitted artifact.
- Actual behavior: `parse_card_result()` validates only the syntax/prefix of evidence refs; the router never reads those evidence files. `validate_review()`/`validate_plan_review()` require a non-empty terminal `evidence_path` but do not resolve it, and the router does not read it. A missing result-evidence file still routes to `review_freeze`; a GREEN review whose evidence file was deleted still routes to `post_review_finalization`.
- Minimal reproduction: (a) create a valid required-review result, delete its referenced evidence file, route; observed `route/review_freeze`. (b) create a GREEN review, delete its terminal evidence file, route; observed `route/post_review_finalization`.
- Why this is materially load-bearing: Recovery and finalization can be authorized by records whose purported proof no longer exists, so incomplete/corrupted durable state fails open exactly at review/finalization boundaries.
- Defect class / likely siblings: Locator validation that checks string shape but never dereferences required evidence; Plan Review terminal evidence is a direct sibling.
- Existing tests that failed to catch it: `test_review_terminal_evidence_and_append_only_history` verifies only that the evidence string is non-empty. Router result/review tests create evidence files but never remove them to prove they are actually consumed.
- Reproduction artifact, if any: `repros/repro_adversarial.py` (`repro_f4_missing_evidence_does_not_fail_closed`).

### F5 — Plan Review acceptance can be unrelated to the Definition it supposedly reviews

- Affected workflow contract/invariant: `workflow/PLAN_REVIEW.md` says Plan Review judges the frozen plan against accepted Definition/requirements/decisions and owns an exact acceptance authority.
- Expected behavior: A Plan Review attempt's acceptance identity must be bound to the current accepted Definition authority (or an exact Planning-owned acceptance surface derived from it); an unrelated authority locator must fail closed.
- Actual behavior: `validate_review()` accepts any `authority` locator under the broad allowed roots, while `validate_plan_review()` checks only workstream, plan revision/cycle and reviewed plan subject. It never compares `acceptance` with current Definition requirements/decisions. An otherwise GREEN Plan Review can point at an unrelated `decisions/UNRELATED.md` and still be consumed; with C already satisfied, routing proceeds to Execution.
- Minimal reproduction: Install the approved-plan fixture, create `decisions/UNRELATED.md`, change only `PLAN_REVIEW.toml` acceptance from the Definition requirements path to that unrelated decision, then route. The selector still returns `route/execution`.
- Why this is materially load-bearing: Independent review can certify the correct plan blob against the wrong acceptance authority, allowing execution without proof that the plan was reviewed against the product requirements that currently govern it.
- Defect class / likely siblings: Review records whose reviewed subject is exact but whose acceptance surface is only class/path-shaped rather than cross-bound to the current authority owner.
- Existing tests that failed to catch it: `test_plan_review_must_match_frozen_subject_and_terminal_evidence` verifies the reviewed plan subject and evidence string but never substitutes a different valid authority locator; router Plan Review fixtures always use the expected requirements path.
- Reproduction artifact, if any: `repros/repro_adversarial.py` (`repro_f5_plan_review_acceptance_is_not_bound_to_definition`).

## Non-blocking observations

The SessionStart bootstrap checks the bundled router for two marker strings and root containment but does not cryptographically bind router documentation to `tools/router.py` or verify the selector exists. I did not elevate this to a material finding because the audited contracts do not state a sufficiently precise installed-package integrity mechanism to prove that marker-level validation alone is a semantic violation.

`PurePosixPath` normalization means explicit `.` path components are normalized before the code tests for `"." in parts`; I did not find a concrete authority escape or cross-workstream bypass from that behavior at this subject.

## Coverage

Primary attack lenses selected from `AUDIT_SUFFIX`:
1. stale commit/blob/path/result/review identity;
2. helper vs documented semantics / parity drift / negative space;
3. plugin / install / update / SessionStart / bootstrap drift;
4. Planning / Premium gates / Execution precedence.

Inspected the canonical router and workflow contracts including `workflow/ROUTER.md`, `STATE.md`, `AUTHORITY.md`, `PLANNING.md`, `PLAN_REVIEW.md`, `EXECUTION_PREP.md`, `EXECUTION.md`, `REVIEW.md`, `BRAINSTORMING.md`, `RESEARCH.md`, `DEFINITION.md`, and `USER_STOP.md`; production helpers `tools/router.py`, `state_contract.py`, `execution_contract.py`, and `recovery_contract.py`; delivery/bootstrap files under `hooks/`, `.codex-plugin/`, `.agents/plugins/`, `skills/`; and the relevant regression suites in `tests/test_router.py`, `test_state_contract.py`, `test_execution_contract.py`, `test_chatgpt_delivery.py`, and `test_codex_delivery.py`.

Negative-space cases were constructed for unchanged SHA labels with changed bytes, upstream Definition changes under stale Planning, malformed implementation identity, deleted evidence, and unrelated Plan Review acceptance authority. A non-mutating executable repro script is persisted with the report.

## Confidence and limitations

Confidence is high for F1, F3, F4 and F5 because the fail-open path is direct in production code and the existing tests explicitly leave the negative-space case uncovered. Confidence is medium-high for F2 because the contracts clearly require Planning to derive from current Definition authority, while no cross-record freshness binding exists; the exact serialized format of `entry_subject` is intentionally not specified, so the finding is about the missing binding, not a required string format.

I could not execute the production Python selector in this audit environment: the generic container has no GitHub network access, and the connected Desktop Commander device had exhausted its monthly tool-call quota. The preserved reproduction script therefore records executable falsifications constructed against the exact audited source but was not run here. Existing source/tests were read from the immutable subject commit.

Blindness caveat: before this audit execution, a status check in the immediately preceding chat turn enumerated audit branch names and head SHAs. No audit branch contents, swarm reports, Issues, PR comments, historical evidence, or reviewer conclusions were opened or used. The finding set above was frozen solely from the target commit's allowed production/contracts/tests surface. No post-freeze historical comparison was performed.
