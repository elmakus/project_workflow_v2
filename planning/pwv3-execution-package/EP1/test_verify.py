"""Synthetic EP1 package-check regressions; no model, network or product inference."""
import copy
import hashlib
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from verify import InvalidPackage, git_blob, load, validate_graph, verify


ROOT = Path(__file__).resolve().parent


class PackageChecks(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "package"
        shutil.copytree(ROOT, self.root)

    def write_json(self, path, data):
        (self.root / path).write_text(json.dumps(data, indent=2) + "\n")

    def rehash(self, path):
        # Isolate inner predicate from the outer inventory guard.
        manifest = load(self.root / "MANIFEST.json")
        data = (self.root / path).read_bytes()
        row = next(r for r in manifest["files"] if r["path"] == path)
        row.update(bytes=len(data), sha256=hashlib.sha256(data).hexdigest(), git_blob=git_blob(data))
        self.write_json("MANIFEST.json", manifest)

    def test_offline_copy_passes(self):
        result = verify(self.root)
        self.assertEqual((result["cards"], result["qualification_obligations"], result["decisions"]), (13, 3, 43))
        self.assertEqual(result["regression_families"], 36)
        self.assertTrue(result["declared_graph"]["acyclic"])

    def test_changed_same_path_fails(self):
        (self.root / "README.md").write_text("changed")
        with self.assertRaisesRegex(InvalidPackage, "length mismatch"):
            verify(self.root)

    def test_missing_file_fails(self):
        (self.root / "QUALIFICATION.md").unlink()
        with self.assertRaisesRegex(InvalidPackage, "inventory"):
            verify(self.root)

    def test_extra_file_fails(self):
        (self.root / "unreviewed.txt").write_text("extra")
        with self.assertRaisesRegex(InvalidPackage, "inventory"):
            verify(self.root)

    def test_symlink_fails(self):
        (self.root / "alias").symlink_to(self.root / "README.md")
        with self.assertRaisesRegex(InvalidPackage, "symlink"):
            verify(self.root)

    def test_snapshot_byte_identity_independent_of_inventory(self):
        path = "snapshots/authority/DEFINITION.md"
        with (self.root / path).open("a") as f:
            f.write("changed acceptance\n")
        self.rehash(path)
        with self.assertRaisesRegex(InvalidPackage, "snapshot differs"):
            verify(self.root)

    def test_missing_family_even_if_inventory_updated(self):
        path = "COVERAGE.json"
        obj = load(self.root / path)
        obj["regression_families"].pop()
        self.write_json(path, obj)
        self.rehash(path)
        with self.assertRaisesRegex(InvalidPackage, "incomplete regression_families"):
            verify(self.root)

    def test_missing_guard_or_negative_or_seam(self):
        original = load(self.root / "COVERAGE.json")
        for group in ("structural_guards", "removed_negatives", "d12_seams", "definition_coverage"):
            with self.subTest(group=group):
                obj = copy.deepcopy(original)
                obj[group].pop()
                self.write_json("COVERAGE.json", obj)
                self.rehash("COVERAGE.json")
                with self.assertRaisesRegex(InvalidPackage, f"incomplete {group}"):
                    verify(self.root)

    def test_unowned_coverage_fails(self):
        obj = load(self.root / "COVERAGE.json")
        obj["regression_families"][0]["owners"] = []
        self.write_json("COVERAGE.json", obj)
        self.rehash("COVERAGE.json")
        with self.assertRaisesRegex(InvalidPackage, "unowned coverage"):
            verify(self.root)

    def test_duplicate_json_key_fails(self):
        (self.root / "MANIFEST.json").write_text('{"files": [], "files": []}')
        with self.assertRaisesRegex(InvalidPackage, "duplicate JSON key"):
            verify(self.root)

    def test_acceptance_back_edge_fails(self):
        contracts = load(self.root / "CONTRACTS.json")
        contracts["extra_acceptance_edges"] = [["S14", "accepted:PWV3-S13"]]
        with self.assertRaisesRegex(InvalidPackage, "cycle"):
            validate_graph(contracts)

    def test_future_material_input_fails(self):
        contracts = load(self.root / "CONTRACTS.json")
        contracts["cards"][0]["material_inputs"] = ["PWV3-S13"]
        with self.assertRaisesRegex(InvalidPackage, "material inputs differ"):
            validate_graph(contracts)

    def test_qualification_cannot_be_card(self):
        contracts = load(self.root / "CONTRACTS.json")
        contracts["post_implementation"][0]["kind"] = "card"
        with self.assertRaisesRegex(InvalidPackage, "qualification cannot"):
            validate_graph(contracts)

    def test_qualification_cannot_skip_card_acceptance(self):
        contracts = load(self.root / "CONTRACTS.json")
        contracts["post_implementation"][0]["material_inputs"] = []
        with self.assertRaisesRegex(InvalidPackage, "prerequisite omitted"):
            validate_graph(contracts)

    def test_snapshot_wrong_source_repository_fails(self):
        obj = load(self.root / "SNAPSHOTS.json")
        obj["snapshots"][0]["repository"] = "untrusted/other"
        self.write_json("SNAPSHOTS.json", obj)
        self.rehash("SNAPSHOTS.json")
        with self.assertRaisesRegex(InvalidPackage, "wrong snapshot source"):
            verify(self.root)

    def test_review_cannot_be_unspecified(self):
        contracts = load(self.root / "CONTRACTS.json")
        contracts["cards"][0]["review"] = "unknown"
        with self.assertRaisesRegex(InvalidPackage, "Review obligation"):
            validate_graph(contracts)

    def test_delegated_unit_cannot_be_dropped(self):
        contracts = load(self.root / "CONTRACTS.json")
        contracts["cards"][1]["delegation_required_unit"] = None
        with self.assertRaisesRegex(InvalidPackage, "delegation-required"):
            validate_graph(contracts)

    def test_worker_cannot_expand_writes(self):
        contracts = load(self.root / "CONTRACTS.json")
        contracts["cards"][1]["delegation_required_unit"]["writes"].append("src/kernel/")
        with self.assertRaisesRegex(InvalidPackage, "envelope exceeds"):
            validate_graph(contracts)


if __name__ == "__main__":
    unittest.main()
