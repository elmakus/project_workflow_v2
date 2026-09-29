# Issue #36 — exploratory scope revision 1

Scope subject: `orphan-preexecution-owners@1`  
Aligned repair subject: `repair:orphan-preexecution-owner-prerequisites:v1`

This is a challenged, ready-for-Definition exploratory proposal. It is not promotion authorization, accepted requirements, a plan or implementation permission.

## Problem and bounded outcome

Current `main@d3ab917f02e4de91b7dbb17915c2287c2387333e` permits a workstream manifest to name Planning without Definition, or Plan Review without Planning, then silently selects unrelated active Execution or Planning without reading the orphan. A declared Planning A-due gate must not disappear because its prerequisite owner was omitted. A declared Plan Review must not disappear because Planning is omitted. The accepted outcome is fail-closed missing-owner classification before downstream stage/Board dispatch, preserving current valid progressive routing and earlier independent owners.

Included candidate obligations for Definition challenge:

1. A manifest-declared Planning owner requires the current lawful Definition locator, including when a Task Board exists; absent Definition is Recovery, not Execution, Brainstorming, or an empty success.
2. A manifest-declared Plan Review requires current Planning (and its lawful upstream chain); absent Planning is Recovery, even if valid Definition or an active Board would otherwise select an earlier return.
3. Check the prerequisite relation without pretending to validate/consume a downstream orphan as accepted state. Malformed or stale records remain fail-closed when their owner is lawfully reached. A valid Brainstorm explicit stop, earlier active/return Research and tracker recovery retain their already accepted precedence; #36 does not subsume #33 or #28. Precisely where the guard belongs is a Definition/Planning technical decision constrained by these positive and negative routes.
4. Positive controls: valid active Definition, GREEN Definition A due, satisfied A with draft/frozen/approved Planning and matching Plan Review, and ordinary Board dispatch retain their respective owners. Counterexamples include both orphan classes with/without active Board and with a present GREEN Definition but missing Planning.
5. Require production-selector tests, read-set and no-mutation assertions, cumulative state/router/stop/continuation regressions, committed exact-subject clean readback, and independent implementation review before claiming a repaired Card.

Excluded: generic priority registry, schema migration, history/attempt redesign (#31/#37), explicit-stop implementation (#33), Intake identity (#32), Research return precedence (#28), Close reconstruction (#29), #23/#26 parity/reconciliation, tracker mutation/closure, integration and deployment. The program plan is dependency context only; it supplies no approval or gate satisfaction for this repair.

## Alternatives and challenge

- **Ignore orphans until an owner appears:** rejected. A declared current owner/gate cannot silently evaporate into Execution; the confirmed counterexamples violate WORKSTREAMS/PLANNING.
- **Validate every downstream file unconditionally at bootstrap:** rejected. It would defeat progressive read order, change earlier stop/Research/tracker precedence and accidentally widen #33/#28.
- **Classify only Plan Review without Planning:** rejected. The missing Definition / A-due Planning counterexample is independent and in the same accepted #36 subject.
- **Infer absent prerequisites from an old Board or normalize the orphan away:** rejected. A Board is not upstream Definition/Planning authority; selection must not mutate or accept files merely to obtain a route.
- **Build generic owner DAG/policy engine:** rejected unless Planning demonstrates a concrete necessity. The two direct declared-prerequisite relations are small and testable.
- **Require a user choice about precedence over an already valid explicit stop:** not needed. The earlier accepted stop contract already owns that decision; #36 must not silently reverse it. If exact semantics materially conflict during Definition, escalate instead of inventing a new user decision.

Challenge audit: **GREEN** for this bounded exploratory subject. The Intake diagnosis and prior-art binding are exact; both independent counterexamples and lawful controls are reproduced. No unresolved product choice is being hidden, but the user has not yet authorized promotion of `orphan-preexecution-owners@1` to Definition. Any substantive scope revision increments the revision and invalidates earlier promotion.
