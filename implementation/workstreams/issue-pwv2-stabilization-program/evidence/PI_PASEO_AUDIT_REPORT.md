# Independent Pi/Paseo runtime defect map — Project Workflow V2

## Verdict

**PWv2 cannot currently be certified deterministic and fail-closed end-to-end through Pi/Paseo.** Several individual selectors/oracles are deterministic and their negative controls pass. However, accepted strings are not consistently tied to actual immutable Git content, some fresh-resume paths bypass authority validation, terminal evidence/history is insufficiently constrained, and Close completion is not selected from a machine-bound durable completion record.

This is diagnosis/research only. Severity below is invariant risk, never implementation authorization. No fixes, canonical workflow edits, live workstream repairs, integration, deployment or closure were performed. Existing issue scopes were not changed. Issues and comments were read only for dedup, not correctness authority; no other stabilization audit's reports/artifacts were consumed.

## Authority, method and evidence

- Repository explicitly selected by user: `elmakus/project_workflow_v2`; current default branch confirmed `main`.
- Canonical snapshot: `d3ab917f02e4de91b7dbb17915c2287c2387333e`; remote main reread during audit remained at that SHA.
- Canonical modules: current `workflow/ROUTER.md`, all lifecycle owners Intake through Close, STATE/AUTHORITY/CONTINUATION/USER_STOP/WORKSTREAMS/GITHUB_ISSUES, and executable `tools/*.py`.
- Selected workspace `/worktrees/1n4cii8x/roasted-squid` is a clean worktree at that snapshot on branch `roasted-squid`. No product files changed. Read-only canonical clone `/tmp/pwv2-runtime-audit/canonical` has an audit branch at the same unchanged commit.
- Existing cumulative repository suite: **271 discovered tests pass**, plus its component runs; `scripts/test.sh` finishes `M01 baseline checks: PASS`. This does not validate every current live/historical artifact.
- Primary harness: 72 observations, including committed synthetic producer output -> new Git clone -> fresh Python canonical consumer, exact-subject CI status matrix and Close oracles. Additional precedence/recovery, identity, dirty-state and unsafe-concurrency probes are separately recorded.
- Three initial native caller-scoped Paseo children: two independent read-only auditors in separate fixture spaces and one fresh Pi consumer of 16 clean committed lifecycle subjects. A fourth fresh child covers seven additional Intake/Research/tracker subjects. All real inference used guarded native-create-agent arguments, `pi/meta/muse-spark-1.3-contributor`, thinking `max`, `notifyOnFinish=true`; Main's model was not changed. Parent relationship/model/max were read back. Runtime identity is diagnostic metadata only, never workflow authority.
- Main read diagnostic files, reran findings independently, and compared all **23 fresh native consumer cases plus seven native session-resumption cases** against exact Git HEADs/clean status and fresh production invocations. The resumed child rerecovered from Git and rerouted from `/tmp`, rather than using its previous conversational completion or output as authority. Child chat completion was never accepted as semantic evidence.
- `results.json`, `extra-results.json`, `identity-extra-results.json`, `isolated-controls.json`, `artifact-inventory.json`, `parent-resume-rerun.json`, native consumer artifacts and the diagnostic issue bodies contain exact outputs/locators.
- Synthetic commits are **local audit subjects**, not product-remote commits. Git bundles preserve those histories with their paths/HEADs recorded. Reproducer scripts are diagnosis-only, not production fixes.

### What the execution proves, and what it does not

The primary confirmed observations are canonical consumer **selection/validation** of committed state and fresh native Pi consumption of those same subjects. Invalid state selecting an execution/finalization owner is not a claim that this audit actually performed unauthorized implementation or merge; no such mutation was allowed. An owner agent might still obey prose and block later. That additional opportunity to catch an error is not an executable selector guarantee.

No normal production machine-constrained writer exists for most lifecycle records. Therefore these tests cannot prove that arbitrary agent-authored production output is always valid. They do prove concrete consumer acceptance/rejection and expose discrepancies between purported validity and durable content. A fixture helper is not misrepresented as a shipped normal-lifecycle writer.

