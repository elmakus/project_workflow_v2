# PWV2-STAB-P1 — dependency-aware stabilization program proposal

Status: program-level diagnosis/planning ONLY. Not accepted Definition, not a frozen Master Plan, not an implementation authorization, and not a Task Board. No product/code/workstream/issue changes were performed.

## 1. Reconciled baseline and provenance

Canonical product authority is `elmakus/project_workflow_v2` default `main@d3ab917f02e4de91b7dbb17915c2287c2387333e`, reread during this task. Non-default code and issue text are evidence, not replacement policy.

Evidence reconciled:
- Independent Pi/Paseo audit: local evidence commit `6f1a047c912898281a645594b8518140172a8682`, REPORT.md, 72 primary observations, 23 fresh native consumptions and seven resumed-session consumptions. Its 271-test suite pass did not certify runtime integration.
- Independent ChatGPT adversarial audit: `research/pwv2-adversarial-stabilization-bug-hunt@95d74bad11115419696a684c8eef11fda076f92f`, `implementation/workstreams/change-adversarial-stabilization-bug-hunt/evidence/ADVERSARIAL_STABILIZATION_AUDIT_2026-09-29.md`. This is the committed report corresponding to #27–#33; it independently overlaps the Pi evidence. Its Brainstorm record is active, promotion pending, explicit_user_stop=true. Research completion is NOT promotion/repair authorization.
- All 26 currently listed open/closed issues, their bodies, metadata and both comments were read back, including #23 and #25–#40, plus #11/#14/#16/#17/#18/#20/#22 and excluded historical #13/#15.
- #24 is a MERGED PR, not a distinct defect issue. It integrated #22 at the canonical snapshot. Prior merged PRs #12/#19/#21 cover #11/#16/#17 and remain regression baselines. PR #10's co-bound Board precedence is also a regression baseline.
- Open PR #9 is a separate PWv2.1 policy-kernel candidate; its body says not to merge before its own gates. This proposal does not adopt, merge, or import its semantics.
- Existing #23 branch: `work/pwv2-durable-state-schema@b076e081fb91815ff570fb70566e71f8cc53154e`. Read its requirements, decisions, plan and Board. Its M01-T01 is in_progress with a Result and a frozen R01; it is not assumed GREEN/qualified. Existing work must be reconciled/reviewed, not reimplemented or overwritten.
- Existing #20 branch: `work/pwv2-paseo-child-delegation@c5e9ba1d3da8d339e882b43b86b4e8a8dd2e9a28`. Read its declared Definition/Brainstorm scope and plan: official caller-scoped create_agent readiness only; no alternate daemon/shell spawner or final PWv2.2 helper. P2 declares C due. This describes its scope boundary, not a claim every current record validates or permission to continue it here.

No issues were closed, merged, reopened, relabeled, edited, or newly created in this planning task. The two audits remain distinct provenance chains.

## 2. Scope and authority controls

Proposed outcome: trustworthy durable-state production and consumption, immutable proof/history, deterministic authorized routing and restart, and reconstructible Close across the intended lifecycle.

Recommended core defect set: #23, #25–#40, #18, and #14. #20 is a narrow runtime-readiness dependency/side track, not an excuse to build a spawner. Closed #11/#16/#17/#22 are mandatory regression baselines, not automatically reopened repair subjects.

Explicit exclusions: adopting PR #9; PWv2.1/PWv2.2 feature expansion; changing approved consumer product scope; mass migration of other repositories; live deployment/credential/runtime administration; alternate child spawning; rewriting historical Results/Reviews/approvals; deleting provenance; fabricating GREEN; and closing/merging issues by similarity. Inclusion of deferred #14 in a new stabilization scope requires explicit approval; it does not lift the deferral inside an existing PWv2.2.0 consumer program.

The program proposal is deliberately separate from existing accepted repair subjects. No existing A/B/C satisfaction or approval is transferred to this larger scope. Any change to an existing workstream's approved strategy or repair subject must go through that workstream's owning Intake/Planning/Definition rules, including renewed subject-bound gates when required.

## 3. Root-cause and repair-boundary reconciliation

Use three distinct relations: (a) observed mechanism; (b) reusable repair boundary; (c) scope subsumption. Sharing (b) does not establish (a) or permit tracker closure.

