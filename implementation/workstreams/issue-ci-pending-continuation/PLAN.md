# Master Plan — CI-pending deterministic continuation

Cycle: 1  
Entry subject: `ci-pending-deterministic-continuation@1`

## Strategy

Repair the regression at the smallest common semantic boundary introduced by issue #16: distinguish pending exact-subject external evidence from a claimed successful semantic reconciliation. Preserve the router as a one-step selector and preserve the existing no-progress/cycle fuse for true semantic stagnation.

No durable polling/session state, new workflow phase, fixed sleep, or CI-provider-specific authority is introduced.

## Milestones

### M01 — Pending external-evidence contract

Extend the common continuation contract with a small runtime-neutral classification for exact-subject external evidence.

Acceptance:
- terminal success is consumable evidence;
- terminal failure is terminal negative evidence and remains correction input;
- queued/requested/waiting/pending/in_progress classify as pending observation;
- temporary missing run after a known trigger classifies as exact-subject readback/observation, not success;
- pending observation does not claim semantic reconciliation and therefore does not trip the unchanged-fingerprint fuse;
- malformed/unsupported evidence fails closed.

Likely surfaces:
- `tools/continuation_contract.py`
- `workflow/CONTINUATION.md`

### M02 — Execution/evidence composition

Specify how Execution waits on required exact-subject evidence before accepting a semantic Card result.

Acceptance:
- an implementation return whose required CI is non-terminal remains `in_progress`;
- exact-subject terminal success can satisfy the evidence gate;
- terminal failure routes bounded correction/recovery;
- technical runtime observation limits remain technical aborts, not workflow stops;
- no runtime/provider/session identity becomes durable authority.

Likely surfaces:
- `workflow/EXECUTION.md`
- `workflow/RECOVERY.md` only if wording is required to preserve recovery semantics.

### M03 — Deterministic regression coverage

Add focused unit/trajectory tests reproducing the timing-independent semantics.

Required cases:
1. terminal success;
2. terminal failure;
3. queued;
4. in_progress;
5. immediate post-push absence requiring exact-subject readback;
6. same durable workflow fingerprint while external evidence is legally pending;
7. unchanged fingerprint after a claimed semantic reconciliation still fails closed;
8. existing issue #16 route-after-reconcile and cycle tests remain GREEN.

Likely surfaces:
- `tests/test_continuation_contract.py`
- `tests/test_m05_trajectory.py`
- any narrower execution-contract test only if implementation introduces a separate helper.

### M04 — Integration qualification

Run affected unit suites plus the repository's deterministic workflow validation surface. Verify no router/state schema regression and no new durable runtime state. Perform independent final-integration review on the exact final subject unless exact stronger review coverage fully covers it.

## Requirement coverage

Definition requirements 1–7 are owned by M01/M02. Requirement 8 is owned by M03. Requirement 9 is a cross-cutting M01–M04 regression gate.

Repository requirements preserved explicitly:
- PWV2-REQ-004/006: runtime identity remains non-canonical;
- PWV2-REQ-031..033: durable evidence/recovery and readback-first semantics remain intact;
- PWV2-REQ-034..038: exact-subject review behavior is unchanged;
- PWV2-REQ-051/052: bounded YAGNI repair and precise Cards;
- PWV2-REQ-067..070: deterministic continuation and real-stop semantics remain intact;
- PWV2-REQ-074: automated deterministic validation.

## JIT Card strategy

Execution Prep should initially materialize M01 and M03 only if their contracts are independently stable. M02 may be combined with M01 when the implementation helper makes the Execution wording mechanically determined; otherwise materialize it after M01's exact result. M04 remains a bounded qualification/final-review gate after implementation results exist.

## Planner challenge audit

GREEN.

Challenges considered:
- A fixed wait would hide rather than remove the race: rejected.
- Treating external status changes as durable semantic progress would leak provider/runtime state into authority: rejected.
- Disabling the progress fuse would regress issue #16 cycle safety: rejected.
- A generic polling subsystem is unnecessary; the contract only needs to distinguish legal pending observation from reconciliation and require exact-subject readback.
- CI failure must not become a stop merely because it is terminal.
- Immediate run absence is materially distinct from terminal absence of required evidence and therefore requires bounded exact-subject observation/readback.

The plan is bounded by the authorized repair and introduces no unresolved product decision.
