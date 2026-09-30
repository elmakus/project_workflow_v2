# PWV3 assurance/orchestration owner decision

Date: 2026-09-30
Workstream: `change-workflow-successor-product`
Brainstorm subject: `workflow-successor-product@2`
Status: OWNER-FIXED PRODUCT DIRECTION / release placement and exact schema remain under Research

## Required optional OP boundaries

PWV3 must support an optional Orchestration Protocol (OP) realization at each of these semantic boundaries:

1. Brainstorming Research;
2. Definition Review;
3. Plan Review;
4. Execution Prep / Execution Package Review.

These are independently selectable. Enabling OP at one boundary does not require enabling it at another.

The capability must be declarable near workstream start through a small owner-facing launch/assurance form, with sensible defaults. The owner may change future selections later. A change must not silently rewrite completed evidence or pretend an in-flight wave reviewed a different subject.

## OP runtime ownership: ChatGPT only

Whenever OP is selected for a boundary, the OP wave is executed **only in fresh ChatGPT contexts under the Project Research / Coordinator Protocol**.

This is true regardless of the runtime that produced the subject:

- if Pi/Paseo/Main reaches an OP-selected boundary, it MUST NOT satisfy that OP obligation with Paseo child agents, Pi subagents, Generic Worker delegation or a local multi-agent substitute;
- it MUST emit a mandatory runtime-neutral handoff to ChatGPT and stop at that boundary;
- if ChatGPT itself authored/prepared the subject, no cross-runtime handoff is needed; however any assurance step that requires fresh independence MUST launch fresh ChatGPT context(s) rather than self-review in the authoring context;
- the completed integrated ChatGPT OP result is then consumed by the canonical PWV3 workflow, after which work may resume in either supported runtime as permitted by normal routing.

Pi/Paseo may continue to use child agents/Generic Workers for ordinary runtime work and for non-OP assurance modes where the accepted product contract permits it. It may not impersonate an enabled OP boundary.

Thus an enabled OP mode implies **mandatory fresh-ChatGPT realization**. A cross-runtime handoff is mandatory only when the current runtime is not ChatGPT. When the current runtime is already ChatGPT, the workflow may stay in ChatGPT and needs only the fresh-context launcher/locator required by the assurance protocol; ordinary same-context pre-planning transitions do not create ceremonial handoffs.


## Handoff minimization rule

Handoff exists to transfer work across a real boundary, not because a lifecycle label changed.

- ChatGPT -> ChatGPT, same context allowed by the current obligation: continue directly; no handoff.
- ChatGPT -> fresh ChatGPT required for independence/OP: emit only the minimal fresh-context launcher/locator needed to start the new context(s). This is a context handoff, not a runtime handoff.
- Pi/Paseo -> ChatGPT because an enabled OP boundary was reached: emit a mandatory runtime-neutral handoff and stop until the durable integrated ChatGPT OP result exists.
- ChatGPT -> Pi/Paseo, or Pi/Paseo -> ChatGPT for another capability reason: handoff only when the runtime actually changes or the target capability requires a fresh context.

For the intended default construction flow, Brainstorming/Research/Definition and other pre-Planning work may remain continuously in ChatGPT unless an OP/fresh-independence boundary itself requires fresh ChatGPT contexts. Do not manufacture a separate handoff merely between semantic stages.

## Discovery behavior

An OP research/review wave MUST NOT stop merely because one valid defect/finding was discovered.

Its discovery phase continues across the declared coverage until the bounded coverage is exhausted or evidence-backed convergence/no-material-new-finding criteria are satisfied.

Requirements:

- no "first finding wins" early exit;
- no fixed semantic finding/attempt count as a substitute for convergence;
- independent workers may find overlapping issues;
- integration deduplicates by root cause/trigger/repair obligation while preserving materially distinct evidence and dissent;
- majority voting does not determine truth;
- one evidence-backed blocking finding remains blocking even if every other lane is clear;
- repair does not contaminate unfinished discovery for the frozen review subject.

The intended topology is: complete broad discovery -> integrate/deduplicate -> repair under the owning semantic stage -> post-repair verification.

## One full OP discovery wave per boundary subject/cycle

For Plan Review and Execution Prep Review, the owner does not want an automatic second **full OP discovery wave** after ordinary repair.

The safe semantics are:

1. run one full OP discovery wave on the frozen subject;
2. integrate all findings;
3. if RED, repair under the owning stage;
4. verify closure of the accepted findings and the repaired exact subject with fresh independent **focused post-repair revalidation**;
5. if that focused revalidation is GREEN and no material scope/strategy/acceptance change or unbounded impact remains, continue downstream;
6. do not run a second full OP discovery wave merely because repair changed bytes.

Focused post-repair revalidation is not a second full OP hunt. It exists because an exact repaired subject cannot lawfully inherit a RED verdict without verifying that the blockers were actually closed.

Escalate to a new full OP wave or upstream semantic owner only when:
- repair materially changes product scope, strategy, acceptance intent or the review surface;
- impact cannot be safely bounded;
- focused revalidation discovers a materially new defect class that invalidates the original coverage assumption;
- the original wave/subject cannot be proven applicable.

The same principle applies to Definition Review when a correction remains bounded: full rediscovery need not be repeated mechanically, but the corrected exact Definition must receive sufficient fresh independent verification before GREEN. Research return follows its own exact applicability rules.

## Product boundary

OP is an assurance realization, not a second semantic workflow and not a project-level parallel scheduler.

Canonical workflow authority remains runtime-neutral and subject-bound. Runtime/model/session/worker identities remain non-authoritative. The fact that OP execution is restricted to ChatGPT is a product/runtime policy for realizing that assurance mode, not semantic authority derived from ChatGPT identity.

The release in which the first-class declaration/profile capability ships (3.0 vs 3.1+) remains a Research/release decision. The four optional OP boundaries and ChatGPT-only OP realization are owner-fixed.
