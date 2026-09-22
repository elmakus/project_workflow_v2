# Project Workflow V2 — Authority

V2 uses one runtime-neutral semantic authority chain. Runtime, model, session and worker identity are not project authority.

For every managed obligation:
1. resolve the exact project and selected workstream;
2. follow only exact durable authority/evidence/result references required by the current obligation;
3. prefer accepted requirements/decisions over summaries and implementation notes;
4. fail closed when a required reference is missing, ambiguous, wrong-class or bound to another workstream;
5. apply proportional YAGNI: add no state or abstraction without a current semantic owner or acceptance need.

Git and external-system observations are evidence, not permission to rewrite accepted product authority.
