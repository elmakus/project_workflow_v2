# PWv2 Adversarial Swarm Audit

## Verdict

FINDINGS FOUND

## Material findings

### F1 — Pre-repair issue diagnosis is incorrectly converted into an alignment stop

- Affected workflow contract/invariant: `workflow/INTAKE.md` requires read-only issue diagnosis first and only introduces alignment after a concrete repair outcome exists; `workflow/ROUTER.md` says the no-response stop is a post-diagnosis/alignment obligation and malformed or contradictory state must fail closed rather than inventing a user gate.
- Expected behavior: An active issue Intake with no concrete `repair_subject`, no response, and pending alignment remains owned by Intake so diagnosis can continue.
- Actual behavior: `validate_intake()` accepts that state. In `tools/router.py`, the prior-art branch is skipped because `repair_subject` is empty, but the later active-issue branch sees `alignment_state = "pending"` plus `response_kind = "none"` and returns `stop / issue_alignment` with an empty subject. A legal continuation is rejected before a repair proposal exists.
- Minimal reproduction: Copy `tests/fixtures/router/valid-project`, add an Intake locator, and create `INTAKE.toml` with `kind="issue"`, `state="active"`, `repair_subject=""`, `response_kind="none"`, and `alignment_state="pending"`. `select_route()` selects `("stop", "issue_alignment")`; the contract requires continued Intake diagnosis.
- Why this is materially load-bearing: It manufactures a human authorization/alignment boundary where no repair subject exists, stopping legal issue diagnosis and changing workflow authority/precedence.
- Defect class / likely siblings: Missing phase predicate around alignment routing. Pending question/concern variants before a concrete repair subject should also be checked because the router currently keys only on issue + pending alignment, not on existence of the subject being aligned.
- Existing tests that failed to catch it: Router issue-alignment tests always install a non-empty repair subject before exercising no-response/question/authorization routing. There is no durable pre-repair issue-Intake continuation case.
- Reproduction artifact, if any: `repros/f1_pre_repair_issue_stop.py`

### F2 — Intake prior-art proof can be fabricated with any non-empty string

- Affected workflow contract/invariant: `workflow/INTAKE.md`, `workflow/RESEARCH.md`, and `workflow/STATE.md` require the exact consumed/applied Research result for the exact repair subject to be durably bound into Intake before repair alignment/implementation can proceed.
- Expected behavior: The Intake-owned prior-art binding must be demonstrably derived from the exact applied/consumed Research result; missing, mismatched, fabricated, or unverifiable result identity must fail closed or require Research reconciliation.
- Actual behavior: `validate_intake()` validates only that `diagnosis_prior_art_subject == repair_subject` and that `diagnosis_prior_art_result` is non-empty. The router's `stable_diagnosis_prior_art` predicate repeats the same two checks. It neither validates the result as a locator/identity nor checks it against a Research record. Therefore an authorized issue can set `diagnosis_prior_art_result = "forged:never-produced"` with no Research record at all, satisfy the mandatory prior-art gate, and continue into implementation.
- Minimal reproduction: Add a completed/authorized issue Intake to the valid router fixture with matching `repair_subject` and `diagnosis_prior_art_subject`, set `diagnosis_prior_art_result` to an arbitrary non-empty string, and do not materialize a Research record. `select_route()` proceeds to the existing executable Card instead of requiring Research/recovery.
- Why this is materially load-bearing: This is a direct bypass of the mandatory diagnosis-prior-art obligation and turns unauthenticated text in mutable state into evidence that unlocks implementation.
- Defect class / likely siblings: Exact-result bindings represented as unchecked free-form strings. Any consumer that treats `return_result`/diagnosis result text as durable identity without validating provenance or exact equality is in the same class.
- Existing tests that failed to catch it: Tests use strings such as `evidence/intake-prior-art.md` and assert only non-empty/stale-subject behavior. No negative test supplies a nonexistent or mismatched result binding, and no test requires equality to an exact consumed Research return.
- Reproduction artifact, if any: `repros/f2_forged_prior_art_binding.py`

### F3 — DONE Cards route to Close without dereferencing result, contract, or required review state

