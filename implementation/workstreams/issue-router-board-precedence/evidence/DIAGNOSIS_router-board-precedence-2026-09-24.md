# Diagnosis — router board precedence (2026-09-24)

- Repair subject: `repair:approved-plan-co-bound-board-precedence:v1` (diagnosis revision 1).
- Defect class: in `tools/router.py`, an approved plan with satisfied premium C
  (lines 426-430), or an exact editorial exemption (lines 408-415), returns
  `execution_prep` before the co-bound Task Board is read and validated
  (line 473). On that path a valid existing Board/Card state — including an
  active Card and terminal RED needing `execution_resolution` — is unreachable.
- Required repair behavior: preserve no-board Execution Prep; when a Task Board
  locator is co-bound, read/validate it first and route valid active Board/Card
  states (especially terminal RED to `execution_resolution`); malformed Board
  state fails closed to Recovery.
- Authorization: user explicitly authorized this exact bounded repair after
  diagnosis (ordinary branch commit/push/readback/test/review writes; no main
  merge, no installed plugin update). Proposal patch left un-applied here.
- Proportionality: single precedence guard in one selector function; bounded
  micro-fix candidate.
