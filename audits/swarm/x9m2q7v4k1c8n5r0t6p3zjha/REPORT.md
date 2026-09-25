# PWv2 Adversarial Swarm Audit

Repository: `elmakus/project_workflow_v2`  
Exact immutable subject: `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`  
Audit suffix: `x9m2q7v4k1c8n5r0t6p3zjha`

## Verdict

**FINDINGS FOUND** — 4 material findings.

## Material findings

### F1 — READY launch trusts self-asserted commit/blob metadata instead of verifying dependency content

**Affected contract / invariant.** `workflow/STATE.md` and `workflow/EXECUTION_PREP.md` require READY predecessor dependencies to be bound by result path plus immutable commit/blob identity, with missing, stale, or same-path-changed inputs failing closed before execution.

**Expected behavior.** If the dependency result file changes while the Task Card and Task Board still claim the previous `path@commit:blob`, launch refresh must detect the content/identity mismatch and route to Recovery.

**Actual behavior.** In `tools/router.py`, `refresh_ready_card()` builds the DONE-result identity set entirely from Task Board metadata, compares the Task Card dependency tuple against that metadata, and then merely reads the dependency file. It never resolves the claimed commit, verifies that the path at that commit has the claimed blob, or verifies current file content against that blob. `tools/state_contract.py` similarly checks the commit/blob values only as 40-hex strings.

A same-path content mutation with unchanged metadata therefore still reaches `route/execution_prep`.

**Minimal reproduction.** Run:

```bash
python3 audits/swarm/x9m2q7v4k1c8n5r0t6p3zjha/repros/f1_dependency_content_drift.py
```

The repro changes only the dependency file contents while preserving the claimed dependency metadata. The observed selector path remains `execution_prep`; the contract requires fail-closed Recovery.

**Why load-bearing.** Downstream implementation can execute against predecessor content different from the supposedly immutable result identity. This defeats launch freshness and can propagate stale or unreviewed semantics.

**Defect class / likely siblings.** Unverified immutable identity / fail-open stale-content acceptance. The same trust pattern appears in plan/review/result Git subjects where validators establish syntax and string equality but do not establish repository-object truth.

**Existing tests that missed it.** `test_ready_card_stale_dependency_fails_closed_before_launch` changes both the Board commit/blob metadata and the dependency file. The router catches the metadata tuple mismatch; it does not test file-only same-path drift.

**Reproduction artifact.** `repros/f1_dependency_content_drift.py`

### F2 — GREEN review can finalize with missing terminal evidence

**Affected contract / invariant.** `workflow/REVIEW.md` requires durable verdict evidence for terminal review attempts, and REQUIRED/activated RECOMMENDED review must block terminal Card completion until exact GREEN.

**Expected behavior.** A terminal GREEN attempt whose `evidence_path` is missing or unreadable must be invalid and fail closed rather than authorize finalization.

**Actual behavior.** `validate_review()` requires only a non-empty safe relative `evidence_path` for GREEN/RED. It does not verify that the evidence path exists or is readable. The router loads review TOML, validates history and subject strings, then routes an exact GREEN directly to `post_review_finalization` without reading the evidence file. The same validation pattern exists for Plan Review evidence.

Deleting the evidence file after a GREEN attempt therefore leaves the review gate satisfied.

**Minimal reproduction.**

```bash
python3 audits/swarm/x9m2q7v4k1c8n5r0t6p3zjha/repros/f2_missing_review_evidence.py
```

The repro creates the normal GREEN fixture attempt, deletes its evidence Markdown, and the selector still returns `route/post_review_finalization`.

**Why load-bearing.** The independent-review gate can become a TOML assertion with a dangling path. Durable evidence required for audit/recovery may be absent while the workflow deterministically finalizes the Card.

**Defect class / likely siblings.** Review-gate fail-open / dangling evidence locator. Plan Review evidence has the same validation shape.

**Existing tests that missed it.** `test_review_terminal_evidence_and_append_only_history` checks only an empty evidence string. `test_required_review_blocks_until_green_then_routes_finalization` creates the evidence file and never removes it.

**Reproduction artifact.** `repros/f2_missing_review_evidence.py`

### F3 — Active Research masks an explicit user stop despite declared precedence

**Affected contract / invariant.** `tools/router.py` declares `explicit_human_or_premium_boundary` above `research_return` in `PRIORITY_FOUNDATION`. PWV2-REQ-067/068 makes an explicit user stop a real stop. `BRAINSTORM.toml` durably owns `explicit_user_stop`.

**Expected behavior.** When a workstream carries a valid explicit user stop and also has active Research, routing must honor the higher-precedence human boundary, or fail closed if the combined state is contradictory. It must not continue Research past the stop.

**Actual behavior.** The selector reads and dispatches active/completed top-level Research before it reads Brainstorming state. The explicit user-stop check occurs only later. `validate_brainstorm()` accepts the stop flag and `validate_research()` independently accepts active Brainstorming-origin Research; there is no cross-record guard forbidding the combination.