No live PR merge, issue closure, CI trigger/cancellation, remote concurrent publication, UI persistence restoration, kill/restart during an external write, or hostile child write into a real workstream was performed. These would exceed a read-only audit. External cases were exercised as synthetic observations; existing exact-head GitHub Actions evidence was read back without triggering inference or CI. Pending classification is not proof of a connected Pi polling/reconciliation loop.

## Consolidated finding classifications

Every confirmed defect below has exactly one class:
- **A**: already covered by an existing issue;
- **B**: new independently established evidence/root-cause information within an existing issue's scope;
- **C**: distinct defect, new diagnosis-only issue.

All confirmed product-consumer defects are **runtime-independent** unless explicitly noted. Pi/Paseo fresh sessions/concurrency expose them; reproduction through Pi is not itself a reason for a duplicate issue.

| ID | Class / tracker | Lifecycle boundary | Violated invariant / result | Diagnostic severity |
|---|---|---|---|---|
| D01 | C / #34 | Result -> Review -> finalization | Matching claimed Result/Review SHA strings do not verify Git objects or the bytes consumed; changed Result/nonexistent blob still selects GREEN finalization. | High |
| D02 | C / #35 | active Card -> fresh Execution resume | Active no-Result path reads but does not parse/refresh the stable Card or named authority; READY controls reject the same inputs. | High |
| D03 | C / #36 | partial pre-execution write -> resume | Planning without Definition and Plan Review without Planning are ignored; even materialized premium-A-due state can be bypassed into Execution. | High |
| D04 | C / #37 | terminal Review -> repair/re-review | A committed valid terminal R01 can be rewritten GREEN->RED or RED->GREEN at the same path/ID and consumed without append-only rejection. | High |
| D05 | C / #38 | child proof -> Result/Review -> parent consume | Result evidence and terminal Review evidence may be absent; syntactically valid locators still select finalization. Each missing-evidence path was isolated independently. | High |
| D06 | C / #39 | Execution -> durable Result -> no-replay | Arbitrary non-Git Implementation subject is parsed as valid semantic recovery truth and selects result_reconciliation. | High |
| D07 | C / #40 | Stage-6 review start -> fresh resume | Shared validator accepts in_progress; selector labels it RED and sends it to Planning correction. | Moderate-high |
| D08 | B / #23 | producer commit -> independent consumer | Default-branch artifacts include incompatible current/older schemas; independently reproduced the #22 materialization/recovery history and scanned 86 artifacts. | High compatibility/liveness risk |
| D09 | A / #26 | Planning/Board/Result write -> continuation | Short B/C bindings fail validation; wrong status/raw-ref/serialized state is rejected or technically aborts. Existing issue already covers producer-enforcement and pending-reservation gap; no new live downstream-bypass claim. | High when ignored by caller |
| D10 | A / #30 | GREEN -> acceptance change -> resume | Same Result, materially changed same-path Card acceptance still selects post_review_finalization. | High |
| D11 | A / #27 | DONE -> Close | Schema-valid path-only Result with absent proof/Review reaches Close without reconstruction. | High |
| D12 | A / #28 | Research complete -> exact return owner | Co-pointed manifest Research shadows Board-owned execution return and selects generic Recovery instead of exact return. | Moderate liveness |
| D13 | A / #29 | Close complete -> fresh resume | Completed default-branch workstream with durable closure evidence still selects undifferentiated Close; end_of_scope requires caller-supplied booleans. | High restart equivalence |
| D14 | A / #31 | RED plan -> material replan -> new review | Exact-path Plan Review locator permits singleton PLAN_REVIEW.toml; no selected append-only history analogous to implementation Review. | High history/recovery risk |
| D15 | A / #18 | internally invalid terminal GREEN -> Recovery | Invalid independence metadata fails closed; appending a valid later attempt cannot make an invalid historical record validate under the existing history validator. Supersession remains undefined. | High recovery liveness |
| D16 | A / #32 | Intake diagnosis -> alignment | Empty repair subject selects an alignment stop; manifest/Intake kind has no relational equality guard. Empty-subject case independently rerun. | Moderate |
| D17 | A / #33 | explicit stop -> Definition/Planning | Promoted Brainstorm explicit_user_stop=true is bypassed by Definition routing; independent variant selects Planning after GREEN Definition. | High authorization-boundary risk |

