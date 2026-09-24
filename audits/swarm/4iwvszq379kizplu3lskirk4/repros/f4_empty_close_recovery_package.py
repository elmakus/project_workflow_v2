#!/usr/bin/env python3
from tools.close_contract import verify_target_side_recovery, cleanup_branch_action

recovery = verify_target_side_recovery(
    source_branch="feat/x",
    source_head="h",
    merged_source_head="h",
    target_package_subject_head="h",
    immutable_merge_evidence=True,
    required_artifacts=frozenset(),
    present_artifacts=frozenset(),
)
print(recovery)
assert recovery == "source_ref_independent_recovery"

cleanup = cleanup_branch_action(
    terminal_package_independent=True,
    source_ref_exists=True,
    current_head="h",
    cleanup_state="safe_to_delete",
    verified_head="h",
)
print(cleanup)
assert cleanup == "delete_exact_ref"
