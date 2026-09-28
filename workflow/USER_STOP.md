# Project Workflow V2 — Real user stop and fresh-context handoff

This module formats a response only after the router has already established a real stop. It never creates a new stop by itself.

## Real-stop boundary

A stop must come from current durable authority and router state, such as:
- unresolved user/product authority;
- an explicit accepted authorization boundary;
- a premium A/B/C boundary;
- a fresh independent-review boundary when the current context produced/repaired the exact subject;
- a concrete non-remediable access/runtime/input blocker;
- explicit user stop;
- durable end of approved scope.

Finishing a role, Card, review, milestone or runtime session is not itself a stop. Normal context replacement is recovered from durable state; there is no Project Workflow Context Health/FRESH lifecycle.

## User-facing response

Keep the stop response concise and state:
1. what completed or was found;
2. what that means for the durable workflow state;
3. the exact next step.

When user action is required, include an explicit `USER ACTION REQUIRED:` line with only the smallest required action.

When a fresh ChatGPT context is required or recommended, include a ready-to-copy `NEW CHAT START PROMPT` using the support template at `prompts/CHATGPT_FRESH_SESSION.md`.

### Delivery completion postcondition

Handoff delivery is an observable postcondition of an **already-established** boundary, never a way to establish one.

- handoff policy `none`: no fresh-context locator is implied;
- handoff policy `offered`: delivery is incomplete until the exact locator-only prompt is present;
- handoff policy `required`: delivery is incomplete until both `USER ACTION REQUIRED:` and the exact locator-only prompt are present.

The same postcondition applies when Review semantics plus transient capability realization establish a fresh independent-context boundary after the router has selected Review. A current context that did not materially produce/repair the exact subject, or a genuinely independent internal context, does not require an external handoff.

Missing or placeholder locator fields fail closed at the delivery boundary. Delivery failure does not mutate workflow state, create a stop, or persist model/session/worker identity. Runtime implementations may render or validate this contract by any mechanism that preserves these observable semantics.

## Premium A/B/C handoff behavior

Premium gates have distinct handoff requirements:

- **Premium A — optional handoff.** The user may continue in the current context when it is already the best available planning context. The stop MUST also include a ready-to-copy locator-only `NEW CHAT START PROMPT` so the user can move Strategic Planning to another context or harness without asking for a prompt.
- **Premium B — mandatory fresh independent handoff.** The current planning context must not review the plan it produced. The stop MUST tell the user to start a fresh independent best-available context/harness and MUST include the ready-to-copy locator-only `NEW CHAT START PROMPT` in the same response.
- **Premium C — optional handoff.** After GREEN Plan Review, the user may continue in the current context or move Execution Prep to a lighter/cheaper context or harness. The stop MUST include a ready-to-copy locator-only `NEW CHAT START PROMPT` so switching does not require another request.

The locator prompt is runtime-neutral. A receiving harness must already have a valid Project Workflow V2 bootstrap/entry mechanism; the locator does not copy workflow policy into the handoff.

## Locator-only fresh handoff

The fresh-session prompt contains only:
- consumer repository;
- exact branch;
- exact entry obligation;
- exact durable start pointer.

Do not copy workflow rules, review evidence, acceptance summaries, chat narrative, model/session identity or historical explanation into the prompt. The receiving context reconstructs truth from the canonical V2 router and the consumer repository's durable state.
