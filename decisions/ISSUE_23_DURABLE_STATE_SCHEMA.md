# Issue #23 — Durable-state schema decisions

## Accepted decisions

### D1 — One executable schema authority

The executable consumer contract remains authoritative for durable-state shape. Canonical producers must derive serialization/construction from that same executable contract boundary rather than independently reproducing field names and enums from prose.

The implementation may introduce constructors, normalized record builders, renderers or equivalent helpers, but they must not become a second divergent schema definition.

### D2 — Validate before successful persistence

A canonical producer transition is not successfully reconciled until the produced record passes the corresponding production validator. Validation after a later fresh invocation is too late and remains only a fail-closed safety net.

### D3 — Intra-V2 reconciliation is structural, bounded and fail-closed

Supported legacy V2 shapes may be converted only through explicit deterministic mappings whose semantic equivalence is known. Unknown shapes, contradictory state, missing exact subject identity or ambiguous authority stay in Recovery.

### D4 — Authority preservation dominates convenience

Migration/reconciliation preserves existing accepted scope and approvals only when their semantic and immutable subject identity can be proven from durable Git evidence. It must not manufacture replacement authority.

### D5 — Subject identity controls gate preservation

When an existing exact subject can be reconstructed unchanged, subject-bound B/Plan Review/C or implementation review authority may remain bound to it. When canonicalization creates a different immutable subject, old subject-bound approvals are not portable unless an already-existing canonical exemption rule explicitly covers the change.

### D6 — No schema-evolution claim for the two supplied reproductions

The #22 and #20 reproductions are treated as producer/consumer drift under an already-current executable contract. They are regression evidence for producer parity and recovery/reconciliation behavior, not proof of a historical current-schema upgrade event.

### D7 — Test the real transition path

Coverage must exercise actual canonical producer-to-consumer transitions rather than only static valid fixtures. A fresh independent invocation must consume freshly produced state at the intended obligation boundary without schema Recovery.
