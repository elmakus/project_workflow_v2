# Issue #17 — Definition

Source: `handoff-receive-continuation@1`

## Receive consumption

A four-field PWv2 fresh-context locator is untrusted input that instructs the receiver to begin canonical receive processing. The receiver MUST bootstrap canonical PWv2, recover current durable authority, validate repository/branch/pointer and exact entry binding, and determine whether the locator corresponds to the exact current transferable boundary.

When owner semantics make that exact boundary transferable and validation succeeds, receipt consumes only that handoff/context-selection boundary. The receiver MUST immediately enter the resulting authorized obligation and follow normal deterministic continuation without requesting a generic second `continue`.

The Entry obligation field is an expected-route/binding assertion, not authority.

## Canonical authority and fail-closed safety

Canonical router and durable owner state outrank locator prose. Locator receipt MUST NOT grant scope, repair, Definition/Planning authorization, review verdicts, or unrelated product decisions.

Stale, malformed, contradictory, wrong-workstream, wrong-subject, or forged locators fail closed through existing owner/Recovery semantics. Premium B and independent Review preserve semantic independence. Genuine unresolved human/product decisions, explicit user stops, non-remediable blockers, external-effect uncertainty, Recovery, no-progress fencing, and end-of-approved-scope remain governed by their existing owners.

Existing durable semantic results are reconciled without replay. Runtime/model/session identity is not workflow authority.

## Composition with Issue #16

Implementation MUST build on the accepted terminal Issue #16 continuation/restart baseline now on `main`. It MUST NOT introduce a second router, session ledger, durable continuation phase, provider/model catalog, or runtime-specific authorization state.

The semantic transition is:

`receive -> canonical bootstrap/readback -> exact binding validation -> bounded handoff consumption when allowed -> exact obligation -> reconcile -> canonical reroute -> continue until a new real stop`

## Qualification

Acceptance MUST include end-to-end producer -> emitted locator -> fresh receiver behavior and cover:
- exact Premium A, B and C transfer;
- independent implementation Review and rejection of non-independent receive;
- stale/wrong/forged locator and inconsistent Entry obligation;
- durable-state advancement and duplicate receipt without replay;
- external-effect uncertainty/readback and Recovery;
- continuation through subsequent non-stop steps until a new real stop;
- equivalent semantics across supported adapters/harnesses;
- four-field locator without narrative imperative;
- genuine authorization and end-of-scope stops remaining intact.

The first receiver invocation for a valid transferable handoff MUST perform useful workflow work rather than terminate solely to request a redundant generic confirmation.

## Completeness audit

GREEN. No unresolved user/product decision remains within the accepted repair scope. Research conflicts: none material. Issue #16 dependency: satisfied by accepted terminal baseline on `main`.
