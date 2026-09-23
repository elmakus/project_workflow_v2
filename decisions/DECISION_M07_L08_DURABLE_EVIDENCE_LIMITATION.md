# M07 L08 durable-evidence limitation — user decision

Date: 2026-09-23
Status: ACCEPTED
Scope: M07 first-production qualification only

## Decision

The user explicitly accepts the known M07-T06 L08 evidence-retention limitation as non-blocking for the first PWv2 production-ready adoption.

The accepted limitation is narrowly scoped to this fact:

- the original L08 live run was durably reported as completing the required N-CAPABLE sequence (S1 BAD -> independent RED -> genuine delegated bounded correction -> S2 GOOD -> independent GREEN -> same-top-level-invocation finalization);
- the terminal disposable consumer Git objects named by that report are no longer independently recoverable from the surviving local fixture or durable GitHub branch;
- therefore a fresh reviewer cannot re-read those exact terminal consumer Git objects today.

The user does **not** require an L08 rerun solely to recreate those missing disposable terminal Git objects.

## What this decision does not waive

This decision does not waive or redefine PWv2 runtime semantics and does not convert the prior independent review verdict into GREEN.

It does not waive:
- PWV2-REQ-075's requirement that the actual N-CAPABLE and N-CHATGPT scenarios were executed before production acceptance;
- the L08 semantic oracle or genuine delegated-capability requirement;
- independent review independence/history requirements;
- the final workstream independent-integration review gate;
- candidate automated qualification;
- pilot rollback/readback requirements;
- any future production evidence/readback obligation outside this historical disposable L08 fixture.

The prior R01 RED remains immutable evidence for its exact former review subject.

## Acceptance rationale

M07-T06 already has a durable control-repository evidence report for the actual L08 run. The defect identified by R01 is loss of later re-readability of the disposable consumer's terminal Git objects, not evidence that the candidate failed the L08 semantic topology.

For this one historical disposable fixture, the user accepts that evidence-retention/reproducibility gap as a known lower-severity limitation. The controlling workstream may therefore treat M07-T06 as completed without rerunning L08, provided the limitation is explicitly carried into the next final-production freeze and independently reviewed as part of the new exact final-integration subject.

No claim may be made that the missing Git objects still exist or were independently re-read after R01.
