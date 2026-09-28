from __future__ import annotations
from typing import Any, Callable, Mapping, Sequence
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
    cards=record.get("cards"); _req(isinstance(cards,list) and cards,"admission must be finite non-empty")
    _req(len(cards)==len(set(cards)) and all(isinstance(x,str) and x for x in cards),"invalid admission cards")
    subjects=record.get("subjects"); _req(isinstance(subjects,Mapping),"admission subjects must be object")
    _req(set(subjects)==set(cards),"admission subjects must exactly cover cards")
    typed_subjects={cid:exact_identity(subjects[cid]) for cid in cards}
    owners=record.get("mutating_owners"); _req(isinstance(owners,Mapping),"admission mutating owners must be object")
    _req(set(owners)==set(cards),"admission mutating owners must exactly cover cards")
    typed_owners={cid:owners[cid] for cid in cards}
    _req(all(isinstance(owner,str) and owner for owner in typed_owners.values()),"invalid admission mutating owner")
    revoked=record.get("revoked",[]); _req(isinstance(revoked,list),"revoked must be list")
    _req(all(isinstance(x,str) and x in cards for x in revoked),"revoked card outside admission")
    return {"type":"pwv2.2-admission","admission_id":aid,"cards":list(cards),"subjects":typed_subjects,"mutating_owners":typed_owners,"revoked":list(revoked)}

def accepted_admission(admission_identity: Mapping[str,Any],
                       read_admission: Callable[[Mapping[str,Any]],Mapping[str,Any]],
                       acceptance_identity: Mapping[str,Any],
                       read_acceptance: Callable[[Mapping[str,Any]],Mapping[str,Any]],
                       verify_identity)->dict[str,Any]:
    admission_ref=exact_identity(admission_identity)
    verify_identity(admission_ref)
    admission=read_admission(admission_ref)
    _req(isinstance(admission,Mapping),"admission artifact must be durable mapping")
    a=typed_admission(admission)
    for subject in a["subjects"].values():
        verify_identity(subject)
    acceptance_ref=exact_identity(acceptance_identity)
    acceptance=read_acceptance(acceptance_ref)
    _req(isinstance(acceptance,Mapping),"admission acceptance must be durable mapping")
    _req(acceptance.get("verdict")=="green","admission acceptance is not GREEN")
    _req(exact_identity(acceptance.get("subject",{}))==admission_ref,"stale admission acceptance")
    return a

def typed_claims(record: Mapping[str,Any])->dict[str,set[str]]:
    cid=record.get("card_id"); _req(isinstance(cid,str) and cid,"missing card id")
    owner=record.get("mutating_owner"); _req(isinstance(owner,str) and owner,"missing mutating owner")
    subject=exact_identity(record.get("subject",{}))
    return {"card_id":cid,"subject":subject,"mutating_owner":owner,**{k:_claim_set(record.get(k,[]),k) for k in CLAIM_KINDS}}

def admitted(card_id: str, subject: Mapping[str,Any], admission: Mapping[str,Any])->bool:
    a=typed_admission(admission)
    return card_id in a["cards"] and card_id not in a["revoked"] and a["subjects"][card_id]==exact_identity(subject)

def parallel_legal(left: Mapping[str,Any], right: Mapping[str,Any], admission_identity: Mapping[str,Any],
                   read_admission, admission_acceptance_identity: Mapping[str,Any], read_acceptance,
                   verify_identity)->bool:
    l=typed_claims(left); r=typed_claims(right)
    a=accepted_admission(admission_identity,read_admission,admission_acceptance_identity,read_acceptance,verify_identity)
    if l["card_id"]==r["card_id"]: return False
    if l["card_id"] not in a["cards"] or l["card_id"] in a["revoked"] or a["subjects"][l["card_id"]]!=l["subject"] or a["mutating_owners"][l["card_id"]]!=l["mutating_owner"]: return False
    if r["card_id"] not in a["cards"] or r["card_id"] in a["revoked"] or a["subjects"][r["card_id"]]!=r["subject"] or a["mutating_owners"][r["card_id"]]!=r["mutating_owner"]: return False
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
                      expected_card_subjects: Mapping[str,Mapping[str,Any]],
                      expected_results: Sequence[Mapping[str,Any]],
                      results: Sequence[Mapping[str,Any]],
                      acceptance_identities: Mapping[str,Mapping[str,Any]],
                      admission_identity: Mapping[str,Any],
                      read_admission,
                      admission_acceptance_identity: Mapping[str,Any],
                      read_acceptance,
                      verify_identity,
                      compatibility)->list[dict[str,Any]]:
    _req(len(expected_results)>1,"fan-in requires sibling set")
    _req(len(expected_card_ids)==len(expected_results)==len(results),"incomplete sibling set")
    _req(len(expected_card_ids)==len(set(expected_card_ids)) and all(isinstance(x,str) and x for x in expected_card_ids),
         "invalid sibling card set")
    a=accepted_admission(admission_identity,read_admission,admission_acceptance_identity,read_acceptance,verify_identity)
    _req(set(expected_card_subjects)==set(expected_card_ids),"sibling subjects must exactly cover cards")
    for cid in expected_card_ids:
        subject=exact_identity(expected_card_subjects[cid])
        _req(cid in a["cards"] and cid not in a["revoked"] and a["subjects"][cid]==subject,"sibling exact subject is not admitted")
    accepted=[]
    for expected,result in zip(expected_results,results):
        rid=result.get("result_id","")
        acc_identity=acceptance_identities.get(rid)
        _req(acc_identity is not None,"missing sibling acceptance")
        acc_ref=exact_identity(acc_identity)
        acc=read_acceptance(acc_ref)
        _req(isinstance(acc,Mapping),"sibling acceptance must be durable mapping")
        accepted.append(accepted_dependency(expected,result,acc,verify_identity))
    _req(bool(compatibility(accepted)),"integrated sibling incompatibility")
    return accepted
