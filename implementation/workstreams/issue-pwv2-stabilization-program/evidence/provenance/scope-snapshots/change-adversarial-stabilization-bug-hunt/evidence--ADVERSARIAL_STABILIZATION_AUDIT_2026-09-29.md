# Project Workflow V2 — adversarial stabilization bug hunt

Date: 2026-09-29
Mode: diagnosis/research only
Canonical snapshot: `main@d3ab917f02e4de91b7dbb17915c2287c2387333e`
Repository: `elmakus/project_workflow_v2`
Audit workstream: `change-adversarial-stabilization-bug-hunt`

No repair is authorized by this audit. GitHub Issues are bookkeeping only.

## Method

The audit entered through current `workflow/ROUTER.md`, then loaded `PROJECT.md`, the exact audit workstream, and progressively inspected only canonical owner modules, executable contracts, templates, tests, existing workstreams, and issue trackers needed to test lifecycle invariants.

The audit treated recent defects as signals, not as a shared root cause. It checked:
- Intake through Close routing and fresh-context restart;
- producer -> consumer round trips;
- malformed/legacy state and current-schema-valid contradictory state;
- Premium A/B/C subject bindings and receive behavior;
- Card/Result/Review exact identity;
- RED -> repair -> re-review and supersession;
- CI queued/in_progress/success/failure/cancelled;
- Research/Recovery precedence;
- continuation/progress-fuse semantics;
- final Close and end-of-scope reconstruction.

## Consolidated defect map

| ID | Invariant / lifecycle boundary | Concrete reproducer / evidence | Relationship | Disposition |
|---|---|---|---|---|
| C01 | Non-stop semantic completion must continue until a real stop | Existing #16 reproduction: terminal RED was durably written and invocation returned before corrective classification. Current `CONTINUATION.md` and `classify_route_completion` now classify RED path as continuation, not stop. | #16 | Already covered / closed baseline |
| C02 | Pending CI is not semantic success; only positive terminal conclusion succeeds | `classify_external_evidence`: queued/requested/waiting/pending/in_progress -> pending observation; completed+success/passed -> terminal success; failure/failed/cancelled/timed_out/action_required -> terminal failure. | #22 | Already covered / current requested matrix is correct |
| C03 | Canonical producers must emit the schema consumed by current router/validators; supported older V2 must reconcile fail-closed | #23 fresh materialization and active-workstream reproductions. | #23 | Existing open issue |
| C04 | Planning B/C bindings and Task Board serialization must round-trip through current validators; invalid state cannot continue | #26 proves short `plan:P3@blob` B/C subjects and literal `\\n` board corruption, with downstream progression. | #26 | Existing open issue |
| C05 | Fresh-context handoff receipt must consume the transferable boundary instead of replaying it | #25 Premium B loop. Current `receive_contract.consume_handoff_and_classify` advances only if its caller supplies a post-receipt route; the durable router itself still returns the same premium stop until owner state changes. The same structural contract is exercised by tests for A/B/C. | #25; regression surface of closed #17 | Additional evidence for existing issue; no new issue |
| C06 | Invalid terminal GREEN history must remain immutable and be superseded append-only | #18 invalid GREEN independence contradiction. Current validator fails closed but Recovery has no supersession path. | #18 | Existing open issue |
| C07 | Plan Review legality must compose execution dependencies with acceptance gates | #14 documented cross-gate cycle that passed planner audit + Plan Review. | #14 | Existing open issue |
| N01 | A DONE Card must have reconstructible exact Result and valid required Review before Close | Current validator accepts a path-only Result locator on DONE. Router all-DONE branch does not read Card/Result/Review and routes Close. Existing all-DONE workstreams also contain historical Result/Review formats current parsers would reject if reread. | New #27 | Distinct current-schema-valid terminal semantic-closure defect |
| N02 | Completed execution Research must return to exact execution owner once | Workstream with both manifest `[research]` and `[task_board]`, plus complete Research `return_target="execution_resolution:M01-T04"`: early manifest Research branch indexes an owner map limited to intake/brainstorming/definition and falls into Recovery before the board branch that supports execution prefixes. | New #28 | Distinct selector precedence/return-target defect |
| N03 | End-of-scope must be reconstructible after fresh restart | `feature-common-preexecution-core` has durable evidence `APPROVED SCOPE COMPLETE` and `end_of_scope_stop`, but selector sees all-DONE board and always routes Close. No Close completion locator/state is available to the router. | New #29 | Distinct durable terminal-resume defect |
| N04 | GREEN review must bind an exact acceptance surface, not only exact reviewed subject | Implementation Review accepts Task Card by mutable path only: mutate Card acceptance/tests after GREEN while Result subject remains unchanged and router can still finalize. Plan Review can use an unrelated syntactically valid authority path because acceptance is not bound to current Definition authority. | New #30 | Distinct Review acceptance-identity defect |
| N05 | Stage-6 Plan Review attempts must be append-only across material replans | Workstream has one fixed `PLAN_REVIEW.toml` locator; validator permits only that filename and validates one attempt. P1 RED -> P2 material replan requires replacement of the selected record or leaves prior RED unreachable from current canonical state. | New #31 | Distinct Stage-6 history/supersession defect |
| N06 | Issue alignment requires a concrete repair subject and Intake identity must agree with workstream identity | Active issue with empty `repair_subject` passes validation then routes to real `issue_alignment` stop with empty subject. Separately, `WORKSTREAM.kind="change"` + `INTAKE.kind="issue"` both validate and router follows Intake. | New #32 | Distinct current-schema-valid Intake relational-closure defect |
| N07 | Durable explicit user stop has precedence over next-stage routing | Valid promoted Brainstorm with `explicit_user_stop=true` plus matching active Definition: router returns Definition before reaching explicit-stop check. | New #33 | Distinct stop-precedence/contradiction defect |

