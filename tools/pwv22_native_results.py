from __future__ import annotations
from typing import Any, Callable, Mapping, Sequence
from tools.pwv22_native_foundation import NativeFoundationError, material_fingerprint

REQUIRED_IDENTITY=("repository","commit","path","blob")

def _req(ok: bool,msg: str)->None:
    if not ok: raise NativeFoundationError(msg)

def exact_identity(value: Mapping[str,Any])->dict[str,str]:
    _req(isinstance(value,Mapping),"identity must be object")
    for key in REQUIRED_IDENTITY:
        _req(isinstance(value.get(key),str) and value[key],f"missing {key}")
    return {key:value[key] for key in REQUIRED_IDENTITY}

def typed_result(record: Mapping[str,Any])->dict[str,Any]:
    _req(record.get("type")=="pwv2.2-result","wrong result type")
    rid=record.get("result_id"); _req(isinstance(rid,str) and rid,"missing result id")
    subject=exact_identity(record.get("implementation_subject",{}))
    materials=record.get("material_inputs",[])
    _req(isinstance(materials,list),"material inputs must be list")
    normalized=[exact_identity(x) for x in materials]
    return {"type":"pwv2.2-result","result_id":rid,"implementation_subject":subject,"material_inputs":normalized}

def accepted_dependency(expected: Mapping[str,Any], result: Mapping[str,Any],
                        acceptance: Mapping[str,Any],
                        verify_identity: Callable[[Mapping[str,Any]],Any])->dict[str,Any]:
    expected=exact_identity(expected)
    locator=exact_identity(result.get("result_artifact",{}))
    _req(locator==expected,"missing, stale or wrong predecessor Result")
    verify_identity(expected)
    typed=typed_result(result)
    verify_identity(typed["implementation_subject"])
    for material in typed["material_inputs"]:
        verify_identity(material)
    _req(acceptance.get("verdict")=="green","predecessor acceptance is not GREEN")
    _req(exact_identity(acceptance.get("subject",{}))==expected,"stale constituent acceptance")
    return typed

def result_fingerprint(result: Mapping[str,Any])->str:
    typed=typed_result(result)
    return material_fingerprint(typed["material_inputs"],{
        "result_id":typed["result_id"],
        "implementation_subject":typed["implementation_subject"],
    })

def material_fresh(result: Mapping[str,Any], current_material_inputs: Sequence[Mapping[str,Any]])->bool:
    typed=typed_result(result)
    current=[exact_identity(x) for x in current_material_inputs]
    return typed["material_inputs"]==current

def affected_results(results: Sequence[Mapping[str,Any]], changed_inputs: Sequence[Mapping[str,Any]])->list[str]:
    changed={tuple(exact_identity(x)[k] for k in REQUIRED_IDENTITY) for x in changed_inputs}
    affected=[]
    for result in results:
        typed=typed_result(result)
        material={tuple(x[k] for k in REQUIRED_IDENTITY) for x in typed["material_inputs"]}
        if material & changed: affected.append(typed["result_id"])
    return affected

def readiness(required: Sequence[Mapping[str,Any]], available: Sequence[Mapping[str,Any]],
              acceptances: Mapping[str,Mapping[str,Any]],
              verify_identity: Callable[[Mapping[str,Any]],Any])->bool:
    by_locator={tuple(exact_identity(r.get("result_artifact",{}))[k] for k in REQUIRED_IDENTITY):r for r in available}
    for dep in required:
        identity=exact_identity(dep); key=tuple(identity[k] for k in REQUIRED_IDENTITY)
        result=by_locator.get(key)
        if result is None: return False
        acceptance=acceptances.get(result.get("result_id",""))
        if acceptance is None: return False
        accepted_dependency(identity,result,acceptance,verify_identity)
    return True

def frontier(cards: Sequence[Mapping[str,Any]], available: Sequence[Mapping[str,Any]],
             acceptances: Mapping[str,Mapping[str,Any]],
             verify_identity: Callable[[Mapping[str,Any]],Any])->list[str]:
    ready=[]
    for card in cards:
        cid=card.get("id"); _req(isinstance(cid,str) and cid,"missing card id")
        deps=card.get("dependencies",[]); _req(isinstance(deps,list),"dependencies must be list")
        if readiness(deps,available,acceptances,verify_identity): ready.append(cid)
    return ready

def append_result(history: Sequence[Mapping[str,Any]], candidate: Mapping[str,Any])->list[Mapping[str,Any]]:
    typed=typed_result(candidate)
    for prior in history:
        p=typed_result(prior)
        _req(p["result_id"]!=typed["result_id"],"Result history is immutable")
        _req(p["implementation_subject"]!=typed["implementation_subject"],"unchanged implementation must retain existing Result")
    return [*history,candidate]