Detailed D01–D07 reproducers, Git evidence, invariants and distinctions from adjacent issues are in the appended diagnosis reports. D08–D17 evidence is below. No finding is assigned a shared root cause merely because the symptoms overlap.

## Exact reproduction and durable evidence for existing-issue findings

### D08 — B / #23: producer/consumer compatibility

Invariant: materialized supported V2 state must be consumable by a fresh canonical consumer, or have an explicit fail-closed reconciliation path preserving accepted scope and identities.

Independently read immutable product Git history:
- `7888399a958e0b824b318165fae234265907dcdb`: newly materialized #22 WORKSTREAM fails current `created_from` 40-hex validation.
- `f0468f2b1b00ce1a1bae618c34c27bc6f47f59b7`: manifest still fails; Board `review_pending` fails current Card status enum.
- `1e0b295381d010df564489c66be33dfd94638b8f`: reconciled manifest/Board both validate. This demonstrates concrete correction of representation, not a hypothesis about who wrote it.
- #22 R01 at `51c5ebccca4ea1b4e1fd60b3f36dddc5fb2e72d2` used subject class `git_commit`; `d3febb5` recovery rebound pending R01 to a `git_blob` Result; `7a75790` then recorded RED. `R01-history.txt` retains exact content. The initially invalid pending binding was changed in place; this is evidence relevant to the already-tracked pending-reservation reconciliation gap, not proof of a safe immutable migration.
- Valid terminal RED R01 remained on its old Result coordinates after correction; new R02 binds corrected Result at `a4ad1db53dddfa31f8024f2e13e4a182cc710474`, blob `fd4c35e544bfb7a237389f156c7d6fdbeaa4cfb4`. This is a positive example of separate attempts after correction, not a claim all repair paths are safe.

Reproduce: `git show <commit>:implementation/workstreams/issue-ci-pending-continuation/{WORKSTREAM,TASK_BOARD}.toml`, parse with tomllib, call canonical validate_workstream/validate_board. Run `artifact-inventory.py` for full inventory. At pinned main, 86 artifacts checked, 45 fail their individual current validators. **Some are unselected historical records**, so this is not a claim that all 45 are active route blockers. Current selected workstreams also produce Recovery for malformed creation identity or invalid approved Plan Review. Existing artifact serialization inconsistencies do not establish Pi-vs-ChatGPT authorship.

### D09 — A / #26: malformed writer/state interfaces

Reproducer: `extra.py` case `short-planning-gate` constructs canonical `[subject]` but B uses `plan:P1@<blob>`; exact default router selects Recovery for premium B subject mismatch. `harness.py` cases wrong-enum/wrong-field/short-created-from fail closed.

Invalid TOML/literal backslash-n/partial-write injections into manifest and Board abort with nonzero TOMLDecodeError, rather than structured Recovery. Malformed PROJECT frontmatter independently does the same (`extra-results.json`). This is a fail-closed **technical abort**, not downstream continuation or semantic success. The primary harness's malformed text appended *after* PROJECT frontmatter is merely Markdown body text and is correctly ignored; it is not counted as a frontmatter bypass.

No claim is made that Pi ignored the returned nonzero code during this audit. Ignoring it would violate CONTINUATION; the connected runtime postcondition is not proven by the pure oracle. Existing #26 comments already include parser raw-ref and pending-reservation examples; no duplicate or issue-scope change was made.

### D10 — A / #30: acceptance drift

