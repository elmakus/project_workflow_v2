# PWV3 Brainstorm revision 4 — post-OP GREEN user gate

Date: 2026-10-01
Workstream: `change-workflow-successor-product`
Scope: `workflow-successor-product@4`
Status: ACTIVE OWNER INPUT / RELEASE PLACEMENT NOT YET PROMOTED

## Owner-required behavior

After every Orchestration Protocol-backed operation reaches an advance-permitting accepted result (GREEN/clear-equivalent for that OP profile), PWV3 must establish a real user-authority stop before canonical continuation.

At that stop the user chooses exactly one of:
1. **CONTINUE** — consume the accepted OP result for forward progress and derive the canonical next workflow obligation;
2. **RUN OP AGAIN** — keep the workflow at the same semantic boundary and launch another fresh OP operation over the same exact accepted subject/acceptance/coverage binding, with a new immutable OP attempt/result.

This applies uniformly to every PWV3 boundary realized through OP, including Research/review/qualification discovery profiles where their profile-specific successful result would otherwise allow forward progress.

## Loop semantics

- RED / repair-required / BLOCKED / UNKNOWN does not create the post-GREEN choice gate; existing repair/revalidation/blocker semantics continue until an advance-permitting accepted OP result exists.
- Every repeated OP attempt is distinct immutable evidence; earlier GREEN evidence is preserved and never overwritten.
- A repeated OP operation does not silently broaden product scope or alter the subject. If scope/acceptance/authority materially changes, normal upstream routing applies instead.
- After every later advance-permitting OP result, the same user-choice stop recurs.
- No fixed retry/repeat limit is implied; each additional OP wave requires an explicit user choice.
- The user-choice artifact is workflow authority for continuation, not runtime/session state.

## Release-placement analysis

This behavior changes canonical lifecycle legality by inserting a mandatory user-authority gate after every successful OP boundary. It is therefore not patch-only behavior.

Current recommendation: include it in **PWV3 3.0.0** because the product is not yet implemented and the owner requires it as a foundational invariant. If intentionally deferred, it belongs to a compatible minor line (for example 3.1), not 3.0.1.

## Impact on current Definition status

The prior Definition revision 3 and its focused revalidation GREEN remain immutable evidence for `workflow-successor-product@3`, but this substantive lifecycle change creates Brainstorm revision 4 and makes prior promotion/Definition completeness inapplicable to the new scope until revision 4 is resolved, promoted, redefined and reviewed.

Because this change materially alters lifecycle/user-stop semantics, the prior Definition Review applicability cannot simply be extended by focused revalidation. After revision-4 Definition repair, a fresh full Definition Review wave is required.
