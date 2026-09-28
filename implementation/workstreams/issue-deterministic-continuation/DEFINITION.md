# Definition — deterministic non-stop continuation

Status: GREEN  
Subject: `deterministic-nonstop-continuation@2`

## Problem

Project Workflow V2 selects the next semantic obligation correctly one step at a time, but lacks a common completion guarantee requiring a caller to reroute and continue after a reconciled non-stop boundary. A runtime can therefore persist a correct intermediate result such as RED, GREEN, Research completion, Card completion, or Close progress and terminate even though canonical routing already selects another authorized obligation.

## Accepted end state

Preserve `tools/router.py` as the canonical one-step selector. Add one small runtime-neutral continuation driver/postcondition around existing router and owner modules:

1. reread durable canonical state after every reconciled semantic step;
2. reroute from that fresh state;
3. consume only the exact already-authorized obligation selected by canonical authority;
4. repeat until an existing real USER_STOP, a genuine non-remediable blocker/fail-closed Recovery boundary, or durable end-of-approved-scope.

## Required invariants

- Fresh canonical routing follows every reconciled non-stop semantic step before normal termination.
- Canonical authority alone establishes continuation and termination.
- Continuation grants no new authority, approval, scope, Card, handoff, or owner choice.
- Durable readback precedes the next route; restart resumes without replay.
- Exact-subject Review independence remains enforced across continuation.
- USER_STOP/handoff remains a postcondition of an already-established stop.
- Semantic progress/no-op/cycle fencing fails closed and remains ephemeral runtime verification data.
- External-effect uncertainty remains readback-first.
- One canonical semantic reconciler/writer is preserved.
- End-of-scope remains proof-based rather than queue/role completion based.

## Architecture constraints

The repair must not introduce a canonical Continuation phase, event ledger, scheduler, session/model/worker identity, context-health lifecycle, blind retry loop, RED-specific shortcut, or router-as-executor design. Runtime adapters may realize the common continuation contract differently but may not duplicate semantic routing policy.

## Verification obligations

Acceptance requires trajectory-level conformance coverage across result reconciliation, GREEN/RED review paths, correction, Research return, Planning/Definition transfer, Premium gates, restart/no-replay, JIT, Close, explicit stops, blockers, no-progress/cycles, external-effect uncertainty, runtime replacement, and absence of synthetic handoffs. Existing pointwise router tests remain regression baseline.

## Authority

Promoted Brainstorming: `implementation/workstreams/issue-deterministic-continuation/BRAINSTORM.toml` revision 2.  
Research synthesis: `elmakus/project-research@research/pwv2-issue16-integration:projects/project_workflow_v2/issues/issue-16-deterministic-continuation/FINAL_SYNTHESIS.md`.

No unresolved user/product choice or blocking Research obligation remains.