`harness.py` case `acceptance-drift`: Result/GREEN subject unchanged, Card acceptance changed to require another security gate. Commit `99c6ef25567d1f545afce306c75e833085af7b02`, new clone, router still `post_review_finalization`. Review acceptance has only path/card_id identity, not immutable acceptance content. Distinct from D01, where acceptance does not change.

### D11 — A / #27: terminal proof closure

`harness.py` case `done-without-proof`: M01-T04 done with a path-only missing Result and no review proof. Commit `2ecd6cf99f4c264a59b9fa4b290d3d59d32315c7`; router `route/close`. Fresh native consumer independently reproduced that exact clean commit. DONE validation requires the result table but does not close over Card/Result/Review proof.

### D12 — A / #28: execution Research shadowing

`extra.py` case `manifest-execution-research-shadow`: Board Research complete with return_target `execution_resolution:M01-T04`, both Board/manifest point at the same Research. Production selects Recovery because early manifest map only has intake/brainstorming/definition. Board-only active/complete/consumed controls correctly select Research, execution_resolution and research_cleanup in `boundary-results.json`. Missing/invalid return mapping is not inferred from child chat.

### D13 — A / #29: Close restart equivalence

Fresh route current target-side `implementation/workstreams/feature-common-preexecution-core/WORKSTREAM.toml` at canonical main. Read durable `evidence/M07-close-postmerge-2026-09-23.md` and `handoffs/M07_ADOPTION_SCOPE_COMPLETE.md`; they record approved-scope completion. Actual selector `route/close`, not reconstructible end_of_scope stop. `close_continuation(True, no-next, no-gate)` returns end_of_scope only after the caller supplies the facts. No canonical Close/completion record is selected by the router. Closed PR/issue state alone remains non-authority.

### D14 — A / #31: Plan Review history

`validate_locator` accepts plan_review only at `implementation/workstreams/<id>/PLAN_REVIEW.toml`; validator handles one attempt matching current cycle/revision/subject. The template says append new attempt for changed plan; no durable selected array/history exists. A new material cycle invalidates the singleton old review; replacing it loses selected prior RED, keeping it blocks the new cycle. This is executable storage-contract inspection, not a fabricated live replan mutation.

### D15 — A / #18: invalid terminal review recovery

`extra.py` case invalid-terminal-green sets materially_produced_or_repaired_subject=true on otherwise valid terminal GREEN. Router correctly selects Recovery. `validate_review_history` validates all records, so a later valid attempt does not itself render the invalid historical GREEN consumable. No terminal record was edited to force the live workflow past Recovery. D04 differs: a previously valid terminal record is rewritten and current consumer accepts it.

### D16 — A / #32: Intake relational gap

`extra.py` case empty-issue-alignment, current-schema issue Intake with empty repair_subject and no response -> `stop/issue_alignment`, subject empty. No actual proposed repair exists. Kind checks are independent and do not compare manifest kind with Intake kind; schema inspection confirms that separate existing issue's second reproducer. Do not broaden #23 to encompass this relational defect.

### D17 — A / #33: explicit stop precedence

`extra.py` explicit-stop-with-definition: promoted scope, exact source binding, GREEN Definition/A satisfied, Brainstorm explicit_user_stop=true -> router selects Planning, never checks the explicit stop. Individual schemas accept. This is a variant within #33, not a new premium-handoff or continuation bug.

## Durable writer inventory and machine constraints

