from __future__ import annotations

import copy
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from tools.router import select_route
from tools.state_contract import ValidationError, read_toml, validate_board

ROOT = Path(__file__).resolve().parents[1]
STATE_VALID = ROOT / "tests" / "fixtures" / "state" / "valid"
ROUTER_FIXTURE = ROOT / "tests" / "fixtures" / "router" / "valid-project"
MANIFEST = "implementation/workstreams/sample-workstream/WORKSTREAM.toml"
BOARD = "implementation/workstreams/sample-workstream/TASK_BOARD.toml"
CARD = "implementation/workstreams/sample-workstream/cards/M01-T04.md"
WORKSTREAM_ID = "sample-workstream"


def _card_content(card_id: str, review: str = "none", dependencies: str = "none") -> str:
    return (
        "# Fixture Card\n"
        f"- Card ID: {card_id}\n"
        "- Included scope: prove launch readiness\n"
        "- Excluded scope: runtime-specific orchestration\n"
        "- Authority refs: requirements/REQUIREMENTS.md\n"
        f"- Dependencies: {dependencies}\n"
        "- Acceptance: route only after current launch inputs are valid\n"
        "- Required tests/readback: production router fixture\n"
        f"- Review requirement: {review}\n"
        "- Technical contract: none\n"
    )


def _result_content(card_id: str, summary: str = "GREEN") -> str:
    return (
        "# Card Result\n"
        f"- Card ID: {card_id}\n"
        "- Implementation subject: owner/repo@commit:" + ("a" * 40) + "\n"
        f"- Evidence refs: implementation/workstreams/{WORKSTREAM_ID}/evidence/{card_id}.md\n"
        f"- Tests/readback summary: {summary}\n"
        "- Result status: success\n"
    )


