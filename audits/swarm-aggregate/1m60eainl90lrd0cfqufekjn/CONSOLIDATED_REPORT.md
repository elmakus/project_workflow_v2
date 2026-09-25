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


## S007 — audit/pwv2-swarm-69f0g74xooo389jwdz456zmv

### S007-F01 — Immutable Git identities are trusted as strings instead of verified content identities

- Source branch: `audit/pwv2-swarm-69f0g74xooo389jwdz456zmv`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: 9. Research / Intake / tracker / external-side-effect recovery; 10. plugin / install / update / SessionStart / bootstrap drift; 1. router precedence / unreachable branches / conflicting obligations; 12. helper vs documented semantics / parity drift / negative space

- Affected workflow contract/invariant: workflow/STATE.md and workflow/EXECUTION_PREP.md require READY launch refresh to verify exact dependency result path + immutable commit/blob identity and explicitly require missing, stale, or same-path-changed dependency input to fail closed. Review/recovery semantics likewise require exact immutable result subjects.
- Expected behavior: Before a dependency, Card result, or frozen plan subject is trusted as the exact immutable object named by its durable locator, the implementation must verify that the bytes being consumed are actually the bytes identified by the recorded Git commit/blob.
- Actual behavior: tools/router.py refresh_ready_card() compares only the dependency's declared (path, commit, blob) tuple with the DONE predecessor's declared tuple and then reads the current path without resolving or hashing it. Active-Card result routing similarly parses the current file and constructs its review subject from the Board's declared metadata; tools/recovery_contract.py exact_result_subject() only formats those strings. Planning validation checks only that commit/blob fields are 40-hex. If both durable references retain the same stale metadata while the file bytes at the path change, the stale/tampered content remains accepted.
- Minimal reproduction: Start from the router fixture, add DONE M01-T03 with result metadata path=P, commit=A, blob=B, and make READY M01-T04 depend on exactly P@A:B. The route is execution_prep. Modify only the bytes at P, leaving both the Task Board and Card dependency tuple unchanged. select_route() still returns route/execution_prep instead of Recovery. The preserved reproduction script includes this exact case.
- Why this is materially load-bearing: A READY Card can execute against dependency content that is no longer the immutable predecessor result it declared. The same trust pattern can allow a changed Card-result file or plan artifact to remain associated with old review/freeze metadata, defeating stale-subject detection.
- Defect class / likely siblings: Declared-identity versus observed-content confusion. Confirmed code siblings are READY dependency refresh, active Card result/review subject recovery, and frozen Planning subject validation.
- Existing tests that failed to catch it: tests/test_router.py::test_ready_card_stale_dependency_fails_closed_before_launch changes the Board's commit/blob metadata at the same time it changes the result file. It therefore proves only that mismatching declared tuples fail; its initial accepted state already uses synthetic commit/blob values that are not verified against the fixture file bytes.
- Reproduction artifact, if any: repros/repro_router_semantic_gaps.py (case stale_dependency_bytes).

### S007-F02 — Active Research masks a durable explicit user stop

- Source branch: `audit/pwv2-swarm-69f0g74xooo389jwdz456zmv`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: 9. Research / Intake / tracker / external-side-effect recovery; 10. plugin / install / update / SessionStart / bootstrap drift; 1. router precedence / unreachable branches / conflicting obligations; 12. helper vs documented semantics / parity drift / negative space

- Affected workflow contract/invariant: tools/router.py PRIORITY_FOUNDATION places explicit human/premium boundaries above research return; workflow/BRAINSTORMING.md states that an explicit user stop is a real stop; workflow/ROUTER.md states that real stops must stop deterministic continuation.
- Expected behavior: If the current Brainstorming revision carries explicit_user_stop=true, the router must surface that real stop before continuing agent-owned Research work.
- Actual behavior: select_route() loads and immediately routes a workstream-level active RESEARCH.toml before it loads BRAINSTORM.toml or checks explicit_user_stop. The state validators permit an active Brainstorming record with explicit_user_stop=true and a simultaneous active Research record returning to brainstorming, so this is a representable durable state rather than a malformed-state-only path.
- Minimal reproduction: Add an active BRAINSTORM.toml with explicit_user_stop=true, then add an active RESEARCH.toml with origin_role=brainstorming, return_target=brainstorming, pending reconciliation, and all four required source classes accounted for. select_route() returns route/research instead of stop/explicit_user_stop.
- Why this is materially load-bearing: The workflow can continue autonomous factual work after the durable state says the user explicitly stopped the work. That violates the highest-precedence human boundary rather than merely choosing a suboptimal internal phase.
- Defect class / likely siblings: Higher-precedence stop shadowed by an earlier owner-specific early return. The exact demonstrated defect is Brainstorming explicit stop versus active Research; other boundaries should be checked for the same ordering pattern before repair.
- Existing tests that failed to catch it: Router tests cover active/completed Research and Brainstorming/promotion behavior separately, but do not compose active Research with explicit_user_stop=true to test precedence.
- Reproduction artifact, if any: repros/repro_router_semantic_gaps.py (case research_masks_user_stop).

### S007-F03 — Syntactically valid failed or unverified Card Results are treated as accepted completion evidence

- Source branch: `audit/pwv2-swarm-69f0g74xooo389jwdz456zmv`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: 9. Research / Intake / tracker / external-side-effect recovery; 10. plugin / install / update / SessionStart / bootstrap drift; 1. router precedence / unreachable branches / conflicting obligations; 12. helper vs documented semantics / parity drift / negative space

- Affected workflow contract/invariant: workflow/EXECUTION.md says only an acceptance/evidence-valid return is reconciled as one durable accepted result; incomplete or incorrect returns remain in_progress for correction. workflow/RECOVERY.md says only a valid durable semantic result prevents replay and drives review/finalization.
- Expected behavior: A Card result that reports failed tests/readback or names missing/unverified evidence must not be treated as accepted semantic completion. It should remain/correct execution or fail closed until acceptance evidence is valid.
- Actual behavior: tools/execution_contract.py parse_card_result() verifies field presence, Card ID, path syntax for evidence refs, and absence of runtime-identity fields, but it accepts any non-empty tests/readback summary, including FAILED, and never reads the named evidence files. tools/router.py treats any result that passes this parser as valid; with Review requirement: none it immediately routes result_reconciliation, and with review required it proceeds to review-freeze/review instead of correcting the failed implementation.
- Minimal reproduction: Give active M01-T04 a Board result locator and a parseable Card Result whose Tests/readback summary is FAILED and whose Evidence refs points to a workstream-local Markdown file that does not exist. With Review requirement: none, select_route() still returns route/result_reconciliation.
- Why this is materially load-bearing: Failed tests or absent verification evidence can be promoted into durable completion truth, allowing implementation work to stop and downstream finalization/review to proceed despite the execution contract explicitly classifying such returns as unaccepted.
- Defect class / likely siblings: Semantic-validity collapse into syntax-validity. The same parser gate feeds no-review reconciliation and review-required paths.
- Existing tests that failed to catch it: Execution-contract tests exercise GREEN-looking summaries, forbidden runtime identity, and cross-workstream evidence syntax. Router result tests create the referenced evidence and use a GREEN summary. There is no negative test for a failed summary or a syntactically valid but missing evidence artifact.
- Reproduction artifact, if any: repros/repro_router_semantic_gaps.py (case failed_result_is_accepted).

### S007-F04 — GREEN reviews are not bound to the actual current acceptance surface

- Source branch: `audit/pwv2-swarm-69f0g74xooo389jwdz456zmv`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: 9. Research / Intake / tracker / external-side-effect recovery; 10. plugin / install / update / SessionStart / bootstrap drift; 1. router precedence / unreachable branches / conflicting obligations; 12. helper vs documented semantics / parity drift / negative space

- Affected workflow contract/invariant: workflow/REVIEW.md requires each implementation review attempt to bind one exact acceptance surface, normally the stable Task Card. workflow/PLAN_REVIEW.md requires the frozen plan to be judged against its accepted Definition/requirements/decisions and planning acceptance surface.
- Expected behavior: A GREEN implementation review must be bound to the exact current Card contract/acceptance being finalized, and a GREEN Plan Review must be bound to the actual accepted Definition authority for that plan. A wrong, stale, or nonexistent acceptance target must fail closed.
- Actual behavior: validate_plan_review() receives Planning but not Definition and validates [acceptance] only as any syntactically allowed authority path; the path is not compared with Definition.requirements/decisions and is not dereferenced. Implementation validate_review() accepts any workstream-local task-card path whose filename stem equals card_id; the router does not compare that acceptance locator with the active Card's current contract locator or immutable content identity. The router then trusts the GREEN verdict.
- Minimal reproduction: Build a frozen plan with premium B satisfied and a matching GREEN PLAN_REVIEW.toml, but change its acceptance path from the current requirements authority to requirements/NOT_CURRENT.md and do not create that file. Validation still succeeds and select_route() returns Planning to consume GREEN rather than Recovery.
- Why this is materially load-bearing: Independent review is a blocking safety gate. If a verdict can be issued against different or nonexistent acceptance criteria, GREEN can authorize plan approval or Card finalization without proving the thing the current workflow actually requires.
- Defect class / likely siblings: Reviewed-subject identity is exact, but reviewed-acceptance identity is only class/path-shaped. Confirmed siblings are Stage-6 Plan Review and implementation Card review.
- Existing tests that failed to catch it: Tests cover wrong subject blobs, independence, evidence presence, and task-card filename/card_id consistency, but not equality to the current authoritative acceptance surface nor existence/immutability of the acceptance artifact.
- Reproduction artifact, if any: repros/repro_router_semantic_gaps.py (case wrong_plan_review_acceptance).

### S007-F05 — SessionStart accepts a semantically empty router if two sentinel strings survive

- Source branch: `audit/pwv2-swarm-69f0g74xooo389jwdz456zmv`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: 9. Research / Intake / tracker / external-side-effect recovery; 10. plugin / install / update / SessionStart / bootstrap drift; 1. router precedence / unreachable branches / conflicting obligations; 12. helper vs documented semantics / parity drift / negative space

- Affected workflow contract/invariant: skills/project_workflow_v2/SKILL.md requires the installed root/router to fail closed when missing, malformed, ambiguous, or escaping the package root. hooks/session-start.py describes itself as a thin fail-closed bootstrap.
- Expected behavior: A truncated, stale, or otherwise malformed installed workflow/ROUTER.md must produce the blocking package-error context rather than be advertised as the canonical router.
- Actual behavior: canonical_router() verifies only that the file exists, resolves under the installed root, is readable, and contains two substrings: '# Project Workflow V2 Router' and 'Production selector: tools/router.py.' (with the selector in Markdown code formatting in the real constant). A file containing essentially only those two sentinels passes and build_context() tells the runtime that it is the canonical bundled router.
- Minimal reproduction: Copy the exact SessionStart hook into a temporary package root and replace workflow/ROUTER.md with only the required header and selector sentinel line. Run the hook with PLUGIN_ROOT set to that root. It emits normal 'Canonical bundled router' context rather than a BLOCKING error.
- Why this is materially load-bearing: The bootstrap establishes which installed file becomes workflow authority. Sentinel-preserving truncation, packaging drift, or arbitrary semantic replacement can therefore fail open and leave a runtime following incomplete/incorrect workflow policy while the bootstrap explicitly claims success.
- Defect class / likely siblings: Shallow sentinel validation used as semantic package-integrity validation.
- Existing tests that failed to catch it: tests/test_codex_delivery.py::test_missing_and_malformed_router_fail_closed tests a missing file and the string 'not a V2 router', which removes both sentinels. It does not test malformed/truncated content that preserves the two accepted sentinels.
- Reproduction artifact, if any: repros/repro_session_start_sentinel.py.

#### S007 source coverage

The audit remained bound to commit 4fb4bfb7d7b1481d6f347c182fc96a5a1135e045. The exact commit and recursive Git tree were read through GitHub's immutable commit/tree APIs. Before findings were frozen, no audit/* branch, other swarm report, GitHub Issue/PR comment, or historical implementation/workstreams/**/evidence/** or reviews/** material was used.

Inspected canonical modules included ROUTER, AUTHORITY, STATE, INTAKE, RESEARCH, BRAINSTORMING, PLANNING, PLAN_REVIEW, EXECUTION_PREP, EXECUTION, REVIEW, RECOVERY, GITHUB_ISSUES, CLOSE, WORKSTREAMS and USER_STOP. Executable/helpers inspected included router.py, state_contract.py, execution_contract.py, recovery_contract.py, review_contract.py and close_contract.py, together with their focused tests and relevant state/templates. Delivery/bootstrap coverage included the Codex plugin manifest, marketplace metadata, Skill, hook manifest, SessionStart hook, ChatGPT bootstrap prompts and delivery tests.

Selected lens 9 was exercised against Research/Intake precedence, tracker recovery and external-effect readback. Lens 10 was exercised against the plugin/Skill/SessionStart bootstrap and malformed-package behavior. Lens 1 was exercised against early-return precedence, especially explicit-stop versus Research. Lens 12 was exercised by comparing documented exact-identity/acceptance semantics with the production validators/selectors and by constructing negative-space cases omitted by tests.

The preserved reproduction scripts are non-mutating and are written to run against the repository checkout containing this audit. They target the production selector/validators and existing router fixture helpers; product code is not patched by the reproductions.

#### S007 original confidence and limitations

Confidence is high in the five control-flow/validation defects because each follows a direct deterministic production path and is contradicted by an explicit canonical invariant. Existing tests also expose the relevant negative space, especially the synthetic unverified blob metadata in the READY dependency fixture.

This environment could not execute a full checkout of the immutable commit: the connected Desktop Commander executor had exhausted its monthly call quota, while the isolated container had no GitHub DNS/network access. Therefore the preserved reproduction scripts were authored against the exact fetched source and fixtures but were not executed in this audit session. No product code was modified to compensate for that limitation.

The exact merge commit returned no associated combined-status entries or workflow runs through the available commit-status wrappers, so this audit does not claim CI verification for the audit subject itself.


## S008 — audit/pwv2-swarm-6ugr6l0d6zsn8fgvpdj1cjsd

### S008-F01 — Immutable Git identities are syntactic labels, so same-path mutations bypass freshness and review checks

- Source branch: `audit/pwv2-swarm-6ugr6l0d6zsn8fgvpdj1cjsd`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: router precedence / unreachable branches / conflicting obligations; Planning / Premium gates / Execution precedence; malformed or contradictory state / fail-closed behavior; plugin / install / update / SessionStart / bootstrap drift

- **Affected workflow contract/invariant:** `workflow/STATE.md` requires READY launch refresh to verify each predecessor result by exact path + immutable commit/blob identity and explicitly says missing, stale, or same-path-changed dependency inputs fail closed. The same state/recovery contracts require implementation review attempts to bind the exact immutable current result subject before GREEN finalization.
- **Expected behavior:** A file at a dependency/result/plan path whose bytes no longer match the declared immutable Git blob must not be accepted merely because its TOML locator still contains the old 40-hex strings. READY launch should recover/fail closed for a same-path mutation, and a reviewed result changed after GREEN must require a new exact review subject.
- **Actual behavior:** `validate_locator`, `_git_blob_subject_key`, and `exact_result_subject` validate only the shape/presence of commit/blob strings. `refresh_ready_card` compares the Card's declared `(path, commit, blob)` tuple with the DONE predecessor's declared tuple and then reads the current path, but never verifies those bytes against the declared blob/commit. The implementation-result review path similarly compares the review's declared subject string with the Board result's declared subject string while reading/parsing the current result file independently. A same-path byte mutation with unchanged labels therefore remains launchable/review-finalizable.
- **Minimal reproduction:** Start with a READY Card depending on a DONE predecessor result whose Board and Card both declare `results/M01-T03.md@aaaa...:bbbb...`. Confirm the selector reaches `execution_prep`. Change only the bytes of `results/M01-T03.md`, leave both declared identities untouched, and select again: the production path still satisfies the tuple equality and reads the changed file without hashing/verifying it. Sibling reproduction: create an in-progress Card with a syntactically valid result plus exact GREEN review, mutate only the result file's tests/readback summary, leave the Board/review blob labels unchanged; the selector still reaches `post_review_finalization`.
- **Why this is materially load-bearing:** Exact Git identity is the mechanism that prevents stale predecessor inputs and stale GREEN review coverage. Treating immutable identity as an unauthenticated label allows unreviewed/mutated content to launch downstream work or pass deterministic finalization while claiming coverage for different bytes.
- **Defect class / likely siblings:** Missing dereference/verification of durable immutable identities. The same class applies wherever a `git_blob` or `path + commit + blob` subject is accepted by string equality without resolving the named Git object, including Planning/Plan Review and any future exact-result reuse path.
- **Existing tests that failed to catch it:** `test_ready_card_stale_dependency_fails_closed_before_launch` changes the Board's declared commit/blob as well as the file, so tuple inequality catches it before byte identity matters. `test_changed_result_after_terminal_review_requires_new_attempt` likewise changes the Board's declared blob string. Neither test mutates same-path bytes while keeping the declared immutable identity constant.
- **Reproduction artifact, if any:** `audits/swarm/6ugr6l0d6zsn8fgvpdj1cjsd/repros/repro_router_semantic_holes.py` — `f1_same_path_dependency_mutation` and `f1_same_path_reviewed_result_mutation`.

### S008-F02 — Research short-circuit bypasses higher-precedence explicit and premium stops

- Source branch: `audit/pwv2-swarm-6ugr6l0d6zsn8fgvpdj1cjsd`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: router precedence / unreachable branches / conflicting obligations; Planning / Premium gates / Execution precedence; malformed or contradictory state / fail-closed behavior; plugin / install / update / SessionStart / bootstrap drift

- **Affected workflow contract/invariant:** `tools/router.py` declares `explicit_human_or_premium_boundary` above `research_return` in `PRIORITY_FOUNDATION`. `workflow/BRAINSTORMING.md` makes `explicit_user_stop` a real stop, and `workflow/USER_STOP.md` makes premium A/B/C real-stop boundaries.
- **Expected behavior:** When a valid durable state simultaneously carries an explicit human/premium boundary and a Research obligation, the higher-precedence boundary must win, or the combination must be rejected as contradictory. A lower-precedence Research route must not make the stop unreachable.
- **Actual behavior:** Immediately after validating the selected workstream, `select_route` loads its top-level Research record and returns for `active` or `complete` Research before it ever loads Brainstorming, Definition, or Planning. The relevant validators independently accept a valid active Research record alongside a valid Brainstorming `explicit_user_stop = true`, and they also accept active Definition-return Research alongside a GREEN Definition with premium A due. In both cases the selector's Research return happens before the higher-precedence stop can be observed.
- **Minimal reproduction:** Co-bind (1) a valid active `RESEARCH.toml` with `origin_role = "brainstorming"`, `return_target = "brainstorming"`, and (2) a valid active `BRAINSTORM.toml` with `explicit_user_stop = true`. The selector returns `route/research` before reading the stop. Sibling: promoted Brainstorming + GREEN Definition with `premium_a = "due"` + valid active Definition-return Research also returns `route/research` before the premium-A stop.
- **Why this is materially load-bearing:** A durable explicit user stop is human authority, and premium stops are mandatory workflow boundaries. Allowing fact-gathering state to hide either boundary violates both deterministic precedence and user-control semantics.
- **Defect class / likely siblings:** Early-return precedence inversion between independently valid state owners. Any higher-precedence obligation stored in a record loaded after the top-level Research short-circuit is exposed to the same class; premium B/C and other later explicit boundaries deserve sibling tests.
- **Existing tests that failed to catch it:** Router tests assert the priority tuple and test Research and premium/explicit routes separately, but do not construct co-bound Research + higher-precedence stop states. Thus the declarative precedence constant is not executable precedence for this interaction.
- **Reproduction artifact, if any:** `audits/swarm/6ugr6l0d6zsn8fgvpdj1cjsd/repros/repro_router_semantic_holes.py` — `f2_research_bypasses_explicit_user_stop` and `f2_research_bypasses_premium_a`.

