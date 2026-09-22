# Project Workflow V2 — Trigger-only fork release versioning

## Applicability

This optional module is not part of an ordinary Close read set.

Load it only when the exact durable current operation explicitly declares a downstream fork release and provides the accepted upstream lineage tuple:

1. upstream repository;
2. upstream version/tag;
3. upstream commit SHA.

A similar version number, repository name or historical fork relationship is not a trigger. Missing or partial lineage fails closed.

## Canonical downstream identity

For accepted upstream baseline `vX.Y.Z`, the canonical downstream release identity is:

```text
vX.Y.Z-private.N
```

`N` is a positive integer local to that exact upstream baseline.

- no existing canonical private tag for the baseline -> `private.1`;
- otherwise -> numeric `max(N) + 1`;
- fork-local work never advances `X.Y.Z`;
- another upstream baseline has its own private lane.

Legacy upstream-looking fork tags, malformed private tags, upstream tags and private tags for another baseline do not participate in the current lane.

## Canonical ordering

When lineage-aware cross-baseline ordering is required, compare the numeric tuple `(X, Y, Z, N)`. Do not use lexical ordering or generic highest-SemVer across mixed upstream, legacy and private tags.

Examples:

- `v5.0.8-private.10` is after `v5.0.8-private.2`;
- `v5.0.9-private.1` is after `v5.0.8-private.99`.

## Historical immutability

Published historical releases/tags are provenance. Do not rewrite, delete, retag or retroactively map legacy releases into a private lane.

## Optional native latest alias

A publication surface may mark the accepted stable canonical artifact as its native `latest` release. When used, that alias must resolve to the same exact artifact identity as the accepted canonical release.

Never synthesize a `vlatest` tag/version.

## Quality and authorization

`private.N` identifies downstream lineage, not alpha/beta/prerelease quality. Publication-quality flags remain separately governed.

This module does not authorize:

- upstream synchronization;
- tag creation or movement;
- release publication;
- deployment/live writes;
- historical tag deletion or rewrite.

Any exact accepted authorization gate still applies. Deployment/live-write status by itself creates no additional gate.

Production deterministic helper: `tools/fork_release_contract.py`.