def _git_identity(project: Path, relpath: str) -> tuple[str, str]:
    if not (project / ".git").exists():
        subprocess.run(["git", "init", "-q", str(project)], check=True)
        subprocess.run(["git", "-C", str(project), "config", "user.email",
                        "fixture@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(project), "config", "user.name",
                        "Fixture"], check=True)
    subprocess.run(["git", "-C", str(project), "add", relpath], check=True)
    subprocess.run(["git", "-C", str(project), "commit", "-q", "-m",
                    f"fixture {relpath}"], check=True)
    commit = subprocess.run(
        ["git", "-C", str(project), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True).stdout.strip()
    blob = subprocess.run(
        ["git", "-C", str(project), "rev-parse", f"HEAD:{relpath}"],
        check=True, capture_output=True, text=True).stdout.strip()
    return commit, blob


class ValidatorShapeTests(unittest.TestCase):
    """RF014 consumed-proof shape in the shared Board validator."""

    def setUp(self) -> None:
        self.workstream = read_toml(STATE_VALID / "WORKSTREAM.toml")

    def base_board(self) -> dict:
        board = read_toml(STATE_VALID / "TASK_BOARD.toml")
        # M01-T01 done with result, M01-T02 in_progress.
        return board

    def test_consumed_without_proof_stays_shape_valid_for_history(self) -> None:
        board = self.base_board()
        board["jit_triggers"] = [{
            "id": "after-M01-T01",
            "after_card": "M01-T01",
            "state": "consumed",
            "condition": "Historical prose-only downstream materialization.",
        }]
        validate_board(board, self.workstream)

    def test_waiting_and_satisfied_with_proof_fail_as_premature(self) -> None:
        for state in ("waiting", "satisfied"):
            board = self.base_board()
            board["jit_triggers"] = [{
                "id": "after-M01-T01",
                "after_card": "M01-T01",
                "state": state,
                "condition": "Downstream boundary depends on predecessor.",
                "consumed_proof": {
                    "card": "M01-T02",
                    "path": f"implementation/workstreams/{WORKSTREAM_ID}/cards/M01-T02.md",
                    "commit": "a" * 40,
                    "blob": "b" * 40,
                },
            }]
            with self.subTest(state=state):
                with self.assertRaisesRegex(ValidationError, "premature|consumed"):
                    validate_board(board, self.workstream)

    def test_prose_and_path_only_proof_fail_closed(self) -> None:
        cases = [
            ("prose string", "downstream M01-T02 materialized"),
            ("path-only", {
                "card": "M01-T02",
                "path": f"implementation/workstreams/{WORKSTREAM_ID}/cards/M01-T02.md",
            }),
            ("missing blob", {
                "card": "M01-T02",
                "path": f"implementation/workstreams/{WORKSTREAM_ID}/cards/M01-T02.md",
                "commit": "a" * 40,
            }),
            ("bad hex", {
                "card": "M01-T02",
                "path": f"implementation/workstreams/{WORKSTREAM_ID}/cards/M01-T02.md",
                "commit": "not-a-commit",
                "blob": "b" * 40,
            }),
            ("extra prose key", {
                "card": "M01-T02",
                "path": f"implementation/workstreams/{WORKSTREAM_ID}/cards/M01-T02.md",
                "commit": "a" * 40,
                "blob": "b" * 40,
                "statement": "Execution Prep consumed the trigger.",
            }),
        ]
        for name, proof in cases:
            board = self.base_board()
            board["jit_triggers"] = [{
                "id": "after-M01-T01",
                "after_card": "M01-T01",
                "state": "consumed",
                "condition": "Downstream materialized.",
                "consumed_proof": proof,
            }]
            with self.subTest(case=name):
                with self.assertRaisesRegex(ValidationError, "consumed|proof|path-only|prose|unproved"):
                    validate_board(board, self.workstream)

    def test_proof_with_unknown_or_self_card_fails_closed(self) -> None:
        for card in ("M01-T99", "M01-T01"):
            board = self.base_board()
            board["jit_triggers"] = [{
                "id": "after-M01-T01",
                "after_card": "M01-T01",
                "state": "consumed",
                "condition": "Downstream materialized.",
                "consumed_proof": {
                    "card": card,
                    "path": f"implementation/workstreams/{WORKSTREAM_ID}/cards/{card}.md",
                    "commit": "a" * 40,
                    "blob": "b" * 40,
                },
            }]
            with self.subTest(card=card):
                with self.assertRaisesRegex(ValidationError, "consumed|downstream|unknown|Card"):
                    validate_board(board, self.workstream)

    def test_proof_path_mismatch_fails_closed(self) -> None:
        board = self.base_board()
        board["jit_triggers"] = [{
            "id": "after-M01-T01",
            "after_card": "M01-T01",
            "state": "consumed",
            "condition": "Downstream materialized.",
            "consumed_proof": {
                "card": "M01-T02",
                "path": f"implementation/workstreams/other-ws/cards/M01-T02.md",
                "commit": "a" * 40,
                "blob": "b" * 40,
            },
        }]
        with self.assertRaisesRegex(ValidationError, "sibling|path|workstream|consumed"):
            validate_board(board, self.workstream)

    def test_exact_shaped_proof_passes_validator(self) -> None:
        board = self.base_board()
        board["jit_triggers"] = [{
            "id": "after-M01-T01",
            "after_card": "M01-T01",
            "state": "consumed",
            "condition": "Downstream M01-T02 materialized from predecessor result.",
            "consumed_proof": {
                "card": "M01-T02",
                "path": f"implementation/workstreams/{WORKSTREAM_ID}/cards/M01-T02.md",
                "commit": "a" * 40,
                "blob": "b" * 40,
            },
        }]
        validate_board(board, self.workstream)

    def test_proof_to_earlier_card_fails_board_order(self) -> None:
        board = self.base_board()
        board["cards"][1]["status"] = "done"
        board["cards"][1]["result"] = {
            "class": "result",
            "path": f"implementation/workstreams/{WORKSTREAM_ID}/results/M01-T02.md",
        }
        board["jit_triggers"] = [{
            "id": "after-M01-T02",
            "after_card": "M01-T02",
            "state": "consumed",
            "condition": "Downstream materialized.",
            "consumed_proof": {
                "card": "M01-T01",
                "path": f"implementation/workstreams/{WORKSTREAM_ID}/cards/M01-T01.md",
                "commit": "a" * 40,
                "blob": "b" * 40,
            },
        }]
        with self.assertRaisesRegex(ValidationError, "order|after"):
            validate_board(board, self.workstream)


class RouterTerminalityTests(unittest.TestCase):
    """H026 all-DONE terminality with waiting/satisfied/consumed JIT."""

    def copy_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(ROUTER_FIXTURE, project)
        return temp, project

    def install_result(self, project: Path, card_id: str = "M01-T04",
                       dependencies: str = "none",
                       write_card: bool = True) -> tuple[str, str]:
        card_path = f"implementation/workstreams/{WORKSTREAM_ID}/cards/{card_id}.md"
        result_path = f"implementation/workstreams/{WORKSTREAM_ID}/results/{card_id}.md"
        if write_card:
            (project / card_path).write_text(_card_content(card_id, dependencies=dependencies))
        authority = project / "requirements" / "REQUIREMENTS.md"
        authority.parent.mkdir(parents=True, exist_ok=True)
        authority.write_text("# Accepted authority\n")
        evidence = project / "implementation" / "workstreams" / WORKSTREAM_ID / "evidence"
        evidence.mkdir(parents=True, exist_ok=True)
        (evidence / f"{card_id}.md").write_text("# Verified evidence\n")
        target = project / result_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_result_content(card_id))
        commit, blob = _git_identity(project, result_path)
        board = project / BOARD
        text = board.read_text()
        # Attach result to the named Card's stanza.
        marker = f'id = "{card_id}"\nstatus = '
        self.assertIn(marker, text)
        # Insert result stanza after the Card's contract block.
        contract_path = f"implementation/workstreams/{WORKSTREAM_ID}/cards/{card_id}.md"
        anchor = f'path = "{contract_path}"\n'
        self.assertIn(anchor, text)
        text = text.replace(
            anchor,
            anchor + f'\n[cards.result]\nclass = "result"\npath = "{result_path}"\n'
            f'commit = "{commit}"\nblob = "{blob}"\n',
            1,
        )
        board.write_text(text)
        return commit, blob

    def flip_done(self, project: Path, card_id: str = "M01-T04") -> None:
        board = project / BOARD
        text = board.read_text()
        marker = f'id = "{card_id}"\nstatus = "in_progress"'
        if marker in text:
            text = text.replace(marker, f'id = "{card_id}"\nstatus = "done"', 1)
        else:
            text = text.replace('status = "in_progress"', 'status = "done"', 1)
        board.write_text(text)

    def add_done_card(self, project: Path, card_id: str,
                      dependencies: str = "none") -> None:
        card_path = f"implementation/workstreams/{WORKSTREAM_ID}/cards/{card_id}.md"
        (project / card_path).write_text(_card_content(card_id, dependencies=dependencies))
        _git_identity(project, card_path)
        board = project / BOARD
        board.write_text(
            board.read_text()
            + f'\n[[cards]]\nid = "{card_id}"\nstatus = "done"\n'
            + '[cards.contract]\nclass = "task_card"\n'
            + f'path = "{card_path}"\n'
        )
        self.install_result(project, card_id, write_card=False)

    def predecessor_ref(self, project: Path, card_id: str = "M01-T04") -> str:
        result_path = f"implementation/workstreams/{WORKSTREAM_ID}/results/{card_id}.md"
        commit = subprocess.run(
            ["git", "-C", str(project), "log", "--format=%H", "-1", "HEAD",
             "--", result_path],
            check=True, capture_output=True, text=True).stdout.strip()
        blob = subprocess.run(
            ["git", "-C", str(project), "rev-parse", f"{commit}:{result_path}"],
            check=True, capture_output=True, text=True).stdout.strip()
        return f"{result_path}@{commit}:{blob}"

    def add_trigger(self, project: Path, trigger_id: str, after_card: str,
                    state: str, proof: dict | None = None) -> None:
        board = project / BOARD
        text = board.read_text()
        text += (
            f'\n[[jit_triggers]]\nid = "{trigger_id}"\n'
            f'after_card = "{after_card}"\nstate = "{state}"\n'
            'condition = "Downstream boundary depends on predecessor result."\n'
        )
        if proof is not None:
            text += (
                "[jit_triggers.consumed_proof]\n"
                f'card = "{proof["card"]}"\n'
                f'path = "{proof["path"]}"\n'
                f'commit = "{proof["commit"]}"\n'
                f'blob = "{proof["blob"]}"\n'
            )
        board.write_text(text)

    def downstream_proof(self, project: Path, card_id: str) -> dict:
        card_path = f"implementation/workstreams/{WORKSTREAM_ID}/cards/{card_id}.md"
        commit = subprocess.run(
            ["git", "-C", str(project), "log", "--format=%H", "-1", "HEAD", "--", card_path],
            check=True, capture_output=True, text=True).stdout.strip()
        blob = subprocess.run(
            ["git", "-C", str(project), "rev-parse", f"{commit}:{card_path}"],
            check=True, capture_output=True, text=True).stdout.strip()
        return {"card": card_id, "path": card_path, "commit": commit, "blob": blob}

    def test_all_done_no_jit_closes(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_result(project)
            self.flip_done(project)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "close"))
        finally:
            temp.cleanup()

    def test_all_done_waiting_blocks_close_to_prep(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_result(project)
            self.flip_done(project)
            self.add_trigger(project, "after-M01-T04", "M01-T04", "waiting")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation),
                             ("route", "execution_prep"))
            self.assertIn("after-M01-T04", routed.reason)
            self.assertIn("waiting", routed.reason)
        finally:
            temp.cleanup()

    def test_all_done_satisfied_blocks_close_to_prep(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_result(project)
            self.flip_done(project)
            self.add_trigger(project, "after-M01-T04", "M01-T04", "satisfied")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation),
                             ("route", "execution_prep"))
            self.assertIn("after-M01-T04", routed.reason)
            self.assertIn("satisfied", routed.reason)
        finally:
            temp.cleanup()

    def test_all_done_consumed_missing_proof_fails_closed(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_result(project)
            self.flip_done(project)
            self.add_trigger(project, "after-M01-T04", "M01-T04", "consumed")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation),
                             ("recovery", "recovery_boundary"))
            self.assertIn("after-M01-T04", routed.reason)
            self.assertIn("missing", routed.reason)
        finally:
            temp.cleanup()

    def test_all_done_consumed_exact_proved_closes(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_result(project)
            self.flip_done(project)
            self.add_done_card(project, "M01-T05",
                               dependencies=self.predecessor_ref(project))
            proof = self.downstream_proof(project, "M01-T05")
            self.add_trigger(project, "after-M01-T04", "M01-T04", "consumed", proof)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation), ("route", "close"))
        finally:
            temp.cleanup()

    def test_consumed_dangling_stale_sibling_unproved_fail_closed(self) -> None:
        # Dangling: proof commit does not resolve.
        temp, project = self.copy_fixture()
        try:
            self.install_result(project)
            self.flip_done(project)
            self.add_done_card(project, "M01-T05",
                               dependencies=self.predecessor_ref(project))
            proof = self.downstream_proof(project, "M01-T05")
            proof = dict(proof, commit="f" * 40, blob="e" * 40)
            self.add_trigger(project, "after-M01-T04", "M01-T04", "consumed", proof)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation),
                             ("recovery", "recovery_boundary"))
            self.assertIn("dangling", routed.reason)
        finally:
            temp.cleanup()
        # Stale: proof blob does not match the exact Git identity for the
        # downstream path (valid commit, wrong blob keeps the worktree valid
        # so DONE proof passes and the JIT stale binding is reached).
        temp, project = self.copy_fixture()
        try:
            self.install_result(project)
            self.flip_done(project)
            self.add_done_card(project, "M01-T05",
                               dependencies=self.predecessor_ref(project))
            proof = self.downstream_proof(project, "M01-T05")
            proof = dict(proof, blob="e" * 40)
            self.add_trigger(project, "after-M01-T04", "M01-T04", "consumed", proof)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation),
                             ("recovery", "recovery_boundary"))
            self.assertIn("stale", routed.reason)
        finally:
            temp.cleanup()
        # Sibling: proof path outside the workstream cards root.
        temp, project = self.copy_fixture()
        try:
            self.install_result(project)
            self.flip_done(project)
            self.add_done_card(project, "M01-T05",
                               dependencies=self.predecessor_ref(project))
            proof = self.downstream_proof(project, "M01-T05")
            proof = dict(proof, path="implementation/workstreams/other-ws/cards/M01-T05.md")
            board = project / BOARD
            text = board.read_text()
            text += (
                '\n[[jit_triggers]]\nid = "after-M01-T04"\n'
                'after_card = "M01-T04"\nstate = "consumed"\n'
                'condition = "Downstream materialized."\n'
                "[jit_triggers.consumed_proof]\n"
                f'card = "{proof["card"]}"\n'
                f'path = "{proof["path"]}"\n'
                f'commit = "{proof["commit"]}"\n'
                f'blob = "{proof["blob"]}"\n'
            )
            board.write_text(text)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation),
                             ("recovery", "recovery_boundary"))
            self.assertIn("sibling", routed.reason)
        finally:
            temp.cleanup()

    def test_consumed_forged_proof_fails_closed(self) -> None:
        # Proof Git-verifies but binds the wrong downstream Card content.
        temp, project = self.copy_fixture()
        try:
            self.install_result(project)
            self.flip_done(project)
            self.add_done_card(project, "M01-T05",
                               dependencies=self.predecessor_ref(project))
            self.add_done_card(project, "M01-T06")
            proof = self.downstream_proof(project, "M01-T06")
            # Claim M01-T05 but bind M01-T06 identity.
            forged = {
                "card": "M01-T05",
                "path": f"implementation/workstreams/{WORKSTREAM_ID}/cards/M01-T05.md",
                "commit": proof["commit"],
                "blob": proof["blob"],
            }
            self.add_trigger(project, "after-M01-T04", "M01-T04", "consumed", forged)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation),
                             ("recovery", "recovery_boundary"))
            self.assertIn("after-M01-T04", routed.reason)
        finally:
            temp.cleanup()

    def test_consumed_unrelated_later_card_fails_closed(self) -> None:
        # Bypass probe: an unrelated existing later Card with its own exact
        # Git identity and matching Card ID is not proof that this trigger
        # was consumed by its exact downstream materialization.
        temp, project = self.copy_fixture()
        try:
            self.install_result(project)
            self.flip_done(project)
            self.add_done_card(project, "M01-T05",
                               dependencies=self.predecessor_ref(project))
            self.add_done_card(project, "M01-T06")
            proof = self.downstream_proof(project, "M01-T06")
            self.add_trigger(project, "after-M01-T04", "M01-T04", "consumed", proof)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation),
                             ("recovery", "recovery_boundary"))
            self.assertIn("after-M01-T04", routed.reason)
            self.assertIn("forged", routed.reason)
        finally:
            temp.cleanup()

    def test_consumed_stale_consumer_edge_fails_closed(self) -> None:
        # The downstream names the predecessor result path but a superseded
        # identity: the consumer edge is stale, not exact proof.
        temp, project = self.copy_fixture()
        try:
            self.install_result(project)
            self.flip_done(project)
            ref = self.predecessor_ref(project)
            stale = ref[:-40] + "e" * 40
            self.add_done_card(project, "M01-T05", dependencies=stale)
            proof = self.downstream_proof(project, "M01-T05")
            self.add_trigger(project, "after-M01-T04", "M01-T04", "consumed", proof)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation),
                             ("recovery", "recovery_boundary"))
            self.assertIn("after-M01-T04", routed.reason)
            self.assertIn("stale", routed.reason)
        finally:
            temp.cleanup()

    def test_consumed_earlier_card_fails_closed(self) -> None:
        # The downstream must materialize after its predecessor on the Board;
        # pointing a trigger at an earlier Card is a forged binding.
        temp, project = self.copy_fixture()
        try:
            self.install_result(project)
            self.flip_done(project)
            self.add_done_card(project, "M01-T05",
                               dependencies=self.predecessor_ref(project))
            _git_identity(project, CARD)
            proof = self.downstream_proof(project, "M01-T04")
            self.add_trigger(project, "after-M01-T05", "M01-T05", "consumed", proof)
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation),
                             ("recovery", "recovery_boundary"))
            self.assertIn("after-M01-T05", routed.reason)
        finally:
            temp.cleanup()