| Artifact / transition | Semantic writer/owner | Canonical consumer | Writer machine-constrained by same schema? |
|---|---|---|---|
| PROJECT/WORKSTREAM create, provenance, current locators | project bootstrap / Intake / owner reconciliation | read_project/validate_project/validate_workstream | No normal atomic writer; templates and manual agent writes. Migration is a special fixture-only path. |
| INTAKE diagnosis/prior-art/alignment | Intake | validate_intake + router relations | No mandatory writer API; response/subject fields are assertions; relational gaps D16. |
| BRAINSTORM revision/audit/promotion/stop | Brainstorming | validate_brainstorm + source binding | No writer API; exact scope revision validated on some paths; stop precedence D17. |
| RESEARCH active/complete/applied/consumed + return | Research and exact return owner | validate_research + router | No atomic normal write; return+applied is prose one-transition rule; shadowing D12. |
| requirements/decisions + DEFINITION completeness/A | Definition | validate_definition + source scope checks | No machine writer; locators validate class/path, not acceptance provenance/content. |
| Plan artifact + PLANNING cycle/freeze/A/B/C/editorial exemption | Planning | validate_planning / exact key construction | No writer; draft-only template, no shipped frozen/approved serialization producer. Short/full drift D09; prerequisite gaps D03. |
| PLAN_REVIEW attempt/verdict/evidence | fresh independent Stage-6 reviewer | validate_plan_review + shared validate_review | No writer; singleton locator D14, in_progress dispatch D07; independence proof is declared semantic assertion. |
| Card materialization/refinement + TASK_BOARD revision/status/JIT | Execution Prep, then Main sole active-Card reconciler | parse_task_card/validate_board/refresh_ready_card | No atomic normal writer/CAS; optional expected_revision validator is not transaction enforcement. Active-resume D02 and terminal D11. |
| implementation/evidence contributions | bounded runtime workers | Main acceptance classification | Worker isolation/return validation required by prose, not enforced by a PWv2 Pi adapter in this repo. Workers may not write shared Board/manifest. |
| normalized Result and Board Result locator | Main only | parse_card_result + recovery/router | No writer binding generator; opaque implementation identity D06, missing evidence D05, Git-content resolution D01. |
| implementation Review freeze/verdict/history locators | Main freezes/reconciles; independent reviewer judges subject | validate_review/history + router | No terminal immutability transaction or history-aware consumer; D04/D15. |
| TRACKER discovery/create_pending/readback/final_pr | Intake/GitHub Issues/Close | validate_tracker + external helper | No connected writer/readback adapter; correlation/verified flags are assertions. Dedup and uncertain-readback policy clear. |
| BLOCKER / execution Research handoff | Main/Recovery | validate_blocker + classifier | No writer; class/path checked, no general Git-bound blocker evidence resolution. |
| EXTERNAL_EFFECT pending/verified/observation | exact obligation owner | validate_external_effect/close retry oracle | No universal ledger (correctly prohibited); normal writer not machine-constrained; uncertainty requires readback. |
| CHECKPOINT / handoff / Close completion / cleanup evidence | owning reconciliation/Close | Markdown/navigation + Close helper assertions | Templates only; no selected terminal Close schema D13. Checkpoint must never become second Board. |
| V1 migration output/apply staging | v1_migration/migration_apply | own validation/materialized readback | Special executable producer exists; fixture-only authorized staged apply/readback/crash tests. Not normal lifecycle enforcement. |

The existing CI suite tests contracts/fixtures but does not generally validate selected durable product workstreams or intercept arbitrary agent commits. `validate_board(expected_revision=...)` rejects an already stale observed revision only when supplied. It does not provide compare-and-swap across validation and write. The production router omits that argument because it is a reader/selector, not a transactional writer.

## Parent/child, fresh sessions and runtime-specific boundaries

### Parent -> child

Native creation omitted workspaceId, used caller workspace and verified true parent relationship. Child prompts carried only diagnostic obligation, immutable canonical snapshot and durable fixture locators; children independently loaded recovery/router/modules. No live workflow authority was delegated. This is a successful constrained audit launch, **not proof of a product mechanism preventing arbitrary parent narrative from manufacturing authority**.

Four-field locator receiver rejects extra narrative, missing fields, placeholders, branch/pointer/repository/obligation mismatch and independence failure. Canonical expectations and receiver independence are caller-supplied; no shipped adapter derives them from Git and semantic provenance automatically. #25 remains relevant to actual Premium-B receipt/consumption. The pure helper can consume a handoff yet return again if fresh state remains stop/premium_B; this audit did not claim a newly reproduced real ChatGPT/Pi infinite loop.

