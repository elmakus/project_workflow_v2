# Project Workflow V2 — M01 Recovery Boundary

Status: identity/binding boundary only; full Recovery lifecycle is not implemented in M01.

When bootstrap identity is missing, ambiguous, malformed, cross-workstream, cross-branch or otherwise invalid:
- stop trusting mutable state;
- do not fall back to a root/default Task Board;
- preserve the diagnostic and exact paths already read;
- return a recovery-boundary result.

M01 does not repair state, consume human/premium gates or infer a replacement owner. Those behaviors belong to later approved milestones.
