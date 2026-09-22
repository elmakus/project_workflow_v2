# Project Workflow V2 — Research

Status: M02-T02 common pre-execution Research contract.

Research answers agent-findable factual questions. It does not make user/product decisions and does not become authority merely by finding popular opinions.

## Prior-art breadth and weight

Every completed Research record must proportionally account for these source classes:
- official/upstream evidence;
- actual project/runtime evidence;
- issue/discussion tracker evidence;
- practitioner/community evidence.

A class may be checked, unavailable or not relevant. Completion may not silently leave a class pending or leave source conflicts unaccounted for. Each class records an explicit weight. Completed Research also records an explicit conflict summary, including an explicit `none` when no material conflict exists. Community evidence may expose practical failure modes/workarounds but does not override stronger authority by popularity; conflicts are reconciled by source weight/authority rather than popularity.

## Durable return ownership

The exact `RESEARCH.toml` record owns:
- origin role + exact subject;
- state: active / complete / consumed;
- exact return target;
- return reconciliation: pending / applied;
- exact return result reference once applied;
- concise finding, limitations and explicit conflict accounting;
- source-class accounting.

A completed record with reconciliation pending routes to its exact return owner. A completed record with reconciliation applied routes to that owner only for consume/clear behavior; it must not replay the already-applied result. Consumed Research is historical and does not route again.

Research never selects a different target by itself.
