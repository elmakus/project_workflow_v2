# Definition — CI-pending deterministic continuation

Accepted subject: `ci-pending-deterministic-continuation@1`

## Outcome

Project Workflow V2 must preserve deterministic non-stop continuation when acceptance of the current exact implementation subject depends on required CI that has not yet reached a terminal state.

## Requirements

1. Required CI/check evidence is bound to the exact immutable implementation subject.
2. A terminal successful required CI result may satisfy its evidence requirement; a terminal failure remains Execution/correction evidence and cannot be accepted as success.
3. `queued`, `requested`, `waiting`, `pending`, and `in_progress` are non-terminal observations. They neither complete the Card nor establish a user stop.
4. Temporary absence of a just-triggered run must be handled by bounded exact-subject readback/observation and cannot be interpreted as success.
5. The continuation progress/cycle fuse must distinguish a legal pending-external-evidence observation from a semantic owner falsely claiming reconciliation with an unchanged authoritative fingerprint.
6. Pending observation state is ephemeral runtime evidence; it must not introduce a canonical Continuation phase, durable polling/session ledger, runtime identity, or new authority source.
7. Runtime iteration/time limits may abort technically but cannot convert pending CI into semantic completion or a workflow stop.
8. Deterministic regression coverage must exercise terminal success/failure and non-terminal queued/in_progress behavior, including unchanged durable workflow state while external evidence legitimately advances independently.
9. Existing #16 continuation, Review independence, Recovery, external-effect readback-first, and end-of-scope semantics remain intact.

## Completeness audit

GREEN. The authorized repair and prior-art diagnosis determine the behavior without unresolved user/product choices.