| Family | Issues | What is established | Repair relation and separation |
|---|---|---|---|
| Structural production/serialization parity | #23; serialization portions of #26 | Default main has validators but no ordinary mandatory validated producer boundary. Both malformed shape and short-key/raw-ref serialization are evidenced. Which actor omitted/ignored validation is not proved. | One producer/consumer schema boundary is appropriate. #23's actual requirements already cover current-schema validation of ordinary writes. #26's serialization counterexamples can qualify that boundary without changing #23's subject. |
| Exact content/acceptance/proof identity | #34/#39/#38/#30 | #34 compares coordinate strings without resolving consumed Git bytes; #39 accepts arbitrary implementation-subject text; #38 does not resolve proof references; #30 acceptance is mutable or unrelated. | Shared exact-object/locator resolution and binding machinery; separate artifact roles and acceptance predicates. Fixing only SHA format, file existence, or reviewed Result equality is insufficient. |
| History and lawful replacement | #37/#31/#18; pending-reservation evidence in #26 | Terminal implementation verdict overwrites are unchecked; Stage-6 stores one selected attempt; invalid terminal history has no lawful supersession; pending stale reservations have no cancellation/replacement law. | Shared transition/history principles, NOT one schema/lifecycle. Stage-6 preserves A/B/C and the planner/reviewer separation. Invalid terminal and unstarted pending attempts need different legal dispositions. |
| Structural relations / stop precedence | #32/#33/#36 | Missing cross-record constraints and early next-stage returns bypass actual owner/gate conditions. | Small fail-closed admission/precedence guards can land before deeper identity/history work. They are not schema-producer parity fixes. |
| State-appropriate consumer closure / dispatch | #35/#27/#28/#40 | Active no-Result Card lacks refresh; DONE skips proof; Research owner map shadows a supported return; in_progress Plan Review falls into RED default. | Shared explicit route predicates but distinct branches/owners. #35/#27 depend on trustworthy proof/authority/history. #28/#40 are local routing defects and can be independently researched/tested early. |
| Handoff/runtime continuation | #25/#20; regression #11/#16/#17/#22 | Receiver oracle requires caller-derived expectations and a real durable post-receipt transition. Current CI classifier passes the status matrix, but connected runtime enforcement is not established. | Separate semantic handoff consumption from runtime capability injection and CI observation scheduling. No model/session identity becomes approval. |
| Strategic gate legality | #14 | Execution-only DAG can hide a cycle in the execution + acceptance-consumption graph. | Separate semantic planning defect; no serializer, history list or dispatcher change alone fixes it. |
| Terminal durable reconstruction | #29, using #27 and prior layers | No selected machine-bound completion proof reconstructs end-of-scope from completed target-side state. | Separate Close owner state/consumption boundary. Rejecting bad DONE is prerequisite, not a substitute for #29. |

### Scope subsumption decisions

1. #23 ALREADY subsumes machine-constrained structural producers, validation-before-success, and explicitly supported structural V2 reconciliation. Its current accepted requirements/decisions expressly exclude unrelated premium, review, orchestration and product-semantic changes.
2. Therefore #26's short B/C serialization, malformed TOML, wrong status and raw-ref producer cases overlap #23's accepted structural parity criteria. Keep #26 evidence and its original tracker; do NOT declare the entire issue a duplicate.
3. #26's pending-reservation replacement problem is NOT subsumed by #23's structural mapping authority, #18's invalid-terminal-GREEN subject, or #37's valid-terminal immutability defect. Preserve it as separately named acceptance within #26 unless a later explicit scope/dedup decision changes its bookkeeping.
4. #34/#38/#39/#30 share infrastructure but no issue fully subsumes the others. Distinguish implementation commit/tree, normalized Result blob, Review subject, Card/Definition acceptance, and evidence closure.
5. #18/#31/#37 are not duplicates: invalid historical attempts, missing Stage-6 storage, and valid terminal overwrite respectively.
6. #27 does not subsume #29; #23 does not subsume current-schema-valid relational/dispatch defects #32/#36/#40; #17 does not subsume #25's eligible receiver looping; #20's title/body do not supersede its narrower durable scope.
7. Do not treat withdrawn #15 as regression evidence. #13 is superseded bookkeeping history, not stabilization work.

## 4. Dependency model and safest integration order

Recommended capability checkpoints:

`W0 admission -> W1 structural integrity/early safety -> W2 exact identity/proof -> W3 lawful history/replacement -> W4 complete routing/strategic legality -> W5 Recovery/receipt/runtime integration -> W6 Close reconstruction -> W7 independent end-to-end acceptance`

Hard dependencies:
- Writer serialization must use the executable contract; consumer admission must also reject raw-write bypasses. A writer helper alone cannot make incomplete validators semantically sufficient.
- Subject/acceptance/evidence resolution must precede credible GREEN reuse, supersession or supported identity-changing recovery.
- Lawful pending/invalid-history replacement must precede applying normalization that changes a subject already bound to an attempt. No rebinding R01 or fabricated verdict to unblock a migration.
- DONE proof closure requires exact Result, acceptance, history and required evidence; Close requires that terminal closure plus a separate reconstructible completion record.
- Handoff receipt must derive from valid current owner/identity/history; runtime integration must then enforce durable consume/reroute, not trust child/UI completion.

Not hard dependencies:
- #33's explicit-stop preservation and #32/#36's structural owner guards do not need a new history model. They are intentionally early safety work in W1.
- #28 and #40's focused owner/enum handling can be independently analyzed and prepared early; W4 is the preferred shared-router integration checkpoint, not proof they logically depend on every identity defect.
- #14's legality analysis is independently researchable at W0. Its positive-path integration is safer after immutable acceptance/history are settled.
- #20 readiness checks may run independently when legally authorized. They do not justify changing the product's semantic layers.

Wave boundaries are program capability/qualification checkpoints, NOT instructions to reorder #23's already-approved Cards, launch concurrent shared writers, merge partial issue scopes, or declare a role stop. If a program dependency requires changing an existing approved strategy, request an explicit owning-Planning replan first. Existing #23 producer work can supply a reviewed prerequisite Result; later program checkpoints qualify it with stronger layers without rewriting its original authorization.

Downstream execution may consume a predecessor's independently GREEN **constituent result** when explicitly sufficient for bounded work; do not make that consumption depend on a final composed review that itself needs the downstream work. Apply #14's combined-gate DAG check to this stabilization program itself. Final program acceptance remains a later, separate gate.

## 5. Repair waves (all proposed, none authorized by this document)

### W0 — Program admission, evidence lock and Definition decisions

Entry: this proposal plus both immutable audit reports and fresh issue readbacks; no implementation permission inferred.

Work/outcomes:
- Dedicated new stabilization scope, or another explicitly selected legal ownership arrangement; do not silently resume/expand either diagnosis-only audit workstream.
- Preserve each issue ID, exact reproducer, audit provenance, candidate branch and accepted-subject boundary; separate active selected state, supported historical state and unselected archival material.
- Freeze decisions for canonical committed authority vs dirty local input; object publication sequencing; actual schema/record compatibility support; Stage-6 verdict states; pending cancellation vs invalid-terminal supersession; minimal Close ownership; and program integration scope. Preferred defaults: consume explicitly bound immutable Git bytes (never a mixed mutable/historical subject); Stage-6 keeps canonical pending/GREEN/RED and rejects in_progress unless separately authorized; preserve invalid old records with an exact-bound invalidity/successor disposition; define cancellation of an unstarted pending reservation separately; minimal Close-owned completion proof rather than a universal event-log redesign.
- Define each transition's acceptance as required shape + required relational bindings + object/proof closure + permitted before/after transition, not merely TOML parse success.
- Resolve #25's outstanding formal Research requirement before its repair authorization: its issue requests one whole-scope lane, one independent red-team lane and at least eight targeted lanes under the referenced project-research protocol. Existing audits do not demonstrate completion of that exercise. Validate canonical ownership and explicitly adopt/reconcile this research gate; do not mark it satisfied by a summary.
- Independent review of the program's combined execution/acceptance DAG; no circular Card DONE/composed-review prerequisite.

Exit: accepted bounded Definition/decisions, preserved authority boundaries, required Research reconciled, GREEN Definition; then real premium A, exact frozen Planning, fresh independent premium-B Plan Review and C as applicable. This informal program is NOT those records. Any unknown choice or failed independence is a real stop, not coding permission.

Qualification: frozen counterexamples and positive controls for every tracked invariant; current failing/passing expectations reproduced, actual producer tests distinguished from handcrafted fixtures; exact audit/branch identities recorded.

