#!/usr/bin/env python3
"""Offline EP1 construction-package checks, not PWV3 implementation or review."""
from __future__ import annotations

import hashlib
import json
import re
import sys
import tomllib
from collections import defaultdict, deque
from pathlib import Path, PurePosixPath


class InvalidPackage(ValueError):
    pass


def require(value, message):
    if not value:
        raise InvalidPackage(message)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load(path):
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)


def safe_path(raw):
    require(isinstance(raw, str) and raw and "\\" not in raw, "unsafe package path")
    path = PurePosixPath(raw)
    require(not path.is_absolute() and all(p not in {"", ".", ".."} for p in raw.split("/")), "unsafe package path")
    return path


def git_blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def validate_graph(contracts):
    order = contracts["total_order"]
    require(order == [f"PWV3-S{i:02}" for i in range(1, 14)], "stable total order differs from P1")
    cards = contracts["cards"]
    require([c["id"] for c in cards] == order, "missing, reordered or extra Card")
    require([c["plan_slot"] for c in cards] == [f"S{i:02}" for i in range(1, 14)], "Card refinement changes P1 slots")
    post = contracts["post_implementation"]
    require([p["id"] for p in post] == ["S14", "S15", "S16"], "post-implementation order")
    require([p["kind"] for p in post] == ["qualification", "qualification", "qualification_integration"], "qualification cannot become a Card")
    expected_inputs = {f"PWV3-S{i:02}": order[:i-1] for i in range(1, 10)}
    expected_inputs.update({"PWV3-S10": ["PWV3-S04", "PWV3-S05", "PWV3-S09"],
                            "PWV3-S11": ["PWV3-S09", "PWV3-S10"],
                            "PWV3-S12": ["PWV3-S06", "PWV3-S07", "PWV3-S09", "PWV3-S10"],
                            "PWV3-S13": order[:12]})
    nodes = {f"{phase}:{card}" for card in order for phase in ("start", "result", "checks", "review", "accepted")} | {p["id"] for p in post}
    edges = set()
    previous = None
    for card in cards:
        cid = card["id"]
        for field in ("scope", "excluded", "writes", "acceptance", "tests", "review", "dependency_gates"):
            require(field in card, f"{cid}: missing {field}")
        require(all(card[f] for f in ("scope", "excluded", "writes", "acceptance", "tests")), f"{cid}: empty contract")
        require(card["review"] == "ordinary_required", f"{cid}: missing/changed Review obligation")
        require(card["material_inputs"] == expected_inputs[cid], f"{cid}: material inputs differ from P1")
        for path in card["writes"]:
            safe_path(path.rstrip("/"))
        required_test = f"node --test test/slots/{card['plan_slot'].lower()}.test.mjs"
        require(required_test in card["tests"], f"{cid}: no bounded slot test")
        phases = [f"{p}:{cid}" for p in ("start", "result", "checks", "review", "accepted")]
        edges.update(zip(phases, phases[1:]))
        if previous:
            edges.add((f"accepted:{previous}", phases[0]))
        for dep in card["material_inputs"]:
            require(order.index(dep) < order.index(cid), "material input not an accepted predecessor")
            edges.add((f"accepted:{dep}", phases[0]))
        previous = cid
    expected_post_inputs = {"S14": ["PWV3-S13"], "S15": ["PWV3-S13", "S14"],
                            "S16": order + ["S14", "S15"]}
    for p in post:
        require(p["material_inputs"] == expected_post_inputs[p["id"]], "post-implementation prerequisite omitted or changed")
        for dep in p["material_inputs"]:
            edges.add((f"accepted:{dep}" if dep in order else dep, p["id"]))
    edges.update((a, b) for a, b in contracts["extra_acceptance_edges"])
    indegree = dict.fromkeys(nodes, 0)
    children = defaultdict(set)
    for a, b in edges:
        require(a in nodes and b in nodes, "unknown graph node")
        if b not in children[a]:
            children[a].add(b)
            indegree[b] += 1
    queue = deque(sorted(n for n in nodes if not indegree[n]))
    visited = []
    while queue:
        node = queue.popleft()
        visited.append(node)
        for child in sorted(children[node]):
            indegree[child] -= 1
            if not indegree[child]:
                queue.append(child)
    require(len(visited) == len(nodes), "combined order/material/acceptance cycle")
    delegated = {c["id"] for c in cards if c["delegation_required_unit"]}
    require(delegated == {"PWV3-S02", "PWV3-S06"}, "delegation-required units lost")
    for card in cards:
        unit = card["delegation_required_unit"]
        if unit:
            require(set(unit["writes"]) <= set(card["writes"]), "worker envelope exceeds Card")
            require(all(unit[f] for f in ("scope", "reads", "evidence", "stops", "condition")), "incomplete worker envelope")
    for relation in contracts["shared_impact_surfaces"]:
        require(relation["surface"] and relation["producers"] and relation["consumers"], "empty impact relation")
        require(set(relation["producers"] + relation["consumers"]) <= set(order + ["S14", "S15", "S16"]), "unknown impact endpoint")
    return {"nodes": len(nodes), "edges": len(edges), "acyclic": True}


