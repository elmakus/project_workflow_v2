#!/usr/bin/env python3
"""Minimal control-flow repro for PWv2 audit F3 at 4fb4bfb7d7b1481d6f347c182fc96a5a1135e045."""

def production_relevant_order(research_state: str, explicit_user_stop: bool):
    # Mirrors tools/router.py order: Research is returned before Brainstorm is loaded.
    if research_state == "active":
        return ("route", "research")
    if research_state == "complete":
        return ("route", "brainstorming")
    if explicit_user_stop:
        return ("stop", "explicit_user_stop")
    return ("route", "brainstorming")

assert production_relevant_order("active", True) == ("route", "research")
assert production_relevant_order("complete", True) == ("route", "brainstorming")
print("Research early return makes the higher-precedence explicit stop unreachable.")
