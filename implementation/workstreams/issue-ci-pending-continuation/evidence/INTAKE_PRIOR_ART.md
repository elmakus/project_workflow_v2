# Intake prior-art diagnosis — CI-pending deterministic continuation regression

Subject: `repair:ci-pending-deterministic-continuation:v1`

## Finding

Issue #16 fixed the semantic completion rule but did not define an external-evidence pending state or a continuation driver that can remain active while required CI is non-terminal.

The concrete M06 reproduction proves the timing window. After M06-T02-R02 GREEN, the same invocation finalized M06-T02, materialized/launched M06-T03, and produced commits through final repair commit `dabc8bdc3acd77cab58753a4715351344840beda` at 2026-09-29T01:09:01Z. GitHub created the required `test` run two seconds later at 01:09:03Z and it completed successfully at 01:09:11Z. Therefore an agent reaching the evidence gate before 01:09:11Z necessarily observes absent/queued/in_progress CI, while a slower invocation observes terminal success.

Current `workflow/CONTINUATION.md` requires fresh rerouting after every reconciled non-stop step and `tools/continuation_contract.py` classifies every `route` as `continue`. But its progress fuse rejects an unchanged authoritative fingerprint, and neither that module nor Execution/Recovery models the legitimate case where required external evidence exists but has not reached a terminal state.

## Required semantic distinction

- terminal required CI: consume the terminal conclusion as evidence; success may permit result reconciliation, failure remains Execution/correction evidence.
- queued/requested/waiting/pending: non-terminal external evidence; do not accept the Card result, do not fabricate a stop, and do not treat unchanged durable workflow state as a semantic cycle.
- in_progress: same non-terminal external-evidence state; continue observation until terminal or a genuine technical/runtime abort, which is not semantic completion.
- missing run immediately after a push: allow bounded exact-subject readback because GitHub may create the run asynchronously; do not interpret temporary absence as success or as a workflow stop.

The repair therefore belongs at the continuation/execution evidence boundary: represent exact-subject pending external evidence separately from semantic no-progress/cycle detection, with deterministic tests for terminal, queued and in_progress states. Workflow semantics must not branch on elapsed agent time.

## Source accounting

### Official/upstream — high weight
GitHub Actions REST and Checks documentation explicitly distinguish non-terminal statuses (`queued`, `in_progress`, `requested`, `waiting`, `pending`) from `completed`, where a conclusion exists:
- https://docs.github.com/en/rest/actions/workflow-runs
- https://docs.github.com/en/rest/guides/using-the-rest-api-to-interact-with-checks
- https://docs.github.com/en/pull-requests/reference/status-checks

### Actual project/runtime — highest weight
- `workflow/CONTINUATION.md`
- `tools/continuation_contract.py`
- `tests/test_continuation_contract.py`
- `tests/test_m05_trajectory.py`
- M06 commit sequence from `e26266b...` through `dabc8bd...`
- GitHub Actions run 36506517414 for `dabc8bd...`: created 01:09:03Z, completed success 01:09:11Z.
- Preceding M06-T03 commits also produced rapidly overlapping Actions runs, including terminal failures that caused subsequent repair commits.

### Issue/discussion tracker — high weight
- #16 documents the original non-stop continuation defect and expected deterministic continuation.
- #22 records this concrete CI-timing regression.

### Practitioner/community — not relevant, low weight
No community convention can override the repository's canonical continuation authority or GitHub's official CI state model. No community evidence is required to establish this repository-local race.

## Conflict summary

None material. GitHub's upstream status model and the repository/runtime evidence agree. The user's timing hypothesis is directionally correct, but the root cause is not “more resources” itself: faster execution merely exposes a pre-existing missing pending-external-evidence state.
