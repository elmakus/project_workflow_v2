# Issue #23 — durable-state schema regression diagnosis and prior art

## Repair subject

Ensure every canonical PWv2 durable-state producer emits state conforming to the same current executable schema used by the router/validators, and add deterministic fail-closed intra-V2 schema reconciliation for supported older or legacy-shaped active workstreams that preserves accepted scope, approvals and immutable authority, with fresh-materialization and resume regression coverage.

## Finding

The two supplied reproductions fail for the same immediate class of defect (producer-generated state does not conform to the executable durable-state contract), but they must not be described as proven instances of the same historical schema-evolution event.

### Reproduction A — fresh issue #22 workstream

The #22 workstream was created from commit `0c01bc0b888a0f42114924ed852a9afe930eb5a8`. At that base, both `tools/state_contract.py` and `tools/router.py` have the same blob identity as current `main`.

Before Recovery, the freshly produced state contained incompatible shapes, including:

- `WORKSTREAM.toml` omitted `created_from` and the `task_board` locator at the review boundary.
- `DEFINITION.toml` used legacy-shaped keys such as `source_scope`, integer `revision`, uppercase lifecycle/audit values, and string locators instead of current authority locator tables.
- `PLANNING.toml` used integer `revision`, `plan_artifact`, `frozen_subject`, `review_mode = "normal"`, and no current immutable `[subject]` table.
- `TRACKER.toml` used `number`, `url`, and `authority` instead of the current dedup/readback contract.
- `TASK_BOARD.toml` used `status = "review_pending"`, top-level `result_path` / `review_requirement`, and no current exact result/review-attempt locators.

At commit `51c5ebccca4ea1b4e1fd60b3f36dddc5fb2e72d2`, the independent-review state therefore could not pass the already-current validator. Recovery later rewrote the manifest, tracker and task board manually in commits beginning `ccea3685...`, `80a15929...`, and `1e0b2953...`.

Conclusion: this reproduction is not caused by a contract update landing after materialization. The producer path wrote a stale/guessed schema while the current executable contract was already authoritative.

### Reproduction B — active issue #20 Paseo workstream

The #20 workstream declares `created_from = dde078d7b2d340cd100b33c9e03c9add6d959eb1`. At that exact base, the blobs for `tools/state_contract.py`, `tools/router.py`, `workflow/PLANNING.md`, `workflow/DEFINITION.md`, `workflow/WORKSTREAMS.md`, and `workflow/RECOVERY.md` are also identical to current `main`.

Before reconciliation, the workstream had the reported legacy-shaped planning and definition state: integer revisions, `plan_artifact`, `review_mode = "normal"`, no immutable current `[subject]` table, and no plan-review locator. Commit `ef627400...` manually reconciled Planning to the current schema and bound an exact Git-blob subject.

Conclusion: this supplied reproduction also does not prove that the workstream was valid under an older V2 schema and only later became stale. It proves a second producer/validator drift incident. The architectural evolution problem still exists, but these two reproductions are not evidence of two distinct historical contract versions.

## Root cause

### 1. Executable consumer contract is centralized; producer contract is not

The router imports and executes the validators from `tools/state_contract.py` before routing durable state. That side is centralized and fail-closed.

The producer side is mostly natural-language workflow modules plus direct repository writes. Those modules describe semantic ownership but do not define one machine-readable writer/serializer surface with exact field names, enum values and structural shapes. For example, Planning prose says "plan artifact locator" and "normal independent review", while the executable contract requires `plan_path` and the exact enum `review_mode = "independent"`. Definition prose similarly describes approved requirement/decision locators without being the exact TOML schema.

A canonical actor can therefore follow the canonical prose semantically yet still emit a shape that the canonical executable consumer rejects.

### 2. No mandatory validate-before-commit boundary for ordinary producers

There is no canonical state materializer/writer in `tools/` for Intake/Definition/Planning/Task Board/Tracker/Review that all normal writes must pass through. The repository contains executable validators, but ordinary durable-state production can bypass them. This is why malformed state can survive until a fresh router/reviewer invocation validates it.

### 3. No intra-V2 durable schema version and no V2->current migration dispatcher

Current durable records do not carry a schema version that lets Recovery distinguish:
- a known supported older V2 schema;
- producer-generated malformed state under the current schema;
- genuinely corrupt/ambiguous state.

The router validates only against the current contract and routes validation failure to Recovery. `workflow/RECOVERY.md` and `tools/recovery_contract.py` reconstruct semantic obligations but contain no schema migration engine.

