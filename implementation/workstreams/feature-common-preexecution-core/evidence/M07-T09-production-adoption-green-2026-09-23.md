# M07-T09 — first production adoption GREEN

Date: 2026-09-23
Status: GREEN

## Production workflow/package identity

- Production repository: `elmakus/project_workflow_v2`
- Production main: `c2f53dc15f35dcbf1506b5a80ad3fd85d32211dd`
- Production tree: `f05d86d72f9bbe941583b4ccf92e2c46b5decf83`
- Plugin namespace/version: `pw 0.2.1`
- Skill: `project_workflow_v2`
- Exact package subject: `elmakus/project_workflow_v2@commit:c2f53dc15f35dcbf1506b5a80ad3fd85d32211dd|tree:f05d86d72f9bbe941583b4ccf92e2c46b5decf83|pw:0.2.1`

The production merge retained the independently reviewed tree exactly.

## Construction custody

- Terminal V1 handoff: `elmakus/chatgpt-codex-project-workflow@961a88dc1343c21d57a5f986faa91453eb83cca3`
- V2 construction custody became sole live owner before pilot activation.
- Bootstrap blocker was recorded before activation and later resolved by explicit user confirmation that the pilot ChatGPT Project Instructions were changed to the canonical V2 bootstrap.
- No V1 controller was resumed after terminal transfer.

## Pilot activation

Authorized pilot only: `elmakus/orchestration-runtime`.

Frozen pre-activation refs:
- `main@c4130e63760d08c3656552f4a92c479239acbea3`
- `work/orchestration-prior-art-findings@636a9ec2b7760fc6a24eddb00319bfff9d583165`

Staged migration:
- commit `29f228e88006250253ea16cbba7c4e426763d19a`
- tree `924e9b53c950053e67ed8d8dc6e51fa183d40ecd`
- direct parent `636a9ec2b7760fc6a24eddb00319bfff9d583165`

Activation was a non-force fast-forward of only the authorized pilot workstream branch to the exact staged commit. Immediate readback verified all expected V2 blobs and unchanged pilot `main`.

Post-activation provenance-only commit:
- `ae38e35ff3a0fd816741352c6421f8a8e9f31e5e`
- tree `4fa5a0d07a81aa077b210171d410dbfd5aa76cf4`

This commit records live activation only; it does not promote Definition or create implementation authority.

## Exact recovered semantic state

Live pilot state preserves:
- Intake complete;
- scope `orchestration-runtime-prior-art@1`;
- Brainstorming `ready_for_definition`;
- GREEN challenge audit required by the V2 state contract;
- promotion `pending`;
- no active Research;
- no Definition;
- no requirements/accepted decisions/plan;
- no Task Board/review/implementation obligation.

The production selector `tools/router.py` from exact PWv2 `main@c2f53dc15f35dcbf1506b5a80ad3fd85d32211dd` was executed against exact pilot `ae38e35ff3a0fd816741352c6421f8a8e9f31e5e` and returned:

- disposition: `stop`
- obligation: `definition_promotion`
- subject: `orchestration-runtime-prior-art@1`
- owner: `workflow/BRAINSTORMING.md`
- reason: Brainstorming is ready but exact current revision is not authorized for Definition.

The selector read only the canonical router, pilot PROJECT/WORKSTREAM/INTAKE/BRAINSTORM state and `workflow/USER_STOP.md`.

## Rollback and scope

The exact pre-activation V1 refs/blobs remain immutable recovery evidence. Because V2 has now produced live pilot state, no blind rollback to V1 is permitted; any reverse migration would require separately authorized verified handling.

No wider project rollout was performed or authorized.

M07-T09 acceptance is satisfied.
