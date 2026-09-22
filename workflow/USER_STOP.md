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

## Locator-only fresh handoff

The fresh-session prompt contains only:
- consumer repository;
- exact branch;
- exact entry obligation;
- exact durable start pointer.

Do not copy workflow rules, review evidence, acceptance summaries, chat narrative, model/session identity or historical explanation into the prompt. The receiving context reconstructs truth from the canonical V2 router and the consumer repository's durable state.
