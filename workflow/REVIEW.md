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

Card Review binds the exact current selected Task Card path plus its exact acceptance content: the attempt acceptance must name the exact selected Card path with exact Git commit/blob identity, that identity must resolve in Git, the commit must be reachable from selected HEAD, and current worktree bytes must still match the declared blob. Alternate same-stem paths, sibling paths, missing identity, off-HEAD commits, and same-path mutated or stale content fail closed; a stale terminal binding freezes a new exact attempt like a changed result subject. Existing terminal M01/M02/M02R history stays valid without rewrite.

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

Historical terminal review attempts that predate the explicit `review_kind` fields remain valid only as an initial legacy history prefix with explicit migration provenance, and are interpreted as discovery. Each legacy-shaped attempt carries `[legacy_migration]` binding the exact immutable source attempt (`source_repository`/`source_commit`/`source_path`/`source_blob`) plus the exact source Git/workstream state (`source_commit` plus `source_workstream`/`source_card`/`source_attempt`); the source resolves in Git, its pre-migration bytes exactly equal the current attempt without provenance, and the source Task Board at the source commit already listed the attempt path. The source bytes must already exist at the source commit's parent, so a legacy file introduced together with its Board listing in one source commit cannot self-certify historical status. File shape alone never proves historical status: newly authored legacy-shaped attempts without provenance, ambiguous provenance, and explicit attempts claiming provenance fail closed. A new PWv2.1 attempt begins as pending/in-progress with the explicit fields; active legacy-shaped attempts are invalid, and once explicit PWv2.1 history begins later attempts cannot return to legacy shape.

## Review epochs and convergence

Convergence-aware PWv2.1 attempts bind a stable `review_scope` (`card`, `milestone`, or `final`) and `review_epoch`. Ordinary implementation, test and finding repair stays inside the same epoch. A changed epoch is legal only after a material accepted authority/acceptance redesign and records both a non-empty durable `epoch_reset_basis` and an exact immutable `epoch_reset_subject` of class `accepted_redesign`. That subject must belong to the reviewed project repository and bind either the exact acceptance surface or one exact authority ref accepted by the current Card. Its commit/path/blob must read back exactly, the same blob must be the accepted content at the new reviewed subject, and that accepted path content must differ from the preceding epoch's reviewed subject; arbitrary files under an authority-looking directory, fabricated Git identities, unchanged authority/acceptance content, foreign repositories, repair/result subjects and convenience prose cannot reset review accounting.

Discovery/convergence counters are derived from append-only attempt history rather than stored as mutable authority. A fresh RED discovery consumes one discovery epoch only when it discovers at least one material defect class not previously discovered in the same review epoch. Closure verification, ordinary repair, GREEN fresh discovery and persistence/recurrence of already-known classes do not consume a discovery epoch. The default hard ceilings are 5 Card discovery epochs, 4 Milestone discovery epochs and 3 Final Integration discovery epochs.

Each material defect class also has a default ceiling of 3 failed repair→closure-verification rounds in the same review epoch. A RED closure-verification attempt records the exact non-empty subset `failed_material_defect_class_ids` of the classes it checked that actually remained blocking; only those classes accrue a failed round. A failed round is derived from a subject-changing repaired-content transition for one of those failed classes. Source-discovery content is not a repair round, unchanged repeated verification and commit-only movement of identical repository/path/blob content do not add a round, while returning to an earlier repaired content state after an intervening content change is another failed repair transition and does count. Reaching either the applicable discovery ceiling or a per-class closure-failure ceiling switches the lifecycle into Main convergence/root-cause analysis; it never turns RED into GREEN and does not authorize another ordinary discovery loop.

After convergence analysis, exactly one fresh full-scope post-convergence discovery may be run, bound to durable `convergence_basis`. A GREEN post-convergence discovery satisfies the normal fresh-discovery rule. A RED post-convergence discovery routes to broader structural classification through Recovery/Planning/Definition as appropriate rather than opening another ordinary repair/review cycle.

## Load-bearing findings versus advisory observations

A finding blocks GREEN only when concrete evidence shows it is materially load-bearing for the applicable acceptance, correctness, safety, security, data-integrity, dependency, compatibility, invariant, contract or required-evidence surface. Material blocking findings are load-bearing by construction. Advisory, stylistic, optional-cleanup, preference or speculative-hardening observations alone cannot keep the subject RED; a GREEN discovery may carry advisory-only observations.

