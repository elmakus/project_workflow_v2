# PWv2 Swarm Audit — Consolidated Independent Results

## Exact aggregation subject

- Repository: elmakus/project_workflow_v2
- Exact commit: 4fb4bfb7d7b1481d6f347c182fc96a5a1135e045
- Source prefix: audit/pwv2-swarm-
- Aggregation only: yes. No independent product review, repair, or Project Workflow transition was performed.
- Final frozen matching source-set size: 36 branches.
- Completed valid original swarm audits included: 34.
- Freeze protocol: prefix enumerated once at start and exactly once more immediately before freeze; the second enumeration was unchanged.

## Executive summary

- Matching audit branches discovered: 36
- Completed valid source audits included: 34
- Incomplete/empty source branches: 2
- CLEAN source audits: 0
- FINDINGS FOUND source audits: 34
- Total original material findings before deduplication: 164
- Candidate defect-class clusters: 27
- Clusters independently reported by 2+ audits: 15
- Unique single-source candidate findings/classes: 12
- Excluded mismatched completed reports: 0

Frequency records independent rediscovery only. It is not a validity threshold or technical confirmation.

## Frozen source set

| Source ID | Branch | Audit commit | Verdict | Findings | Lenses |
|---|---|---|---|---:|---|
| S001 | audit/pwv2-swarm-11j9refnjjr4zgst7rm39sz9 | 88377fa9baebcb3bd89bcbe13bef97fa6f0f0858 | FINDINGS FOUND | 3 | Close/finalization; helper/document parity; Planning/Premium; router precedence |
| S002 | audit/pwv2-swarm-1m24f9qan3e4kmlfif0xw93w | dff6632cfe774a70588dc3a868a3b5621e743d92 | FINDINGS FOUND | 7 | stale identity; Close/finalization; router precedence; plugin/bootstrap |
| S003 | audit/pwv2-swarm-1nf66pps8yiv44rk65rdcv5g | 0ee4c90539541c7a89d5914704922c05a7f70692 | FINDINGS FOUND | 4 | RED/recovery; path/locator safety; Planning/Premium; Close/finalization |
| S004 | audit/pwv2-swarm-45ulo91hciq37ytbao10h4wv | 5b8b188042de878e2971e652d332c946094bd335 | FINDINGS FOUND | 5 | plugin/bootstrap; Close/finalization; review bypass; Task Board/JIT |
| S005 | audit/pwv2-swarm-4iwvszq379kizplu3lskirk4 | b18b4fb9c9e53415045de8691dc474fa08329a38 | FINDINGS FOUND | 4 | stale identity; Close/finalization; RED/recovery; Research/Intake |
| S006 | audit/pwv2-swarm-57c66ill1e5ntlgarmntge88 | 5226743cb20e78631635060f0642a1ed80019811 | FINDINGS FOUND | 4 | path safety; malformed state; review bypass; router precedence |
| S007 | audit/pwv2-swarm-69f0g74xooo389jwdz456zmv | 2bfc9a707b0c8709247c963989f5b51e0aeb5058 | FINDINGS FOUND | 5 | Research/Intake; plugin/bootstrap; router precedence; helper/document parity |
| S008 | audit/pwv2-swarm-6ugr6l0d6zsn8fgvpdj1cjsd | 34057ae5bb9d4b9fbf979bc01187107bfb4f2366 | FINDINGS FOUND | 4 | router precedence; Planning/Premium; malformed state; plugin/bootstrap |
| S009 | audit/pwv2-swarm-704a9fctlw3yp99at6ov43d5 | 5774f55a4bda9599d851f56b1364349b48783bc8 | FINDINGS FOUND | 6 | path safety; malformed state; router precedence; review bypass |
| S010 | audit/pwv2-swarm-7sgwic5vusy2pkcta7682nm2 | f0433d4406e979daa8b63f5d2b9da29a196653cb | FINDINGS FOUND | 4 | Planning/Premium; Research/Intake; RED/recovery; router precedence |
| S011 | audit/pwv2-swarm-8wu3nv7atoj98fvx5u4a1lzs | 9de74746c63aa1ff99da9af2da7420f16c1cf0b8 | FINDINGS FOUND | 6 | Research/Intake; helper/document parity; path safety; stale identity |
| S012 | audit/pwv2-swarm-9l58xtzmupt9tz7p7gxv5975 | cc8130b2f2067020b8a8f82abbccd9902f7533db | FINDINGS FOUND | 6 | plugin/bootstrap; stale identity; Planning/Premium; RED/recovery |
| S013 | audit/pwv2-swarm-b7qtnwcsraaa1fat6o96n77a | 3be5f3f034fe96f7e5262667fde5bd684c06b55e | FINDINGS FOUND | 4 | helper/document parity; stale identity; Research/Intake; router precedence |
| S014 | audit/pwv2-swarm-jyxmfic5ggkl2cok7gu7ng4w | 3b0ac915d68e9783e48cfceba7c9bffef1ab6ca1 | FINDINGS FOUND | 4 | review bypass; Close/finalization; stale identity; Research/Intake |
| S015 | audit/pwv2-swarm-k7m2q9v4x1c8n5r0t6w3z8pa | fce5f9f6b0661f23b4b9039275be874ee002993c | FINDINGS FOUND | 6 | router precedence; stale identity; RED/recovery; helper/document parity |
| S016 | audit/pwv2-swarm-k7m2q9v4x1c8n6r0t5h3p2zb | aefc7d69448f200e8617d4061cc7b36bed516429 | FINDINGS FOUND | 5 | malformed state; stale identity; Close/finalization; helper/document parity |
| S017 | audit/pwv2-swarm-k7m2v9q4x1n8c5r0t6p3b2d9 | e8c6f32a5c37e622347312acd30b3ddf14ff80cf | FINDINGS FOUND | 5 | review bypass; Close/finalization; Research/Intake; path safety |
| S018 | audit/pwv2-swarm-ky3dtpzh88ndw84aq45itmdv | e1da747118d64b42e39850817aecdd5be5a86192 | FINDINGS FOUND | 4 | malformed state; helper/document parity; router precedence; path safety |
| S019 | audit/pwv2-swarm-luba8a4q8jb2nbtv2i2mra8w | a084d0a0e6bcfaff17de036846989970c4cc4f2b | FINDINGS FOUND | 5 | Research/Intake; plugin/bootstrap; path safety; review bypass |
| S020 | audit/pwv2-swarm-m7q2v9x4c1k8r6p3n0t5h2z7 | 507ab769530607009f218881b90d87ba7ee182c4 | FINDINGS FOUND | 7 | Planning/Premium; malformed state; Research/Intake; review bypass |
| S021 | audit/pwv2-swarm-ni3axnsfbpabhyhjgl2dy7q4 | 9e170d02e0460b63b879e7a92e6306d6c4c6db2a | FINDINGS FOUND | 4 | plugin/bootstrap; Research/Intake; Close/finalization; malformed state |
| S022 | audit/pwv2-swarm-novka0hlkl74xbxwtotil5iz | f34a0ef440b1375f8008dba0ba31cf16d1c95cf0 | FINDINGS FOUND | 4 | review bypass; malformed state; stale identity; Task Board/JIT |
| S023 | audit/pwv2-swarm-o9x9kt40jy3l8lsxhgj5posd | e11c5d9ded773150867709d1673121c2c872742f | FINDINGS FOUND | 4 | plugin/bootstrap; Planning/Premium; RED/recovery; helper/document parity |
| S024 | audit/pwv2-swarm-os2xq9rsnl22hac1qcjfptsz | bef8ce04dd4e512302bac1d513ac547c323b0df0 | FINDINGS FOUND | 7 | malformed state; stale identity; helper/document parity; Research/Intake |
| S025 | audit/pwv2-swarm-q7m2v9k4x1c8n5r0t6p3zjhw | 2d6e0e797eee08c402ff33057dcead54e0dc26f6 | FINDINGS FOUND | 5 | stale identity; RED/recovery; Close/finalization; helper/document parity |
| S026 | audit/pwv2-swarm-qiegju16x0nv1c3tz4ls8wss | df90084da1707278a4e8772520e14e6569477a00 | FINDINGS FOUND | 7 | Close/finalization; helper/document parity; Planning/Premium; plugin/bootstrap |
| S027 | audit/pwv2-swarm-s06uaj47ohetuymvwvo8x0da | d0d63b59d7e026b88673166165a92a2ec15b7eac | FINDINGS FOUND | 4 | malformed state; helper/document parity; Task Board/JIT; router precedence |
| S028 | audit/pwv2-swarm-sdcia5015cuyksv7guxzxuw6 | f53adb7d40c0c90b29647b8779abd71134073938 | FINDINGS FOUND | 5 | review bypass; Task Board/JIT; malformed state; stale identity |
| S029 | audit/pwv2-swarm-t1qv8efwb5ghlfht8sckdb1q | 3ec54c8ea9ab1ac04b90b3ed8a10078656a2b408 | FINDINGS FOUND | 5 | Planning/Premium; review bypass; stale identity; RED/recovery |
| S030 | audit/pwv2-swarm-uppoz22buvceidlmlgxop9gg | c7dc9aba6c4bfdc995347ec1b2a2939f8874a823 | FINDINGS FOUND | 4 | RED/recovery; Planning/Premium; Close/finalization; stale identity |
| S031 | audit/pwv2-swarm-v59lpyq5jxrsgegtivvtk470 | 0784553af41ec52a7f4800a449f31229c0b3cc07 | FINDINGS FOUND | 5 | stale identity; helper/document parity; plugin/bootstrap; Planning/Premium |
| S032 | audit/pwv2-swarm-x9m2q7v4k1c8n5r0t6p3zjha | d0f83f0423b7afd248ddbfa687fdb6d9dea97047 | FINDINGS FOUND | 4 | immutable subject/content; review evidence/gates; router real-stop precedence; issue prior-art authorization |
| S033 | audit/pwv2-swarm-yc80f4r9jz0jn7b0vzdv424d | a98beb2b2c08d6a073cdf41fbcb17ec778f48ec0 | FINDINGS FOUND | 3 | router precedence; stale identity; plugin/bootstrap; Task Board/JIT |
| S034 | audit/pwv2-swarm-ze8eya3df1xsxsb7q93smiac | 6eab0280ab30c8f0cafe693c7e5b4f2a8838f2fb | FINDINGS FOUND | 5 | helper/document parity; Close/finalization; stale identity; Task Board/JIT |

