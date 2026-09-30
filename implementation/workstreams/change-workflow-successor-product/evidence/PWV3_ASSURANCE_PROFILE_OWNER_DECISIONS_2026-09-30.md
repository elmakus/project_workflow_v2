# PWV3 Assurance Profile — owner-fixed decisions

Date: 2026-09-30
Brainstorm subject: `workflow-successor-product@2`

These are owner-fixed product requirements for the PWV3 lineage. Research may recommend representation, defaults, release placement and mechanics, but must not remove these capabilities.

## Required optional Orchestration Protocol modes

A workstream must support independently selectable optional formal Orchestration Protocol (OP) realization for:

1. Brainstorming Research;
2. Definition Review;
3. Plan Review;
4. Execution Prep / Execution Package Review.

Each option is independently selectable. A user may choose any subset.

The declaration should be available at/near workstream start through a small user-facing launch/assurance form, and the user may later change a future choice before the affected assurance boundary, subject to exact-subject/staleness rules.

## Review/search behavior

When an OP-backed review or research wave is selected, it must not be fail-fast on the first discovered defect or concern.

The wave must continue its declared bounded coverage after finding defects, so that it returns a substantially complete set of findings for the frozen subject rather than one-at-a-time discovery.

Required behavior:
- findings are accumulated and deduplicated across the declared coverage;
- one finding does not terminate unexplored lanes/surfaces;
- review/research continues until the wave's coverage obligations are exhausted or a genuine safety/capability blocker prevents further evidence gathering;
- findings do not become truth by majority vote;
- integration preserves materially distinct dissent and root-cause families;
- correction happens only after findings integration, unless continued investigation itself would be unsafe or meaningless.

This does not authorize an unbounded infinite loop. Completion is coverage/convergence based, not "stop after first RED" and not arbitrary attempt-count based.

## Semantic boundary

OP changes assurance realization, not canonical workflow semantics:
- it does not create parallel Project Cards;
- it does not create a second workflow scheduler;
- runtime/model/session/worker identity remains non-authoritative;
- exact subject and acceptance authority remain canonical.