def verify(root):
    root = Path(root).resolve()
    manifest = load(root / "MANIFEST.json")
    require(manifest["producing_contract"] == "EP1/1", "unsupported package contract")
    require(manifest["self_binding"] == "immutable containing Git subtree; manifest excluded from its own inventory", "manifest self-binding")
    inventory = manifest["files"]
    paths = [row["path"] for row in inventory]
    require(len(paths) == len(set(paths)), "duplicate inventory path")
    actual = set()
    for path in root.rglob("*"):
        require(not path.is_symlink(), "symlink in package")
        if path.is_file():
            actual.add(path.relative_to(root).as_posix())
    require(set(paths) == actual - {"MANIFEST.json"}, "inventory missing/extra file")
    for row in inventory:
        safe_path(row["path"])
        data = (root / row["path"]).read_bytes()
        require(len(data) == row["bytes"], f"length mismatch: {row['path']}")
        require(hashlib.sha256(data).hexdigest() == row["sha256"], f"content mismatch: {row['path']}")
        require(git_blob(data) == row["git_blob"], f"blob mismatch: {row['path']}")
        require(row["producing_contract"] == ("historical-unversioned; original bytes retained" if row["path"].startswith("snapshots/") else "EP1/1"), "incorrect producing contract")
    index = load(root / "SNAPSHOTS.json")
    snapshots = index["snapshots"]
    by_id = {s["id"]: s for s in snapshots}
    require(len(by_id) == len(snapshots) == 57, "snapshot closure changed")
    require(len({s["local_path"] for s in snapshots}) == len(snapshots), "duplicate snapshot path")
    require({s["local_path"] for s in snapshots} == {p for p in paths if p.startswith("snapshots/")}, "snapshot inventory mismatch")
    for row in snapshots:
        safe_path(row["path"])
        safe_path(row["local_path"])
        require(re.fullmatch(r"[0-9a-f]{40}", row["commit"]), "invalid source commit")
        expected_repo = "elmakus/project-research" if row["id"] in {"corpus", "donor", "r5", "d12-review"} else "elmakus/project_workflow_v2"
        require(row["repository"] == expected_repo, "wrong snapshot source repository")
        require(git_blob((root / row["local_path"]).read_bytes()) == row["blob"], "snapshot differs from source blob")
    pins = {
        "d12": ("acba6b0eee1b88d56400b8aaaa77b5083c45aa30", "f8cbe2416de455c45adb2319bfd82a97b8b43360"),
        "d12-decisions": ("acba6b0eee1b88d56400b8aaaa77b5083c45aa30", "c1e52e7676a8f6ce05118dfda91982e214838594"),
        "p1": ("c67645f7cd0a0887003da178bc8eaaf44357668b", "ba2990d773cdd30673f2ce23a6bc74700c6c56cf"),
        "corpus": ("a2797f4b92ff932d66927b846e2f7ca17e691363", "1f29a31f6bfa0b2b9486654c2a20eb6c1258c1a6"),
        "donor": ("ee2c9a1bcdda70444c1207404ab1dfb8524d5038", "d6d6329bdb58196ba1127c6a98620bdedc299f56"),
        "r5": ("0bdfccd332b78caa0795283ec64d366def01b511", "94753f446542d03171f81a2827cb188420cf1df2"),
        "d12-review": ("1704c68a3e2f2839f3dd83adbaece45281104dd2", "e386fb1bc888fd671e99409cdf274e365a36303b")}
    for key, (commit, blob) in pins.items():
        require((by_id[key]["commit"], by_id[key]["blob"]) == (commit, blob), f"accepted pin changed: {key}")
    definition = tomllib.loads((root / by_id["d12-decisions"]["local_path"]).read_text())
    require(definition["state"] == "green" and definition["revision"] == "D12", "D12 acceptance missing")
    ordered = index["decision_order"]
    require(ordered == [f"decision-{n:02}" for n in range(1, 44)], "decision ordering lost")
    require(len(definition["decisions"]) == 43, "decision set size")
    for ref, key in zip(definition["decisions"], ordered):
        require(ref["path"] == by_id[key]["path"] and by_id[key]["commit"] == pins["d12"][0], "wrong ordered decision binding")
    planning = tomllib.loads((root / by_id["approved-planning"]["local_path"]).read_text())
    review = tomllib.loads((root / by_id["plan-review"]["local_path"]).read_text())
    require(planning["state"] == "approved" and planning["premium_c"] == "satisfied", "P1/C not accepted")
    require(review["verdict"] == "green" and not review["independence"]["materially_produced_or_repaired_subject"], "P1 review missing")
    for key in ("repository", "commit", "path", "blob"):
        require(planning["subject"][key] == review["subject"][key] == by_id["p1"][key], "P1 subject mismatch")
    contracts = load(root / "CONTRACTS.json")
    graph = validate_graph(contracts)
    coverage = load(root / "COVERAGE.json")
    corpus = (root / by_id["corpus"]["local_path"]).read_text()
    expected_families = set(re.findall(r"^### (PWV3-REG-\S+)", corpus, re.M))
    expected_negatives = set(re.findall(r"^\| (PWV3-NEG-\S+) \|", corpus, re.M))
    expectations = {"regression_families": expected_families,
                    "removed_negatives": expected_negatives,
                    "structural_guards": {f"PWV3-GUARD-{n:02}" for n in range(1, 21)},
                    "d12_seams": {f"PWV3-D12-{n:02}" for n in range(1, 11)},
                    "definition_coverage": {f"C{n:02}" for n in range(1, 27)}}
    allowed = set(contracts["total_order"] + ["S14", "S15", "S16"])
    for group, expected in expectations.items():
        rows = coverage[group]
        require(len(rows) == len(expected) and {r["id"] for r in rows} == expected, f"incomplete {group}")
        for row in rows:
            require(row["owners"] and set(row["owners"]) <= allowed, f"unowned coverage: {row['id']}")
            for path in row.get("test_paths", []) + ([row["test_path"]] if "test_path" in row else []):
                safe_path(path)
    require(len(coverage["live_matrix"]) == 6, "live surface omitted")
    donors = load(root / "DONORS.json")
    for unit in donors["units"]:
        require(unit["disposition"] in {"REIMPLEMENT", "DROP", "TEST_ONLY"}, "unaudited COPY/PORT")
        require(all(unit[key] for key in ("invariant", "repository", "commit", "path", "blob", "symbols", "target", "transformation", "licence_notice", "tests")), "incomplete donor provenance")
        require(re.fullmatch(r"[0-9a-f]{40}", unit["commit"]) and re.fullmatch(r"[0-9a-f]{40}", unit["blob"]), "invalid donor identity")
    return {"package_check": "PASS", "not_independent_review": True, "not_product_qualification": True,
            "files": len(paths) + 1, "snapshots": len(snapshots), "decisions": len(ordered),
            "cards": len(contracts["cards"]), "qualification_obligations": 3,
            "regression_families": len(expected_families), "guards": 20, "removed_negatives": len(expected_negatives),
            "d12_seams": 10, "definition_coverage": 26, "declared_graph": graph}


if __name__ == "__main__":
    try:
        print(json.dumps(verify(Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).resolve().parent), indent=2))
    except (InvalidPackage, KeyError, TypeError, ValueError, OSError) as exc:
        print(f"EP1 INVALID: {exc}", file=sys.stderr)
        sys.exit(1)
