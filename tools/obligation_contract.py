#!/usr/bin/env python3
"""PWv2.1 M02 transport-neutral Execution Obligation / Result contracts."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import PurePosixPath
from typing import Any, Callable, Mapping, Sequence

from tools.close_contract import CloseContractError, external_effect_recovery_action

OBLIGATION_KIND = "pwv2_execution_obligation"
RESULT_KIND = "pwv2_execution_result"
SUPPORTED_SCHEMA_VERSION = 1
SHA40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
RULE_ID = re.compile(r"^PWV21-K[0-9]{3}$")
REPOSITORY = re.compile(r"^[^/]+/[^/]+$")
RESULT_STATUSES = {"success", "blocked", "failed"}
TEST_STATUSES = {"green", "red", "not_run"}
READBACK_STATUSES = {"verified", "failed", "not_applicable"}
INPUT_PATH = re.compile(r"^[a-z_][a-z0-9_]*(?:\.[a-z_][a-z0-9_]*)*$")
STALE_ACTIONS = {"reuse", "rebase", "reconcile"}
TELEMETRY_KEYS = {
    "provider", "model", "model_id", "worker", "worker_id", "session", "session_id",
    "retry", "retries", "worktree", "paseo", "runtime", "invocation", "scheduler",
}


class ExecutionEnvelopeError(ValueError):
    """Typed obligation/result payload violates the M02 contract."""


ExactReader = Callable[[Mapping[str, str]], bytes | str]


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ExecutionEnvelopeError(message)


def canonical_json(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError) as exc:
        raise ExecutionEnvelopeError("canonical JSON value must be finite and JSON-serializable") from exc


def _sha256(value: Any) -> str:
    return "sha256:" + hashlib.sha256(canonical_json(value)).hexdigest()


def git_blob_sha(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()


def _safe_path(raw: Any, label: str) -> str:
    _require(isinstance(raw, str) and raw, f"{label}: path must be non-empty string")
    path = PurePosixPath(raw)
    _require(not path.is_absolute() and "." not in path.parts and ".." not in path.parts,
             f"{label}: unsafe repository path")
    return raw


def _reject_telemetry_keys(value: Any, where: str = "$") -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = str(key).lower()
            _require(normalized not in TELEMETRY_KEYS,
                     f"{where}: telemetry key {key!r} is non-canonical")
            _reject_telemetry_keys(child, f"{where}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _reject_telemetry_keys(child, f"{where}[{index}]")


def validate_exact_ref(ref: Any, label: str = "ref") -> dict[str, str]:
    _require(isinstance(ref, Mapping), f"{label}: exact ref must be an object")
    expected = {"repository", "commit", "path", "blob"}
    _require(set(ref) == expected, f"{label}: exact ref keys must be {sorted(expected)}")
    repository = ref["repository"]
    _require(isinstance(repository, str) and REPOSITORY.fullmatch(repository) is not None,
             f"{label}: repository must be owner/name")
    commit = ref["commit"]
    blob = ref["blob"]
    _require(isinstance(commit, str) and SHA40.fullmatch(commit) is not None,
             f"{label}: commit must be exact 40-hex")
    _require(isinstance(blob, str) and SHA40.fullmatch(blob) is not None,
             f"{label}: blob must be exact 40-hex")
    path = _safe_path(ref["path"], f"{label}.path")
    return {"repository": repository, "commit": commit, "path": path, "blob": blob}


def _string_list(value: Any, label: str) -> list[str]:
    _require(isinstance(value, Sequence) and not isinstance(value, (str, bytes)),
             f"{label}: expected an array")
    result = list(value)
    _require(all(isinstance(item, str) and item.strip() for item in result),
             f"{label}: entries must be non-empty strings")
    return result


def resolve_authority_bundle(
    refs: Sequence[Mapping[str, Any]],
    reader: ExactReader,
) -> list[dict[str, str]]:
    _require(isinstance(refs, Sequence) and not isinstance(refs, (str, bytes)) and refs,
             "authority: at least one exact authority ref is required")
    normalized = [validate_exact_ref(ref, f"authority[{index}]") for index, ref in enumerate(refs)]
    keys = [(ref["repository"], ref["commit"], ref["path"], ref["blob"]) for ref in normalized]
    _require(len(keys) == len(set(keys)), "authority: duplicate exact ref")
    bundle: list[dict[str, str]] = []
    for ref in sorted(normalized, key=lambda item: (item["repository"], item["path"], item["commit"], item["blob"])):
        raw = reader(ref)
        content = raw.encode("utf-8") if isinstance(raw, str) else raw
        _require(isinstance(content, bytes), "authority reader must return bytes or text")
        _require(git_blob_sha(content) == ref["blob"],
                 f"authority: blob mismatch for {ref['repository']}:{ref['path']}")
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ExecutionEnvelopeError("authority: bundle sources must be UTF-8 text") from exc
        bundle.append({
            **ref,
            "content_sha256": "sha256:" + hashlib.sha256(content).hexdigest(),
            "content": text,
        })
    return bundle


def _completion(
    acceptance: Sequence[str],
    tests: Sequence[str],
    evidence: Sequence[str],
) -> dict[str, list[str]]:
    return {
        "acceptance": _string_list(acceptance, "completion.acceptance"),
        "tests": _string_list(tests, "completion.tests"),
        "evidence": _string_list(evidence, "completion.evidence"),
    }


def _condition_list(value: Any, label: str) -> list[dict[str, Any]]:
    _require(isinstance(value, Sequence) and not isinstance(value, (str, bytes)),
             f"{label}: expected an array")
    result: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        _require(isinstance(item, Mapping) and set(item) == {"path", "equals"},
                 f"{label}[{index}]: expected path/equals object")
        path = item["path"]
        _require(isinstance(path, str) and INPUT_PATH.fullmatch(path) is not None,
                 f"{label}[{index}]: invalid canonical path")
        _reject_telemetry_keys(item["equals"], f"{label}[{index}].equals")
        try:
            exact_value = json.loads(canonical_json(item["equals"]).decode("utf-8"))
        except (TypeError, ValueError) as exc:
            raise ExecutionEnvelopeError(f"{label}[{index}]: equals must be JSON-serializable") from exc
        result.append({"path": path, "equals": exact_value})
    return result


def _mutation(
    preconditions: Sequence[Mapping[str, Any]],
    postconditions: Sequence[Mapping[str, Any]],
) -> dict[str, list[dict[str, Any]]]:
    return {
        "preconditions": _condition_list(preconditions, "mutation.preconditions"),
        "postconditions": _condition_list(postconditions, "mutation.postconditions"),
    }


def build_freshness_material(
    *,
    subject: Mapping[str, Any],
    authority_refs: Sequence[Mapping[str, Any]],
    prerequisites: Sequence[str],
    constraints: Sequence[str],
    completion: Mapping[str, Any],
    mutation: Mapping[str, Any],
    determining_inputs: Mapping[str, Any],
) -> dict[str, Any]:
    _require(isinstance(determining_inputs, Mapping), "freshness inputs must be an object")
    _reject_telemetry_keys(determining_inputs, "freshness.inputs")
    authority = [validate_exact_ref(ref, f"authority[{i}]") for i, ref in enumerate(authority_refs)]
    authority.sort(key=lambda item: (item["repository"], item["path"], item["commit"], item["blob"]))
    return {
        "subject": validate_exact_ref(subject, "subject"),
        "authority": authority,
        "prerequisites": _string_list(prerequisites, "prerequisites"),
        "constraints": _string_list(constraints, "constraints"),
        "completion": dict(completion),
        "mutation": dict(mutation),
        "inputs": json.loads(canonical_json(determining_inputs).decode("utf-8")),
    }


def _validate_freshness_material(material: Any) -> None:
    _require(isinstance(material, Mapping), "freshness material must be an object")
    expected = {
        "subject", "authority", "prerequisites", "constraints",
        "completion", "mutation", "inputs",
    }
    _require(set(material) == expected, "freshness material: invalid keys")
    validate_exact_ref(material["subject"], "freshness.subject")
    authority = material["authority"]
    _require(isinstance(authority, list) and authority, "freshness.authority must be non-empty")
    normalized = [validate_exact_ref(ref, f"freshness.authority[{i}]") for i, ref in enumerate(authority)]
    _require(normalized == sorted(
        normalized,
        key=lambda item: (item["repository"], item["path"], item["commit"], item["blob"]),
    ), "freshness.authority must use canonical ordering")
    _string_list(material["prerequisites"], "freshness.prerequisites")
    _string_list(material["constraints"], "freshness.constraints")
    completion = material["completion"]
    _require(isinstance(completion, Mapping) and set(completion) == {"acceptance", "tests", "evidence"},
             "freshness.completion: invalid keys")
    for key in ("acceptance", "tests", "evidence"):
        _string_list(completion[key], f"freshness.completion.{key}")
    mutation = material["mutation"]
    _require(isinstance(mutation, Mapping) and set(mutation) == {"preconditions", "postconditions"},
             "freshness.mutation: invalid keys")
    _condition_list(mutation["preconditions"], "freshness.mutation.preconditions")
    _condition_list(mutation["postconditions"], "freshness.mutation.postconditions")
    _require(isinstance(material["inputs"], Mapping), "freshness.inputs must be an object")
    _reject_telemetry_keys(material["inputs"], "freshness.inputs")


def freshness_fingerprint(material: Mapping[str, Any]) -> str:
    _validate_freshness_material(material)
    _reject_telemetry_keys(material, "freshness")
    return _sha256(material)


def compile_execution_obligation(
    *,
    rule_id: str,
    role: str,
    subject: Mapping[str, Any],
    authority_refs: Sequence[Mapping[str, Any]],
    authority_reader: ExactReader,
    prerequisites: Sequence[str],
    constraints: Sequence[str],
    acceptance: Sequence[str],
    tests: Sequence[str],
    evidence_requirements: Sequence[str],
    determining_inputs: Mapping[str, Any],
    mutation_preconditions: Sequence[Mapping[str, Any]],
    mutation_postconditions: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    _require(isinstance(rule_id, str) and RULE_ID.fullmatch(rule_id) is not None,
             "obligation.rule_id must be a registered-rule identifier")
    _require(isinstance(role, str) and role.strip(), "obligation.role must be non-empty")
    exact_subject = validate_exact_ref(subject, "subject")
    normalized_authority = [validate_exact_ref(ref, f"authority[{i}]") for i, ref in enumerate(authority_refs)]
    bundle = resolve_authority_bundle(normalized_authority, authority_reader)
    completion = _completion(acceptance, tests, evidence_requirements)
    mutation = _mutation(mutation_preconditions, mutation_postconditions)
    prereq = _string_list(prerequisites, "prerequisites")
    bounded_constraints = _string_list(constraints, "constraints")
    material = build_freshness_material(
        subject=exact_subject,
        authority_refs=normalized_authority,
        prerequisites=prereq,
        constraints=bounded_constraints,
        completion=completion,
        mutation=mutation,
        determining_inputs=determining_inputs,
    )
    fingerprint = freshness_fingerprint(material)
    obligation_id = _sha256({
        "rule_id": rule_id,
        "role": role,
        "subject": exact_subject,
        "freshness_fingerprint": fingerprint,
    })
    payload = {
        "kind": OBLIGATION_KIND,
        "schema_version": SUPPORTED_SCHEMA_VERSION,
        "obligation_id": obligation_id,
        "rule_id": rule_id,
        "role": role,
        "subject": exact_subject,
        "authority_bundle": bundle,
        "prerequisites": prereq,
        "constraints": bounded_constraints,
        "completion": completion,
        "freshness": {"fingerprint": fingerprint, "material": material},
        "mutation": mutation,
    }
    validate_execution_obligation(payload)
    return payload


def _validate_authority_source(source: Any, label: str) -> None:
    _require(isinstance(source, Mapping), f"{label}: must be object")
    expected = {"repository", "commit", "path", "blob", "content_sha256", "content"}
    _require(set(source) == expected, f"{label}: invalid keys")
    ref = {key: source[key] for key in ("repository", "commit", "path", "blob")}
    validate_exact_ref(ref, label)
    content = source["content"]
    digest = source["content_sha256"]
    _require(isinstance(content, str), f"{label}.content must be UTF-8 text")
    _require(isinstance(digest, str) and SHA256.fullmatch(digest) is not None,
             f"{label}.content_sha256 must be sha256")
    raw = content.encode("utf-8")
    _require(digest == "sha256:" + hashlib.sha256(raw).hexdigest(),
             f"{label}: content sha256 mismatch")
    _require(source["blob"] == git_blob_sha(raw), f"{label}: git blob mismatch")


def validate_execution_obligation(payload: Any) -> None:
    _require(isinstance(payload, Mapping), "obligation must be object")
    _reject_telemetry_keys(payload, "obligation")
    expected = {
        "kind", "schema_version", "obligation_id", "rule_id", "role", "subject",
        "authority_bundle", "prerequisites", "constraints", "completion",
        "freshness", "mutation",
    }
    _require(set(payload) == expected, "obligation: invalid top-level keys")
    _require(payload["kind"] == OBLIGATION_KIND, "obligation: wrong kind")
    _require(payload["schema_version"] == SUPPORTED_SCHEMA_VERSION,
             f"obligation: unsupported schema_version {payload['schema_version']!r}")
    _require(isinstance(payload["rule_id"], str) and RULE_ID.fullmatch(payload["rule_id"]) is not None,
             "obligation: invalid rule_id")
    _require(isinstance(payload["role"], str) and payload["role"].strip(), "obligation: invalid role")
    subject = validate_exact_ref(payload["subject"], "obligation.subject")
    bundle = payload["authority_bundle"]
    _require(isinstance(bundle, list) and bundle, "obligation: authority_bundle must be non-empty")
    for index, source in enumerate(bundle):
        _validate_authority_source(source, f"obligation.authority_bundle[{index}]")
    bundle_refs = [
        {key: source[key] for key in ("repository", "commit", "path", "blob")}
        for source in bundle
    ]
    _string_list(payload["prerequisites"], "obligation.prerequisites")
    _string_list(payload["constraints"], "obligation.constraints")
    completion = payload["completion"]
    _require(isinstance(completion, Mapping) and set(completion) == {"acceptance", "tests", "evidence"},
             "obligation.completion: invalid keys")
    for key in ("acceptance", "tests", "evidence"):
        _string_list(completion[key], f"obligation.completion.{key}")
    mutation = payload["mutation"]
    _require(isinstance(mutation, Mapping) and set(mutation) == {"preconditions", "postconditions"},
             "obligation.mutation: invalid keys")
    _condition_list(mutation["preconditions"], "obligation.mutation.preconditions")
    _condition_list(mutation["postconditions"], "obligation.mutation.postconditions")
    freshness = payload["freshness"]
    _require(isinstance(freshness, Mapping) and set(freshness) == {"fingerprint", "material"},
             "obligation.freshness: invalid keys")
    fingerprint = freshness["fingerprint"]
    _require(isinstance(fingerprint, str) and SHA256.fullmatch(fingerprint) is not None,
             "obligation.freshness: invalid fingerprint")
    _require(fingerprint == freshness_fingerprint(freshness["material"]),
             "obligation: freshness material drift")
    _require(bundle_refs == freshness["material"]["authority"],
             "obligation: authority bundle/freshness drift")
    _require(subject == freshness["material"]["subject"],
             "obligation: subject/freshness drift")
    _require(payload["prerequisites"] == freshness["material"]["prerequisites"],
             "obligation: prerequisites/freshness drift")
    _require(payload["constraints"] == freshness["material"]["constraints"],
             "obligation: constraints/freshness drift")
    _require(payload["completion"] == freshness["material"]["completion"],
             "obligation: completion/freshness drift")
    _require(payload["mutation"] == freshness["material"]["mutation"],
             "obligation: mutation/freshness drift")
    obligation_id = payload["obligation_id"]
    _require(isinstance(obligation_id, str) and SHA256.fullmatch(obligation_id) is not None,
             "obligation: invalid obligation_id")
    expected_id = _sha256({
        "rule_id": payload["rule_id"],
        "role": payload["role"],
        "subject": subject,
        "freshness_fingerprint": fingerprint,
    })
    _require(obligation_id == expected_id, "obligation: deterministic identity drift")


def serialize_obligation(payload: Mapping[str, Any]) -> bytes:
    validate_execution_obligation(payload)
    return canonical_json(payload) + b"\n"


def validate_execution_result(payload: Any) -> None:
    _require(isinstance(payload, Mapping), "result must be object")
    _reject_telemetry_keys(payload, "result")
    expected = {
        "kind", "schema_version", "obligation_id", "freshness_fingerprint", "status",
        "subject", "changed_artifacts", "tests", "evidence", "readback",
        "blocker", "semantic_outcome",
    }
    _require(set(payload) == expected, "result: invalid top-level keys")
    _require(payload["kind"] == RESULT_KIND, "result: wrong kind")
    _require(payload["schema_version"] == SUPPORTED_SCHEMA_VERSION,
             f"result: unsupported schema_version {payload['schema_version']!r}")
    for key in ("obligation_id", "freshness_fingerprint"):
        _require(isinstance(payload[key], str) and SHA256.fullmatch(payload[key]) is not None,
                 f"result: invalid {key}")
    _require(payload["status"] in RESULT_STATUSES, "result: invalid status")
    validate_exact_ref(payload["subject"], "result.subject")
    changed = payload["changed_artifacts"]
    _require(isinstance(changed, list), "result.changed_artifacts must be array")
    for index, ref in enumerate(changed):
        validate_exact_ref(ref, f"result.changed_artifacts[{index}]")
    tests = payload["tests"]
    _require(isinstance(tests, list), "result.tests must be array")
    for index, item in enumerate(tests):
        _require(isinstance(item, Mapping) and set(item) == {"name", "status", "evidence"},
                 f"result.tests[{index}]: invalid keys")
        _require(isinstance(item["name"], str) and item["name"].strip(),
                 f"result.tests[{index}]: invalid name")
        _require(item["status"] in TEST_STATUSES, f"result.tests[{index}]: invalid status")
        _require(isinstance(item["evidence"], str), f"result.tests[{index}]: invalid evidence")
    _string_list(payload["evidence"], "result.evidence")
    readback = payload["readback"]
    _require(isinstance(readback, list), "result.readback must be array")
    for index, item in enumerate(readback):
        _require(isinstance(item, Mapping) and set(item) == {"target", "status", "observation"},
                 f"result.readback[{index}]: invalid keys")
        _require(isinstance(item["target"], str) and item["target"].strip(),
                 f"result.readback[{index}]: invalid target")
        _require(item["status"] in READBACK_STATUSES, f"result.readback[{index}]: invalid status")
        _require(isinstance(item["observation"], str) and item["observation"].strip(),
                 f"result.readback[{index}]: invalid observation")
    blocker = payload["blocker"]
    _require(blocker is None or (isinstance(blocker, str) and blocker.strip()),
             "result.blocker must be null or non-empty string")
    if payload["status"] == "blocked":
        _require(isinstance(blocker, str) and blocker.strip(), "blocked result requires blocker")
    _require(isinstance(payload["semantic_outcome"], str) and payload["semantic_outcome"].strip(),
             "result.semantic_outcome must be non-empty")


def serialize_result(payload: Mapping[str, Any]) -> bytes:
    validate_execution_result(payload)
    return canonical_json(payload) + b"\n"


def reconcile_execution_result(
    result: Mapping[str, Any],
    obligation: Mapping[str, Any],
    *,
    current_freshness_material: Mapping[str, Any],
    stale_resolution: Mapping[str, Any] | None = None,
) -> str:
    validate_execution_obligation(obligation)
    validate_execution_result(result)
    _require(result["obligation_id"] == obligation["obligation_id"],
             "result: obligation binding mismatch")
    _require(result["freshness_fingerprint"] == obligation["freshness"]["fingerprint"],
             "result: original freshness binding mismatch")
    _require(result["subject"] == obligation["subject"],
             "result: subject binding mismatch")
    current = freshness_fingerprint(current_freshness_material)
    prior = obligation["freshness"]["fingerprint"]
    if current == prior:
        return "accept"
    if stale_resolution is None:
        return "reexecute"
    expected = {
        "prior_fingerprint", "current_fingerprint", "action", "safety_proven", "basis",
    }
    _require(isinstance(stale_resolution, Mapping) and set(stale_resolution) == expected,
             "stale result: invalid resolution proof")
    _require(stale_resolution["prior_fingerprint"] == prior
             and stale_resolution["current_fingerprint"] == current,
             "stale result: proof fingerprint mismatch")
    _require(stale_resolution["action"] in STALE_ACTIONS,
             "stale result: invalid safe resolution action")
    _require(stale_resolution["safety_proven"] is True,
             "stale result: resolution proof does not establish safety")
    _require(isinstance(stale_resolution["basis"], str) and stale_resolution["basis"].strip(),
             "stale result: resolution proof basis is required")
    return stale_resolution["action"]


def _extract_canonical_path(root: Mapping[str, Any], path: str) -> Any:
    value: Any = root
    for part in path.split("."):
        _require(isinstance(value, Mapping) and part in value,
                 f"mutation readback missing canonical path {path!r}")
        value = value[part]
    return value


def _verify_conditions(conditions: Sequence[Mapping[str, Any]], state: Mapping[str, Any], label: str) -> str:
    _require(isinstance(state, Mapping), f"{label}: state must be an object")
    for condition in conditions:
        actual = _extract_canonical_path(state, condition["path"])
        _require(actual == condition["equals"],
                 f"{label}: condition failed for {condition['path']!r}")
    return "verified"


def verify_mutation_preconditions(
    obligation: Mapping[str, Any],
    current_state: Mapping[str, Any],
) -> str:
    validate_execution_obligation(obligation)
    return _verify_conditions(obligation["mutation"]["preconditions"], current_state, "mutation precondition")


def verify_mutation_readback(
    obligation: Mapping[str, Any],
    observed_state: Mapping[str, Any],
) -> str:
    validate_execution_obligation(obligation)
    return _verify_conditions(obligation["mutation"]["postconditions"], observed_state, "mutation readback")


def external_effect_retry_decision(*, readback_state: str, observation: str) -> str:
    try:
        return external_effect_recovery_action(
            readback_state=readback_state,
            observation=observation,
        )
    except CloseContractError as exc:
        raise ExecutionEnvelopeError(str(exc)) from exc
