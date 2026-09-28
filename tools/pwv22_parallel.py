from __future__ import annotations
from typing import Any, Mapping, Sequence
from tools.pwv22_native_foundation import NativeFoundationError
from tools.pwv22_native_results import exact_identity, accepted_dependency

CLAIM_KINDS=("writes","resources","semantics","effects")

def _req(ok: bool,msg: str)->None:
    if not ok: raise NativeFoundationError(msg)

def _claim_set(value: Any, kind: str)->set[str]:
    _req(isinstance(value,list),f"{kind} claims must be list")
    out=set()
    for item in value:
        _req(isinstance(item,str) and item,f"invalid {kind} claim")
        out.add(item)
    return out

def typed_admission(record: Mapping[str,Any])->dict[str,Any]:
    _req(record.get("type")=="pwv2.2-admission","wrong admission type")
    aid=record.get("admission_id"); _req(isinstance(aid,str) and aid,"missing admission id")
    subject=exact_identity(record.get("subject",{}))
    cards=record.get("cards"); _req(isinstance(cards,list) and cards,"admission must be finite non-empty")
    _req(len(cards)==len(set(cards)) and all(isinstance(x,str) and x for x in cards),"invalid admission cards")
    revoked=record.get("revoked",[]); _req(isinstance(revoked,list),"revoked must be list")
    _req(all(isinstance(x,str) and x in cards for x in revoked),"revoked card outside admission")
    return {"type":"pwv2.2-admission","admission_id":aid,"subject":subject,"cards":list(cards),"revoked":list(revoked)}

def accepted_admission(admission: Mapping[str,Any], acceptance: Mapping[str,Any], verify_identity)->dict[str,Any]:
    a=typed_admission(admission)
    verify_identity(a["subject"])
    _req(acceptance.get("verdict")=="green","admission acceptance is not GREEN")
    _req(exact_identity(acceptance.get("subject",{}))==a["subject"],"stale admission acceptance")
    return a

def typed_claims(record: Mapping[str,Any])->dict[str,set[str]]:
    cid=record.get("card_id"); _req(isinstance(cid,str) and cid,"missing card id")
    owner=record.get("mutating_owner"); _req(isinstance(owner,str) and owner,"missing mutating owner")
    return {"card_id":cid,"mutating_owner":owner,**{k:_claim_set(record.get(k,[]),k) for k in CLAIM_KINDS}}

def admitted(card_id: str, admission: Mapping[str,Any])->bool:
    a=typed_admission(admission)
    return card_id in a["cards"] and card_id not in a["revoked"]

def parallel_legal(left: Mapping[str,Any], right: Mapping[str,Any], admission: Mapping[str,Any],
                   admission_acceptance: Mapping[str,Any], verify_identity)->bool:
    l=typed_claims(left); r=typed_claims(right)
    a=accepted_admission(admission,admission_acceptance,verify_identity)
    if l["card_id"]==r["card_id"]: return False
    if l["card_id"] not in a["cards"] or l["card_id"] in a["revoked"]: return False
    if r["card_id"] not in a["cards"] or r["card_id"] in a["revoked"]: return False
    for kind in CLAIM_KINDS:
        if not l[kind] or not r[kind]: return False
        if l[kind] & r[kind]: return False
    return True

def one_mutating_owner(claim_sets: Sequence[Mapping[str,Any]])->bool:
    owners:dict[str,str]={}
    for raw in claim_sets:
        c=typed_claims(raw)
        prior=owners.setdefault(c["card_id"],c["mutating_owner"])
        if prior!=c["mutating_owner"]: return False
    return True

def compatible_fan_in(expected_card_ids: Sequence[str],
                      expected_results: Sequence[Mapping[str,Any]],
                      results: Sequence[Mapping[str,Any]],
                      acceptances: Mapping[str,Mapping[str,Any]],
                      admission: Mapping[str,Any],
                      admission_acceptance: Mapping[str,Any],
                      verify_identity,
                      compatibility)->list[dict[str,Any]]:
    _req(len(expected_results)>1,"fan-in requires sibling set")
    _req(len(expected_card_ids)==len(expected_results)==len(results),"incomplete sibling set")
    _req(len(expected_card_ids)==len(set(expected_card_ids)) and all(isinstance(x,str) and x for x in expected_card_ids),
         "invalid sibling card set")
    a=accepted_admission(admission,admission_acceptance,verify_identity)
    for cid in expected_card_ids:
        _req(cid in a["cards"] and cid not in a["revoked"],"sibling is not admitted")
    accepted=[]
    for expected,result in zip(expected_results,results):
        rid=result.get("result_id","")
        acc=acceptances.get(rid)
        _req(acc is not None,"missing sibling acceptance")
        accepted.append(accepted_dependency(expected,result,acc,verify_identity))
    _req(bool(compatibility(accepted)),"integrated sibling incompatibility")
    return accepted
