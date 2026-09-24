#!/usr/bin/env python3
"""PWv2.1 M01 stateless mechanical-policy kernel.

The registry contains only named mechanical predicates over canonical repository
state.  It is not a workflow DSL and it owns no project mutation.  Semantic
reasoning remains in the workflow modules/roles.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, Protocol

from tools.obligation_contract import (
    compile_execution_obligation,
    reconcile_execution_result,
    validate_execution_result,
)
from tools.state_contract import ValidationError

SUPPORTED_REGISTRY_VERSION = 1
SUPPORTED_SCHEMA_VERSION = 1
REGISTRY_KIND = "pwv2_mechanical_policy"
RULE_ID = re.compile(r"^PWV21-K[0-9]{3}$")
INPUT_PATH = re.compile(r"^[a-z_][a-z0-9_]*(?:\.[a-z_][a-z0-9_]*)*$")
ALLOWED_DISPOSITIONS = {"route", "stop", "recovery"}


class KernelContractError(ValidationError):
    """Mechanical-policy package or input disagrees with the fixed contract."""


class DeferredKernelCapabilityError(NotImplementedError):
    """A declared seam belongs to a later PWv2.1 milestone."""


@dataclass(frozen=True)
class MechanicalDecision:
    rule_id: str
    disposition: str
    obligation: str
    owner_module: str


Predicate = Callable[[Mapping[str, Any]], bool]


def _eq(name: str, expected: Any) -> Predicate:
    return lambda inputs: inputs[name] == expected


def _planning_frozen_b_due(inputs: Mapping[str, Any]) -> bool:
    return inputs["planning.state"] == "frozen" and inputs["planning.premium_b"] == "due"


def _planning_approved_c_due(inputs: Mapping[str, Any]) -> bool:
    return inputs["planning.state"] == "approved" and inputs["planning.premium_c"] == "due"


def _board_statuses(inputs: Mapping[str, Any]) -> list[str]:
    cards = inputs["board.cards"]
    if not isinstance(cards, list):
        raise KernelContractError("board.cards must be a list")
    statuses: list[str] = []
    for index, card in enumerate(cards):
        if not isinstance(card, Mapping) or not isinstance(card.get("status"), str):
            raise KernelContractError(f"board.cards[{index}] must carry string status")
        statuses.append(card["status"])
    return statuses


def _board_one_ready_card(inputs: Mapping[str, Any]) -> bool:
    return _board_statuses(inputs).count("ready") == 1


def _board_all_cards_done(inputs: Mapping[str, Any]) -> bool:
    statuses = _board_statuses(inputs)
    return bool(statuses) and all(status == "done" for status in statuses)


DEFAULT_PREDICATES: dict[str, Predicate] = {
    "definition_premium_a_due": _eq("definition.premium_a", "due"),
    "planning_premium_a_due": _eq("planning.premium_a", "due"),
    "planning_state_draft": _eq("planning.state", "draft"),
    "planning_frozen_premium_b_due": _planning_frozen_b_due,
    "plan_review_pending": _eq("plan_review.verdict", "pending"),
    "plan_review_green": _eq("plan_review.verdict", "green"),
    "planning_approved_premium_c_due": _planning_approved_c_due,
    "tracker_ambiguous": _eq("tracker.state", "ambiguous"),
    "brainstorm_explicit_user_stop": _eq("brainstorm.explicit_user_stop", True),
    "brainstorm_active": _eq("brainstorm.state", "active"),
    "board_one_ready_card": _board_one_ready_card,
    "board_all_cards_done": _board_all_cards_done,
}


class PolicyKernelSeams(Protocol):
    """Stable M01 seam names; full Obligation/Result behavior is M02-owned."""

    def route(self, rule_id: str, canonical_state: Mapping[str, Any]) -> MechanicalDecision | None: ...
    def validate(self) -> None: ...
    def compile_obligations(self, *args: Any, **kwargs: Any) -> Any: ...
    def validate_results(self, *args: Any, **kwargs: Any) -> Any: ...
    def reconcile(self, *args: Any, **kwargs: Any) -> Any: ...


def _exact_keys(value: Mapping[str, Any], expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        raise KernelContractError(f"{label}: keys mismatch missing={missing} extra={extra}")


def _extract_path(root: Mapping[str, Any], path: str) -> Any:
    value: Any = root
    for part in path.split("."):
        if not isinstance(value, Mapping) or part not in value:
            raise KernelContractError(f"missing canonical input {path!r}")
        value = value[part]
    return value


class PolicyKernel:
    """Validated, immutable-by-convention, read-only mechanical rule evaluator."""

    def __init__(
        self,
        registry: Mapping[str, Any],
        *,
        implementations: Mapping[str, Predicate] | None = None,
    ) -> None:
        self._registry = json.loads(json.dumps(registry))
        self._implementations = dict(implementations or DEFAULT_PREDICATES)
        self._rules_by_id: dict[str, dict[str, Any]] = {}
        self._validate_registry()

    @classmethod
    def from_path(cls, path: Path) -> "PolicyKernel":
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise KernelContractError(f"cannot load mechanical-policy registry: {exc}") from exc
        if not isinstance(payload, Mapping):
            raise KernelContractError("mechanical-policy registry must be a JSON object")
        return cls(payload)

    @classmethod
    def from_mapping(
        cls,
        payload: Mapping[str, Any],
        *,
        implementations: Mapping[str, Predicate] | None = None,
    ) -> "PolicyKernel":
        return cls(payload, implementations=implementations)

    @property
    def registry(self) -> dict[str, Any]:
        return json.loads(json.dumps(self._registry))

    @property
    def rule_ids(self) -> tuple[str, ...]:
        return tuple(rule["id"] for rule in sorted(self._rules_by_id.values(), key=lambda item: item["precedence"]))

    def _validate_registry(self) -> None:
        _exact_keys(
            self._registry,
            {"kind", "registry_version", "schema_version", "rules"},
            "registry",
        )
        if self._registry["kind"] != REGISTRY_KIND:
            raise KernelContractError(f"registry: unsupported kind {self._registry['kind']!r}")
        if self._registry["registry_version"] != SUPPORTED_REGISTRY_VERSION:
            raise KernelContractError(
                f"registry: unsupported registry_version {self._registry['registry_version']!r}"
            )
        if self._registry["schema_version"] != SUPPORTED_SCHEMA_VERSION:
            raise KernelContractError(
                f"registry: unsupported schema_version {self._registry['schema_version']!r}"
            )
        rules = self._registry["rules"]
        if not isinstance(rules, list) or not rules:
            raise KernelContractError("registry.rules must be a non-empty array")

        ids: set[str] = set()
        predicates: set[str] = set()
        precedences: set[int] = set()
        for index, raw_rule in enumerate(rules):
            if not isinstance(raw_rule, Mapping):
                raise KernelContractError(f"registry.rules[{index}] must be an object")
            _exact_keys(
                raw_rule,
                {"id", "precedence", "predicate", "inputs", "outcome", "semantics"},
                f"registry.rules[{index}]",
            )
            rule_id = raw_rule["id"]
            if not isinstance(rule_id, str) or RULE_ID.fullmatch(rule_id) is None:
                raise KernelContractError(f"registry.rules[{index}].id is invalid")
            if rule_id in ids:
                raise KernelContractError(f"duplicate rule id {rule_id!r}")
            ids.add(rule_id)

            precedence = raw_rule["precedence"]
            if not isinstance(precedence, int) or precedence <= 0:
                raise KernelContractError(f"{rule_id}: precedence must be positive integer")
            if precedence in precedences:
                raise KernelContractError(f"duplicate precedence {precedence}")
            precedences.add(precedence)

            predicate = raw_rule["predicate"]
            if not isinstance(predicate, str) or predicate not in self._implementations:
                raise KernelContractError(f"{rule_id}: unknown predicate {predicate!r}")
            if predicate in predicates:
                raise KernelContractError(f"predicate {predicate!r} is bound more than once")
            predicates.add(predicate)

            inputs = raw_rule["inputs"]
            if (
                not isinstance(inputs, list)
                or not inputs
                or len(set(inputs)) != len(inputs)
                or not all(isinstance(item, str) and INPUT_PATH.fullmatch(item) for item in inputs)
            ):
                raise KernelContractError(f"{rule_id}: inputs must be unique canonical dotted paths")

            outcome = raw_rule["outcome"]
            if not isinstance(outcome, Mapping):
                raise KernelContractError(f"{rule_id}: outcome must be an object")
            _exact_keys(outcome, {"disposition", "obligation", "owner_module"}, f"{rule_id}.outcome")
            if outcome["disposition"] not in ALLOWED_DISPOSITIONS:
                raise KernelContractError(f"{rule_id}: invalid disposition")
            if not isinstance(outcome["obligation"], str) or not outcome["obligation"].strip():
                raise KernelContractError(f"{rule_id}: missing obligation")
            owner = outcome["owner_module"]
            if not isinstance(owner, str) or not owner.startswith("workflow/") or not owner.endswith(".md"):
                raise KernelContractError(f"{rule_id}: invalid owner_module")
            semantics = raw_rule["semantics"]
            if not isinstance(semantics, str) or not semantics.strip():
                raise KernelContractError(f"{rule_id}: missing semantics")

            self._rules_by_id[rule_id] = dict(raw_rule)

        implementation_names = set(self._implementations)
        if predicates != implementation_names:
            raise KernelContractError(
                "registry/implementation predicate vocabulary mismatch: "
                f"registry_only={sorted(predicates - implementation_names)} "
                f"implementation_only={sorted(implementation_names - predicates)}"
            )

    def validate(self) -> None:
        """Constructor validation is exhaustive; this is the stable explicit seam."""
        self._validate_registry()

    def route(self, rule_id: str, canonical_state: Mapping[str, Any]) -> MechanicalDecision | None:
        rule = self._rules_by_id.get(rule_id)
        if rule is None:
            raise KernelContractError(f"unknown mechanical rule {rule_id!r}")
        if not isinstance(canonical_state, Mapping):
            raise KernelContractError("canonical_state must be a mapping")
        inputs = {path: _extract_path(canonical_state, path) for path in rule["inputs"]}
        matched = self._implementations[rule["predicate"]](inputs)
        if not isinstance(matched, bool):
            raise KernelContractError(f"{rule_id}: predicate returned non-boolean")
        if not matched:
            return None
        outcome = rule["outcome"]
        return MechanicalDecision(
            rule_id=rule_id,
            disposition=outcome["disposition"],
            obligation=outcome["obligation"],
            owner_module=outcome["owner_module"],
        )

    def matches(self, rule_id: str, canonical_state: Mapping[str, Any]) -> bool:
        return self.route(rule_id, canonical_state) is not None

    def render_projection(self) -> str:
        lines = [
            "# PWv2.1 Mechanical Policy Projection",
            "",
            "> GENERATED from `policy/mechanical_policy.json` by `tools/policy_kernel.py`.",
            "> Do not edit rule semantics here; change the registry and regenerate/verify this projection.",
            "",
            f"Registry version: `{self._registry['registry_version']}`  ",
            f"Schema version: `{self._registry['schema_version']}`",
            "",
            "This projection documents only named mechanical predicates over canonical repository state.",
            "It is not a workflow DSL, does not own semantic judgment, and authorizes no canonical writes.",
            "",
        ]
        for rule in sorted(self._rules_by_id.values(), key=lambda item: item["precedence"]):
            outcome = rule["outcome"]
            lines.extend([
                f"## {rule['id']} — `{rule['predicate']}`",
                "",
                f"- Precedence: `{rule['precedence']}`",
                "- Canonical inputs: " + ", ".join(f"`{item}`" for item in rule["inputs"]),
                f"- Outcome: `{outcome['disposition']} / {outcome['obligation']}`",
                f"- Owner: `{outcome['owner_module']}`",
                f"- Semantics: {rule['semantics']}",
                "",
            ])
        return "\n".join(lines).rstrip() + "\n"

    def verify_projection(self, path: Path) -> None:
        try:
            actual = path.read_text(encoding="utf-8")
        except OSError as exc:
            raise KernelContractError(f"cannot read mechanical-policy projection: {exc}") from exc
        expected = self.render_projection()
        if actual != expected:
            raise KernelContractError("registry/contract projection drift")

    def _rule_inputs(
        self,
        rule_id: str,
        canonical_state: Mapping[str, Any],
    ) -> dict[str, Any]:
        rule = self._rules_by_id.get(rule_id)
        if rule is None:
            raise KernelContractError(f"unknown mechanical rule {rule_id!r}")
        if not isinstance(canonical_state, Mapping):
            raise KernelContractError("canonical_state must be a mapping")
        return {
            path: _extract_path(canonical_state, path)
            for path in rule["inputs"]
        }

    def compile_obligations(
        self,
        rule_id: str,
        *,
        canonical_state: Mapping[str, Any],
        **kwargs: Any,
    ) -> dict[str, Any]:
        decision = self.route(rule_id, canonical_state)
        if decision is None:
            raise KernelContractError(
                f"{rule_id}: cannot compile obligation because the registered rule does not match current canonical state"
            )
        if "determining_inputs" in kwargs:
            raise KernelContractError(
                "determining_inputs are kernel-derived from the registered rule and canonical state"
            )
        supplied_role = kwargs.pop("role", decision.obligation)
        if supplied_role != decision.obligation:
            raise KernelContractError(
                f"{rule_id}: role {supplied_role!r} does not match registered obligation {decision.obligation!r}"
            )
        return compile_execution_obligation(
            rule_id=rule_id,
            role=decision.obligation,
            determining_inputs=self._rule_inputs(rule_id, canonical_state),
            **kwargs,
        )

    def validate_results(self, payload: Mapping[str, Any]) -> None:
        validate_execution_result(payload)

    def reconcile(
        self,
        result: Mapping[str, Any],
        obligation: Mapping[str, Any],
        *,
        canonical_state: Mapping[str, Any],
        current_freshness_material: Mapping[str, Any],
        stale_resolution: Mapping[str, Any] | None = None,
        observed_canonical_state: Mapping[str, Any] | None = None,
    ) -> str:
        if not isinstance(obligation, Mapping):
            raise KernelContractError("obligation must be a mapping")
        rule_id = obligation.get("rule_id")
        rule = self._rules_by_id.get(rule_id) if isinstance(rule_id, str) else None
        if rule is None:
            raise KernelContractError(f"unknown mechanical rule {rule_id!r}")
        expected_role = rule["outcome"]["obligation"]
        if obligation.get("role") != expected_role:
            raise KernelContractError(
                f"{rule_id}: obligation role does not match registered obligation {expected_role!r}"
            )
        if not isinstance(current_freshness_material, Mapping):
            raise KernelContractError("current_freshness_material must be a mapping")
        current_material = json.loads(json.dumps(current_freshness_material))
        current_material["inputs"] = self._rule_inputs(rule_id, canonical_state)
        return reconcile_execution_result(
            result,
            obligation,
            current_freshness_material=current_material,
            stale_resolution=stale_resolution,
            observed_canonical_state=observed_canonical_state,
        )