### Child -> parent

Main consumed artifact files and independently reran every confirmed child identity finding; all 23 native fresh-consumer outputs and seven resumed-session outputs match exact clean committed Git subjects and fresh reruns. Child notifications/results were treated as runtime completion only. No child response finalized a Board or Review.

### Concurrency

Two independent native audit children ran concurrently with distinct fixture/output spaces, read-only shared canonical tree. No completion-order dependency or shared canonical write was observed.

Synthetic unsafe two-writer barrier test: both readers of revision N can pass expected_revision=N before either writes, then overwrite shared Board content. One-Card validation rejects two visible in_progress Cards, but cannot detect a lost update whose final state has only one Card/result. **This topology violates the canonical sole-Main/shared-writer rule**, so it is an operational non-enforcement risk, not a separately confirmed lawful PWv2 concurrency defect or new issue. A real hostile/two-Main runtime test was not authorized. Result same-path overwrite is separately concretely captured by D01; terminal Review overwrite by D04.

### Runtime dependency map

- Pi/Paseo UI/session identity: not canonical inputs; no consumer branch selects semantic policy based on model/session fields. Prohibited keys are rejected; environment-noise tests pass.
- Child memory/context: not needed for rerun outputs; independently fresh child+process agree. Independence assertions cannot be mechanically established from an LLM's self-report alone.
- Working directory: explicit project_root/package_root was used; native child cwd matches subject, Main reruns from `/tmp` match. Wrong/missing selection fails closed. Caller choosing a wrong but valid project is not prevented by those helper APIs.
- Uncommitted local files: actual inputs. Same Git HEAD with dirty malformed Result changes GREEN selection to Recovery; `identity-extra-results.json` records it. The reader consumes working-tree bytes, not exclusively committed bound objects. Valid-but-changed bytes with old binding are D01's unsafe variant.
- Timing: pure CI classification has no agent-speed branch. Connected waiting/readback scheduling remains runtime responsibility; no timing-safety certification is inferred from unit tests.
- Child finish order: correct when children are isolated and Main rereads; no automatic fencing or immutable fan-in manifest is shipped here. Do not persist runtime orchestration as workflow authority to compensate.

## External CI and progress

At pinned main, exact-head readback found completed/success Actions runs including `36515776317`, headSha `d3ab917f02e4de91b7dbb17915c2287c2387333e`. This is current evidence, not authorization.

Synthetic exact-subject matrix independently exercised:

| Observation | Correct helper result |
|---|---|
| queued / requested / in_progress | pending_observation |
| completed + success | terminal_success |
| completed + failure / cancelled / timed_out | terminal_failure |
| missing run | readback_exact_subject |
| stale/wrong-subject pending or terminal observation | ContinuationContractError |
| completed without conclusion / unsupported neutral conclusion | ContinuationContractError |

The #22 classifier regression is **not reproduced** at this snapshot. Pending observation is distinct from claimed semantic reconciliation: unchanged progress still raises the no-progress fuse; a pending external observation does not itself call it. Cycle identity is ephemeral; restart consumes durable Result when present; uncertain effect readback outranks replay.

Limit: `exact_subject_observed` is a caller-provided boolean (default true); helper has no actual run/head data and cannot itself prove exact subject. `classify_progress` similarly accepts caller fingerprints/epochs. There is no connected Pi/Paseo orchestrator here enforcing every call. This is an assurance/integration gap, not automatic proof of a new CI-classifier defect or reopening #22. Live queued→terminal latency/technical timeout behavior was not exercised by creating CI work.

## Close and recovery tests

Positive helper-level controls: moved target rejects pre-mutation reuse; changed content/behavior/expanded acceptance requires new review; unchanged content requires affected compatibility GREEN; uncertain external effect blocks retry; verified no_effect alone permits replay; expected_effect reconciles without replay; source-ref cleanup requires exact verified head and absence readback in existing suite; deployment status alone is not a stop.

