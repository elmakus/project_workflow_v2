# M07-T09 — pilot staging and ChatGPT bootstrap blocker

Date: 2026-09-23
Status: BLOCKED before pilot activation
Class: runtime_access_input

## Completed safely

Construction custody is live in `elmakus/project_workflow_v2` after terminal V1 handoff:
- V1 terminal transfer commit: `961a88dc1343c21d57a5f986faa91453eb83cca3`;
- V2 custody activation commit before this blocker: `6ca0ca11aa5d1d0dfc216f562b93973d921dfbad`;
- exact custody activation Actions run `35914045985`: SUCCESS.

Pilot pre-activation refs were re-read unchanged:
- `elmakus/orchestration-runtime main@c4130e63760d08c3656552f4a92c479239acbea3`;
- `work/orchestration-prior-art-findings@636a9ec2b7760fc6a24eddb00319bfff9d583165`.

A reversible V2 migration package is staged only on:
- branch `migration/pwv2-orchestration-prior-art`;
- commit `29f228e88006250253ea16cbba7c4e426763d19a`;
- tree `924e9b53c950053e67ed8d8dc6e51fa183d40ecd`;
- parent `636a9ec2b7760fc6a24eddb00319bfff9d583165`.

Exact migrated V2 blobs read back:
- `PROJECT.md`: `7662ce44d0dc9f21bc5882bcb44bd50960f3aecb`;
- `workflow/PWV2_ADOPTION.md`: `a289a90e75e5900ac6bb73088beb8d40edf19db9`;
- `WORKSTREAM.toml`: `5250feb44a97124bd2134ed451e53bc77095c7b9`;
- `INTAKE.toml`: `e29b800c63939b3af8c150e4b781938e48689cf9`;
- `BRAINSTORM.toml`: `053db048a815992a5a1643dabb7bbd088e478022`;
- migration provenance: `3f319ccc9c9375bc8d19c56593ac43f4eb3e2f03`.

The package preserves Intake complete, `orchestration-runtime-prior-art@1` ready for Definition, GREEN completion/challenge audit required by the V2 schema, promotion pending, no active Research, no Definition/Planning/Task Board/review/implementation authority. Canonical V2 router semantics therefore lead to the Definition-promotion real stop after activation.

The old V1 `WORKSTREAM.yaml` and `INTAKE.md` are removed in the staged tree; their exact source objects remain immutable at the source commit. The original live pilot branch has not been moved, so no V2 live effect exists in the pilot yet.

## Exact blocker

PWV2-REQ-007 and ADR-PWV2-002 require ChatGPT to obtain V2 workflow authority from `elmakus/project_workflow_v2` through user-owned Project Instructions/bootstrap.

The active ChatGPT Project bootstrap for this session still points to `elmakus/chatgpt-codex-project-workflow`. The canonical production replacement is `prompts/CHATGPT_PROJECT_INSTRUCTIONS.md` from `elmakus/project_workflow_v2` current main, with the consumer repository set to `elmakus/orchestration-runtime`.

No available capability in this session can mutate ChatGPT Project Instructions. Activating the pilot repository branch before that user-owned bootstrap is corrected would knowingly create a state where durable consumer state is V2 but a fresh ChatGPT context still enters through V1, violating the required bootstrap/recovery acceptance.

Therefore pilot activation is deliberately not performed.

## Resume rule

After the user updates the ChatGPT Project Instructions:
1. recover this V2 custody workstream and blocker from durable state;
2. re-read the PWv2 production package, V1 terminal handoff, pilot original branch and staged migration branch;
3. verify the staging commit is still the exact direct descendant of the frozen V1 pilot head;
4. clear this blocker and activate only `work/orchestration-prior-art-findings` by fast-forwarding it to exact staged commit `29f228e88006250253ea16cbba7c4e426763d19a`;
5. recover the activated pilot through the canonical V2 router and verify the expected Definition-promotion stop;
6. finish M07-T09 readback/close without wider rollout.
