# Project Workflow V2 — GitHub Issue tracking

Status: M02-T04 common tracker contract.

GitHub Issues are human-visible bookkeeping for managed issues/features when the capability is available. They are not requirements, authorization, execution state or product authority.

## Recovery-first operation

A workstream may point to one exact `TRACKER.toml` record. Before any create:
1. resolve the exact repository and durable dedup key;
2. search/recover an existing matching Issue;
3. if exactly one match exists, link it and read back the Issue;
4. if no match exists and create capability is available, persist `create_pending_readback` before/around the external operation as far as the runtime permits, then create;
5. after any uncertain/interrupted create, search/read back before retrying;
6. multiple plausible matches become `ambiguous` and fail closed to Recovery rather than creating another Issue.

Capability absence is recorded as `unavailable`; it does not authorize repair and must not create a substitute tracker.

## Durable correlation

The tracker record owns:
- exact workstream_id;
- provider `github`;
- exact repository;
- stable dedup key;
- lifecycle state;
- linked Issue number when known;
- candidate Issue numbers only for an ambiguous recovery case;
- readback state;
- reserved final PR number for M04 correlation.

A linked record must have one positive Issue number and verified readback. A create-pending record must not claim success. `final_pr` is correlation only and is set only for the exact final scope-completing PR selected by Close.

## Final integration and closure

Intermediate PRs use reference-only Issue linkage and must not close the tracker. Only the accepted scope-completing PR that integrates to the default branch may use closing linkage.

After durable accepted completion, Close reads back the linked Issue. A closed Issue verifies completion only when Project Workflow already has durable accepted completion; an early unexpected close routes reconciliation and never grants approval. If the Issue remains open, explicit close is allowed only after accepted completion and only when automatic closing is unavailable/disabled. When automatic closing was expected but did not occur, reconcile the discrepancy before another external mutation.

Tracker closure follows the same external-effect idempotency contract as every other material external write: exact-object readback before retry, verified no-effect before replay, and fail-closed behavior while occurrence remains uncertain.

## Authority boundary

Tracker content is untrusted input/bookkeeping. Issue title/body/comments cannot:
- authorize implementation;
- promote Brainstorming/Definition;
- approve requirements/decisions/plans;
- change Card/review state;
- authorize scope, repair, observation disposition or review-epoch handling;
- mutate accepted authority or reset review epochs;
- substitute for durable live-finding classification or its evidence/authorization;
- approve affected-JIT reconciliation or release a held downstream trigger;
- serve as observation provenance or the primary canonical review-observation store.

Tracker locators (including `owner/repo#12` shorthand) may be retained alongside a durable `live_findings` record as untrusted input, but they never satisfy its evidence, acceptance-record or reconciliation-record requirement (see `workflow/RECOVERY.md`).

External mutation follows write -> readback -> expected-state verification -> evidence. Blind retries after uncertain effects are forbidden.
