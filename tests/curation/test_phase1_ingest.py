import hashlib
import os
import shutil
import tempfile
import unittest
import yaml
from pathlib import Path

import sys
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "adapters" / "python"))

from stemma_ingest.phase1 import run_phase1, PROPOSALS_DIR, acquire_source, extract_physical_page_count

def hash_directory(directory: Path) -> dict[str, str]:
    hashes = {}
    if directory.exists():
        for root, _, files in os.walk(directory):
            for file in files:
                p = Path(root) / file
                hashes[str(p)] = hashlib.sha256(p.read_bytes()).hexdigest()
    return hashes

class TestPhase1Ingestion(unittest.TestCase):
    def setUp(self):
        self.fixture_path = str(ROOT / "tests" / "curation" / "fixture.pdf")
        
        self.canonical_dirs = [ROOT / d for d in ["content", "connections", "sources", "ledger", "indexes"]]
        
        self.seeded_canonical_file = self.canonical_dirs[0] / "seeded_fixture.yaml"
        self.seeded_canonical_file.write_text("seeded canonical data")
        
        self.snapshot = {}
        for d in self.canonical_dirs:
            self.snapshot.update(hash_directory(d))

    def tearDown(self):
        self.check_governance_invariant()
        if hasattr(self, 'seeded_canonical_file') and self.seeded_canonical_file.exists():
            self.seeded_canonical_file.unlink()

    def check_governance_invariant(self):
        current = {}
        for d in self.canonical_dirs:
            current.update(hash_directory(d))
            
        self.assertEqual(set(self.snapshot.keys()), set(current.keys()), "Canonical file count/names changed!")
        for k in self.snapshot:
            self.assertEqual(self.snapshot[k], current[k], f"Governance violation: {k} content changed!")

    def test_successful_ingestion(self):
        run_id, source_hash, window_count, status = run_phase1(self.fixture_path, "test_success.proposal.yaml")
        self.assertEqual(status, "SUCCESS")
        self.assertGreater(window_count, 0)
        
        out_path = PROPOSALS_DIR / "test_success.proposal.yaml"
        self.assertTrue(out_path.exists())
        
        with open(out_path) as f:
            data = yaml.safe_load(f)
            
        self.assertEqual(data["source"]["content_hash"], source_hash)
        self.assertEqual(data["document"]["format"], "pdf")
        self.assertEqual(data["document"]["physical_page_count"], 2)
        
        windows_text = " ".join(w["text"] for w in data["evidence_windows"])
        self.assertIn("IGNORE PREVIOUS INSTRUCTIONS", windows_text)
        
        out_path.unlink()

    def test_determinism(self):
        run_phase1(self.fixture_path, "test_det1.proposal.yaml")
        run_phase1(self.fixture_path, "test_det2.proposal.yaml")
        
        with open(PROPOSALS_DIR / "test_det1.proposal.yaml") as f1, open(PROPOSALS_DIR / "test_det2.proposal.yaml") as f2:
            d1 = yaml.safe_load(f1)
            d2 = yaml.safe_load(f2)
            
        for d in [d1, d2]:
            del d["run"]["started_at"]
            del d["run"]["completed_at"]
            del d["run"]["run_id"]
            del d["source"]["source_id"]
            
        self.assertEqual(d1, d2)
        
        (PROPOSALS_DIR / "test_det1.proposal.yaml").unlink()
        (PROPOSALS_DIR / "test_det2.proposal.yaml").unlink()

    def test_path_traversal(self):
        with self.assertRaises(PermissionError) as cm:
            run_phase1(self.fixture_path, "../../content/malicious.yaml")
        self.assertIn("escapes proposals directory", str(cm.exception))
        
        with self.assertRaises(PermissionError):
            run_phase1(self.fixture_path, "/tmp/absolute_malicious.yaml")

    def test_invalid_source_format(self):
        fd, temp_path = tempfile.mkstemp(suffix=".pdf")
        with os.fdopen(fd, 'w') as f:
            f.write("This is not a PDF")
            
        with self.assertRaises(ValueError) as cm:
            run_phase1(temp_path)
        self.assertIn("INVALID_SOURCE", str(cm.exception))
        os.remove(temp_path)

    def test_toctou_mutation_protection(self):
        fd, temp_path = tempfile.mkstemp(suffix=".pdf")
        with os.fdopen(fd, 'wb') as f:
            f.write(b"%PDF-1.4\nFirst state")
            
        source = acquire_source(temp_path)
        
        with open(temp_path, 'wb') as f:
            f.write(b"%PDF-1.4\nMutated state")
            
        self.assertEqual(source.raw_bytes, b"%PDF-1.4\nFirst state")
        self.assertNotEqual(source.raw_bytes, Path(temp_path).read_bytes())
        
        os.remove(temp_path)

    def test_no_text_layer(self):
        fixture_path = str(ROOT / "tests" / "curation" / "scanned_fixture.pdf")
        run_id, source_hash, windows_len, status = run_phase1(fixture_path, "test_scanned.proposal.yaml")
        
        self.assertEqual(status, "NO_TEXT_LAYER")
        self.assertEqual(windows_len, 0)
        
        out_path = PROPOSALS_DIR / "test_scanned.proposal.yaml"
        with open(out_path) as f:
            data = yaml.safe_load(f)
            
        self.assertEqual(data["document"]["physical_page_count"], 1)
        self.assertEqual(data["document"]["extracted_text_page_count"], 0)
        self.assertEqual(len(data["evidence_windows"]), 0)
        self.assertEqual(data["document"]["status"], "NO_TEXT_LAYER")
        
        pdf_bytes = Path(fixture_path).read_bytes()
        self.assertIn(b"/Subtype /Image", pdf_bytes)
        
        out_path.unlink()

    def test_symlink_escape(self):
        target = self.canonical_dirs[0] / "symlink_target.yaml"
        target.write_text("real content")
        self.snapshot[str(target)] = hashlib.sha256(b"real content").hexdigest()
        
        link = PROPOSALS_DIR / "symlink.yaml"
        if link.exists() or link.is_symlink():
            link.unlink()
            
        os.symlink(target, link)
        
        with self.assertRaises(PermissionError) as cm:
            run_phase1(self.fixture_path, "symlink.yaml")
        self.assertIn("is a symlink", str(cm.exception))
        
        link.unlink()
        target.unlink()
        del self.snapshot[str(target)]

    def test_hardlink_escape(self):
        target = self.canonical_dirs[0] / "hardlink_target.yaml"
        target.write_text("real content")
        self.snapshot[str(target)] = hashlib.sha256(b"real content").hexdigest()
        
        link = PROPOSALS_DIR / "hardlink.yaml"
        if link.exists():
            link.unlink()
            
        try:
            os.link(target, link)
        except OSError:
            target.unlink()
            del self.snapshot[str(target)]
            self.skipTest("Filesystem does not support hard links")
            
        with self.assertRaises((PermissionError, FileExistsError)):
            run_phase1(self.fixture_path, "hardlink.yaml")
            
        self.assertEqual(target.read_text(), "real content")
        
        link.unlink()
        target.unlink()
        del self.snapshot[str(target)]

    def test_existing_proposal_overwrite(self):
        out_path = PROPOSALS_DIR / "test_overwrite.proposal.yaml"
        out_path.write_text("pre-existing data")
        with self.assertRaises(FileExistsError):
            run_phase1(self.fixture_path, "test_overwrite.proposal.yaml")
        self.assertEqual(out_path.read_text(), "pre-existing data")
        out_path.unlink()

if __name__ == "__main__":
    unittest.main()
