# PWV3 Brainstorm revision 4 — post-OP GREEN user gate

Date: 2026-10-01
Workstream: `change-workflow-successor-product`
Scope: `workflow-successor-product@4`
Status: OWNER DECISION CONFIRMED

## Owner-fixed behavior

After every Orchestration Protocol-backed operation reaches an advance-permitting accepted result (GREEN/clear-equivalent for that OP profile), PWV3 establishes a real user-authority stop before canonical continuation.

At that stop the user chooses exactly one of:
1. **CONTINUE** — consume the accepted OP result for forward progress and derive the canonical next workflow obligation;
2. **RUN OP AGAIN** — keep the workflow at the same semantic boundary and launch another fresh OP operation over the same exact accepted subject/acceptance/coverage binding, with a new immutable OP attempt/result.

The same stop recurs after every later advance-permitting OP result until the owner selects CONTINUE.

## Scope

This applies uniformly to every PWV3 boundary realized through OP, including:
- Brainstorming Research;
- Definition Review;
- Plan Review;
- Execution Prep / Execution Package Review;
- Final Qualification Targeted Bug Hunt;
- Final Qualification Global Bug Hunt;
- any future PWV3 boundary that invokes OP through the stable OP caller/result contract.

## Loop semantics

- RED / repair-required / BLOCKED / UNKNOWN does not create the post-GREEN choice gate; existing repair/revalidation/blocker semantics continue until an advance-permitting accepted OP result exists.
- Every repeated OP attempt is distinct immutable evidence; earlier GREEN evidence is preserved and never overwritten.
- Repeating OP does not silently broaden scope or alter the frozen subject/acceptance/coverage binding.
- If scope, authority or acceptance materially changes, normal upstream routing applies and a new applicable subject is required rather than pretending it is another attempt on the old one.
- No fixed repeat limit is imposed. Each additional OP wave requires an explicit owner choice.
- The durable owner choice is workflow authority for continuation; runtime/session state is not.

## Release placement

Owner decision: **ship this invariant in PWV3 3.0.0**.

Reason:
- it changes canonical continuation legality and user-authority boundaries;
- PWV3 is not yet implemented, so there is no compatibility value in intentionally shipping 3.0 without a required foundational lifecycle invariant;
- if this behavior were ever deferred, it would be compatible-minor semantics rather than a 3.0.1 patch.

## Effect on prior Definition evidence

Definition revision 3 and its focused revalidation GREEN remain immutable historical evidence for `workflow-successor-product@3`.

They are not discarded. Revision 4 Definition must start from the complete repaired revision-3 Definition and apply only the accepted lifecycle delta plus directly required flow-down.

Because the new invariant materially changes lifecycle/user-stop semantics, the prior Definition Review GREEN cannot be reused as acceptance of the new subject. After revision-4 Definition is produced, it requires a fresh full Definition Review wave.

No prior FR-01..FR-20 repair is reopened merely because a new full review is required.
