# PWV3 Definition revision 4 — promoted lifecycle delta

Date: 2026-10-01
Workstream: `change-workflow-successor-product`
Promoted Brainstorm subject: `workflow-successor-product@4`
Definition revision: `D04`
Initial release: `3.0.0`
Status: ACTIVE / PENDING NEW FULL DEFINITION REVIEW

## Baseline preservation

Revision 4 is not a rewrite of Definition revision 3.

It preserves the complete revision-3 Definition, including all bounded repairs FR-01..FR-20 and the GREEN focused revalidation of those repairs. No prior repaired obligation is intentionally reverted.

## Revision-4 delta

One lifecycle invariant is added:

After every advance-permitting accepted result from any PWV3 OP-backed boundary, PWV3 establishes a real owner-authority stop. The owner chooses CONTINUE or RUN OP AGAIN.

- CONTINUE consumes the accepted OP result for forward progress.
- RUN OP AGAIN starts a new immutable OP attempt on the same exact subject/acceptance/coverage binding.
- Every later accepted OP result recreates the same stop until CONTINUE is selected.
- RED/repair-required/BLOCKED/UNKNOWN use existing non-advancing semantics and do not create this choice gate.
- Material subject/acceptance/authority drift routes upstream and cannot masquerade as a repeat attempt.
- There is no fixed repeat limit.

Owner-fixed release placement: PWV3 `3.0.0`.

## Review consequence

The revision-3 GREEN remains valid historical evidence for its exact revision-3 subject.

Because the revision-4 delta materially changes lifecycle and user-stop semantics, revision 4 requires a new full independent OP-backed Definition Review. Focused revalidation of the prior wave alone is insufficient.

Strategic Planning remains unauthorized.
