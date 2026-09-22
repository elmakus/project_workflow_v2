# M01 state-envelope schema

Serialization chosen for the M01 structured records is TOML so the implementation can parse it with Python standard-library tomllib and avoid a schema dependency solely for bootstrap state.

tools/state_contract.py is the executable contract for the implemented M01 fields. Later milestones may extend records only for concrete owned transitions.

Implemented record classes:
- PROJECT.md with TOML front matter;
- WORKSTREAM.toml;
- TASK_BOARD.toml;
- REVIEW_ATTEMPT.toml;
- EXTERNAL_EFFECT.toml.

Artifact locators use class plus path. Class/path pairing is validated for authority, Task Board, Task Card, result and evidence references. Test fixtures are never selectable live state.
