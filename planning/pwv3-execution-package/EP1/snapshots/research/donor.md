# PWV3 donor strategy — FINAL_SYNTHESIS

Status: FINAL RESEARCH SYNTHESIS
Analysis subject: workflow-successor-product@2-v2-donor-strategy
Claim generation: 2
Frozen research base: 3763737f8d50809041b69d563766b2a0be7ca230
Integration branch: research/pwv3-donor-strategy-integration-g2
Consumer repository: elmakus/project_workflow_v2
Consumer branch: work/workflow-successor-product
Current consumer head reconciled at integration: 690d5350b436b1472fa8b647f018a34b3a67bb9d
Implementation repository: elmakus/pwv3
Implementation repository state for this Research wave: empty_at_launch

This synthesis is Research evidence only. It does not authorize Planning or implementation and does not mutate either product repository.

## 0. Integration basis and generation validation

Current LANES.toml declares generation 2 with 16 finite lanes, one frozen research base, and integration branch research/pwv3-donor-strategy-integration-g2.

All 16 declared finite lanes were validated before synthesis:

- W00, R00, L01-L11 and L14 use the declared generation-preserved branches.
- L12 uses research/pwv3-donor-strategy-L12-chatgpt-g2.
- L13 uses research/pwv3-donor-strategy-L13-coupling-risk-g2.
- Every accepted branch is ahead of the frozen base, behind_by = 0, and has merge-base exactly 3763737f8d50809041b69d563766b2a0be7ca230.
- Every declared output exists at its exact LANES.toml path.

The overflow allocator is at 103, so the valid supplemental runs are R100, R101 and R102. All three were validated against the same frozen base and their exact overflow/Rxxx/FINDINGS.md output paths were consumed.

No result from the historical partial integration branch, old generation-1 reclaimed L12/L13 branches, or undeclared alternate lane branches is treated as current-generation authority.

### Consumer/donor drift reconciliation

Most finite lanes inspected consumer head 9105b707f67e28376cb761414bc5d682ba6d4952. L12/L13 later inspected 97cc440193c68c4965f15c15b8e489af00b91fd7. Integration reconciled once against current consumer head 690d5350b436b1472fa8b647f018a34b3a67bb9d.

The comparison from 9105b707... to 690d535... is five commits ahead and changes only three successor-workstream evidence files:

- PWV3_ADDITIONAL_RESEARCH_WAVES_2026-09-30.md
- PWV3_ASSURANCE_OWNER_DECISION_2026-09-30.md
- PWV3_ASSURANCE_PROFILE_OWNER_DECISIONS_2026-09-30.md

No donor source or donor test changed in that drift window. Therefore the source-level donor findings remain current, while the owner-fixed assurance semantics below must modify how some otherwise-generic review/handoff donors are classified.

## 1. What clean rewrite means concretely

Clean rewrite does not mean zero reuse. It means clean semantic, authority, state and compatibility lineage.

PWV3 may reuse proven algorithms, failure cases and small source fragments from PWV2/V2.2 only after the surviving behavior is independently stated as a PWV3 invariant. After extraction, PWV3 owns the implementation. Normal PWV3 build, test, bootstrap, routing, validation, Review, Recovery, Close and release behavior must work with elmakus/project_workflow_v2 unavailable.

Clean rewrite therefore requires all of the following:

1. New PWV3-native checkpoint and artifact contracts rather than renamed V2 WORKSTREAM/TASK_BOARD/phase records.
2. No native V1/V2/V2.2 compatibility reader in ordinary PWV3 runtime.
3. No runtime/build dependency on the donor repository, old construction repository, old plugin namespace or a shared V2/V3 semantic library.
4. Exact immutable Git/GitHub identity and positive readback remain first-class because those are enduring invariants, not V2-specific representation.
5. Historical regression evidence is preserved more aggressively than implementation.
6. Runtime/provider/model/session/worker identity remains capability metadata, never semantic authority.
7. Project Card execution remains sequential with exactly one active Card.
8. Optional assurance orchestration does not become a second scheduler or resurrect V2.2 parallel admission/fan-in.
9. Per-artifact contract evolution replaces the V2.2 global epoch/generation model.
10. A copied primitive can carry provenance about V2, but never authority from V2.

The practical shorthand is:

semantic transplant, not subsystem transplant.

## 2. Donor-policy constitution

The following rules are normative for later Definition/Planning donor decisions.

### D1 — Surviving invariant first

No source is reusable merely because it is small, stable, green-tested or old. First identify the PWV3 invariant it serves. If the capability is absent from PWV3, DROP or REFERENCE_ONLY applies.

### D2 — Four-axis purity

A COPY/PORT candidate must pass all four:

