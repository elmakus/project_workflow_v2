#!/usr/bin/env python3
"""Fixture-only apply/restart/rollback mechanics for PWV2 M06-T03."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import tomllib
from pathlib import Path
from typing import Any, Callable

from tools.state_contract import (
    validate_board as validate_v2_board,
    validate_review,
    validate_review_history,
    validate_workstream,
)

HEX64 = re.compile(r"^[0-9a-f]{64}$")


class MigrationApplyError(RuntimeError):
    """The migration apply cannot proceed without violating the bounded contract."""


class SimulatedMigrationCrash(RuntimeError):
    """Deterministic fixture-only crash injection used by M06 acceptance tests."""


def authorization_for(bundle: dict[str, Any]) -> str:
    """Return the explicit fixture-only authorization token for one exact bundle."""
    fingerprint = bundle.get("source_fingerprint")
    if not isinstance(fingerprint, str) or HEX64.fullmatch(fingerprint) is None:
        raise MigrationApplyError("bundle has no exact source fingerprint")
    return f"authorize-fixture-migration:{fingerprint}"


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n").encode("utf-8")


def _sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _verify_output_fingerprint(bundle: dict[str, Any]) -> None:
    if bundle.get("schema") != "pwv2-m06-conversion-v1":
        raise MigrationApplyError("apply requires an M06 conversion bundle")
    claimed = bundle.get("output_fingerprint")
    if not isinstance(claimed, str) or HEX64.fullmatch(claimed) is None:
        raise MigrationApplyError("bundle output fingerprint is missing or invalid")
    payload = dict(bundle)
    payload.pop("output_fingerprint", None)
    actual = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    if actual != claimed:
        raise MigrationApplyError("conversion bundle diverged from its output fingerprint")


def _validate_bundle(bundle: dict[str, Any]) -> None:
    _verify_output_fingerprint(bundle)
    workstream = bundle.get("workstream")
    task_board = bundle.get("task_board")
    if not isinstance(workstream, dict) or not isinstance(task_board, dict):
        raise MigrationApplyError("conversion bundle is missing canonical V2 state")
    validate_workstream(workstream)
    validate_v2_board(task_board, workstream)
    histories = bundle.get("review_attempts", {})
    if not isinstance(histories, dict):
        raise MigrationApplyError("review_attempts must be a mapping")
    for card_id, attempts in histories.items():
        validate_review_history(
            attempts,
            expected_card_id=card_id,
            workstream_id=workstream["workstream_id"],
        )


def _verify_current_source(
    bundle: dict[str, Any],
    *,
    observed_commit: str,
    board_text: str,
    manifest_text: str | None,
) -> None:
    provenance = bundle.get("provenance")
    source = provenance.get("source") if isinstance(provenance, dict) else None
    if not isinstance(source, dict):
        raise MigrationApplyError("conversion bundle is missing exact source provenance")
    expected_manifest = source.get("manifest_sha256")
    actual_manifest = _sha256_text(manifest_text) if manifest_text is not None else None
    checks = {
        "commit": observed_commit,
        "board_sha256": _sha256_text(board_text),
        "manifest_sha256": actual_manifest,
    }
    for key, actual in checks.items():
        if source.get(key) != actual:
            raise MigrationApplyError(f"source divergence detected for {key}")


def _toml_key(value: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_-]+", value):
        return value
    return json.dumps(value, ensure_ascii=False)


def _toml_value(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(item) for item in value) + "]"
    if isinstance(value, dict):
        entries = [
            f"{_toml_key(str(key))} = {_toml_value(child)}"
            for key, child in value.items()
            if child is not None
        ]
        return "{ " + ", ".join(entries) + " }"
    raise MigrationApplyError(f"cannot render canonical TOML value {type(value).__name__}")


def _render_toml(data: dict[str, Any]) -> bytes:
    return ("\n".join(
        f"{_toml_key(str(key))} = {_toml_value(value)}"
        for key, value in data.items()
        if value is not None
    ) + "\n").encode("utf-8")


def _relative_generated_path(bundle: dict[str, Any], absolute_project_path: str) -> Path:
    workstream_id = bundle["workstream"]["workstream_id"]
    prefix = f"implementation/workstreams/{workstream_id}/"
    if not absolute_project_path.startswith(prefix):
        raise MigrationApplyError("generated artifact escapes destination workstream")
    relative = absolute_project_path[len(prefix):]
    path = Path(relative)
    if not relative or path.is_absolute() or ".." in path.parts:
        raise MigrationApplyError("generated artifact path is unsafe")
    return path


def _stage_payloads(bundle: dict[str, Any]) -> dict[str, bytes]:
    payloads: dict[str, bytes] = {
        "WORKSTREAM.toml": _render_toml(bundle["workstream"]),
        "TASK_BOARD.toml": _render_toml(bundle["task_board"]),
        "migration/conversion-bundle.json": _json_bytes(bundle),
        "migration/provenance.json": _json_bytes(bundle["provenance"]),
        "migration/artifact-plan.json": _json_bytes(bundle.get("artifact_plan", [])),
        "migration/result-provenance.json": _json_bytes(bundle.get("result_provenance", [])),
    }
    for attempts in bundle.get("review_attempts", {}).values():
        for attempt in attempts:
            ref = next(
                (
                    item
                    for item in bundle["task_board"]["cards"]
                    if item["id"] == attempt["card_id"]
                ),
                None,
            )
            if ref is None:
                raise MigrationApplyError("review attempt belongs to an unknown Card")
            attempt_ref = next(
                (
                    item
                    for item in ref.get("review_attempts", [])
                    if Path(item["path"]).stem == f"{attempt['card_id']}-{attempt['attempt']}"
                ),
                None,
            )
            if attempt_ref is None:
                raise MigrationApplyError("review attempt locator is missing from Task Board")
            rel = _relative_generated_path(bundle, attempt_ref["path"])
            payloads[rel.as_posix()] = _render_toml(attempt)

    for obligation in bundle.get("review_obligations", []):
        blocker_path = obligation.get("blocker_path")
        if not isinstance(blocker_path, str):
            raise MigrationApplyError("review obligation lacks blocker path")
        rel = _relative_generated_path(bundle, blocker_path)
        blocker = {
            "workstream_id": bundle["workstream"]["workstream_id"],
            "card_id": obligation["card_id"],
            "class": "runtime_access_input",
            "summary": obligation["reason"],
            "evidence_path": "",
        }
        payloads[rel.as_posix()] = _render_toml(blocker)
    return payloads


def _stage_path(destination_root: Path, bundle: dict[str, Any]) -> Path:
    return destination_root.parent / (
        f".{destination_root.name}.migration-stage-{bundle['output_fingerprint'][:16]}"
    )


def _read_record(root: Path) -> dict[str, Any]:
    record_path = root / "migration" / "migration-record.json"
    try:
        record = json.loads(record_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise MigrationApplyError("destination migration record is missing or invalid") from exc
    if not isinstance(record, dict):
        raise MigrationApplyError("destination migration record must be an object")
    return record


def _verify_materialized_root(root: Path, bundle: dict[str, Any]) -> dict[str, Any]:
    record = _read_record(root)
    if record.get("schema") != "pwv2-m06-apply-record-v1":
        raise MigrationApplyError("destination migration record schema mismatch")
    if record.get("source_fingerprint") != bundle["source_fingerprint"]:
        raise MigrationApplyError("destination is bound to a different source fingerprint")
    if record.get("output_fingerprint") != bundle["output_fingerprint"]:
        raise MigrationApplyError("destination is bound to a different output fingerprint")
    files = record.get("files")
    if not isinstance(files, dict) or not files:
        raise MigrationApplyError("destination migration record has no file inventory")
    for relative, expected_digest in files.items():
        if not isinstance(relative, str) or not isinstance(expected_digest, str):
            raise MigrationApplyError("destination file inventory is invalid")
        path = root / relative
        try:
            actual = _sha256_bytes(path.read_bytes())
        except OSError as exc:
            raise MigrationApplyError(f"destination file missing: {relative}") from exc
        if actual != expected_digest:
            raise MigrationApplyError(f"destination divergence detected: {relative}")

    try:
        workstream = tomllib.loads((root / "WORKSTREAM.toml").read_text(encoding="utf-8"))
        task_board = tomllib.loads((root / "TASK_BOARD.toml").read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise MigrationApplyError("materialized canonical V2 state is unreadable") from exc
    validate_workstream(workstream)
    validate_v2_board(task_board, workstream)

    review_groups: dict[str, list[dict[str, Any]]] = {}
    for relative in sorted(files):
        if not relative.startswith("reviews/") or not relative.endswith(".toml"):
            continue
        try:
            review = tomllib.loads((root / relative).read_text(encoding="utf-8"))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            raise MigrationApplyError(f"review readback failed: {relative}") from exc
        validate_review(review)
        review_groups.setdefault(review["card_id"], []).append(review)
    for card_id, attempts in review_groups.items():
        validate_review_history(
            attempts,
            expected_card_id=card_id,
            workstream_id=workstream["workstream_id"],
        )
    return record


def readback_fixture_destination(
    destination_root: Path,
    bundle: dict[str, Any],
) -> dict[str, Any]:
    """Verify the activated destination without consulting the V1 source."""
    _validate_bundle(bundle)
    if not destination_root.is_dir():
        raise MigrationApplyError("destination is not activated")
    record = _verify_materialized_root(destination_root, bundle)
    return {
        "status": "verified",
        "source_fingerprint": record["source_fingerprint"],
        "output_fingerprint": record["output_fingerprint"],
    }


def rollback_fixture_staging(
    destination_root: Path,
    bundle: dict[str, Any],
) -> dict[str, str]:
    """Remove only an unactivated exact staging tree."""
    _validate_bundle(bundle)
    if destination_root.exists():
        raise MigrationApplyError("activated destination is forward-repair only; rollback is forbidden")
    stage = _stage_path(destination_root, bundle)
    if not stage.exists():
        return {"status": "noop"}
    record_path = stage / "migration" / "migration-record.json"
    if record_path.exists():
        _verify_materialized_root(stage, bundle)
    shutil.rmtree(stage)
    return {"status": "rolled_back"}


def reconcile_uncertain_external_effect(
    readback: Callable[[], str],
) -> dict[str, str]:
    """Read back an uncertain effect before any retry decision."""
    observation = readback()
    if observation == "expected_effect":
        return {"status": "verified", "action": "do_not_retry"}
    if observation == "no_effect":
        return {"status": "verified", "action": "retry_permitted"}
    if observation in {"unknown", "unexpected_effect"}:
        raise MigrationApplyError("external effect remains uncertain; retry is forbidden")
    raise MigrationApplyError("external effect readback returned an unsupported observation")


def apply_fixture_conversion(
    *,
    bundle: dict[str, Any],
    destination_root: Path,
    authorization: str,
    observed_commit: str,
    board_text: str,
    manifest_text: str | None,
    crash_at: str | None = None,
) -> dict[str, str]:
    """Apply one exact conversion to a disposable fixture destination."""
    if authorization != authorization_for(bundle):
        raise MigrationApplyError("explicit exact fixture migration authorization is required")
    if crash_at not in {None, "before_record", "after_record", "after_promotion"}:
        raise MigrationApplyError("unsupported crash injection point")
    _validate_bundle(bundle)
    _verify_current_source(
        bundle,
        observed_commit=observed_commit,
        board_text=board_text,
        manifest_text=manifest_text,
    )

    if destination_root.exists():
        readback_fixture_destination(destination_root, bundle)
        return {"status": "noop", "output_fingerprint": bundle["output_fingerprint"]}

    stage = _stage_path(destination_root, bundle)
    record_path = stage / "migration" / "migration-record.json"
    if stage.exists():
        if record_path.exists():
            _verify_materialized_root(stage, bundle)
        else:
            shutil.rmtree(stage)

    if not stage.exists():
        payloads = _stage_payloads(bundle)
        stage.mkdir(parents=True, exist_ok=False)
        for relative, payload in payloads.items():
            path = stage / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(payload)

        if crash_at == "before_record":
            raise SimulatedMigrationCrash("fixture crash before migration record")

        record = {
            "schema": "pwv2-m06-apply-record-v1",
            "source_fingerprint": bundle["source_fingerprint"],
            "output_fingerprint": bundle["output_fingerprint"],
            "files": {
                relative: _sha256_bytes(payload)
                for relative, payload in sorted(payloads.items())
            },
        }
        record_path.parent.mkdir(parents=True, exist_ok=True)
        record_path.write_bytes(_json_bytes(record))
        _verify_materialized_root(stage, bundle)

        if crash_at == "after_record":
            raise SimulatedMigrationCrash("fixture crash after migration record")

    if destination_root.exists():
        readback_fixture_destination(destination_root, bundle)
        shutil.rmtree(stage)
        return {"status": "noop", "output_fingerprint": bundle["output_fingerprint"]}

    destination_root.parent.mkdir(parents=True, exist_ok=True)
    os.replace(stage, destination_root)

    if crash_at == "after_promotion":
        raise SimulatedMigrationCrash("fixture crash after destination promotion")

    readback_fixture_destination(destination_root, bundle)
    return {"status": "applied", "output_fingerprint": bundle["output_fingerprint"]}