class ConsumerEdgeTests(unittest.TestCase):
    """Causal trigger/downstream binding plus canonical Card parsing."""

    def _board(self, trigger: dict) -> dict:
        card = lambda cid, status="done": {  # noqa: E731
            "id": cid,
            "status": status,
            "contract": {
                "class": "task_card",
                "path": f"implementation/workstreams/{WORKSTREAM_ID}/cards/{cid}.md",
            },
            "result": {
                "class": "result",
                "path": f"implementation/workstreams/{WORKSTREAM_ID}/results/{cid}.md",
                "commit": "a" * 40,
                "blob": "b" * 40,
            },
        }
        return {
            "workstream_id": WORKSTREAM_ID,
            "cards": [card("M01-T04"), card("M01-T05"), card("M01-T07", "planned")],
            "jit_triggers": [trigger],
            "late_oversize_returns": [{
                "card_id": "M01-T04",
                "state": "residual_bound",
                "residual_card": "M01-T05",
                "residual_trigger": "after-M01-T04",
            }],
        }

    def _trigger(self, card: str) -> dict:
        return {
            "id": "after-M01-T04",
            "after_card": "M01-T04",
            "state": "consumed",
            "condition": "Residual scope handed to its bound Card.",
            "consumed_proof": {
                "card": card,
                "path": f"implementation/workstreams/{WORKSTREAM_ID}/cards/{card}.md",
                "commit": "c" * 40,
                "blob": "d" * 40,
            },
        }

    def test_handoff_trigger_must_name_bound_residual_card(self) -> None:
        from tools.jit_terminality_contract import (
            JitTerminalityError,
            validate_trigger_consumed_proof,
        )
        board = self._board(self._trigger("M01-T07"))
        with self.assertRaises(JitTerminalityError) as ctx:
            validate_trigger_consumed_proof(
                board["jit_triggers"][0], board, "task_board.jit_triggers[0]"
            )
        self.assertEqual(ctx.exception.kind, "forged")
        self.assertIn("M01-T05", str(ctx.exception))

    def test_handoff_trigger_bound_residual_passes_shape(self) -> None:
        from tools.jit_terminality_contract import validate_trigger_consumed_proof
        board = self._board(self._trigger("M01-T05"))
        proof = validate_trigger_consumed_proof(
            board["jit_triggers"][0], board, "task_board.jit_triggers[0]"
        )
        assert proof is not None
        self.assertEqual(proof["card"], "M01-T05")

    def test_forged_card_id_prose_fails_closed(self) -> None:
        from tools.jit_terminality_contract import (
            JitTerminalityError,
            verify_consumed_trigger,
        )
        temp = tempfile.TemporaryDirectory()
        try:
            project = Path(temp.name) / "project"
            card_rel = f"implementation/workstreams/{WORKSTREAM_ID}/cards/M01-T05.md"
            (project / card_rel).parent.mkdir(parents=True, exist_ok=True)
            # Anchored field names another Card; the claimed Card ID appears
            # only mid-line inside free prose. A substring check passes this.
            (project / card_rel).write_text(
                "# Fixture Card\n"
                "- Card ID: M01-T06\n"
                "- Included scope: handle - Card ID: M01-T05 legacy references\n"
                "- Excluded scope: runtime-specific orchestration\n"
                "- Authority refs: requirements/REQUIREMENTS.md\n"
                "- Dependencies: none\n"
                "- Acceptance: observable acceptance\n"
                "- Required tests/readback: fixtures\n"
                "- Review requirement: none\n"
                "- Technical contract: none\n"
            )
            subprocess.run(["git", "init", "-q", str(project)], check=True)
            subprocess.run(["git", "-C", str(project), "config", "user.email",
                            "fixture@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(project), "config", "user.name",
                            "Fixture"], check=True)
            subprocess.run(["git", "-C", str(project), "add", card_rel], check=True)
            subprocess.run(["git", "-C", str(project), "commit", "-q", "-m",
                            "fixture"], check=True)
            commit = subprocess.run(
                ["git", "-C", str(project), "rev-parse", "HEAD"],
                check=True, capture_output=True, text=True).stdout.strip()
            blob = subprocess.run(
                ["git", "-C", str(project), "rev-parse", f"HEAD:{card_rel}"],
                check=True, capture_output=True, text=True).stdout.strip()
            board: dict = {
                "workstream_id": WORKSTREAM_ID,
                "cards": [
                    {
                        "id": "M01-T04",
                        "status": "done",
                        "contract": {
                            "class": "task_card",
                            "path": f"implementation/workstreams/{WORKSTREAM_ID}/cards/M01-T04.md",
                        },
                        "result": {
                            "class": "result",
                            "path": f"implementation/workstreams/{WORKSTREAM_ID}/results/M01-T04.md",
                            "commit": "a" * 40,
                            "blob": "b" * 40,
                        },
                    },
                    {
                        "id": "M01-T05",
                        "status": "done",
                        "contract": {"class": "task_card", "path": card_rel},
                    },
                ],
            }
            trigger = {
                "id": "after-M01-T04",
                "after_card": "M01-T04",
                "state": "consumed",
                "condition": "Downstream materialized.",
                "consumed_proof": {
                    "card": "M01-T05",
                    "path": card_rel,
                    "commit": commit,
                    "blob": blob,
                },
            }
            with self.assertRaises(JitTerminalityError) as ctx:
                verify_consumed_trigger(
                    project_root=project,
                    project_repository="owner/fixture",
                    board=board,
                    trigger=trigger,
                    label="task_board.jit_triggers[0]",
                )
            self.assertEqual(ctx.exception.kind, "forged")
        finally:
            temp.cleanup()