- dependency purity: no rejected donor imports;
- vocabulary purity: no hidden V2 lifecycle/stop/action/type names becoming PWV3 API accidentally;
- layout purity: no V2 path/file/serialization topology becoming compatibility law;
- authority purity: the function does not encode an obsolete V2 semantic-owner decision.

### D3 — Smallest stable responsibility

Split mixed modules. Reuse a leaf algorithm if safe; do not copy its architecture-owning parent module.

### D4 — Runtime/language translation is a port

If PWV3 uses the currently preferred plain ESM/Node helper, translating Python donor logic is PORT_WITH_SMALL_ADAPTATION or REIMPLEMENT_FROM_CONTRACT, never COPY_AS_IS.

### D5 — Exact identity is verified, not formatted

Repository + commit + path + blob strings are not authoritative merely because they are well formed. Exact identity requires actual object/readback verification where correctness depends on identity.

### D6 — Derived hashes are never authority

Canonical hashes/material fingerprints may optimize impact/cache decisions but cannot replace the exact underlying identities.

### D7 — Remote mutation is fenced and read back

Expected-old/freshness checks plus positive authoritative readback are mandatory. A process exit, API success response or local state is not semantic publication proof.

### D8 — UNKNOWN fails closed

Unknown version, impact, external-effect occurrence, ambiguous Issue match, missing capability or untrusted health query cannot be converted to success.

### D9 — Evidence may outlive implementation

Tests, fixtures and historical defect scenarios may be retained even when their original implementation is DROP.

### D10 — No compatibility-by-convenience

Do not retain Task Board, Premium, global epoch, migration readers, V2 path grammar or old type tags because copied code happens to expect them.

### D11 — One-way ownership

After extraction PWV3 owns copied/ported code independently. Donor provenance is documentation, not a synchronization or dependency mechanism.

### D12 — Current owner drift overrides generic donor convenience

At an OP-selected boundary, ChatGPT-only orchestration is owner-fixed. A donor helper that would otherwise permit local/internal independent realization cannot override that product requirement.

## 3. Module and file-family disposition map

