# M01-T01 bounded repair verification — 2026-09-28

Repair subject: `d457b7b85d1fa84fb545b483647d1a605f7883f5`.

R01 RED finding corrected:
- delivery requirements with offered/required handoff now carry exact expected locator identity;
- validation compares the delivered repository, branch, entry obligation and durable pointer against that exact identity;
- the `NEW CHAT START PROMPT` tail is restricted to exactly the four locator fields;
- unresolved common placeholders and angle-bracket template values fail closed;
- negative tests cover wrong-but-nonempty locator values, extra prompt content, unresolved placeholders, and missing expected locator identity.

Verification:
- fresh clone of `work/pwv2-handoff-determinism` on exact head `d457b7b85d1fa84fb545b483647d1a605f7883f5`;
- `python3 -m unittest discover -s tests -q`;
- 175 tests passed;
- checkout HEAD read back as `d457b7b85d1fa84fb545b483647d1a605f7883f5`.

The repair stays inside M01-T01 accepted authority and does not change stop selection, Premium A/B/C policy, Review independence semantics, or canonical runtime identity.