### W1 — Structural producer/consumer integrity and early fail-closed safety

Issues: #23 producer/write boundary; #26 serialization portions; #32/#33/#36 independently bounded admission guards.

Entry: approved exact W1 subjects/Cards, W0 decisions and tests; reconcile the existing #23 M01 Result/R01 instead of replacing it.

Required outcome:
- One executable schema authority and mandatory normal producer construction/render/validate/readback boundary for every concrete lifecycle writer. Templates/docs reference it, not another schema.
- A producer is not reconciled successfully merely because it wrote bytes; candidate output passes applicable current validators and required relationships before accepted publication.
- Reader/continuation-side validation blocks a raw-edit/commit bypass. Invalid TOML/partial writes yield deterministic failure/Recovery with no downstream success or forged normal stop.
- Coupled records cannot expose an accepted mixed old/new state; stale expected revisions/heads are rejected at acceptance. Runtime filesystem isolation/transaction realization stays outside workflow identity.
- Empty Intake repair remains diagnosis; manifest/Intake intent agrees; materialized owner prerequisites cannot be silently ignored; explicit user stop cannot be bypassed into Definition/Planning.

Exit: valid producer -> committed accepted transition -> fresh consumer round trips across record kinds; malformed writes and contradictory owner/stop cases never continue downstream. This establishes structural safety, NOT proof that existing semantic validators are complete or that #23's full migration scope is finished.

Qualification: short/full A/B/C keys; raw vs backticked/trailing-period refs; literal backslash-n; wrong fields/types/enums; missing locators; truncated and mixed writes; stale source; direct raw-write bypass; crash before/after publication; sole-Main writer and isolated child contribution tests. Explicitly distinguish rejection before authority mutation from cleanup of unaccepted temporary files.

### W2 — Exact immutable Git identity and evidence/acceptance closure

Issues: #34/#39/#38/#30.

Entry: W1 producer/reader integrity; accepted identity-role decisions. No free-text summary or boolean alone is an exact subject.

Required outcome:
- Verify repository, exact commit, path and blob resolve consistently; consume the bytes identified by those coordinates.
- Distinguish implementation subject from normalized Result subject, Review subject and immutable Card/Definition acceptance surface.
- Bind Review acceptance to the actual accepted owner surface, not any path under an allowed directory.
- Resolve required evidence in the subject's declared durable context; missing/unretrievable/wrong-subject proof cannot qualify a transition. Existence alone does not establish semantic test success.
- Changed current bytes must never be parsed together with an old approval. Either reject the mismatch or deliberately consume/verify the exact still-selected immutable historical subject under an explicit contract.
- Publish identities without self-referential commits: implementation first, Result publication next, Review freeze after its exact subject exists; same discipline for Plan and later Close identities.

Exit: no unproven Git identity, unrelated acceptance, or unresolved evidence can satisfy Result acceptance or GREEN reuse; verified historical objects can resume without needing old local files/session memory.

Qualification: nonexistent full SHAs, short SHAs, path/blob mismatch, wrong repository, stale subject, same-path edits, dirty worktree, missing object retrieval, unrelated authority, changed tests/acceptance, forged evidence summary. Include valid old objects available only via Git history. Original #34/#38 cases must test WHICH bytes/proof are consumed, not blindly require Recovery if the bound historical proof really is available. Add a truly nonexistent proof-at-bound-subject case. This avoids converting durable historical evidence into a false missing-file failure.

### W3 — Append-only Result/Review history and lawful replacement

Issues: #37/#31/#18; #26 pending-reservation gap. #23 identity-changing reconciliation depends on these laws when a subject-bound attempt exists.

Entry: W2 exact identity/proof; W1 validated publication; accepted semantic lifecycle changes.

Required outcome:
- Terminal implementation attempts cannot be overwritten or rebound. Repair publishes a new exact Result subject/version; existing terminal Review retains its original subject/acceptance/evidence.
- Stage-6 has durable reachable attempt history across material cycles without conflating its A/B/C premium semantics with ordinary implementation Review.
- Preserve invalid historical raw records/evidence; separately identify their invalidity and lawful successor so they never authorize downstream work. Do not demand an invalid historical record become valid by rewriting it.
- Define a narrowly lawful disposition for unstarted/stale pending reservations and replacement; preserve the old reservation and prevent it from later verdicting the new subject. Do not invent GREEN/RED, silently rebind R01, or leave two active attempts.
- No old approval transfers to a changed immutable subject absent an existing applicable exemption. Independence is recomputed for every repaired subject.