### S008-F03 — Card status/result contradictions can ignore durable completion evidence and replay work

- Source branch: `audit/pwv2-swarm-6ugr6l0d6zsn8fgvpdj1cjsd`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: router precedence / unreachable branches / conflicting obligations; Planning / Premium gates / Execution precedence; malformed or contradictory state / fail-closed behavior; plugin / install / update / SessionStart / bootstrap drift

- **Affected workflow contract/invariant:** `workflow/STATE.md` and `workflow/RECOVERY.md` say a durable valid semantic result is recovery truth and prevents implementation replay; invalid/stale/contradictory binding must fail closed. Mutable Task Board state is supposed to represent the single Card lifecycle coherently.
- **Expected behavior:** A Card that already carries a durable result must be reconciled/reviewed/finalized according to that result, or an impossible status/result combination must fail closed. A Card must not be simultaneously READY/planned/blocked and completed enough to carry a durable accepted result that the router then ignores.
- **Actual behavior:** `validate_board` permits a `result` locator on every Card status; it only requires one when status is `done`. The router inspects a result only inside the `in_progress` branch. A READY Card with a valid result passes `refresh_ready_card` and routes to `execution_prep`; planned cards with results fall to JIT preparation, and blocked cards route by blocker classification. The durable result is therefore not recovery truth for these accepted state combinations.
- **Minimal reproduction:** Use a valid in-progress Card/result with review requirement `none`, then change only its Task Board status to `ready` while retaining the result locator. `validate_board` accepts the record. The selector places the Card in the READY set, performs launch refresh, ignores `cards.result`, and returns `route/execution_prep` instead of result reconciliation or Recovery.
- **Why this is materially load-bearing:** Torn or partially persisted state can make already accepted implementation work execute again. For Cards with external effects, that turns a state-consistency bug into duplicate mutation risk; even for pure code it can overwrite or diverge from the durable accepted result.
- **Defect class / likely siblings:** Missing status/result state-machine invariants plus routing that conditions result authority on one mutable status. Siblings are `planned + result`, `ready + result`, and `blocked + result`; review-attempt/status coherence should be tested similarly.
- **Existing tests that failed to catch it:** State-contract tests require results for DONE Cards but do not reject results on non-result-bearing statuses. Router tests exercise a result on `in_progress` and DONE closure, but not READY/planned/blocked Cards that retain result evidence.
- **Reproduction artifact, if any:** `audits/swarm/6ugr6l0d6zsn8fgvpdj1cjsd/repros/repro_router_semantic_holes.py` — `f3_ready_result_is_ignored`.

### S008-F04 — Active execution trusts Card existence rather than validating the stable Task Card contract

- Source branch: `audit/pwv2-swarm-6ugr6l0d6zsn8fgvpdj1cjsd`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: router precedence / unreachable branches / conflicting obligations; Planning / Premium gates / Execution precedence; malformed or contradictory state / fail-closed behavior; plugin / install / update / SessionStart / bootstrap drift

- **Affected workflow contract/invariant:** `workflow/EXECUTION_PREP.md` defines the stable Task Card contract as exact Card ID, bounded included/excluded scope, authority refs, dependency identities, observable acceptance, tests/readback, review requirement, and optional technical contract. `workflow/EXECUTION.md` requires launch refresh before implementation. `workflow/ROUTER.md` requires incomplete/invalid binding to fail closed.
- **Expected behavior:** On fresh recovery of an `in_progress` Card, the selector must establish that the durable Card still satisfies the stable Card contract before routing implementation. A missing/incomplete acceptance or authority contract should be Recovery, not Execution.
- **Actual behavior:** The active/no-result branch in `select_route` only reads the Card file to prove it exists and then returns `route/execution`. It invokes `parse_task_card` only if the Card already has a result. The repository's own default router fixture proves the gap: its active M01-T04 Card contains only a heading and one sentence, while `test_active_card_routes_to_runtime_neutral_execution` and the baseline route test expect Execution. The same text is rejected by `parse_task_card` for missing stable fields.
- **Minimal reproduction:** Run `select_route` on `tests/fixtures/router/valid-project`; it returns `route/execution` for M01-T04. Pass that exact fixture Card to `parse_task_card(..., "M01-T04", "sample-workstream")`; it raises `ValidationError` because the stable fields are absent.
- **Why this is materially load-bearing:** Recovery after a context/runtime transition can continue code mutation without durable bounded scope, authority, dependencies, acceptance, tests, or review requirements. The workflow therefore cannot prove that the recovered execution is still authorized or know how to validate/finalize it.
- **Defect class / likely siblings:** Validation asymmetry between READY/result-bearing Cards and active result-less Cards. Any recovery path that treats file existence as contract validity can accept truncated/stale Card authority.
- **Existing tests that failed to catch it:** This is not merely uncovered negative space: the shipped active-Card fixture and tests encode the fail-open route as the expected behavior, while READY tests replace the fixture with a complete Card before launch refresh.
- **Reproduction artifact, if any:** `audits/swarm/6ugr6l0d6zsn8fgvpdj1cjsd/repros/repro_router_semantic_holes.py` — `f4_active_malformed_card_executes`.

#### S008 source coverage

The audit remained bound to `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045` for product semantics. It inspected canonical routing/state/authority/Brainstorming/Research/Planning/Plan Review/Execution Prep/Execution/Recovery/Close/user-stop contracts; the production router and state/execution/recovery/close helpers; router/state/execution/recovery/close test suites and fixtures; Task Board/Card/result templates; the state-envelope schema; Codex plugin metadata, Skill, SessionStart hook and delivery tests; ChatGPT bootstrap instructions; and the repository test entrypoint.

All four selected attack lenses were exercised:
- router precedence / conflicting obligations: F2, plus Board-precedence negative-space checks;
- Planning / Premium gates / Execution precedence: F2 premium-A sibling and review-subject checks;
- malformed/contradictory state / fail-closed behavior: F1, F3, F4;
- plugin / install / update / SessionStart / bootstrap drift: no material finding demonstrated.

The audit did not inspect any `audit/*` branch/report, GitHub Issue, or PR comment during blind discovery. Historical workstream evidence was inspected only after the four-finding set was frozen.

#### S008 original confidence and limitations

Confidence is high in the four semantic counterexamples because each follows a concrete production-code path and is anchored to explicit canonical invariants. F4 is additionally embodied by the repository's own executable router fixture/test expectation. F1's existing tests also expose the precise negative space: they detect changed declared labels, not changed bytes behind unchanged labels.

Ad-hoc execution of the preserved reproduction script was not available in this chat environment: the local container had no usable repository-network checkout path and the outer command harness was unavailable to this turn. The reproductions are therefore preserved as non-mutating scripts against the repository's existing disposable test helpers rather than claimed as locally executed results. This limitation does not alter the source-level actual behaviors described above, but an independent runner should execute the script on the exact subject commit as final confirmation.

No exhaustive historical search was performed after freeze; historical classification below is based only on directly relevant durable material already present at the exact subject.


## S009 — audit/pwv2-swarm-704a9fctlw3yp99at6ov43d5

### S009-F01 — Exact Git identities are declared but never verified against the bytes they name

- Source branch: `audit/pwv2-swarm-704a9fctlw3yp99at6ov43d5`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: path traversal / locator safety / cross-workstream binding; malformed or contradictory state / fail-closed behavior; router precedence / unreachable branches / conflicting obligations; review independence / review bypass / result mutation

- Affected workflow contract/invariant: EXECUTION_PREP and STATE require READY dependencies to be bound by exact result path + immutable commit/blob identity, and explicitly require same-path-changed inputs to fail closed. REVIEW/RECOVERY likewise require GREEN coverage of the exact still-current result subject.
- Expected behavior: launch/review/finalization must prove that the bytes read at a declared path are the bytes named by the recorded blob/commit, and recover when they are stale or nonexistent.
- Actual behavior: refresh_ready_card compares only the Card dependency tuple (path, commit, blob) with the tuple copied into a DONE predecessor on TASK_BOARD.toml, then merely reads the path. It never resolves the commit/blob or hashes the bytes. The same declaration-only pattern is used for current result/review subjects. Arbitrary 40-hex identities therefore act as authority, and changing file bytes while leaving metadata unchanged is invisible.
- Minimal reproduction: create a DONE predecessor with result path P, commit A and blob B; make a READY Card depend on P@A:B. The selector routes execution_prep. Change only the bytes at P while leaving the Board and Card tuple unchanged. The membership test still succeeds and the selector still routes execution_prep instead of Recovery. The preserved repro also demonstrates the declaration-only identity path.
- Why this is materially load-bearing: stale dependency content can launch downstream implementation, and a same-path mutation of an already-reviewed result can preserve a nominal GREEN subject even though the reviewed bytes changed.
- Defect class / likely siblings: identity-by-string rather than identity-by-Git-object; likely siblings include Planning immutable subjects, implementation result refs and implementation/plan review subjects.
- Existing tests that failed to catch it: test_ready_card_stale_dependency_fails_closed_before_launch changes both the Board commit/blob metadata and the file bytes, so it exercises tuple mismatch rather than same-metadata/same-path byte mutation. Changed-result review tests likewise mutate the recorded blob field.
- Reproduction artifact, if any: repros/repro_router_semantics.py (F1).

### S009-F02 — A REQUIRED-review Card can be marked DONE and bypass review entirely

- Source branch: `audit/pwv2-swarm-704a9fctlw3yp99at6ov43d5`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: path traversal / locator safety / cross-workstream binding; malformed or contradictory state / fail-closed behavior; router precedence / unreachable branches / conflicting obligations; review independence / review bypass / result mutation

- Affected workflow contract/invariant: REVIEW and STATE say REQUIRED/activated RECOMMENDED review is blocking; no attempt, pending, in-progress or RED must block terminal Card completion.
- Expected behavior: a Card whose stable contract requires review cannot be accepted as DONE unless the exact current result has a qualifying GREEN attempt; contradictory DONE state must fail closed or route the outstanding review/finalization obligation.
- Actual behavior: validate_board requires only that a DONE Card have a result locator. The router reads review requirements/history only inside the in_progress branch. If the same Card is persisted as done, the review code is skipped and an all-DONE Board routes directly to Close.
- Minimal reproduction: start with one Card, give it a valid durable result, set its Task Card field Review requirement: required, leave review_attempts empty, and set Board status to done. validate_board accepts the state and select_route returns route/close.
- Why this is materially load-bearing: a single mutable status value can erase a mandatory independent-review gate and move the workstream into final integration/closure semantics.
- Defect class / likely siblings: lifecycle invariants enforced only on one router branch rather than in the durable state validator; pending or RED attempts on a DONE Card are sibling bypasses.
- Existing tests that failed to catch it: required-review router tests keep the Card in_progress. test_all_terminal_cards_route_to_close_not_directly_to_stop explicitly uses Review requirement: none.
- Reproduction artifact, if any: repros/repro_router_semantics.py (F2).

### S009-F03 — Contradictory READY + durable-result state is accepted and routes toward launch instead of reconciliation

- Source branch: `audit/pwv2-swarm-704a9fctlw3yp99at6ov43d5`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: path traversal / locator safety / cross-workstream binding; malformed or contradictory state / fail-closed behavior; router precedence / unreachable branches / conflicting obligations; review independence / review bypass / result mutation

- Affected workflow contract/invariant: EXECUTION and RECOVERY state that a valid durable semantic result is recovery truth and prevents implementation replay; malformed/contradictory durable state must fail closed.
- Expected behavior: a Card carrying an accepted result cannot simultaneously behave as a not-yet-executed READY Card. The selector must reconcile the durable result or reject the contradiction.
- Actual behavior: validate_board permits result locators on planned, ready and blocked Cards. Result reconciliation is checked only for in_progress. A READY Card with a result passes launch refresh and routes execution_prep with the reason that it is ready for launch.
- Minimal reproduction: add a valid result locator/file to the fixture Card, change its status from in_progress to ready, provide its authority file, and call select_route. The result is route/execution_prep, not result_reconciliation or Recovery.
- Why this is materially load-bearing: interrupted or partially persisted state can cause already-completed implementation to be treated as launchable work, undermining the no-replay recovery invariant.
- Defect class / likely siblings: status/result cross-field invariants absent from Board validation; planned+result and blocked+result are neighboring contradictory states.
- Existing tests that failed to catch it: durable-result recovery is tested only with an in_progress Card; READY tests contain no result.
- Reproduction artifact, if any: repros/repro_router_semantics.py (F3).

### S009-F04 — Result and terminal-review evidence may be nonexistent or unrelated while reconciliation/finalization proceeds

- Source branch: `audit/pwv2-swarm-704a9fctlw3yp99at6ov43d5`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: path traversal / locator safety / cross-workstream binding; malformed or contradictory state / fail-closed behavior; router precedence / unreachable branches / conflicting obligations; review independence / review bypass / result mutation

- Affected workflow contract/invariant: EXECUTION requires accepted semantic results to carry durable evidence and verified tests/readback; REVIEW requires terminal attempts to retain durable verdict evidence.
- Expected behavior: evidence locators used to justify an accepted result or GREEN/RED terminal review must be class/workstream-bound as appropriate and dereference to durable evidence before reconciliation/finalization.
- Actual behavior: parse_card_result validates only the syntax/prefix of Evidence refs and never reads them. validate_review requires terminal evidence_path to be a nonempty safe relative string but does not bind it to the workstream evidence directory or verify that it exists. The router therefore accepts a result whose evidence file is absent, and can finalize a GREEN attempt whose evidence_path is absent or unrelated.
- Minimal reproduction: (a) active Card with Review requirement: none, valid result text, but a nonexistent workstream evidence ref -> route/result_reconciliation; (b) REQUIRED review with valid result and GREEN attempt whose evidence_path names a nonexistent file -> route/post_review_finalization.
- Why this is materially load-bearing: the durable evidence chain can be fabricated by path strings while the workflow proceeds as though implementation and independent verdict evidence were preserved.
- Defect class / likely siblings: locator syntax accepted without object existence/class validation; Plan Review terminal evidence_path uses the same pattern.
- Existing tests that failed to catch it: execution_contract tests parse evidence paths without creating those evidence files; state tests check terminal evidence_path is nonempty, not that it exists or belongs to the expected evidence class.
- Reproduction artifact, if any: repros/repro_router_semantics.py (F4).

### S009-F05 — Task-Board Research can return execution to a nonexistent or wrong Card

- Source branch: `audit/pwv2-swarm-704a9fctlw3yp99at6ov43d5`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: path traversal / locator safety / cross-workstream binding; malformed or contradictory state / fail-closed behavior; router precedence / unreachable branches / conflicting obligations; review independence / review bypass / result mutation

- Affected workflow contract/invariant: RESEARCH says the exact record owns one exact return target and never selects a different target by itself; RECOVERY gives implementation Research precedence but must return to the exact durable owner.
- Expected behavior: Board-owned implementation Research must be bound to the actual originating/current Card and exact owner role; a stale or fabricated return Card must fail closed.
- Actual behavior: validate_research treats any string beginning execution:, execution_prep: or execution_resolution: as a valid execution return target. The Board router checks origin_role but never verifies that origin_subject/return-target Card identity exists in the Board or matches the originating Card. It then routes using the arbitrary suffix as subject.
- Minimal reproduction: keep active Card M01-T04, point Board research_obligation at a complete Research record with origin_subject M01-T04 but return_target = execution:M99-T99. The selector returns route/execution with subject M99-T99 even though that Card does not exist.
- Why this is materially load-bearing: a stale or malformed Research record can redirect deterministic continuation across Card authority boundaries instead of failing closed.
- Defect class / likely siblings: free-form role:subject strings without owner-object referential integrity; empty execution: suffix is also accepted by the validator.
- Existing tests that failed to catch it: Task-Board Research tests use matching origin_subject and return_target for M01-T04 only.
- Reproduction artifact, if any: repros/repro_router_semantics.py (F5).

### S009-F06 — Backslash traversal bypasses workstream-local locator checks on Windows

- Source branch: `audit/pwv2-swarm-704a9fctlw3yp99at6ov43d5`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: path traversal / locator safety / cross-workstream binding; malformed or contradictory state / fail-closed behavior; router precedence / unreachable branches / conflicting obligations; review independence / review bypass / result mutation

- Affected workflow contract/invariant: path traversal is forbidden; every locator must be exact, class-checked and workstream-bound across supported runtimes.
- Expected behavior: path validation must reject traversal using any separator semantics that the host filesystem will interpret, so a sample-workstream Task Card cannot resolve into another workstream.
- Actual behavior: _safe_relative_path and Reads first tokenize with PurePosixPath and raw-string prefix checks, but Reads later constructs a host-native Path. A component such as ..\..\other contains no POSIX '..' part and the raw path still starts with the required sample-workstream prefix. On Windows, host path normalization interprets the backslashes and resolves into implementation\workstreams\other\....
- Minimal reproduction: validate a task_card locator with path implementation/workstreams/sample-workstream/cards/..\..\other/cards/M01-T99.md. The production string/Posix checks accept its shape. Python ntpath normalization of that exact raw path under C:\repo yields C:\repo\implementation\workstreams\other\cards\M01-T99.md.
- Why this is materially load-bearing: on Windows a supposedly workstream-bound locator can read another workstream's Card while still passing the intended cross-workstream/path-traversal checks.
- Defect class / likely siblings: mixed POSIX validation with host-native filesystem interpretation; applies to other prefix-bound locators and authority/technical-contract reads.
- Existing tests that failed to catch it: locator tests cover forward-slash ../ escape and explicit other-workstream paths, not backslash traversal.
- Reproduction artifact, if any: repros/repro_windows_locator.py (F6).

#### S009 source coverage

Inspected the exact subject's workflow router/state/execution-prep/execution/recovery/review/research/planning/plan-review/close/workstream contracts; production router, state, execution, recovery, review and close helpers; router/state/execution/review/close tests; templates/schema inventory; test runner/workflow configuration.