| Donor surface | Primary disposition | Integrated rationale |
|---|---|---|
| prompts/CHATGPT_FRESH_SESSION.md | COPY_AS_IS, narrowly | Four-field locator-only text has no semantic verdict or V2 lifecycle policy. It remains untrusted bootstrap data and may be copied literally only while the same four-field boundary contract is retained. |
| tools/pwv22_native_foundation.py::canonical_json | PORT_WITH_SMALL_ADAPTATION | Preserve deterministic canonical bytes, but freeze a PWV3 cross-runtime encoding contract and golden vectors. |
| tools/pwv22_native_foundation.py::safe_path | PORT_WITH_SMALL_ADAPTATION | Strong generic POSIX-relative path safety; detach from Python error types and define PWV3 path grammar. |
| material_fingerprint | PORT_WITH_SMALL_ADAPTATION | Useful only as derived, non-authoritative material metadata. |
| guarded_publish | PORT_WITH_SMALL_ADAPTATION | Generic expected-old -> one mutation -> positive readback skeleton survives. Adapter must provide the real fence. |
| remote_ref_head | PORT_WITH_SMALL_ADAPTATION | Keep exact ref readback as host-adapter operation, not semantic state. |
| guarded_git_ref_publish | REIMPLEMENT_FROM_CONTRACT | Git CLI, origin/ref and force-with-lease realization are host-specific; preserve race/readback invariant, not exact implementation. |
| exact_blob | REIMPLEMENT_FROM_CONTRACT | Excellent contract/test donor but hardcodes local Git, origin, main reachability and GitHub URL assumptions. |
| validate_atomic_candidate | PORT_WITH_SMALL_ADAPTATION | Bounded write-envelope algorithm survives if digest stays non-authoritative. |
| admit_native | DROP | Hard-coded pwv2.2-native generation and global epoch conflict with PWV3 per-artifact evolution. |
| tools/pwv22_native_results.py::exact_identity | REIMPLEMENT_FROM_CONTRACT | Structural normalization is insufficient; PWV3 needs one verified exact-identity type. |
| accepted_dependency | REIMPLEMENT_FROM_CONTRACT | Preserve exact accepted predecessor semantics but bind PWV3 Result/acceptance/version types. |
| affected_results | PORT_WITH_SMALL_ADAPTATION at algorithm level | Transitive material-impact cone is useful once inputs are PWV3-native verified identities. |
| material_fresh | REIMPLEMENT_FROM_CONTRACT | PWV3 must explicitly define ordered/set semantics and verified identities. |
| readiness/frontier | DROP as scheduler authority | Dependency validation survives; multi-ready frontier must not become a canonical scheduler. |
| append_result | REIMPLEMENT_FROM_CONTRACT | Result immutability survives, but old rule forbidding a new Result for unchanged implementation subject is too strong for legitimate reexecution/new evidence. |
| pwv22 Review exact-subject/append-only/finalization logic | REIMPLEMENT_FROM_CONTRACT | Strong semantics and tests, but PWV3 Review versioning, waiver honesty and OP realization must be native. |
| pwv22 Review safe_deferred subsystem | DROP | Explicitly excluded from PWV3 core. Retain only generic negative findings as regression evidence. |
| fixed Review/discovery/repair ceilings | DROP | Current owner intent requires coverage/convergence, not arbitrary semantic attempt counts. |
| tools/pwv22_effects.py whole module | REIMPLEMENT_FROM_CONTRACT | Preserve intent/attempt/readback/UNKNOWN but bind token to exact caller intent and use PWV3 versioned effect records. |
| close_contract.external_effect_recovery_action | PORT_WITH_SMALL_ADAPTATION | Compact fail-closed readback-before-retry truth table is a strong leaf donor. |
| continuation_contract.resume_action | PORT_WITH_SMALL_ADAPTATION | Durable Result => reconcile/no replay; uncertain effect => readback before retry. Use PWV3-native types. |
| continuation_contract.classify_external_evidence | PORT_WITH_SMALL_ADAPTATION | Preserve terminal/pending/missing classification but accept verified subject binding rather than caller narration alone. |
| continuation_contract.classify_progress | REIMPLEMENT_FROM_CONTRACT | No-progress/cycle invariant survives; old fingerprint/evidence_epoch vocabulary must not become authority or global epoch. |
| continuation_contract route completion string API | REIMPLEMENT_FROM_CONTRACT | stop/route/recovery and action strings are V2-shaped control vocabulary. |
| execution_contract.classify_return | PORT_WITH_SMALL_ADAPTATION | Tiny truth table survives, but PWV3 owns enum names and target language. |
| execution_contract.parse_card_result | REIMPLEMENT_FROM_CONTRACT | Hard-coded Markdown labels and V2 evidence paths would create compatibility obligations. |
| review_contract.select_review_realization | REIMPLEMENT_FROM_CONTRACT as global selector | Its ordinary non-OP truth table is reusable as a test subcase, but current @2 owner drift requires ChatGPT-only realization at OP-selected boundaries. |
| receive_contract.py | REIMPLEMENT_FROM_CONTRACT with heavy test reuse | Preserve stale/forged/narrative locator rejection and independence checks; PWV3 owns final handoff representation. |
| user_stop_contract.py | SPLIT: delivery parser PORT; Premium map DROP; stop policy REIMPLEMENT | Delivery is downstream postcondition, never semantic authority. |
| recovery_contract exact-subject formatting | PORT_WITH_SMALL_ADAPTATION only atop verified identity | Canonical textual rendering is useful but cannot make an unverified locator authoritative. |
| recovery_contract classify_resolution | REIMPLEMENT_FROM_CONTRACT | Old route names encode V2 lifecycle ownership. |
| current tools/state_contract.py | REIMPLEMENT_FROM_CONTRACT / REUSE_TESTS_OR_FIXTURES | Monolithic V2 schema authority, Task Board, Premium and path topology must not survive. |
| current tools/router.py | REIMPLEMENT_FROM_CONTRACT / REUSE_TESTS_OR_FIXTURES | Preserve deterministic/fail-closed/progressive-read/no-replay invariants, not the V2 graph. |
| templates/WORKSTREAM.toml, TASK_BOARD.toml | DROP as PWV3 canonical state | Replace with compact checkpoint + immutable/revisioned artifacts. |
| templates/CHECKPOINT.md | REIMPLEMENT_FROM_CONTRACT | Old checkpoint is cumulative recovery evidence, not the new single compact authority. |
| V2 Review/External Effect fixtures | REUSE_TESTS_OR_FIXTURES | Translate semantic scenarios to PWV3-native schema. |
| workflow/STATE.md, ROUTER.md, RECOVERY.md, CONTINUATION.md, CLOSE.md | REFERENCE_ONLY / contract evidence | Preserve rationale and failure knowledge; rewrite PWV3-native contracts. |
| Planning/Plan Review validators and Premium cycle | REIMPLEMENT_FROM_CONTRACT; Premium DROP | Keep immutable exact Plan subject + independent Review; do not import A/B/C cycle/editorial-exempt machinery. |
| Task Card parser/dependency launch refresh | REIMPLEMENT_FROM_CONTRACT | Keep stable Card contract, exact dependencies and pre-launch refresh; remove V2 Board/path restrictions. |
| classify_jit_refinement | PORT_WITH_SMALL_ADAPTATION | Bounded execution detail vs strategy vs product intent vs missing facts is a useful semantic classifier. |
| current close_contract.py whole module | REIMPLEMENT_FROM_CONTRACT | Mixed useful readback invariants with stacked/tracker/cleanup V2 policy. |
| verify_pre_mutation_target | PORT_WITH_SMALL_ADAPTATION as precheck only | Useful freshness oracle but not an atomic GitHub merge base fence. |
| stacked_integration_path | DROP | PWV3 removes stacked-workstream product semantics. |
| cleanup_branch_action | REFERENCE_ONLY / optional host hygiene port | Source-ref cleanup is non-semantic and must never determine Close. |
| pwv22_close.py | REFERENCE_ONLY + selected tests | Boolean close_ready-style proof is weaker than PWV3 exact target-side evidence. |
| pwv22_evolution classify_evolution inner material rule | PORT_WITH_SMALL_ADAPTATION | Preserve preserve/revalidate/stale/recovery logic only after historical reader validation; delete global epoch inputs. |
| activation_allowed/global epoch | DROP | Direct conflict with per-artifact versioning. |
| v1_migration.py, migration_apply.py | DROP from normal runtime; REFERENCE_ONLY/test reuse | Any future migration is exceptional external extract/validate/initialize tooling, not native compatibility. |
| fork_release_contract.py | DROP from PWV3 semantic core | Private-fork release policy is outside PWV3 core. Pure tag helpers are relevant only if a later explicit release contract adopts the same grammar. |
| pwv22_parallel.py | DROP | OP/runtime parallelism must not become canonical Card admission/claims/fan-in. |
| pwv22_lifecycle.py | DROP / REFERENCE_ONLY | Monolithic lifecycle composition is an anti-pattern for the new architecture. |
| current ChatGPT Project Instructions | REIMPLEMENT_FROM_CONTRACT | Thin-bootstrap principle survives; live V2/default-branch authority does not. |
| current Codex/Skill/package manifests | REIMPLEMENT_FROM_CONTRACT, test pattern reuse | Keep bounded package-root/fail-closed ideas, replace V2 namespace and weak marker identity with immutable PWV3 package identity. |
| pi-unraid instruction/update plane | REUSE IN PLACE operationally, not vendored | Host distribution/update/rollback remains pi-unraid-owned. PWV3 consumes an exact qualified package through a handshake. |
| non-main pi-unraid managed-component/update branches | REFERENCE_ONLY until reconciled/requalified | Useful design/test evidence but not current integrated host authority. |
| historical Paseo child-delegation workaround | REFERENCE_ONLY negative evidence | Use official caller-scoped capability; no custom spawner/daemon/shell fallback. |

