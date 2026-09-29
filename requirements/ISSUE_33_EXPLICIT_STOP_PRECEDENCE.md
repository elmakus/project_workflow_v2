# Issue #33 — Explicit stop precedence requirements

Revision: `R1`
Status: `accepted`
Definition subject: `brainstorm-explicit-stop-precedence@1`
Repair subject: `repair:brainstorm-explicit-stop-precedence:v1`

## Goal

Ensure that a valid durable Brainstorm explicit-user-stop signal cannot be bypassed by matching later pre-execution state.

## Requirements

### I33-R1 — Explicit stop is controlling

After the selected Brainstorm record has been read and validated, `explicit_user_stop = true` MUST select the real `explicit_user_stop` stop owned by `workflow/BRAINSTORMING.md` before any Definition, Planning, Plan Review, Execution Prep, or Task Board obligation is returned.

### I33-R2 — Exact stop identity

The stop MUST retain the exact `scope_id@revision` subject, `workflow/BRAINSTORMING.md` owner, canonical reason, and existing USER_STOP delivery semantics. It MUST NOT be relabeled as successful Definition/Planning progress.

### I33-R3 — Later state cannot clear the stop

The presence of active or GREEN Definition, frozen/approved Planning, Plan Review, or implementation state MUST NOT silently clear, supersede, or bypass a valid Brainstorm-owned explicit stop.

### I33-R4 — No downstream mutation

Selecting the stop MUST NOT delete, rewrite, normalize, or claim acceptance of later records. Clearing the stop requires a lawful Brainstorm-owner transition on the selected record.

### I33-R5 — Resume after lawful clearing

When `explicit_user_stop` becomes false through lawful owner state, existing progressive validation and routing MUST resume. Matching active Definition and GREEN Definition/premium routes MUST preserve their current lawful outcomes, and malformed later state MUST still fail closed when it becomes routable.

### I33-R6 — Preserve earlier Research semantics

The repair MUST NOT absorb Issue #28 or change current manifest/Task-Board Research return ownership. The bounded defect concerns later Definition/Planning/pre-execution dispatch after Brainstorm state is reached.

### I33-R7 — Production enforcement

The precedence rule MUST be enforced on the production selector path after local Brainstorm validation and before downstream pre-execution reads/returns. Documentation-only wording, a test-only helper, or post-selection USER_STOP rendering is insufficient.

### I33-R8 — Discriminating qualification

Automated coverage MUST include:

1. explicit stop plus matching active Definition;
2. explicit stop plus GREEN Definition with premium A due and satisfied variants;
3. explicit stop with later Planning/Plan Review or Board locators where proportional;
4. exact stop subject/owner/reason and USER_STOP read-set behavior;
5. stop-only and active/ready Brainstorm controls;
6. stop-cleared Definition and premium controls;
7. malformed Brainstorm Recovery and resumed malformed downstream failure;
8. cumulative router/state/stop/continuation tests and clean detached exact-commit readback.

The exact implementation subject MUST receive independent review before Card completion.

### I33-R9 — Scope isolation

The repair MUST NOT implement #36 orphan-owner closure, #31 Stage-6 history, #29 Close reconstruction, #28 Research return precedence, #23/#26 reconciliation, historical migration, a generic policy registry, tracker closure, integration, or deployment.

## Acceptance boundary

Definition accepts the stop-precedence behavior and its bounded ordering semantics. It does not claim the code is already repaired, satisfy premium gates, authorize integration, or transfer authority from the stabilization program.