class HoldPreservationTests(unittest.TestCase):
    """Live-finding/live-consumer holds keep their owning routes on terminal boards."""

    def copy_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(ROUTER_FIXTURE, project)
        return temp, project

    def install_done(self, project: Path) -> None:
        card_path = CARD
        result_path = f"implementation/workstreams/{WORKSTREAM_ID}/results/M01-T04.md"
        (project / card_path).write_text(_card_content("M01-T04"))
        authority = project / "requirements" / "REQUIREMENTS.md"
        authority.parent.mkdir(parents=True, exist_ok=True)
        authority.write_text("# Accepted authority\n")
        evidence = project / "implementation" / "workstreams" / WORKSTREAM_ID / "evidence"
        evidence.mkdir(parents=True, exist_ok=True)
        (evidence / "M01-T04.md").write_text("# Verified evidence\n")
        target = project / result_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(_result_content("M01-T04"))
        commit, blob = _git_identity(project, result_path)
        board = project / BOARD
        board.write_text(
            board.read_text().replace('status = "in_progress"', 'status = "done"', 1)
            + '\n[cards.result]\nclass = "result"\n'
            + f'path = "{result_path}"\ncommit = "{commit}"\nblob = "{blob}"\n'
        )

    def test_satisfied_held_by_finding_routes_finding_owner(self) -> None:
        temp, project = self.copy_fixture()
        try:
            self.install_done(project)
            board = project / BOARD
            board.write_text(
                board.read_text()
                + '\n[[jit_triggers]]\nid = "after-M01-T04"\n'
                + 'after_card = "M01-T04"\nstate = "satisfied"\n'
                + 'condition = "Downstream boundary depends on predecessor."\n'
                + '\n[[live_findings]]\nid = "LF-001"\n'
                + 'finding_class = "implementation_defect"\n'
                + 'observed = "Live execution exposed a material downstream observation."\n'
                + 'evidence_refs = ["implementation/workstreams/sample-workstream/evidence/LF-001.md"]\n'
                + 'owner_stage = "execution"\nauthorization = "none"\n'
                + 'tracker_locators = []\n'
                + '[live_findings.downstream]\ndisposition = "material"\n'
                + 'trigger = "after-M01-T04"\naspect = "semantics"\n'
                + 'material_evidence_refs = ["implementation/workstreams/sample-workstream/evidence/LF-001-material.md"]\n'
                + 'reconciliation = "pending"\n'
            )
            base = project / "implementation" / "workstreams" / WORKSTREAM_ID
            (base / "evidence" / "LF-001.md").parent.mkdir(parents=True, exist_ok=True)
            (base / "evidence" / "LF-001.md").write_text("# evidence\n")
            (base / "evidence" / "LF-001-material.md").write_text("# material\n")
            routed = select_route(project, [MANIFEST], package_root=ROOT)
            self.assertEqual((routed.disposition, routed.obligation),
                             ("route", "finding_reconciliation"))
            self.assertEqual(routed.subject, "after-M01-T04")
        finally:
            temp.cleanup()

    def test_historical_terminal_boards_validate_unchanged(self) -> None:
        for workstream_id in (
            "feature-common-preexecution-core",
            "issue-router-board-precedence",
        ):
            with self.subTest(workstream=workstream_id):
                prefix = ROOT / "implementation" / "workstreams" / workstream_id
                workstream = read_toml(prefix / "WORKSTREAM.toml")
                board = read_toml(prefix / "TASK_BOARD.toml")
                validate_board(board, workstream)


