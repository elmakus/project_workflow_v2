from __future__ import annotations
import hashlib, json, re, subprocess
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping

HEX40=re.compile(r"^[0-9a-f]{40}$")
class NativeFoundationError(ValueError): pass

def _req(ok: bool, msg: str) -> None:
    if not ok: raise NativeFoundationError(msg)

def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode()

def safe_path(raw: str) -> str:
    _req(isinstance(raw,str) and raw, "path required")
    _req("\\" not in raw, "unsafe path")
    p=PurePosixPath(raw)
    _req(not p.is_absolute() and ".." not in p.parts and "." not in p.parts, "unsafe path")
    return p.as_posix()

def _git(repo: Path, *args: str) -> bytes:
    try: return subprocess.check_output(["git","-C",str(repo),*args], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e: raise NativeFoundationError(e.output.decode(errors="replace").strip()) from e

def _remote_repository_identity(repo: Path, remote: str) -> str:
    url=_git(repo,"remote","get-url",remote).decode().strip().rstrip("/")
    github=re.fullmatch(r"(?:https://github\\.com/|git@github\\.com:)([^/]+/[^/]+?)(?:\\.git)?",url)
    if github: return github.group(1)
    local=Path(url[7:] if url.startswith("file://") else url).name
    _req(bool(local),"cannot derive repository identity")
    return local[:-4] if local.endswith(".git") else local

def exact_blob(repo: Path, actual_repository: str, ref: Mapping[str,Any], serving_bytes: bytes|None=None,
               *, remote: str="origin", canonical_ref: str="refs/heads/main") -> bytes:
    for k in ("repository","commit","path","blob"): _req(isinstance(ref.get(k),str) and ref[k], f"missing {k}")
    derived_repository=_remote_repository_identity(repo,remote)
    _req(ref["repository"]==actual_repository==derived_repository, "wrong repository")
    _req(bool(HEX40.fullmatch(ref["commit"])) and bool(HEX40.fullmatch(ref["blob"])), "identity must be 40-hex")
    path=safe_path(ref["path"])
    remote_head=remote_ref_head(repo,remote,canonical_ref)
    try:
        subprocess.check_output(["git","-C",str(repo),"merge-base","--is-ancestor",ref["commit"],remote_head],
                                stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        raise NativeFoundationError("commit not reachable from canonical published ref") from e
    entry=_git(repo,"ls-tree",ref["commit"],"--",path).decode().rstrip("\n")
    _req(bool(entry) and "\n" not in entry, "path missing or ambiguous")
    meta, found_path=entry.split("\t",1)
    mode, typ, actual=meta.split(" ",2)
    _req(found_path==path and typ=="blob" and mode!="120000","object is not regular blob")
    _req(actual==ref["blob"],"wrong blob")
    data=_git(repo,"show",f'{ref["commit"]}:{path}')
    if serving_bytes is not None: _req(data==serving_bytes,"serving bytes differ")
    return data

def material_fingerprint(refs: list[Mapping[str,Any]], properties: Mapping[str,Any]) -> str:
    normalized=[{k:r[k] for k in ("repository","commit","path","blob")} for r in refs]
    return hashlib.sha256(canonical_json({"refs":normalized,"properties":properties})).hexdigest()

def admit_native(state: Mapping[str,Any], official: Mapping[str,Any]) -> dict[str,str]:
    _req(state.get("generation")=="pwv2.2-native","unsupported or legacy generation")
    epoch=state.get("epoch"); _req(isinstance(epoch,str) and epoch,"missing epoch")
    _req(official.get("official") is True and official.get("epoch")==epoch,"unsupported official epoch")
    commit=official.get("commit"); _req(isinstance(commit,str) and HEX40.fullmatch(commit) is not None,"invalid official commit")
    _req(state.get("epoch")==epoch,"mixed native epoch")
    return {"epoch":epoch,"official_commit":commit}

def guarded_publish(*, expected_old: str, candidate: str,
                    read_head: Callable[[],str],
                    publish: Callable[[str,str],None],
                    readback: Callable[[],str]) -> str:
    _req(HEX40.fullmatch(expected_old) is not None and HEX40.fullmatch(candidate) is not None,"invalid commit identity")
    observed=read_head(); _req(observed==expected_old,"stale expected-old")
    publish(expected_old,candidate)
    final=readback(); _req(final==candidate,"target readback mismatch")
    return final

def validate_atomic_candidate(changes: Mapping[str,bytes], allowed_paths: set[str]) -> str:
    _req(bool(changes),"empty candidate")
    for p,v in changes.items():
        _req(safe_path(p) in allowed_paths,"write outside envelope")
        _req(isinstance(v,bytes),"candidate bytes required")
    return hashlib.sha256(canonical_json({p:hashlib.sha256(v).hexdigest() for p,v in sorted(changes.items())})).hexdigest()

def remote_ref_head(repo: Path, remote: str, ref: str) -> str:
    _req(isinstance(remote,str) and remote, "remote required")
    _req(isinstance(ref,str) and ref.startswith("refs/heads/"), "branch ref required")
    out=_git(repo,"ls-remote","--refs",remote,ref).decode().strip().splitlines()
    _req(len(out)==1, "remote ref missing or ambiguous")
    sha, found_ref=out[0].split("\t",1)
    _req(found_ref==ref and HEX40.fullmatch(sha) is not None, "invalid remote ref identity")
    return sha

def guarded_git_ref_publish(*, repo: Path, remote: str, ref: str,
                            expected_old: str, candidate: str) -> str:
    """Atomically publish one already-assembled Git commit with remote CAS and readback."""
    _req(HEX40.fullmatch(expected_old) is not None and HEX40.fullmatch(candidate) is not None,
         "invalid commit identity")
    _git(repo,"cat-file","-e",f"{candidate}^{{commit}}")
    observed=remote_ref_head(repo,remote,ref)
    _req(observed==expected_old,"stale expected-old")
    try:
        subprocess.check_output(
            ["git","-C",str(repo),"push","--porcelain",remote,
             f"{candidate}:{ref}",f"--force-with-lease={ref}:{expected_old}"],
            stderr=subprocess.STDOUT,
        )
    except subprocess.CalledProcessError as e:
        raise NativeFoundationError(e.output.decode(errors="replace").strip()) from e
    final=remote_ref_head(repo,remote,ref)
    _req(final==candidate,"target readback mismatch")
    return final