Thus the declared precedence tuple is not enforced for this combination: the selector returns `route/research` rather than `stop/explicit_user_stop`.

**Minimal reproduction.**

```bash
python3 audits/swarm/x9m2q7v4k1c8n5r0t6p3zjha/repros/f3_user_stop_precedence.py
```

**Why load-bearing.** A durable explicit human stop is a hard agency boundary. Continuing an agent-owned factual obligation after that stop is an illegal transition across the router's highest-precedence class.

**Defect class / likely siblings.** Router precedence inversion / real-stop bypass. Any higher-precedence stop stored in a record read after an earlier-returning obligation deserves analogous co-bound tests.

**Existing tests that missed it.** `test_priority_and_real_stop_foundations_are_runtime_neutral` asserts the constant ordering only. Research routing and Brainstorming stops are tested separately, not co-bound.

**Reproduction artifact.** `repros/f3_user_stop_precedence.py`

### F4 — Arbitrary Intake string can bypass mandatory issue prior-art Research

**Affected contract / invariant.** `workflow/INTAKE.md` requires a concrete issue repair subject to materialize proportional Intake-origin Research, apply and consume that exact result, and only then persist the diagnosis-prior-art subject/result binding. PWV2-REQ-049 makes the proportional prior-art check mandatory.

**Expected behavior.** An authorized/completed issue with no qualifying Research provenance must route to the missing Research/reconciliation obligation or fail closed. A self-asserted string must not stand in for the required consumed Research result.

**Actual behavior.** `validate_intake()` models `diagnosis_prior_art_result` as an unconstrained string and, for authorization, requires only that it be non-empty while the prior-art subject equals `repair_subject`. The router then defines stable diagnosis prior art as that subject equality plus a non-empty result string. Once those two fields are present it skips the exact Research provenance check.

A completed authorized issue with `diagnosis_prior_art_result = "forged-no-research"`, no Research locator, and an existing Task Board therefore continues directly to implementation routing.

**Minimal reproduction.**

```bash
python3 audits/swarm/x9m2q7v4k1c8n5r0t6p3zjha/repros/f4_forged_prior_art_binding.py
```

The base fixture's live Card routes to `execution` despite no Intake-origin Research record being materialized.

**Why load-bearing.** This bypasses the mandatory diagnosis/prior-art precondition before repair implementation. User authorization may be exact while the factual/provenance prerequisite is fabricated.

**Defect class / likely siblings.** Authorization-precondition bypass / unverified provenance token. Any durable field used as proof of a previously completed mandatory obligation needs provenance stronger than a free-form non-empty string.

**Existing tests that missed it.** Current Intake tests reject empty or stale bindings. `test_completed_authorized_issue_continues_to_existing_board` installs valid Research but there is no negative case with a non-empty forged binding and no qualifying Research provenance.

**Reproduction artifact.** `repros/f4_forged_prior_art_binding.py`

## Non-blocking observations

- `validate_research()` classifies execution return targets with prefix checks such as `startswith("execution:")` without requiring a non-empty subject suffix. A value such as `execution:` can therefore pass the return-target class check. This was not promoted because the four findings above establish stronger fail-open paths.
- Several unit fixtures intentionally use synthetic values such as `"a"*40` and `"b"*40`. That is useful for isolated tests, but it also means those tests prove internal string consistency rather than Git-object truth.

## Coverage

Four attack lenses were frozen before detailed inspection:

1. immutable-subject-and-content identity;
2. review-evidence-and-gate integrity;
3. router precedence and real stops;
4. issue-diagnosis prior-art authorization boundary.

Files examined from the exact immutable subject include:

- `requirements/PROJECT_WORKFLOW_V2.md`;
- `workflow/ROUTER.md`, `STATE.md`, `INTAKE.md`, `RESEARCH.md`, `BRAINSTORMING.md`;
- `workflow/EXECUTION_PREP.md`, `REVIEW.md`, `RECOVERY.md`, `CLOSE.md`;
- `tools/router.py`, `state_contract.py`, `execution_contract.py`, `recovery_contract.py`, `close_contract.py`;
- `tests/test_router.py`, `tests/test_state_contract.py`, and `scripts/test.sh`.

No moving-`main` state was used as semantic audit authority. Other swarm report contents, GitHub Issues, PR discussions/comments, and historical diagnosis/review artifacts were not inspected before the finding set was frozen.

## Confidence and limitations

Confidence is **high** for the four reported control-flow/validation defects. Each follows directly from the frozen router/validator implementation and has a minimal runnable repro built from the repository's own fixture helpers.

Execution limitation: an isolated local run was attempted on the connected Tower, but Remote Desktop Commander reported that its monthly tool-call quota was exhausted and explicitly instructed not to retry. GitHub reported no workflow runs directly associated with the exact merge commit. Therefore this report does **not** claim captured local repro stdout or exact-subject CI execution in this audit session; the deterministic repro scripts are persisted for execution in any checkout of the audited commit.

This audit did not mutate canonical Project Workflow state, `main`, other work branches, Issues, pull requests, comments, or merges.
