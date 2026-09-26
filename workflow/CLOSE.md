# Project Workflow V2 — Close and integration

Status: M04-T04 integration-refresh, external-effect, tracker-close, terminal-recovery, trigger-only fork-lineage and end-of-scope contract.

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

## Returned handoff terminals

A `returned` Card is a non-GREEN late-oversize handoff disposition, never accepted completion. When the board is all-terminal with at least one `returned` Card, the router walks every bound residual outcome through anchor sizing-audit allocations, JIT-trigger resolutions, and chained handoffs: Close is reached only when each outcome terminates in an accepted (`done`) downstream Card. Any gap — uncovered or changed outcome, unmaterialized or unbound trigger, dropped chained scope, or circular handoff — routes back to a concrete Execution Prep obligation instead. A `returned` Card alone, or beside one arbitrary `done` Card, never completes approved scope.

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

## Target-side terminal recovery and cleanup

Before final merge, the exact merge subject must already contain every unique recovery artifact that can be known before merge: workstream identity/provenance, selected board, stable Card contracts, required review/result/evidence and checkpoint/handoff refs. Merge-result-dependent fields may be reconciled afterward only when target-side state plus immutable PR/merge evidence identify the exact merged source head.

After merge, closure correctness depends on the target-side package and immutable merge evidence, not on source-branch survival. Automatic deletion of the merged head is normal success and must not trigger source-ref recreation. Original source branch, creation base and parent/dependency provenance remain unchanged historical identity.

If a source ref survives and later cleanup is needed, use the minimal `safe_to_delete` fallback only after terminal recovery is independent of that ref. Persist the exact verified head, reread the current ref immediately before deletion, forbid deletion when the head moved, and read back ref absence before recording `deleted`. If GitHub already removed the merged head, do not activate fallback state merely to mirror that deletion.

A terminal unmerged/superseded workstream must preserve its recovery/history package independently of the source ref before cleanup, but rejected implementation content must not be imported into the integration target merely to preserve metadata.

Production deterministic helpers in `tools/close_contract.py` verify target-package completeness and exact merge identity, safe-delete head freshness/absence readback, and terminal-unmerged history separation.

## Pre-Final observation reconciliation and bounded cleanup

Before Final Integration may complete, every still-open non-load-bearing observation must be reconciled to exactly one terminal disposition: `resolved`, `cleanup_candidate`, `deferred`, `promoted` or `tracked`. The authoritative gate derives the complete review-attempt inventory from durable Git/workstream state (worktree reviews directory plus required HEAD and history reads), requires the Board to list every durable attempt, proves every listed locator through exact RF007/T11 Git identity and legacy provenance, reads and validates each attempt file, freezes terminal bytes against Git history, and derives the canonical observation set itself: an unreadable Git inventory, a path-only relied-upon locator, an omitted durable attempt, a duplicated locator, an omitted known observation, a fabricated unknown one, a relabeled derived disposition, or a dangling or stale attempt locator all fail against durable truth. Only a workstream with a Git-verified empty durable inventory may reconcile vacuously; a Board that lists no attempts while durable state holds an attempt fails as truncated. A separate relative-consistency helper checks a proposed set against caller-supplied history or a snapshot, but proves nothing about the completeness of its own inputs and must not substitute for the board-bound gate where durable state is available. GitHub Issues/trackers may receive intentionally exported follow-up work but remain optional bookkeeping and never become the primary canonical observation store or workflow authority.

Concrete bounded safe in-scope cleanup candidates are grouped into the smallest meaningful cleanup work with its own exact subject, tests/evidence and independent review. Each cleanup candidate must be covered by a completed independently GREEN-reviewed cleanup work before Final Integration evaluates the final codebase, and the Final gate itself validates each covering work's exact subject, tests/evidence, bounded scope and GREEN independent review; bare boolean claims, speculative redesign and new product scope cannot pass. Cleanup admits no speculative redesign or new product scope, and it does not recursively stay open merely because further advisory improvement is conceivable: once the bounded work is complete and reviewed, reconciliation terminates.

Production deterministic helpers: `tools/close_contract.py` (`verify_final_observation_reconciliation_from_board`, `verify_final_observation_reconciliation`, `validate_cleanup_work`).

## Trigger-only downstream fork publication

Ordinary Close MUST NOT load fork-release lineage policy. Load `workflow/FORK_RELEASE_VERSIONING.md` only when the exact durable current operation explicitly declares a downstream fork release and supplies the accepted upstream repository/tag/SHA lineage tuple.

That optional module selects/validates lineage only. It never authorizes upstream sync, tag creation, release publication, deployment or another live write. Release quality remains independent of lineage.

## End of approved scope

Finishing a Card, review, milestone or Close sub-step is not itself an end-of-scope stop.

Close reports completion and stops only when durable project/workstream truth proves the approved scope is complete and no already-authorized obligation remains. If another legal obligation remains, continue deterministically. If completion is not yet durable, continue Close reconciliation rather than inventing follow-up work or claiming completion.

Deployment/live-write status alone never creates a human gate. An exact accepted authorization boundary still does and must stop before the gated mutation.

`tools/close_contract.py` owns the deterministic continuation oracle. True end of scope returns `end_of_scope_stop`; it is never inferred merely from an empty current Card queue.
