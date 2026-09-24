# Project Workflow V2 — Common independent implementation review

Status: M03-T03 exact-subject review contract.

Implementation/final review is an exact-subject blocking gate when REQUIRED or when RECOMMENDED has been activated by the stable Card/workstream contract. Stage-6 Plan Review remains separate premium planning semantics.

## Subject and acceptance identity

Each review attempt binds:
- one exact immutable Git content subject;
- one exact acceptance surface (normally the stable Task Card for Card review);
- one append-only attempt ID;
- semantic independence evidence;
- pending/in-progress/GREEN/RED lifecycle;
- durable verdict evidence for terminal attempts.

A changed reviewed subject or a new verdict attempt is a new attempt. Existing terminal attempts remain immutable history.

## Discovery and finding closure

PWv2.1 distinguishes two review-pass kinds:

- `discovery` is a fresh full-scope review. It evaluates the complete applicable acceptance surface, does not stop at the first blocker, and freezes the complete independently discovered material finding set before repair begins.
- `closure_verification` is intentionally anchored to one earlier RED discovery attempt and the known finding IDs frozen by that discovery. It verifies the repair, required regression evidence, and the materially implicated causal blast radius. It is not a substitute for the next fresh full-scope discovery review.

A closure-verification evidence package must explicitly account for:
- the known findings being closed;
- the demonstrated defect class(es);
- root-cause evidence showing the repair is not limited to the literal reported example;
- the repair diff;
- required regression evidence;
- materially implicated reachable callers;
- consumers;
- providers;
- contracts;
- sibling representations;
- negative-space cases.

A causal category may be empty only when no materially implicated member exists; omission of the category is not equivalent to an empty checked set. Closure evidence must cover every concrete materially implicated item.

Repair targets the defect class/root cause and materially adjacent sibling/negative-space cases rather than only the literal reported example.

After all known material findings from a RED discovery are closure-verified, one new fresh `discovery` attempt over the exact current subject is mandatory. A GREEN closure attempt that covers only part of the source discovery set therefore keeps the lifecycle in closure verification for the remaining known findings; only after cumulative GREEN closure covers the full frozen set does the router freeze the fresh discovery attempt. Closure can never finalize the Card. Only a GREEN discovery attempt can satisfy the review obligation.

Historical terminal review attempts that predate the explicit `review_kind` fields remain valid as an initial legacy history prefix and are interpreted as discovery. A new PWv2.1 attempt begins as pending/in-progress with the explicit fields; active legacy-shaped attempts are invalid, and once explicit PWv2.1 history begins later attempts cannot return to legacy shape.

## Review epochs and convergence

Convergence-aware PWv2.1 attempts bind a stable `review_scope` (`card`, `milestone`, or `final`) and `review_epoch`. Ordinary implementation, test and finding repair stays inside the same epoch. A changed epoch is legal only after a material accepted authority/acceptance redesign and records both a non-empty durable `epoch_reset_basis` and an exact immutable `epoch_reset_subject` of class `accepted_redesign`. That subject must belong to the reviewed project repository and bind either the exact acceptance surface or one exact authority ref accepted by the current Card; arbitrary files under an authority-looking directory, foreign repositories, repair/result subjects and convenience prose cannot reset review accounting.

Discovery/convergence counters are derived from append-only attempt history rather than stored as mutable authority. A fresh RED discovery consumes one discovery epoch only when it discovers at least one material defect class not previously discovered in the same review epoch. Closure verification, ordinary repair, GREEN fresh discovery and persistence/recurrence of already-known classes do not consume a discovery epoch. The default hard ceilings are 5 Card discovery epochs, 4 Milestone discovery epochs and 3 Final Integration discovery epochs.

Each material defect class also has a default ceiling of 3 failed repair→closure-verification rounds in the same review epoch. A failed round is derived from a subject-changing repaired-content transition that receives RED closure verification. Source-discovery content is not a repair round, unchanged repeated verification and commit-only movement of identical repository/path/blob content do not add a round, while returning to an earlier repaired content state after an intervening content change is another failed repair transition and does count. Reaching either the applicable discovery ceiling or a per-class closure-failure ceiling switches the lifecycle into Main convergence/root-cause analysis; it never turns RED into GREEN and does not authorize another ordinary discovery loop.

After convergence analysis, exactly one fresh full-scope post-convergence discovery may be run, bound to durable `convergence_basis`. A GREEN post-convergence discovery satisfies the normal fresh-discovery rule. A RED post-convergence discovery routes to broader structural classification through Recovery/Planning/Definition as appropriate rather than opening another ordinary repair/review cycle.

## Semantic independence

Independence is about material production/repair of the exact subject, not runtime identity.

A context that materially produced or repaired the subject cannot issue its independent verdict. Concrete provider/model/session/worker/invocation identity is non-canonical and must not be persisted merely to prove independence.

A runtime may satisfy review with an internal independent context when one genuinely exists. Otherwise:
- if the current context did not produce/repair the subject, it may review it;
- if the current context produced/repaired it and cannot obtain a qualifying independent context, freeze the pending exact review obligation and use a fresh-context locator handoff.

## Blocking lifecycle

For REQUIRED/activated RECOMMENDED review:
- no attempt / pending / in-progress / RED blocks terminal Card completion;
- GREEN for the exact current subject + acceptance permits deterministic post-review finalization;
- GREEN is not a verdict-only user stop;
- RED remains attached to its failed subject and routes to corrective classification; RED itself is not automatically a user stop.

## Attempt history

The selected Card owns ordered review-attempt locators in its Task Board state. Attempt files are workstream-local under `reviews/`.

At most one pending/in-progress attempt may exist and it must be the last attempt. Terminal attempts keep non-empty evidence. A later attempt never overwrites a prior GREEN/RED file.

## Runtime boundary

Capability detection and reviewer context launch remain runtime behavior. Project Workflow stores only the semantic attempt, exact subject/acceptance, independence basis and verdict/evidence.
