# Project Workflow V2 — Close and integration

Status: M04-T02 integration-refresh, external-effect and tracker-close contract.

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

## External effects

For each material external mutation with meaningful readback:

1. record the exact target and expected durable state;
2. perform the action/write once;
3. read back the exact external object before deciding whether any retry is safe;
4. verify the observation against the expected state and preserve evidence;
5. only a verified `no_effect` permits retry; a verified `expected_effect` reconciles without replay; an `unexpected_effect` routes reconciliation; unresolved occurrence fails closed.

A timeout or unknown mutation result never authorizes a blind retry. `tools/close_contract.py` owns the deterministic retry/reconcile oracle; the external-effect durable record distinguishes readback status from the observed effect.

## GitHub tracker final lifecycle

GitHub Issue state remains bookkeeping and never authorizes implementation or completion.

- Intermediate PRs and non-final integrations use reference-only linkage.
- Closing linkage is allowed only for the accepted scope-completing PR that integrates to the default branch.
- After durable accepted completion, read back the linked Issue state.
- An Issue found closed before accepted completion is unexpected external state and routes reconciliation; it is never workflow approval.
- When accepted completion is durable and the Issue is already closed, record verified closure.
- When accepted completion is durable but the Issue remains open, explicit close is allowed only when automatic closing is unavailable/disabled. If automatic close was expected, reconcile that discrepancy first.
- Deployment/live-write status alone does not introduce a user gate; only an explicit accepted authorization boundary does.

## Deferred M04 slices

M04-T03 adds target-side terminal recovery and cleanup.
M04-T04 adds trigger-only fork lineage and true end-of-scope behavior.
