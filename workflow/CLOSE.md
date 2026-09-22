# Project Workflow V2 — Close and integration

Status: M04-T01 integration-refresh contract.

Close reconciles an accepted workstream against current target truth. Textual merge cleanliness, target ancestry, source-branch survival and runtime identity are never substitutes for semantic verification.

## Refresh before review reuse or integration

Before first final-review freeze/reuse and before final integration/publication:

1. Read the exact reviewed subject and acceptance coverage.
2. Read the current integration target.
3. Compare covered content and behavior, not only target SHA/ancestry.
4. Run the affected compatibility verification required by the changed target surface.
5. If covered content/behavior is unchanged and current acceptance is fully covered by the GREEN review, GREEN may be reused after affected verification is GREEN.
6. If covered content, behavior or required acceptance materially changes, reconcile only inside accepted authority and freeze a new immutable review subject. The correcting context cannot independently review that subject.
7. Immediately before a target mutation that can race, reread the target. Any movement after refresh invalidates the mutation attempt until refresh is repeated.

A clean textual merge is never sufficient semantic-compatibility proof.

Production deterministic helper: tools/close_contract.py.

## Stacked workstreams

Stacking exists only for a genuine unmerged parent-only dependency.

- If that dependency is not yet accepted in the target, fold the child into the parent integration path.
- If the dependency is already accepted in the target, the child integrates independently after its own refresh/verification.
- Correctness does not depend on the parent source branch surviving.

## Deferred M04 slices

M04-T02 adds external-effect and final tracker lifecycle semantics.
M04-T03 adds target-side terminal recovery and cleanup.
M04-T04 adds trigger-only fork lineage and true end-of-scope behavior.
