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


## S001 — audit/pwv2-swarm-11j9refnjjr4zgst7rm39sz9

### S001-F01 — READY dependency identity is metadata-only; mutated result content still launches

- Source branch: `audit/pwv2-swarm-11j9refnjjr4zgst7rm39sz9`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: Close / finalization / end-of-approved-scope; helper vs documented semantics / parity drift / negative space; Planning / Premium gates / Execution precedence; router precedence / unreachable branches / conflicting obligations

- Affected workflow contract/invariant: `workflow/EXECUTION_PREP.md` and `workflow/STATE.md` require each predecessor dependency to be bound as result path + immutable commit/blob identity and launch refresh to fail closed when that exact dependency is stale.
- Expected behavior: before a READY Card launches, the current dependency artifact must actually match the declared immutable blob/commit identity of the DONE predecessor. A same-path content mutation must fail closed.
- Actual behavior: `tools/router.py::refresh_ready_card` compares the dependency tuple only against the tuple stored on the DONE predecessor in `TASK_BOARD.toml`, then merely reads the dependency path. It never checks the current file's Git blob (or commit) against the declared identity. If both Card and Board retain the same stale tuple while the file contents change, launch refresh succeeds.
- Minimal reproduction: a DONE predecessor and READY successor both declare `results/M01-T01.md@aaaaaaaa...:bbbbbbbb...`; replace the result file contents without changing either metadata tuple. The production refresh logic accepts the dependency although the actual Git blob SHA is `411155663101521e759cf7b78a635350d2577962`, not `bbbb...`.
- Why this is materially load-bearing: downstream execution can consume a different predecessor result than the one its stable Card contract authorized, defeating immutable dependency binding and allowing stale/mutated state to pass a launch gate.
- Defect class / likely siblings: stale blob/commit/path identity; any refresh that checks locator metadata equality but does not bind it to repository object identity is suspect.
- Existing tests that failed to catch it: `test_ready_card_stale_dependency_fails_closed_before_launch` changes the Board result commit/blob tuple as well as the file, so it proves tuple mismatch detection, not actual blob verification when metadata remains unchanged.
- Reproduction artifact, if any: `repros/F1_dependency_blob_not_verified.py`.

### S001-F02 — Card Result evidence references are accepted even when the evidence artifact does not exist

- Source branch: `audit/pwv2-swarm-11j9refnjjr4zgst7rm39sz9`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: Close / finalization / end-of-approved-scope; helper vs documented semantics / parity drift / negative space; Planning / Premium gates / Execution precedence; router precedence / unreachable branches / conflicting obligations

- Affected workflow contract/invariant: `workflow/EXECUTION.md` requires Main to validate returned implementation/evidence before normalizing an accepted semantic result; an accepted result must contain durable evidence refs.
- Expected behavior: a Card Result whose required evidence ref is missing/unreadable must fail closed before `result_reconciliation`, review freeze, or terminal finalization.
- Actual behavior: `tools/execution_contract.py::parse_card_result` validates only the syntax/prefix of `Evidence refs`. In the active-Card result path, `tools/router.py` reads the result file and Card contract but never reads any referenced evidence artifacts. A syntactically valid path to `.../evidence/DOES-NOT-EXIST.md` is accepted.
- Minimal reproduction: parse a valid Card Result with `Evidence refs: implementation/workstreams/sample-workstream/evidence/DOES-NOT-EXIST.md` while no such file exists. The production parser returns that ref successfully; the router contains no subsequent evidence read before result reconciliation/review routing.
- Why this is materially load-bearing: workflow state can treat an implementation as an accepted durable semantic result without the durable evidence the result contract says is required, permitting review/finalization to proceed on nonexistent proof.
- Defect class / likely siblings: negative-space durability validation; locators are syntax-validated but not dereferenced at the acceptance boundary. Review evidence locators deserve similar scrutiny.
- Existing tests that failed to catch it: result-routing tests create the referenced evidence file before routing; there is no negative case deleting/omitting the evidence while retaining the same Card Result.
- Reproduction artifact, if any: `repros/F2_missing_result_evidence.py`.

### S001-F03 — Research routing preempts higher-precedence explicit/premium stops

- Source branch: `audit/pwv2-swarm-11j9refnjjr4zgst7rm39sz9`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: Close / finalization / end-of-approved-scope; helper vs documented semantics / parity drift / negative space; Planning / Premium gates / Execution precedence; router precedence / unreachable branches / conflicting obligations

- Affected workflow contract/invariant: `tools/router.py::PRIORITY_FOUNDATION` declares `explicit_human_or_premium_boundary` above `research_return`; `workflow/ROUTER.md` likewise defines explicit user/premium gates as real stops.
- Expected behavior: if a durable explicit user stop or due premium gate coexists with a Research obligation, the higher-precedence stop must win; if the combination is semantically contradictory, routing must fail closed rather than silently bypass the stop.
- Actual behavior: `select_route` loads `workstream.research` immediately after the manifest and returns for `active` or `complete` Research before it loads Brainstorming, Definition, Planning, or Plan Review. Therefore `brainstorm.explicit_user_stop = true`, premium A due, premium B due, or premium C due can be unreachable while Research is active/complete. The validators do not reject these cross-record combinations.
- Minimal reproduction: valid Research with `state = "active"`, `origin_role = "brainstorming"`, and a valid Brainstorm record with `explicit_user_stop = true`. Both records pass their individual validators; router control flow returns `route/research` before reading the explicit stop. The same ordering preempts later premium checks.
- Why this is materially load-bearing: the selector can continue work after an explicit human boundary or required premium boundary that its own precedence table says must dominate, violating deterministic authorization/stop semantics.
- Defect class / likely siblings: router precedence drift between declared precedence and executable ordering; especially early-return modules that run before higher-priority records are loaded.
- Existing tests that failed to catch it: tests cover Research routing and premium-stop routing separately and assert the precedence constant, but no interaction test combines Research with an explicit/premium boundary. There is no `explicit_user_stop = true` router case in the exact test file.
- Reproduction artifact, if any: `repros/F3_research_preempts_stop.py`.

#### S001 source coverage

