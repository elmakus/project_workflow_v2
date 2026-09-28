from __future__ import annotations
from typing import Any, Mapping, Sequence
from tools.pwv22_native_foundation import NativeFoundationError, admit_native
from tools.pwv22_native_routing import route_owner
from tools.pwv22_review import blocked_results, typed_finding

MECHANICAL_REPAIRS={"derived_readiness":"recompute","interrupted_finalization":"resume_guarded_finalizer","missing_projection":"rebuild_projection"}
SEMANTIC_OWNER_CHOICES={"factual","strategy","intent"}

def _req(ok: bool,msg: str)->None:
    if not ok: raise NativeFoundationError(msg)

def reconstruct_owner(state: Mapping[str,Any], official: Mapping[str,Any])->str:
    admit_native(state,official)
    pending=state.get("return_pending")
    consumed=state.get("return_consumed") is True
    if pending is not None:
        _req(isinstance(pending,Mapping),"invalid pending return")
        owner=pending.get("owner")
        _req(isinstance(owner,str) and owner,"pending return missing owner")
        _req(not consumed,"consumed return cannot remain pending")
        routed=route_owner({**state,"phase":owner},official)
        _req(routed==owner,"pending return conflicts with native routing")
        return owner
    return route_owner(state,official)

def classify_repair(record: Mapping[str,Any])->dict[str,str]:
    kind=record.get("kind")
    _req(isinstance(kind,str) and kind,"repair kind required")
    if kind in MECHANICAL_REPAIRS:
        _req(record.get("semantic_change") is not True,"semantic change is not mechanical repair")
        return {"class":"mechanical","operation":MECHANICAL_REPAIRS[kind]}
    if kind in SEMANTIC_OWNER_CHOICES:
        owner=record.get("owner")
        _req(isinstance(owner,str) and owner,"semantic repair requires owner")
        return {"class":"owner_choice","owner":owner}
    raise NativeFoundationError("unknown repair classification")

def recovery_blocked_results(findings: Sequence[Mapping[str,Any]])->set[str]:
    for finding in findings: typed_finding(finding)
    return blocked_results(findings)

def durable_result_replay_allowed(result_id: str,durable_result_ids: Sequence[str])->bool:
    _req(isinstance(result_id,str) and result_id,"result id required")
    _req(all(isinstance(x,str) and x for x in durable_result_ids),"invalid durable result ids")
    return result_id not in set(durable_result_ids)

def recovery_action(state: Mapping[str,Any],official: Mapping[str,Any],
                    issue: Mapping[str,Any],findings: Sequence[Mapping[str,Any]],
                    *,result_id: str|None=None,durable_result_ids: Sequence[str]=())->dict[str,Any]:
    owner=reconstruct_owner(state,official)
    repair=classify_repair(issue)
    blocked=sorted(recovery_blocked_results(findings))
    if result_id is not None:
        _req(durable_result_replay_allowed(result_id,durable_result_ids),"durable semantic Result must not be replayed")
    if repair["class"]=="owner_choice":
        return {"action":"return_to_owner","owner":repair["owner"],"blocked_results":blocked}
    return {"action":"mechanical_repair","owner":owner,"operation":repair["operation"],"blocked_results":blocked}