Source IDs follow lexicographic branch order. Every included source metadata record names repository elmakus/project_workflow_v2 and exact subject 4fb4bfb7d7b1481d6f347c182fc96a5a1135e045.

## Incomplete / excluded sources

| Branch | Classification | Reason |
|---|---|---|
| audit/pwv2-swarm-5oa5ebacdvo91ef5uabc1bdk | Incomplete/empty | Branch exists, but audits/swarm/5oa5ebacdvo91ef5uabc1bdk/META.toml and REPORT.md were both absent at freeze. |
| audit/pwv2-swarm-q7m2v9k4x1c8n5r0t6b3p2hz | Incomplete/empty | Branch exists, but audits/swarm/q7m2v9k4x1c8n5r0t6b3p2hz/META.toml and REPORT.md were both absent at freeze. |

No completed report was excluded for wrong repository, wrong subject, malformed source identity, aggregate/triage/repair character, formal Project Workflow review status, or M02R shadow-review status.

## Candidate defect-class clusters

Every original material finding is assigned to one primary cluster. Broad source findings may mention sibling risks that overlap another class; those overlaps are preserved in the finding ledger rather than double-counted. Clustering is descriptive and does not technically confirm or reject any claim.


### C001 — Unverified immutable Git subject/content identity

- Similarity classification: SAME CLASS
- Independently reported by: 34 source audits
- Source findings: S001-F01, S002-F02, S003-F01, S004-F01, S005-F01, S005-F02, S006-F01, S007-F01, S008-F01, S009-F01, S010-F03, S011-F01, S012-F01, S013-F01, S014-F01, S015-F03, S016-F02, S017-F01, S018-F02, S019-F02, S020-F05, S022-F02, S023-F02, S024-F01, S025-F01, S025-F02, S026-F03, S027-F03, S028-F03, S029-F01, S030-F02, S031-F01, S032-F01, S033-F02, S034-F03.
- Affected contracts/invariants reported by sources: STATE exact result/dependency identity; EXECUTION_PREP READY refresh; REVIEW exact result subject; PLANNING/PLAN_REVIEW frozen Git subject.
- Shared core claim: repository/commit/path/blob values are shape-checked or compared as declarations, but the bytes/object actually consumed are not proven to be the named Git object. Several sources also note that a result locator may be path-only.
- Distinct reproduction vectors: same-path result mutation after GREEN; READY dependency file mutation with unchanged tuple; synthetic/fabricated 40-hex identities; foreign/nonexistent Planning subject; path-only result accepted.
- Important disagreements between sources: no material disagreement on the identity gap; sources differ on which consumer demonstrates it and whether path-only results are a sibling or part of the same class.
- Existing reproduction artifacts: numerous source-local selector scripts named in the full ledger; several use the repository router fixture.
- Why sources considered it material/load-bearing: exact immutable identity is the stated basis for stale-input rejection, review reuse, recovery truth, and dependency launch.
- Source limitations: many selector repros were preserved but could not be executed in-session because exact-checkout execution was unavailable; some parser/helper cases were executed in isolation.
- Triage priority hints: widespread independent rediscovery; many concrete executable reproductions; authority/review/recovery relevance.