## 4. Exact source-level candidates safe to copy or lightly port

### Literal COPY_AS_IS

There is no approved whole executable production module for literal copying.

The only current literal-copy candidate is the non-authoritative four-field prompts/CHATGPT_FRESH_SESSION.md template, because it contains bootstrap coordinates only. It is safe only if the receiving side freshly derives the expected canonical boundary and compares every field. If PWV3 changes that minimum handoff shape, the template becomes REIMPLEMENT rather than a compatibility requirement.

### Preferred function/algorithm-level PORT candidates

The strongest bounded ports are:

1. canonical JSON byte construction, after a cross-runtime canonicalization contract is frozen;
2. safe repository-relative POSIX path validation;
3. generic expected-old -> one mutation -> positive readback orchestration;
4. exact remote-ref observation as a host adapter operation;
5. bounded write-envelope checking;
6. non-authoritative material fingerprinting;
7. transitive affected-Result cone propagation;
8. execution return classification;
9. JIT refinement classification;
10. external-evidence terminal/pending/missing classification;
11. durable-Result no-replay restart classification;
12. external-effect readback-before-retry classification;
13. last-moment target equality precheck, explicitly not treated as the atomic final-merge fence;
14. handoff delivery structural validation after a semantic boundary already exists.

Every port must use PWV3-owned types/enums/error classes and must pass the transitive dependency/vocabulary/layout/authority audit.

### Strong contract donors that should not be copied literally

- exact Git blob/object verifier;
- Result/dependency schemas;
- Review append-only history;
- effect intent/attempt/readback artifact;
- Recovery owner reconstruction;
- router/derive-next;
- compact checkpoint;
- final PR integration;
- global health;
- target-side Close;
- per-artifact version reader/applicability;
- ChatGPT immutable-helper bootstrap;
- Pi/Paseo semantic adapter.

Their historical implementations are valuable specifications and regression sources, but their topology/host assumptions must not define PWV3.

## 5. Code and machinery that must not enter PWV3 core

The following are a hard production denylist, except where mentioned in historical documentation or explicitly negative fixtures:

- project_workflow = v2 or pwv2.2-native as native lineage;
- V2/V2.2 native artifact type tags accepted by ordinary PWV3 readers;
- one global official epoch/generation admission or activation gate;
- Premium A/B/C/D state or route names as PWV3 authority;
- TASK_BOARD.toml or a broad mutable equivalent as the canonical scheduler/state database;
- product-level parallel Card admission, claims, sibling fan-in or multi-ready frontier authority;
- safe_deferred subsystem;
- fixed semantic Review/discovery/repair attempt ceilings;
- stacked-workstream semantics;
- monolithic integrated lifecycle validator;
- native V1/V2/V2.2 migration/compatibility readers;
- V2 workstream path topology as required PWV3 authority;
- current V2 router/state modules behind a thin new adapter;
- live runtime/build import from elmakus/project_workflow_v2;
- live dependency on the old construction repository;
- current V2 ChatGPT default-branch workflow fetch;
- marker-only package authenticity checks;
- runtime/model/session/worker/lane/batch/scheduler identity as semantic legality;
- material fingerprint as acceptance identity;
- branch/session termination as semantic Close;
- source-branch survival as a requirement for terminal truth;
- Issue state as workflow authorization;
- blind retry after uncertain external mutation;
- local/private helper cache or deployment state as workflow truth;
- custom Paseo worker spawner/daemon/shell fallback;
- mandatory MCP or mandatory Paseo semantic state plugin for v1.

## 6. Reusable semantic primitive set

PWV3 should converge on a small native primitive set rather than a port of V2 modules.

### Identity and publication

- SafeRepoPath
- ParsedGitObjectRef
- VerifiedGitObjectRef
- ExactRefObservation
- ExpectedOldPublication
- PositiveReadback
- BoundedWriteEnvelope
- DerivedMaterialFingerprint

### Durable semantic artifacts

- CompactCheckpoint
- ResultRecord
- AcceptedDependency
- ReviewAttempt
- ReviewHistory
- ExternalEffectIntent/Attempt/Readback
- artifact-kind + producing-contract-version reader registry

### Deterministic decisions

- deriveNextObligation over compact checkpoint + exact artifacts
- classifyExecutionReturn
- classifyJitRefinement
- classifyExternalEvidence
- classifyExternalEffectNextAction
- classifyResumeNoReplay
- classifyMaterialApplicability
- classifyNoProgress/Cycle
- classifyTargetRefresh/ReviewApplicability

### Terminal/integration

- FinalPrObservation
- FinalIntegrationProof
- TargetSideCloseProof
- ConfirmedDefectHealth = HEALTHY | BLOCKED(issue_ids) | UNKNOWN

### Runtime/bootstrap

- immutable helper/package discovery + verification;
- explicit capability probe;
- thin ChatGPT adapter;
- thin Pi/Paseo adapter;
- locator-only fresh-context bootstrap;
- handoff delivery validator that cannot mint semantic authority.

These primitives are intentionally smaller than the old state/router/lifecycle surface.

## 7. Test, fixture and regression migration map

The enduring regression corpus should be established before or alongside the first implementation primitives.

### Near-verbatim low-level scenarios

From V2.2 native foundation/effects tests:

- wrong repository identity fails;
- wrong blob/path/object fails;
- served bytes differing from Git bytes fail;
- unsafe/backslash/traversal path fails;
- symlink rejected where regular blob required;
- unpublished local-only commit rejected when canonical publication is required;
- stale expected-old loses;
- interleaving remote writer defeats stale candidate;
- readback mismatch is not success;
- crash before publish leaves remote canonical state unchanged;
- UNKNOWN external effect forbids retry;
- attempted-without-readback forbids retry;
- verified no-effect may allow controlled retry;
- verified expected effect reconciles without replay.

### Result/Review/evolution scenarios

Translate to PWV3-native artifact versions:

- forged or stale accepted dependency fails;
- changed implementation requires a new Result;
- legitimate reexecution may create new evidence/Result according to the PWV3 Result contract even when implementation bytes are unchanged;
- unrelated material change preserves unaffected evidence;
- transitive affected cone is conservative;
- Review binds exact subject + exact acceptance surface;
- terminal Review history is append-only;
- material author/repairer cannot be represented as independent approval;
- unknown impact fails closed;
- unchanged implementation may be revalidated without rewriting historical Result bytes;
- unknown historical artifact version/reader fails closed.

### Current V2 continuation/routing scenarios

Retain semantic oracles, not V2 directory topology:

- runtime-noise changes do not change legal semantic outcome;
- worker/Research/Review completion alone is not a stop;
- durable Result after restart reconciles without replay;
- uncertain effect requires readback before retry;
- pending external evidence is not success;
- claimed reconciliation without semantic/evidence progress fails;
- evidence-free cycle fails;
- exact Research return owner cannot be shadowed;
- one active Card;
- stale dependency cannot launch;
- changed reviewed Result requires a new Review;
- terminal Cards continue into Close reconciliation rather than ending by role completion.

### Historical defect corpus that must survive

At minimum preserve these historical counterexamples with provenance:

- #25: fresh independent-review handoff loop;
- #26: producer/consumer serialization mismatch and malformed durable bytes;
- #28: Research-return owner shadowing;
- #32: incomplete relational state manufacturing authorization/alignment;
- #33: explicit user stop bypassed by later routing;
- #36: orphan pre-execution owners silently bypassed.

The rewritten PWV3 scenarios should state the enduring failure class, not preserve Premium, Task Board or old file topology.

### Current @2 assurance/OP regressions to add

Because of the owner drift, add explicit PWV3 regressions:

1. enabled OP at any of the four owner-fixed boundaries cannot be locally substituted by Pi/Paseo Generic Workers;
2. Pi/Paseo reaching an enabled OP boundary emits a runtime-neutral handoff to ChatGPT and stops;
3. ChatGPT already at the same semantic runtime does not perform a fake cross-runtime handoff; a fresh ChatGPT context is requested only where OP/independence requires it;
4. OP discovery does not stop at the first finding; declared bounded coverage continues to exhaustion/convergence unless genuinely blocked;
5. findings are deduplicated/integrated without majority voting;
6. after bounded repair, focused fresh revalidation is used rather than automatically launching a second full OP wave;
7. a new full OP wave requires the owner-defined material triggers;
8. OP metadata never creates parallel Project Cards, claims or fan-in state.

### Tests that must not become PWV3 positive acceptance

Drop or convert to negative historical evidence:

- global epoch/generation tests;
- Premium A/B/C/D sequencing;
- V2.2 parallel admission/claims/fan-in;
- safe-deferred subsystem;
- fixed convergence ceilings;
- stacked-workstream behavior;
- fork-release semantics inside PWV3 core;
- normal-runtime V1/V2 migration;
- exact V2 path/read-order assertions whose only purpose is predecessor representation.

## 8. Shared-library extraction decision

Reject a shared pwv2/pwv3 semantic runtime library for PWV3 bootstrap.

Reasons:

1. the strongest reusable algorithms are small;
2. several need PWV3-specific tightening anyway;
3. current preferred helper direction is ESM/Node while donor implementations are Python;
4. a shared package would convert historical reuse into permanent cross-lineage maintenance and compatibility coupling;
5. exact provenance plus migrated golden/regression tests preserves continuity without shared execution authority;
6. shared-library versioning would create another semantic ambiguity before PWV3 contracts stabilize.

If, after PWV3 is independently qualified, a truly product-neutral utility is useful to multiple products, it may later become an independent package only if it has no workflow semantics, independent versioning/tests and no ability to route or interpret workflow state. That future possibility is not part of this extraction plan.

## 9. Provenance and history treatment

Every copied/ported source unit or translated historical regression should have durable provenance with:

- origin_repository;
- origin_commit;
- origin_path;
- origin_blob where available;
- source symbol/test/scenario;
- disposition;
- target path;
- transformation/adaptation summary;
- validation/regression IDs;
- applicable license/notice action.

Rules:

- use immutable commit/blob references, not branch names, as provenance;
- preserve required third-party notices;
- record provenance in a repository-level ledger and/or importing commit, not as semantic state;
- do not use Git submodules, subtree linkage, symlinks, editable installs, generated donor fetches or shared V2 packages as the provenance mechanism;
- after import, PWV3 owns the code independently;
- later V2 changes do not automatically propagate;
- historical V2 fixtures may remain in a quarantined negative corpus without becoming native readable state.

## 10. Practical extraction order into empty elmakus/pwv3

### E0 — Native recipient and provenance skeleton

Create only PWV3-native package metadata, test runner, minimal source layout and non-authoritative donor provenance ledger.

Acceptance:
- no V2 checkout/package/network dependency;
- clean lineage;
- package trust origin is fixed outside mutable consumer workstream content.

### E1 — Regression corpus first

Create the implementation-independent scenario schema and import/translate exact identity, race, effect, Result/Review/no-replay and historical defect cases.

Acceptance:
- each retained scenario states its enduring invariant and provenance;
- no test requires V2 runtime modules;
- removed V2 semantics are quarantined or negative-only.

### E2 — Identity/path/publication kernel

Implement safe paths, verified exact Git identity, ref observation, expected-old publication/readback, bounded write envelopes and derived fingerprinting.