## Detailed reproductions

### N01 — terminal Card semantic closure (#27)

Starting from `tests/fixtures/router/valid-project`:
1. set M01-T04 status to `done`;
2. add `[cards.result]` with class=result and only a valid workstream-local result path; no commit/blob and no file are required by `validate_board`;
3. set the Task Card review requirement to `required`;
4. leave review attempts empty or terminal RED;
5. route.

Executable cause:
- `validate_locator(..., "result")` requires 40-hex commit/blob only if one of those keys is already present;
- DONE only requires the presence of a Result table;
- all-DONE path routes Close without parsing the stable Card, Result content, or review history.

Expected invariant: exact terminal proof must be validated before Close.

### N02 — execution Research shadow (#28)

Use one valid Research record:
- state = complete;
- origin_role = execution_resolution;
- return_target = execution_resolution:M01-T04;
- complete source accounting.

Point both the manifest `[research]` and Task Board `[research_obligation]` to it.

Executable cause:
- early manifest-level complete-Research path uses an owner map with only intake/brainstorming/definition;
- execution-prefixed return target causes KeyError -> generic Recovery;
- later board-level code already knows how to route execution prefixes but is not reached.

Expected invariant: one exact Research return owner is reconstructed independently of which valid locator made the record reachable.

### N03 — Close terminal resume (#29)

Current repository evidence:
- `implementation/workstreams/feature-common-preexecution-core/evidence/M07-close-postmerge-2026-09-23.md`: GREEN / APPROVED SCOPE COMPLETE and `Close continuation is end_of_scope_stop`;
- `handoffs/M07_ADOPTION_SCOPE_COMPLETE.md`: CLOSED / INTEGRATED / END-OF-SCOPE READY;
- Task Board: only M07-T09 DONE.

Fresh selection still has only the all-DONE -> Close router path. `close_continuation` can classify terminality only from booleans supplied by a caller; no canonical durable Close binding lets a fresh router reconstruct those booleans.

Expected invariant: fresh restart is observationally equivalent to the context that completed Close.

### N04 — Review acceptance identity (#30)

Implementation Review:
1. freeze GREEN review for Result S with acceptance Task Card path C;
2. mutate acceptance/tests in C without changing path;
3. keep Result subject S unchanged;
4. route.

The old GREEN remains valid because acceptance identity has no immutable Card content identity.

