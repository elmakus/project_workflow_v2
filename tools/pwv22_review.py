from __future__ import annotations
from typing import Any, Mapping, Sequence
from tools.pwv22_native_foundation import NativeFoundationError
from tools.pwv22_native_results import exact_identity

VERDICTS=("GREEN","RED")
CEILINGS={"local":5,"integration":4,"final":3}
MAX_FAILED_REPAIR_CLOSURE_ROUNDS=3

def _req(ok: bool,msg: str)->None:
    if not ok: raise NativeFoundationError(msg)

def typed_attempt(record: Mapping[str,Any])->dict[str,Any]:
    _req(record.get("type")=="pwv2.2-review-attempt","wrong review attempt type")
    aid=record.get("attempt_id"); _req(isinstance(aid,str) and aid,"missing attempt id")
    subject=exact_identity(record.get("subject",{}))
    acceptance=exact_identity(record.get("acceptance_surface",{}))
    verdict=record.get("verdict")
    _req(verdict in (None,*VERDICTS),"review verdict must be GREEN or RED")
    evidence=record.get("evidence")
    if verdict is not None:
        _req(isinstance(evidence,Mapping),"terminal review requires evidence")
        evidence=exact_identity(evidence)
    _req(isinstance(record.get("material_author_or_repairer"),bool),"missing material independence fact")
    _req(not record["material_author_or_repairer"],"material author/repairer cannot independently review subject")
    return {"type":"pwv2.2-review-attempt","attempt_id":aid,"subject":subject,
            "acceptance_surface":acceptance,"verdict":verdict,"evidence":evidence,
            "material_author_or_repairer":False}

def append_attempt(history: Sequence[Mapping[str,Any]], candidate: Mapping[str,Any])->list[Mapping[str,Any]]:
    c=typed_attempt(candidate)
    ids=set()
    for raw in history:
        p=typed_attempt(raw)
        _req(p["attempt_id"] not in ids,"duplicate historical attempt")
        ids.add(p["attempt_id"])
        _req(p["attempt_id"]!=c["attempt_id"],"review attempt history is append-only")
        _req(p["verdict"] is not None,"only last attempt may be pending")
    return [*history,candidate]

def reviewer_publication(prior: Mapping[str,Any], proposed: Mapping[str,Any])->dict[str,Any]:
    p=typed_attempt(prior); n=typed_attempt(proposed)
    for key in ("type","attempt_id","subject","acceptance_surface","material_author_or_repairer"):
        _req(p[key]==n[key],"reviewer attempted unauthorized publication")
    _req(p["verdict"] is None,"terminal attempt is immutable")
    _req(n["verdict"] in VERDICTS,"reviewer must publish binary verdict")
    return n

def deterministic_finalization(attempt: Mapping[str,Any], expected_subject: Mapping[str,Any],
                               expected_acceptance: Mapping[str,Any], current_state: str)->str:
    a=typed_attempt(attempt)
    _req(a["subject"]==exact_identity(expected_subject),"stale review subject")
    _req(a["acceptance_surface"]==exact_identity(expected_acceptance),"wrong acceptance surface")
    _req(current_state=="review_pending","unexpected finalizer state")
    _req(a["verdict"] in VERDICTS,"pending review cannot finalize")
    return "done" if a["verdict"]=="GREEN" else "repair_required"

def typed_finding(record: Mapping[str,Any])->dict[str,Any]:
    fid=record.get("finding_id"); _req(isinstance(fid,str) and fid,"missing finding id")
    impact=record.get("impact")
    _req(impact in ("acceptance_falsifying","safe_deferred","unknown"),"invalid finding impact")
    affected=record.get("affected_results",[])
    _req(isinstance(affected,list) and all(isinstance(x,str) and x for x in affected),"invalid affected results")
    if impact=="safe_deferred":
        proof=record.get("safe_continuation_proof")
        boundary=record.get("latest_safe_boundary")
        _req(isinstance(proof,str) and proof,"safe deferral requires positive proof")
        _req(isinstance(boundary,str) and boundary,"safe deferral requires latest-safe boundary")
    return {"finding_id":fid,"impact":impact,"affected_results":list(affected),
            "safe_continuation_proof":record.get("safe_continuation_proof"),
            "latest_safe_boundary":record.get("latest_safe_boundary")}

def completion_allowed(findings: Sequence[Mapping[str,Any]])->bool:
    for raw in findings:
        f=typed_finding(raw)
        if f["impact"]!="safe_deferred": return False
    return True

def blocked_results(findings: Sequence[Mapping[str,Any]])->set[str]:
    blocked=set()
    for raw in findings:
        f=typed_finding(raw)
        if f["impact"] in ("acceptance_falsifying","unknown"):
            blocked.update(f["affected_results"])
    return blocked

def must_repair_before(finding: Mapping[str,Any], next_consumed_results: Sequence[str],
                       reached_boundary: str|None=None)->bool:
    f=typed_finding(finding)
    if f["impact"]!="safe_deferred": return True
    return bool(set(f["affected_results"]) & set(next_consumed_results)) or reached_boundary==f["latest_safe_boundary"]

def convergence_mode(surface: str, discovery_epochs: int, failed_repair_closure_rounds: int)->str:
    _req(surface in CEILINGS,"unknown review surface")
    _req(isinstance(discovery_epochs,int) and discovery_epochs>=0,"invalid discovery epoch count")
    _req(isinstance(failed_repair_closure_rounds,int) and failed_repair_closure_rounds>=0,"invalid repair round count")
    if failed_repair_closure_rounds>=MAX_FAILED_REPAIR_CLOSURE_ROUNDS:
        return "escalate"
    if discovery_epochs>=CEILINGS[surface]:
        return "change_mode"
    return "continue"

def fresh_closure_required(material_repair: bool, prior_reviewer_reused: bool)->bool:
    return bool(material_repair and prior_reviewer_reused)