### C002 — DONE terminal status can bypass result/review terminal proof

- Similarity classification: SAME CLASS
- Independently reported by: 24 source audits
- Source findings: S002-F03, S003-F02, S004-F03, S009-F02, S011-F04, S012-F05, S013-F02, S014-F02, S015-F02, S016-F01, S018-F01, S019-F01, S020-F04, S021-F03, S022-F01, S023-F01, S024-F07, S026-F01, S027-F02, S028-F01, S029-F03, S030-F01, S033-F03, S034-F02.
- Affected contracts/invariants reported by sources: STATE terminal Card semantics; REVIEW blocking lifecycle; ROUTER all-DONE Close handoff.
- Shared core claim: Board validation/all-DONE routing trust status=done without reconstructing the valid-result and exact-GREEN review proof that makes DONE legal.
- Distinct reproduction vectors: no review attempt; pending/RED review; missing result artifact; required-review Card directly flipped to DONE; blocker residue.
- Important disagreements between sources: none on the core bypass; some sources include missing result validity while others focus exclusively on review.
- Existing reproduction artifacts: multiple source-local DONE-state fixture repros, listed in the ledger.
- Why sources considered it material/load-bearing: mutable Board status can erase an independent review or recovery obligation and send invalid work toward Close/integration.
- Source limitations: most source reports rely on direct selector/control-flow analysis plus preserved fixture scripts; some lacked a fresh runtime.
- Triage priority hints: widespread independent rediscovery; executable reproduction; review/recovery/finalization relevance.

### C003 — Durable result/review evidence paths are not dereferenced

- Similarity classification: SAME CLASS
- Independently reported by: 16 source audits
- Source findings: S001-F02, S004-F02, S006-F03, S009-F04, S011-F05, S012-F02, S013-F03, S015-F06, S017-F05, S018-F03, S019-F03, S020-F07, S022-F03, S031-F04, S032-F02, S034-F05.
- Affected contracts/invariants reported by sources: EXECUTION durable evidence refs; REVIEW terminal verdict evidence; PLAN_REVIEW terminal evidence.
- Shared core claim: evidence references are checked for syntax/non-emptiness but are not required to exist/read before result reconciliation or terminal review consumption.
- Distinct reproduction vectors: delete result evidence; point GREEN/RED evidence to nonexistent file; delete both result and review evidence; arbitrary relative evidence.
- Important disagreements between sources: some sources include Plan Review only as a sibling; one source expresses slightly lower confidence about evidence-content semantics, not existence.
- Existing reproduction artifacts: evidence-deletion and missing-evidence scripts on many source branches.
- Why sources considered it material/load-bearing: terminal proof and accepted-result recovery truth can survive disappearance or fabrication of the durable evidence they claim.
- Source limitations: most are source-level/control-flow reproductions, often not executed in the constrained audit sessions.
- Triage priority hints: widespread rediscovery; concrete executable reproduction; review/recovery relevance.

