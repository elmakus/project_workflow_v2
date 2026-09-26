#!/usr/bin/env python3
"""Runtime-neutral Project Workflow V2 obligation selector through M04-T04."""

from __future__ import annotations

import argparse
import json
import subprocess
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path, PurePosixPath

from tools.editorial_exemption_contract import (
    EditorialExemptionError,
    validate_editorial_exemption_classification,
)
from tools.exact_locator import (
    ExactLocatorError,
    normalize_locator_path,
    verify_exact_git_locator,
    verify_worktree_freshness,
)
from tools.definition_authority import (
    DefinitionAuthorityError,
    verify_planning_authority_freshness,
)
from tools.execution_contract import ExecutionContractError, is_accepted_success, parse_card_result
from tools.recovery_contract import RecoveryContractError, classify_resolution, exact_result_subject, review_subject
from tools.research_provenance import (
    ResearchProvenanceError,
    verify_complete_board_return,
    verify_complete_workstream_return,
    verify_consumed_prior_art_proof,
)
from tools.review_contract import (
    can_finalize_review_obligation,
    remaining_closure_findings,
    review_convergence_state,
    review_kind,
)
from tools.policy_kernel import MechanicalDecision, PolicyKernel
from tools.topology_contract import compute_card_contract_digest, ready_topology_hold
from tools.late_oversize_contract import (
    bound_handoff_hold,
    pending_late_return,
    unfinished_residual_scope,
)
from tools.live_finding_contract import (
    LiveFindingError,
    live_finding_owner_module,
    validate_finding_trigger_gates,
    validate_live_findings,
    verify_finding_trigger_records,
    verify_live_finding_records,
)
from tools.live_consumer_contract import (
    LiveConsumerError,
    validate_live_consumer_gates,
    verify_live_consumer_records,
)
from tools.review_attempt_provenance import (
    ReviewAttemptProvenanceError,
    verify_legacy_migration,
    verify_review_attempt_locator,
    verify_terminal_append_only_from_git,
)
from tools.state_contract import (
    ValidationError,
    read_project,
    read_toml,
    validate_board,
    validate_brainstorm,
    validate_definition,
    validate_intake,
    validate_plan_review,
    parse_task_card,
    validate_planning,
    validate_project,
    validate_research,
    validate_review_history,
    validate_blocker,
    validate_tracker,
    validate_workstream,
)

PRIORITY_FOUNDATION = (
    "explicit_human_or_premium_boundary",
    "independent_review_or_red_correction",
    "research_return",
    "result_reconciliation",
    "current_card",
    "next_legal_stage",
)

REAL_STOP_FOUNDATION = (
    "explicit_user_stop",
    "unresolved_user_or_product_decision",
    "authorization_alignment_or_promotion_gate",
    "premium_gate",
    "independence_boundary",
    "nonremediable_access_runtime_or_input_blocker",
    "end_of_approved_scope",
)


@dataclass(frozen=True)
class RouteResult:
    disposition: str
    obligation: str
    subject: str | None
    owner_module: str | None
    reason: str
    read_set: tuple[str, ...]


class Reads:
    def __init__(self, project_root: Path, package_root: Path) -> None:
        self.project_root = project_root.resolve()
        self.package_root = package_root.resolve()
        self.items: list[str] = []

    def _read_path(self, root: Path, raw: str, owner: str) -> Path:
        try:
            canonical = normalize_locator_path(raw, owner)
        except ExactLocatorError as exc:
            raise ValidationError(f"unsafe {owner} path {raw!r}: {exc}") from exc
        rel = PurePosixPath(canonical)
        path = (root / Path(*rel.parts)).resolve()
        try:
            path.relative_to(root)
        except ValueError as exc:
            raise ValidationError(f"{owner} path escapes root: {raw!r}") from exc
        self.items.append(f"{owner}:{raw}")
        return path

    def project(self, raw: str) -> Path:
        return self._read_path(self.project_root, raw, "project")

    def package(self, raw: str) -> Path:
        return self._read_path(self.package_root, raw, "package")


def result(reads: Reads, disposition: str, obligation: str, reason: str,
           subject: str | None = None, owner_module: str | None = None) -> RouteResult:
    if disposition == "stop":
        try:
            reads.package("workflow/USER_STOP.md").read_text(encoding="utf-8")
        except OSError as exc:
            return recovery(reads, f"real-stop formatter unavailable: {exc}")
    return RouteResult(disposition, obligation, subject, owner_module, reason, tuple(reads.items))


def recovery(reads: Reads, reason: str) -> RouteResult:
    try:
        reads.package("workflow/RECOVERY.md").read_text(encoding="utf-8")
    except OSError:
        reason += "; recovery module unreadable"
    return result(reads, "recovery", "recovery_boundary", reason,
                  owner_module="workflow/RECOVERY.md")


