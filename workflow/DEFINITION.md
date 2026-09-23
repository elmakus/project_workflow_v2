# Project Workflow V2 — Project Definition

Status: M02-T02 common Definition contract.

Definition converts one explicitly promoted exploratory revision into accepted requirements/decision authority. It must not infer promotion from readiness, chat continuation or Research completion.

## Entry

Definition requires the exact promoted Brainstorming subject `scope_id@revision`.

The selected workstream may point to one exact `DEFINITION.toml` record binding:
- source promoted scope subject;
- Definition revision;
- approved requirements locator;
- accepted decision locators;
- completeness audit;
- premium stop A state.

## Completion

Definition is GREEN only when:
- requirements/decisions needed for downstream planning are durably identifiable;
- completeness audit is GREEN;
- no unresolved user/product choice remains inside the accepted scope;
- premium stop A is due or already satisfied.

Definition GREEN does not automatically enter Strategic Planning.

## Premium stop A

When Definition becomes GREEN, premium stop A is a real human-facing boundary before material Strategic Planning. The stop must recommend using the best available model/context for Strategic Planning. Staying in the current context is allowed when it already satisfies that recommendation, but the stop must also render the optional ready-to-copy locator-only handoff defined by `workflow/USER_STOP.md` so Strategic Planning can be moved to another context or harness without another prompt request. That recommendation is presentation guidance only: canonical state records semantic gate state, never a product/model/session identity or a hard-coded product model name.

After A is durably satisfied, Strategic Planning owns continuation; full Planning semantics arrive in M02-T03.
