# Project Workflow V2 — Common independent implementation review

Status: M03-T03 exact-subject review contract.

Implementation/final review is an exact-subject blocking gate when REQUIRED or when RECOMMENDED has been activated by the stable Card/workstream contract. Stage-6 Plan Review remains separate premium planning semantics.

## Subject and acceptance identity

Each review attempt binds:
- one exact immutable Git content subject;
- one exact acceptance surface (normally the stable Task Card for Card review);
- one append-only attempt ID;
- semantic independence evidence;
- pending/in-progress/GREEN/RED lifecycle;
- durable verdict evidence for terminal attempts.

A changed reviewed subject or a new verdict attempt is a new attempt. Existing terminal attempts remain immutable history.

## Semantic independence

Independence is about material production/repair of the exact subject, not runtime identity.

A context that materially produced or repaired the subject cannot issue its independent verdict. Concrete provider/model/session/worker/invocation identity is non-canonical and must not be persisted merely to prove independence.

A runtime may satisfy review with an internal independent context when one genuinely exists. Otherwise:
- if the current context did not produce/repair the subject, it may review it;
- if the current context produced/repaired it and cannot obtain a qualifying independent context, freeze the pending exact review obligation and use a fresh-context locator handoff.

## Blocking lifecycle

For REQUIRED/activated RECOMMENDED review:
- no attempt / pending / in-progress / RED blocks terminal Card completion;
- GREEN for the exact current subject + acceptance permits deterministic post-review finalization;
- GREEN is not a verdict-only user stop;
- RED remains attached to its failed subject and routes to corrective classification; RED itself is not automatically a user stop.

## Attempt history

The selected Card owns ordered review-attempt locators in its Task Board state. Attempt files are workstream-local under `reviews/`.

At most one pending/in-progress attempt may exist and it must be the last attempt. Terminal attempts keep non-empty evidence. A later attempt never overwrites a prior GREEN/RED file.

## Runtime boundary

Capability detection and reviewer context launch remain runtime behavior. Project Workflow stores only the semantic attempt, exact subject/acceptance, independence basis and verdict/evidence.
