Use Project Workflow V2 from `elmakus/project_workflow_v2` as the workflow authority for this ChatGPT Project.

Consumer project repository: `<owner/repository>`

For workflow entry or continuation:
1. read the canonical `workflow/ROUTER.md` from the current default branch of `elmakus/project_workflow_v2`;
2. recover the consumer repository's `PROJECT.md`, exact selected workstream and only the durable pointers required by the router;
3. follow the canonical router and progressively load only the exact current module, authority and evidence it requires;
4. continue deterministic authorized transitions until the router reaches a real stop.

These Project Instructions are a bootstrap locator, not a copy of Project Workflow semantics. Do not reconstruct missing workflow policy from chat memory, runtime/model/session identity, or a second project/state store. Do not pin the consumer project to an exact workflow patch solely for ordinary update propagation.