Exit: RED -> repair -> new Result -> fresh independent review; valid-terminal immutability; invalid-terminal recovery; pending reservation replacement; material Plan re-entry all survive fresh resume with immutable history and one effective current obligation.

Qualification: terminal verdict/evidence/subject overwrite attempts; Result edits after R01; late stale verdicts; duplicate IDs; conflicting successors; multiple active attempts; invalid GREEN and RED; metadata/prose disagreement; pending-not-started vs started review; crash between replacement publication and selection; same model/new context does not itself prove independence; repairing actor never independently approves its own repaired subject.

### W4 — Complete consumer closure, owner dispatch and strategic gate legality

Issues: #35/#27/#28/#40; #14; cumulative #32/#33/#36 regression.

Entry: W2/W3 predicates available for active and terminal consumption; W1 guards qualified.

Required outcome:
- Active no-Result resume refreshes stable Card/authority/dependencies; started Card cannot be silently refined in place.
- Every DONE claim reconstructs exact Result, current acceptance, required GREEN Review and evidence before Close/dependency/JIT consumption. Do not simply demote DONE or replay implementation when durable evidence proves completion.
- Research returns once to its exact owner, whether reached through manifest or Board; applied/consumed return never replays.
- Stage-6-specific verdict validation keeps canonical pending/GREEN/RED; in_progress fails closed under the recommended scope rather than silently extending Stage-6 or defaulting it to RED. Any future support for that state needs its own accepted semantic contract.
- Planning audit/independent Plan Review compose implementation dependencies, result-consumption rights and acceptance/composed-review gates into a cycle check; distinguish constituent acceptance from final composed acceptance.
- Keep progressive disclosure: validate the selected obligation's required closure and declared prerequisite consistency, not every archival file in the repository.

Exit: one deterministic owner or legitimate fail-closed/stop disposition for every lifecycle state; valid workflows remain live; no illegal terminality or strategic acceptance cycle is admitted.

Qualification: decision table across Card statuses/results/review states, multi-READY selection, blocked Research, all Research returns/cleanup, every Stage-6 verdict, explicit stop plus later-stage records, orphan owners, stale dependencies, technical-contract absent/present, rejected execution+acceptance cycles and valid composed-review plans. Existing co-bound Board precedence from PR #10 must remain correct.

### W5 — Recovery/reconciliation, handoff consumption and connected runtime continuation

Issues: #23 full structural reconciliation qualification; #25; #20 narrow runtime side track; regression baselines #11/#16/#17/#22.

Entry: W1–W4; required #25 Research resolved; only explicitly supported structural profiles and legally authorized runtime-readiness changes.

Required outcome:
- Known structural mappings are deterministic/idempotent; ambiguous/corrupt source or unprovable authority stays Recovery. Preserve historical source artifacts and accepted scope. Apply only exact expected-before/already-after states; reject unrelated divergence.
- Subject-preserving mappings retain only eligible exact approvals. Subject-changing normalization uses W3's lawful reset/replacement path before any application; no parser-compatibility workaround mutates frozen identity.
- Eligible fresh A/B/C/Review handoff receiver derives expectations from durable owner state and consumes only the transferable boundary. Receipt never authorizes missing human/product choices; planner cannot spawn its own Stage-6 reviewer.
- Parent delegates bounded immutable locators; child rerecovers authority; parent validates durable contribution and rereads/reroutes. Child end-of-turn/verdict is not parent workflow completion.
- Runtime invocation enforces non-stop continuation and real stop delivery, not just calling a helper optionally.
- CI observation is bound to the actual implementation/head/run tuple. Pending observation remains separate from successful-reconciliation no-progress, and technical observation timeout is not success or semantic stop. Uncertain writes require readback before retry.
- #20 stays official native capability injection/readiness/fail-closed diagnostics; no fallback spawn and no workflow worker/model/session authority.

Exit: actual producer/consumer resume and handoff traces continue to the next genuine stop, with no redundant confirmation, repeated eligible B handoff, replayed durable result/effect, or completion-order dependency. Full #23 scope is qualified here, not declared fixed by its early writer capability alone.