Audit subject remained bound to commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`. I inspected canonical `workflow/ROUTER.md`, `CLOSE.md`, `PLANNING.md`, `PLAN_REVIEW.md`, `EXECUTION.md`, `EXECUTION_PREP.md`, and `STATE.md`; production `tools/router.py`, `close_contract.py`, `execution_contract.py`, `recovery_contract.py`, and relevant portions of `state_contract.py`; and exact-commit router tests around READY dependency refresh, Research, premium gates, result reconciliation, and Close. The four selected attack lenses were exercised: Close/finalization, helper-vs-documentation negative space, Planning/Premium/Execution precedence, and router precedence.

Executable falsification was performed with isolated reproductions copied from the exact production functions/order: F1 demonstrated acceptance of a dependency file whose actual Git blob differs from the declared blob; F2 demonstrated acceptance of a nonexistent evidence ref; F3 demonstrated the executable early-return ordering that selects Research before explicit-stop evaluation. Existing test coverage was inspected at the same immutable commit rather than moving `main`.

#### S001 original confidence and limitations

Confidence is high for F1 and F2 because the relevant production checks are local and the counterexamples directly exercise the exact acceptance logic. Confidence is high for F3 because both the declared precedence and executable early-return ordering are explicit and the state validators lack a cross-record exclusion for the counterexample.

A full checkout/test-suite execution was not available in the local container because outbound Git access is disabled, and the authorized Remote Desktop Commander had exhausted its monthly usage quota. I therefore used exact-commit GitHub reads plus isolated executable reproductions of the relevant production functions/order. No historical `audit/*` branch, swarm report, Issue, PR comment, or historical implementation evidence/review was inspected before freezing these findings.


## S002 — audit/pwv2-swarm-1m24f9qan3e4kmlfif0xw93w

### S002-F01 — Malformed TOML escapes Recovery and crashes the selector

- Source branch: `audit/pwv2-swarm-1m24f9qan3e4kmlfif0xw93w`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: stale commit/blob/path/result/review identity; Close / finalization / end-of-approved-scope; router precedence / unreachable branches / conflicting obligations; plugin / install / update / SessionStart / bootstrap drift

- Affected workflow contract/invariant: Invalid, missing, stale or contradictory durable state must fail closed to Recovery. The router is supposed to return a deterministic Recovery obligation rather than let malformed durable state become runtime behavior.
- Expected behavior: Syntax-corrupt TOML in PROJECT/workstream/pre-execution/Task Board/review state should produce `recovery / recovery_boundary`.
- Actual behavior: `read_toml()` and `read_project()` use `tomllib`, whose syntax failures raise `tomllib.TOMLDecodeError`. The main `select_route()` exception boundaries catch `OSError`, `ValidationError` and `KeyError`, but not `TOMLDecodeError`. The parse exception therefore escapes the selector.
- Minimal reproduction: Copy the normal router fixture, replace `TASK_BOARD.toml` with syntactically invalid TOML such as `revision = [`, then call `select_route(...)`. `tomllib.TOMLDecodeError` escapes instead of returning a Recovery `RouteResult`. The same defect class applies to malformed WORKSTREAM, planning, review and other TOML read through the selector.
- Why this is materially load-bearing: A partially written or corrupted durable state file destroys deterministic fail-closed recovery and hands control back to runtime/harness exception behavior.
- Defect class / likely siblings: Every selector-side `read_toml()`/`read_project()` parse site whose surrounding exception boundary omits `tomllib.TOMLDecodeError`.
- Existing tests that failed to catch it: Router tests cover semantically invalid bindings and missing state, but not syntactically malformed TOML. `state_contract.py`'s CLI does explicitly catch `tomllib.TOMLDecodeError`, making the selector/helper behavior inconsistent.
- Reproduction artifact, if any: none persisted; reproduction is direct from the production exception boundary.

### S002-F02 — Result Git identity is declarative only and permits stale/unreviewed content

- Source branch: `audit/pwv2-swarm-1m24f9qan3e4kmlfif0xw93w`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: stale commit/blob/path/result/review identity; Close / finalization / end-of-approved-scope; router precedence / unreachable branches / conflicting obligations; plugin / install / update / SessionStart / bootstrap drift

- Affected workflow contract/invariant: A durable Card result and review subject must bind exact immutable repository/commit/path/blob identity. Changed result content must not reuse a prior exact review.
- Expected behavior: The selector must verify that the result artifact being consumed is the exact object named by its commit/blob binding. Same-path content drift must fail closed or require a new review subject.
- Actual behavior: `validate_locator(..., "result", ...)` accepts a result locator with no `commit`/`blob` at all when both keys are omitted. When identity fields are present it validates only their 40-hex syntax. The router reads the current result path but never verifies its bytes against the claimed blob/commit. `exact_result_subject()` simply concatenates the locator's claimed strings. Consequently a result file can change in place while its locator and GREEN review remain unchanged, and the router still treats the old review as covering the current result.
- Minimal reproduction: Start with an active review-required Card whose result locator names commit A/blob B and whose GREEN attempt covers A/path/B. Change the result file contents at that same path without changing the Board locator or review TOML. Keep the result syntactically parseable. `select_route()` still reaches `post_review_finalization`. A no-review active result can additionally omit commit/blob completely and still reach `result_reconciliation`.
- Why this is materially load-bearing: Unreviewed result content can inherit a GREEN verdict for different bytes, defeating exact-subject review/recovery semantics.
- Defect class / likely siblings: Claimed immutable Git identities are syntactically checked rather than dereferenced/hashed. Dependency and planning identities deserve the same negative-space scrutiny.
- Existing tests that failed to catch it: `test_changed_result_after_terminal_review_requires_new_attempt` changes the locator blob itself. `test_ready_card_stale_dependency_fails_closed_before_launch` changes the Board's declared predecessor identity. Neither mutates bytes while leaving the claimed exact identity unchanged.
- Reproduction artifact, if any: none persisted; minimal state mutation is described above.

### S002-F03 — DONE fast path can bypass result/review validity and enter Close

- Source branch: `audit/pwv2-swarm-1m24f9qan3e4kmlfif0xw93w`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: stale commit/blob/path/result/review identity; Close / finalization / end-of-approved-scope; router precedence / unreachable branches / conflicting obligations; plugin / install / update / SessionStart / bootstrap drift

- Affected workflow contract/invariant: REQUIRED/activated RECOMMENDED review pending/in-progress/RED blocks terminal Card completion; invalid/missing result/review state must fail closed. Close must not be reached merely because mutable Board status says `done`.
- Expected behavior: Before a Card is accepted as terminal, its durable result and blocking review state must be consistent with terminal completion.
- Actual behavior: `validate_board()` requires a `done` Card only to contain a syntactically valid result locator. It does not read the result, Card contract or attempts and does not prove review completion. Once no active/blocked/ready Cards remain, the router checks only `all(card["status"] == "done")` and routes directly to Close without loading those artifacts.
- Minimal reproduction: Build a review-required Card with a durable result and a pending or RED review attempt, then mutate Board status to `done`. Alternatively delete the referenced result file after marking the Card `done`. The Board still validates structurally and the selector reaches `route / close` without reading the blocking/missing artifacts.
- Why this is materially load-bearing: Mutable status can bypass the independent-review gate and move malformed work into final integration/closure ownership.
- Defect class / likely siblings: Terminal-status trust without semantic terminal-state validation; missing/stale result files and unresolved review attempts share the same fast path.
- Existing tests that failed to catch it: `test_all_terminal_cards_route_to_close_not_directly_to_stop` exercises a Card whose review requirement is `none`; there is no negative terminal-state test with REQUIRED review pending/RED or a missing result artifact.
- Reproduction artifact, if any: none persisted; minimal state mutation is described above.

### S002-F04 — JIT-trigger lifecycle is ignored by routing and can lose approved downstream scope

- Source branch: `audit/pwv2-swarm-1m24f9qan3e4kmlfif0xw93w`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: stale commit/blob/path/result/review identity; Close / finalization / end-of-approved-scope; router precedence / unreachable branches / conflicting obligations; plugin / install / update / SessionStart / bootstrap drift

- Affected workflow contract/invariant: Predecessor-dependent downstream work remains a Task Board JIT trigger until its stable Card becomes knowable. A `satisfied` trigger means downstream materialization is now due; `consumed` must represent successful consumption rather than disappearance of scope. End-of-scope/Close must not preempt an already-authorized downstream obligation.
- Expected behavior: A satisfied JIT trigger with a DONE predecessor should route to Execution Prep for downstream Card materialization. A trigger must not become `consumed` without durable evidence that its downstream Card contract was materialized.
- Actual behavior: `validate_board()` checks only that `satisfied` or `consumed` triggers name a DONE predecessor with a result. It does not bind `consumed` to any downstream Card. `select_route()` does not inspect `jit_triggers` at all. Therefore a Board whose existing Cards are all DONE and which contains a `satisfied` trigger routes to Close; a trigger may also be marked `consumed` with no downstream Card and produce the same result.
- Minimal reproduction: Create one DONE predecessor Card with a result and add a JIT trigger `after_card=<that Card>, state="satisfied"`. Leave no active/ready downstream Card. The Board validates, then the router reaches the all-DONE branch and selects Close instead of Execution Prep. Changing the trigger to `consumed` with no materialized downstream Card is also accepted.
- Why this is materially load-bearing: Accepted downstream scope can disappear from deterministic routing and the workstream can enter finalization prematurely.
- Defect class / likely siblings: Task Board JIT state is validated locally but never participates in selector precedence/terminal completeness; `consumed` has no durable downstream binding.
- Existing tests that failed to catch it: `test_jit_trigger_preserves_predecessor_boundary_without_placeholder_card` validates `waiting` and `satisfied` schema state but never routes it. Router tests contain JIT refinement classification tests but no JIT-trigger lifecycle/Close interaction.
- Reproduction artifact, if any: none persisted; minimal state mutation is described above.

### S002-F05 — GREEN review can finalize without durable evidence or exact current acceptance binding

- Source branch: `audit/pwv2-swarm-1m24f9qan3e4kmlfif0xw93w`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: stale commit/blob/path/result/review identity; Close / finalization / end-of-approved-scope; router precedence / unreachable branches / conflicting obligations; plugin / install / update / SessionStart / bootstrap drift

- Affected workflow contract/invariant: Terminal review attempts require durable verdict evidence and bind the exact current acceptance surface of the Card.
- Expected behavior: GREEN finalization should require the referenced evidence to exist and the review acceptance identity to match the active Card's exact acceptance contract.
- Actual behavior: `validate_review()` requires a terminal `evidence_path` only to be a non-empty safe relative string; neither the validator nor the router reads that path. A nonexistent evidence file therefore satisfies the review gate. For task-card acceptance, validation checks only that the path is inside the workstream's cards directory and its basename stem equals `card_id`; the router does not compare it to `card["contract"]["path"]` and does not read the acceptance artifact identified by the review.
- Minimal reproduction: Use a review-required active Card/result and a GREEN review whose result subject matches but whose `evidence_path` points to a nonexistent file. `select_route()` still reaches `post_review_finalization`. As a sibling, point review acceptance at `cards/archive/M01-T04.md` while the Board's actual contract is `cards/M01-T04.md`; the same Card-ID stem is enough for validation even if the acceptance path is absent or different.
- Why this is materially load-bearing: An exact independent review gate can become a self-declared GREEN flag with no durable verdict evidence and potentially no binding to the actual acceptance contract being finalized.
- Defect class / likely siblings: Undereferenced review locators; Plan Review terminal evidence uses the same non-empty-path-only pattern.
- Existing tests that failed to catch it: Review tests prove only that terminal `evidence_path` is non-empty. Router fixtures happen to create an evidence file, but no test removes it or varies acceptance independently from the active Card contract.
- Reproduction artifact, if any: none persisted; minimal state mutation is described above.

### S002-F06 — Task-Board Research can route to a fabricated/stale Card subject

- Source branch: `audit/pwv2-swarm-1m24f9qan3e4kmlfif0xw93w`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: stale commit/blob/path/result/review identity; Close / finalization / end-of-approved-scope; router precedence / unreachable branches / conflicting obligations; plugin / install / update / SessionStart / bootstrap drift

- Affected workflow contract/invariant: Implementation/recovery Research must be owned by the selected Task Board with an exact origin and return owner; recovery must resume the exact durable Card obligation rather than an unrelated/fabricated subject.
- Expected behavior: Board-owned Research origin/return subject must be coherent and bound to an existing applicable Card on that Board.
- Actual behavior: `validate_research()` requires only a non-empty `origin_subject` and a prefix-shaped execution return target. The Board-specific handler verifies that `origin_role` is an implementation/recovery role but does not require the return-target suffix to equal `origin_subject`, does not require either value to name a Board Card, and does not require the Card to be the applicable current/blocked Card.
- Minimal reproduction: Point the Board at completed Research with `origin_role="execution_resolution"`, `origin_subject="M01-T04"` and `return_target="execution_resolution:PHANTOM"`. Validation succeeds and the router selects `execution_resolution` with subject `PHANTOM`.
- Why this is materially load-bearing: Corrupt/stale Research state can redirect recovery or execution ownership away from the actual Card rather than fail closed.
- Defect class / likely siblings: Missing origin/return/card coherence validation in Research bindings.
- Existing tests that failed to catch it: `test_task_board_research_return_is_recovered_before_execution` exercises only matching `M01-T04` origin/return subjects and does not include mismatched/nonexistent Card cases.
- Reproduction artifact, if any: none persisted; minimal state mutation is described above.

### S002-F07 — SessionStart accepts a sentinel-preserving truncated router as valid

- Source branch: `audit/pwv2-swarm-1m24f9qan3e4kmlfif0xw93w`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: stale commit/blob/path/result/review identity; Close / finalization / end-of-approved-scope; router precedence / unreachable branches / conflicting obligations; plugin / install / update / SessionStart / bootstrap drift

- Affected workflow contract/invariant: The installed Codex bootstrap must fail closed when its canonical router is missing or malformed. Missing workflow policy must not be reconstructed from runtime/chat state.
- Expected behavior: A truncated router lacking the actual routing contract should produce the blocking plugin-package error.
- Actual behavior: `hooks/session-start.py::canonical_router()` considers a router valid if the file exists inside the package root and contains two substrings: `# Project Workflow V2 Router` and `Production selector: \`tools/router.py\`.`. It performs no stronger structural/integrity validation.
- Minimal reproduction: Replace installed `workflow/ROUTER.md` with only the expected header and selector sentinel. The two sentinels pass `canonical_router()` and `build_context()` reports `Project Workflow V2 package is enabled` rather than a blocking package error.
- Why this is materially load-bearing: SessionStart can certify an installation whose canonical workflow semantics are effectively absent, undermining the package's fail-closed bootstrap boundary.
- Defect class / likely siblings: Sentinel-presence validation used as policy-integrity validation; partial/truncated install/update states containing both markers are accepted.
- Existing tests that failed to catch it: `test_missing_and_malformed_router_fail_closed` uses `not a V2 router`, which removes both sentinels. No test preserves the sentinels while deleting the semantic body.
- Reproduction artifact, if any: none persisted; the two-line replacement is the complete reproducer.

#### S002 source coverage

The audit remained bound to repository `elmakus/project_workflow_v2` commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`.

Inspected canonical/product surfaces included `workflow/ROUTER.md`, `workflow/STATE.md`, `workflow/PLANNING.md`, `workflow/EXECUTION_PREP.md`, `workflow/EXECUTION.md`, `workflow/REVIEW.md`, `workflow/RECOVERY.md`, `workflow/CLOSE.md`, `workflow/USER_STOP.md`, `tools/router.py`, `tools/state_contract.py`, `tools/execution_contract.py`, `tools/recovery_contract.py`, `tools/close_contract.py`, router/state/Close/ChatGPT/Codex delivery tests, package manifests, Skill/SessionStart hook and ChatGPT bootstrap templates.

Selected attack lenses exercised:

1. stale commit/blob/path/result/review identity — result and review binding paths;
2. Close/finalization/end-of-approved-scope — DONE fast path, JIT terminal interaction and Close helpers;
3. router precedence/conflicting obligations — Task Board Research, review/finalization, JIT and pre-execution/Board dispatch;
4. plugin/install/update/SessionStart/bootstrap drift — installed-root, router validation, Skill/hook and delivery tests.

No `audit/*` branches, other swarm reports, GitHub Issues or PR comments were inspected before freezing the finding set.

#### S002 original confidence and limitations

Confidence is high for the source-level counterexamples because each follows a direct accepted validation/routing path in the exact audited code.

Full execution of newly invented selector probes could not be completed in the available remote runtime: the connected Desktop Commander host had exhausted its monthly execution quota. Findings therefore rely on exact-commit source/contract falsification plus limited local exception-class reasoning rather than an executed fresh clone.

During immutable-commit verification, the GitHub commit connector returned the merge commit's diff, including snippets from historical implementation evidence/review paths. Those unsolicited snippets were not used as an audit checklist and did not supply any of the seven findings. The independent finding set was frozen before any optional historical comparison.


## S003 — audit/pwv2-swarm-1nf66pps8yiv44rk65rdcv5g

### S003-F01 — Immutable Git identities are trusted as declarations instead of verified against repository content

- Source branch: `audit/pwv2-swarm-1nf66pps8yiv44rk65rdcv5g`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: RED / recovery / blocker / interrupted-runtime continuation; path traversal / locator safety / cross-workstream binding; Planning / Premium gates / Execution precedence; Close / finalization / end-of-approved-scope

- Affected workflow contract/invariant: exact immutable result/dependency/review/plan identities; READY launch refresh; review subject refresh; fail-closed stale binding.
- Expected behavior: whenever a durable locator claims `path + commit + blob`, the selector must establish that the claimed commit contains that path at that blob (and, where current worktree content is being consumed, that the consumed artifact is the exact claimed subject). A same-path content change under an unchanged stale locator must fail closed before launch/finalization.
- Actual behavior: `validate_locator` and `_git_blob_subject_key` validate only shape/40-hex syntax. `refresh_ready_card` compares Card dependency tuples only to Board-declared tuples, then reads the current file without hashing it. Active-result review refresh similarly builds `current_subject` only from Board-declared commit/blob and compares that string to the review record; it parses the current result file but never proves those bytes equal the declared blob. Consequently, materially changing a reviewed result file while leaving the Board locator unchanged still reaches `post_review_finalization`. The same trust model also affects declared Planning Git subjects.
- Minimal reproduction: run `python3 audits/swarm/1nf66pps8yiv44rk65rdcv5g/repros/router_counterexamples.py F1`. It creates a REQUIRED-review result, records GREEN against the declared exact subject, then changes the result bytes without changing the Board `commit/blob`; the production selector still returns `route/post_review_finalization`.
- Why this is materially load-bearing: immutable Git identity is the core anti-staleness boundary for recovery and independent review. If identity is not checked against Git content, a stale or contradictory durable locator can authorize finalization of bytes that were never reviewed.
- Defect class / likely siblings: declarative Git-identity trust without object verification. Confirmed code paths include active Card result/review and READY dependency refresh; Planning subject validation uses the same syntax-only pattern and is a likely sibling.
- Existing tests that failed to catch it: `test_changed_result_after_terminal_review_requires_new_attempt` changes the Board blob itself, and `test_ready_card_stale_dependency_fails_closed_before_launch` changes the Board commit/blob tuple as well as the file. Neither mutates artifact bytes while leaving the claimed immutable locator stale.
- Reproduction artifact, if any: `repros/router_counterexamples.py` (F1).

### S003-F02 — A `done` Card can bypass REQUIRED review and force Close

- Source branch: `audit/pwv2-swarm-1nf66pps8yiv44rk65rdcv5g`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: RED / recovery / blocker / interrupted-runtime continuation; path traversal / locator safety / cross-workstream binding; Planning / Premium gates / Execution precedence; Close / finalization / end-of-approved-scope

- Affected workflow contract/invariant: REQUIRED/activated RECOMMENDED review must block terminal Card completion until exact GREEN; Close only follows legally terminal Cards.
- Expected behavior: a Card whose stable contract requires review cannot be accepted as `done` unless its exact current result has a valid GREEN attempt. Contradictory `done` state must fail closed rather than advance to Close.
- Actual behavior: `validate_board` requires only that a `done` Card have a result locator. It does not parse the Card review requirement, validate its result subject, or require a GREEN attempt. The router then returns `route/close` whenever all Cards are `done`, without revalidating result/review terminality. A REQUIRED-review Card with no attempt (or stale/RED history) can therefore be made terminal by Board status alone.
- Minimal reproduction: run `python3 audits/swarm/1nf66pps8yiv44rk65rdcv5g/repros/router_counterexamples.py F2`. It creates a REQUIRED-review result with no review attempt, changes only Card status to `done`, and the production selector returns `route/close`.
- Why this is materially load-bearing: Board corruption, interrupted reconciliation, or an incorrect writer can bypass the independent-review safety gate and enter final integration/closure.
- Defect class / likely siblings: terminal-state validation that trusts lifecycle status without reconstructing the terminal proof it semantically implies.
- Existing tests that failed to catch it: `test_all_terminal_cards_route_to_close_not_directly_to_stop` uses `Review requirement: none`; there is no negative all-DONE case for REQUIRED/RECOMMENDED review or RED/stale review history.
- Reproduction artifact, if any: `repros/router_counterexamples.py` (F2).

### S003-F03 — Plan Review `in_progress` is accepted and misclassified as RED

- Source branch: `audit/pwv2-swarm-1nf66pps8yiv44rk65rdcv5g`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: RED / recovery / blocker / interrupted-runtime continuation; path traversal / locator safety / cross-workstream binding; Planning / Premium gates / Execution precedence; Close / finalization / end-of-approved-scope

- Affected workflow contract/invariant: Plan Review attempt lifecycle and deterministic Planning/Review precedence.
- Expected behavior: canonical `workflow/PLAN_REVIEW.md` defines Plan Review verdicts as `pending / green / red`. An `in_progress` Plan Review record is therefore contradictory and should fail closed (or be normalized by an explicitly documented lifecycle before routing), never be treated as RED.
- Actual behavior: the shared `validate_review` accepts `in_progress`, and `validate_plan_review` does not narrow that set. In the frozen-plan router branch, only `pending` and `green` are handled explicitly; every other accepted value takes the unconditional RED return to Planning. Thus a syntactically valid `in_progress` Plan Review is routed as if RED evidence existed.
- Minimal reproduction: run `python3 audits/swarm/1nf66pps8yiv44rk65rdcv5g/repros/router_counterexamples.py F3`. It changes an otherwise valid pending Plan Review to `in_progress` with no terminal evidence; the production selector returns `route/planning` with the RED-correction reason.
- Why this is materially load-bearing: an unfinished independent review can be converted into correction authority, bypassing the actual review obligation and fabricating a RED semantic transition.
- Defect class / likely siblings: shared-validator state widening combined with router fall-through that assumes the remaining value is a specific terminal verdict.
- Existing tests that failed to catch it: `test_plan_review_must_match_frozen_subject_and_terminal_evidence` covers pending and GREEN but not `in_progress`; router tests contain no `plan_review_content("in_progress")` case.
- Reproduction artifact, if any: `repros/router_counterexamples.py` (F3).

### S003-F04 — A durable explicit Brainstorming user stop is bypassed by downstream Definition state

- Source branch: `audit/pwv2-swarm-1nf66pps8yiv44rk65rdcv5g`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: RED / recovery / blocker / interrupted-runtime continuation; path traversal / locator safety / cross-workstream binding; Planning / Premium gates / Execution precedence; Close / finalization / end-of-approved-scope

- Affected workflow contract/invariant: explicit human stop precedence; contradictory state must fail closed; runtime/router priority foundation places explicit human boundaries first.
- Expected behavior: `explicit_user_stop = true` is a real stop. If combined with already-promoted/downstream state, the router must either honor the stop before deterministic continuation or reject the contradiction to Recovery.
- Actual behavior: `validate_brainstorm` permits `state = "promoted"`, exact promotion authorization, and `explicit_user_stop = true` simultaneously. The router loads that record but evaluates Definition/Planning first and can return from those branches before reaching the later explicit-user-stop check. With a GREEN Definition and satisfied A, it returns `route/planning`, silently bypassing the durable user stop.
- Minimal reproduction: run `python3 audits/swarm/1nf66pps8yiv44rk65rdcv5g/repros/router_counterexamples.py F4`. It installs the valid promoted+GREEN Definition fixture, flips only `explicit_user_stop` to true, and the production selector still returns `route/planning`.
- Why this is materially load-bearing: an explicit human stop is one of the workflow's highest-precedence authority boundaries. Allowing downstream state to override it violates human control and makes contradictory recovery state fail open.
- Defect class / likely siblings: high-precedence stop state validated independently but checked only after lower-precedence early returns.
- Existing tests that failed to catch it: Brainstorming/Definition router fixtures set `explicit_user_stop = false`; there is no promoted/downstream state case with the flag true.
- Reproduction artifact, if any: `repros/router_counterexamples.py` (F4).

#### S003 source coverage

The audit remained bound to commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`. It inspected canonical routing/state/Planning/Plan Review/Recovery/Execution Prep/Execution/Close/Brainstorming/Research/workstream contracts, the approved requirements, production selector and state/recovery/execution/close helpers, and targeted existing router/state tests.

The selected attack lenses were exercised as follows:
- RED/recovery/blocker/interrupted continuation: reviewed durable result recovery, review refresh, blocker classification, and Task-Board Research return paths; F1 is directly recovery/review-reuse relevant.
- path/locator safety/cross-workstream binding: inspected `Reads._read_path`, `_safe_relative_path`, workstream-local locator validation, result/dependency binding, and negative-path tests; F1 exposes identity verification beyond lexical path safety.
- Planning/Premium/Execution precedence: traced A/B/Plan Review/C and co-bound Board precedence; F3 and F4 are precedence/state-domain failures.
- Close/finalization: traced DONE terminal routing and Close helpers; F2 demonstrates a review-gate bypass into Close.

Existing passing tests were treated as evidence of covered positive cases, not proof against the negative-space counterexamples above.

#### S003 original confidence and limitations

Confidence is high in the four code-path counterexamples because each follows accepted validator states directly through the production selector and contradicts an explicit canonical invariant. A runnable non-mutating reproduction script is preserved for each case.

The audit environment could not execute the repository Python suite: the local container could not resolve GitHub for cloning, the connected Desktop Commander device had exhausted its monthly execution allowance, and no valid outer-Codex execution token was available. Therefore the reproduction script was not executed in this chat; actual routes are derived from the exact production source at the immutable subject and the existing fixture/helper semantics.

A GitHub commit-metadata request unexpectedly returned the merge diff, which included historical evidence/review text for the router-board-precedence hotfix before this finding set was frozen. No `audit/*` branch or swarm report was inspected, no GitHub Issues/PR-comment defect search was performed, and the exposed hotfix narrative was not used to derive or modify F1-F4. No post-freeze historical comparison was performed.


## S004 — audit/pwv2-swarm-45ulo91hciq37ytbao10h4wv

### S004-F01 — Router trusts declared Git-blob metadata instead of the reviewed bytes

- Source branch: `audit/pwv2-swarm-45ulo91hciq37ytbao10h4wv`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: plugin / install / update / SessionStart / bootstrap drift; Close / finalization / end-of-approved-scope; review independence / review bypass / result mutation; Task Board / READY / active / DONE / JIT-trigger lifecycle

- Affected workflow contract/invariant: `workflow/REVIEW.md` exact immutable Git content subject; `workflow/STATE.md` exact-current-result review/finalization and recovery truth.
- Expected behavior: if the bytes at the current Card result change after the GREEN attempt was frozen, the old review must not authorize finalization. The current result must be proven to be the declared immutable `path + commit + blob` subject, otherwise a new attempt or Recovery is required.
- Actual behavior: `tools/router.py` reads the current filesystem result text and parses it, but computes `current_subject` only from the Board-declared result locator through `exact_result_subject()`. Neither the router nor `parse_card_result()` verifies the actual result bytes against the declared blob/commit. A post-review content mutation with unchanged Board/review metadata therefore still reaches `post_review_finalization`.
- Minimal reproduction: `repros/f1_result_blob_mutation.py` first binds Board and GREEN review metadata to the Git-blob SHA of the original result bytes, then mutates the result file without changing those locators. The production control path still compares the two unchanged declarations and selects finalization.
- Why this is materially load-bearing: an exact-subject independent review can be reused for bytes it never reviewed, defeating the integrity boundary between durable result, review, and terminal Card completion.
- Defect class / likely siblings: declared immutable identities are treated as self-authenticating metadata. The same class is relevant to frozen/approved planning subjects because Plan Review compares declared Git identities rather than re-hashing or reading the exact Git object.
- Existing tests that failed to catch it: router stale-result tests mutate the Board `blob` field and therefore exercise metadata mismatch, not same-locator content mutation.
- Reproduction artifact, if any: `repros/f1_result_blob_mutation.py`.

### S004-F02 — Terminal review evidence is neither bound to the workstream nor dereferenced

- Source branch: `audit/pwv2-swarm-45ulo91hciq37ytbao10h4wv`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: plugin / install / update / SessionStart / bootstrap drift; Close / finalization / end-of-approved-scope; review independence / review bypass / result mutation; Task Board / READY / active / DONE / JIT-trigger lifecycle

- Affected workflow contract/invariant: `workflow/REVIEW.md` requires durable verdict evidence for terminal attempts; `workflow/STATE.md` makes terminal review history part of the exact blocking gate.
- Expected behavior: GREEN/RED terminal evidence must identify an allowed durable evidence artifact that actually exists; missing or unrelated evidence must fail closed and cannot authorize post-review finalization.
- Actual behavior: `validate_review()` requires only a non-empty safe-relative `evidence_path` for GREEN/RED. It does not require the path to be workstream-local and the router never reads that path. A GREEN review whose evidence is changed to a nonexistent `ghost-review-evidence.md` remains valid and reaches `post_review_finalization`.
- Minimal reproduction: create the existing required-review fixture and GREEN attempt, replace only its evidence path with `ghost-review-evidence.md`, then run `select_route()`; the review TOML still validates and GREEN remains finalizable.
- Why this is materially load-bearing: durable evidence is the audit trail for the independent verdict. A terminal gate can currently be satisfied by an arbitrary string naming no artifact at all.
- Defect class / likely siblings: non-empty locator syntax is accepted without existence/binding verification. Card-result evidence refs are similarly parsed as workstream-local strings without being dereferenced by `parse_card_result()`.
- Existing tests that failed to catch it: `test_review_terminal_evidence_and_append_only_history` rejects only an empty terminal evidence path; it does not test nonexistent or out-of-workstream paths.
- Reproduction artifact, if any: `repros/f2_review_evidence_missing.py`.

### S004-F03 — `done` Board state bypasses REQUIRED review and RED correction

- Source branch: `audit/pwv2-swarm-45ulo91hciq37ytbao10h4wv`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: plugin / install / update / SessionStart / bootstrap drift; Close / finalization / end-of-approved-scope; review independence / review bypass / result mutation; Task Board / READY / active / DONE / JIT-trigger lifecycle

- Affected workflow contract/invariant: `workflow/REVIEW.md` blocking lifecycle; `workflow/STATE.md` requires no-attempt/pending/in-progress/RED to block terminal completion and only exact GREEN to permit deterministic finalization.
- Expected behavior: a Card marked `done` while a REQUIRED review is absent, pending, in-progress, or RED is contradictory durable state and must fail closed (or be routed back to the unresolved review/correction owner), never proceed to Close.
- Actual behavior: `validate_board()` requires a `done` Card only to have a result locator. It does not read the stable Task Card or review history. When no Card is active/READY/blocked, `tools/router.py` routes an all-`done` Board directly to `close`, without reading the Card, result, or review attempts. Thus both `done + pending REQUIRED review` and `done + RED REQUIRED review` bypass their blocking gates.
- Minimal reproduction: materialize a required-review result and pending/RED attempt with existing test helpers, change only Card status from `in_progress` to `done`, then select a route. The all-terminal branch selects `route/close`.
- Why this is materially load-bearing: a single Board status mutation can erase the precedence of independent review or RED correction and prematurely enter final integration/closure.
- Defect class / likely siblings: cross-record state invariants are enforced only while a Card is `in_progress`; terminal status is trusted without proving the prerequisites that make it legal.
- Existing tests that failed to catch it: `test_all_terminal_cards_route_to_close_not_directly_to_stop` deliberately uses a Card whose review requirement is `none`; required-review terminal contradictions are not covered.
- Reproduction artifact, if any: `repros/f3_done_bypasses_review.py`.

### S004-F04 — A satisfied JIT trigger is ignored when current Cards are DONE

- Source branch: `audit/pwv2-swarm-45ulo91hciq37ytbao10h4wv`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: plugin / install / update / SessionStart / bootstrap drift; Close / finalization / end-of-approved-scope; review independence / review bypass / result mutation; Task Board / READY / active / DONE / JIT-trigger lifecycle

- Affected workflow contract/invariant: `workflow/EXECUTION_PREP.md` JIT lifecycle (`waiting -> satisfied -> consumed`) and the rule that a satisfied predecessor-dependent trigger materializes the newly knowable downstream Card; `workflow/CLOSE.md` forbids completion while an already-authorized obligation remains.
- Expected behavior: once a JIT trigger is `satisfied` by its DONE predecessor/result, the router must keep Execution Prep/JIT materialization ahead of Close until that trigger is consumed into the downstream stable Card.
- Actual behavior: `validate_board()` accepts a `satisfied` trigger when its predecessor is DONE with a result, but the selector never consults `jit_triggers` after validation. With all current Cards `done`, the router takes the all-terminal branch and returns `route/close` even though a satisfied, unconsumed JIT obligation remains.
- Minimal reproduction: make the fixture Card `done` with a durable result and append a `satisfied` trigger whose `after_card` is that Card. Board validation succeeds; route selection reaches Close.
- Why this is materially load-bearing: approved predecessor-dependent work can disappear from executable routing exactly when its contract becomes knowable, allowing premature Close/end-of-scope reconciliation.
- Defect class / likely siblings: Task Board trigger state is validated structurally but absent from obligation precedence/selection.
- Existing tests that failed to catch it: the state-contract trigger test checks that `satisfied` requires a DONE predecessor result, but there is no router test asserting that a satisfied trigger preempts Close.
- Reproduction artifact, if any: `repros/f4_satisfied_jit_routes_close.py`.

### S004-F05 — SessionStart accepts a marker-preserving truncated router as canonical authority

- Source branch: `audit/pwv2-swarm-45ulo91hciq37ytbao10h4wv`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: plugin / install / update / SessionStart / bootstrap drift; Close / finalization / end-of-approved-scope; review independence / review bypass / result mutation; Task Board / READY / active / DONE / JIT-trigger lifecycle

- Affected workflow contract/invariant: `skills/project_workflow_v2/SKILL.md` requires missing, malformed, ambiguous, or escaping installed router authority to fail closed; the SessionStart hook is the thin Codex bootstrap for bundled canonical semantics.
- Expected behavior: an installed `workflow/ROUTER.md` that has lost its routing semantics must be classified malformed and emit the blocking package-error context rather than advertise valid workflow authority.
- Actual behavior: `canonical_router()` validates router content only by requiring two substrings: the router heading and `Production selector: tools/router.py`. A two-line file containing just those markers passes and `build_context()` says the package is enabled with a canonical bundled router.
- Minimal reproduction: replace only the temporary copied router with the two accepted marker lines and invoke the real hook with matching `PLUGIN_ROOT`; the non-blocking enabled context is emitted.
- Why this is materially load-bearing: silent package truncation/corruption can remove all routing precedence and safety semantics while the bootstrap explicitly tells the runtime that canonical authority is healthy.
- Defect class / likely siblings: integrity is inferred from sentinel presence rather than structural or manifest-bound package integrity.
- Existing tests that failed to catch it: `test_missing_and_malformed_router_fail_closed` uses `not a V2 router`, which removes both sentinels; marker-preserving corruption is not tested.
- Reproduction artifact, if any: `repros/f5_sessionstart_truncated_router.py`.

#### S004 source coverage

All repository reads used the immutable subject `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`. Inspection covered canonical router/state/review/execution-prep/Close contracts; production router, state, execution, review, recovery and Close helpers; Task Board and router fixtures; relevant router/state/Close/delivery tests; Codex plugin manifest/marketplace, Skill, SessionStart hook and bootstrap test; and ChatGPT bootstrap prompts/requirements needed for parity context.

The four selected attack lenses were all exercised: bootstrap integrity (F5), Close/end-of-scope interaction (F4), review/result integrity and bypass (F1-F3), and Task Board/JIT lifecycle (F3-F4). Negative-space tests were inspected specifically for same-locator mutation, nonexistent evidence, terminal contradictory review state, satisfied-trigger routing, and marker-preserving router corruption.

#### S004 original confidence and limitations

Confidence is high in the demonstrated control-flow defects because each counterexample follows production validation/selector branches directly and is preserved as a non-mutating repro script against existing test helpers. However, this audit environment could not execute the scripts: the local container could not resolve GitHub for checkout, and the authorized Desktop Commander reported its monthly quota exhausted and explicitly instructed not to retry. Existing tests were therefore inspected rather than rerun here.

Blind-discovery limitation: an exact-commit metadata fetch unexpectedly returned diff snippets that included historical workstream evidence/review text before the finding set was frozen. Those snippets were not used to generate, validate, add, remove, or rank any finding. No `audit/*` branch, swarm report, GitHub Issue/PR comment, or post-freeze historical comparison was inspected.


## S005 — audit/pwv2-swarm-4iwvszq379kizplu3lskirk4

### S005-F01 — Planning can approve a foreign or nonexistent frozen plan subject

- Source branch: `audit/pwv2-swarm-4iwvszq379kizplu3lskirk4`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: stale commit/blob/path/result/review identity; Close / finalization / end-of-approved-scope; RED / recovery / blocker / interrupted-runtime continuation; Research / Intake / tracker / external-side-effect recovery

- Affected workflow contract/invariant: Planning must freeze one exact immutable Git-blob plan subject, Plan Review must judge that exact subject, stale/wrong-project bindings must fail closed, and only the reviewed plan may reach premium C / Execution Prep.
- Expected behavior: the frozen planning subject must resolve to the selected project's repository and to the actual `plan_path` content at the declared commit/blob. A missing plan artifact or a subject whose repository differs from `PROJECT.md.repository` must route Recovery before B/review/C can be consumed.
- Actual behavior: `validate_planning()` validates only syntactic repository/path/40-hex fields and `subject.path == plan_path`; it receives no project repository and never resolves the Git object. `validate_plan_review()` only compares the review subject to the planning record. The router then trusts that internally consistent key. The repository's own router tests hard-code planning/review subjects as `owner/repo` while the fixture PROJECT declares `owner/router-fixture`, and they do not create `planning/MASTER_PLAN.md`; successful planning routes are still asserted.
- Minimal reproduction: copy `tests/fixtures/router/valid-project`; install the existing GREEN Definition fixture; install an approved planning record with A/B/C satisfied and subject `owner/repo@aaaaaaaa...:planning/MASTER_PLAN.md@bbbbbbbb...`; install a matching GREEN `PLAN_REVIEW.toml`; remove the Task Board locator so the next route is visible. Do not create `planning/MASTER_PLAN.md`. `select_route(...)` routes to `execution_prep` instead of Recovery even though PROJECT.repository is `owner/router-fixture` and the plan file is absent.
- Why this is materially load-bearing: Stage-6 review and premium gates can authorize execution from an artifact that is neither the selected project's plan nor even present. That defeats exact-subject review authority rather than merely weakening diagnostics.
- Defect class / likely siblings: unverified Git-subject locators; any gate that only compares self-declared repository/commit/path/blob tuples without resolving the object is suspect.
- Existing tests that failed to catch it: planning helpers in `tests/test_router.py` normalize the mismatch by generating `owner/repo` subjects against an `owner/router-fixture` project and by never materializing the plan file; planning-route tests still expect success.
- Reproduction artifact, if any: `repros/f1_foreign_nonexistent_plan.py`

### S005-F02 — Post-review result mutation is invisible when locator metadata is left unchanged

- Source branch: `audit/pwv2-swarm-4iwvszq379kizplu3lskirk4`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: stale commit/blob/path/result/review identity; Close / finalization / end-of-approved-scope; RED / recovery / blocker / interrupted-runtime continuation; Research / Intake / tracker / external-side-effect recovery

- Affected workflow contract/invariant: result locators and review attempts bind an immutable Git subject; GREEN may finalize only the exact still-current result; READY dependencies must match immutable predecessor result identity.
- Expected behavior: before result reconciliation/review finalization and before READY dependency launch, the declared commit/blob identity must be verified against the actual referenced object/content. Changing the result file after review must make the subject stale and require Recovery/new review.
- Actual behavior: `validate_locator(..., "result")` only checks that supplied commit/blob strings look like 40-hex. `refresh_ready_card()` compares dependency tuples copied from state and merely reads the path; it never checks the file's blob. Active-result routing parses current text but `exact_result_subject()` is built from the unchanged Task Board metadata. Therefore a syntactically valid result file can be materially changed after a GREEN review while board/result and review metadata retain the old tuple; the router still sees subject equality and returns `post_review_finalization`.
- Minimal reproduction: use the router fixture, install a REQUIRED reviewable result and GREEN attempt using the existing test helpers, then modify only `results/M01-T04.md` (for example change the implementation subject) while leaving the board `commit/blob` and review subject unchanged. `select_route(...)` still returns `route/post_review_finalization`.
- Why this is materially load-bearing: reviewed content can be replaced without invalidating GREEN. The same metadata-only comparison also lets a READY dependency file drift while its declared predecessor tuple remains unchanged.
- Defect class / likely siblings: claimed immutable identity is compared but never resolved/hashed. Planning subjects, result subjects, review subjects and dependency results should be audited for the same failure mode.
- Existing tests that failed to catch it: `test_changed_result_after_terminal_review_requires_new_attempt` changes the Task Board's declared blob, not the referenced file with metadata held constant. The result fixtures already use synthetic blob strings unrelated to file contents, so the suite does not prove object identity.
- Reproduction artifact, if any: `repros/f2_post_review_result_mutation.py`

### S005-F03 — Research origin and return ownership can contradict each other and route to another Card/owner

- Source branch: `audit/pwv2-swarm-4iwvszq379kizplu3lskirk4`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: stale commit/blob/path/result/review identity; Close / finalization / end-of-approved-scope; RED / recovery / blocker / interrupted-runtime continuation; Research / Intake / tracker / external-side-effect recovery

- Affected workflow contract/invariant: Research owns one exact origin subject and one exact return owner; it never selects a different target by itself. Recovery must return completed implementation Research to the exact originating obligation.
- Expected behavior: role/subject and return target must be cross-validated. Examples: `origin_role = intake` must return to `intake`; `origin_role = execution_resolution`, `origin_subject = M01-T04` must return to `execution_resolution:M01-T04`. Contradictory bindings must fail closed.
- Actual behavior: `validate_research()` validates `origin_role`, `origin_subject`, and `return_target` independently. The Task Board router checks only that the role is one of the execution roles and then trusts the target suffix. A complete record with origin `execution_resolution/M01-T04` and return target `execution_resolution:M99` validates and routes `execution_resolution` with subject `M99`. Likewise a top-level intake-origin Research record may name a different pre-execution return owner.
- Minimal reproduction: attach a Task-Board `research_obligation` for the sample workstream, set state complete, origin_role `execution_resolution`, origin_subject `M01-T04`, return_target `execution_resolution:M99`, with otherwise valid source accounting. `select_route(...)` routes to `execution_resolution` for `M99` instead of Recovery.
- Why this is materially load-bearing: stale or contradictory Research can redirect the deterministic recovery path away from the Card/owner that requested the facts, bypassing exact return ownership and potentially mutating the wrong durable state.
- Defect class / likely siblings: missing cross-field owner/subject invariants between origin and return references.
- Existing tests that failed to catch it: Research validator/router tests exercise only matching origin/return pairs and do not include cross-owner or cross-Card mismatches.
- Reproduction artifact, if any: `repros/f3_research_return_mismatch.py`

### S005-F04 — Close can certify source-ref-independent recovery with an empty recovery package

- Source branch: `audit/pwv2-swarm-4iwvszq379kizplu3lskirk4`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: stale commit/blob/path/result/review identity; Close / finalization / end-of-approved-scope; RED / recovery / blocker / interrupted-runtime continuation; Research / Intake / tracker / external-side-effect recovery

- Affected workflow contract/invariant: before final merge/cleanup, target-side recovery must contain the mandatory durable recovery package (workstream identity/provenance, selected board, stable Card contracts, required result/review/evidence and relevant checkpoint/handoff refs); source-branch deletion is allowed only after recovery is independent of that ref.
- Expected behavior: the Close verifier itself must reject a recovery claim that omits mandatory core artifact classes. An empty or caller-underdeclared required set cannot prove package completeness.
- Actual behavior: `verify_target_side_recovery()` checks only `required_artifacts - present_artifacts`, where both sets are entirely caller-supplied. With both empty, matching non-empty head labels and `immutable_merge_evidence=True`, it returns `source_ref_independent_recovery`. Feeding that conclusion into `cleanup_branch_action(... cleanup_state="safe_to_delete" ...)` permits `delete_exact_ref`.
- Minimal reproduction: call `verify_target_side_recovery(source_branch="feat/x", source_head="h", merged_source_head="h", target_package_subject_head="h", immutable_merge_evidence=True, required_artifacts=frozenset(), present_artifacts=frozenset())`; it returns success. Then call `cleanup_branch_action(terminal_package_independent=True, source_ref_exists=True, current_head="h", cleanup_state="safe_to_delete", verified_head="h")`; it returns `delete_exact_ref`.
- Why this is materially load-bearing: Close can authorize destructive source-ref cleanup without proving that any of the recovery artifacts mandated by the canonical Close contract are present, risking unrecoverable terminal state.
- Defect class / likely siblings: completeness delegated to unvalidated caller assertions instead of encoded mandatory invariants.
- Existing tests that failed to catch it: Close tests use caller-supplied non-empty sets and test subtraction/missing members, but never the empty/underdeclared mandatory-set case.
- Reproduction artifact, if any: `repros/f4_empty_close_recovery_package.py`

#### S005 source coverage

The audit remained bound to commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`. Before freezing findings, inspection was limited to permitted canonical/product surfaces: `workflow/ROUTER.md`, `AUTHORITY.md`, `STATE.md`, `PLANNING.md`, `PLAN_REVIEW.md`, `EXECUTION_PREP.md`, `EXECUTION.md`, `REVIEW.md`, `RECOVERY.md`, `RESEARCH.md`, `INTAKE.md`, `GITHUB_ISSUES.md`, `CLOSE.md`; production helpers `tools/router.py`, `state_contract.py`, `execution_contract.py`, `recovery_contract.py`, `close_contract.py`; relevant templates; router/state/close tests and fixtures; and CI test entry configuration.

Selected lens 3 was exercised against planning/result/review/dependency Git identity. Lens 8 was exercised against Close continuation, external-effect handling, target-side recovery and cleanup. Lens 5 was exercised against durable results, RED/review subject refresh, blocker precedence and implementation Research return. Lens 9 was exercised against Intake prior-art handling, Research return ownership, tracker recovery and external-effect recovery.

No `audit/*` branch, swarm report, GitHub Issue/PR defect discussion, or historical workstream evidence/review narrative was inspected before findings were frozen. No post-freeze historical comparison was performed.

#### S005 original confidence and limitations

Confidence is high for the four reported semantic paths because each follows directly from the exact production validators/selectors/helpers and is corroborated by the shape of existing tests. The current execution environment could read/write GitHub but did not provide a usable local checkout: the local container had no GitHub network access and the connected remote command service had exhausted its command quota. Therefore the preserved repro scripts were not executed in this session. They are non-mutating and import the production modules/fixtures directly so they can be run from the audited commit/branch without modifying product code.


## S006 — audit/pwv2-swarm-57c66ill1e5ntlgarmntge88

### S006-F01 — Declared result Git identity is never verified against the result bytes

- Source branch: `audit/pwv2-swarm-57c66ill1e5ntlgarmntge88`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: path traversal / locator safety / cross-workstream binding; malformed or contradictory state / fail-closed behavior; review independence / review bypass / result mutation; router precedence / unreachable branches / conflicting obligations

- Affected workflow contract/invariant: `workflow/STATE.md` READY dependency identity and durable-result recovery; `workflow/EXECUTION_PREP.md` launch refresh; `workflow/REVIEW.md` exact immutable review subject; PWV2-REQ-030/031/034/036.
- Expected behavior: A result/dependency locator carrying path + commit + blob must identify the bytes actually consumed. If the same path changes after review, or a dependency's bytes no longer match its immutable locator, routing must fail closed or freeze a new exact review subject before execution/finalization.
- Actual behavior: `tools/router.py` reads current result/dependency paths but never verifies the declared commit/blob against Git content. For an active reviewed Card, `current_subject` is built entirely from the Task Board locator. A result file can therefore be edited after GREEN while the Board locator and review attempt remain unchanged, and the selector still returns `route/post_review_finalization`. The same primitive exists in READY dependency refresh: tuple equality is checked only between Card text and Board metadata, then the current path is read without content-identity verification.
- Minimal reproduction: From the official router fixture, install a REQUIRED reviewable result and matching GREEN attempt; verify `post_review_finalization`; then edit only `results/M01-T04.md` while leaving the Board `commit/blob` and review subject unchanged. Calling the production selector again still yields `post_review_finalization`. Sibling: a READY Card whose dependency tuple still equals the DONE predecessor locator remains launchable after only the predecessor result file bytes are changed.
- Why this is materially load-bearing: Exact immutable subjects are the safety boundary that prevents stale review reuse and stale predecessor input. Self-asserted SHA fields without verification let changed content inherit prior GREEN/recovery authority.
- Defect class / likely siblings: Unverified immutable locator identity. Likely siblings include any path+commit+blob state that is compared as strings but consumed from the working tree without hashing/fetching the named Git object.
- Existing tests that failed to catch it: `test_changed_result_after_terminal_review_requires_new_attempt` changes the Board blob field rather than mutating bytes under an unchanged locator. `test_ready_card_stale_dependency_fails_closed_before_launch` changes both Board identity and file content rather than file content alone.
- Reproduction artifact, if any: `repros/repro_router_counterexamples.py --case F1`.

### S006-F02 — GREEN review acceptance is not bound to the selected Card's actual contract locator

- Source branch: `audit/pwv2-swarm-57c66ill1e5ntlgarmntge88`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: path traversal / locator safety / cross-workstream binding; malformed or contradictory state / fail-closed behavior; review independence / review bypass / result mutation; router precedence / unreachable branches / conflicting obligations

- Affected workflow contract/invariant: `workflow/REVIEW.md` exact acceptance surface; `workflow/STATE.md` review-attempt binding; PWV2-REQ-021/034/036.
- Expected behavior: An implementation review that permits finalization must cover the exact stable Task Card contract currently selected by the Task Board.
- Actual behavior: `validate_review()` accepts any workstream-local `cards/**/*.md` path whose filename stem equals `card_id`. `validate_review_history()` checks Card/workstream IDs, but `tools/router.py` never compares `review.acceptance.path` with `card.contract.path` and never reads the claimed acceptance artifact. A matching GREEN result review can therefore name a different or nonexistent nested Card path such as `cards/archive/M01-T04.md` and still route to `post_review_finalization`.
- Minimal reproduction: Install the official fixture's REQUIRED result and GREEN review, then change only the review acceptance path from the current `cards/M01-T04.md` to nonexistent `cards/archive/M01-T04.md`. Keep `card_id = "M01-T04"` and the exact result subject unchanged. The production selector accepts the attempt and finalizes.
- Why this is materially load-bearing: The review gate can be satisfied without reviewing the contract that defines current scope, acceptance and tests, bypassing the required exact acceptance surface.
- Defect class / likely siblings: Syntactic-locator validation substituted for referential binding. Plan/final review consumers should be checked for the same “valid-looking locator but wrong current authority” pattern.
- Existing tests that failed to catch it: `test_task_card_review_acceptance_is_exact_and_semantic` validates class/stem semantics but does not compare against a selected Board Card contract. `test_required_review_blocks_until_green_then_routes_finalization` always uses the matching current Card path.
- Reproduction artifact, if any: `repros/repro_router_counterexamples.py --case F2`.

### S006-F03 — Terminal review verdicts can finalize with missing or arbitrary evidence locators

- Source branch: `audit/pwv2-swarm-57c66ill1e5ntlgarmntge88`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: path traversal / locator safety / cross-workstream binding; malformed or contradictory state / fail-closed behavior; review independence / review bypass / result mutation; router precedence / unreachable branches / conflicting obligations

- Affected workflow contract/invariant: `workflow/REVIEW.md` durable terminal verdict evidence; `workflow/PLAN_REVIEW.md` terminal evidence locator; PWV2-REQ-034/036.
- Expected behavior: A terminal GREEN/RED attempt must have durable, readable evidence for that attempt before the verdict can authorize finalization/correction.
- Actual behavior: `validate_review()` requires terminal `evidence_path` to be merely non-empty and syntactically relative. It neither constrains implementation-review evidence to the workstream evidence root nor reads/verifies the target. `validate_plan_review()` repeats the same non-empty/path-safety check. The router never dereferences terminal review evidence before consuming GREEN.
- Minimal reproduction: Install a REQUIRED result and matching GREEN attempt, set `evidence_path` to `implementation/workstreams/sample-workstream/evidence/DOES-NOT-EXIST.md`, ensure that file does not exist, and run the production selector. It still returns `route/post_review_finalization`.
- Why this is materially load-bearing: Required review can become a bare verdict assertion with no durable evidence artifact, weakening recovery/audit truth exactly at the completion gate.
- Defect class / likely siblings: Existence/ownership validation missing from durable evidence locators. The same helper path affects Stage-6 Plan Review terminal evidence.
- Existing tests that failed to catch it: `test_review_terminal_evidence_and_append_only_history` rejects only an empty evidence string. The Plan Review test likewise checks empty versus non-empty, not existence or ownership.
- Reproduction artifact, if any: `repros/repro_router_counterexamples.py --case F3`.

### S006-F04 — Execution-origin Research can preempt the Task Board without Board ownership

- Source branch: `audit/pwv2-swarm-57c66ill1e5ntlgarmntge88`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: path traversal / locator safety / cross-workstream binding; malformed or contradictory state / fail-closed behavior; review independence / review bypass / result mutation; router precedence / unreachable branches / conflicting obligations

- Affected workflow contract/invariant: `workflow/RECOVERY.md` implementation/recovery Research ownership; `workflow/STATE.md` Task Board research obligation; router precedence/fail-closed owner binding.
- Expected behavior: Implementation/recovery Research exists only when the selected Task Board points to the exact `research_obligation`; otherwise an execution-origin Research record must not seize routing from the current Board/Card.
- Actual behavior: `validate_research()` permits execution origins/targets for any Workstream `[research]` locator. `tools/router.py` processes the Workstream research locator before reading the Task Board, and an `active` execution-origin record immediately returns `route/research`. No Board `research_obligation` pointer is required. The later Board-specific Research path does enforce execution ownership, so the two individually-valid mechanisms disagree when combined.
- Minimal reproduction: Starting from the official fixture with active Card `M01-T04`, add a Workstream `[research]` locator to an active `RESEARCH.toml` whose `origin_role = "execution_resolution"` and `return_target = "execution_resolution:M01-T04"`; do not add `task_board.research_obligation`. The selector returns `route/research` before reading the Board instead of failing closed or continuing the Board-owned obligation.
- Why this is materially load-bearing: A stale or contradictory manifest-level record can bypass the authoritative implementation owner and redirect the deterministic next obligation, defeating recovery precedence.
- Defect class / likely siblings: Cross-owner state accepted by a shared schema plus higher-precedence generic routing. Completed execution-origin Workstream Research also exposes an inconsistent path because the pre-execution owner map cannot resolve execution-prefixed return targets.
- Existing tests that failed to catch it: `test_active_and_completed_research_route_to_exact_owner` exercises manifest-level pre-execution Research only. `test_task_board_research_return_is_recovered_before_execution` exercises execution Research only when the Board pointer is present. No negative-space test combines execution-origin Research with a missing Board pointer.
- Reproduction artifact, if any: `repros/repro_router_counterexamples.py --case F4`.

#### S006 source coverage

The audit remained bound to `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045` for substantive inspection. It inspected the canonical router/state/authority/workstream, Research, Planning/Plan Review, Execution Prep/Execution, Review/Recovery and Close contracts; `tools/router.py`, `tools/state_contract.py`, `tools/execution_contract.py`, `tools/recovery_contract.py`, `tools/review_contract.py`, `tools/close_contract.py`; Task Card/Workstream/Task Board templates; exact router/state/execution/review/close tests and router fixtures.

All four selected attack lenses were exercised:
- path traversal / locator safety / cross-workstream binding: exact locator checks plus F2/F3 ownership gaps;
- malformed or contradictory state / fail-closed behavior: F1 and F4 negative-space states;
- review independence / review bypass / result mutation: F1-F3;
- router precedence / unreachable branches / conflicting obligations: F4 and the non-blocking JIT/Close interaction.

Existing tests were treated as hypotheses to attack rather than proof. No `audit/*` branch, swarm report, GitHub Issue/PR comment, or historical finding database was intentionally inspected before freezing the finding set. No post-freeze historical comparison was performed.

#### S006 original confidence and limitations

Confidence is high in the demonstrated control-flow defects because each finding follows a direct production-code path and has a preserved selector-level reproduction against the repository's own fixture/helpers. The current environment could not execute those reproductions against a local checkout: outbound Git from the local container was unavailable, and the connected remote desktop execution service had reached its usage limit. The reproduction script is therefore preserved but was not executed during this audit; this is the main limitation.

While resolving the immutable target commit, the GitHub connector unexpectedly expanded the merge commit response with its diff, including historical implementation/evidence/review paths that were outside the intended blind-read set. Those historical conclusions were not used to generate, add, remove, or prioritize the frozen findings above. Intentional inspection remained on the permitted canonical workflow/tools/tests/templates surfaces.

