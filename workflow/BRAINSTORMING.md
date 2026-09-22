# Project Workflow V2 — Brainstorming

Status: M02-T02 common exploratory contract.

Brainstorming owns open-ended product/problem exploration after Intake when the next correct state is not yet accepted Definition.

## Adaptive grilling

Adaptive grilling is intrinsic. There is no active `#grill` command.

Questions must:
- target genuine user/product/strategy choices rather than agent-findable facts;
- be grouped thematically and numbered when multiple choices are asked;
- include the workflow's current recommendation and relevant tradeoff;
- continue while another sensible round has material expected decision value.

Agent-findable facts route to Research. Do not offload repository/runtime/prior-art lookup to the user.

## Durable exploratory revision

The selected workstream may point to one exact `BRAINSTORM.toml` record.

A revision owns:
- stable scope_id + integer revision;
- active / ready_for_definition / promoted lifecycle;
- final challenge/completion audit;
- explicit user-stop signal;
- exact promotion authorization subject.

Before Definition:
1. final challenge audit must be GREEN;
2. the exact current `scope_id@revision` must be explicitly user-authorized for promotion;
3. substantive scope change increments revision and makes prior promotion authorization stale.

Ready-for-definition is not permission to enter Definition by itself.

## Stops

- explicit user stop -> real stop;
- ready_for_definition without exact promotion authorization -> real Definition-promotion stop;
- exact promoted revision -> Definition owns continuation.

Research may temporarily own fact gathering and must return to its exact recorded target once.