Failures remain D11 (invalid terminal proof can reach Close) and D13 (completed Close lacks router-consumable terminal binding). Exact-head CI, compatibility fingerprints, accepted completion and external readback are supplied by callers rather than a complete bound durable Close record. Restart during merge/publication/closure and externally moving the real target were not induced. No issue was closed and no branch deleted by this audit.

## Lifecycle coverage / assurance limits

| Boundary | Exercised | Outcome / limit |
|---|---|---|
| Intake / alignment / tracker | valid committed records, empty-subject adversary, fresh native consumers | Expected valid routes; D16; tracker remains bookkeeping. |
| Brainstorm / promotion / Definition | exact scope+source checks, fresh resume | Stale source rejects; D17 stop bypass. |
| Premium A / Planning / re-entry | fresh commit clones + native context; stale/short subject controls | Ordinary gates correct; D03 prerequisite bypass, D08/D09 writer drift. |
| Premium B / Plan Review | fresh pending/GREEN/RED/in_progress; strict receive helper | Ordinary routes correct; D07; #25 real receiver-loop not newly run. |
| Premium C / Execution Prep | fresh clones/native; editorial controls; READY refresh suite | Ordinary gate correct; no normal machine writer roundtrip assurance. |
| Card Execution / Result | valid, malformed, missing authority, dirty bytes, opaque subject | D01/D02/D05/D06. |
| independent Review / RED repair / re-review | terminal vs nonterminal coordinate changes, invalid independence, verdict overwrite | Updated terminal coords freeze new attempt; stale pending rejects; D04/D10/D15. No live repair performed. |
| Research / Recovery | Board-owned active/complete/consumed, shadowing, stale input | Expected Board routes; D12; invalid state never relabeled completion. |
| Close / final qualification / exact-head CI | completed package resume, real read-only CI result, refresh/effect helper matrix | D11/D13. No live merge/close/crash injection. |
| child concurrency / completion order | parallel read-only native diagnostics + controlled unsafe writer simulation | Lawful isolation worked in this audit; no hostile write prevention guarantee. |

## Bookkeeping and non-authorization

Relevant open **and closed** issues were fully read back (bodies and all comments) before distinct reports were filed. Each create was one-shot with exact-object readback; no blind retries. New diagnosis-only issues #34–#40 preserve separate invariants and explicitly distinguish adjacent scopes. Existing issues were neither modified nor reopened. No repair plan or new Task Board/workflow state store was created.

The final defect map is therefore **seven distinct confirmed new consumer defects**, plus independently overlapping evidence for existing defects and explicit untested runtime-integration surfaces. It is not a clean certification, and it does not authorize stabilization work.

---

## Appendix: complete distinct-defect reproducer reports

The evidence package preserves these complete diagnosis reports, each with invariant, exact reproducer, durable local Git evidence, lifecycle boundary, runtime specificity, issue relationship and severity:

- `issue-evidence/git-binding.md` — https://github.com/elmakus/project_workflow_v2/issues/34
- `issue-evidence/active-card.md` — https://github.com/elmakus/project_workflow_v2/issues/35
- `issue-evidence/orphan-owner.md` — https://github.com/elmakus/project_workflow_v2/issues/36
- `issue-evidence/terminal-overwrite.md` — https://github.com/elmakus/project_workflow_v2/issues/37
- `issue-evidence/missing-evidence.md` — https://github.com/elmakus/project_workflow_v2/issues/38
- `issue-evidence/opaque-subject.md` — https://github.com/elmakus/project_workflow_v2/issues/39
- `issue-evidence/plan-review-in-progress.md` — https://github.com/elmakus/project_workflow_v2/issues/40

`github-bookkeeping-evidence.json` records positive exact-object readbacks and body hashes. `bundle-index.json` identifies local synthetic histories preserved in Git bundles. None of these diagnostic files is workflow authority, a Task Board, an approval, or a repair authorization.
