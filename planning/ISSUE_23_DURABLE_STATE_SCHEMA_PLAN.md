# Issue #23 — Durable-state parity and bounded intra-V2 reconciliation — P2

## Exact planning authority and material delta

- Workstream: `implementation/workstreams/issue-durable-state-schema/WORKSTREAM.toml`.
- Definition: `DEFINITION.toml`, revision **R2**, unchanged promoted scope `durable-state-schema-contract-parity@1`.
- Planning: cycle **2**, revision **P2**, exact entry `definition:R2|planning-cycle:2`; premium A is satisfied for that entry.
- Accepted requirements: `requirements/ISSUE_23_DURABLE_STATE_SCHEMA.md` R2; decisions: `decisions/ISSUE_23_DURABLE_STATE_SCHEMA.md` D1–D7.
- Correction evidence: `implementation/workstreams/issue-durable-state-schema/evidence/DEFINITION_R2_FIXTURE_CORRECTION.md` and `evidence/M02_REAL_SOURCE_AUTHORITY_CONFLICT.md`.

P2 replaces P1's strategy, not its historical approvals. Real pre-Recovery #20 and #22 are **negative Recovery fixtures**, not positive migration promises. Positive older-V2 coverage uses the independently evidenced historical Planning contract described below. There is no #20 reopening/readiness work, #26 pending-attempt replacement, new product scope, or transfer of P1's A/B/C to P2.

## Existing implementation and execution boundary

1. **M01-T01 is DONE and independently GREEN.** Retain its accepted Result at `implementation/workstreams/issue-durable-state-schema/results/M01-T01.md@d15defabd601348bfba68db89941ee755f855367:aedcd2262a1b0a01ebde710ea186e2d65498dd0b`. Do not rerun or reapprove M01 solely because of replan.
2. **M02-T01 is blocked, with no accepted Result/review.** `tools/v2_reconciliation.py` and `tests/test_v2_reconciliation.py` at `d524ce429d4759be4555916f16b182de81fb8b33` are unaccepted experimental implementation. Passing synthetic tests does not establish an evidenced real-source reconciliation profile.
3. Task Board revision 8, original M02 Card, blocker and P1 Plan Review **artifact** remain unchanged during Planning/B/Plan Review/C. The WORKSTREAM's single current `plan_review` locator still names P1; before freezing P2, remove this now-stale locator by a validated WORKSTREAM write, retaining the P1 attempt file and Git evidence unchanged. Do not let the router validate a P1 attempt against P2 or silently overwrite the P1 file. Bind the new P2 attempt only after exact B satisfaction. Their historical Git subjects must remain readable.
4. Only after exact P2 GREEN review consumption and premium C may Execution Prep/Recovery reconcile the plan-strategy correction into the blocked M02 Card. Explicitly re-contract M02-T01 against approved P2/R2 before unblocking it; retain the original contract at `6607b9d` in Git and record the replacement basis in workstream-local evidence. This is an owner-classified material plan correction, not L1/L2 JIT editing of a started contract. Do not mark the old work DONE, fabricate a Result, remove old review evidence, add a cancellation status, or create a competing Card/Task Board.
5. Refresh exact M01 dependency, current accepted authority and replacement Card before launch. If the owning Recovery/Execution Prep contract cannot lawfully reconcile that correction, fail closed there rather than inventing a supersession protocol. P2 approval is not permission to change workflow legality.

## Strategy

Keep `tools/state_contract.py` and its production validators as the single executable current-schema authority. Canonical producer success passes through M01's validated rendering/write boundary. Reconciliation builds a fully validated, source-bound output plan before mutation and never guesses semantic authority from schema-invalid prose.

Separate three facts:

- current canonical production must be resumable;
- an explicitly evidenced older schema can receive a representation-only mapping;
- real malformed historical reproductions with unprovable authority remain Recovery.

Do not import V1 policy, generalize old fixture-only migration, or add runtime identity, schema registries per stage, workflow phases or a parallel migration/approval ledger.

## M01 — Preserve the accepted validated-write foundation

No new implementation Card is required for accepted M01. Its record-kind dispatch, generic TOML serialization and validate/render/parse/validate/write boundary remain the foundation for all subsequent work.

M03/M04 requalify the registered current record kinds and producer-owner references. If they reveal a bounded defect in that foundation, correct it through canonical execution/review against the new exact result; do not retroactively rewrite the accepted M01 Result or GREEN attempt.

