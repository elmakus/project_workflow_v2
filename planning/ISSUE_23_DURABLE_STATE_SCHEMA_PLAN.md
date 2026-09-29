# Issue #23 — Durable-state schema parity and intra-V2 reconciliation plan

## Planning authority

- Definition: `implementation/workstreams/issue-durable-state-schema/DEFINITION.toml` revision `R1`
- Requirements: `requirements/ISSUE_23_DURABLE_STATE_SCHEMA.md`
- Decisions: `decisions/ISSUE_23_DURABLE_STATE_SCHEMA.md`
- Intake diagnosis evidence: `implementation/workstreams/issue-durable-state-schema/evidence/INTAKE_PRIOR_ART.md`
- Authorized repair subject is unchanged. This plan does not alter unrelated workflow, premium-gate, review, execution-orchestration or product semantics.

## Strategy

Repair the producer/consumer mismatch at the executable state boundary rather than by adding more prose-only examples. Successful canonical production must pass the same `tools/state_contract.py` validators that the router consumes. Add one deterministic intra-V2 reconciliation mechanism under Recovery for explicitly supported legacy shapes; it may preserve authority only when exact semantic/immutable identity is provable and otherwise resets the affected subject-bound gate or fails closed.

Do not generalize the old fixture-only V1 migration machinery into a second state authority. Reuse its proven restart/fingerprint techniques only where they can be made generic without importing V1 semantics.

## M01 — Canonical validated state-write boundary

### Goal

Make it impossible for a canonical producer path to claim a successful durable-state transition with a record that the current canonical consumer rejects.

### Work

1. Add a small generic state-write/render boundary adjacent to `tools/state_contract.py`.
   - Record-kind dispatch must call the existing production validators, including contextual validators that need the current workstream/planning relation.
   - Serialization must be generic TOML rendering of already-validated data; it must not maintain a second list of allowed field names/enums.
   - Validation is required before a write is considered reconciled.
2. Expose the validator/record-kind dispatch from the executable contract so producers and tests do not duplicate which validator owns which durable record.
3. Update canonical producer modules that create or mutate durable records (Intake, Research, GitHub Issues tracker state, Brainstorming, Definition, Planning/Plan Review, Execution Prep/Task Board, Execution/Review/Recovery/Close where applicable) to require the validated write boundary before successful reconciliation.
4. Keep `tools/router.py` as a consumer of the same validators; do not add a router-only schema.
5. Add parity tests showing every canonical record kind accepted through the producer boundary is accepted by the corresponding production validator/router precondition, and malformed records are rejected before successful persistence.

### Acceptance

- No canonical producer success path bypasses current production validation.
- Current field names/types/enums/locator shapes remain defined by the executable contract, not duplicated in workflow prose or a writer schema.
- A deliberate stale-shape write such as integer Definition/Planning revision, `plan_artifact`, `review_mode="normal"`, legacy tracker fields, or Card `review_pending` is rejected at the producer boundary.

## M02 — Deterministic intra-V2 schema reconciliation

### Goal

Allow Recovery to reconcile explicitly supported older/legacy-shaped active V2 state without guessing, widening scope, or transferring authority to a different immutable subject.

### Work

1. Add a dedicated V2 reconciliation contract/tool, separate from V1 discovery semantics.
2. Recognize supported source shapes by deterministic structural/profile checks plus exact source fingerprints/evidence. At minimum cover the pre-Recovery #20 Planning/Definition shape and the pre-Recovery #22 Workstream/Definition/Planning/Tracker/Task-Board shape used by the issue reproductions.
3. Produce a complete reconciliation plan in memory before mutation:
   - exact source paths and fingerprints;
   - exact canonical outputs;
   - per-record validation result;
   - authority-preservation/reset decisions;
   - unsupported/ambiguous reason when no safe mapping exists.
4. Preserve accepted scope/Definition decisions/user authorization verbatim when their semantic authority is unchanged.
5. Preserve an immutable subject-bound approval/review only when the exact canonical repository+commit+path+blob identity is already proven by durable Git evidence.
   - Do not synthesize missing commit/blob identity from mutable current content.
   - If canonicalization changes or cannot prove the exact subject, reset the affected B/Plan Review/C or implementation review obligation instead of transferring approval.
   - Keep prior terminal review evidence append-only; never rewrite it onto a different subject.
