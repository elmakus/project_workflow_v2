from __future__ import annotations
from typing import Any, Mapping, Sequence
from tools.pwv22_native_foundation import NativeFoundationError
from tools.pwv22_effects import effect_complete
from tools.pwv22_review import blocked_results, typed_finding

def _req(ok: bool,msg: str)->None:
    if not ok: raise NativeFoundationError(msg)

def close_ready(*,integration_confirmed: bool,publication_confirmed: bool,
                effects: Sequence[Mapping[str,Any]],findings: Sequence[Mapping[str,Any]],
                evolution_disposition: str,durable_confirmation: bool)->bool:
    _req(isinstance(integration_confirmed,bool) and isinstance(publication_confirmed,bool),"invalid completion proof")
    _req(isinstance(durable_confirmation,bool),"invalid durable confirmation")
    _req(evolution_disposition in ("preserve","revalidate","stale","recovery"),"invalid evolution disposition")
    for finding in findings: typed_finding(finding)
    if not integration_confirmed or not publication_confirmed or not durable_confirmation:return False
    if evolution_disposition in ("stale","recovery"):return False
    if blocked_results(findings):return False
    if any(not effect_complete(effect) for effect in effects):return False
    return True

def close_transition(record: Mapping[str,Any])->dict[str,Any]:
    _req(record.get("trigger")=="approved_scope_completion","branch or session termination is not Close")
    ready=close_ready(integration_confirmed=record.get("integration_confirmed"),
                      publication_confirmed=record.get("publication_confirmed"),
                      effects=record.get("effects",[]),findings=record.get("findings",[]),
                      evolution_disposition=record.get("evolution_disposition"),
                      durable_confirmation=record.get("durable_confirmation"))
    _req(ready,"Close obligations remain")
    return {"state":"closed","durable_confirmation":True}
