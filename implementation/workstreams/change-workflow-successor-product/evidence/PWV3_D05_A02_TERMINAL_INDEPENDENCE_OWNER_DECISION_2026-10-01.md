# PWV3 A02 terminal independence waiver — owner decision

Date: 2026-10-01
Workstream: `change-workflow-successor-product`
Source finding: `A02-F04`
Status: **OWNER DECISION — OPTION B**

The human owner selected **Option B — terminal independence is waivable**.

## Accepted semantics

The generic exact-scope owner waiver may satisfy the terminal acceptance gate for:
- corrected final-candidate QF; and
- SH0 self-hosting admission,

only when the waiver is explicit, durable and bound to the exact terminal subject/acceptance surface.

A terminal result produced under such a waiver:
- is semantically sufficient for the applicable terminal acceptance gate;
- uses the disposition **WAIVED_ACCEPTANCE**;
- is not, and must never be labeled, independent GREEN.

For QF, “fresh terminal acceptance” still requires a newly produced post-QF terminal acceptance result after the corrected QF/current acceptance surface and prior-evidence applicability are fixed. Reusing an older acceptance result does not satisfy that fresh terminal gate.

For SH0, the terminal acceptance result is likewise bound to the exact SH0 candidate/safety surface; an explicit exact-scope waiver may produce WAIVED_ACCEPTANCE sufficient for admission.

This decision does not weaken ordinary exact-subject applicability, freshness, publication/readback or no-replay requirements.