## M02 — Evidenced reconciliation, authority preservation and safe apply

### Supported positive profile: pre-review-classification Planning

Profile name: `planning-pre-review-classification-v1`.

Historical evidence is executable contract `tools/state_contract.py@7cd4617c5bfcbbc9de9adaf550387191cf3896a6` (blob `b6d4a59b65d0fa7e5ab7983c72b5b5c17d281d02`) and its `workflow/PLANNING.md` / `workflow/PLAN_REVIEW.md` semantics (blobs `e38e1a7b3b82123b91f95e2b2bc2e768cec63c17` / `3dd6189e1f40e2cff677482e074643766979dc3d`). That contract has exact cycle/entry, A/B/C subjects, immutable repository/commit/path/blob, frozen/approved lifecycle, and same-subject independent Plan Review, but not the later three review-classification fields. Its owner modules already require independent Stage-6 review; no editorial exemption exists to infer.

The sole mapping adds:

- `review_mode = "independent"`;
- `review_exemption_basis = ""`;
- `review_exemption_base_subject = ""`.

All other data, exact plan subject, Definition/Intake authority, gate values/subjects and review bytes remain unchanged. This changes the Planning record representation, **not the immutable plan artifact subject**. Do not rename paths, rewrite plan text or supply missing gate/subject/authorization fields.

Recognition must require all three classification fields absent, no mixed/partial classification or unsupported extras, historical-profile evidence and exact source-set fingerprints, current valid surrounding owners, and successful current production validation after precisely this additive mapping. A structurally plausible input is not sufficient proof of approval: verify exact Git objects and cross-owner cycle, entry, acceptance and review relations. Preserve satisfied B/C only with valid matching durable review/authority evidence; absence, contradiction or unverifiable subject remains Recovery. No caller-supplied 40-hex strings are accepted as proof without repository object/readback verification.

For reproducible positive qualification, construct an explicitly labeled **controlled historical-contract fixture**, not a claimed historical production incident:

- start with the immutable R1/P1 snapshot at `4975b12fe3b330b1cee9ee0048e4421c7df3dfca`, whose Planning blob is `0d513a5bad4dc0260c5db15398d7c1fe5ff4a6f6`;
- omit exactly the three later classification fields, retaining the snapshot's R1 authority and exact GREEN Plan Review unchanged in a sandbox;
- prove the source satisfies the pinned historical validator and historical independent-review semantics;
- prove the current validator rejects it before mapping, accepts it after mapping, and a fresh consumer resumes at the intended premium/review/Execution Prep boundary;
- use declared lifecycle variants for frozen B-due, B-satisfied/pending review, and approved C-due/satisfied. Variants are synthetic trajectory inputs with explicit provenance, not new approvals in the real workstream;
- the retained plan subject is `elmakus/project_workflow_v2@8c009500dc1cdc98baa88613a8d5b258cba5791a:planning/ISSUE_23_DURABLE_STATE_SCHEMA_PLAN.md@ea1f3a1a034e180a9b21df5588011c624aa6782f`.

The old validator is test/provenance evidence only, not a second production-schema implementation. The current validator owns every output. Never transplant this fixture's R1/P1 approvals into live R2/P2.

### Negative historical profiles and experimental disposition

- #20 at `af76106415504c746668113d1df46a411fdcebd7`, workstream `issue-paseo-child-delegation`, remains negative Recovery: fragment/prose authority, unproven frozen identity and noncanonical plan path are not repair permission. Do not reopen the issue or implement optional readiness.
- #22 at `51c5ebccca4ea1b4e1fd60b3f36dddc5fb2e72d2`, workstream `issue-ci-pending-continuation`, remains negative Recovery. Its pending `reviews/M01-T01-R01.toml` blob `87db02e2fe07c557418e9fb21e22802e7f78c319`, subject `git_commit` at `32e7971f96e76a403de6bc5cd7b8d5979ac0dfe2:tools/continuation_contract.py`, must remain byte-for-byte unchanged. No dropping, rebinding, replacement attempt or #26 dependency is authorized here.
- Replace the experimental reconciler's misleading `issue20-*`/`issue22-*` positive-profile claims. Its broad synthetic integer/enum/locator coercions are not approved production mappings. Retain useful apply/validation techniques only after qualification; quarantine/remove unsupported normalization from production dispatch. Synthetic unit logic is labeled as such, never counted as positive historical coverage.

