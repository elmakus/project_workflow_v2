from __future__ import annotations
from typing import Any, Mapping
from tools.pwv22_native_foundation import NativeFoundationError

STATES=("intent","attempted","known","UNKNOWN")

def _req(ok: bool,msg: str)->None:
    if not ok: raise NativeFoundationError(msg)

def effect_intent(*,obligation_id: str,subject: Mapping[str,Any],target: str,request_id: str|None=None)->dict[str,Any]:
    _req(isinstance(obligation_id,str) and obligation_id,"obligation id required")
    _req(isinstance(target,str) and target,"target required")
    _req(isinstance(subject,Mapping) and bool(subject),"subject required")
    if request_id is not None:_req(isinstance(request_id,str) and request_id,"invalid request id")
    _req(not any("secret" in str(k).lower() for k in subject),"secrets forbidden in effect subject")
    return {"type":"pwv2.2-effect","obligation_id":obligation_id,"subject":dict(subject),"target":target,
            "state":"intent","request_id":request_id}

def record_attempt(intent: Mapping[str,Any], *, attempt_id: str)->dict[str,Any]:
    _req(intent.get("state")=="intent","effect attempt requires intent")
    _req(isinstance(attempt_id,str) and attempt_id,"attempt id required")
    return {**intent,"state":"attempted","attempt_id":attempt_id}

def record_readback(attempt: Mapping[str,Any], *, observed: bool|None, evidence: Mapping[str,Any])->dict[str,Any]:
    _req(attempt.get("state")=="attempted","readback requires attempted effect")
    _req(isinstance(evidence,Mapping) and bool(evidence),"readback evidence required")
    if observed is None:return {**attempt,"state":"UNKNOWN","readback":dict(evidence)}
    return {**attempt,"state":"known","applied":bool(observed),"readback":dict(evidence)}

def retry_allowed(record: Mapping[str,Any], *, target_supports_idempotency: bool)->bool:
    state=record.get("state"); _req(state in STATES,"invalid effect state")
    if state=="UNKNOWN": return False
    if state=="known": return record.get("applied") is False
    if state=="attempted": return False
    if target_supports_idempotency:
        return isinstance(record.get("request_id"),str) and bool(record.get("request_id"))
    return True

def effect_complete(record: Mapping[str,Any])->bool:
    return record.get("state")=="known" and record.get("applied") is True
