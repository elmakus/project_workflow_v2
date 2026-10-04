# PWV3 D10 A01 Definition Review — RED pending Global-repeat owner decision

Date: 2026-10-04
Workstream: `change-workflow-successor-product`
Attempt: `D10-OP-DEFREV-A01`
Status: **RED / OWNER DECISION REQUIRED**

## Exact review result

Repository: `elmakus/project-research`
Integration branch: `review/pwv3-definition-d10-r1-integration`
Integration commit: `722c321f3386fc8205257436420a985d70ff4370`
Result path: `projects/project_workflow_v2/successor-product/v3-definition-review-d10-r1/FINAL_REVIEW.md`
Result blob: `40beb0406bb0facfe6b79e9095bc200039a45f7f`
Disposition: **RED**

Nine blocking findings were integrated. D10-F01 and D10-F03..F09 are bounded Definition repairs. D10-F02 requires one owner product decision.

## D10-F02 — explicit Global repeat versus automatic terminal closure

Already accepted owner rules:
- the user explicitly launches the independent Global Bug Hunt;
- an applicable Global CLEAR does not create a routine CONTINUE / RUN OP AGAIN gate;
- CLEAR automatically continues to fresh terminal acceptance;
- RUN OP AGAIN remains available only when explicitly requested.

The missing rule is what happens if the owner explicitly requests another same-binding Global after CLEAR has already started the automatic terminal-acceptance path.

### Option A — repeat may preempt pending terminal acceptance

An explicit same-binding Global-repeat request is legal until the fresh terminal-acceptance result has itself become accepted and advancement-sufficient.

If such a repeat request is durably published while terminal acceptance is still pending/in-progress:
1. the repeat request atomically supersedes the current terminal-acceptance frontier;
2. the predecessor CLEAR remains immutable history but loses forward authority;
3. one new exact Global attempt frontier is created and positively read back;
4. Recovery reconstructs only the new Global frontier;
5. no older CLEAR or superseded terminal-acceptance attempt may authorize advancement.

Once fresh terminal acceptance is accepted, the normal qualification path is closed; any later extra Global hunt is optional new work and does not reopen the same canonical boundary automatically.

**Recommendation: A.**

This preserves the owner's earlier intent:
- no routine post-Global user gate;
- automatic CLEAR continuation;
- but an explicit RUN OP AGAIN remains genuinely usable after seeing CLEAR, until terminal closure is actually accepted.

### Option B — automatic terminal-acceptance cut wins immediately

Once an applicable Global CLEAR is consumed and the terminal-acceptance frontier is durably established, a same-binding Global repeat is no longer legal inside that canonical qualification cycle.

To run Global again, the repeat must already have been requested before CLEAR consumption / terminal-frontier creation.

This is simpler, but in practice the user may have little or no opportunity to see CLEAR and then explicitly request another Global because automatic continuation begins immediately.

## Workflow consequence

Until the owner selects A or B:
- D10 remains active and RED;
- no D10 repair may invent the precedence;
- Premium A is not due;
- Strategic Planning is unauthorized.

After the owner decision, the remaining A01 findings can be repaired as bounded D11 Definition work and focused independent revalidation can cover RG-A through RG-D unless repair triggers a new full-review condition.
