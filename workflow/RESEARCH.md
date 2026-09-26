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

For a concrete `#issue` diagnosis, Intake uses this same contract: `origin_role = intake`, `origin_subject` is the exact current repair subject and `return_target = intake`. Alignment cannot proceed until that exact proportional prior-art result has been applied and consumed **and** Intake has persisted the exact subject/result binding described in `workflow/INTAKE.md`. After that reconciliation, the single current Research slot may be reused for a later legitimate Brainstorming/Definition obligation without erasing proof that diagnosis prior art was checked. That proof is the exact `diagnosis_prior_art_proof` RF007 locator to the immutable consumed-Research Git blob; the persisted binding must equal the blob's origin/result exactly. If the repair subject changes, the Intake-owned binding and old Research result are stale for alignment.

Research never selects a different target by itself.

## Exact origin/return provenance

A completed record routes to its declared return target only when the exact origin-to-return binding is proved from a real owning subject: the owning record must first pass its owning validation, the declared target must be the owning boundary of the verified origin role (`intake`, `brainstorming`, or `definition`), and the origin subject must equal that owner's exact current subject (the issue repair subject, `scope_id@revision`, or the Definition revision). Implementation/recovery Research is Board-owned: its return target must be exactly `<origin_role>:<origin_subject>` and name an exact current Task Board Card. Mismatched or nonexistent origins fail closed to Recovery; a declared target alone is never proof.