### Authority and subject-change rules

1. Same immutable subject + exact semantic/cross-owner proof: retain eligible existing authority; never upgrade a pending attempt to GREEN or an unsatisfied gate to satisfied.
2. A separately lawful canonical subject change: do not copy the old B/Plan Review/C or implementation-review approval. Keep old attempts attached to their subjects; use the existing Planning/review correction owners to create the fresh exact gates/attempt required for the changed subject. A material plan correction creates a new cycle with A due; B becomes due on the newly frozen subject and C only after exact GREEN consumption.
3. Missing identity, unproven subject mapping or absent authorization: Recovery with **no mutation**; do not silently manufacture a draft cycle or infer a subject from current files.
4. An implementation result change cannot inherit prior GREEN; the changed exact result requires its own lawful independent attempt. Reconciliation never replaces #22's reserved attempt.

The additive positive profile does not itself need to change the plan subject. Subject-change/reset behavior is qualified through the existing canonical correction/production transition, with an explicit changed-subject negative for reconciliation, rather than by inventing another migration profile.

### Plan/apply safety

Before writing, build a complete in-memory plan binding the recognized profile/provenance, exact source paths/bytes/fingerprints, cross-owner/Git evidence, exact outputs, preservation decisions and production validation results. Parse source bytes and derive records from those same bytes: caller dictionaries cannot disagree with the fingerprinted TOML.

Revalidate the plan and complete file set before apply. Reject tampered outputs, unsafe paths/symlinks, foreign workstreams, unknown files and any source divergence before mutation. Accept a file only as exact expected-before or exact already-produced-after. Persist exclusively through M01's validated boundary. Interrupted exact before/after sets converge deterministically; completed/current sets are no-ops. Reconstruct a retry from immutable source/evidence and local before/after bytes, not process memory or a new canonical migration journal. No external tracker operation or duplicate approval/attempt/effect occurs.

Integrate with `workflow/RECOVERY.md` only: invalid V2 state can use this expressly supported proven mapping; unsupported states remain Recovery. Router semantics and premium/review authority are unchanged.

### Acceptance and review

A source-bound positive older-V2 premium/review resume succeeds with unchanged exact semantic authority; both real historical reproductions fail closed unchanged. Changed/unproven subjects never inherit approval. Tampering, ambiguous input and partial/divergent apply are covered. Outputs use the single current production validator. **Independent implementation Review REQUIRED**, against a committed exact accepted Result after correction/qualification, not the experimental commit alone.

## M03 — Transition-level regression and independent fresh resume

After accepted M02 Result, materialize a bounded regression Card with exact M01/M02 DONE dependencies.

1. Cover every record kind registered by M01's production dispatch, including contextual validators. Test actual validated producer writes and fresh consumption, not only hand-written static fixtures.
2. Build the pre-execution chain through canonical Intake/Research/Definition/Planning/Plan Review producers. Fresh invocation reaches B on a newly frozen exact plan; a valid independent review fixture is consumed toward C/Execution Prep without schema Recovery. Independent here means a fresh consumer/context of persisted bytes, not a real LLM test requirement.
3. Vendor exact #20/#22 pre-Recovery bytes with repository/commit/path/blob provenance so tests do not depend on mutable branch tips. Include the surrounding relevant owners and #22 reservation. Assert direct consumer rejection, producer refusal, reconciliation rejection and byte-identical state after rejected apply. Prove no #20 reopening or #22 attempt replacement.
4. Exercise the controlled historical-contract positive fixture across B, pending/GREEN review and C, proving unchanged authority and no replay. Distinguish it from the two actual negative incidents in test names and evidence.
5. Test same-subject approval preservation; lawful subject-change gate/attempt reset without rewriting prior review history; missing/ambiguous evidence Recovery; mixed current/legacy fields; malformed enums/types; input bytes/data mismatch; plan/output tampering; source-set divergence; idempotent replan/reapply; restart at every partial-write boundary with a freshly reconstructed plan; already-current no-op.
6. Run focused state/write/router/recovery/review/reconciliation suites, existing V1 migration suites and the full repository suite. Use synthetic fixtures and local subprocess consumers, with no real LLM inference required.

