# PWV3 Brainstorm revision 6 — invocation-derived executor owner direction

Date: 2026-10-02
Subject: workflow-successor-product@6
Status: OWNER DIRECTION

## Owner direction

The user must not predeclare or persist an execution mode such as native_pwv3, goal, Pi, Paseo or ChatGPT before execution.

The same exact reviewed Execution Package must be portable across supported execution venues.

Execution realization is selected implicitly by invocation context:
- if the package is launched in Pi through a qualified goal-capable runtime, that runtime executes it;
- if launched in ChatGPT/PWV3, ChatGPT/PWV3 executes it and may use handoffs/subagents according to the same semantic contract;
- if launched in another qualified PWV3 runtime, that runtime executes it.

No user-facing execution_mode choice is required.

## Semantic/runtime split

PWV3 semantic authority owns:
- the exact reviewed Execution Package;
- Card/order/dependency/acceptance semantics;
- Result/Review/recovery/qualification rules;
- the pre-Global boundary.

The runtime/executor owns only execution mechanics.

At launch, the runtime may auto-derive a small transient/runtime launch envelope from the invocation environment. The owner must not have to author or choose that envelope manually.

For reproducibility and recovery, the exact executor/runtime/provider bundle actually used must be positively observed and durably recorded after launch/binding, but this is provenance/readback, not a prior product decision and not a semantic branch in the Plan or Execution Package.

## Consequence

PWV3 has one execution semantic path, not two product-level modes.

The distinction between Pi /goal, native PWV3, ChatGPT with handoffs, or another qualified executor is runtime realization only.

This is a substantive refinement of revision 5, so the Brainstorm subject advances to workflow-successor-product@6 and prior promotion readiness for revision 5 is stale.