Every terminal PWv2.1 RED discovery records `finding_severity` binding each material finding to its load-bearing surface plus concrete evidence; absent or empty severity on a new RED discovery is rejected. Historical pre-`review_kind` attempts remain valid legacy. Advisory observations travel in `observations`/`observation_updates`; closure verification inherits its source discovery classification. Severity and observation records require a terminal attempt with durable verdict evidence.

Every non-load-bearing observation remains durable and traceable to its originating terminal review attempt and review evidence path. Observation evidence must be canonical review evidence bound to that originating review evidence file, optionally with a fragment or equivalent suffix; mismatched or missing source evidence and tracker/Issue pointers are rejected as provenance. Each observation carries an explicit disposition: `open` until reconciled, then exactly one terminal disposition: `resolved`, `cleanup_candidate`, `deferred`, `promoted` or `tracked`. Reconciliation is a single open-to-terminal update with a concrete basis; unknown targets, duplicate introductions and second reconciliations are rejected.

Material finding ids and observation ids must stay disjoint inside one review epoch. Relabeling a load-bearing finding as advisory is a downgrade: convenience, repair cost, reviewer fatigue and desire to finish never justify it. A promoted observation keeps its advisory identity while follow-up blocking work uses a new finding id; genuine misclassification is corrected only through a governed accepted-redesign epoch, never by convenience relabeling.

Production deterministic helpers: `tools/review_contract.py` (`validate_finding_severity`, `validate_verdict_severity`, `derive_observation_state`, `unreconciled_observations`).

## Semantic independence

Independence is about material production/repair of the exact subject, not runtime identity.

A context that materially produced or repaired the subject cannot issue its independent verdict. Concrete provider/model/session/worker/invocation identity is non-canonical and must not be persisted merely to prove independence.

A runtime may satisfy review with an internal independent context when one genuinely exists. Otherwise:
- if the current context did not produce/repair the subject, it may review it;
- if the current context produced/repaired it and cannot obtain a qualifying independent context, freeze the pending exact review obligation and use a fresh-context locator handoff.

## Blocking lifecycle

For REQUIRED/activated RECOMMENDED review:
- no attempt / pending / in-progress / RED blocks accepted (`done`) terminal Card completion; a late-oversize handoff transitions to `returned` (non-acceptance) without claiming GREEN instead of bypassing this gate;
- GREEN for the exact current subject + acceptance permits deterministic post-review finalization;
- GREEN is not a verdict-only user stop;
- RED remains attached to its failed subject and routes to corrective classification; RED itself is not automatically a user stop.

## Card versus Milestone layering

Card Review owns bounded local correctness for one Card's coherent outcome; Milestone Review owns broader composition/integration acceptance across Cards. Execution Prep must not draw a Card boundary so broad that Card Review effectively substitutes for Milestone integration review: such a boundary is rejected by the prelaunch topology gate unless concrete atomicity evidence justifies the single boundary, and it always receives a fresh independent topology challenge before first launch. Deterministic helpers live in `tools/topology_contract.py`.

## Attempt history

The selected Card owns ordered review-attempt locators in its Task Board state. Attempt files are workstream-local under `reviews/`. Each relied-upon locator carries exact Git identity (`commit` plus `blob` with the Card path); the router proves the locator in Git, proves the locator commit sits within HEAD ancestry, proves current worktree bytes still hash to the declared blob, and parses only the verified bytes. Missing, dangling, mismatched, sibling or bogus-identity locators fail closed, and the same attempt ID cannot silently change bytes or verdict. Terminal bytes additionally freeze against actual Git history: every historical terminal version of an attempt path must match the current attempt, so a same-ID rewrite fails even with a rebound Board locator, while pending/in-progress attempts may still finalize to terminal.

At most one pending/in-progress attempt may exist and it must be the last attempt. Terminal attempts keep non-empty evidence. A later attempt never overwrites a prior GREEN/RED file.

Review may surface late-oversize evidence, but the return preserves attempt history and routes through Execution Prep (see `workflow/EXECUTION_PREP.md`); it binds the originating attempt id to one exact durable attempt locator on the Card and never deletes attempts, reuses attempt IDs, or manufactures GREEN.

## Runtime boundary

Capability detection and reviewer context launch remain runtime behavior. Project Workflow stores only the semantic attempt, exact subject/acceptance, independence basis and verdict/evidence.