### C004 — Implementation review acceptance is path-only or not bound to the selected Card contract

- Similarity classification: SAME CLASS
- Independently reported by: 11 source audits
- Source findings: S002-F05, S006-F02, S011-F06, S015-F04, S016-F04, S017-F02, S019-F05, S024-F02, S028-F02, S029-F05, S034-F04.
- Affected contracts/invariants reported by sources: REVIEW exact acceptance surface; STATE review binding; EXECUTION_PREP stable Task Card authority.
- Shared core claim: GREEN freshness binds result subject strongly but accepts Task Card acceptance as mutable path/Card ID; current Card bytes or selected contract locator are not immutably cross-checked.
- Distinct reproduction vectors: same-path Acceptance or required-tests mutation; changing Review requirement; relocating Board contract to same-ID archive path; nonexistent alternate acceptance path.
- Important disagreements between sources: none on the mutable/path-only acceptance problem; vectors differ between same-path mutation and wrong-current-contract binding.
- Existing reproduction artifacts: Task Card mutation and relocation scripts in source reports.
- Why sources considered it material/load-bearing: GREEN can authorize finalization under acceptance criteria the reviewer did not evaluate.
- Source limitations: preserved scripts are often unexecuted; control-flow gap is directly described.
- Triage priority hints: widespread rediscovery; executable reproduction; review-gate relevance.

### C005 — Plan Review acceptance is not bound to current Definition authority

- Similarity classification: SAME CLASS
- Independently reported by: 3 source audits
- Source findings: S007-F04, S024-F04, S031-F05.
- Affected contracts/invariants reported by sources: PLAN_REVIEW exact acceptance authority; PLANNING review gate.
- Shared core claim: a Plan Review may use a syntactically permitted but unrelated authority path because acceptance is not cross-bound to current Definition/requirements/decisions.
- Distinct reproduction vectors: workflow/ROUTER.md as acceptance; unrelated decision file; NOT_CURRENT requirements path.
- Important disagreements between sources: none material.
- Existing reproduction artifacts: source-local Plan Review validator/router scripts.
- Why sources considered it material/load-bearing: Stage-6 GREEN can be recorded against the wrong product authority.
- Source limitations: primarily source-level validator/control-flow demonstrations.
- Triage priority hints: independent rediscovery; planning/review authority relevance.

### C006 — Research origin/return owner or Card subject lacks referential coherence

- Similarity classification: SAME CLASS
- Independently reported by: 11 source audits
- Source findings: S002-F06, S005-F03, S009-F05, S010-F01, S011-F03, S013-F04, S014-F04, S015-F05, S017-F03, S019-F04, S020-F02.
- Affected contracts/invariants reported by sources: RESEARCH exact return ownership; RECOVERY Task-Board Research return; ROUTER fail-closed binding.
- Shared core claim: origin_role, origin_subject and return_target are validated independently/by prefix, permitting jumps to another owner, nonexistent Card, phantom subject or empty suffix.
- Distinct reproduction vectors: Intake-origin returning Definition; M01-T04 returning M99-T99; execution: with empty suffix; PHANTOM subject; origin/return-role mismatch.
- Important disagreements between sources: none on missing cross-field integrity; sources cover pre-execution and implementation forms.
- Existing reproduction artifacts: numerous Research fixture scripts in the ledger.
- Why sources considered it material/load-bearing: Research is explicitly non-authoritative and must return once to the exact durable owner.
- Source limitations: most scripts preserved rather than executed.
- Triage priority hints: widespread rediscovery; authority/routing/recovery relevance.

### C007 — Early generic Research dispatch can outrun higher-precedence boundaries or Board ownership

- Similarity classification: OVERLAPPING / NEEDS TRIAGE
- Independently reported by: 13 source audits
- Source findings: S001-F03, S006-F04, S007-F02, S008-F02, S011-F02, S012-F03, S014-F03, S024-F03, S025-F05, S026-F07, S027-F04, S030-F03, S032-F03.
- Affected contracts/invariants reported by sources: ROUTER precedence; explicit/premium stops; INTAKE issue boundaries; Task-Board implementation Research ownership.
- Shared core claim: the top-level workstream Research branch runs before later owner state and can preempt a stop/Intake/Board obligation or mis-handle legal co-bound implementation Research.
- Distinct reproduction vectors: active Research + explicit stop; Research + premium A; unrelated Research + issue alignment/prior-art requirement; orphan execution Research; co-bound execution Research shadowed by pre-execution owner map.
- Important disagreements between sources: effects differ—illegal continuation, wrong-owner preemption, or rejection of a legal state—so later triage should decide whether one ordering repair or several owner-specific repairs are required.
- Existing reproduction artifacts: source-local router scripts across listed findings.
- Why sources considered it material/load-bearing: it can cross human authority, issue safety, or selected-Board ownership boundaries.
- Source limitations: some vectors share only the early generic Research dispatch and may separate under technical triage.
- Triage priority hints: widespread rediscovery; routing/authority/recovery relevance.

### C008 — Explicit Brainstorming stop is checked too late behind downstream stages