Acceptance: fresh production and positive supported resume reach their exact expected obligations; both supplied historical incidents remain negative Recovery; current unrelated workflow semantics and authority boundaries are unchanged. **Independent implementation Review REQUIRED** because the tests qualify authority retention/reset and safe reconciliation, not just documentation.

## M04 — Documentation convergence and final qualification

After accepted M03 Result, materialize a bounded final qualification Card with exact DONE predecessor identities.

1. Update `workflow/STATE.md` and only producer/recovery owner documentation needed to name the single executable write/reconciliation boundary. Preserve semantic policy rather than restating another schema in prose.
2. Correct experimental profile claims and document the narrowly supported positive source shape, provenance, failure behavior and distinction from #20/#22 negative fixtures.
3. Add documentation/qualification assertions for producer-boundary references and Recovery's explicit supported profile. No permissive promise to normalize arbitrary old V2 files.
4. At the exact committed subject, run full tests and fresh subprocess trajectories for canonical fresh production, supported historical-schema resume and both historical Recovery negatives. Read back changed/excluded blobs and unchanged #22 reservation; bind evidence to that exact implementation subject.
5. Follow common Review/finalization/Close and integration rules until approved-scope completion. Card/milestone completion is not itself a stop; no integration/live mutation is preauthorized by this plan.

Acceptance: one current schema authority, validated producer success, evidence-backed bounded reconciliation, unchanged authority/runtime separation, and no unresolved historical-positive claims. Review **RECOMMENDED** if only documentation/qualification is changed; escalate to REQUIRED if production/authority behavior is corrected.

## Card/dependency and gate strategy

Order remains M01 → M02 → M03 → M04. Reuse accepted M01; explicitly reconcile/re-contract the blocked M02 after approved P2/C. Keep M03/M04 as bounded predecessor-dependent JIT triggers until exact accepted results make their contracts knowable. Only one Card may be in progress; no parallel canonical writer or speculative placeholder Card.

P2 authoring → GREEN planner audit → validated removal of the stale P1 current-review locator (preserving its file) → freeze exact Git-blob subject → premium B due → **fresh independent Main Plan Review** → Planning consumes exact GREEN → premium C due → Execution Prep. P1's GREEN review remains immutable historical evidence, not P2 approval. Use a new P2 pending attempt/locator at the lawful review entry; do not overwrite P1 evidence or reuse its attempt subject. RED correction follows common owner classification and fresh material cycle gates.

## Requirement/decision coverage and planner challenge audit

| Accepted requirement | Strategy / observable coverage |
| --- | --- |
| R1–R5, D1–D2, D7 | Retained accepted M01; M03 registered-kind producer/consumer parity and fresh transitions; M04 documentation qualification. |
| R6–R7, D3, D6 | M02 one historical-contract-evidenced additive profile; actual #20/#22 negative Recovery; no synthetic-profile masquerade or guessed migration. |
| R8, D4 | Exact source/Git/cross-owner proof; unchanged authority and review bytes; positive sandbox retains R1 authority only. |
| R9, D5 | Same-subject preservation; lawful canonical subject-change gates/attempts reset; unproven changes fail closed; old evidence never rebound. |
| R10 | No synthesized authorization or missing subject; no #20 reopening, #26 replacement, tracker authority or scope expansion. |
| R11 | Bytes-derived source plan, validation before mutation, tamper/divergence rejection, reconstructed restart and current-state no-op. |
| R12 | Fresh materialization/resume; exact two negative incident fixtures; positive older-schema B/review/C trajectory; identity/reset/ambiguity/restart matrix. |
| R13 | No model/session/worker identity, second state store, runtime orchestration or phase. |

**Planner audit: GREEN.** The previous contradiction is removed without changing R2/D1–D7. The positive profile has a pinned historical executable and semantic contract, not hypothetical field coercion; a direct Planning-time feasibility probe validated the controlled source under that historical contract, observed current rejection, then validated the additive output and unchanged exact GREEN Plan Review. This is bounded strategy feasibility, not acceptance of the experimental M02 implementation. The plan retains completed work and failed/unaccepted evidence, names a lawful owner boundary for the blocked Card correction, requires exact independent implementation reviews and tests real transitions. It does not claim P2 approval, Stage-6 review, satisfied B/C, or completed implementation before those obligations occur.
