# Issue #23 — Durable-state producer/consumer parity requirements

## Authorized scope

Repair only the durable-state/schema inconsistency covered by the exact authorized Intake repair subject. Do not change unrelated workflow semantics, premium-gate policy, review independence, execution orchestration, or accepted product scope.

## Requirements

1. Every canonical PWv2 producer that creates or mutates durable workflow state must emit the exact current executable schema consumed by the canonical router and production validators.
2. Canonical production must use one machine-enforced schema authority for field names, types, enums, locator shapes, required values and serialization semantics. Narrative workflow prose may explain semantics but must not be an independent executable schema.
3. A canonical durable-state write must be validated against the same production contract before it is accepted as a successful producer transition.
4. Freshly materialized state must be resumable by a fresh canonical consumer without Recovery caused by producer-generated schema drift.
5. The repair must cover the durable owner records implicated by the reproductions and any other canonical producers that write records validated by the same current state contract; it must not create parallel per-stage schema definitions.
6. PWv2 must have a deterministic fail-closed reconciliation path for explicitly supported older or legacy-shaped active V2 durable state.
7. Reconciliation must distinguish a supported known source shape from ambiguous/corrupt state. Unsupported or ambiguous state remains Recovery and must not be guessed into validity.
8. Reconciliation must preserve the exact authorized repair/scope subject, accepted Definition authority, user approvals, review history and exact immutable Git identities whenever semantic identity is provable.
9. Subject-bound approvals may be retained only when the exact canonical subject remains identical. If reconciliation necessarily changes the immutable subject and no existing canonical exemption applies, the corresponding subject-bound gate/review approval must become due again rather than being silently transferred.
10. Reconciliation must never synthesize authorization, widen accepted scope, rewrite terminal review history onto a different subject, or infer missing immutable identity from mutable/current content.
11. Reconciliation must be deterministic, idempotent and restart-safe. Reapplying it to already-current state must not create duplicate approvals, attempts, effects or semantic transitions.
12. Regression coverage must include:
    - canonical fresh materialization followed by fresh independent resume/review;
    - the pre-Recovery #22 malformed producer shape as a negative regression fixture;
    - the pre-Recovery #20 legacy-shaped active state as a reconciliation fixture;
    - a supported older-V2 premium/review-boundary resume proving preserved semantic authority;
    - exact subject-preservation and subject-change reset behavior;
    - ambiguous/unsupported fail-closed behavior;
    - idempotent/restart-safe reconciliation.
13. The repair must retain the existing separation between workflow semantic authority and runtime/model/session/worker identity.