- Similarity classification: SAME CLASS
- Independently reported by: 6 source audits
- Source findings: S003-F04, S010-F04, S015-F01, S020-F01, S029-F02, S033-F01.
- Affected contracts/invariants reported by sources: BRAINSTORMING explicit stop; USER_STOP; ROUTER human-boundary precedence.
- Shared core claim: validator-legal downstream Definition/Planning/Board state can return before the Brainstorming explicit_user_stop check.
- Distinct reproduction vectors: promoted+GREEN Definition routes Planning; approved plan+live Board routes Execution; active Definition route.
- Important disagreements between sources: none; this cluster excludes Research-early-return variants placed in C007.
- Existing reproduction artifacts: source-local promoted-Brainstorm stop fixture scripts.
- Why sources considered it material/load-bearing: a durable explicit human stop is a top-precedence agency boundary.
- Source limitations: mostly source-mechanical route-order proofs.
- Triage priority hints: independent rediscovery; human-authority/routing relevance.

### C009 — JIT lifecycle is not tied to routing/terminal completeness

- Similarity classification: OVERLAPPING / NEEDS TRIAGE
- Independently reported by: 8 source audits
- Source findings: S002-F04, S004-F04, S020-F06, S022-F04, S024-F06, S026-F02, S027-F01, S034-F01.
- Affected contracts/invariants reported by sources: EXECUTION_PREP JIT waiting/satisfied/consumed; STATE Task Board; CLOSE end-of-approved-scope.
- Shared core claim: selector terminality ignores JIT state; additionally consumed may lack proof of downstream materialization.
- Distinct reproduction vectors: satisfied trigger + all Cards DONE -> Close; consumed trigger with no downstream Card -> Close; no consumed-by binding.
- Important disagreements between sources: several other auditors retained the same JIT/Close interaction only as non-blocking because Close could theoretically bounce back; only promoted findings are counted here. Consumed-proof may be a separate defect from satisfied-trigger dispatch.
- Existing reproduction artifacts: multiple JIT fixture scripts in source reports.
- Why sources considered it material/load-bearing: authorized predecessor-dependent work can disappear or reach Close before materialization.
- Source limitations: ownership boundary between Router and Close is the main triage uncertainty.
- Triage priority hints: strong rediscovery; Task Board/finalization relevance.

### C010 — Nonterminal Card status can override an already durable result and replay work

- Similarity classification: OVERLAPPING / NEEDS TRIAGE
- Independently reported by: 6 source audits
- Source findings: S008-F03, S009-F03, S016-F03, S023-F04, S025-F03, S028-F04.
- Affected contracts/invariants reported by sources: STATE durable result recovery truth; EXECUTION/RECOVERY no-replay.
- Shared core claim: result reconciliation is status-gated to in_progress while validators permit results on READY/blocked/planned states.
- Distinct reproduction vectors: READY+result -> Execution Prep; blocked+result+bounded correction -> Execution; planned+result noted as sibling.
- Important disagreements between sources: READY and blocked vectors may require separate fixes despite sharing the same state-coherence root.
- Existing reproduction artifacts: READY/blocked fixture scripts retained in source reports.
- Why sources considered it material/load-bearing: replay can duplicate code or external effects despite durable completion evidence.
- Source limitations: mostly source/control-flow analyses.
- Triage priority hints: independent rediscovery; recovery/execution relevance.

### C011 — Approved Planning is not bound to current Definition revision/authority

- Similarity classification: SAME CLASS
- Independently reported by: 5 source audits
- Source findings: S010-F02, S020-F03, S026-F04, S029-F04, S031-F02.
- Affected contracts/invariants reported by sources: DEFINITION current authority; PLANNING entry/premium cycle; PLAN_REVIEW.
- Shared core claim: a self-consistent old Planning/Plan Review/premium chain remains executable after current Definition revision or requirements authority changes.
- Distinct reproduction vectors: Definition R1 -> R2 with stale R1 plan; change requirements locator while retaining approved plan; live Board still routes Execution.
- Important disagreements between sources: none material; exact entry-subject serialization is not the claim.
- Existing reproduction artifacts: stale-Definition Planning scripts in source reports.
- Why sources considered it material/load-bearing: execution may proceed under superseded product authority and stale premium approvals.
- Source limitations: source reports note that the exact string format of entry_subject is not itself prescribed.
- Triage priority hints: independent rediscovery; planning/authority relevance.

### C012 — SessionStart accepts marker-preserving semantically destroyed router

- Similarity classification: SAME CLASS
- Independently reported by: 6 source audits
- Source findings: S002-F07, S004-F05, S007-F05, S012-F06, S021-F04, S026-F06.
- Affected contracts/invariants reported by sources: SessionStart/Skill fail-closed bootstrap; installed canonical router authority.
- Shared core claim: two sentinel substrings are treated as sufficient router integrity, so truncated/counterfeit/stale policy can be advertised as canonical.
- Distinct reproduction vectors: two-line router; marker-preserving corrupted body; arbitrary contradictory text retaining markers.
- Important disagreements between sources: several other auditors explicitly did not promote this under their reading of installed-package trust; promoted reports specifically target semantic destruction while markers survive.
- Existing reproduction artifacts: temporary-package hook repros, some executed.
- Why sources considered it material/load-bearing: bootstrap can positively assert canonical policy while the actual semantic body is absent/corrupt.
- Source limitations: package-integrity mechanism is not equally interpreted by all sources.
- Triage priority hints: independent rediscovery; bootstrap/authority relevance.

### C013 — Card Result acceptance validates shape rather than semantic success/exactness

