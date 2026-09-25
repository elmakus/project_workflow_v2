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

