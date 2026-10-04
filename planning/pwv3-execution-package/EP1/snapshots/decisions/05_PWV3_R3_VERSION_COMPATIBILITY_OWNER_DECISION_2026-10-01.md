# PWV3 revision 3 — release/version compatibility owner decision

Date: 2026-10-01
Workstream: `change-workflow-successor-product`
Subject: `workflow-successor-product@3`
Status: OWNER-FIXED PRODUCT DIRECTION

## Product release numbering

PWV3 starts at `3.0.0`.

- patch component (`3.0.1`, `3.0.2`, ...) is for bug-fix/maintenance releases;
- minor component (`3.1.0`, `3.2.0`, ...) is for compatible product/contract evolution;
- major component increments only for a genuinely breaking product/contract boundary that cannot safely preserve or interpret valid prior-lineage work.

Release labels are human/package communication only. Compatibility is proven by exact package identity, artifact contract versions, supported readers/capabilities and applicability evidence.

## Patch-release compatibility

A normal `3.0.x` patch:

- may fix implementation defects;
- may make previously false-positive/false-GREEN states correctly fail to Recovery/repair;
- may require affected-cone revalidation or repair of state that was invalid under the already-existing contract;
- should preserve the artifact contracts of the `3.0` line;
- must not rewrite immutable Results/Reviews/history merely because the package changed;
- must remain able to read valid history produced by earlier `3.0.x` releases under the same contracts.

A patch package/helper update with unchanged artifact contracts must be adoptable without semantic migration. Safe patch adoption belongs in 3.0.

## When a patch is not enough

If fixing a defect genuinely requires a new compatible durable artifact contract, prefer the next minor release (for example `3.1.0`) with explicit old+new reader/applicability support.

If a defect exposes a fundamental semantic break such that valid prior-lineage work cannot be safely interpreted/preserved under the new rules, treat that as a major-version boundary, not as a disguised patch.

Do not infer breaking/non-breaking status from version numbers alone; the exact contract/applicability proof remains authoritative.

## Rollback direction

PWV3 does not plan an automatic rollback controller.

The design goal is forward repair through qualified patch/minor releases, exact contract readers and fail-closed Recovery. Once a newer incompatible contract has been written, blind package downgrade is forbidden unless exact compatibility is proven.

This supersedes the previously unresolved version-compatibility note in the revision-3 roadmap evidence.