The existing migration machinery is explicitly V1-focused/fixture-oriented (`tools/v1_migration.py`, `tools/migration_apply.py`) and is not a general active-V2 schema reconciliation path.

### 4. Regression coverage validates consumers and fixtures, not a producer->consumer round trip

The suite has strong validator/router fixtures, but no test that takes a freshly materialized workstream through the canonical producing transitions and immediately resumes it in a fresh canonical consumer/reviewer. Static valid fixtures cannot catch a producer that invents or reuses stale field names.

## Required reconciliation invariants

Any supported intra-V2 migration/reconciliation must be structural and authority-preserving, never an implicit re-approval.

- Preserve the exact accepted repair/scope subject and user authorization. Never synthesize a new authorization or widen scope.
- Preserve Definition requirements/decision authority exactly, or bind the migrated record to an exact immutable source artifact proving semantic identity.
- Preserve premium/review approvals only when their exact subject identity is still provably the same.
- Preserve append-only review history; never rewrite a RED/GREEN attempt onto a different subject.
- Preserve immutable Git subjects as repository + commit + path + blob. If a legacy record lacks enough data, recover the identity only from exact Git history/evidence; otherwise fail closed.
- If migration must move/copy a plan and therefore creates a new blob/path subject, subject-bound B/Plan Review/C approval cannot be silently carried to the new subject. The appropriate gate must become due again unless an existing explicit canonical exemption rule applies.
- Map pure representation changes only when semantic equivalence is deterministic (for example, a legacy "normal" review mode may map to current "independent" only when the source contract unambiguously defined "normal" as independent review).
- Migration must be idempotent and restart-safe, with exact before/after fingerprints and no duplicate external effects.
- Unsupported or ambiguous legacy shapes remain Recovery, not best-effort repair.

## Regression coverage required

1. **Fresh materialization round trip:** use the actual canonical producer/materializer path to create Intake -> Research -> Definition -> Planning -> Plan Review -> Execution Prep/Task Board state. Validate after every write with the same executable state contract. A fresh independent Review invocation must route to the intended review obligation, not Recovery.

2. **Producer/validator parity:** every canonical durable-state producer must serialize through one current schema authority and its emitted state must pass the corresponding production validator. Test all owner records and enums, including manifest locators.

3. **Known #22 fixture:** retain the pre-Recovery malformed #22 state as a negative fixture proving the current producer cannot recreate `review_pending`, legacy tracker fields, legacy Definition/Planning shapes, or missing required locators.

4. **Known #20 fixture:** retain the pre-Recovery #20 Planning/Definition shape as a migration/reconciliation fixture.

5. **Supported older-V2 resume:** start from a versioned older active workstream at a Premium B / independent Plan Review boundary, migrate it to current schema, prove a semantic authority digest is unchanged, and reroute to the intended premium/review obligation rather than Intake/Definition/Recovery.

6. **Subject preservation:** prove exact user authorization, Definition authority, premium gate subjects, frozen plan Git identity and review history are preserved when identities remain unchanged.

7. **Subject-change safety:** prove that when canonicalization necessarily creates a new immutable plan subject, old subject-bound B/review/C approval is not transferred silently.

8. **Ambiguous migration fail-closed:** missing commit/blob identity, contradictory approvals, unknown enums or multiple possible source subjects must produce Recovery without mutation.

9. **Idempotent restart:** applying the same supported migration twice or resuming after an interrupted migration must produce one deterministic current state with no duplicated approvals/reviews/effects.

## Source accounting

- Official/upstream: current PWv2 workflow modules, `tools/state_contract.py`, `tools/router.py`, `tools/recovery_contract.py`, and V1 migration tooling.
- Project/runtime: exact #22 and #20 workstream snapshots and their Recovery commits.
- Tracker/discussion: GitHub issues #20, #22 and #23 as symptom/context evidence only, never authority.
- Practitioner/community: not relevant to this internal durable-state schema contract; external popularity cannot establish PWv2 authority.

## Conflict accounting

Issue #23 describes the second reproduction as an active workstream becoming incompatible "after PWv2 contract evolution." Exact Git evidence conflicts with that characterization: the executable contract and relevant workflow module blobs at the workstream's declared creation base are identical to current `main`. The durable finding therefore classifies both supplied reproductions as producer/consumer drift while separately confirming that PWv2 lacks a deterministic intra-V2 schema-evolution migration mechanism for future or genuinely older supported states.

## Limitations

This diagnosis does not authorize implementation and does not select the final implementation architecture. In particular, it does not decide whether the single schema authority should be constructors, typed models, generated TOML serializers, versioned adapters, or another equivalent mechanism. Those choices belong to the post-alignment Definition/Planning path.
