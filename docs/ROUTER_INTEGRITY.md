# Canonical router integrity manifest

`SessionStart` (`hooks/session-start.py`) verifies the exact bytes of the
canonical bundled `workflow/ROUTER.md` against the shipped package manifest
`.codex-plugin/router-integrity.json`. The manifest carries the exact Git blob
identity of the router and nothing else:

- `version`: manifest shape version, currently `1`;
- `router`: always `workflow/ROUTER.md`;
- `git_blob_sha1`: lowercase hex Git blob SHA-1 of the exact router bytes.

The manifest is release packaging metadata, not workflow policy and not a
consumer project version pin. Verification is offline and local: the hook reads
only the router plus its manifest, computes the Git blob identity itself, and
fails closed (`BLOCKING`) on any missing, malformed, or mismatched
manifest/router bytes. Marker substrings alone never enable the package.

## Regenerating after a legal router update

When an accepted change edits `workflow/ROUTER.md`, regenerate the manifest in
the same change so the shipped package stays self-consistent:

```sh
git hash-object workflow/ROUTER.md
```

Put the printed blob SHA-1 into `git_blob_sha1`, then run:

```sh
python3 -m unittest tests.test_session_router_integrity tests.test_codex_delivery
sh scripts/test-plugin-probe.sh
```

`tests/test_session_router_integrity.py` pins the expected blob and fails when
the manifest no longer matches the tracked router.