def project_git_blob_reader(project_root: Path, project_repository: str):
    """Return an exact blob reader for immutable subjects in the selected project Git repository."""
    def read_blob(repository: str, commit: str, path: str) -> str | None:
        if repository != project_repository:
            return None
        try:
            resolved = subprocess.run(
                ["git", "-C", str(project_root), "rev-parse", "--verify", f"{commit}:{path}"],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            if resolved.returncode != 0:
                return None
            sha = resolved.stdout.strip()
            if len(sha) != 40 or any(char not in "0123456789abcdef" for char in sha):
                return None
            kind = subprocess.run(
                ["git", "-C", str(project_root), "cat-file", "-t", sha],
                capture_output=True,
                text=True,
                check=False,
                timeout=5,
            )
            if kind.returncode != 0 or kind.stdout.strip() != "blob":
                return None
            return sha
        except (OSError, subprocess.SubprocessError):
            return None

    return read_blob


def read_exact_editorial_classification(
    reads: Reads,
    project_repository: str,
    ref: dict[str, object],
) -> dict[str, object]:
    """Read the one RF008 proof record by exact Git identity.

    Identity proof reuses the shared RF007 exact-locator resolver; the
    RF008 serving boundary keeps its accepted messages and readback shape.
    """
    repository = ref.get("repository")
    commit = ref.get("commit")
    path = ref.get("path")
    expected_blob = ref.get("blob")
    if repository != project_repository:
        raise ValidationError("editorial classification repository does not match selected project")
    if not isinstance(commit, str) or not isinstance(path, str) or not isinstance(expected_blob, str):
        raise ValidationError("editorial classification locator is incomplete")
    try:
        normalize_locator_path(path, "editorial classification")
    except ExactLocatorError as exc:
        raise ValidationError("editorial classification path is unsafe") from exc
    try:
        verify_exact_git_locator(
            project_root=reads.project_root,
            repository=repository,
            expected_repository=project_repository,
            commit=commit,
            path=path,
            blob=expected_blob,
            label="editorial classification",
        )
    except ExactLocatorError as exc:
        if exc.kind == "dangling":
            raise ValidationError("editorial classification exact Git subject does not resolve") from exc
        if exc.kind == "blob_mismatch":
            raise ValidationError("editorial classification blob does not match exact locator") from exc
        if exc.kind == "not_blob":
            raise ValidationError("editorial classification locator does not resolve to a Git blob") from exc
        if exc.kind == "git_unavailable":
            raise ValidationError(f"editorial classification Git readback failed: {exc}") from exc
        raise ValidationError(f"editorial classification locator is invalid: {exc}") from exc
    try:
        payload = subprocess.run(
            ["git", "-C", str(reads.project_root), "cat-file", "-p", expected_blob],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if payload.returncode != 0:
            raise ValidationError("editorial classification blob content is unreadable")
    except (OSError, subprocess.SubprocessError) as exc:
        raise ValidationError(f"editorial classification Git readback failed: {exc}") from exc
    reads.items.append(
        f"project-git:{repository}@{commit}:{path}@{expected_blob}"
    )
    try:
        parsed = tomllib.loads(payload.stdout)
    except (tomllib.TOMLDecodeError, ValueError) as exc:
        raise ValidationError(f"editorial classification TOML is malformed: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValidationError("editorial classification top-level TOML must be a table")
    return parsed


def policy_result(
    reads: Reads,
    decision: MechanicalDecision,
    reason: str,
    *,
    subject: str | None = None,
) -> RouteResult:
    if decision.disposition == "recovery":
        try:
            reads.package(decision.owner_module).read_text(encoding="utf-8")
        except OSError:
            reason += "; recovery module unreadable"
    return result(
        reads,
        decision.disposition,
        decision.obligation,
        reason,
        subject=subject,
        owner_module=decision.owner_module,
    )


def classify_jit_refinement(change_class: str) -> tuple[str, str]:
    routes = {
        "bounded_execution_detail": (
            "execution_prep",
            "Bounded L1/L2 refinement stays inside accepted execution authority",
        ),
        "strategy": (
            "planning",
            "Milestone strategy/order/outcome change belongs to Strategic Planning",
        ),
        "product_or_global_intent": (
            "definition",
            "Accepted product/global intent change belongs to Project Definition",
        ),
        "missing_facts": (
            "research",
            "Missing factual evidence must be resolved by Research before preparation continues",
        ),
        "required_seam_challenge": (
            "planning",
            "Evidence that a required seam is wrong returns to Strategic Planning "
            "for accepted revision; Execution Prep cannot silently override it",
        ),
        "preferred_seam_deviation": (
            "execution_prep",
            "Preferred-seam merge/split deviation stays in Execution Prep only with "
            "qualifying durable technical rationale",
        ),
        "topology_challenge": (
            "execution_prep",
            "Materially risky Card topology requires a fresh independent "
            "topology challenge before first launch; Execution Prep owns the "
            "challenge and any bounded re-decomposition",
        ),
        "late_oversize_return": (
            "execution_prep",
            "Material execution/review evidence that the active Card is "
            "oversized returns only the residual unaccepted scope to "
            "Execution Prep for bounded re-decomposition; independently valid "
            "evidence is preserved and the Worker never self-splits",
        ),
    }
    if change_class not in routes:
        raise ValidationError(f"unknown JIT refinement class {change_class!r}")
    return routes[change_class]


def accepted_planning_seams(reads: Reads, workstream: dict) -> list[dict] | None:
    """Return accepted Planning seam declarations for Task Board fidelity validation.

    Returns None when the workstream binds no Planning record or the accepted
    record declares no seams (legacy plans stay valid). Otherwise the Task
    Board must carry exactly one durable JIT decision per declared seam.
    """
    if "planning" not in workstream:
        return None
    planning = read_toml(reads.project(workstream["planning"]["path"]))
    validate_planning(planning, workstream["workstream_id"])
    return planning.get("seams")


def read_verified_card_result(
    reads: Reads,
    project_repository: str,
    card: dict,
) -> str:
    """Read the active Card result only after proving its exact locator.

    A declared ``(commit, blob)`` identity must resolve in Git and the
    current worktree bytes must still match that blob (H010/H020); legacy
    locators without declared identity keep worktree existence/readback.
    Returns the verified text so callers never re-read past the proof.
    """
    ref = card["result"]
    locator_path = ref["path"]
    if "commit" in ref or "blob" in ref:
        try:
            verified = verify_exact_git_locator(
                project_root=reads.project_root,
                repository=project_repository,
                expected_repository=project_repository,
                commit=ref.get("commit"),
                path=locator_path,
                blob=ref.get("blob"),
                label="card result",
            )
            content = verify_worktree_freshness(
                project_root=reads.project_root,
                path=locator_path,
                blob=ref.get("blob"),
                label="card result",
            )
        except ExactLocatorError as exc:
            raise ValidationError(str(exc)) from exc
        reads.items.append(f"project-git:{verified.key}")
        reads.project(locator_path)
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ValidationError(
                f"card result {locator_path!r} is not UTF-8 text: {exc}"
            ) from exc
    try:
        return reads.project(locator_path).read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValidationError(
            f"card result {locator_path!r} is not UTF-8 text: {exc}"
        ) from exc


def refresh_ready_card(
    reads: Reads,
    board: dict,
    workstream: dict,
    card: dict,
    *,
    project_repository: str,
) -> dict:
    contract_path = card["contract"]["path"]
    text = reads.project(contract_path).read_text(encoding="utf-8")
    contract = parse_task_card(text, card["id"], workstream["workstream_id"])

    for audit in board.get("topology_audits", []) or []:
        if audit.get("card_id") == card["id"] and audit.get("risk") == "risky":
            challenge = audit.get("challenge") or {}
            expected = challenge.get("card_contract_digest", "")
            actual = compute_card_contract_digest(
                reads.project(contract_path).read_bytes()
            )
            if actual != expected:
                raise ValidationError(
                    f"READY Card {card['id']} topology challenge subject does not "
                    "match the exact current Card contract; the challenge is stale "
                    "and must be renewed before launch"
                )
            break

    for authority_path in contract["authority_refs"]:
        reads.project(authority_path).read_text(encoding="utf-8")

    done_results = {
        (
            item["result"]["path"],
            item["result"].get("commit"),
            item["result"].get("blob"),
        )
        for item in board["cards"]
        if item["status"] == "done" and "result" in item
    }
    for dependency in contract["dependencies"]:
        exact_dependency = (
            dependency["path"],
            dependency["commit"],
            dependency["blob"],
        )
        if exact_dependency not in done_results:
            raise ValidationError(
                f"ready Card dependency {dependency['path']!r} no longer matches the exact current DONE predecessor result"
            )
        try:
            verified = verify_exact_git_locator(
                project_root=reads.project_root,
                repository=project_repository,
                expected_repository=project_repository,
                commit=dependency["commit"],
                path=dependency["path"],
                blob=dependency["blob"],
                label="ready Card dependency",
            )
            verify_worktree_freshness(
                project_root=reads.project_root,
                path=dependency["path"],
                blob=dependency["blob"],
                label="ready Card dependency",
            )
        except ExactLocatorError as exc:
            raise ValidationError(str(exc)) from exc
        reads.items.append(f"project-git:{verified.key}")
        reads.project(dependency["path"]).read_text(encoding="utf-8")

    technical_contract = contract["technical_contract"]
    if technical_contract is not None:
        reads.project(technical_contract).read_text(encoding="utf-8")

    return contract


def select_route(project_root: Path, selected_workstreams: list[str], *,
                 package_root: Path | None = None, entry: str = "continue") -> RouteResult:
    reads = Reads(project_root, package_root or Path(__file__).resolve().parents[1])
    try:
        reads.package("workflow/ROUTER.md").read_text(encoding="utf-8")
        project = read_project(reads.project("PROJECT.md"))
        validate_project(project)
    except (OSError, ValidationError) as exc:
        return recovery(reads, f"bootstrap project identity invalid: {exc}")

    intake_entries = {
        "new_managed_intent": "change",
        "new_issue": "issue",
        "new_feature": "feature",
    }
    if entry in intake_entries:
        return result(
            reads, "route", "intake",
            "Common Intake owns new managed intent before implementation authority exists",
            subject=intake_entries[entry], owner_module="workflow/INTAKE.md",
        )
    if entry != "continue":
        return recovery(reads, f"unknown entry kind {entry!r}")
    if len(selected_workstreams) != 1:
        return recovery(reads, f"expected exactly one selected workstream, got {len(selected_workstreams)}")

    try:
        manifest_rel = selected_workstreams[0]
        workstream = read_toml(reads.project(manifest_rel))
        validate_workstream(workstream)
        expected_manifest = f"implementation/workstreams/{workstream['workstream_id']}/WORKSTREAM.toml"
        if manifest_rel != expected_manifest:
            raise ValidationError(f"selected manifest must be exact path {expected_manifest!r}")
        kernel = PolicyKernel.from_path(reads.package("policy/mechanical_policy.json"))
        kernel.verify_projection(reads.package("workflow/POLICY_KERNEL.md"))
        research = None
        if "research" in workstream:
            research = read_toml(reads.project(workstream["research"]["path"]))
            validate_research(research, workstream["workstream_id"])
            if research["state"] == "active":
                return result(
                    reads, "route", "research",
                    "Active Research owns the next factual obligation",
                    subject=research["origin_subject"], owner_module="workflow/RESEARCH.md",
                )
            if research["state"] == "complete":
                owner_modules = {
                    "intake": "workflow/INTAKE.md",
                    "brainstorming": "workflow/BRAINSTORMING.md",
                    "definition": "workflow/DEFINITION.md",
                }

                def _read_origin_owner(role: str) -> dict | None:
                    owned = {
                        "intake": ("intake", validate_intake),
                        "brainstorming": ("brainstorm", validate_brainstorm),
                        "definition": ("definition", validate_definition),
                    }
                    key, validator = owned[role]
                    if key not in workstream:
                        return None
                    owner = read_toml(reads.project(workstream[key]["path"]))
                    validator(owner, workstream["workstream_id"])
                    return owner

                try:
                    verified_target = verify_complete_workstream_return(
                        research=research,
                        workstream=workstream,
                        read_owner=_read_origin_owner,
                    )
                except ResearchProvenanceError as exc:
                    raise ValidationError(f"{exc}") from exc
                reason = (
                    "Completed Research must be reconciled by its exact return owner"
                    if research["return_reconciliation"] == "pending"
                    else "Research result is already applied; return owner may only consume/clear it"
                )
                return result(
                    reads, "route", verified_target, reason,
                    subject=research["origin_subject"],
                    owner_module=owner_modules[verified_target],
                )

        intake = None
        if "intake" in workstream:
            intake = read_toml(reads.project(workstream["intake"]["path"]))
            validate_intake(intake, workstream["workstream_id"])
            if intake["kind"] == "issue" and intake["repair_subject"]:
                stable_diagnosis_prior_art = (
                    intake["diagnosis_prior_art_subject"] == intake["repair_subject"]
                    and bool(intake["diagnosis_prior_art_result"].strip())
                )
                if stable_diagnosis_prior_art:
                    try:
                        consumed_prior_art, proof_read = verify_consumed_prior_art_proof(
                            project_root=reads.project_root,
                            project_repository=project["repository"],
                            workstream_id=workstream["workstream_id"],
                            intake=intake,
                        )
                    except ResearchProvenanceError as exc:
                        raise ValidationError(f"{exc}") from exc
                    validate_research(consumed_prior_art, workstream["workstream_id"])
                    reads.items.append(proof_read)
                if not stable_diagnosis_prior_art:
                    exact_diagnosis_research = (
                        research is not None
                        and research["state"] == "consumed"
                        and research["origin_role"] == "intake"
                        and research["origin_subject"] == intake["repair_subject"]
                        and research["return_target"] == "intake"
                        and research["return_reconciliation"] == "applied"
                        and bool(research["return_result"].strip())
                    )
                    if exact_diagnosis_research:
                        return result(
                            reads, "route", "intake",
                            "Exact diagnosis prior-art Research is consumed; Intake must persist its exact "
                            "subject/result binding before repair alignment proceeds or the Research slot is reused",
                            subject=intake["repair_subject"], owner_module="workflow/INTAKE.md",
                        )
                    return result(
                        reads, "route", "intake",
                        "Concrete issue diagnosis must materialize and consume proportional prior-art Research "
                        "for the exact current repair subject before repair alignment can proceed",
                        subject=intake["repair_subject"], owner_module="workflow/INTAKE.md",
                    )
            if intake["state"] == "active":
                if intake["kind"] == "issue" and intake["alignment_state"] == "pending":
                    response = intake["response_kind"]
                    if response == "none":
                        return result(
                            reads, "stop", "issue_alignment",
                            "Issue diagnosis has a proposed repair but no subsequent user alignment response yet",
                            subject=intake["repair_subject"], owner_module="workflow/INTAKE.md",
                        )
                    if response in {"question", "concern", "alternative"}:
                        return result(
                            reads, "route", "brainstorming",
                            "User response continues repair alignment without authorizing implementation",
                            subject=intake["repair_subject"], owner_module="workflow/BRAINSTORMING.md",
                        )
                    return result(
                        reads, "route", "intake",
                        "Explicit authorization response exists and Intake must reconcile the exact aligned subject",
                        subject=intake["repair_subject"], owner_module="workflow/INTAKE.md",
                    )
                return result(
                    reads, "route", "intake",
                    "Selected workstream has active Intake/discovery state",
                    subject=intake["kind"], owner_module="workflow/INTAKE.md",
                )

        tracker = None
        if "tracker" in workstream:
            tracker = read_toml(reads.project(workstream["tracker"]["path"]))
            validate_tracker(tracker, workstream["workstream_id"])
            if (decision := kernel.route("PWV21-K001", {"tracker": tracker})) is not None:
                return policy_result(
                    reads,
                    decision,
                    "GitHub Issue tracker recovery is ambiguous; creating another tracker is forbidden",
                )
            if tracker["state"] == "discovery":
                return result(
                    reads, "route", "github_issues",
                    "Tracker discovery/dedup must complete before any create",
                    subject=tracker["dedup_key"], owner_module="workflow/GITHUB_ISSUES.md",
                )
            if tracker["state"] == "create_pending_readback":
                return result(
                    reads, "route", "github_issues",
                    "Interrupted/uncertain Issue create requires exact readback before any retry",
                    subject=tracker["dedup_key"], owner_module="workflow/GITHUB_ISSUES.md",
                )

        brainstorm = None
        if "brainstorm" in workstream:
            brainstorm = read_toml(reads.project(workstream["brainstorm"]["path"]))
            validate_brainstorm(brainstorm, workstream["workstream_id"])

        definition = None
        if "definition" in workstream:
            definition = read_toml(reads.project(workstream["definition"]["path"]))
            validate_definition(definition, workstream["workstream_id"])
            if brainstorm is None:
                raise ValidationError("Definition locator requires durable Brainstorming promotion state")
            expected_scope = f"{brainstorm['scope_id']}@{brainstorm['revision']}"
            if (
                brainstorm["state"] != "promoted"
                or brainstorm["promotion_state"] != "authorized"
                or brainstorm["promotion_subject"] != expected_scope
                or definition["source_scope_subject"] != expected_scope
            ):
                raise ValidationError("Definition source does not match exact promoted Brainstorming revision")

        # RF002 stop precedence is pre-execution only: Board-coupled Definition
        # routes keep parent behavior, while brainstorm-only stop is unchanged.
        if brainstorm is not None and ("task_board" not in workstream or definition is None):
            exact_scope = f"{brainstorm['scope_id']}@{brainstorm['revision']}"
            if (decision := kernel.route("PWV21-K009", {"brainstorm": brainstorm})) is not None:
                return policy_result(
                    reads,
                    decision,
                    "Brainstorming carries an explicit user stop",
                    subject=exact_scope,
                )

        plan_gate_passed_with_board = False
        if definition is not None:
            if definition["state"] == "active":
                return result(
                    reads, "route", "definition",
                    "Promoted scope has active Definition work",
                    subject=definition["source_scope_subject"], owner_module="workflow/DEFINITION.md",
                )
            if (decision := kernel.route("PWV21-K002", {"definition": definition})) is not None:
                return policy_result(
                    reads,
                    decision,
                    "Definition is GREEN; premium stop A is due before material Strategic Planning; "
                    "recommend the best available model/context for Strategic Planning without making model identity canonical",
                    subject=definition["revision"],
                )

            planning = None
            if "planning" in workstream:
                planning = read_toml(reads.project(workstream["planning"]["path"]))
                validate_planning(planning, workstream["workstream_id"])

            if planning is None:
                return result(
                    reads, "route", "planning",
                    "Premium stop A is satisfied; Strategic Planning owns the next obligation",
                    subject=definition["revision"], owner_module="workflow/PLANNING.md",
                )

            if (decision := kernel.route("PWV21-K003", {"planning": planning})) is not None:
                return policy_result(
                    reads,
                    decision,
                    "Material planning re-entry has a new exact cycle; premium stop A is due before Planning resumes; "
                    "recommend the best available model/context for Strategic Planning without making model identity canonical",
                    subject=planning["entry_subject"],
                )

            if (decision := kernel.route("PWV21-K004", {"planning": planning})) is not None:
                return policy_result(
                    reads,
                    decision,
                    "Current planning cycle has exact premium A satisfaction and is still being authored",
                    subject=planning["entry_subject"],
                )

            plan_review = None
            if "plan_review" in workstream:
                plan_review = read_toml(reads.project(workstream["plan_review"]["path"]))
                validate_plan_review(plan_review, workstream["workstream_id"], planning)

            try:
                authority_reads = verify_planning_authority_freshness(
                    project_root=reads.project_root,
                    project_repository=project["repository"],
                    workstream_id=workstream["workstream_id"],
                    definition=definition,
                    planning=planning,
                    plan_review=plan_review,
                )
            except DefinitionAuthorityError as exc:
                raise ValidationError(f"planning authority freshness failed: {exc}") from exc
            reads.items.extend(authority_reads)

            subject_key = (
                f"{planning['subject']['repository']}@{planning['subject']['commit']}:"
                f"{planning['subject']['path']}@{planning['subject']['blob']}"
            )
            if planning["state"] == "frozen":
                if (decision := kernel.route("PWV21-K005", {"planning": planning})) is not None:
                    return policy_result(
                        reads,
                        decision,
                        "Exact plan subject is frozen; premium stop B requires a fresh independent best-available review context",
                        subject=subject_key,
                    )
                if plan_review is None:
                    raise ValidationError("premium B satisfied without exact Plan Review attempt")
                if (decision := kernel.route("PWV21-K006", {"plan_review": plan_review})) is not None:
                    return policy_result(
                        reads,
                        decision,
                        "Fresh independent Plan Review owns the frozen exact subject",
                        subject=subject_key,
                    )
                if (decision := kernel.route("PWV21-K007", {"plan_review": plan_review})) is not None:
                    return policy_result(
                        reads,
                        decision,
                        "GREEN Plan Review must be consumed into approved plan state",
                        subject=subject_key,
                    )
                if plan_review["verdict"] == "red":
                    return result(
                        reads, "route", "planning",
                        "RED Plan Review returns to Planning for correction classification",
                        subject=subject_key, owner_module="workflow/PLANNING.md",
                    )
                raise ValidationError(
                    f"unsupported Plan Review verdict {plan_review['verdict']!r}; "
                    "frozen plan routes only pending, green or red"
                )

            if planning["review_mode"] == "editorial_exempt":
                if plan_review is None or plan_review["verdict"] != "green":
                    raise ValidationError("editorial exemption requires prior exact GREEN Plan Review")
                classification_ref = planning["review_exemption_classification"]
                classification = read_exact_editorial_classification(
                    reads,
                    project["repository"],
                    classification_ref,
                )
                try:
                    validate_editorial_exemption_classification(
                        classification,
                        workstream_id=workstream["workstream_id"],
                        planning=planning,
                    )
                except EditorialExemptionError as exc:
                    raise ValidationError(f"{exc}") from exc
                if "task_board" not in workstream:
                    return result(
                        reads, "route", "execution_prep",
                        "Exact independent GREEN editorial-only classification preserves prior GREEN review and satisfied C; no new Stage-6 review is due",
                        subject=subject_key, owner_module="workflow/EXECUTION_PREP.md",
                    )
                plan_gate_passed_with_board = True
            else:
                if plan_review is None or plan_review["verdict"] != "green":
                    raise ValidationError("approved plan requires exact GREEN Plan Review")
                if (decision := kernel.route("PWV21-K008", {"planning": planning})) is not None:
                    return policy_result(
                        reads,
                        decision,
                        "GREEN Plan Review is approved; premium stop C is due before Execution Prep; "
                        "recommend switching to a lighter/cheaper model/context for Execution Prep",
                        subject=subject_key,
                    )
                if "task_board" not in workstream:
                    return result(
                        reads, "route", "execution_prep",
                        "Premium stop C is satisfied; common Execution Prep owns Card materialization",
                        subject=subject_key, owner_module="workflow/EXECUTION_PREP.md",
                    )
                plan_gate_passed_with_board = True

        if not plan_gate_passed_with_board and brainstorm is not None:
            exact_scope = f"{brainstorm['scope_id']}@{brainstorm['revision']}"
            if (decision := kernel.route("PWV21-K010", {"brainstorm": brainstorm})) is not None:
                return policy_result(
                    reads,
                    decision,
                    "Active exploratory scope owns the next product/strategy clarification",
                    subject=exact_scope,
                )
            if brainstorm["promotion_state"] == "pending":
                return result(
                    reads, "stop", "definition_promotion",
                    "Brainstorming is ready but exact current revision is not authorized for Definition",
                    subject=exact_scope, owner_module="workflow/BRAINSTORMING.md",
                )
            if brainstorm["state"] != "promoted":
                raise ValidationError(
                    "Brainstorming carries exact promotion authorization but is not promoted; "
                    "Definition entry requires promoted state"
                )
            return result(
                reads, "route", "definition",
                "Exact current exploratory revision is promoted and authorized for Definition",
                subject=exact_scope, owner_module="workflow/DEFINITION.md",
            )

        if not plan_gate_passed_with_board and "task_board" not in workstream:
            if intake is None:
                raise ValidationError("selected workstream has no routable pre-execution state or Task Board")
            if intake["kind"] == "issue" and intake["micro_fix_candidate"]:
                return result(
                    reads, "route", "execution_prep",
                    "Aligned issue is a bounded micro-fix candidate; common Execution Prep owns preparation",
                    subject=intake["repair_subject"], owner_module="workflow/EXECUTION_PREP.md",
                )
            return result(
                reads, "route", "brainstorming",
                "Completed pre-execution Intake continues to common Brainstorming",
                subject=intake["kind"], owner_module="workflow/BRAINSTORMING.md",
            )

        board = read_toml(reads.project(workstream["task_board"]["path"]))
        validate_board(
            board, workstream, planning_seams=accepted_planning_seams(reads, workstream)
        )

        if board.get("research_obligation") is not None:
            research_ref = board["research_obligation"]
            board_research = read_toml(reads.project(research_ref["path"]))
            validate_research(board_research, workstream["workstream_id"])
            if board_research["origin_role"] not in {"execution_prep", "execution", "execution_resolution"}:
                raise ValidationError("Task Board Research pointer must own implementation/recovery Research")
            if board_research["state"] == "active":
                return result(
                    reads, "route", "research",
                    "Implementation/recovery Research owns the next factual obligation",
                    subject=board_research["origin_subject"], owner_module="workflow/RESEARCH.md",
                )
            if board_research["state"] == "complete":
                try:
                    obligation = verify_complete_board_return(
                        research=board_research, board=board
                    )
                except ResearchProvenanceError as exc:
                    raise ValidationError(f"{exc}") from exc
                return result(
                    reads, "route", obligation,
                    "Completed implementation Research returns once to its exact durable owner before pointer cleanup",
                    subject=board_research["origin_subject"],
                    owner_module="workflow/RECOVERY.md" if obligation == "execution_resolution" else (
                        "workflow/EXECUTION_PREP.md" if obligation == "execution_prep" else "workflow/EXECUTION.md"
                    ),
                )
            return result(
                reads, "route", "research_cleanup",
                "Task Board still points to consumed Research; clear only the stale pointer without replay",
                subject=board_research["origin_subject"], owner_module="workflow/RECOVERY.md",
            )
    except (OSError, ValidationError, KeyError) as exc:
        return recovery(reads, f"selected workstream identity invalid: {exc}")

    if board.get("live_findings"):
        def _live_record_reader(raw: str) -> str | None:
            try:
                return reads.project(raw).read_text(encoding="utf-8")
            except (OSError, ValidationError):
                return None

        try:
            verify_live_finding_records(board, record_reader=_live_record_reader)
        except LiveFindingError as exc:
            return recovery(reads, f"live-finding intake verification failed: {exc}")

        try:
            verify_finding_trigger_records(board, record_reader=_live_record_reader)
        except LiveFindingError as exc:
            return recovery(reads, f"affected-JIT reconciliation verification failed: {exc}")

    if board.get("jit_triggers"):
        def _consumer_record_reader(raw: str) -> str | None:
            try:
                return reads.project(raw).read_text(encoding="utf-8")
            except (OSError, ValidationError):
                return None

        try:
            verify_live_consumer_records(
                board,
                record_reader=_consumer_record_reader,
                git_reader=project_git_blob_reader(
                    reads.project_root, project["repository"]
                ),
            )
        except LiveConsumerError as exc:
            return recovery(reads, f"live-consumer admission verification failed: {exc}")

    late = pending_late_return(board)
    handoff = bound_handoff_hold(board) if late is None else None
    held = late if late is not None else handoff
    if held is not None:
        try:
            record = next(
                item for item in board.get("late_oversize_returns", [])
                if isinstance(item, dict) and item.get("card_id") == held
            )
        except StopIteration as exc:
            return recovery(reads, f"late-oversize return record unreadable: {exc}")
        try:
            for ref in record.get("preserved_refs", []):
                reads.project(ref).read_text(encoding="utf-8")
        except (OSError, ValidationError) as exc:
            return recovery(reads, f"late-oversize preserved evidence unreadable: {exc}")
        if record.get("origin") == "review":
            try:
                attempt_data = read_toml(reads.project(record.get("origin_attempt_path", "")))
            except (OSError, ValueError) as exc:
                return recovery(reads, f"late-oversize review attempt readback failed: {exc}")
            if attempt_data.get("attempt") != record.get("origin_attempt"):
                return recovery(
                    reads,
                    f"late-oversize review attempt binding mismatch for Card {held}: "
                    f"locator {record.get('origin_attempt_path')!r} does not carry "
                    f"attempt {record.get('origin_attempt')!r}",
                )
        if late is not None:
            reason = (
                f"Card {held} has a pending late-oversize return; independently "
                "valid evidence is preserved and only the residual unaccepted "
                "scope returns to Execution Prep, which must materialize the "
                "residual Card and bind the return before the original "
                "transitions to returned"
            )
        else:
            reason = (
                f"Card {held} has a bound late-oversize return; Execution Prep owns "
                "handoff finalization — transition the original to returned, "
                "its non-GREEN terminal disposition, so the bound residual "
                "Card can proceed"
            )
        return result(
            reads, "route", "execution_prep", reason,
            subject=held, owner_module="workflow/EXECUTION_PREP.md",
        )

    active = [card for card in board["cards"] if card["status"] == "in_progress"]
    ready = [card for card in board["cards"] if card["status"] == "ready"]

    if active:
        card = active[0]
        try:
            card_text = reads.project(card["contract"]["path"]).read_text(encoding="utf-8")
            contract = parse_task_card(
                card_text,
                card["id"],
                workstream["workstream_id"],
            )
            if "result" in card:
                result_text = read_verified_card_result(
                    reads, project["repository"], card
                )
                parsed_result = parse_card_result(
                    result_text, card["id"], workstream["workstream_id"]
                )
                if not is_accepted_success(parsed_result):
                    raise ValidationError(
                        "card result is not accepted success; only structured "
                        "Result status success can authorize reconciliation, "
                        "review, or no-replay recovery"
                    )
                for evidence_ref in parsed_result["evidence_refs"]:
                    try:
                        reads.project(evidence_ref).read_text(encoding="utf-8")
                    except (OSError, ValidationError) as exc:
                        raise ValidationError(
                            f"card result evidence {evidence_ref!r} cannot be read back: {exc}"
                        ) from exc
                requirement = contract["review_requirement"]
                attempt_refs = card.get("review_attempts", [])
                if requirement == "none":
                    # Review-free Cards never rely on attempt history; still
                    # reject malformed locators so Boards stay shape-clean.
                    attempts: list[dict] = []
                    for attempt_ref in attempt_refs:
                        attempt = read_toml(reads.project(attempt_ref["path"]))
                        attempts.append(attempt)
                else:
                    attempts = []
                    for index, attempt_ref in enumerate(attempt_refs):
                        label = f"review_attempts[{index}]"
                        try:
                            attempt, _, locator_read = verify_review_attempt_locator(
                                project_root=reads.project_root,
                                project_repository=project["repository"],
                                workstream_id=workstream["workstream_id"],
                                card_id=card["id"],
                                ref=attempt_ref,
                                label=label,
                            )
                        except ReviewAttemptProvenanceError as exc:
                            raise ValidationError(
                                f"review attempt identity failed: {exc}"
                            ) from exc
                        reads.items.append(locator_read)
                        reads.project(attempt_ref["path"])
                        if "review_kind" not in attempt and attempt.get("verdict") in {
                            "green",
                            "red",
                        }:
                            try:
                                provenance_read = verify_legacy_migration(
                                    project_root=reads.project_root,
                                    project_repository=project["repository"],
                                    workstream_id=workstream["workstream_id"],
                                    card_id=card["id"],
                                    attempt=attempt,
                                )
                            except ReviewAttemptProvenanceError as exc:
                                raise ValidationError(
                                    f"legacy review attempt provenance failed: {exc}"
                                ) from exc
                            reads.items.append(provenance_read)
                        attempts.append(attempt)

                if requirement == "none":
                    return result(
                        reads, "route", "result_reconciliation",
                        "An accepted-success semantic result is already durable and this Card requires no independent review; do not replay implementation",
                        subject=card["id"], owner_module="workflow/EXECUTION.md",
                    )
                if not attempts:
                    return result(
                        reads, "route", "review_freeze",
                        "Accepted semantic result requires an exact independent review attempt before terminal completion",
                        subject=card["id"], owner_module="workflow/REVIEW.md",
                    )

                validate_review_history(
                    attempts,
                    expected_card_id=card["id"],
                    workstream_id=workstream["workstream_id"],
                    accepted_authority_paths=set(contract["authority_refs"]),
                    exact_blob_reader=project_git_blob_reader(
                        reads.project_root,
                        project["repository"],
                    ),
                    expected_review_scope="card",
                )
                # Terminal bytes freeze against actual Git history: a same-ID
                # rewrite with a rebound Board locator still routes unless the
                # prior durable state is re-derived here. Runs after history
                # validation so established failure reasons keep precedence.
                try:
                    history_reads = verify_terminal_append_only_from_git(
                        project_root=reads.project_root,
                        workstream_id=workstream["workstream_id"],
                        card_id=card["id"],
                        attempts=attempts,
                    )
                except ReviewAttemptProvenanceError as exc:
                    raise ValidationError(
                        f"review history is not append-only: {exc}"
                    ) from exc
                reads.items.extend(history_reads)
                current_subject = exact_result_subject(project["repository"], card["result"])
                verdict = attempts[-1]["verdict"]
                covered_subject = review_subject(attempts[-1])
                if covered_subject != current_subject:
                    if verdict in {"pending", "in_progress"}:
                        raise ValidationError("active review attempt is stale for the current durable result")
                    return result(
                        reads, "route", "review_freeze",
                        "Current durable result changed after terminal review history; preserve history and freeze a new exact attempt",
                        subject=card["id"], owner_module="workflow/REVIEW.md",
                    )
                if verdict in {"pending", "in_progress"}:
                    return result(
                        reads, "route", "review",
                        "Exact REQUIRED/RECOMMENDED review attempt blocks terminal Card completion until GREEN",
                        subject=card["id"], owner_module="workflow/REVIEW.md",
                    )
                if verdict == "green":
                    if can_finalize_review_obligation(attempts[-1]):
                        return result(
                            reads, "route", "post_review_finalization",
                            "Exact current fresh discovery review is GREEN; Card finalization is deterministic and is not a verdict-only stop",
                            subject=card["id"], owner_module="workflow/EXECUTION.md",
                        )
                    if review_kind(attempts[-1]) == "closure_verification":
                        source_id = attempts[-1]["source_discovery_attempt"]
                        remaining = remaining_closure_findings(attempts, source_id)
                        if remaining:
                            return result(
                                reads, "route", "review_freeze",
                                "Some known findings remain unverified; freeze another closure-verification attempt before fresh discovery",
                                subject=card["id"], owner_module="workflow/REVIEW.md",
                            )
                        convergence = review_convergence_state(
                            attempts, expected_review_scope="card"
                        )
                        if (
                            convergence.convergence_required
                            and convergence.post_convergence_attempt is None
                        ):
                            return result(
                                reads, "route", "review_freeze",
                                "Known findings are closed after a convergence threshold; freeze the single fresh post-convergence full-scope validation",
                                subject=card["id"], owner_module="workflow/REVIEW.md",
                            )
                        return result(
                            reads, "route", "review_freeze",
                            "All known findings are closure-verified, but closure cannot satisfy the review obligation; freeze a fresh full-scope discovery attempt",
                            subject=card["id"], owner_module="workflow/REVIEW.md",
                        )

                convergence = review_convergence_state(
                    attempts, expected_review_scope="card"
                )
                if attempts[-1].get("post_convergence_validation") is True:
                    return result(
                        reads, "route", "review_structural_resolution",
                        "Fresh post-convergence validation is RED; broader structural classification is required instead of another ordinary review loop",
                        subject=card["id"], owner_module="workflow/RECOVERY.md",
                    )
                if convergence.convergence_required:
                    return result(
                        reads, "route", "review_convergence",
                        "Review discovery or per-class repair/closure ceiling is reached; Main convergence/root-cause analysis owns the next correction mode",
                        subject=card["id"], owner_module="workflow/RECOVERY.md",
                    )
                return result(
                    reads, "route", "execution_resolution",
                    "RED review evidence remains durable; execution resolution classifies bounded correction, Planning, Definition, Research or a real stop",
                    subject=card["id"], owner_module="workflow/RECOVERY.md",
                )
        except (OSError, ValidationError, ExecutionContractError, KeyError) as exc:
            return recovery(reads, f"current Card execution state invalid: {exc}")
        return result(
            reads, "route", "execution",
            "Current Card owns runtime-neutral implementation; delegated/direct realization stays outside canonical state",
            subject=card["id"], owner_module="workflow/EXECUTION.md",
        )

    blocked = [card for card in board["cards"] if card["status"] == "blocked"]
    if blocked:
        card = blocked[0]
        try:
            blocker_ref = card["blocker"]
            blocker = read_toml(reads.project(blocker_ref["path"]))
            validate_blocker(blocker, workstream["workstream_id"], card["id"])
            route, is_stop = classify_resolution(blocker["class"])
        except (OSError, ValidationError, RecoveryContractError, KeyError) as exc:
            return recovery(reads, f"blocked Card recovery invalid: {exc}")
        if route == "research":
            return result(
                reads, "route", "research_handoff",
                "Blocked Card is missing factual evidence; materialize exact Task-Board-owned Research before continuing",
                subject=card["id"], owner_module="workflow/RECOVERY.md",
            )
        return result(
            reads, "stop" if is_stop else "route", route,
            "Blocked Card classification reached an exact durable owner",
            subject=card["id"], owner_module="workflow/RECOVERY.md",
        )

    held = ready_topology_hold(board)
    if held is not None:
        triggers = next(
            (
                ", ".join(audit.get("triggers", []))
                for audit in board.get("topology_audits", [])
                if audit.get("card_id") == held
            ),
            "",
        )
        return result(
            reads, "route", "topology_challenge",
            f"READY Card {held} has materially risky topology ({triggers}); "
            "a fresh independent topology challenge must be GREEN before first launch",
            subject=held, owner_module="workflow/EXECUTION_PREP.md",
        )

    if (decision := kernel.route("PWV21-K011", {"board": board})) is not None:
        card = ready[0]
        try:
            refresh_ready_card(
                reads, board, workstream, card,
                project_repository=project["repository"],
            )
        except (OSError, ValidationError, KeyError) as exc:
            return recovery(reads, f"ready Card launch refresh failed: {exc}")
        return policy_result(
            reads,
            decision,
            "READY Card passed launch refresh against current authority, DONE dependency results and optional technical contract",
            subject=card["id"],
        )

    if len(ready) > 1:
        return result(
            reads, "route", "execution_prep",
            "Multiple READY Cards remain semantically ready; Execution Prep must choose the next deterministic Card from accepted plan/dependency authority",
            owner_module="workflow/EXECUTION_PREP.md",
        )

    if (decision := kernel.route("PWV21-K012", {"board": board})) is not None:
        return policy_result(
            reads,
            decision,
            "All current Cards are terminal; Close owns finalization and decides whether approved scope is durably complete",
        )

    statuses = {card["status"] for card in board["cards"]}
    if statuses and statuses <= {"done", "returned"} and "returned" in statuses:
        unfinished = unfinished_residual_scope(board)
        if unfinished is not None:
            return result(
                reads, "route", "execution_prep", unfinished,
                owner_module="workflow/EXECUTION_PREP.md",
            )
        return result(
            reads, "route", "close",
            "All current Cards are terminal and every bound residual outcome "
            "lands in accepted downstream Cards; Close owns finalization and "
            "must not equate a returned Card alone with accepted completion",
            owner_module="workflow/CLOSE.md",
        )

    if board.get("live_findings") and board.get("jit_triggers"):
        try:
            validated = validate_live_findings(
                board.get("live_findings"), workstream["workstream_id"]
            )
            holds = validate_finding_trigger_gates(validated, board["jit_triggers"])
        except LiveFindingError as exc:
            return recovery(reads, f"affected-JIT gate invalid: {exc}")
        states = {
            trigger["id"]: trigger.get("state")
            for trigger in board["jit_triggers"]
            if isinstance(trigger, dict) and isinstance(trigger.get("id"), str)
        }
        held = sorted(
            trigger_id for trigger_id in holds if states.get(trigger_id) == "satisfied"
        )
        if held:
            parts = []
            for trigger_id in held:
                owners = sorted({
                    str(validated[finding_id].get("owner_stage"))
                    for finding_id in holds[trigger_id]
                })
                parts.append(
                    f"{trigger_id} (finding(s) "
                    f"{', '.join(holds[trigger_id])} @ {', '.join(owners)})"
                )
            first_finding = holds[held[0]][0]
            first_owner = str(validated[first_finding].get("owner_stage"))
            try:
                owner_module = live_finding_owner_module(first_owner)
            except LiveFindingError as exc:
                return recovery(reads, f"affected-JIT gate invalid: {exc}")
            return result(
                reads, "route", "finding_reconciliation",
                "Satisfied JIT trigger(s) "
                + "; ".join(parts)
                + " held by pending material live finding(s); owning-stage "
                "reconciliation must be accepted and read back before "
                "Execution Prep consumes the affected trigger",
                subject=held[0], owner_module=owner_module,
            )

    if board.get("jit_triggers"):
        try:
            consumer_holds = validate_live_consumer_gates(
                board["jit_triggers"], workstream["workstream_id"]
            )
        except LiveConsumerError as exc:
            return recovery(reads, f"live-consumer gate invalid: {exc}")
        states = {
            trigger["id"]: trigger.get("state")
            for trigger in board["jit_triggers"]
            if isinstance(trigger, dict) and isinstance(trigger.get("id"), str)
        }
        consumer_held = sorted(
            trigger_id
            for trigger_id in consumer_holds
            if states.get(trigger_id) == "satisfied"
        )
        if consumer_held:
            return result(
                reads, "route", "live_consumer_readiness",
                "Satisfied intentional live-consumer trigger(s) "
                + ", ".join(consumer_held)
                + " held by pending readiness; verified corrected authority "
                "and every required Definition, Planning, review, predecessor "
                "and Milestone gate must be complete and read back before "
                "Execution Prep consumes the intended consumer",
                subject=consumer_held[0],
                owner_module="workflow/EXECUTION_PREP.md",
            )

    return result(reads, "route", "execution_prep",
                  "No executable Card is selected; common Execution Prep owns bounded JIT materialization/refinement",
                  owner_module="workflow/EXECUTION_PREP.md")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("project_root", type=Path)
    parser.add_argument("--workstream", action="append", default=[])
    parser.add_argument("--entry", default="continue")
    args = parser.parse_args()
    routed = select_route(args.project_root, args.workstream, entry=args.entry)
    print(json.dumps(asdict(routed), indent=2))
    return 2 if routed.disposition == "recovery" else 0


if __name__ == "__main__":
    raise SystemExit(main())
