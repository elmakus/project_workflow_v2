from __future__ import annotations
from typing import Any, Mapping, Sequence
from tools.pwv22_native_foundation import NativeFoundationError

DISPOSITIONS=("preserve","revalidate","stale","recovery")

def _req(ok: bool,msg: str)->None:
    if not ok: raise NativeFoundationError(msg)

def classify_evolution(*,current_epoch: str,candidate_epoch: str,changed_properties: Sequence[str],
                       result_properties: Sequence[str],impact_known: bool,
                       implementation_changed: bool)->str:
    _req(isinstance(current_epoch,str) and current_epoch,"current epoch required")
    _req(isinstance(candidate_epoch,str) and candidate_epoch,"candidate epoch required")
    _req(current_epoch==candidate_epoch,"mixed native epochs or semantic downgrade forbidden")
    _req(isinstance(impact_known,bool),"impact knowledge required")
    if not impact_known:return "recovery"
    changed=set(changed_properties); material=set(result_properties)
    _req(all(isinstance(x,str) and x for x in changed|material),"invalid property")
    if not changed:return "preserve"
    if changed.isdisjoint(material):return "preserve"
    return "stale" if implementation_changed else "revalidate"

def revalidation_attachment(result: Mapping[str,Any], *, disposition: str,
                            implementation_changed: bool,acceptance_evidence: Mapping[str,Any]|None=None)->dict[str,Any]:
    _req(disposition in DISPOSITIONS,"invalid evolution disposition")
    _req(isinstance(result,Mapping) and bool(result.get("result_id")),"result required")
    if disposition=="revalidate":
        _req(not implementation_changed,"changed implementation requires a new Result")
        _req(isinstance(acceptance_evidence,Mapping) and bool(acceptance_evidence),"revalidation evidence required")
        return {"result_id":result["result_id"],"result":dict(result),"acceptance_evidence":dict(acceptance_evidence)}
    if disposition=="preserve":
        _req(not implementation_changed,"changed implementation cannot preserve Result identity")
        return {"result_id":result["result_id"],"result":dict(result)}
    raise NativeFoundationError("stale/recovery disposition cannot attach unchanged acceptance")

def activation_allowed(*,official_epoch: str,lineage_epoch: str)->bool:
    _req(isinstance(official_epoch,str) and official_epoch,"official epoch required")
    _req(isinstance(lineage_epoch,str) and lineage_epoch,"lineage epoch required")
    return official_epoch==lineage_epoch
