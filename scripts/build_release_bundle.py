#!/usr/bin/env python3
"""Build the deterministic R6 release bundle (R6 increment 2).

release/R6-bundle-<content_hash12>/ containing:
  knowledge.jsonld          (canonical projection)
  knowledge.canonical.json  (canonical consumer export)
  stemma-shapes.ttl         (SHACL contract)
  SHA256SUMS.txt            (sorted, sha256 of the payload files)
  manifest.json             (versions, counts, payload hash, status)

status is PENDING-PUBLICATION until the Amendment-0001 identifier-base
decision exists (docs/decisions/r6-identifier-base.md, human:* record);
scripts/publication_gate.py enforces that mechanically.

Deterministic: no timestamps, no randomness; regenerated bundles are
byte-identical when inputs are unchanged.
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

PAYLOAD = [
    ("exports/knowledge.jsonld", "knowledge.jsonld"),
    ("exports/knowledge.canonical.json", "knowledge.canonical.json"),
    ("schema/projection/stemma-shapes.ttl", "stemma-shapes.ttl"),
]
DECISION_RECORD = ROOT / "docs/decisions/r6-identifier-base.md"


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(out_root: pathlib.Path | None = None) -> pathlib.Path:
    out_root = out_root or (ROOT / "release")
    sums = ""
    for src, _ in PAYLOAD:
        sums += f"{sha256(ROOT / src)}  {src.split('/')[-1]}\n"
    payload_hash = hashlib.sha256(sums.encode("utf-8")).hexdigest()
    name = f"R6-bundle-{payload_hash[:12]}"
    bundle = out_root / name
    if bundle.exists():
        shutil.rmtree(bundle)
    bundle.mkdir(parents=True)
    for src, dst in PAYLOAD:
        shutil.copyfile(ROOT / src, bundle / dst)
    (bundle / "SHA256SUMS.txt").write_text(sums, encoding="utf-8")
    proj = json.loads((ROOT / "exports/knowledge.jsonld").read_text(encoding="utf-8"))
    manifest = {
        "bundle": name,
        "release_phase": "R6 projection publication — candidate",
        "payload_hash_sha256": payload_hash,
        "entity_count": sum(1 for n in proj["@graph"] if isinstance(n.get("@type"), list)),
        "assertion_count": sum(1 for n in proj["@graph"] if n.get("@type") == "stemma:Assertion"),
        "schema_version": json.loads((ROOT / "exports/knowledge.canonical.json")
                                     .read_text(encoding="utf-8")).get("schema_version"),
        "identifier_base": "STAGED-WITHOUT-DECISION (stemma: URNs bound; external base NOT claimed)",
        "amendment_0001_gate": ("BLOCKED until docs/decisions/r6-identifier-base.md exists with"
                                " decided_by human:* + decision per ADR-0053 candidate set"
                                " (w3id | datacite-doi | ark-n2t | stemma-urn-only-as-declared)"),
        "export_version": json.loads((ROOT / "exports/knowledge.canonical.json")
                                     .read_text(encoding="utf-8")).get("export_version"),
        "shacl_contract": "stemma-shapes.ttl enforced by scripts/validate_shacl_shapes.py",
    }
    (bundle / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                                          encoding="utf-8")
    return bundle


def verify(bundle: pathlib.Path) -> int:
    errors = []
    if not bundle.exists():
        print(f"FAIL: bundle missing: {bundle}", file=sys.stderr)
        return 1
    sums = (bundle / "SHA256SUMS.txt").read_text(encoding="utf-8").splitlines()
    for line in sums:
        digest, _, fname = line.partition("  ")
        errors += [] if sha256(bundle / fname) == digest else [f"checksum mismatch: {fname}"]
    manifest = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    recomputed = hashlib.sha256(("".join(s + "\n" for s in sums)).encode("utf-8")).hexdigest()
    if manifest.get("payload_hash_sha256") != recomputed:
        errors.append("manifest/payload hash mismatch")
    if bundle.name != f"R6-bundle-{recomputed[:12]}":
        errors.append(f"bundle dir name does not match payload hash: {bundle.name}")
    if errors:
        print("FAIL: bundle verification:")
        for e in errors[:10]:
            print(f"  - {e}")
        return 1
    print(f"OK: bundle verified — {bundle.name}")
    return 0


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", metavar="BUNDLE_DIR", help="verify an existing bundle (checksums + manifest)")
    ap.add_argument("--print-name", action="store_true")
    args = ap.parse_args()
    if args.verify:
        sys.path.insert(0, str(pathlib.Path(args.verify).parent))
        return verify(ROOT / args.verify if not args.verify.startswith("/") else pathlib.Path(args.verify))
    bundle = build()
    print(f"OK: built {bundle.relative_to(ROOT)}")
    rc = verify(bundle)
    if args.print_name:
        print(bundle.name)  # last line on stdout: the bundle directory name
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