- Similarity classification: OVERLAPPING / NEEDS TRIAGE
- Independently reported by: 4 source audits
- Source findings: S007-F03, S016-F05, S024-F05, S031-F03.
- Affected contracts/invariants reported by sources: EXECUTION accepted semantic result; STATE durable result as recovery truth.
- Shared core claim: parse/consume boundary accepts non-empty fields without proving successful tests/readback, exact implementation identity, or evidence validity.
- Distinct reproduction vectors: Tests/readback summary explicitly FAILED; Implementation subject = banana; nonexistent evidence plus otherwise valid shape.
- Important disagreements between sources: these are distinct missing semantic predicates and may split under triage; evidence-existence overlap with C003 is retained in the ledger.
- Existing reproduction artifacts: parser/router scripts, with at least some parser cases executed in isolation.
- Why sources considered it material/load-bearing: failed/malformed output can become no-replay completion truth.
- Source limitations: overlap with C001/C003 requires later technical boundary decisions.
- Triage priority hints: independent rediscovery; execution/recovery relevance.

### C014 — Lexical locator validation is not preserved through filesystem resolution

- Similarity classification: OVERLAPPING / NEEDS TRIAGE
- Independently reported by: 2 source audits
- Source findings: S009-F06, S018-F04.
- Affected contracts/invariants reported by sources: AUTHORITY/WORKSTREAM class confinement; traversal/cross-workstream fail-closed rule.
- Shared core claim: a path can pass lexical class/workstream checks then resolve differently under host filesystem semantics while staying under broad project root.
- Distinct reproduction vectors: Windows backslash traversal; in-repository symlink escaping declared semantic root.
- Important disagreements between sources: mechanisms and platform scope differ; likely separate implementation fixes.
- Existing reproduction artifacts: repro_windows_locator.py; repro_symlink_locator.py.
- Why sources considered it material/load-bearing: wrong-class or cross-workstream content can masquerade as canonical authority.
- Source limitations: Windows impact is platform-conditional; symlink vector was locally exercised by its source.
- Triage priority hints: two-source overlap; concrete path reproductions; authority/path-safety relevance.

### C015 — Malformed TOML parse errors escape selector Recovery

