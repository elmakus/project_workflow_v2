from __future__ import annotations
from pathlib import Path
from typing import Any, Mapping, Sequence
from tools.pwv22_native_foundation import (
    NativeFoundationError,
    admit_native,
    exact_blob,
    material_fingerprint,
)

OWNERS=("intake","research","brainstorming","definition","planning","execution_prep","execution","review","close")
GATES=("A","B","C","D")
QUALIFICATION=("handoff","known_defect_cleanup","targeted_bug_hunt","global_bug_hunt","findings_reconciliation","final_acceptance","publication","close")

def _req(ok: bool,msg: str)->None:
    if not ok: raise NativeFoundationError(msg)

def exact_subject(subject: Mapping[str,Any], *, repo: Path, actual_repository: str,
                  remote: str="origin", canonical_ref: str="refs/heads/main")->dict[str,str]:
    # S05 exact_blob is the single exact Git identity validator: repository identity,
    # 40-hex commit/blob, safe regular-blob path, canonical reachability and commit:path == blob.
    exact_blob(repo,actual_repository,subject,remote=remote,canonical_ref=canonical_ref)
    return {k:subject[k] for k in ("repository","commit","path","blob")}

def route_owner(state: Mapping[str,Any], official: Mapping[str,Any])->str:
    # Ordinary native routing is illegal until S05 native admission proves generation/epoch.
    admit_native(state,official)
    phase=state.get("phase")
    _req(phase in OWNERS,"unsupported owner phase")
    if state.get("return_consumed") is True:
        _req(not state.get("return_pending"),"consumed return repeated")
    if state.get("research_required") is True: return "research"
    if state.get("question_or_alternative") is True: return "brainstorming"
    return phase

def simplification_ready(record: Mapping[str,Any])->bool:
    findings=record.get("material_findings",[])
    _req(isinstance(findings,list),"invalid simplification findings")
    dispositions=record.get("owner_dispositions",{})
    _req(isinstance(dispositions,Mapping),"invalid simplification dispositions")
    for f in findings:
        _req(isinstance(f,str) and f,"invalid simplification finding")
        if f in dispositions: _req(dispositions[f] in ("accept","reject"),"invalid owner disposition")
    return all(f in dispositions for f in findings)

def satisfy_gate(gate: str, expected_subject: Mapping[str,Any], presented_subject: Mapping[str,Any],
                 *, repo: Path, actual_repository: str, remote: str="origin",
                 canonical_ref: str="refs/heads/main")->dict[str,Any]:
    _req(gate in GATES,"unsupported gate")
    expected=exact_subject(expected_subject,repo=repo,actual_repository=actual_repository,remote=remote,canonical_ref=canonical_ref)
    presented=exact_subject(presented_subject,repo=repo,actual_repository=actual_repository,remote=remote,canonical_ref=canonical_ref)
    _req(expected==presented,"stale or wrong gate subject")
    return {"gate":gate,"subject":expected,"satisfied":True}

def initial_prep(seams: Sequence[Mapping[str,Any]])->dict[str,list[str]]:
    materialize=[]; jit=[]
    for seam in seams:
        sid=seam.get("id"); classification=seam.get("classification")
        _req(isinstance(sid,str) and sid,"missing seam id")
        _req(classification in ("materialization_ready","jit_dependent"),"invalid seam classification")
        if classification=="materialization_ready": materialize.append(sid)
        else:
            _req(bool(seam.get("future_fact")),"convenience JIT forbidden")
            jit.append(sid)
    return {"materialize":materialize,"jit":jit}

def premium_d_subject(prepared_subject: Mapping[str,Any], readback_subject: Mapping[str,Any],
                      *, repo: Path, actual_repository: str, remote: str="origin",
                      canonical_ref: str="refs/heads/main")->dict[str,Any]:
    return satisfy_gate("D",prepared_subject,readback_subject,repo=repo,actual_repository=actual_repository,
                        remote=remote,canonical_ref=canonical_ref)

def next_qualification(completed: Sequence[str])->str:
    completed=list(completed)
    _req(len(completed)<=len(QUALIFICATION),"invalid qualification history")
    _req(completed==list(QUALIFICATION[:len(completed)]),"skipped or reordered qualification")
    return "done" if len(completed)==len(QUALIFICATION) else QUALIFICATION[len(completed)]

def routing_fingerprint(state: Mapping[str,Any], official: Mapping[str,Any],
                        authority_refs: Sequence[Mapping[str,Any]])->str:
    material={"owner":route_owner(state,official),"phase":state.get("phase"),"gate":state.get("gate"),"qualification":state.get("qualification")}
    return material_fingerprint(list(authority_refs),material)