Acceptance:
- forged identity, path, symlink, unpublished object, stale writer and readback mismatch regressions are GREEN;
- no success without positive authoritative readback.

### E3 — Result/dependency/impact

Define PWV3 Result version/schema, immutable evidence, exact accepted dependencies and material-local impact.

Acceptance:
- stale/forged dependencies fail;
- changed implementation cannot reuse old acceptance;
- unrelated evidence remains valid;
- no frontier/scheduler authority exists.

### E4 — Review/effects/Recovery

Implement append-only exact Review, semantic independence/waiver honesty, versioned effect intent/attempt/readback/UNKNOWN, no-replay Recovery and mechanical-vs-semantic repair boundary.

Acceptance:
- author/repairer cannot self-approve as independent;
- UNKNOWN never retries;
- durable Result never reexecutes from runtime loss;
- no fixed semantic attempt ceiling.

### E5 — Compact checkpoint and per-artifact readers

Define the smallest authoritative current/recovery checkpoint plus independently versioned artifact readers.

Acceptance:
- no Task Board-equivalent broad mutable projection;
- no global epoch;
- no runtime/session state;
- unknown versions fail closed;
- historical PWV3 bytes use their producing reader.

### E6 — Sequential derive-next lifecycle

Implement one legal next obligation from checkpoint + exact artifacts, with Main owning genuine semantic ambiguity.

Acceptance:
- exactly one active Card;
- no claims/fan-in/multi-ready scheduler;
- no Premium/legacy branch;
- no-progress/cycle and stop precedence regressions pass.

### E7 — GitHub/Issues/final PR/Close

Implement exact final PR observation, native base-freshness policy, mutation/readback, Issue dedup/readback, confirmed-defect health and target-side Close.

Acceptance:
- expected head/base races fail closed;
- uncertain merge/effect reads back before retry;
- Issue state cannot authorize workflow;
- health query failure/pagination ambiguity => UNKNOWN;
- Close reconstructs after source-ref deletion.

### E8 — Runtime-neutral helper/package and thin adapters

Implement one immutable verified helper package, minimal ChatGPT bootstrap, Pi/Paseo skill/native adapter and CLI/debug surface over the same core.

Acceptance:
- mutable discovery channel is not execution identity;
- helper digest/object mismatch fails closed;
- capability is probed, not inferred from host name;
- cross-runtime semantic parity for same exact inputs;
- Pi/Paseo host distribution/update remains host-owned rather than vendored.

### E9 — Dependency purge and PWV3-on-PWV3 qualification

Run import/string/schema/provenance audits and representative dogfood.

Acceptance:
- zero runtime/build dependency on project_workflow_v2;
- no accidental pwv2.2, Premium, global epoch, Task Board authority, parallel claim/fan-in, safe-deferred, legacy reader or fork-release core;
- build/test succeeds with donor repositories unavailable;
- representative PWV3-on-PWV3 work reaches terminal Close using only PWV3-native durable truth.

## 11. Acceptance checks proving PWV3-native rather than V2-dependent

Before donor extraction is considered complete, require all applicable checks:

1. No production import, package, submodule, generated fetch or runtime lookup reaches elmakus/project_workflow_v2.
2. No build/test requires the old construction repository.
3. No normal runtime accepts V1/V2/V2.2 state as native PWV3 state.
4. No semantic production schema contains Premium, global V2.2 epoch/generation, Task Board authority, safe-deferred, canonical parallel claims/fan-in or stacked-workstream state.
5. Each durable artifact has an explicit PWV3 producing contract version.
6. Unknown artifact version/reader fails closed.
7. Exact identities are positively resolved against real Git/GitHub objects where required.
8. Valid-looking forged repository/commit/path/blob fails.
9. Branch name or mutable channel alone never satisfies immutable acceptance identity.
10. Publication loses stale expected-old races and requires positive remote readback.
11. A readback mismatch is never reported as semantic progress.
12. Derived fingerprint loss/recomputation cannot lose workflow truth.
13. Result/Review terminal history is immutable/append-only.
14. Changed implementation cannot inherit prior GREEN silently.
15. Acceptance binds exact subject plus exact acceptance surface.
16. Runtime/provider/model/session/worker identity cannot determine legality or independence.
17. Exactly one Project Card is semantically active.
18. Dependency/impact helpers cannot schedule parallel Cards.
19. Durable Result after restart reconciles without replay.
20. UNKNOWN external effect blocks blind retry; verified no-effect is required before retry where applicable.
21. Exact caller intent binds any idempotency/request token.
22. No-progress/evidence-free cycles fail closed without fixed arbitrary semantic retry ceilings.
23. Final integration uses exact PR/head/base/candidate/acceptance/readback evidence and repository-native freshness policy.
24. Target-side Close survives source-ref deletion.
25. GitHub Issue state cannot manufacture semantic approval.
26. Confirmed-defect global health is HEALTHY only after a complete trusted query proves zero matching open Issues; failures are UNKNOWN.
27. ChatGPT and Pi/Paseo adapters share the same semantic contract and produce equivalent semantic outcomes for equivalent exact inputs.
28. Moving helper/package channels are discovery only; execution identity is immutable and verified.
29. OP-selected boundaries obey ChatGPT-only realization and cannot be satisfied locally by Pi/Paseo workers.
30. OP orchestration never creates canonical Project Card parallelism or a second workflow scheduler.
31. A clean clone builds/tests/runs with donor repositories unavailable.
32. Every copied/ported unit and translated historical regression has immutable provenance.