- Affected workflow contract/invariant: `workflow/STATE.md` says a durable valid result is recovery truth, REQUIRED/activated RECOMMENDED review blocks terminal completion until exact GREEN, and invalid/missing/stale bindings fail closed. `workflow/ROUTER.md` routes all current Cards terminal to Close only after those durable semantics are valid.
- Expected behavior: Before treating a Card as terminal, recovery must prove that its result artifact exists and is valid for that Card/current immutable subject, and that any required independent review is exact GREEN.
- Actual behavior: `validate_board()` only requires a DONE Card to contain a syntactically shaped result locator; it does not dereference the result, parse the Card contract, or verify review requirement/history. The router only performs those checks for an `in_progress` Card. If every Card is marked `done`, it immediately returns `route / close`. A DONE Card can therefore point at a nonexistent result file and have a valid contract requiring review with zero review attempts, yet still enter Close.
- Minimal reproduction: In the valid router fixture, set the sole Card to `status="done"`, give it an exact-looking result locator whose file is absent, and make the Card contract require review without adding any review attempt. `select_route()` returns `("route", "close")` and its read set never opens the Card contract or result.
- Why this is materially load-bearing: A single stale/corrupt/manual terminal-state mutation can bypass semantic result verification and mandatory independent review, then hand an unproven workstream to finalization/integration.
- Defect class / likely siblings: Terminal-state trust gap: semantic checks are attached only to the active-card path instead of being invariants of terminal Cards. Siblings include path-only/mismatched result identity and terminal RED/pending review history that is never revalidated.
- Existing tests that failed to catch it: `test_all_terminal_cards_route_to_close_not_directly_to_stop` marks a no-review Card DONE and expects Close; no negative test makes a DONE Card's result missing/invalid or its review requirement unsatisfied.
- Reproduction artifact, if any: `repros/f3_done_card_bypasses_terminal_checks.py`

### F4 — SessionStart accepts stale/counterfeit router content if two marker strings survive

- Affected workflow contract/invariant: `skills/project_workflow_v2/SKILL.md` and the SessionStart bootstrap require the bundled canonical router to be present, unambiguous, and not malformed; malformed bootstrap authority must fail closed. The router is the semantic authority entrypoint.
- Expected behavior: A partial/stale/corrupted installed router must not be advertised as the canonical V2 router merely because superficial text markers remain.
- Actual behavior: `hooks/session-start.py::canonical_router()` authenticates router content only by checking for the header string `# Project Workflow V2 Router` and selector string `Production selector: \`tools/router.py\`.`. Any stale, truncated, or counterfeit file retaining those two literals passes and produces the normal "package is enabled" context.
- Minimal reproduction: Copy the production hook to a temporary package, replace `workflow/ROUTER.md` with just the two accepted marker lines plus arbitrary contradictory policy text, set `PLUGIN_ROOT` to that temporary root, and execute the hook. It emits a non-blocking canonical-router context rather than the blocking package error.
- Why this is materially load-bearing: Ordinary partial update/install drift can silently promote the wrong policy blob to bootstrap authority. Once accepted, every later obligation selection may be based on non-canonical semantics.
- Defect class / likely siblings: Identity-by-content-substring instead of package/version/blob integrity. A stale router from an older release is especially likely to retain both markers and pass.
- Existing tests that failed to catch it: `test_missing_and_malformed_router_fail_closed` only replaces the router with text lacking the markers. No test preserves the markers while changing/truncating the semantic body or tests cross-file/version coherence.
- Reproduction artifact, if any: `repros/f4_sessionstart_marker_spoof.py`

## Non-blocking observations

No additional advisory item was promoted. The Close helper truth table inspected for end-of-scope, explicit authorization gates, target refresh, external-effect readback, tracker closure, and cleanup appeared internally consistent for the exercised combinations; no material Close-specific defect was independently demonstrated.

## Coverage

The audit was bound to commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045` and inspected the exact Git tree for canonical workflow modules, production router/state/close/recovery helpers, bootstrap hook/Skill/plugin manifests, templates, and relevant tests. The four seeded lenses exercised were:

1. plugin / install / update / SessionStart / bootstrap drift;
2. Research / Intake / tracker / external-side-effect recovery;
3. Close / finalization / end-of-approved-scope;
4. malformed or contradictory state / fail-closed behavior.

Concrete negative-space states were constructed against the production control flow for Intake with no repair subject, fabricated prior-art binding, terminal Cards with missing semantic artifacts/review, and marker-preserving bootstrap corruption. No `audit/*` branches, other swarm reports, GitHub Issues/PR comments, or historical implementation evidence/review directories were consulted for discovery.

## Confidence and limitations

Confidence is high in the four control-flow/state-validation defects because each follows a short deterministic production path and the preserved repros instantiate the exact missing predicate or unchecked binding.

The audit environment had authenticated read/write GitHub access but no networked local checkout, so the exact production Python could not be executed locally during discovery. The reproduction scripts are non-mutating and are preserved for execution from this exact branch/commit lineage. Existing repository tests were inspected to confirm the negative cases are absent. No post-freeze historical comparison was performed.
