# PWV3 revision 3 — roadmap pruning and release-version owner direction

Date: 2026-09-30
Workstream: `change-workflow-successor-product`
Subject: `workflow-successor-product@3`
Status: OWNER-FIXED WHERE EXPLICIT / VERSION COMPATIBILITY POLICY STILL UNDER BRAINSTORMING

## Explicit roadmap removals

The owner does not want these previously proposed later-roadmap capabilities as planned PWV3 backlog:

- staged/ring rollout automation;
- automatic rollback controller;
- persistent telemetry/tracing backend;
- fleet/cross-workstream analytics;
- Paseo status/semantic plugin;
- optional MCP adapter, because the extension/package path already covers the required integration unless future evidence proves otherwise;
- additional runtimes/providers beyond the accepted ChatGPT and Pi/Paseo surfaces;
- additional external tracker integrations beyond the accepted GitHub Issues path;
- stronger signing/attestation/SBOM/provenance subsystem under the current single-owner threat model.

These are removed from planned 3.1/3.2+ scope. They may only return through a future genuine product decision backed by a concrete need.

## Additional roadmap removals

The owner also removes these previously proposed later-roadmap items:

- historical/status browser; agents use canonical inspect/resume/state directly and no separate owner UI is required;
- additional managed merge methods beyond the one qualified 3.0 merge path; support one qualified final integration method unless a future concrete repository requirement reopens the decision.

These are not planned 3.1/3.2 backlog.

## Release numbering owner direction

The product release line starts at:

`3.0.0`

The owner wants the third component to represent bug-fix releases:

`3.0.0 -> 3.0.1 -> 3.0.2 -> ...`

The exact compatibility rule for a bug fix is intentionally not yet frozen by this evidence. The Brainstorm must distinguish:
- implementation-only fixes that preserve artifact contracts;
- fixes that require revalidation or repair of affected durable evidence;
- fixes that introduce a new compatible artifact contract;
- truly breaking fixes that cannot safely interpret or preserve prior workstream history.

The final Definition should separate product/package version from per-artifact contract versions and must not infer compatibility from the release label alone.