Plan Review:
1. use a valid frozen plan subject;
2. create matching GREEN Plan Review but set acceptance to unrelated valid authority path such as `workflow/ROUTER.md`;
3. `validate_plan_review` accepts because it does not bind acceptance to the Definition requirements/decisions.

Expected invariant: both subject and acceptance surface are exact and still current at consumption.

### N05 — Plan Review append-only history (#31)

Policy says RED history remains attached and changed material subject requires a new attempt. Executable state has one `[plan_review]` locator fixed to `.../PLAN_REVIEW.toml`; no ordered history exists. After P1 RED and material P2 replan, selecting the new attempt necessarily replaces the singleton current record or leaves the old attempt outside canonical selected state.

Expected invariant: failed attempt history remains durably reachable while the new exact attempt is current.

### N06 — Intake relational closure (#32)

Reproducer A:
`kind=issue, state=active, repair_subject="", response_kind=none, alignment_state=pending` passes `validate_intake`. Router skips prior-art logic (empty subject) then emits real `issue_alignment` stop with empty subject.

Reproducer B:
WORKSTREAM kind and INTAKE kind can disagree because no cross-record check exists.

Expected invariant: marker/symptom remains diagnosis work; only a concrete diagnosed repair subject can reach alignment.

### N07 — explicit stop precedence (#33)

Use:
- Brainstorm: promoted, GREEN challenge, exact authorized promotion, `explicit_user_stop=true`;
- Definition: active and bound to same promoted scope.

Both validate. Router processes Definition first and returns Definition before later checking the Brainstorm explicit stop.

Expected invariant: explicit durable stop wins, or contradictory state fails closed.

## Requested adversarial surfaces with no new distinct tracker

### Premium A/B/C immutable bindings

Current `validate_planning` correctly requires:
- A subject == exact planning entry subject;
- frozen/approved B subject == full `repository@commit:path@blob`;
- approved C subject == same full immutable plan key;
- editorial exemption remains bound to exact prior reviewed base.

#26 proves writers can nevertheless emit short B/C bindings and progression can occur without effective validation. #25 proves fresh Premium B receipt can loop. The receive helper/tests structurally exercise A/B/C transfer, so this audit records that as additional evidence for #25/#17 rather than widening either tracker or opening a duplicate.

### CI external evidence

The exact requested states are classified conservatively and correctly in current `tools/continuation_contract.py`:
- queued/requested/waiting/pending/in_progress -> pending observation;
- success/passed -> terminal success;
- completed requires supported positive/negative conclusion;
- failure/failed/cancelled/timed_out/action_required -> terminal failure;
- missing -> exact-subject readback;
- wrong-subject terminal/pending evidence fails closed.

No distinct new CI issue was found beyond #22.

### Progress fuse / deterministic continuation

`classify_route_completion` and `classify_progress` encode the intended non-stop continuation and no-progress/cycle rules. The progress oracle is not itself the router and canonical policy assigns enforcement to the invoking context. #16 is the prior observed non-stop-return failure; #26 supplies current evidence that invalid durable state can nevertheless be followed by downstream progression. This audit found no separate reproducer that should be split into another issue beyond those existing trackers.

### Malformed / legacy durable state

#23 owns producer/current-consumer schema alignment plus supported older-V2 reconciliation. #26 owns the focused valid-writer/invalid-serialization and ineffective validation case. New terminal semantic closure (#27) is intentionally separate because its minimal reproduction is current-schema-valid.

### Review supersession

#18 remains the implementation-Review invalid-terminal-GREEN supersession tracker. #31 is separate because Stage-6 Plan Review has a different singleton durable model and cannot represent append-only attempts at all.

## Root-cause partition

The findings do **not** share one root cause:

1. producer/schema drift — #23/#26;
2. handoff receipt/transfer semantics — #25;
3. terminal semantic validation omission — #27;
4. selector precedence/return-target handling — #28/#33;
5. missing durable terminal Close identity — #29;
6. mutable/unbound acceptance identity — #30;
7. missing Stage-6 attempt-history model — #31;
8. missing Intake relational constraints — #32.

## Stop condition

This audit is diagnosis/research only. The next legal transition for the audit workstream is an explicit user stop. No Definition, Planning, Execution Prep, Execution, Review repair, or code change is authorized by this research result.