6. Validate every proposed canonical output with the production validators before applying any change.
7. Make apply deterministic and restart-safe:
   - fingerprint the source set;
   - accept each affected file only in its exact expected before-state or already-produced after-state;
   - reject unrelated divergence;
   - deterministic reapply is a no-op after completion;
   - no session/runtime identity or parallel migration state store becomes authority.
8. Integrate the mechanism with `workflow/RECOVERY.md`: schema-invalid current V2 state first attempts only an explicitly recognized safe reconciliation profile; unsupported/ambiguous state remains fail-closed Recovery.

### Acceptance

- Pre-Recovery #20 can be reconciled into current canonical state without silently preserving a subject-bound approval whose exact subject cannot be proven.
- Pre-Recovery #22 can be structurally reconciled into current canonical records, including current Workstream/Tracker/Task-Board shapes, while preserving only evidence that is still exactly attributable.
- Unknown or mixed contradictory shapes are rejected rather than normalized heuristically.
- Reconciliation can be restarted after a partial local write without duplicate semantic effects.

## M03 — Fresh-materialization and resume regression suite

### Goal

Turn both failure modes into permanent end-to-end regression coverage.

### Work

1. Add a fresh-materialization trajectory that constructs canonical records through the validated producer boundary across the pre-execution chain and then invokes a fresh router consumer.
   - At the frozen plan boundary, routing must reach Premium B rather than Recovery.
   - After an exact independent review fixture, fresh resume must route to the intended next owner rather than Recovery.
2. Preserve the malformed pre-Recovery #22 records as negative fixtures and assert:
   - direct validation fails;
   - canonical producer boundary cannot emit them;
   - supported reconciliation yields valid current state.
3. Preserve pre-Recovery #20 as an intra-V2 reconciliation fixture and test:
   - exact deterministic mapping;
   - authority preservation where provable;
   - gate reset where exact immutable subject is not provable;
   - fresh router resume after reconciliation.
4. Add explicit cases for:
   - unchanged exact subject preserves eligible authority;
   - changed/unprovable subject never inherits old B/Plan Review/C or implementation review authority;
   - ambiguous/unsupported profile stays Recovery;
   - idempotent second apply;
   - restart from a partially applied exact before/after set;
   - source divergence fails closed.
5. Add a producer/validator parity table test covering every durable record kind registered by the canonical write boundary.
6. Run the existing state, router, recovery, migration and full unit suites to prove no unrelated routing semantics changed.

### Acceptance

- Both issue reproductions are represented by regression fixtures.
- Fresh canonical materialization and fresh resume are tested as transitions, not only as isolated valid TOML samples.
- Existing canonical router and review/premium semantics remain unchanged outside the authorized repair.

## M04 — Contract/documentation convergence and qualification

### Goal

Ensure future canonical actors cannot reintroduce a prose-vs-executable schema split.

### Work

1. Update `workflow/STATE.md` and only the producer-owner modules touched by M01/M02 to name the executable validated-write/reconciliation boundary instead of restating stale structural vocabulary.
2. Keep semantic descriptions in workflow modules, but reference the executable contract for exact machine shape.
3. Add qualification assertions/document checks that canonical producer documentation points to the validated executable boundary and Recovery points to the V2 reconciler.
4. Run the complete test suite and a final router trajectory from a freshly produced workstream plus a reconciled legacy workstream.

### Acceptance

- Documentation and executable behavior identify one current schema authority.
- No new workflow phase, state store, runtime identity, approval source or broadened migration policy is introduced.
- Final qualification demonstrates both fresh-production parity and deterministic legacy resume.

## Cardization after GREEN Plan Review and Premium C

Execution Prep should materialize bounded Cards in this dependency order:

1. **M01 — validated state-write boundary**
2. **M02 — intra-V2 reconciliation**
3. **M03 — regression fixtures and transition tests**
4. **M04 — documentation convergence and final qualification**

M02 depends on M01's canonical validation/write boundary. M03 depends on M01+M02. M04 depends on all prior implementation results.

Independent review is REQUIRED for M01 and M02 because they alter the contract used to accept/migrate durable authority. M03 and M04 may be RECOMMENDED unless Execution Prep identifies a higher-risk coupling.

## Planner challenge audit

GREEN.

The plan covers every Definition requirement, keeps both supplied reproductions distinct from a proven schema-evolution event, avoids a second executable schema, preserves approvals only under exact subject identity, includes fail-closed ambiguity handling, and requires transition-level regression tests for both fresh materialization and older active-state resume.