class CloseGateTests(unittest.TestCase):
    """Close terminality requires JIT completeness plus exact proof."""

    def copy_fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temp = tempfile.TemporaryDirectory()
        project = Path(temp.name) / "project"
        shutil.copytree(ROUTER_FIXTURE, project)
        return temp, project

    def test_close_gate_blocks_unconsumed_and_unproved(self) -> None:
        from tools.close_contract import CloseContractError
        from tools.close_contract import verify_terminal_jit_completeness_from_board
        for state, word in (("waiting", "unconsumed"), ("satisfied", "unconsumed"),
                            ("consumed", "missing")):
            temp, project = self.copy_fixture()
            try:
                board = project / BOARD
                # Satisfied/consumed require a DONE predecessor with result for
                # shape validity; waiting needs none. Use a path-only result
                # locator (shape-valid; Close JIT gate checks JIT, not DONE).
                text = board.read_text().replace(
                    'status = "in_progress"', 'status = "done"', 1
                )
                text += (
                    '\n[cards.result]\nclass = "result"\n'
                    'path = "implementation/workstreams/sample-workstream/results/M01-T04.md"\n'
                )
                text += (
                    f'\n[[jit_triggers]]\nid = "after-M01-T04"\n'
                    + 'after_card = "M01-T04"\n'
                    + f'state = "{state}"\n'
                    + 'condition = "Downstream boundary depends on predecessor."\n'
                )
                board.write_text(text)
                with self.subTest(state=state):
                    with self.assertRaisesRegex(CloseContractError, word):
                        verify_terminal_jit_completeness_from_board(
                            project_root=project,
                            workstream_path=MANIFEST,
                            board_path=BOARD,
                        )
            finally:
                temp.cleanup()

    def test_close_gate_accepts_no_jit(self) -> None:
        from tools.close_contract import verify_terminal_jit_completeness_from_board
        temp, project = self.copy_fixture()
        try:
            verify_terminal_jit_completeness_from_board(
                project_root=project,
                workstream_path=MANIFEST,
                board_path=BOARD,
            )
        finally:
            temp.cleanup()


if __name__ == "__main__":
    unittest.main()
