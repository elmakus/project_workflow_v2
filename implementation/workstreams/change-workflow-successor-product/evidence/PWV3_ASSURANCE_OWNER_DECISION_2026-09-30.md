# PWV3 assurance/orchestration owner decision

Date: 2026-09-30
Workstream: `change-workflow-successor-product`
Brainstorm subject: `workflow-successor-product@2`
Status: OWNER-FIXED PRODUCT DIRECTION / release placement and exact schema remain under Research

## Required capability in the PWV3 lineage

PWV3 must support an optional Orchestration Protocol (OP) realization at each of these semantic boundaries:

1. Brainstorming Research;
2. Definition Review;
3. Plan Review;
4. Execution Prep / Execution Package Review.

These are independently selectable. Enabling OP at one boundary does not require enabling it at another.

The capability must be declarable near workstream start through a small owner-facing launch/assurance form, with sensible defaults. The owner may change future selections later. Exact mutation/staleness rules are to be derived by Research, but a change must not silently rewrite an already-completed review/research subject or pretend an in-flight wave reviewed a different subject.

## OP review/discovery behavior

An OP review/research wave MUST NOT stop merely because one valid defect/finding was discovered.

Its discovery phase must continue across the declared coverage until the wave's bounded coverage is actually exhausted or it reaches evidence-backed convergence/no-material-new-finding criteria.

Requirements:

- no "first finding wins" early exit;
- no fixed semantic finding/attempt count as a substitute for convergence;
- multiple independent workers may find overlapping issues;
- integration must deduplicate by root cause/trigger/repair obligation while preserving materially distinct evidence and dissent;
- majority voting does not determine truth;
- a blocking finding remains blocking even if only one valid lane found it;
- repair must not contaminate unfinished discovery for the same frozen review subject unless the defined protocol explicitly ends that discovery wave and creates a new subject/cycle.

This should preserve the useful Project Research / Coordinator Protocol pattern: broad independent discovery first, integration/dedup second, repair only afterward under the correct workflow owner.

## Product boundary

OP is an assurance realization, not a second semantic workflow and not a project-level parallel scheduler.

Canonical workflow authority remains runtime-neutral and subject-bound. Runtime/model/session/worker identities remain non-authoritative.

The release in which the full declaration/profile capability ships (3.0 vs 3.1+) remains a Research question. The requirement that PWV3 lineage supports the four optional OP boundaries above is owner-fixed.
