# D12 authority-locator recovery

Date: 2026-10-04  
Workstream: `change-workflow-successor-product`

## Observed predecessor state

At published commit `acba6b0eee1b88d56400b8aaaa77b5083c45aa30`, D12 is GREEN with owner CONTINUE consumed and Premium A due. The canonical default-branch PWV2 selector fails closed with:

`definition.requirements: authority path is outside accepted authority roots`

The requirements and all 43 decision locators use workstream-local paths, whereas `tools/state_contract.py::validate_locator` permits authority roots `requirements/`, `decisions/`, `planning/`, `workflow/` only. The canonical package used is unchanged from default-branch commit `d3ab917f02e4de91b7dbb17915c2287c2387333e`.

## Bounded recovery

The existing accepted authority is sufficient to repair the locator representation without a product decision:

- `requirements/PWV3_D12.md` imports the exact reviewed D12 blob, unchanged;
- `decisions/PWV3_D12_AUTHORITY.md` imports the exact 43-reference ordered decision set from the frozen predecessor manifest, resolving each path at that immutable commit;
- current `DEFINITION.toml` points to those authority-root bindings;
- no reviewed requirement, owner disposition, review evidence, Brainstorming scope, acceptance state or premium gate is changed by this recovery;
- original source artifacts remain unchanged, and the source manifest remains available by exact Git identity;
- no validator/router relaxation, new state schema, V2 stabilization or V3 implementation is performed.

The historical DRAFT/pending sentences in the exact reviewed Markdown remain intact. Current Definition acceptance is read from the live Definition state plus its accepted owner/result evidence, not rewritten into the immutable review subject.

## Verification and continuation

Verify all source objects exist, the D12 blob matches the reviewed blob, the frozen source manifest has exactly 43 resolvable decision references, the repaired state validates and a fresh canonical route returns Premium A (D12). Only then consume the user's explicit new-context Premium A entry as the next separate transition. This evidence records recovery, not Plan Review or product qualification.