## 12. Current Brainstorm/owner drift and its donor consequences

The @2 owner drift is material to donor integration even though donor source/tests did not change.

Owner-fixed requirements now include independently selectable optional formal Orchestration Protocol realization at:

1. Brainstorming Research;
2. Definition Review;
3. Plan Review;
4. Execution Prep / Execution Package Review.

When selected, OP executes only in fresh ChatGPT contexts under the Research/Coordinator model. Pi/Paseo must hand off runtime-neutrally to ChatGPT and stop at the OP-selected boundary. If execution is already in ChatGPT, no fake cross-runtime handoff is required; a fresh ChatGPT context is used when OP/semantic independence requires it.

OP discovery continues bounded declared coverage after findings, integrates/deduplicates root causes without majority voting, and uses focused fresh post-repair revalidation rather than an automatic second full wave. A new full wave requires the owner-defined material triggers.

These owner-fixed rules alter donor classification in four places:

- current review_contract.select_review_realization is not safe as the universal PWV3 realization selector because its internal-independent path could incorrectly allow Pi/Paseo local satisfaction of an enabled OP boundary;
- historical pwv22_parallel remains DROP and cannot be repurposed as OP machinery;
- fixed Review/discovery ceilings remain DROP and are even less compatible with the owner-fixed coverage/convergence model;
- fresh-context bootstrap/handoff donors remain useful, but the implementation must distinguish same-runtime fresh ChatGPT context from actual cross-runtime Pi/Paseo -> ChatGPT handoff.

The current consumer also states that Brainstorming cannot finalize until the release-roadmap, donor-strategy, defect-regression-corpus and assurance-orchestration-profile evidence is integrated and owner-facing contradictions/choices are reconciled. This donor synthesis therefore does not promote Definition or Planning.

## 13. Genuine unresolved owner decision

No donor-policy-specific owner decision remains unresolved by this evidence.

The donor evidence is sufficient to decide the reuse boundary: selective one-way primitive/test reuse, new PWV3 authority/state contracts, no shared V2/V3 semantic dependency, and explicit rejection of obsolete V2/V2.2 machinery.

One broader product/release question remains outside this donor package: placement of the first-class assurance/orchestration profile in PWV3 3.0 versus a later release. Current consumer evidence explicitly assigns that reconciliation to the release-roadmap/parallel Brainstorm Research. This synthesis does not guess or replace that result. The owner-fixed capability itself and its four selectable boundaries are already settled; only release placement remains a separate Research/release reconciliation.

If the parallel release-roadmap evidence does not resolve release placement mechanically, that becomes the owner-facing decision before the next Definition. It is not a reason to reopen the donor-policy conclusions above.

## 14. Final integrated donor strategy

PWV3 should be a clean successor with selective memory:

- preserve exact identity, publication/readback, no-replay, append-only evidence, effect UNKNOWN, material-local impact, one-active-Card and fail-closed recovery semantics;
- port only the smallest demonstrably generic algorithms into PWV3-owned types;
- reimplement all lifecycle/state/compatibility-owning modules from the PWV3 contract;
- migrate the strongest historical regressions before or with implementation;
- keep pi-unraid operational host machinery outside the PWV3 semantic core and integrate through an exact package/capability handshake;
- record immutable provenance without live donor dependency;
- reject Task Board, Premium, global epoch, parallel claims/fan-in, safe-deferred, fixed semantic ceilings, stacked workstreams, native legacy migration and monolithic lifecycle machinery;
- make OP a ChatGPT-only assurance realization when selected, never canonical Card parallelism.

The safest extraction order is:

regressions first -> verified identity/readback -> Result/dependency/impact -> Review/effects/Recovery -> compact per-artifact state -> sequential derive-next -> GitHub/final PR/Close -> immutable helper + thin host adapters -> dependency purge and PWV3-on-PWV3 qualification.

That preserves the expensive knowledge embedded in PWV2/V2.2 while making the rejected predecessor architecture unnecessary.
