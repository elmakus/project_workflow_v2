# Issue #33 — Intake diagnosis and proportional prior art

Research subject: `repair:brainstorm-explicit-stop-precedence:v1`

This evidence supports issue diagnosis and later exact user alignment only. It does not authorize implementation, Definition promotion, Planning, tracker mutation, integration, or issue closure.

## Canonical invariant

`workflow/BRAINSTORMING.md` declares `explicit user stop -> real stop`. The router priority foundation places explicit human/premium boundaries first, and `workflow/USER_STOP.md` requires an existing durable stop to be delivered rather than bypassed by ordinary stage continuation.

Current state validation accepts a promoted, GREEN, exactly authorized Brainstorm record with `explicit_user_stop = true`. A matching Definition record may also validate. Therefore the selector must preserve the explicit stop before Definition/Planning routing, or fail closed if accepted Definition chooses to classify that combination as contradictory. It must never silently continue downstream.

## Exact current behavior

On `main@d3ab917f02e4de91b7dbb17915c2287c2387333e`, `tools/router.py` evaluates and returns from the Definition branch before reaching the later Brainstorm explicit-stop check.

A disposable current-schema fixture with:

- promoted Brainstorm revision, GREEN challenge, exact promotion authorization, and `explicit_user_stop = true`;
- matching active Definition bound to that promoted scope;

validates and freshly routes to `route / definition` instead of the durable explicit stop. A GREEN Definition with A satisfied similarly proceeds toward Planning. These are the same precedence defect, not separate issues.

Lawful controls establish the boundary:

- the same Brainstorm record without Definition correctly routes `stop / explicit_user_stop`;
- removing the explicit stop preserves normal promoted-scope Definition routing;
- no existing production test covers the exact stop-plus-Definition relation.

## Repository and tracker prior art

Issue #33 is OPEN with correlation `pwv2-brainstorm-explicit-stop-precedence` and the same concrete reproducer. It is bookkeeping and diagnosis evidence only.

The stabilization program independently preserved ChatGPT audit N07 and Pi/Paseo variant D17. Both identify the same bypass class. No landed branch contains an accepted repair for this exact subject. The broad `work/pwv21-policy-kernel` history still evaluates the explicit-stop policy only after the Definition branch and therefore does not supply an accepted result.

The defect is distinct from:

- #11 stop delivery after a stop is selected;
- #16 deterministic continuation after RED;
- #25 Premium-B handoff receipt;
- #28 execution-Research return-owner precedence;
- #36 orphan Planning/Plan Review prerequisite ownership.

## Proposed bounded repair outcome

For `repair:brainstorm-explicit-stop-precedence:v1`:

### Included

- preserve a durable Brainstorm explicit stop before matching Definition or Planning next-stage dispatch;
- establish the smallest production selected-state precedence/relational guard needed for that invariant;
- cover active and GREEN Definition variants plus lawful stop-absent and stop-only controls;
- preserve USER_STOP delivery and existing valid Brainstorm promotion/Definition behavior.

### Excluded

- #36 orphan-owner closure, #31 Stage-6 history, #29 Close reconstruction, #23/#26 schema reconciliation, historical migration, broad priority-kernel adoption, tracker closure, integration, and deployment.

The exact production placement and whether accepted Definition chooses stop precedence or fail-closed contradiction remain later Definition/Planning decisions. Current canonical wording strongly favors preserving the explicit stop.

## Source accounting

- **Official/upstream — checked, controlling:** canonical Router, Brainstorming, User Stop, State, and Authority contracts.
- **Actual project/runtime — checked, controlling defect evidence:** current selector ordering, disposable production reproducer, lawful controls, validator and test inspection.
- **Tracker/discussion — checked, supporting:** verified Issue #33 and program provenance; used for deduplication and history, never authorization.
- **Practitioner/community — not relevant:** this is an internal deterministic precedence invariant with direct canonical and executable evidence.

## Conflicts and limitations

No material source conflict exists. Audit variants differ only in which downstream phase is selected (`definition` versus `planning`); both bypass the same durable stop.

Research was read-only. Tracker state was consumed from durable verified provenance rather than a new live API readback. The reproducer used a synthetic current-schema project, not mutation of a managed production workstream. No repair was implemented or approved.