- Similarity classification: UNIQUE
- Independently reported by: 1 source audit
- Source finding: S002-F01.
- Affected contracts/invariants reported by source: malformed durable state must fail closed to Recovery.
- Shared core claim: TOMLDecodeError is not caught by selector state-read exception boundaries.
- Distinct reproduction vector: replace TASK_BOARD.toml or another selector-read TOML with syntax such as revision = [.
- Existing reproduction artifacts: no persisted script; complete minimal mutation is in the source finding.
- Why source considered it material/load-bearing: corrupted/partial durable state hands authority back to runtime exception behavior.
- Source limitations: direct source/exception-boundary reasoning, no fresh selector run.
- Triage priority hints: static/direct counterexample; recovery relevance.

### C016 — Plan Review in_progress is accepted and then misclassified as RED

- Similarity classification: UNIQUE
- Independently reported by: 1 source audit
- Source finding: S003-F03.
- Affected contracts/invariants reported by source: Plan Review verdict domain and Planning/Review precedence.
- Shared core claim: shared validator admits in_progress, while router handles pending/green then treats the remaining accepted value as RED.
- Distinct reproduction vector: valid frozen Plan Review changed to in_progress with no terminal evidence.
- Existing reproduction artifact: repros/router_counterexamples.py F3.
- Why source considered it material/load-bearing: an unfinished review gains correction authority as if RED evidence existed.
- Source limitations: repro preserved but not executed in-source.
- Triage priority hints: executable counterexample; review/planning relevance.

### C017 — Close recovery package can be certified from an empty caller-declared artifact set

- Similarity classification: UNIQUE
- Independently reported by: 1 source audit
- Source finding: S005-F04.
- Affected contracts/invariants reported by source: CLOSE mandatory target-side recovery package before destructive source-ref cleanup.
- Shared core claim: verifier checks only caller-supplied required minus present sets; empty/empty can certify source-ref-independent recovery.
- Distinct reproduction vector: matching heads + immutable merge evidence true + empty required/present sets, then safe_to_delete -> delete_exact_ref.
- Existing reproduction artifact: repros/f4_empty_close_recovery_package.py.
- Why source considered it material/load-bearing: source ref can be deleted without proving any mandatory recovery artifacts.
- Source limitations: script preserved but not executed in-source.
- Triage priority hints: concrete helper counterexample; Close/recovery relevance.

### C018 — Definition can bind a Brainstorm revision whose lifecycle is not promoted

- Similarity classification: UNIQUE
- Independently reported by: 1 source audit
- Source finding: S012-F04.
- Affected contracts/invariants reported by source: BRAINSTORMING promotion lifecycle; DEFINITION exact promoted source.
- Shared core claim: cross-record check proves promotion authorization/subject but not brainstorm.state=promoted.
- Distinct reproduction vector: normal GREEN Definition fixture with Brainstorm state changed promoted -> active while promotion authorization remains exact.
- Existing reproduction artifact: repros/repro_router_state_gaps.py F4.
- Why source considered it material/load-bearing: downstream Definition can exist while upstream owner still says scope is active.
- Source limitations: preserved selector repro not executed.
- Triage priority hints: lifecycle/authority relevance.

### C019 — Active execution trusts Card existence rather than the stable Task Card contract

- Similarity classification: UNIQUE
- Independently reported by: 1 source audit
- Source finding: S008-F04.
- Affected contracts/invariants reported by source: EXECUTION_PREP stable Card contract; EXECUTION recovery; ROUTER fail-closed binding.
- Shared core claim: active/no-result branch checks only that Card file exists and routes Execution without parse_task_card.
- Distinct reproduction vector: stock active fixture routes Execution while parse_task_card rejects the same file for missing stable fields.
- Existing reproduction artifact: repro_router_semantic_holes.py F4.
- Why source considered it material/load-bearing: recovered mutation can continue without bounded scope, authority, acceptance, tests or review requirement.
- Source limitations: source points to existing fixture expectation as evidence; fresh probe unavailable.
- Triage priority hints: fixture/executable contradiction; execution/authority relevance.

### C020 — Documented Close to end_of_scope_stop transition is disconnected from production selector

- Similarity classification: UNIQUE
- Independently reported by: 1 source audit
- Source finding: S017-F04.
- Affected contracts/invariants reported by source: ROUTER Close/end-of-scope semantics; CLOSE true-end helper; USER_STOP.
- Shared core claim: all-DONE selector returns route/close repeatedly and has no input/path consuming close_continuation into a real stop.
- Distinct reproduction vector: call select_route twice on unchanged all-DONE state; call close_continuation separately and observe end_of_scope_stop.
- Existing reproduction artifact: repros/repro_findings.py F04.
- Why source considered it material/load-bearing: manual/runtime logic may become hidden authority over workflow termination.
- Source limitations: source confidence is high-to-moderate because module separation may be intentional.
- Triage priority hints: helper-router parity claim; finalization relevance.

### C021 — Pre-repair issue diagnosis is converted into alignment stop before a repair subject exists

- Similarity classification: UNIQUE
- Independently reported by: 1 source audit
- Source finding: S021-F01.
- Affected contracts/invariants reported by source: INTAKE diagnosis-before-alignment lifecycle.
- Shared core claim: issue + pending alignment + no response routes a human stop even when repair_subject is empty.
- Distinct reproduction vector: active issue Intake with repair_subject="", response_kind=none, alignment_state=pending.
- Existing reproduction artifact: repros/f1_pre_repair_issue_stop.py.
- Why source considered it material/load-bearing: a legal diagnosis continuation is rejected and a human gate is fabricated before a repair proposal exists.
- Source limitations: script preserved for exact checkout.
- Triage priority hints: Intake/human-boundary relevance.

### C022 — Intake diagnosis-prior-art proof is an unauthenticated non-empty string

- Similarity classification: SAME CLASS
- Independently reported by: 2 source audits
- Source findings: S021-F02, S032-F04.
- Affected contracts/invariants reported by sources: INTAKE mandatory issue prior-art; RESEARCH consumed/applied result provenance.
- Shared core claim: matching prior-art subject plus any non-empty diagnosis_prior_art_result is treated as completed proof without binding to an actual Research result.
- Distinct reproduction vectors: forged:never-produced / forged-no-research strings with no qualifying Research record.
- Important disagreements between sources: none.
- Existing reproduction artifacts: f2_forged_prior_art_binding.py and f4_forged_prior_art_binding.py.
- Why sources considered it material/load-bearing: mandatory prior-art can be bypassed before repair implementation.
- Source limitations: execution constraints noted by sources.
- Triage priority hints: independent rediscovery; Intake/authorization relevance.

### C023 — editorial_exempt Planning review exemption is content-blind/self-attested

- Similarity classification: UNIQUE
- Independently reported by: 1 source audit
- Source finding: S023-F03.
- Affected contracts/invariants reported by source: PLANNING/PLAN_REVIEW material-change exception.
- Shared core claim: changed plan can claim editorial_exempt based on metadata and any non-empty basis; old/new plan semantics are not compared.
- Distinct reproduction vector: new blob + retained old reviewed base/B/C + wording-only prose basis.
- Existing reproduction artifact: repros/repro_counterexamples.py.
- Why source considered it material/load-bearing: a material strategy change could suppress mandatory Plan Review/premium replay.
- Source limitations: source rates high-to-moderate because editorial classification inherently needs semantic judgment not represented in schema.
- Triage priority hints: planning/review parity relevance.

### C024 — RECOMMENDED review lacks durable activation state and is always blocking

- Similarity classification: UNIQUE
- Independently reported by: 1 source audit
- Source finding: S025-F04.
- Affected contracts/invariants reported by source: REVIEW rule that RECOMMENDED blocks only when activated.
- Shared core claim: schema carries none|required|recommended but no activation bit/record; router treats all non-none as blocking.
- Distinct reproduction vector: result-bearing Card with Review requirement: recommended and no attempt -> review_freeze.
- Existing reproduction artifact: repros/router_counterexamples.py F4.
- Why source considered it material/load-bearing: documented legal unactivated recommendation cannot be represented.
- Source limitations: source-level state/document parity claim.
- Triage priority hints: documentation/executable parity; review lifecycle relevance.

### C025 — Close review reuse treats acceptance-surface shrink as unchanged coverage

- Similarity classification: UNIQUE
- Independently reported by: 1 source audit
- Source finding: S026-F05.
- Affected contracts/invariants reported by source: CLOSE final review reuse and exact acceptance surface.
- Shared core claim: current acceptance subset of reviewed acceptance is treated as reusable GREEN when fingerprints/compatibility match.
- Distinct reproduction vector: reviewed {A,B,C}; current {A,B}; same content/behavior + compatibility GREEN -> reuse_green_review.
- Existing reproduction artifact: repros/repro_close_acceptance_shrink.py.
- Why source considered it material/load-bearing: finalization can reuse review frozen against a different acceptance contract.
- Source limitations: repository test reportedly asserts the subset behavior, making this a policy/semantics triage point.
- Triage priority hints: Close/review relevance; explicit parity dispute.

### C026 — Terminal implementation review attempts can be rewritten in place

- Similarity classification: UNIQUE
- Independently reported by: 1 source audit
- Source finding: S028-F05.
- Affected contracts/invariants reported by source: REVIEW append-only attempt history.
- Shared core claim: Board stores attempt path only; current-state validator cannot prove terminal attempt immutability across history.
- Distinct reproduction vector: R01 RED -> rewrite same file/path/ID to GREEN -> correction route becomes finalization.
- Existing reproduction artifact: repros/repro_findings.py F5.
- Why source considered it material/load-bearing: failed review history can be semantically erased without a new append-only attempt.
- Source limitations: preserved repro not executed.
- Triage priority hints: review/recovery integrity relevance.

### C027 — Human-authority blocker can coexist with in_progress and be ignored

- Similarity classification: UNIQUE
- Independently reported by: 1 source audit
- Source finding: S030-F04.
- Affected contracts/invariants reported by source: STATE Card/blocker coherence; RECOVERY human-authority blocker.
- Shared core claim: validator enforces blocked -> blocker but not blocker -> blocked; active branch can route Execution without reading an attached human-authority blocker.
- Distinct reproduction vector: keep Card in_progress, attach valid human_authority blocker, route.
- Existing reproduction artifact: repros/adversarial_repros.py F4.
- Why source considered it material/load-bearing: partially written contradictory state can cross a human authority boundary.
- Source limitations: direct branch-order reasoning; repro preserved.
- Triage priority hints: human-authority/recovery relevance.

## Unique candidate findings

Unique classes are C015, C016, C017, C018, C019, C020, C021, C023, C024, C025, C026 and C027. Each remains in the report irrespective of frequency. The full source-finding ledger below contains the original expected/actual/reproduction/materiality details required for later triage.

## Cross-audit coverage

This matrix uses only explicit source metadata, selected lenses, stated coverage, or material finding subjects. NO/UNKNOWN means no explicit focused evidence was found; it is not inferred from silence.

| Coverage area | YES / explicit focused evidence | PARTIAL / adjacent explicit evidence | NO/UNKNOWN |
|---|---|---|---|
| Router precedence / conflicting obligations | S001,S002,S006,S007,S008,S009,S010,S013,S015,S018,S027,S032,S033 | S014,S020,S024,S025,S026,S030 | others |
| Malformed / contradictory state | S006,S008,S009,S016,S018,S020,S021,S022,S024,S027,S028 | S002,S003,S012,S023,S025,S030,S033 | others |
| Stale identity/blob/path/result/review | S002,S005,S011,S012,S013,S014,S015,S016,S022,S024,S025,S028,S029,S030,S031,S032,S033,S034 | S001,S003,S004,S006,S007,S008,S009,S010,S017,S018,S019,S020,S023,S026,S027 | S021 |
| Review lifecycle / bypass | S004,S006,S009,S014,S017,S019,S020,S022,S028,S029,S032 | S002,S003,S007,S011,S012,S013,S015,S016,S018,S024,S026,S027,S033,S034 | others |
| RED / recovery / blocker continuation | S003,S005,S010,S012,S015,S023,S025,S029,S030 | S002,S008,S011,S014,S016,S017,S020,S022,S024,S028,S033 | others |
| Task Board / READY / DONE / JIT | S004,S022,S027,S028,S033,S034 | S002,S008,S009,S011,S015,S016,S020,S023,S024,S025,S026,S030 | others |
| Planning / Premium / Execution | S001,S003,S008,S010,S012,S020,S023,S026,S029,S030,S031 | S005,S007,S015,S017,S024,S033 | others |
| Close / finalization / end-of-scope | S001,S003,S004,S005,S014,S016,S017,S021,S025,S026,S030,S034 | S002,S011,S012,S020,S022,S023,S024,S027,S033 | others |
| Research / Intake / tracker / external-effect | S005,S007,S010,S011,S013,S014,S017,S019,S020,S021,S024,S032 | S001,S006,S008,S012,S015,S025,S026,S027,S030 | others |
| Plugin / bootstrap / update | S002,S004,S007,S008,S012,S019,S021,S023,S026,S031,S033 | S005,S020 | others |
| Path / locator safety | S003,S006,S009,S011,S017,S018,S019 | S002,S005,S013,S014,S015,S024,S025,S028,S030,S032 | others |
| Documentation / executable parity | S001,S007,S011,S013,S015,S016,S018,S023,S024,S025,S026,S027,S031,S034 | S008,S012,S017,S020,S029 | others |
| Negative-space / sibling cases | Explicitly described across S001-S034 | Depth varies; see source limitations in ledger | none inferred |

## Finding-frequency distribution

| Independent source audits per candidate class | Number of candidate classes |
|---:|---:|
| 1 | 12 |
| 2 | 2 |
| 3 | 1 |
| 4+ | 12 |

There are 15 candidate classes independently reported by at least two sources. Frequency is not proof of validity.

## CLEAN audit coverage

No valid included source audit returned CLEAN. All 34 included source audits returned FINDINGS FOUND. Therefore no CLEAN-depth comparison exists; source inspection/execution/limitations are preserved in the ledger.

## Full source-finding ledger

Every original material finding from every included audit is represented below. The source report remains authoritative for its exact wording and any nuance not reproduced verbatim here.