Qualification: new session at every important lifecycle boundary; consumed locator replay and wrong/stale locator; independence failure; RED/repair/re-review; loss of child/parent runtime context; result/effect committed but notification missing; existing malformed #22/#20 source profiles; normalization after pending R01; repeated recovery apply and mid-apply interruption; native capability missing; concurrent isolated contributions with reversed finish order; prohibited shared-authority mutation; two stale coordinators competing for acceptance; CI queued/requested/in_progress/success/failure/cancelled/timed_out/missing/stale runs under fast and slow scheduling.

Runtime adapter gaps discovered here are separately owned and must be explicitly scoped. Do not import the final PWv2.2 helper or a second workflow queue merely to make tests pass.

### W6 — Reconstructible Close and exact-subject external finalization

Issue: #29; depends on #27 and W1–W5.

Entry: qualified terminal Cards/approved-scope coverage, current target, exact reviewed head/acceptance and external-effect safety.

Required outcome:
- Minimal Close-owned durable proof reconstructs in-progress Close, accepted completion and end-of-scope from target-side state and immutable integration evidence; booleans supplied by a conversational caller are not proof.
- Distinguish reviewed source head, refreshed target, PR head/check subject, merge commit/tree and post-merge reconciliation subject. Target movement or material coverage change requires refresh/requalification; no stale CI is inherited by a newer subject.
- Premerge package includes all uniquely knowable recovery artifacts. Source-branch deletion cannot destroy recovery or provoke recreation.
- Tracker closure follows durable scope completion/readback; early issue closure never grants approval. Unknown external outcomes never permit blind retries.
- Completion requires no remaining authorized in-scope obligation, not merely an empty Card list. Close substeps do not become synthetic stops.

Exit: fresh resume before/after integration, source deletion, tracker change and completed Close reconstructs the correct same semantic obligation or real end-of-scope stop.

Qualification: missing/invalid terminal package; target moves after refresh; same content vs changed behavior/acceptance; exact-head CI becomes stale; interruption before/after merge and before/after readback; unexpected early issue close; expected automatic closure missing; cleanup head moves; source already absent; terminal-unmerged history preservation. Use explicitly authorized disposable repositories/external objects, never live product mutations by default.

### W7 — Independent final adversarial qualification

Entry: all wave results independently GREEN; complete issue-to-invariant coverage; supported compatibility profiles and intended runtime envelope declared; no unresolved high-risk invariant silently waived.

Exit: the final gate below passes for the EXACT release/integration candidate and the resulting integrated subject. Any material change resets affected coverage; speed/session/order changes do not change legal transitions.

## 6. Qualification after EVERY repair wave

1. Reproduce each wave's frozen original counterexample, positive control and cross-layer mutations through the actual repaired entrypoint/producer, not fixture helpers alone.
2. Run the cumulative production contract suite and prior-wave adversarial cases. Prior 271-test success is a baseline, not acceptance.
3. Commit -> clean clone/worktree -> fresh canonical consumer. Verify exact objects and consumed bytes; compare the canonical semantic route/owner and external effects, not timestamps or runtime IDs.
4. Check supported historic active state separately from unselected archival records. No bulk rewriting of history to obtain a green scan.
5. Inject failure at publication/acceptance boundaries and verify restart/idempotency. No downstream mutation after invalid state; no lost accepted update, partial effective authority or duplicate effect.
6. Independent exact-subject review by a context that did not execute or repair the subject; retain all verdicts/evidence immutably. Stage-6's fresh premium boundary remains distinct.
7. Record qualification locators in canonical owning records ONLY once this program is authorized/materialized. This proposal/issue map is not a second Task Board.
8. Refresh target and rerun affected integration qualification before any authorized merge. Wave acceptance does not automatically close a tracker or merge an intermediate branch. Intermediate PRs use reference-only linkage.

## 7. Final end-to-end stability gate

