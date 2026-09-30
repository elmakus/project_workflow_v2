# PWV3 revision 3 — mandatory Orchestration Protocol owner decision

Date: 2026-09-30
Workstream: `change-workflow-successor-product`
Subject: `workflow-successor-product@3`
Status: OWNER-FIXED PRODUCT DIRECTION

This decision supersedes the prior revision-2 assumption that OP was optional/configurable through an Assurance Profile.

## Mandatory OP boundaries

Orchestration Protocol is a normal mandatory part of PWV3 at exactly these four boundaries:

1. Brainstorming Research;
2. Definition Review;
3. Plan Review;
4. Execution Prep / Execution Package Review.

There is no per-workstream on/off selector for these boundaries.

There is no Assurance Profile for enabling/disabling OP.

There is no launch form asking whether OP should be used.

## Abstraction boundary

PWV3 owns only the semantic fact that one of the four boundaries requires OP and the exact subject/acceptance binding needed to invoke it and consume its durable result.

The Orchestration Protocol owns how the wave is executed, including:
- worker/lane topology;
- number and type of lanes;
- fresh-context launchers;
- lane isolation;
- integration mechanics;
- discovery-completion/convergence rules;
- focused post-repair revalidation mechanics.

PWV3 must not duplicate OP's internal configuration or worker topology.

Changing OP's internal strength later (for example fewer lanes, different lane composition, or another compatible orchestration topology) is an Orchestration Protocol change, not a PWV3 product change, provided the stable PWV3<->OP invocation/result contract remains compatible.

## Runtime realization

OP remains ChatGPT-only.

- If the current owner-facing runtime is already ChatGPT, the same Main/coordinator chat may remain in place and invoke/use Orchestration Protocol. OP itself creates/coordinates the fresh contexts it requires.
- Ordinary ChatGPT stage changes do not create ceremonial handoffs.
- If Pi/Paseo reaches one of the four mandatory OP boundaries, Pi/Paseo must not substitute child agents, Pi subagents or Generic Workers. It emits a runtime-neutral handoff to ChatGPT and stops at that boundary.
- After the durable OP result is consumed, canonical PWV3 routing resumes.

## Review topology

The previously accepted OP quality rules remain in force:

- discovery is not fail-fast on the first defect;
- bounded declared coverage/convergence is completed before ordinary repair;
- findings are integrated/deduplicated without majority voting;
- one evidence-backed blocker remains blocking;
- Plan Review and Execution Package Review use one full discovery wave, then bounded repair plus fresh focused independent revalidation;
- a second full wave is required only when material scope/strategy/acceptance/review-surface drift, unbounded impact, failed applicability or a materially new defect class invalidates the original wave.

## Release implication

Mandatory OP support is part of PWV3 3.0 because these four boundaries are now part of the normal lifecycle.

The previously proposed 3.1 Assurance Profile and its launch-form/profile-editing/staleness UX are removed from the roadmap.

Likewise, future-roadmap items whose only purpose was to improve profile toggles, OP enablement UX, OP launchers, OP result visibility or profile defaults/presets are not PWV3 product backlog. Those concerns belong to Orchestration Protocol itself if ever desired.

This revision does not alter the clean-rewrite, donor, regression, runtime-neutral authority, sequential execution, Recovery, Final Qualification or Close decisions already accepted.
