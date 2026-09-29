# Preserved program inputs — evidence, not transferred authority

Workstream: `issue-pwv2-stabilization-program`.

## Canonical product boundary

Repository: `elmakus/project_workflow_v2`.
Current default branch verified before entry: `main@d3ab917f02e4de91b7dbb17915c2287c2387333e`.
The selected formalization branch starts at that exact commit. No code or canonical policy is imported from non-default candidates.

## Independently preserved audit chains

- `PROPOSED_PROGRAM_P1.md`: exact original proposal, SHA256 `869f277e95ae8b15e969beb04d48d3b53d5ef095e4553359a4d356158e1ecce3`. It remains proposed, including its wave structure. Read `USER_AUTHORIZATION.md` for the newer explicit limitations.
- `PI_PASEO_AUDIT_REPORT.md`: SHA256 `ce88653db76d334009d322788a38c53021783ac51b902827efa44c7fd55caf90`, copied from evidence commit `6f1a047c912898281a645594b8518140172a8682`.
- `provenance/pi-paseo-audit.bundle`: portable original evidence repository plus canonical/subject Git histories. Bundle verification succeeded. The packaged evidence repository contains REPORT.md, individual issue evidence, fixture observations and bundle-index.json. Original reports may mention prior local paths; those paths are not fresh-context authority. Recover the exact evidence commit from the bundle rather than assume the paths survive.
- `CHATGPT_ADVERSARIAL_AUDIT_REPORT.md`: SHA256 `b1b8bda83304c62c989abf8c347bee2ee0df01a1de4ebe6ee64fcce93f8b05c2`, copied verbatim from `research/pwv2-adversarial-stabilization-bug-hunt@95d74bad11115419696a684c8eef11fda076f92f`, path `implementation/workstreams/change-adversarial-stabilization-bug-hunt/evidence/ADVERSARIAL_STABILIZATION_AUDIT_2026-09-29.md`.

Neither audit completion, audit agreement, Git history nor copied issue content authorizes a repair.

## Existing scope boundaries

Read `provenance/issue23-existing-authority.md`, `provenance/issue20-existing-authority.md` and their exact raw state snapshots under `provenance/scope-snapshots/`. These are evidence copies, NOT selected owner records for this workstream.

- #23 snapshot: `work/pwv2-durable-state-schema@b076e081fb91815ff570fb70566e71f8cc53154e`. Preserve structural/schema parity and explicitly supported bounded V2 reconciliation. Its candidate code is not canonical main and is not adopted by importing this evidence.
- #20 snapshot: `work/pwv2-paseo-child-delegation@c5e9ba1d3da8d339e882b43b86b4e8a8dd2e9a28`. Preserve official caller-scoped capability readiness only; no alternate spawn implementation or final helper.
- ChatGPT diagnosis-only audit remains its own stopped exploratory workstream; importing its findings does not clear its explicit stop or authorize promotion.
- `provenance/source-scopes.bundle` preserves all three source Git histories, including the exact snapshot commits. It is evidence for immutable readback, not a second workflow store.
- `provenance/preserved-scope-verification.json` checks 15 raw source-state copies byte-for-byte against their exact source Git blobs. This establishes preservation, not validation/current legality of those other workstreams.

## Tracker and proposed issue relationships

`provenance/issue-readback.json` preserves the original 26 open/closed issue readbacks and both comments. Fresh readback may be added separately without overwriting the earlier evidence epoch. #24 is merged PR evidence for #22. Open PR #9 is explicitly excluded from adoption.

For every separately demonstrated defect, maintain its own invariant and acceptance tests. Shared constructors/resolvers/history infrastructure are capability reuse only, never silent issue absorption, duplicate classification, widened authorization or closing evidence. The #26 comment's raw-ref/pending-reservation gap remains distinct from #18/#37 even if infrastructure is reused.

## Return/authority chain

`USER_AUTHORIZATION.md` records the exact bounded user response. Selected canonical lifecycle state remains in this workstream's pointed INTAKE/RESEARCH/BRAINSTORM records as actually materialized. Imported snapshots, draft outputs and this index own no current route, approval, premium state or task status.
