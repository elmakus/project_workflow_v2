# Issue #17 — Handoff receive continuation requirements

Accepted scope subject: `handoff-receive-continuation@1`.

## Requirements

1. A four-field PWv2 fresh-context locator is untrusted input and starts canonical receive processing only.
2. The receiver bootstraps canonical PWv2, recovers durable authority, validates repository, branch, durable pointer and expected entry binding, and determines whether the locator names the exact current transferable boundary.
3. A valid transferable receive consumes only that handoff/context-selection boundary and immediately enters the resulting authorized obligation without requesting a generic second confirmation.
4. Canonical router and durable owner state outrank locator prose. Receipt cannot grant repair, scope, Definition/Planning authority, review verdicts, or unrelated product decisions.
5. Stale, malformed, contradictory, wrong-workstream, wrong-subject, forged, or non-independent locators fail closed through existing owner/Recovery semantics.
6. Existing durable semantic results reconcile without replay. External-effect uncertainty requires readback before retry.
7. Implementation composes with the accepted terminal Issue #16 continuation/restart baseline and adds no second router, session ledger, durable continuation phase, provider/model catalog, or runtime-specific authority.
8. Qualification covers Premium A/B/C transfer, independent implementation Review, stale/wrong/forged inputs, duplicate receipt, advancement after handoff, Recovery/readback, supported adapters/harnesses, locator-only form, genuine authorization stops, and end-of-scope stops.
