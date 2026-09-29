# Issue #28 — execution Research return owner precedence decisions

Status: `accepted`  
Definition revision: `D1`  
Source scope: `execution-research-return-owner-precedence@1`

## I28-D1 — Return-target semantics outrank locator order

**Decision:** A lawful Research record's exact `return_target` determines its return owner. The fact that the record is encountered first through the manifest locator must not restrict valid execution return targets to the pre-execution owner set.

**Why:** The current defect is caused by locator precedence changing semantics for the same schema-valid record.

## I28-D2 — Preserve one Research record, not two competing obligations

**Decision:** Manifest and Task Board may lawfully point to the same Research record. The repair must compose those locators as two references to one semantic obligation rather than creating a duplicate Research state, mirrored result, or second lifecycle.

**Why:** The single Research slot is intentionally reusable and current execution routing already owns exact return/cleanup semantics.

## I28-D3 — Reuse exact execution owner mapping

**Decision:** The three execution return prefixes must resolve consistently with the existing Task-Board path: execution-resolution returns to Recovery-owned execution resolution, execution-prep to Execution Prep, and execution to Execution. Planning may choose the smallest shared/helper or branch-local mechanism, but semantic outputs must be identical.

## I28-D4 — Consumed state remains cleanup-only

**Decision:** A consumed/applied execution Research record is never replayed. If a Task Board still points to it, preserve the existing stale-pointer cleanup route. The manifest locator alone does not manufacture a second cleanup protocol.

## I28-D5 — Preserve earlier Research behaviors

**Decision:** Do not change active Research priority or valid Intake/Brainstorming/Definition return behavior. Unsupported targets remain invalid. Positive pre-execution controls are mandatory.

## I28-D6 — No broad router architecture change

**Decision:** Solve the demonstrated owner-resolution/precedence defect without introducing a generic workflow phase graph, routing registry, new durable fields, or a parallel execution-research subsystem.

## I28-D7 — Separate constituent authority

**Decision:** #28 remains a dedicated repair constituent. Its Definition/Planning/gates/Card/Review are exact-subject-bound and do not inherit #23/#32/#33/#36 acceptance. Later composition and integration remain separate program obligations.