### Mandatory lifecycle scenarios
- Valid new issue, feature and change: Intake/prior-art/alignment where required -> Brainstorm/promotion -> Definition -> A -> Planning -> B independent review -> C -> Execution Prep -> execution -> Result -> independent Review -> finalization -> Close -> fresh completed resume.
- RED implementation -> bounded repair/new Result/new review; invalid terminal attempt -> lawful supersession; malformed Result under pending R01 -> lawful reservation replacement; material plan RED -> new cycle A/B/C with retained history; bounded editorial exemption without inappropriate approval transfer.
- Composed-review planning including #14's illegal cycle and lawful constituent-input/final-acceptance distinction.
- Current fresh producers AND each explicitly supported legacy-shaped active V2 profile; changed/unprovable identity never inherits authorization.

### Runtime and adversarial matrix
At every meaningful boundary, vary fresh vs resumed context, parent/child disappearance, notification absence, wrong cwd, dirty local files, malformed TOML/literal backslash-n, partial state, wrong fields/enums/locators, short/nonexistent/stale subjects, changed acceptance, stale attempts, proof unavailable, independent/non-independent context, and child finish order. For adversarial state, prove no unauthorized downstream transition; for valid state, prove eventual intended next obligation/real stop.

Use controlled schedule traces for sole Main + isolated workers, and negative competing-writer/stale-coordinator races. Either one accepted lawful transition wins or all conflicting attempts fail closed; no silent last-writer-wins authority, double active attempt or double external effect.

Exercise actual connected pending external evidence and fault injection in disposable authorized infrastructure, including queued/requested/in_progress/completed-success/completed-failure/cancelled/timed_out/missing/stale runs. Identical durable input and exact external observations must produce identical semantic decisions independent of agent speed. Pending waits are not unchanged-success loops; technical aborts leave a resumable obligation.

Fresh Pi/Paseo native execution is mandatory; runtime-neutral and applicable ChatGPT entry/delivery/recovery contracts plus the independently supplied ChatGPT evidence remain in the cross-harness matrix. A genuine external ChatGPT lifecycle observation must be obtained through an allowed external harness if cross-harness runtime certification is claimed; absent evidence is BLOCKED, not silently simulated or claimed from Markdown tests. All real-LLM tests initiated in this environment must use the guarded Muse Spark contributor/max profile with no fallback; Main's model stays user-selected.

### Exact-subject release acceptance
- Full cumulative suite + actual producer round trips + all open-issue reproductions + closed regression baselines + wave integration tests GREEN on the exact candidate.
- Fresh independent whole-program adversarial review against a frozen candidate, not recycled executor/repair reviewer; semantic independence, immutable subject and acceptance proof checked.
- All current required Card/Plan Review/CI gates satisfied for exact subjects; no unexplained skipped/xfail invariant, unresolved unsafe pending state or unqualified environment declared stable.
- Exact-head CI and target compatibility refreshed before integration; target movement invalidates stale qualification.
- After an authorized integration, read back merge identity/tree, target-side recovery, exact integrated-subject qualification, required tracker state and fresh Close/end-of-scope reconstruction. Post-merge failure means NOT stable.
- Report the qualified runtime/compatibility envelope and outstanding non-core limitations explicitly. A safe abort alone is not evidence that a valid workflow can complete.

## 8. Implementation-authorization stop and exact next user action

This task stops with the program PROPOSED. No wave is implementation-authorized; no issue relationship is a closing verdict.

Next required authorization is acceptance of the bounded stabilization scope and permission to materialize its managed Intake/Research/Brainstorming/Definition preparation. This allows the proposal to become an exact durable scope subject; it does not retroactively promote either stopped audit workstream or bless existing branch code.

Suggested user instruction:

> I approve PWV2-STAB-P1 as the bounded stabilization repair-scope proposal. Authorize a dedicated managed workstream to formalize this scope through Intake/prior-art reconciliation, Brainstorming and Definition preparation. Preserve the existing #23 and #20 repair boundaries and all issue/audit provenance. No implementation, consumer migration, issue closure, merge, PR #9 adoption or live deployment is authorized. Return at the next canonical user/premium gate and stop before the first implementation authorization.

Exact Brainstorm promotion must still bind the durable scope_id@revision once materialized; this document's proposal ID is not that record. GREEN Definition then requires premium A; material Planning freezes an exact subject; B requires fresh independent Plan Review; GREEN consumption/C must precede Execution Prep. First implementation permission must name the exact accepted W1 subject/Card(s) after those prerequisites—not 'fix all related issues'. Existing separately authorized workstreams do not gain an expanded subject from this program map.