Selected lens coverage:
- path traversal / locator safety / cross-workstream binding: F5, F6 and locator validation review;
- malformed or contradictory state / fail-closed behavior: F2, F3, F4, F5;
- router precedence / unreachable branches / conflicting obligations: F2, F3, F5;
- review independence / review bypass / result mutation: F1, F2, F4.

Negative-space testing focused on interactions the existing suite does not combine: unchanged declared identity with changed bytes, terminal status with mandatory review, READY plus a durable result, absent evidence objects, mismatched Research return owners, and Windows separator semantics. GitHub Actions check runs visible for the exact subject_commit report success, confirming the repository's ordinary suite did not reject these states.

No audit/* branch/report, GitHub Issue/PR defect discussion, or historical workstream evidence/review narrative was consulted before freezing the finding set. No post-freeze historical comparison was performed.

#### S009 original confidence and limitations

Confidence is high for F1-F5 because each follows directly through the production validator/router branches and preserved minimal fixture mutations. F6 is high for the validator/path-normalization mismatch and platform-conditional in impact; direct Python normalization confirmed the same raw path that lacks a PurePosix '..' part normalizes across workstreams under Windows path semantics.

A detached local execution of the full exact commit could not be completed in this session: direct container Git fetch lacked network name resolution and the connected remote-command service had exhausted its current usage allowance. I did not retry that unavailable service. The exact-subject GitHub Actions test check is green, and the non-mutating repro scripts are persisted for execution in any checkout pinned to the subject commit.


## S010 — audit/pwv2-swarm-7sgwic5vusy2pkcta7682nm2

### S010-F01 — Research return ownership is not bound to its origin, allowing an illegal owner jump

- Source branch: `audit/pwv2-swarm-7sgwic5vusy2pkcta7682nm2`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: Planning / Premium gates / Execution precedence; Research / Intake / tracker / external-side-effect recovery; RED / recovery / blocker / interrupted-runtime continuation; router precedence / unreachable branches / conflicting obligations

- Affected workflow contract/invariant: `workflow/RESEARCH.md` durable return ownership; `workflow/INTAKE.md` issue prior-art/alignment boundary; `workflow/ROUTER.md` fail-closed routing.
- Expected behavior: Intake-origin Research for an issue repair must return to Intake for once-only reconciliation, and a contradictory origin/return pair must fail closed before any later phase is reachable.
- Actual behavior: `validate_research()` validates `origin_role` and `return_target` independently. A syntactically valid record with `origin_role = "intake"`, the current repair subject, `state = "complete"`, but `return_target = "definition"` is accepted. `select_route()` handles completed Research before Intake and routes directly to Definition from the untrusted `return_target`.
- Minimal reproduction: Start from the valid router fixture; add active issue Intake for `repair:v2` with no diagnosis-prior-art binding and pending alignment; add completed Research with `origin_role = "intake"`, `origin_subject = "repair:v2"`, `return_target = "definition"`, pending reconciliation, and otherwise valid source accounting. The selector reaches `route/definition` instead of Intake/Recovery.
- Why this is materially load-bearing: This can skip the mandatory Intake reconciliation and post-diagnosis user-alignment/authorization boundary and therefore select an illegal later workflow owner.
- Defect class / likely siblings: Missing cross-field authority binding. The same validator also permits Brainstorming/Definition origin-return swaps and execution-origin records whose return prefix/suffix is unrelated to the origin subject.
- Existing tests that failed to catch it: `test_active_and_completed_research_route_to_exact_owner` exercises only matching origin/return pairs; `test_issue_diagnosis_requires_exact_consumed_prior_art_research` uses the expected Intake return.
- Reproduction artifact, if any: `repros/F1_research_return_bypass.py`.

### S010-F02 — Premium A / Planning state is not bound to the current Definition revision

- Source branch: `audit/pwv2-swarm-7sgwic5vusy2pkcta7682nm2`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: Planning / Premium gates / Execution precedence; Research / Intake / tracker / external-side-effect recovery; RED / recovery / blocker / interrupted-runtime continuation; router precedence / unreachable branches / conflicting obligations

- Affected workflow contract/invariant: `workflow/PLANNING.md` exact planning-cycle entry and full A→Planning→B→Plan Review→C replay on material re-entry; PWV2-REQ-044; stale/contradictory state fail-closed behavior.
- Expected behavior: A changed current Definition must not be able to reuse a Planning cycle and premium-gate satisfaction belonging to an older Definition entry. The exact current Definition-to-Planning handoff must be provable.
- Actual behavior: `validate_definition()` stores only `premium_a = due|satisfied` and has no exact premium-A subject. `validate_planning()` requires only that its self-declared `premium_a_subject` equal its self-declared `entry_subject`; neither is compared with the current Definition revision. `select_route()` performs no such cross-record comparison. A current GREEN Definition R2 can therefore coexist with an approved R1 Planning cycle, GREEN plan review, satisfied B/C, and an active Board, and downstream execution remains selectable.
- Minimal reproduction: Install the normal GREEN Definition/approved-plan fixture, change only the current Definition revision from R1 to R2 while leaving the old Planning entry `definition:R1|planning-cycle:1` and its satisfied gates intact, then route. The stale plan is accepted and the active Board is dispatched.
- Why this is materially load-bearing: A material Definition change can alter accepted authority while execution continues under strategy and premium approvals from the previous Definition, bypassing the required planning/review gate sequence.
- Defect class / likely siblings: Missing cross-record epoch/subject binding between Definition completion, premium A, and Planning entry. Any state writer that accidentally or maliciously retains old Planning state across a Definition revision can pass validation.
- Existing tests that failed to catch it: `test_stale_premium_cycle_and_wrong_review_subject_fail_closed` checks inconsistencies inside Planning/Plan Review but does not vary the current Definition revision against an older Planning entry; planning helpers consistently use Definition R1.
- Reproduction artifact, if any: `repros/F2_stale_definition_planning.py`.

### S010-F03 — “Exact” Git commit/blob identities are trusted without verifying the bytes read

- Source branch: `audit/pwv2-swarm-7sgwic5vusy2pkcta7682nm2`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: Planning / Premium gates / Execution precedence; Research / Intake / tracker / external-side-effect recovery; RED / recovery / blocker / interrupted-runtime continuation; router precedence / unreachable branches / conflicting obligations

- Affected workflow contract/invariant: `workflow/STATE.md` exact immutable result/dependency identity and same-path-change fail-closed rule; `workflow/EXECUTION_PREP.md` READY launch refresh; `workflow/REVIEW.md` exact reviewed subject + acceptance; `workflow/RECOVERY.md` exact current result refresh.
- Expected behavior: A dependency/result/acceptance that changes at the same path without matching its declared immutable identity must fail closed. GREEN may finalize only the exact bytes and acceptance surface actually reviewed.
- Actual behavior: Result/dependency commit/blob fields are only checked as 40-hex strings. READY refresh compares a Card dependency tuple to the Board’s declared tuple, then reads the current path without hashing or resolving the declared commit/blob. Active-result recovery likewise parses the current result file but constructs `current_subject` solely from the Board’s declared commit/blob. Review acceptance is only a mutable Task Card path. Thus current dependency/result/Card bytes can change while the stale metadata remains unchanged, and the selector still treats the old identity as current.
- Minimal reproduction: (1) Build a READY Card whose dependency tuple exactly matches a DONE predecessor, then change only the predecessor result file contents while leaving both declared tuples unchanged; launch still routes to `execution_prep`. (2) Create a REQUIRED GREEN review for an active result, then mutate the result file and the Task Card acceptance at the same paths without changing the Board/review metadata; routing still reaches `post_review_finalization`.
- Why this is materially load-bearing: This permits execution on stale predecessor evidence and, more seriously, deterministic finalization of result/acceptance bytes that the GREEN review did not cover.
- Defect class / likely siblings: Syntactic identity instead of object verification. The same pattern applies to frozen Planning/Plan Review Git-blob subjects and other locators that claim immutable Git identity without resolving it.
- Existing tests that failed to catch it: `test_ready_card_stale_dependency_fails_closed_before_launch` changes the Board’s declared commit/blob as well as the file, so it tests tuple mismatch rather than same-path content drift. `test_changed_result_after_terminal_review_requires_new_attempt` changes the Board blob, not the underlying result bytes while retaining the old declared identity.
- Reproduction artifact, if any: `repros/F3_unverified_git_identity.py`.

### S010-F04 — A durable explicit user stop can be bypassed once Definition exists

- Source branch: `audit/pwv2-swarm-7sgwic5vusy2pkcta7682nm2`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: Planning / Premium gates / Execution precedence; Research / Intake / tracker / external-side-effect recovery; RED / recovery / blocker / interrupted-runtime continuation; router precedence / unreachable branches / conflicting obligations

- Affected workflow contract/invariant: `workflow/BRAINSTORMING.md` explicit-user-stop semantics; PWV2-REQ-068; router precedence for real human-owned stops.
- Expected behavior: A durable `explicit_user_stop = true` is a real stop, or a contradictory promoted/downstream state containing that stop must fail closed until the stop is explicitly cleared/reconciled.
- Actual behavior: `validate_brainstorm()` permits `explicit_user_stop = true` together with `state = "promoted"` and authorized promotion. In `select_route()`, Definition/Planning handling occurs before the Brainstorming stop check; with a Definition locator present, the selector can route Planning (and, with an approved plan/Board, execution) without ever honoring the explicit stop.
- Minimal reproduction: Start from the normal promoted GREEN Definition fixture, flip only `explicit_user_stop` from false to true in the promoted Brainstorm record, and route. The selector returns `route/planning`, not a real stop or Recovery.
- Why this is materially load-bearing: The implementation can continue authorized work despite durable state explicitly recording that the user stopped it.
- Defect class / likely siblings: Higher-precedence human stop is checked too late and contradictory state is not rejected. Downstream Definition/Planning/Board routes all sit ahead of the stop check.
- Existing tests that failed to catch it: Brainstorming/Definition router tests use `explicit_user_stop = false`; state-contract tests validate the boolean but do not exercise promoted/downstream state with it set true.
- Reproduction artifact, if any: `repros/F4_explicit_stop_bypass.py`.

#### S010 source coverage

Audit subject remained the immutable commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`. I inspected canonical `workflow/ROUTER.md`, `STATE.md`, `PLANNING.md`, `PLAN_REVIEW.md`, `INTAKE.md`, `RESEARCH.md`, `RECOVERY.md`, `BRAINSTORMING.md`, `EXECUTION_PREP.md`, `REVIEW.md`, and `CLOSE.md`; the accepted requirements; `tools/router.py`, `state_contract.py`, `execution_contract.py`, `recovery_contract.py`, `review_contract.py`, and `close_contract.py`; relevant router/state tests, fixture helpers, schema notes, and the repository test runner. The selected Planning/Premium, Research/Intake, RED/recovery, and router-precedence lenses were all exercised. No `audit/*` branch/report, GitHub Issue, or PR discussion was intentionally inspected.

#### S010 original confidence and limitations

Confidence is high in the control-flow/validation counterexamples because they follow directly from the exact production validator and selector and use the repository’s own fixture-building helpers. A fresh command-execution environment was not available during this audit: network cloning was unavailable and the connected remote command service had exhausted its usage quota, so the newly preserved repro scripts could not be executed in-session. They are non-mutating scripts intended to run from a checkout of the exact subject and assert the observed unsafe routes.

Blindness limitation: an early exact-commit metadata fetch unexpectedly returned the merge diff, including historical evidence/review text under `implementation/workstreams/**`, before the independent finding set was frozen. I did not intentionally open those historical files, did not inspect audit branches/reports or tracker discussions, and did not use that material as a checklist; subsequent discovery was confined to the allowed canonical workflow, production tools, tests, schemas/scripts, and fixtures. No post-freeze historical comparison was performed.


## S011 — audit/pwv2-swarm-8wu3nv7atoj98fvx5u4a1lzs

### S011-F01 — Declared immutable Git identities are never resolved against the bytes actually read

- Source branch: `audit/pwv2-swarm-8wu3nv7atoj98fvx5u4a1lzs`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: Research / Intake / tracker / external-side-effect recovery; helper vs documented semantics / parity drift / negative space; path traversal / locator safety / cross-workstream binding; stale commit/blob/path/result/review identity

- Affected workflow contract/invariant: workflow/STATE.md requires exact immutable commit/blob identity for predecessor results and exact immutable review subjects; workflow/EXECUTION_PREP.md requires same-path-changed dependency inputs to fail closed; workflow/REVIEW.md requires one exact immutable Git content subject.
- Expected behavior: before launch, review reuse, result reconciliation or GREEN finalization, the selector must establish that repository + commit + path + blob identifies the artifact bytes being consumed. A same-path content change with stale declared commit/blob identity must fail closed or force a new exact subject.
- Actual behavior: tools/state_contract.py validates commit/blob only as 40-hex strings. tools/router.py refresh_ready_card compares the Task Card dependency tuple to the Task Board result locator tuple and then reads the current path, but never proves that the declared blob is the blob at that commit/path or that the bytes read match it. Active-result review uses exact_result_subject(), which only formats the Task Board strings; review_subject() likewise only formats stored strings. Therefore changing result/dependency file bytes while leaving the declared tuple unchanged preserves the old identity and still routes as if the exact subject were unchanged.
- Minimal reproduction: on the router valid-project fixture, add a DONE predecessor result with path@A:B, make the active Card READY with the same dependency, verify execution_prep, then rewrite only the predecessor result file without changing board/Card A:B. The selector still returns execution_prep. Sibling reproduction: create a required-review result with GREEN review, rewrite only the result artifact while preserving Card ID/shape, and the selector still returns post_review_finalization.
- Why this is materially load-bearing: stale or replaced implementation evidence can be launched against, treated as completed recovery truth, or finalized under a GREEN review that covered different bytes.
- Defect class / likely siblings: stale commit/blob/path identity; syntactic Git-subject validation without repository resolution. The same primitive is used by frozen Planning/Plan Review subjects.
- Existing tests that failed to catch it: test_ready_card_stale_dependency_fails_closed_before_launch changes the declared board commit/blob together with the file; test_changed_result_after_terminal_review_requires_new_attempt and test_active_review_for_changed_result_fails_closed change the declared result blob. None changes only the bytes at the same declared path/identity.
- Reproduction artifact, if any: repros/repro_router_counterexamples.py (cases F1_dependency_bytes and F1_reviewed_result_bytes).

### S011-F02 — Co-bound implementation Research is shadowed by the pre-execution Research branch

- Source branch: `audit/pwv2-swarm-8wu3nv7atoj98fvx5u4a1lzs`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: Research / Intake / tracker / external-side-effect recovery; helper vs documented semantics / parity drift / negative space; path traversal / locator safety / cross-workstream binding; stale commit/blob/path/result/review identity

- Affected workflow contract/invariant: workflow/RECOVERY.md says Task-Board-owned implementation/recovery Research must recover its exact return target before unrelated execution; workflow/ROUTER.md routes completed Research to its exact owner. tools/v1_migration.py emits the same implementation Research locator in both task_board.research_obligation and workstream.research.
- Expected behavior: a legal completed execution Research record co-bound exactly as migration emits must route to execution, execution_prep, or execution_resolution according to its exact return_target.
- Actual behavior: tools/router.py reads workstream.research before the Task Board. For state=complete it indexes a pre-execution-only owner map containing intake, brainstorming, and definition. A legal execution return_target such as execution_resolution:M01-T04 causes KeyError, which is caught and converted to Recovery. The later Task Board Research branch that correctly understands execution_* targets is unreachable in this co-bound state.
- Minimal reproduction: install a complete Task Board Research record with return_target=execution_resolution:M01-T04; it routes execution_resolution. Add workstream.research pointing to the same RESEARCH.toml, matching the binding emitted by tools/v1_migration.py; the same durable Research record now routes recovery_boundary.
- Why this is materially load-bearing: a legal migrated/recovered state cannot continue deterministically and is rejected solely because two canonical owners point at the same intended implementation Research record.
- Defect class / likely siblings: router precedence/shadowing plus producer-consumer parity drift between v1_migration.py and router.py.
- Existing tests that failed to catch it: test_task_board_research_return_is_recovered_before_execution installs only task_board.research_obligation and never co-binds workstream.research; migration tests do not feed the emitted co-bound state through the production router.
- Reproduction artifact, if any: repros/repro_router_counterexamples.py (case F2_cobound_execution_research).

### S011-F03 — Execution Research can route to a nonexistent or unrelated Card

- Source branch: `audit/pwv2-swarm-8wu3nv7atoj98fvx5u4a1lzs`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: Research / Intake / tracker / external-side-effect recovery; helper vs documented semantics / parity drift / negative space; path traversal / locator safety / cross-workstream binding; stale commit/blob/path/result/review identity

- Affected workflow contract/invariant: workflow/RESEARCH.md gives every Research record one exact return owner; workflow/RECOVERY.md requires recovery of the exact Task-Board-owned Research obligation and return target; malformed/stale/contradictory bindings must fail closed.
- Expected behavior: an execution_* return_target must be structurally complete and bound to an actual compatible Card/owner in the selected Task Board. A nonexistent Card target must route Recovery.
- Actual behavior: validate_research accepts any string beginning execution:, execution_prep:, or execution_resolution:. It does not validate the suffix, bind it to origin_subject, or require that a matching Card exists. The Task Board router branch strips the prefix and returns that arbitrary suffix as the subject.
- Minimal reproduction: with a Task Board Research pointer, set origin_role=execution, origin_subject=M99-T99 and return_target=execution:M99-T99 while the board contains only M01-T04. Validation succeeds and the selector returns route/execution with subject M99-T99 instead of Recovery.
- Why this is materially load-bearing: a stale/corrupt Research record can redirect continuation away from the canonical Card and create an execution obligation for work that does not exist in durable Task Board state.
- Defect class / likely siblings: missing cross-record owner binding; prefix-only validation of exact return identity.
- Existing tests that failed to catch it: test_task_board_research_return_is_recovered_before_execution covers only a matching M01-T04 target and has no nonexistent/mismatched target negative case.
- Reproduction artifact, if any: repros/repro_router_counterexamples.py (case F3_unbound_research_target).

### S011-F04 — DONE status bypasses REQUIRED review and can route directly to Close

- Source branch: `audit/pwv2-swarm-8wu3nv7atoj98fvx5u4a1lzs`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: Research / Intake / tracker / external-side-effect recovery; helper vs documented semantics / parity drift / negative space; path traversal / locator safety / cross-workstream binding; stale commit/blob/path/result/review identity

- Affected workflow contract/invariant: PWV2-REQ-036 and workflow/REVIEW.md require REQUIRED and activated RECOMMENDED review to block completion until GREEN; pending/in-progress/RED attempts block terminal Card completion.
- Expected behavior: a Card marked done while its stable contract requires review and no exact GREEN attempt exists is contradictory durable state and must fail closed or resume the review/correction obligation before Close.
- Actual behavior: validate_board requires a result locator for done Cards but does not load the Task Card contract or review-attempt verdicts. router.py loads review history only for an in_progress Card. When every Card is done it routes Close without checking review requirement or pending/RED/no-review state.
- Minimal reproduction: create a required-review result, add a pending review attempt, then change only Card status from in_progress to done. The state passes board validation and the selector returns route/close.
- Why this is materially load-bearing: a single status edit/corruption can bypass the independent-review gate and place unreviewed or RED work on the finalization path.
- Defect class / likely siblings: terminal-state trust without revalidating blocking obligations.
- Existing tests that failed to catch it: test_required_review_blocks_until_green_then_routes_finalization keeps the Card in_progress; test_all_terminal_cards_route_to_close_not_directly_to_stop uses Review requirement: none.
- Reproduction artifact, if any: repros/repro_router_counterexamples.py (case F4_done_bypasses_pending_review).

### S011-F05 — Missing result/review evidence is accepted as durable completion evidence

- Source branch: `audit/pwv2-swarm-8wu3nv7atoj98fvx5u4a1lzs`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: Research / Intake / tracker / external-side-effect recovery; helper vs documented semantics / parity drift / negative space; path traversal / locator safety / cross-workstream binding; stale commit/blob/path/result/review identity

- Affected workflow contract/invariant: workflow/EXECUTION.md requires accepted results to carry durable evidence refs; workflow/REVIEW.md requires durable verdict evidence for terminal attempts; recovery treats a valid durable result as authoritative completion evidence.
- Expected behavior: evidence locators used to justify accepted result or terminal GREEN/RED review must resolve to readable durable evidence. Missing evidence must invalidate the state before reconciliation/finalization.
- Actual behavior: parse_card_result validates evidence refs only lexically and router.py never reads them. validate_review requires terminal evidence_path to be non-empty and lexically relative, but router.py never dereferences it. A deleted/nonexistent evidence file therefore does not invalidate the result or terminal review.
- Minimal reproduction: create a valid no-review result and delete its evidence file; the selector still returns result_reconciliation. Separately, create a required result plus GREEN review, delete the review evidence file, and the selector still returns post_review_finalization.
- Why this is materially load-bearing: completion and GREEN finalization can survive loss or fabrication of the very durable evidence claimed to justify them.
- Defect class / likely siblings: existence/readback gap for durable evidence locators.
- Existing tests that failed to catch it: router result/review helpers always materialize evidence files; state-contract tests reject empty evidence_path but do not test a non-empty path whose artifact is absent.
- Reproduction artifact, if any: repros/repro_router_counterexamples.py (cases F5_missing_result_evidence and F5_missing_review_evidence).

### S011-F06 — GREEN implementation review is not bound to immutable acceptance criteria

- Source branch: `audit/pwv2-swarm-8wu3nv7atoj98fvx5u4a1lzs`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: Research / Intake / tracker / external-side-effect recovery; helper vs documented semantics / parity drift / negative space; path traversal / locator safety / cross-workstream binding; stale commit/blob/path/result/review identity

- Affected workflow contract/invariant: workflow/STATE.md and workflow/REVIEW.md say each implementation review attempt binds the exact immutable subject to its exact acceptance surface; material acceptance change requires renewed coverage rather than reuse of stale GREEN.
- Expected behavior: if the stable Task Card acceptance/tests surface changes after GREEN, the old attempt must no longer authorize finalization; the selector must require a new exact review or fail closed.
- Actual behavior: REVIEW_ATTEMPT acceptance stores only class=task_card plus a mutable path. validate_review checks that the path stem matches card_id, but stores no commit/blob identity for the acceptance surface. router.py rereads the current Task Card only to parse fields/review requirement; it compares the review only to the result subject. Editing Acceptance or Required tests/readback in the same Task Card path after GREEN leaves the old review accepted and still routes post_review_finalization.
- Minimal reproduction: create a required result plus GREEN review, then change only the Task Card Acceptance line at the same path. The selector still returns post_review_finalization.
- Why this is materially load-bearing: reviewed code can be finalized against materially different acceptance criteria that the independent reviewer never evaluated.
- Defect class / likely siblings: mutable-path acceptance identity; review coverage not cryptographically/version bound.
- Existing tests that failed to catch it: implementation-review tests mutate result blob identity but never mutate the Task Card acceptance surface after GREEN.
- Reproduction artifact, if any: repros/repro_router_counterexamples.py (case F6_mutable_acceptance_surface).

#### S011 source coverage

Inspected only the exact subject commit 4fb4bfb7d7b1481d6f347c182fc96a5a1135e045 through GitHub Git/tree/file reads. No audit/* branch, swarm report, GitHub Issue, PR comment, or historical defect narrative was used during discovery.

Canonical/production surfaces inspected include workflow/ROUTER.md, STATE.md, INTAKE.md, RESEARCH.md, GITHUB_ISSUES.md, RECOVERY.md, EXECUTION_PREP.md, EXECUTION.md, REVIEW.md, CLOSE.md; requirements/PROJECT_WORKFLOW_V2.md; relevant templates; tools/router.py, state_contract.py, execution_contract.py, recovery_contract.py, close_contract.py, migration_apply.py and v1_migration.py; and targeted router/state/close tests and fixtures.

Selected attack lenses exercised:
- Research / Intake / tracker / external-side-effect recovery: execution Research ownership/return routing, tracker validation and external-effect helper semantics.
- helper vs documented semantics / parity drift / negative space: migration-to-router co-binding parity and missing negative tests around evidence, terminal review and exact identities.
- path traversal / locator safety / cross-workstream binding: lexical path validation, project-root containment and class/workstream locator binding; symlink aliasing retained only as a non-blocking observation.
- stale commit/blob/path/result/review identity: dependency/result Git identity, review subject identity and acceptance-surface binding.

#### S011 original confidence and limitations

Confidence is high in the six code-path findings because each follows deterministic production selector/validator branches and is paired with a minimal repro harness that calls tools.router.select_route against the repository's existing valid fixture.

I could not execute the repository test suite or repro harness in this audit session: the local container has no GitHub network access, and the connected Desktop Commander device reported its monthly usage limit before command execution. Consequently, Actual behavior above is derived from exact production code at the immutable subject rather than a captured runtime transcript. The repro harness is non-mutating and uses temporary fixture copies so it can be executed directly from this audit branch later.


## S012 — audit/pwv2-swarm-9l58xtzmupt9tz7p7gxv5975

### S012-F01 — Declared commit/blob identity is not verified against current result bytes

- Source branch: `audit/pwv2-swarm-9l58xtzmupt9tz7p7gxv5975`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: plugin / install / update / SessionStart / bootstrap drift; stale commit/blob/path/result/review identity; Planning / Premium gates / Execution precedence; RED / recovery / blocker / interrupted-runtime continuation

- Affected workflow contract/invariant: `workflow/STATE.md` requires READY dependencies to be bound by exact result path + immutable commit/blob identity and says missing, stale, or same-path-changed dependency inputs fail closed; `workflow/RECOVERY.md` requires review subject refresh against the exact current result; `workflow/REVIEW.md` permits GREEN finalization only for the exact current immutable subject.
- Expected behavior: if a dependency/result file changes at the same path while its Board-declared commit/blob values remain unchanged, launch or post-review finalization must fail closed or require a new exact subject/review.
- Actual behavior: `refresh_ready_card()` compares only the dependency tuple declared in the Task Card with the tuple declared in the Task Board, then reads the current path without checking that its bytes correspond to the declared blob/commit. The active-result path similarly parses the current file but derives `current_subject` only from Board strings; a GREEN review whose strings match those stale declarations still routes to `post_review_finalization`.
- Minimal reproduction: create a REQUIRED reviewed result with GREEN R01, then replace the result file at the same path with different but syntactically valid Card Result content while leaving Board/review commit/blob values unchanged. The selector reaches `route/post_review_finalization`. Sibling: mutate a DONE predecessor result file at the same path while leaving both Task Card dependency identity and Board identity unchanged; READY refresh still reaches `route/execution_prep`.
- Why this is materially load-bearing: immutable identity is the safety boundary that prevents changed implementation/dependency content from inheriting prior review or readiness. String agreement between two stale records is not proof of the referenced Git object.
- Defect class / likely siblings: stale immutable-identity trust / TOCTOU. Any path whose commit/blob identity is accepted without resolving the actual Git object is suspect; review acceptance is also path-only and therefore deserves the same class of scrutiny.
- Existing tests that failed to catch it: `test_ready_card_stale_dependency_fails_closed_before_launch` changes the Board commit/blob as well as the file, so it exercises metadata mismatch rather than same-path byte mutation. `test_changed_result_after_terminal_review_requires_new_attempt` changes the Board blob, not the reviewed file while metadata stays stale.
- Reproduction artifact, if any: `audits/swarm/9l58xtzmupt9tz7p7gxv5975/repros/repro_router_state_gaps.py` (`f1_same_path_result_mutation_keeps_green_review`).

### S012-F02 — Terminal evidence locators are accepted without dereferencing durable evidence

- Source branch: `audit/pwv2-swarm-9l58xtzmupt9tz7p7gxv5975`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: plugin / install / update / SessionStart / bootstrap drift; stale commit/blob/path/result/review identity; Planning / Premium gates / Execution precedence; RED / recovery / blocker / interrupted-runtime continuation

- Affected workflow contract/invariant: `workflow/EXECUTION.md` requires an accepted semantic result to carry durable evidence; `workflow/REVIEW.md` requires durable verdict evidence for terminal attempts; `workflow/PLAN_REVIEW.md` requires terminal Plan Review evidence; `workflow/AUTHORITY.md` requires missing required references to fail closed.
- Expected behavior: a terminal result/review whose referenced evidence file is absent or unreadable must not be reconciled, approved, or finalized.
- Actual behavior: `parse_card_result()` validates only the syntax/root of Evidence refs. `validate_review()` and `validate_plan_review()` require a non-empty safe `evidence_path` for terminal verdicts but do not read it. The router does not dereference those evidence locators before result reconciliation, GREEN finalization, RED correction, or Plan Review consumption.
- Minimal reproduction: create a REQUIRED result plus GREEN review using the normal router fixture helpers, delete both the Card Result evidence file and GREEN review evidence file, then call the production selector. It still reaches `route/post_review_finalization`.
- Why this is materially load-bearing: a terminal verdict or accepted result can become durable authority with no durable proof behind its evidence locator, allowing lost/fabricated evidence to pass gates that are explicitly evidence-backed.
- Defect class / likely siblings: locator-existence / evidence-integrity fail-open. The same class applies to implementation result evidence, implementation review terminal evidence, and Plan Review terminal evidence.
- Existing tests that failed to catch it: implementation-result/review tests materialize evidence and never delete it. `test_green_plan_review_consumes_to_c_before_execution_prep` supplies a terminal Plan Review evidence path but does not materialize that file, yet expects Planning consumption, so the suite itself demonstrates the missing dereference without asserting against it.
- Reproduction artifact, if any: `audits/swarm/9l58xtzmupt9tz7p7gxv5975/repros/repro_router_state_gaps.py` (`f2_missing_terminal_evidence_is_not_dereferenced`).

### S012-F03 — Active Research short-circuits a higher-precedence explicit user stop

- Source branch: `audit/pwv2-swarm-9l58xtzmupt9tz7p7gxv5975`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: plugin / install / update / SessionStart / bootstrap drift; stale commit/blob/path/result/review identity; Planning / Premium gates / Execution precedence; RED / recovery / blocker / interrupted-runtime continuation

- Affected workflow contract/invariant: the router priority foundation puts `explicit_human_or_premium_boundary` before `research_return`; `workflow/BRAINSTORMING.md` says an explicit user stop is a real stop; `workflow/ROUTER.md` says real stops must be honored rather than bypassed by lower-precedence work.
- Expected behavior: when the current Brainstorm record carries `explicit_user_stop = true`, an independently valid co-bound active Research record must not cause Research continuation ahead of that stop.
- Actual behavior: `select_route()` loads the workstream-level Research record immediately after the manifest and returns `route/research` for `state = active` before it reads the Brainstorm record at all. Therefore the explicit stop is unreachable on that state combination.
- Minimal reproduction: add a valid active Brainstorm record with `explicit_user_stop = true` and a valid active Brainstorm-origin Research record. The selector returns `route/research`, and the read set does not contain `BRAINSTORM.toml`.
- Why this is materially load-bearing: a durable human stop is an authority boundary. Allowing lower-precedence factual work to bypass it violates the router's own precedence contract and can continue work the user explicitly stopped.
- Defect class / likely siblings: premature return / unread higher-precedence state. Any higher-precedence stop stored in a record that is read after the unconditional Research return is a sibling risk; premium gates warrant the same negative-space test.
- Existing tests that failed to catch it: `test_active_and_completed_research_route_to_exact_owner` has no competing stop. `test_priority_and_real_stop_foundations_are_runtime_neutral` asserts the precedence constants but does not test that control flow implements their ordering.
- Reproduction artifact, if any: `audits/swarm/9l58xtzmupt9tz7p7gxv5975/repros/repro_router_state_gaps.py` (`f3_research_short_circuits_explicit_user_stop`).

### S012-F04 — Definition can bind to a Brainstorm revision whose lifecycle is not promoted

- Source branch: `audit/pwv2-swarm-9l58xtzmupt9tz7p7gxv5975`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: plugin / install / update / SessionStart / bootstrap drift; stale commit/blob/path/result/review identity; Planning / Premium gates / Execution precedence; RED / recovery / blocker / interrupted-runtime continuation

- Affected workflow contract/invariant: `workflow/BRAINSTORMING.md` defines `active -> ready_for_definition -> promoted` lifecycle semantics and says the exact promoted revision enters Definition; `workflow/DEFINITION.md` states Definition requires the exact promoted Brainstorming subject; `workflow/ROUTER.md` requires stale/contradictory binding to fail closed.
- Expected behavior: a Definition locator is legal only when the referenced Brainstorm record is actually in `state = promoted` for the exact authorized subject.
- Actual behavior: `validate_brainstorm()` allows `state = active` together with `promotion_state = authorized` and exact `promotion_subject`. The router's Definition cross-record check verifies only promotion_state/subject/source_subject, not `brainstorm.state == "promoted"`. A GREEN Definition attached to such an active Brainstorm can route onward to Planning.
- Minimal reproduction: install the normal GREEN Definition fixture, change only `BRAINSTORM.toml` from `state = "promoted"` to `state = "active"`, leaving exact promotion authorization intact. Both records validate and the selector returns `route/planning`.
- Why this is materially load-bearing: the lifecycle transition itself is part of durable promotion authority. Accepting a downstream Definition while the upstream scope is still active permits contradictory state to skip the owner that is supposed to control exploration/promotion.
- Defect class / likely siblings: cross-record lifecycle binding omission. Variants include `ready_for_definition` with authorized promotion and an active record additionally carrying an explicit stop.
- Existing tests that failed to catch it: `test_brainstorming_requires_challenge_and_exact_definition_promotion` tests clean pending/promoted cases; `test_definition_source_mismatch_fails_closed` tests only subject mismatch, not lifecycle mismatch with matching subject.
- Reproduction artifact, if any: `audits/swarm/9l58xtzmupt9tz7p7gxv5975/repros/repro_router_state_gaps.py` (`f4_definition_accepts_non_promoted_brainstorm_state`).

### S012-F05 — `done` Card status can enter Close without validating result or required review

- Source branch: `audit/pwv2-swarm-9l58xtzmupt9tz7p7gxv5975`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: plugin / install / update / SessionStart / bootstrap drift; stale commit/blob/path/result/review identity; Planning / Premium gates / Execution precedence; RED / recovery / blocker / interrupted-runtime continuation

- Affected workflow contract/invariant: `workflow/STATE.md` says REQUIRED/activated RECOMMENDED review blocks terminal Card completion until exact GREEN; `workflow/REVIEW.md` says no attempt/pending/in-progress/RED blocks terminal completion; `workflow/CLOSE.md` requires result/review/evidence recovery artifacts before terminal integration; invalid/missing/contradictory bindings must fail closed.
- Expected behavior: a Card persisted as `done` must be rejected or recovered unless its result exists/validates and its stable Card review requirement is terminally satisfied.
- Actual behavior: `validate_board()` requires a `result` locator for `done` but does not read the result, parse the Card contract, or validate review history/requirement. After active/blocked/READY dispatch, the router checks only `all(card["status"] == "done")` and routes directly to Close.
- Minimal reproduction: create a Card contract with `Review requirement: required` and a result locator, add no review attempt, change status from `in_progress` to `done`, delete the result file, and select a route. The selector still returns `route/close`.
- Why this is materially load-bearing: a contradictory terminal bit can bypass both recovery truth and the blocking independent-review gate, moving invalid execution state into finalization.
- Defect class / likely siblings: terminal-state trust / incomplete cross-record validation. Any DONE Card with a missing/stale result, unsatisfied review, stale acceptance, or missing evidence can be misclassified as terminal.
- Existing tests that failed to catch it: `test_all_terminal_cards_route_to_close_not_directly_to_stop` uses a present result and `Review requirement: none`; there is no negative terminal test with REQUIRED review absent or result target missing.
- Reproduction artifact, if any: `audits/swarm/9l58xtzmupt9tz7p7gxv5975/repros/repro_router_state_gaps.py` (`f5_done_card_bypasses_result_and_review_validation`).

### S012-F06 — SessionStart treats marker-preserving corrupted/stale router text as canonical

- Source branch: `audit/pwv2-swarm-9l58xtzmupt9tz7p7gxv5975`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: plugin / install / update / SessionStart / bootstrap drift; stale commit/blob/path/result/review identity; Planning / Premium gates / Execution precedence; RED / recovery / blocker / interrupted-runtime continuation

- Affected workflow contract/invariant: `skills/project_workflow_v2/SKILL.md` says a missing, malformed, ambiguous, or escaping installed router must fail closed; `hooks/session-start.py` describes itself as a fail-closed bootstrap and must not silently accept bootstrap drift.
- Expected behavior: a truncated/corrupted or incompatible stale router must emit the blocking plugin-package error rather than assert that PWv2 is enabled.
- Actual behavior: `canonical_router()` accepts any readable in-root file containing only two sentinel substrings: the router heading and `Production selector: tools/router.py`. A file containing those two lines plus arbitrary corrupted/truncated body is accepted as canonical. An exact-copy execution of the subject hook with such a router emitted normal `Project Workflow V2 package is enabled` context.
- Minimal reproduction: copy the production SessionStart hook into a temporary package, replace `workflow/ROUTER.md` with the two required sentinel lines plus `CORRUPTED/TRUNCATED POLICY BODY`, set `PLUGIN_ROOT` to that package, and execute the hook. It returns normal enabled bootstrap context, not a BLOCKING error.
- Why this is materially load-bearing: SessionStart is the authority-root bootstrap. Marker-preserving corruption or an older incompatible router can be trusted as current policy, after which missing semantics may be supplied by runtime behavior or memory—the exact drift the bootstrap contract is intended to prevent.
- Defect class / likely siblings: weak package-content identity / update drift. Any stale router version retaining the two sentinels is accepted; the hook also does not bind router bytes to plugin/package version or a manifest digest.
- Existing tests that failed to catch it: `test_missing_and_malformed_router_fail_closed` uses `not a V2 router`, which removes both sentinels. Delivery tests verify package metadata separately but never make SessionStart verify router content/version identity.
- Reproduction artifact, if any: `audits/swarm/9l58xtzmupt9tz7p7gxv5975/repros/repro_sessionstart_marker_corruption.py`.

#### S012 source coverage

The audit stayed bound to subject commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`. Inspection covered canonical routing/state/planning/plan-review/recovery/execution-prep/execution/review/Close/Research/Brainstorming/Definition/authority contracts; production router, state, execution, review, recovery and Close helpers; SessionStart/Skill/plugin packaging; relevant templates; router/state/execution/review/recovery/Close/delivery tests; and the current router fixture.

The selected lenses were exercised as follows:

- plugin / install / update / SessionStart / bootstrap drift: F6;
- stale commit/blob/path/result/review identity: F1, F2, F5;
- Planning / Premium gates / Execution precedence: F2, F3, F4;
- RED / recovery / blocker / interrupted-runtime continuation: F1, F2, F5, plus inspection of RED/blocker/Research-return dispatch.

Negative-space cases were derived against the production selector/validators rather than treating existing GREEN tests as proof. The preserved repro scripts mutate only temporary fixture/package copies and do not modify product code.

#### S012 original confidence and limitations

Confidence is high on the demonstrated control-flow/state-contract mismatches because each finding follows a direct production branch that lacks the required cross-record/content check, and F6 was executed with an exact copy of the subject hook source: marker-preserving corruption produced normal enabled bootstrap context.

A full local execution of F1-F5 against the immutable checkout could not be completed in this chat environment. The ordinary shell could not resolve GitHub for cloning; the connected Desktop Commander device reported its monthly tool-call allowance exhausted and explicitly requested no retry; the available native Codex command bridge required an unavailable valid outer turn token. The GitHub commit-run lookup returned no PR-triggered workflow run for the exact merge subject. The checked-in repro script is designed to run directly from an exact checkout and imports the production selector plus the repository's own router fixture helpers.

Blindness limitation: the first immutable-commit metadata fetch unexpectedly embedded changed-file patches, including historical `implementation/workstreams/**/evidence/**` material, before finding freeze. No `audit/*` branch/report, GitHub Issue, or PR discussion was inspected, and the frozen findings above were derived from canonical workflow/tools/tests rather than using that embedded historical material as a checklist. No post-freeze historical comparison was performed.


## S013 — audit/pwv2-swarm-b7qtnwcsraaa1fat6o96n77a

### S013-F01 — Same-path dependency/result drift is trusted without blob verification

- Source branch: `audit/pwv2-swarm-b7qtnwcsraaa1fat6o96n77a`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: helper vs documented semantics / parity drift / negative space; stale commit/blob/path/result/review identity; Research / Intake / tracker / external-side-effect recovery; router precedence / unreachable branches / conflicting obligations

- Affected workflow contract/invariant: `workflow/STATE.md` and `workflow/EXECUTION_PREP.md` require READY launch refresh to verify exact dependency result path + immutable commit/blob identity, and explicitly require missing/stale or same-path-changed dependency inputs to fail closed. `workflow/RECOVERY.md` likewise treats immutable result identity as the basis for review/finalization.
- Expected behavior: if a dependency/result file changes at the same path while its declared commit/blob locator remains unchanged, routing must fail closed before Execution Prep or later review/finalization consumes that content.
- Actual behavior: `tools/router.py::refresh_ready_card` compares the Task Card dependency tuple only against the tuple declared on the DONE predecessor in the Task Board, then reads the current working-tree file by path. It never verifies that the bytes read are the declared blob or that the declared commit/path actually resolves to that blob. The same trust pattern exists for the active Card result: current file content is parsed, while review identity is derived from Task Board metadata rather than from the bytes just read.
- Minimal reproduction: create the existing READY dependency fixture with matching `path@commit:blob`, then modify only the dependency result file contents while leaving both the Task Card dependency and Task Board result locator unchanged. The production selector follows the READY path and returns `route/execution_prep`; contractually this same-path drift must recover. Preserved in `repros/repro_semantic_defects.py` case `f1`.
- Why this is materially load-bearing: downstream work can launch against predecessor bytes that are not the immutable accepted result named by the workflow, and the same identity gap can let review/finalization reason about locator metadata that no longer describes the current result file.
- Defect class / likely siblings: declared immutable identity is compared as metadata but never proven against artifact bytes/Git objects. Siblings include same-path active-result mutation and any other exact Git subject whose consumer reads the current path without object/hash verification.
- Existing tests that failed to catch it: `test_ready_card_stale_dependency_fails_closed_before_launch` mutates the Task Board commit/blob together with the file; it does not exercise content-only same-path drift with unchanged metadata.
- Reproduction artifact, if any: `audits/swarm/b7qtnwcsraaa1fat6o96n77a/repros/repro_semantic_defects.py`.

### S013-F02 — DONE Card can bypass required review and jump to Close

- Source branch: `audit/pwv2-swarm-b7qtnwcsraaa1fat6o96n77a`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: helper vs documented semantics / parity drift / negative space; stale commit/blob/path/result/review identity; Research / Intake / tracker / external-side-effect recovery; router precedence / unreachable branches / conflicting obligations

- Affected workflow contract/invariant: `workflow/STATE.md` and `workflow/REVIEW.md` state that REQUIRED/activated RECOMMENDED review with no attempt, pending/in-progress, or RED blocks terminal Card completion; GREEN for the exact current subject is what permits deterministic post-review finalization.
- Expected behavior: a Task Board that marks a Card `done` while its stable Card requires review but has no qualifying exact GREEN attempt is contradictory and must fail closed or route back to the review/finalization obligation, never to Close.
- Actual behavior: `tools/state_contract.py::validate_board` requires only that a `done` Card have a result locator. It does not read the Card contract or validate review history against terminal status. `tools/router.py` skips review handling when no Card is `in_progress`; if all Cards are `done`, it immediately returns `route/close`.
- Minimal reproduction: on the valid router fixture, install a valid semantic result for the active Card with `Review requirement: required`, add no review attempt, change only Task Board status from `in_progress` to `done`, and call the production selector. It returns `route/close`. Preserved as case `f2`.
- Why this is materially load-bearing: a malformed/stale Board mutation can bypass independent review authority and move the workstream into integration/finalization ownership.
- Defect class / likely siblings: Task Board status/result/review cross-field invariants are not enforced for terminal/non-active Cards. Related states such as READY/BLOCKED Cards carrying already-durable results deserve the same negative-space validation.
- Existing tests that failed to catch it: `test_all_terminal_cards_route_to_close_not_directly_to_stop` first installs a result with `Review requirement: none`; no test marks a review-required Card DONE without GREEN.
- Reproduction artifact, if any: `audits/swarm/b7qtnwcsraaa1fat6o96n77a/repros/repro_semantic_defects.py`.

### S013-F03 — GREEN review can finalize with missing verdict evidence

- Source branch: `audit/pwv2-swarm-b7qtnwcsraaa1fat6o96n77a`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: helper vs documented semantics / parity drift / negative space; stale commit/blob/path/result/review identity; Research / Intake / tracker / external-side-effect recovery; router precedence / unreachable branches / conflicting obligations

- Affected workflow contract/invariant: `workflow/REVIEW.md` requires terminal attempts to keep durable verdict evidence; the router contract says missing/invalid/stale bindings fail closed. `workflow/CLOSE.md` also treats required review/result/evidence as part of the recovery package.
- Expected behavior: a GREEN/RED terminal review whose declared evidence artifact is missing or not a valid workstream evidence locator must be invalid and fail closed before post-review finalization.
- Actual behavior: `tools/state_contract.py::validate_review` checks only that terminal `evidence_path` is a non-empty safe relative string. It does not constrain it to the workstream evidence root and does not verify that the file exists. `tools/router.py` reads review TOML but never reads the terminal evidence path, so a GREEN attempt can drive `route/post_review_finalization` after its evidence file has been deleted. `validate_plan_review` has the same syntax-only evidence treatment for Plan Review.
- Minimal reproduction: install a REQUIRED result, add a GREEN attempt using the normal workstream evidence path, delete only that evidence file, and call the production selector. The selector still returns `route/post_review_finalization`. Preserved as case `f3`.
- Why this is materially load-bearing: the independent review gate can become a bare verdict bit with a dangling/irrelevant evidence string, defeating the durable-evidence and recovery guarantees.
- Defect class / likely siblings: evidence locator is treated as unverified prose rather than a bound artifact. Plan Review terminal evidence is a direct sibling.
- Existing tests that failed to catch it: state-contract tests reject an empty terminal `evidence_path` but do not test a nonexistent/non-workstream path; router tests create the evidence file but never remove or redirect it.
- Reproduction artifact, if any: `audits/swarm/b7qtnwcsraaa1fat6o96n77a/repros/repro_semantic_defects.py`.

### S013-F04 — Implementation Research can redirect continuation to an arbitrary subject

- Source branch: `audit/pwv2-swarm-b7qtnwcsraaa1fat6o96n77a`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: helper vs documented semantics / parity drift / negative space; stale commit/blob/path/result/review identity; Research / Intake / tracker / external-side-effect recovery; router precedence / unreachable branches / conflicting obligations

- Affected workflow contract/invariant: `workflow/RESEARCH.md`, `workflow/RECOVERY.md`, and `workflow/STATE.md` require one exact return owner; implementation/recovery Research is owned by the selected Task Board and must return to that exact durable owner. Research must not choose a different target by itself.
- Expected behavior: an execution Research return target must have a non-empty exact subject and must be consistent with the Board/origin obligation (for example, it must not redirect M01-T04 recovery to a nonexistent M01-T99). Contradictory targets must fail closed.
- Actual behavior: `tools/state_contract.py::validate_research` accepts any string beginning `execution:`, `execution_prep:`, or `execution_resolution:`; it does not require a non-empty suffix, an existing matching Card/trigger, or consistency with `origin_role`/`origin_subject`. The Board branch in `tools/router.py` merely splits at the first colon and routes the suffix as the new subject.
- Minimal reproduction: use the existing Board-owned completed Research fixture for active Card/origin `M01-T04`, change only `return_target` from `execution_resolution:M01-T04` to `execution_resolution:M01-T99`, and call the production selector. It returns `route/execution_resolution` with subject `M01-T99` although no such selected Card owns the obligation. Preserved as case `f4`.
- Why this is materially load-bearing: a stale/corrupt Research record can select an illegal continuation subject outside the exact Board obligation, violating deterministic routing and authority binding.
- Defect class / likely siblings: structurally unbound encoded return targets. Empty suffixes, mismatched origin roles, nonexistent Card IDs, and execution-vs-resolution target switching are siblings.
- Existing tests that failed to catch it: `test_task_board_research_return_is_recovered_before_execution` tests only a matched `origin_subject = M01-T04` / `return_target = execution_resolution:M01-T04`; state-contract Research tests cover lifecycle/source accounting but no execution-target binding negatives.
- Reproduction artifact, if any: `audits/swarm/b7qtnwcsraaa1fat6o96n77a/repros/repro_semantic_defects.py`.

#### S013 source coverage

Selected attack lenses:
1. helper vs documented semantics / parity drift / negative space;
2. stale commit/blob/path/result/review identity;
3. Research / Intake / tracker / external-side-effect recovery;
4. router precedence / unreachable branches / conflicting obligations.

Inspected on exact subject `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`:
- `workflow/ROUTER.md`, `STATE.md`, `RESEARCH.md`, `INTAKE.md`, `PLANNING.md`, `REVIEW.md`, `RECOVERY.md`, `EXECUTION_PREP.md`, `EXECUTION.md`, `GITHUB_ISSUES.md`, `CLOSE.md`;
- `tools/router.py`, `state_contract.py`, `execution_contract.py`, `recovery_contract.py`, `close_contract.py`;
- relevant negative-space coverage in `tests/test_router.py`, `tests/test_state_contract.py`, and `tests/test_close_contract.py`.

The audit did not inspect `audit/*` branches, GitHub Issues, PR comments, or other swarm reports. Findings were frozen before any intentional historical comparison.

#### S013 original confidence and limitations

Confidence is high for F1, F2 and F4 because the production branches and missing validations are direct and the existing tests expose the exact negative space. Confidence is medium-high for F3 because the contract says durable verdict evidence and the production router never resolves the path, although evidence-file content is not separately schema-defined.

Executable probes could not be run in the audit environment: the local container had no GitHub network resolution and the authorized Desktop Commander endpoint reported that its monthly usage limit was exhausted. The preserved repro script calls the real production selector and existing exact-subject fixture helpers; it was therefore written for direct execution on this audit subject but was not executed here.

Strict-blindness caveat: during bootstrap, the GitHub commit-metadata endpoint unexpectedly returned the merge commit diff, which included historical implementation/evidence paths. Those passages were not used to generate or freeze the findings above; every frozen finding was re-derived from canonical workflow contracts, production helpers, and current tests. No audit branch/report, Issue, or PR discussion was inspected.


## S014 — audit/pwv2-swarm-jyxmfic5ggkl2cok7gu7ng4w

### S014-F01 — Declared Git identities are trusted without dereferencing current bytes

- Source branch: `audit/pwv2-swarm-jyxmfic5ggkl2cok7gu7ng4w`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: review independence / review bypass / result mutation; Close / finalization / end-of-approved-scope; stale commit/blob/path/result/review identity; Research / Intake / tracker / external-side-effect recovery

- Affected workflow contract/invariant: PWV2-REQ-030, PWV2-REQ-034, PWV2-REQ-036; `workflow/STATE.md` exact dependency/result identity; `workflow/RECOVERY.md` exact current review subject; router rule that stale bindings fail closed.
- Expected behavior: A dependency/result/review subject expressed as path + immutable commit/blob must be verified against Git truth before launch, review reuse, or GREEN finalization. Same-path changed bytes, an impossible commit/path/blob tuple, or a result no longer matching the declared immutable subject must fail closed or require a new exact review subject.
- Actual behavior: `validate_locator`, `_git_blob_subject_key`, and `validate_review` only validate 40-hex syntax. `refresh_ready_card` compares dependency metadata tuples from the Card and Board and then reads the current path, but never proves that current bytes are the declared blob or that commit:path resolves to it. The active-result route parses the current result file, then `exact_result_subject` and `review_subject` merely stringify Board/review metadata. Consequently a GREEN review continues to authorize `post_review_finalization` after the result file is mutated at the same path while the declared commit/blob are left unchanged. The same trust defect applies to predecessor dependency refresh; planning/Plan Review subjects use the same syntactic identity pattern.
- Minimal reproduction: Start from the valid router fixture. Materialize a REQUIRED result whose Board locator declares commit `aaaa…`/blob `bbbb…`, add a GREEN review declaring the same tuple, and observe `post_review_finalization`. Mutate the result file bytes at the same path without changing Board/review metadata. The selector still reaches `post_review_finalization` because no Git identity is dereferenced. Preserved in `repros/adversarial_router_cases.py::case_f1_same_path_result_mutation_keeps_green`.
- Why this is materially load-bearing: Exact immutable subjects are the safety boundary that permits review reuse, finalization, recovery without replay, and predecessor-dependent launch. Trusting caller-authored hex strings instead of Git truth allows unreviewed content to inherit a prior GREEN verdict and allows downstream execution to consume altered predecessor results.
- Defect class / likely siblings: Declared-identity-vs-observed-identity confusion. Likely siblings include READY dependency result tuples, planning frozen subjects, Plan Review subjects, and acceptance artifacts that are represented by a mutable path rather than a verified immutable identity.
- Existing tests that failed to catch it: `test_changed_result_after_terminal_review_requires_new_attempt` changes Board blob metadata rather than same-path file bytes. `test_ready_card_stale_dependency_fails_closed_before_launch` changes Board dependency metadata so tuple comparison detects it. Fixture tests intentionally use synthetic `a*40`/`b*40` identities unrelated to actual fixture blobs, so they prove syntactic equality rather than immutable Git binding.
- Reproduction artifact, if any: `audits/swarm/jyxmfic5ggkl2cok7gu7ng4w/repros/adversarial_router_cases.py` (F1).

### S014-F02 — DONE status bypasses REQUIRED/RED review and reaches Close

- Source branch: `audit/pwv2-swarm-jyxmfic5ggkl2cok7gu7ng4w`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: review independence / review bypass / result mutation; Close / finalization / end-of-approved-scope; stale commit/blob/path/result/review identity; Research / Intake / tracker / external-side-effect recovery

- Affected workflow contract/invariant: PWV2-REQ-034, PWV2-REQ-036, `workflow/REVIEW.md` blocking lifecycle, and `workflow/STATE.md` rule that REQUIRED/activated RECOMMENDED pending/in-progress/RED blocks terminal Card completion.
- Expected behavior: A Card whose stable contract requires review cannot become terminal DONE, and cannot enter Close, until the exact current result has a valid GREEN attempt. Missing, pending/in-progress, RED, stale, or otherwise invalid review state must keep terminal completion blocked or route recovery/correction.
- Actual behavior: `validate_board` requires a DONE Card to have a result locator but does not read its Card contract, result, review requirement, or review attempts. `select_route` performs those checks only for `in_progress` Cards. If every Card is marked `done`, the selector routes directly to `close` without reading the Card contract/result/review history. A Card with `Review requirement: required` and no attempt therefore reaches Close; the same structural bypass can hide a lingering RED/pending attempt on a DONE Card.
- Minimal reproduction: Materialize a valid semantic result and a stable Card with `Review requirement: required`, create no review attempt, then change only the Board status from `in_progress` to `done`. The selector returns `route/close`. Preserved in `repros/adversarial_router_cases.py::case_f2_done_required_without_green_routes_close`.
- Why this is materially load-bearing: This converts mutable Board status into a bypass around the mandatory independent review gate and can advance an unreviewed or explicitly failed implementation into final integration/Close.
- Defect class / likely siblings: Terminal-state validation that trusts status before validating the obligations required to make that status legal. Siblings are DONE Cards with pending/in-progress/RED/stale review attempts or malformed result/review content that is never read on the all-DONE branch.
- Existing tests that failed to catch it: `test_required_review_blocks_until_green_then_routes_finalization` covers only an `in_progress` Card. `test_all_terminal_cards_route_to_close_not_directly_to_stop` deliberately uses `review_requirement="none"` before setting DONE. There is no DONE + REQUIRED/non-GREEN negative-space test.
- Reproduction artifact, if any: `audits/swarm/jyxmfic5ggkl2cok7gu7ng4w/repros/adversarial_router_cases.py` (F2).

### S014-F03 — Unrelated active Research preempts unresolved issue authorization

- Source branch: `audit/pwv2-swarm-jyxmfic5ggkl2cok7gu7ng4w`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: review independence / review bypass / result mutation; Close / finalization / end-of-approved-scope; stale commit/blob/path/result/review identity; Research / Intake / tracker / external-side-effect recovery

- Affected workflow contract/invariant: PWV2-REQ-053, PWV2-REQ-054, PWV2-REQ-067/068; `workflow/INTAKE.md` exact issue alignment; `workflow/RESEARCH.md` durable return ownership; router precedence foundation placing explicit human/premium boundaries above research return.
- Expected behavior: An unresolved issue repair boundary remains authoritative: after exact diagnosis prior art is bound, no post-diagnosis response must route to the real `issue_alignment` stop. Before that binding exists, exact Intake-origin prior-art Research for the current repair subject owns the obligation. A contradictory later-stage Research record must not silently preempt that higher-precedence boundary; malformed ordering should fail closed if it cannot be reconciled.
- Actual behavior: `select_route` reads the workstream-level `research` locator before `intake` and immediately returns for Research state `active` or `complete`. It therefore never validates or routes the unresolved Intake state in those cases. A valid issue Intake that would independently produce `stop/issue_alignment` changes to `route/research` simply by adding an unrelated active Brainstorming Research record.
- Minimal reproduction: With the valid fixture, add an active issue Intake for `repair:v1`, an exact persisted diagnosis-prior-art binding, and no user response. Without Research the router returns `stop/issue_alignment`. Add a valid active Research record with `origin_role="brainstorming"`, `origin_subject="unrelated-scope@1"`, and `return_target="brainstorming"`. The router now returns `route/research` for the unrelated subject before reading Intake. Preserved in `repros/adversarial_router_cases.py::case_f3_unrelated_research_preempts_alignment_stop`.
- Why this is materially load-bearing: The issue-repair authorization boundary is explicitly human-owned. A stale/later-stage Research slot can make the router miss that stop and select an obligation from contradictory durable state, violating both human-control and deterministic-precedence guarantees.
- Defect class / likely siblings: Cross-stage precedence without phase/owner compatibility validation. Any active/complete workstream Research can preempt unresolved Intake because the early Research return occurs before Intake validation.
- Existing tests that failed to catch it: `test_issue_without_post_diagnosis_response_is_real_alignment_stop` uses consumed exact Intake Research, which does not early-return. `test_later_brainstorming_research_does_not_erase_issue_diagnosis_prior_art` also uses `state="consumed"`. No test combines unresolved Intake with unrelated active/complete Research.
- Reproduction artifact, if any: `audits/swarm/jyxmfic5ggkl2cok7gu7ng4w/repros/adversarial_router_cases.py` (F3).

### S014-F04 — Implementation Research can return to a nonexistent or empty Card subject

- Source branch: `audit/pwv2-swarm-jyxmfic5ggkl2cok7gu7ng4w`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: review independence / review bypass / result mutation; Close / finalization / end-of-approved-scope; stale commit/blob/path/result/review identity; Research / Intake / tracker / external-side-effect recovery

- Affected workflow contract/invariant: `workflow/RESEARCH.md` exact return ownership, `workflow/RECOVERY.md` implementation Research handoff, router rule that stale/contradictory bindings fail closed.
- Expected behavior: Task-Board-owned implementation/recovery Research must return once to the exact durable owner that initiated it. The execution return subject must be non-empty and bound to the initiating/current Card (or another explicitly valid durable execution owner); a stale, nonexistent, or contradictory target must route Recovery.
- Actual behavior: `validate_research` treats any string beginning with `execution_resolution:`, `execution_prep:`, or `execution:` as a valid execution return target. It does not require a non-empty suffix and does not bind that suffix to `origin_subject` or a Card on the selected Board. For complete Board Research, the router derives both obligation and subject solely from that prefix/suffix. Thus `origin_subject="M01-T04"` + `return_target="execution:M99-T99"` routes to Execution for nonexistent `M99-T99`; `return_target="execution:"` routes to Execution with an empty subject.
- Minimal reproduction: Point the valid Board's `research_obligation` at a complete Research record with `origin_role="execution_resolution"`, `origin_subject="M01-T04"`, and first `return_target="execution:M99-T99"`, then `return_target="execution:"`. Both records validate and route to `execution`, with subject `M99-T99` and `""` respectively. Preserved in `repros/adversarial_router_cases.py::case_f4_execution_research_accepts_wrong_or_empty_card_subject`.
- Why this is materially load-bearing: Recovery can resume work under the wrong or nonexistent Card after a factual handoff, breaking exact return ownership and potentially escaping the authority/acceptance surface of the blocked/current Card.
- Defect class / likely siblings: Prefix-only typed locator validation without referential integrity. Siblings are stale execution return targets after Card evolution and mismatches among `origin_role`, `origin_subject`, return obligation, and Board membership.
- Existing tests that failed to catch it: `test_task_board_research_return_is_recovered_before_execution` only supplies matching `execution_resolution:M01-T04`. State-contract Research tests cover non-execution return owners and do not exercise empty/nonexistent/mismatched execution suffixes.
- Reproduction artifact, if any: `audits/swarm/jyxmfic5ggkl2cok7gu7ng4w/repros/adversarial_router_cases.py` (F4).

#### S014 source coverage

The audit remained bound to `elmakus/project_workflow_v2@4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`. I inspected the canonical router/state/review/recovery/execution/Execution Prep/Close/Intake/Research/GitHub-Issues modules; the approved V2 requirements; production `router.py`, `state_contract.py`, `execution_contract.py`, `recovery_contract.py`, `review_contract.py`, and `close_contract.py`; router/state/Close tests; and the exact router/state fixtures needed for negative-space construction.

The four selected attack lenses were all exercised:
- review independence / review bypass / result mutation: F1, F2;
- Close / finalization / end-of-approved-scope: F2 plus all-DONE/JIT negative space;
- stale commit/blob/path/result/review identity: F1;
- Research / Intake / tracker / external-side-effect recovery: F3, F4, plus tracker/external-effect contract inspection.

I did not inspect `audit/*` branches, swarm reports, GitHub Issues, or PR comments before freezing the finding set. The finding set was frozen as F1–F4 before any historical-comparison step.

#### S014 original confidence and limitations

Confidence is high in the source-level counterexamples: each follows a concrete selector/validator branch and the existing tests demonstrate the omitted negative-space dimension. The preserved repro script imports the production selector and mutates only temporary copies of the repository's own valid fixture.

I could not execute the preserved repro script in this session. The sandbox could not resolve GitHub for an exact checkout, and the connected remote-command environment reported its monthly command quota exhausted and explicitly prohibited retries. I therefore did not claim an executed PASS/FAIL transcript; the reproductions are source-mechanical and ready to run against the exact subject/audit branch.

A GitHub commit-metadata fetch for the exact audit subject returned the merge commit's own diff, which included workstream bookkeeping/evidence text. That material was not used as a defect checklist, and no audit reports, tracker discussions, Issues, or PR comments were consulted. Findings F1–F4 were derived from canonical workflow contracts, production helpers/selectors, tests, and fixtures.


## S015 — audit/pwv2-swarm-k7m2q9v4x1c8n5r0t6w3z8pa

### S015-F01 — Explicit user stop is bypassed after the planning gate reaches a live Task Board

- Source branch: `audit/pwv2-swarm-k7m2q9v4x1c8n5r0t6w3z8pa`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: router precedence / unreachable branches / conflicting obligations; stale commit/blob/path/result/review identity; RED / recovery / blocker / interrupted-runtime continuation; helper vs documented semantics / parity drift

- Affected workflow contract/invariant: PWV2-REQ-068 requires an explicit user stop to be a real stop; workflow/ROUTER.md places explicit human/premium boundaries above current-card work.
- Expected behavior: If durable Brainstorming carries explicit_user_stop = true, continuation must stop there, or fail closed to Recovery if the co-bound downstream state makes that combination contradictory. It must never continue into implementation.
- Actual behavior: tools/router.py checks brainstorm["explicit_user_stop"] only inside the branch guarded by not plan_gate_passed_with_board. An approved plan with satisfied C and a Task Board sets plan_gate_passed_with_board = true, so the explicit stop is never examined and the board can route directly to Execution, Review, or Close.
- Minimal reproduction: In the stock router fixture, install the normal promoted GREEN Definition, approved GREEN-reviewed plan with premium C satisfied, keep the fixture Task Board with M01-T04 in_progress, then change only BRAINSTORM.toml from explicit_user_stop = false to true. select_route still reaches the Task Board and returns route/execution rather than a stop or Recovery.
- Why this is materially load-bearing: A durable human-owned stop can be silently crossed into implementation. This is a direct authority/precedence violation, not merely a diagnostic inconsistency.
- Defect class / likely siblings: Any high-precedence pre-execution stop whose check is conditionally skipped once plan_gate_passed_with_board is true should be audited for the same precedence inversion.
- Existing tests that failed to catch it: tests/test_router.py exercises co-bound approved-plan/Task-Board precedence but its Brainstorming fixtures use explicit_user_stop = false; there is no explicit-user-stop=true co-bound downstream case.
- Reproduction artifact, if any: repros/router_adversarial_repros.py::repro_explicit_user_stop_bypass

### S015-F02 — A DONE Card can bypass a REQUIRED review and route to Close

- Source branch: `audit/pwv2-swarm-k7m2q9v4x1c8n5r0t6w3z8pa`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: router precedence / unreachable branches / conflicting obligations; stale commit/blob/path/result/review identity; RED / recovery / blocker / interrupted-runtime continuation; helper vs documented semantics / parity drift

- Affected workflow contract/invariant: PWV2-REQ-036 and workflow/REVIEW.md require REQUIRED/activated RECOMMENDED review to block terminal Card completion until exact GREEN.
- Expected behavior: A Card marked done while its stable Task Card requires review but no exact GREEN attempt exists is contradictory durable state and must fail closed or recover the missing review/finalization obligation. It must not be accepted as terminal.
- Actual behavior: validate_board checks only that a done Card has a result locator. Review requirement/history is validated only inside the router's active in_progress Card branch. If every Card is marked done, the router skips all result/review validation and returns route/close.
- Minimal reproduction: Use install_reviewable_result(project, "required") on the stock fixture, verify the active state routes to review_freeze, then change only status = "in_progress" to status = "done". With no review attempt at all, select_route returns route/close.
- Why this is materially load-bearing: Canonical state can assert terminal completion without satisfying a mandatory independent review gate, allowing Close/integration to proceed from an illegally finalized Card.
- Defect class / likely siblings: DONE Cards with no attempts, pending attempts, RED attempts, stale GREEN subjects, malformed result contents, or path-only result identity are all outside the active-card validation path.
- Existing tests that failed to catch it: test_required_review_blocks_until_green_then_routes_finalization covers only an in_progress Card. test_all_terminal_cards_route_to_close_not_directly_to_stop uses Review requirement: none and therefore does not test the blocking invariant.
- Reproduction artifact, if any: repros/router_adversarial_repros.py::repro_done_required_review_bypass

### S015-F03 — Claimed immutable result/dependency Git identity is compared as strings but never verified against bytes

- Source branch: `audit/pwv2-swarm-k7m2q9v4x1c8n5r0t6w3z8pa`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: router precedence / unreachable branches / conflicting obligations; stale commit/blob/path/result/review identity; RED / recovery / blocker / interrupted-runtime continuation; helper vs documented semantics / parity drift

- Affected workflow contract/invariant: workflow/STATE.md says READY dependency inputs are bound by path + immutable commit/blob identity and that missing, stale, or same-path-changed inputs fail closed; workflow/REVIEW.md requires exact immutable review subjects; PWV2-REQ-034 and PWV2-REQ-063 depend on exact subject freshness.
- Expected behavior: Before launch or GREEN reuse/finalization, the implementation must prove that the bytes being consumed are the bytes identified by the claimed commit/blob. Changing the file at the same path without changing the persisted identity must not preserve validity.
- Actual behavior: refresh_ready_card checks only that the dependency's persisted (path, commit, blob) tuple equals the DONE predecessor's persisted tuple, then reads the current path without hashing/resolving it. Active-result recovery similarly parses the current result file but constructs current_subject only from the unchanged locator strings. A changed current file therefore inherits the old immutable identity and a prior GREEN review can still match.
- Minimal reproduction: (a) create a REQUIRED result plus GREEN review, then change only the result file contents while leaving its board commit/blob and review subject unchanged; select_route still returns post_review_finalization. (b) create a READY Card with an exact predecessor dependency, then change only the predecessor result file contents while leaving both exact tuples untouched; select_route still returns execution_prep.
- Why this is materially load-bearing: Stale or replaced content can be executed/finalized under review/dependency proof belonging to different bytes. This defeats the principal safety property of exact immutable subjects.
- Defect class / likely siblings: Planning and Plan Review subject keys also validate only syntactic 40-hex identity; result locators may even omit commit/blob entirely when both fields are absent. Every consumer that treats persisted Git strings as proof without resolving the Git object is in the same class.
- Existing tests that failed to catch it: test_changed_result_after_terminal_review_requires_new_attempt changes the board blob string; test_ready_card_stale_dependency_fails_closed_before_launch changes the predecessor commit/blob strings as well as the file. Neither tests same-path byte mutation with unchanged claimed identity.
- Reproduction artifact, if any: repros/router_adversarial_repros.py::repro_result_bytes_change_under_green and repro_ready_dependency_bytes_change

### S015-F04 — Mutable path-only Task Card acceptance can rewrite the review gate after implementation

- Source branch: `audit/pwv2-swarm-k7m2q9v4x1c8n5r0t6w3z8pa`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: router precedence / unreachable branches / conflicting obligations; stale commit/blob/path/result/review identity; RED / recovery / blocker / interrupted-runtime continuation; helper vs documented semantics / parity drift

- Affected workflow contract/invariant: workflow/EXECUTION_PREP.md defines the Task Card as stable authority; workflow/REVIEW.md says each attempt binds the exact acceptance surface; workflow/EXECUTION_PREP.md forbids silently rewriting an in-progress Card through refinement.
- Expected behavior: Once an in-progress/result-bearing Card's stable acceptance/review contract is established, changing its scope, acceptance, tests, or review requirement must invalidate the old execution/review state unless the change is explicitly reconciled as a new exact acceptance subject.
- Actual behavior: Task Board Card contracts and review acceptance identities carry only a Task Card path. They have no commit/blob identity. The active-result router reparses whatever bytes are currently at that path. Rewriting Review requirement: required to none at the same path immediately changes routing from review_freeze to result_reconciliation without any durable authority transition; a previous GREEN review likewise has no immutable Card-acceptance identity to compare.
- Minimal reproduction: Install a result whose Task Card says Review requirement: required and observe review_freeze. Modify only that same Card file to Review requirement: none, leaving Board/result state unchanged. select_route now returns result_reconciliation.
- Why this is materially load-bearing: A mutable file rewrite can downgrade or alter the gate that controls acceptance of already-produced implementation, bypassing independent review without changing canonical Card identity.
- Defect class / likely siblings: Any post-start mutation of Included scope, Excluded scope, Acceptance, Required tests/readback, authority refs, dependencies, or review requirement at the same Card path is not cryptographically distinguishable by review acceptance.
- Existing tests that failed to catch it: test_task_card_review_acceptance_is_exact_and_semantic validates a path-only Task Card acceptance as sufficient; active-review router tests assume the Card file does not change after the result is produced.
- Reproduction artifact, if any: repros/router_adversarial_repros.py::repro_task_card_review_downgrade

### S015-F05 — Implementation Research can return to a nonexistent or wrong Card subject

- Source branch: `audit/pwv2-swarm-k7m2q9v4x1c8n5r0t6w3z8pa`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: router precedence / unreachable branches / conflicting obligations; stale commit/blob/path/result/review identity; RED / recovery / blocker / interrupted-runtime continuation; helper vs documented semantics / parity drift

- Affected workflow contract/invariant: workflow/RECOVERY.md requires Task-Board-owned Research to recover an exact Research obligation and return target before unrelated execution, with the Research record owning the exact origin and once-only return owner; workflow/ROUTER.md requires stale/contradictory bindings to fail closed.
- Expected behavior: An execution_* Research return target must be bound to the originating/current workstream Card and compatible owner. A stale or nonexistent Card subject must route Recovery rather than manufacture a deterministic continuation.
- Actual behavior: validate_research accepts any nonempty suffix after execution_resolution:, execution_prep:, or execution:. The router maps the prefix to an obligation and returns the suffix as subject without checking that it equals origin_subject, identifies any Card on the selected Task Board, or is compatible with origin_role/current Card.
- Minimal reproduction: On the stock active M01-T04 board, install a complete Task-Board Research record, then change only return_target from execution_resolution:M01-T04 to execution_resolution:M99-T99. select_route returns route/execution_resolution with subject M99-T99 instead of Recovery.
- Why this is materially load-bearing: Recovery can abandon the real active Card and select a fabricated/stale owner, violating deterministic durable recovery and potentially skipping the actual corrective obligation.
- Defect class / likely siblings: Mismatches between origin_role and return-target prefix, origin_subject and return-target suffix, or suffix and Task Board membership are all accepted by the same loose prefix check.
- Existing tests that failed to catch it: test_task_board_research_return_is_recovered_before_execution uses only the matching execution_resolution:M01-T04 target and has no wrong/nonexistent-owner variant.
- Reproduction artifact, if any: repros/router_adversarial_repros.py::repro_research_return_to_nonexistent_card

### S015-F06 — Terminal GREEN/RED review evidence may point to a nonexistent artifact

- Source branch: `audit/pwv2-swarm-k7m2q9v4x1c8n5r0t6w3z8pa`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: router precedence / unreachable branches / conflicting obligations; stale commit/blob/path/result/review identity; RED / recovery / blocker / interrupted-runtime continuation; helper vs documented semantics / parity drift

- Affected workflow contract/invariant: workflow/REVIEW.md requires durable verdict evidence for terminal attempts; workflow/ROUTER.md says invalid/missing bindings fail closed.
- Expected behavior: A terminal attempt's evidence locator must resolve to durable evidence of the correct class/scope before GREEN can authorize finalization.
- Actual behavior: validate_review requires terminal evidence_path to be merely a nonempty safe relative string. It does not require the path to exist, be workstream-local, or reside under the evidence root, and the router never reads that evidence before post_review_finalization. The same structural issue exists in Plan Review validation.
- Minimal reproduction: Create a REQUIRED result plus GREEN implementation review, then change only evidence_path in the review record to missing/review.md and ensure that path does not exist. select_route still returns post_review_finalization.
- Why this is materially load-bearing: A terminal verdict can authorize finalization without the durable evidence the review contract explicitly requires, weakening recovery/audit integrity and allowing fabricated evidence locators.
- Defect class / likely siblings: RED implementation attempts and terminal Plan Review attempts use the same nonempty-path pattern; cross-workstream or unrelated existing paths are also not semantically constrained.
- Existing tests that failed to catch it: state-contract tests check that terminal evidence_path is nonempty but do not require existence/class binding. Router helper add_review_attempt normally creates the referenced evidence, so routing tests do not exercise a missing target.
- Reproduction artifact, if any: repros/router_adversarial_repros.py::repro_missing_green_review_evidence

#### S015 source coverage

The audit remained bound to commit 4fb4bfb7d7b1481d6f347c182fc96a5a1135e045. I inspected the canonical router/recovery/review/state/execution/execution-prep/planning/plan-review/close contracts, accepted requirements, production router/state/recovery/execution/close helpers, templates, bootstrap Skill/SessionStart/plugin metadata, and the relevant router/state/execution/recovery/close tests and fixtures.

The selected attack lenses were exercised as follows:
- router precedence / unreachable branches / conflicting obligations: F1, F2;
- stale commit/blob/path/result/review identity: F3, F4, F6;
- RED / recovery / blocker / interrupted-runtime continuation: F2, F5, F6;
- helper vs documented semantics / parity drift / negative space: all findings, especially F2-F6.

I intentionally did not inspect audit/* branches, swarm reports, GitHub Issues/PR comments, or historical workstream evidence/review diagnosis narratives before freezing the finding set.

#### S015 original confidence and limitations

Confidence is high for F1-F6 because each follows a concrete accepted contract invariant and a direct reachable branch in the exact production selector/validator at the audit commit, with negative-space coverage identified in the exact test suite.

A runnable checkout was not available in the audit environment: the local container could not resolve github.com, the authorized Remote Desktop Commander had exhausted its monthly execution allowance, and the outer command bridge was unavailable to this turn. I therefore could not execute pytest or the preserved reproduction script in this session. The reproduction artifact calls the real tools.router.select_route against the repository's existing router fixtures/helpers and is intended for deterministic execution in any checkout of the audited commit; no product code changes are required.


## S016 — audit/pwv2-swarm-k7m2q9v4x1c8n6r0t5h3p2zb

### S016-F01 — DONE state bypasses result and required-review validation before Close

- Source branch: `audit/pwv2-swarm-k7m2q9v4x1c8n6r0t5h3p2zb`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: malformed or contradictory state / fail-closed behavior; stale commit/blob/path/result/review identity; Close / finalization / end-of-approved-scope; helper vs documented semantics / parity drift

- Affected workflow contract/invariant: workflow/STATE.md and workflow/REVIEW.md require REQUIRED/activated RECOMMENDED review to block terminal completion until exact GREEN, while workflow/ROUTER.md requires invalid/missing/stale/contradictory binding to fail closed and workflow/CLOSE.md assumes accepted terminal truth.
- Expected behavior: A Card may reach Close only after its durable result and all required review state are validated. A done Card with no review attempt, a pending/RED review, or an unreadable/stale result must route to review/recovery rather than Close.
- Actual behavior: validate_board() only requires a result locator when status = "done"; it does not read the Task Card, result artifact, or review attempts. After active/blocked/READY checks, select_route() returns route/close when every Card is done, again without reading those artifacts. Merely flipping the Board status to done can therefore bypass required review and result integrity.
- Minimal reproduction: Start from the router fixture, install a valid Task Card with Review requirement: required and a result locator, leave review_attempts empty, change the Card status from in_progress to done, then call select_route(). The production path returns route/close.
- Why this is materially load-bearing: It permits workflow finalization/integration entry without the blocking independent-review gate and without proving the terminal result is valid.
- Defect class / likely siblings: Terminal-state trust without semantic validation; siblings include done plus pending/RED review, path-only/missing result identity, or a result file that disappeared after Board mutation.
- Existing tests that failed to catch it: test_all_terminal_cards_route_to_close_not_directly_to_stop uses a no-review result. Required-review lifecycle tests keep the Card in_progress, so no test combines done with an unsatisfied review obligation.
- Reproduction artifact, if any: repros/reproduce_findings.py (F1).

### S016-F02 — Immutable result/dependency blob identities are trusted as metadata, not verified against bytes

- Source branch: `audit/pwv2-swarm-k7m2q9v4x1c8n6r0t5h3p2zb`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: malformed or contradictory state / fail-closed behavior; stale commit/blob/path/result/review identity; Close / finalization / end-of-approved-scope; helper vs documented semantics / parity drift

- Affected workflow contract/invariant: workflow/STATE.md, workflow/EXECUTION_PREP.md, and workflow/RECOVERY.md require exact path+commit+blob identity and explicitly require same-path-changed dependency inputs to fail closed; GREEN finalization must cover the exact still-current result.
- Expected behavior: Before launch or GREEN finalization, the selector must establish that the current artifact bytes at the named path are the bytes identified by the claimed immutable Git blob/commit.
- Actual behavior: READY dependency refresh checks only that the Card's (path, commit, blob) tuple equals metadata stored on a DONE predecessor, then merely reads the current path. Active-result recovery similarly reads/parses the current result but derives the current review subject from Board metadata; no code hashes or resolves the current artifact against the claimed blob/commit. If bytes change in place while metadata remains unchanged, launch/finalization still proceeds.
- Minimal reproduction: (a) Create a READY Card whose dependency tuple matches a DONE predecessor; mutate only the dependency result file bytes, leaving both locators unchanged; select_route() still returns execution_prep. (b) Create an in_progress result with exact GREEN review; mutate only the result file bytes while keeping Board and review subject metadata unchanged; the selector still returns post_review_finalization.
- Why this is materially load-bearing: Exact immutable identity is the basis for stale-input rejection, review coverage, recovery truth, and no-replay semantics. Metadata-only equality lets changed content masquerade as the reviewed/depended-on blob.
- Defect class / likely siblings: Unverified Git-object identity. Likely siblings are every transition that compares commit/blob strings without resolving the named Git object/path bytes.
- Existing tests that failed to catch it: test_ready_card_stale_dependency_fails_closed_before_launch changes the Board commit/blob metadata together with file content, so it tests locator disagreement rather than same-path byte drift. test_changed_result_after_terminal_review_requires_new_attempt likewise changes Board blob metadata instead of current result bytes.
- Reproduction artifact, if any: repros/reproduce_findings.py (F2a/F2b).

### S016-F03 — READY Card with a durable result is relaunched instead of recovered from result truth

- Source branch: `audit/pwv2-swarm-k7m2q9v4x1c8n6r0t5h3p2zb`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: malformed or contradictory state / fail-closed behavior; stale commit/blob/path/result/review identity; Close / finalization / end-of-approved-scope; helper vs documented semantics / parity drift

- Affected workflow contract/invariant: workflow/STATE.md, workflow/EXECUTION.md, and workflow/RECOVERY.md say a durable valid semantic result is recovery truth and prevents implementation replay solely because runtime state disappeared.
- Expected behavior: If a selected Card already carries a valid durable result, continuation must start from result reconciliation/review/finalization, regardless of stale mutable execution status; it must not prepare the implementation for launch again.
- Actual behavior: validate_board() permits a result locator on a ready Card. select_route() considers durable results only inside the in_progress branch. The later single-READY branch calls refresh_ready_card() and returns route/execution_prep without checking card["result"].
- Minimal reproduction: Convert the fixture Card to ready, give it a valid stable Card/authority plus a valid durable result locator/artifact, and invoke select_route(). It returns route/execution_prep, not result_reconciliation.
- Why this is materially load-bearing: A stale status bit can cause already-completed implementation to be replayed, violating the durable-recovery guarantee and potentially duplicating mutations.
- Defect class / likely siblings: Result-recovery precedence is conditional on mutable Card status. planned/blocked result-bearing states deserve the same negative-space scrutiny.
- Existing tests that failed to catch it: Result-reconciliation tests use in_progress; READY tests use Cards without durable results. No test crosses the two state dimensions.
- Reproduction artifact, if any: repros/reproduce_findings.py (F3).

### S016-F04 — GREEN review acceptance is path-only, so same-path Task Card changes retain stale approval

- Source branch: `audit/pwv2-swarm-k7m2q9v4x1c8n6r0t5h3p2zb`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: malformed or contradictory state / fail-closed behavior; stale commit/blob/path/result/review identity; Close / finalization / end-of-approved-scope; helper vs documented semantics / parity drift

- Affected workflow contract/invariant: workflow/REVIEW.md requires each attempt to bind one exact acceptance surface and says GREEN finalization is only for the exact current subject plus acceptance; workflow/ROUTER.md requires stale bindings to fail closed.
- Expected behavior: If the stable Task Card acceptance changes after a review attempt was frozen/GREEN, that review cannot authorize finalization of the changed acceptance surface.
- Actual behavior: validate_review() validates Task Card acceptance only as a workstream-local path whose filename matches card_id; no immutable acceptance commit/blob is stored or checked. During active-result routing, select_route() validates review history and exact result subject but never verifies that current Task Card bytes still equal the acceptance reviewed by the attempt. Same-path acceptance edits leave GREEN reusable.
- Minimal reproduction: Create an in_progress required-review result and GREEN attempt, confirm post_review_finalization, edit only the Task Card's Acceptance: text at the same path while retaining a valid Card, and route again. The selector still returns post_review_finalization.
- Why this is materially load-bearing: It allows an independent GREEN verdict to authorize materially different acceptance criteria than the reviewer evaluated.
- Defect class / likely siblings: Mutable path-only acceptance identity / review bypass.
- Existing tests that failed to catch it: Review tests bind and compare result subject identity but do not mutate the acceptance Card at the same path after review.
- Reproduction artifact, if any: repros/reproduce_findings.py (F4).

### S016-F05 — Accepted Card results do not prove an exact implementation subject or durable evidence

- Source branch: `audit/pwv2-swarm-k7m2q9v4x1c8n6r0t5h3p2zb`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: malformed or contradictory state / fail-closed behavior; stale commit/blob/path/result/review identity; Close / finalization / end-of-approved-scope; helper vs documented semantics / parity drift

- Affected workflow contract/invariant: workflow/EXECUTION.md defines an accepted semantic result as carrying an exact implementation subject plus durable evidence refs and verified tests/readback; workflow/STATE.md treats a valid result as recovery truth.
- Expected behavior: A malformed/non-immutable implementation subject or evidence locator that does not resolve to durable evidence must not be accepted as semantic completion.
- Actual behavior: parse_card_result() requires only that Implementation subject be a non-empty string. Evidence refs are checked only for a syntactically workstream-local .md path; neither the parser nor result-routing path requires that those evidence files exist. A result with Implementation subject: definitely-not-an-immutable-git-subject and a nonexistent evidence path parses successfully and an in_progress, no-review Card advances to result_reconciliation.
- Minimal reproduction: Replace the fixture's result text with a valid Card ID, arbitrary nonempty implementation-subject text, a workstream-local but nonexistent evidence .md path, and nonempty tests summary; call select_route().
- Why this is materially load-bearing: Such a record can become durable no-replay/recovery truth without identifying what was implemented or preserving the evidence claimed to justify acceptance.
- Defect class / likely siblings: Semantic result validation is syntactic rather than identity/evidence validating.
- Existing tests that failed to catch it: test_result_rejects_runtime_identity_and_cross_workstream_evidence covers forbidden field names and cross-workstream paths, but not implementation-subject grammar/identity or evidence existence.
- Reproduction artifact, if any: repros/reproduce_findings.py (F5). An isolated execution of the exact parse_card_result() logic from the audited blob accepted this malformed subject and nonexistent evidence locator.

#### S016 source coverage

The audit remained bound to commit 4fb4bfb7d7b1481d6f347c182fc96a5a1135e045. Inspected canonical modules included workflow/ROUTER.md, STATE.md, EXECUTION_PREP.md, EXECUTION.md, REVIEW.md, RECOVERY.md, PLANNING.md, PLAN_REVIEW.md, CLOSE.md, BRAINSTORMING.md, and USER_STOP.md; executable code included tools/router.py, state_contract.py, execution_contract.py, review_contract.py, recovery_contract.py, and close_contract.py; test coverage included router, state, execution, review/recovery and Close tests/fixtures plus schemas/STATE_ENVELOPE.md.

The selected lenses were exercised as follows: malformed/contradictory fail-closed behavior (F1, F3, F5); stale commit/blob/path/result/review identity (F2, F4); Close/finalization/end-of-scope (F1, F2, F4); helper/documented-semantics parity and negative space (all findings, with emphasis on test cases that mutate a dimension the existing test keeps constant).

No audit/* branch/report, GitHub Issue, or PR-comment corpus was intentionally inspected. No historical comparison was performed after freeze.

#### S016 original confidence and limitations

Confidence is high in the five code-path defects because each is a direct mismatch between canonical contracts and reachable production branches/validators, and the supplied reproduction script uses the repository's real selector plus existing fixture helpers without modifying product code.

A full exact-checkout selector run was not available in this session: container Git access could not resolve GitHub, and the connected remote terminal reported its monthly command quota exhausted. The exact parse_card_result() implementation was separately executed in isolation and accepted the F5 malformed subject/nonexistent evidence case. The remaining selector reproductions are preserved for direct execution from an exact checkout but were not run here.

During initial target-SHA verification, the GitHub commit-metadata response automatically included the merge diff, which itself contained historical workstream evidence/review text. That disclosure occurred before the finding set was frozen despite the intended blindness boundary. I did not inspect audit/*, Issues/PR comments, or use those historical conclusions as a defect checklist; the five frozen findings above were derived from canonical workflow/code/test behavior. This transport-level disclosure is the principal independence limitation.


## S017 — audit/pwv2-swarm-k7m2v9q4x1n8c5r0t6p3b2d9

### S017-F01 — GREEN review can finalize content that no longer matches the declared reviewed blob

- Source branch: `audit/pwv2-swarm-k7m2v9q4x1n8c5r0t6p3b2d9`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: review independence/bypass/result mutation; Close/finalization/end-of-approved-scope; Research/Intake/tracker/external-side-effect recovery; path traversal/locator safety/cross-workstream binding

Affected workflow contract/invariant:
PWV2-REQ-034; `workflow/REVIEW.md` exact immutable review subject; `workflow/ROUTER.md` exact-GREEN and stale-binding fail-closed rules; `workflow/STATE.md` current exact result/dependency identity.

Expected behavior:
Before a GREEN attempt authorizes post-review finalization, the production router must establish that the current durable result bytes are the exact Git blob identified by the Card result locator and review subject. A same-path content change after review must require a new exact attempt or fail closed.

Actual behavior:
`tools/router.py` reads and parses the current result file, but constructs `current_subject` only from the Task Board's declared `path/commit/blob`. It never hashes the current file or verifies the declared commit/blob against repository content. If the result file changes while the locator remains unchanged, `review_subject(attempt) == current_subject` still holds and GREEN routes to `post_review_finalization`.

Minimal reproduction:
Create an in-progress Card with REQUIRED review, a result locator declaring blob B, and a GREEN review attempt for blob B. Then edit only the result file at the same path while leaving the Board locator and review subject untouched. `select_route(...)` still returns `route/post_review_finalization`.

Why this is materially load-bearing:
The exact-subject review gate can authorize terminal finalization of implementation content that was never reviewed. This is a direct review bypass, not merely stale metadata display.

Defect class / likely siblings:
Stale immutable-identity trust / fail-open on declared locator metadata. The same pattern is present in READY dependency refresh: dependency equality is checked against Board metadata, but the current predecessor result bytes are not verified against the declared blob.

Existing tests that failed to catch it:
`test_changed_result_after_terminal_review_requires_new_attempt` changes the Board's declared blob, so the mismatch is visible. `test_ready_card_stale_dependency_fails_closed_before_launch` changes both Board identity and file content. Neither covers content-only drift with unchanged locator metadata.

Reproduction artifact, if any:
`audits/swarm/k7m2v9q4x1n8c5r0t6p3b2d9/repros/repro_findings.py::f01_result_content_swap_after_green`

### S017-F02 — GREEN review does not bind an immutable acceptance surface

- Source branch: `audit/pwv2-swarm-k7m2v9q4x1n8c5r0t6p3b2d9`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: review independence/bypass/result mutation; Close/finalization/end-of-approved-scope; Research/Intake/tracker/external-side-effect recovery; path traversal/locator safety/cross-workstream binding

Affected workflow contract/invariant:
PWV2-REQ-021, PWV2-REQ-038; `workflow/REVIEW.md` requirement that each attempt bind one exact acceptance surface; exact final subject/acceptance coverage semantics.

Expected behavior:
Changing the Task Card acceptance/tests after a GREEN implementation review must invalidate that review coverage or require a new exact attempt for the changed acceptance surface.

Actual behavior:
A Card review stores `[acceptance] class = "task_card", path = "..."` with no commit/blob identity. During routing the current Task Card is reparsed, but no immutable acceptance key is compared with the attempt. The same GREEN attempt therefore remains valid after material acceptance or required-test changes at the same Task Card path.

Minimal reproduction:
Create a REQUIRED-review Card result plus GREEN attempt. After GREEN, edit only the Task Card's `Acceptance` or `Required tests/readback` field, keeping its path unchanged. `select_route(...)` still returns `route/post_review_finalization`.

Why this is materially load-bearing:
A reviewer may approve one acceptance contract while finalization occurs under a different one. The gate therefore does not prove the result satisfies the acceptance surface that is current at completion time.

Defect class / likely siblings:
Stale acceptance identity / path-only mutable locator. Similar risk applies anywhere review coverage is represented by a mutable path without immutable content identity.

Existing tests that failed to catch it:
Review lifecycle tests keep the Task Card unchanged across review and finalization. There is no regression that mutates acceptance after GREEN while preserving the acceptance path.

Reproduction artifact, if any:
`audits/swarm/k7m2v9q4x1n8c5r0t6p3b2d9/repros/repro_findings.py::f02_acceptance_surface_changes_after_green`

### S017-F03 — Research can return to a different semantic owner and bypass issue alignment

- Source branch: `audit/pwv2-swarm-k7m2v9q4x1n8c5r0t6p3b2d9`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: review independence/bypass/result mutation; Close/finalization/end-of-approved-scope; Research/Intake/tracker/external-side-effect recovery; path traversal/locator safety/cross-workstream binding

Affected workflow contract/invariant:
PWV2-REQ-049; `workflow/RESEARCH.md` exact durable return ownership and “Research never selects a different target by itself”; `workflow/INTAKE.md` issue-alignment boundary; `workflow/ROUTER.md` active/completed Research -> exact return owner and issue-without-response -> alignment stop.

Expected behavior:
`origin_role` and `return_target` must be mutually consistent. In particular, Intake-origin diagnosis Research must return to Intake before any later stage can run.

Actual behavior:
`validate_research` validates `origin_role` and `return_target` independently but never requires their pairing. A record with `origin_role = "intake"` and `return_target = "definition"` is valid. Because `tools/router.py` processes completed Research before Intake, it immediately routes that record to Definition and never evaluates the pending issue-alignment obligation.

Minimal reproduction:
Attach an active/pending issue Intake record and a completed Research record with the same repair subject, `origin_role = "intake"`, but `return_target = "definition"`. The production selector returns `route/definition` rather than the Intake-owned prior-art/alignment obligation.

Why this is materially load-bearing:
A schema-valid contradictory Research record can jump across a mandatory human repair-authorization boundary and select an illegal workflow transition.

Defect class / likely siblings:
Contradictory state accepted / return-owner integrity gap. Execution-owned Research has the same structural weakness because execution origin roles and execution return-target prefixes are not paired.

Existing tests that failed to catch it:
`test_active_and_completed_research_route_to_exact_owner` exercises only matching origin/return pairs. State-contract tests validate legal values and source accounting, not role-target consistency.

Reproduction artifact, if any:
`audits/swarm/k7m2v9q4x1n8c5r0t6p3b2d9/repros/repro_findings.py::f03_research_owner_mismatch_bypasses_intake`

### S017-F04 — The documented Close -> end_of_scope_stop transition is unreachable through the production router

- Source branch: `audit/pwv2-swarm-k7m2v9q4x1n8c5r0t6p3b2d9`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: review independence/bypass/result mutation; Close/finalization/end-of-approved-scope; Research/Intake/tracker/external-side-effect recovery; path traversal/locator safety/cross-workstream binding

Affected workflow contract/invariant:
PWV2-REQ-070; `workflow/ROUTER.md` implemented route “Close -> ... then end-of-scope stop”; `workflow/CLOSE.md` true-end semantics; requirement that every real stop load `workflow/USER_STOP.md`.

Expected behavior:
Once Close proves durable approved-scope completion with no authorized obligation remaining, the production routing path must be able to emit a real `end_of_scope_stop` and load the stop formatter.

Actual behavior:
`tools/router.py` routes an all-DONE Board to `route/close` unconditionally. It does not import or call `close_continuation`, read any durable Close-completion state, or expose an input by which Close completion can become a `RouteResult` stop. Re-running the selector on the same terminal durable state returns `close` again. `tools/close_contract.py` can independently return the string `end_of_scope_stop`, but that helper is not connected to the production selector or USER_STOP loading.

Minimal reproduction:
Make the fixture Card DONE with a valid result. Call `select_route(...)` twice without changing state: both calls return `route/close`. Separately, `close_continuation(approved_scope_durably_complete=True, next_authorized_obligation=False, explicit_authorization_gate_due=False)` returns `end_of_scope_stop`, demonstrating the disconnected semantic branch.

Why this is materially load-bearing:
The canonical selector cannot represent the documented terminal transition. Completion must therefore be inferred manually/out-of-band or Close repeats indefinitely, allowing runtime behavior to become hidden authority over when the workflow actually ends.

Defect class / likely siblings:
Unreachable documented transition / helper-router parity gap / finalization state integration gap.

Existing tests that failed to catch it:
`test_all_terminal_cards_route_to_close_not_directly_to_stop` proves only the first half. `test_end_of_scope_requires_durable_completion` tests the helper in isolation. No end-to-end test proves a terminal durable state can progress through the production selector to a real stop.

Reproduction artifact, if any:
`audits/swarm/k7m2v9q4x1n8c5r0t6p3b2d9/repros/repro_findings.py::f04_close_stop_is_disconnected`

### S017-F05 — Terminal GREEN review can reference nonexistent verdict evidence and still unblock completion

- Source branch: `audit/pwv2-swarm-k7m2v9q4x1n8c5r0t6p3b2d9`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: review independence/bypass/result mutation; Close/finalization/end-of-approved-scope; Research/Intake/tracker/external-side-effect recovery; path traversal/locator safety/cross-workstream binding

Affected workflow contract/invariant:
PWV2-REQ-036; `workflow/REVIEW.md` durable verdict evidence for terminal attempts; `workflow/AUTHORITY.md` fail-closed rule for missing required references.

Expected behavior:
A terminal GREEN/RED attempt must point to durable, readable, correctly scoped evidence. Missing evidence must fail closed before a verdict can affect Card completion.

Actual behavior:
`validate_review` requires only that `evidence_path` be a non-empty safe relative string for terminal verdicts. It neither constrains the path to the workstream evidence root nor verifies that the file exists. `tools/router.py` reads the attempt but never dereferences `evidence_path`. A GREEN attempt naming a nonexistent file therefore routes to `post_review_finalization`.

Minimal reproduction:
Create a valid REQUIRED-review result and GREEN attempt whose `evidence_path` is a nonexistent relative file. Do not create that evidence file. `select_route(...)` still returns `route/post_review_finalization`.

Why this is materially load-bearing:
The blocking review gate can become terminal without the durable evidence the workflow requires for recovery/auditability, and missing required evidence does not fail closed.

Defect class / likely siblings:
Missing reference dereference / under-validated evidence locator. Review-attempt locators themselves are also path-only and rely on writer discipline for append-only immutability.

Existing tests that failed to catch it:
Terminal review tests create the evidence file when constructing GREEN/RED attempts. State validation tests check only non-empty terminal `evidence_path`; no test removes the referenced file or points it outside the workstream evidence directory.

Reproduction artifact, if any:
`audits/swarm/k7m2v9q4x1n8c5r0t6p3b2d9/repros/repro_findings.py::f05_missing_terminal_review_evidence`

#### S017 source coverage

The audit remained bound to `elmakus/project_workflow_v2@4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`; moving `main` was not used as the audit subject. The exact commit tree was enumerated while excluding `audits/*` during blind discovery.

Inspected production semantics included `tools/router.py`, `tools/state_contract.py`, `tools/recovery_contract.py`, `tools/review_contract.py`, `tools/close_contract.py`, `tools/execution_contract.py`, and the matching workflow modules for Router, State, Authority, Intake, Research, Review, GitHub Issues and Close. Relevant requirements, templates, fixtures and regression tests were inspected to establish intended invariants and missing cases.

Selected attack lenses exercised:
- review independence/bypass/result mutation: F1, F2, F5;
- Close/finalization/end-of-approved-scope: F4;
- Research/Intake/tracker/external-side-effect recovery: F3 plus tracker/close contract inspection;
- path traversal/locator safety/cross-workstream binding: F1, F2, F5 and locator validation review.

The repository's existing tests were inspected, including router, state, review, recovery and Close tests. No prior audit report was read before findings were frozen.

#### S017 original confidence and limitations

Confidence is high for F1, F2, F3 and F5 because each follows a direct production validation/routing path with no semantic inference beyond the documented invariant. Confidence is high-to-moderate for F4: the helper clearly implements the terminal decision, but the production selector has no executable or durable integration path to surface that decision as a real stop.

The reproduction script was constructed against the exact repository fixture/API exposed by the audited commit, but an isolated execution runner for the exact checkout was unavailable during this audit session, so the new repro script itself was not executed here. Existing repository tests were inspected but not rerun locally. No post-freeze historical audit comparison was performed.


## S018 — audit/pwv2-swarm-ky3dtpzh88ndw84aq45itmdv

### S018-F01 — DONE Card can bypass unresolved required review and route to Close

- Source branch: `audit/pwv2-swarm-ky3dtpzh88ndw84aq45itmdv`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: malformed or contradictory state / fail-closed behavior; helper vs documented semantics / parity drift / negative space; router precedence / unreachable branches / conflicting obligations; path traversal / locator safety / cross-workstream binding

- Affected workflow contract/invariant: `workflow/STATE.md` and `workflow/REVIEW.md` require REQUIRED/activated RECOMMENDED review to block terminal Card completion until an exact current GREEN verdict; invalid or contradictory durable state must fail closed rather than skip the review gate.
- Expected behavior: A Card whose stable contract requires review cannot be durably terminal while its current review is absent, pending, in progress, RED, or stale. Such contradictory state must be recovered/reconciled; it must not enter Close as terminal work.
- Actual behavior: `validate_board()` accepts `status = "done"` as long as a result locator exists. It validates only the shape of any review-attempt locators and never reads the Card contract or attempt verdict for a DONE Card. `select_route()` performs result/review validation only inside the `in_progress` branch, then later returns `route/close` whenever every Card status is `done`. Therefore a DONE Card with `Review requirement: required` plus a pending or RED attempt reaches Close without reading the Card, result, or review attempt.
- Minimal reproduction: Start from the valid router fixture; add a valid result and a REQUIRED Task Card, attach a pending (or RED) review attempt, and change the Card status from `in_progress` to `done`. The Board passes its structural validation and the selector's all-DONE branch returns Close. The preserved repro script constructs both pending and RED variants.
- Why this is materially load-bearing: Independent review is a blocking integrity gate. A contradictory status bit can currently bypass that gate and make unreviewed or explicitly failed work look terminal to the next workflow phase.
- Defect class / likely siblings: Missing cross-record lifecycle invariants between Card status, result state, stable review requirement, and review history. A sibling is READY plus an already-durable result being accepted as prep state instead of rejected as contradictory.
- Existing tests that failed to catch it: `test_required_review_blocks_until_green_then_routes_finalization` exercises only an `in_progress` Card. `test_all_terminal_cards_route_to_close_not_directly_to_stop` uses `Review requirement: none`. The suite does not cross DONE with REQUIRED + non-GREEN review state.
- Reproduction artifact, if any: `audits/swarm/ky3dtpzh88ndw84aq45itmdv/repros/repro_board_lifecycle.py`

### S018-F02 — Declared commit/blob identity is trusted rather than verified against current Git content

- Source branch: `audit/pwv2-swarm-ky3dtpzh88ndw84aq45itmdv`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: malformed or contradictory state / fail-closed behavior; helper vs documented semantics / parity drift / negative space; router precedence / unreachable branches / conflicting obligations; path traversal / locator safety / cross-workstream binding

- Affected workflow contract/invariant: `workflow/EXECUTION_PREP.md` requires launch refresh to verify each dependency result's exact path + commit/blob identity and says missing/stale or same-path-changed inputs fail closed. `workflow/RECOVERY.md` requires review refresh against the exact current result. `workflow/STATE.md` describes result/dependency identity as immutable recovery truth.
- Expected behavior: Exact result identity must be mandatory where recovery/review/readiness relies on it, and the declared commit/blob must correspond to the actual referenced Git object/content. Changing bytes at the same path while leaving the stored identity unchanged must be detected before launch or finalization.
- Actual behavior: `validate_locator(..., "result")` requires commit+blob only when either key is present; both may be omitted and still validate. Where identity is present, production routing compares only stored strings. `refresh_ready_card()` compares the dependency `(path, commit, blob)` in the Task Card with the tuple copied into a DONE predecessor Board entry, then merely reads the current path; it never proves that the declared commit contains that path/blob or that current bytes match the blob. Review recovery similarly builds `current_subject` from Board locator strings and compares it with review strings, without hashing/reading the Git object identified by those strings. Thus same-path content can change while the declared tuple stays constant and the selector still treats the subject as exact/current. A no-review active result can also reconcile from a path-only result locator.
- Minimal reproduction: For a READY Card, create a DONE predecessor with result tuple `path@aaaa...:bbbb...`, put the same tuple in the dependency field, route once, then modify the dependency result file bytes without changing either stored tuple. The selector takes the same READY -> Execution Prep route. Separately, create a REQUIRED result with a matching GREEN review, mutate the result file bytes while leaving the Board/review tuple unchanged, and the same GREEN finalization route remains selected.
- Why this is materially load-bearing: Immutable subject identity is the anti-staleness boundary for dependency launch, recovery, and review reuse. Trusting two agreeing declarations instead of the Git object they purport to identify lets stale or mutated content inherit authority from an old identity.
- Defect class / likely siblings: Declared-identity equality is substituted for object verification; optional identity on result locators creates helper/router parity drift. Any downstream consumer that treats these strings as proof of immutable Git content is in the same defect class.
- Existing tests that failed to catch it: `test_ready_card_stale_dependency_fails_closed_before_launch` changes the Board's declared commit/blob strings, not the referenced file bytes with unchanged declarations; its accepted baseline uses synthetic 40-hex values. `test_changed_result_after_terminal_review_requires_new_attempt` likewise changes the Board blob string. `test_exact_result_subject_requires_immutable_identity` tests only a helper, while Board validation and the no-review routing path still accept path-only results.
- Reproduction artifact, if any: `audits/swarm/ky3dtpzh88ndw84aq45itmdv/repros/repro_identity_and_evidence.py`

### S018-F03 — Dangling result/review evidence can still authorize post-review finalization

- Source branch: `audit/pwv2-swarm-ky3dtpzh88ndw84aq45itmdv`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: malformed or contradictory state / fail-closed behavior; helper vs documented semantics / parity drift / negative space; router precedence / unreachable branches / conflicting obligations; path traversal / locator safety / cross-workstream binding

- Affected workflow contract/invariant: `workflow/EXECUTION.md` says an accepted semantic result includes durable evidence refs and is validated before durable reconciliation. `workflow/REVIEW.md` requires durable verdict evidence for terminal attempts. These artifacts form the evidence boundary for result acceptance and independent review.
- Expected behavior: Result evidence refs and terminal review evidence must resolve to the required durable workstream-local artifacts before a result is treated as accepted or a GREEN verdict permits finalization. Missing evidence must fail closed.
- Actual behavior: `parse_card_result()` validates only the lexical form of each evidence path; it does not read or verify the evidence target. `validate_review()` requires terminal `evidence_path` to be non-empty and syntactically safe but never checks that it exists. In the active-card route, the router parses the result and review attempt but never reads either the result's evidence refs or the terminal review evidence path before returning `post_review_finalization` for GREEN. Valid-looking dangling paths therefore satisfy the gate.
- Minimal reproduction: Create an `in_progress` REQUIRED Card with a syntactically valid result whose `Evidence refs` points to a nonexistent workstream evidence Markdown file and a matching GREEN review whose `evidence_path` is also nonexistent. The selector can still return post-review finalization; the preserved repro also prints that both evidence targets are absent.
- Why this is materially load-bearing: The workflow can finalize work whose claimed implementation and independent-review evidence is not durable at all. This weakens both recovery truth and the independent review gate from evidence-backed state to unchecked path assertions.
- Defect class / likely siblings: Locator syntax is validated without target existence/identity verification at the semantic transition that consumes it. Similar evidence-only locators should be checked where they become authorization inputs.
- Existing tests that failed to catch it: `tests/test_execution_contract.py` checks evidence path syntax and cross-workstream rejection only. `test_review_terminal_evidence_and_append_only_history` checks empty versus non-empty terminal evidence. Router GREEN tests create evidence files but contain no negative case with a missing target.
- Reproduction artifact, if any: `audits/swarm/ky3dtpzh88ndw84aq45itmdv/repros/repro_identity_and_evidence.py`

### S018-F04 — In-repository symlinks bypass locator class-root confinement

- Source branch: `audit/pwv2-swarm-ky3dtpzh88ndw84aq45itmdv`
- Original verdict context: FINDINGS FOUND
- Selected attack lenses: malformed or contradictory state / fail-closed behavior; helper vs documented semantics / parity drift / negative space; router precedence / unreachable branches / conflicting obligations; path traversal / locator safety / cross-workstream binding

- Affected workflow contract/invariant: `workflow/AUTHORITY.md` requires exact authority/evidence references and fail-closed behavior for wrong-class or cross-workstream references. `workflow/WORKSTREAMS.md` states locators are exact, class-checked, and workstream-bound.
- Expected behavior: A locator declared as `workflow/...`, `requirements/...`, or another accepted class root must resolve to content inside that declared semantic root; a lexical authority path must not alias arbitrary untrusted project content.
- Actual behavior: `validate_locator()` checks the raw path lexically. `Reads._read_path()` then resolves filesystem symlinks and only checks that the resolved target remains somewhere under the broad project/package root. It does not reassert the locator's semantic class/workstream root after resolution. An authority locator such as `workflow/ALIAS.md` therefore passes lexical validation even when `ALIAS.md` is a symlink to `../untrusted/ISSUE_TEXT.md`; `Reads` follows it, consumes the untrusted target, and records only the declared `project:workflow/ALIAS.md` in the read set. A local executable probe of the exact path logic resolved such an alias outside the declared `workflow/` root while still inside the project root.
- Minimal reproduction: Inside a temporary project root, create `untrusted/ISSUE_TEXT.md`, then create `workflow/ALIAS.md -> ../untrusted/ISSUE_TEXT.md`. Validate `workflow/ALIAS.md` as an `authority` locator and read it through production `Reads.project()`. Validation succeeds and the resolved file is the untrusted target.
- Why this is materially load-bearing: Locator class boundaries are authority boundaries. A repository-controlled alias can make content outside an accepted authority root appear to the router as canonical authority, while the read set masks the resolved source path.
- Defect class / likely siblings: Lexical class validation is not preserved across filesystem resolution. The same issue can affect other locator classes where the exact lexical path or class-root prefix is relied on for binding. A platform-specific sibling is backslash traversal when POSIX lexical validation is followed by native Windows path interpretation.
- Existing tests that failed to catch it: `test_missing_cross_workstream_and_escape_locators_fail_closed` covers explicit lexical `../` traversal, and state locator tests cover ordinary cross-workstream strings. No test covers symlink aliases or semantic-root preservation after `resolve()`.
- Reproduction artifact, if any: `audits/swarm/ky3dtpzh88ndw84aq45itmdv/repros/repro_symlink_locator.py`

#### S018 source coverage

The audit remained bound to commit `4fb4bfb7d7b1481d6f347c182fc96a5a1135e045`. I inspected exact-commit content for `workflow/ROUTER.md`, `STATE.md`, `RECOVERY.md`, `EXECUTION_PREP.md`, `EXECUTION.md`, `REVIEW.md`, `CLOSE.md`, `WORKSTREAMS.md`, `AUTHORITY.md`, `RESEARCH.md`, and `PLANNING.md`; production helpers including `tools/router.py`, `state_contract.py`, `execution_contract.py`, `recovery_contract.py`, `review_contract.py`, and `close_contract.py`; the relevant Task Board/Workstream/Research templates; router/state/execution/review/recovery tests; and the repository test entrypoints/CI workflow.

The selected lenses were exercised as follows: malformed/contradictory fail-closed state (F1, F2, F3); helper/documented-semantics parity and negative space (F2, F3); router precedence/conflicting obligations (F1 and the non-blocking JIT/Close probe); path/locator/cross-workstream safety (F4). I constructed adversarial state variants absent from the existing tests and preserved non-mutating repro scripts for the demonstrated classes.

#### S018 original confidence and limitations

Confidence is high in the four source-level counterexamples because each follows a deterministic production branch or validator gap and is tied to an explicit canonical invariant. The symlink class-root escape was additionally executed in a local temporary filesystem using the exact `Reads._read_path` semantics.

A full exact-commit checkout and repository test run could not be executed in this environment: direct local Git network access was unavailable, and the connected remote-shell quota was exhausted. Exact source and tree content were instead read through the GitHub connector with the immutable commit ref, and the preserved repro scripts are designed to import the unmodified production helpers when run from an exact checkout. This limitation is recorded rather than treating existing passing tests as proof.

Before findings were frozen, one GitHub commit-metadata call unexpectedly returned the merge commit's diff, which included historical workstream evidence/review text even though that material was not requested. I did not use those historical narratives to generate, classify, add, remove, or prioritize findings, and I avoided further historical audit/review material. I did not inspect branches matching other `audit/*`, swarm reports, GitHub Issues, or PR comments. No post-freeze historical comparison was performed.

