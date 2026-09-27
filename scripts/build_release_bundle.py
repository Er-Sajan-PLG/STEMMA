#!/usr/bin/env python3
"""Build the deterministic release bundle (R6 increment 2; distribution item 3).

release/R6-bundle-<payload_hash12>/ (staging, git-ignored) containing:
  knowledge.json              (full export, all statuses; consumers pick a tier)
  knowledge.hash.json         (small pointer: sha256 + content_hash of knowledge.json)
  knowledge.<consumer>.json   (one per schema/consumer-registry.yaml consumer)
  connections.canonical.json  (review-aware view: canonical connections only, NOT an export;
                               shipped before v3.0.0-rc2 as knowledge.canonical.json)
  knowledge.jsonld            (canonical projection)
  stemma-shapes.ttl           (SHACL contract)
  SHA256SUMS.txt              (sorted, sha256 of the payload files)
  manifest.json               (versions, content_hash, per-file sha256, license, status)

Published by .github/workflows/release.yml as GitHub Release assets with a
Sigstore build attestation; the owner's GPG signature (SHA256SUMS.sig, via
scripts/sign_release_bundle.py) stays a manual, local step.

Never shipped: embeddings / vector stores / placeholder vectors (ADR-0054) —
the builder refuses them, and refuses consumer bundles that are stale relative
to knowledge.json.

status is PENDING-PUBLICATION until the Amendment-0001 identifier-base
decision exists (docs/decisions/r6-identifier-base.md, human:* record);
scripts/publication_gate.py enforces that mechanically.

Deterministic: no wall clock, no randomness. manifest.generated_at is the
source commit time (SOURCE_DATE_EPOCH if set, else `git log -1 %ct`), so a
rebuild of the same commit is byte-identical.
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import shutil
import subprocess
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent

BASE_EXPORT = "exports/knowledge.json"
STATIC_PAYLOAD = [
    (BASE_EXPORT, "knowledge.json"),
    ("exports/knowledge.canonical.json", "connections.canonical.json"),
    ("exports/knowledge.jsonld", "knowledge.jsonld"),
    ("schema/projection/stemma-shapes.ttl", "stemma-shapes.ttl"),
]
HASH_POINTER = "knowledge.hash.json"
DECISION_RECORD = ROOT / "docs/decisions/r6-identifier-base.md"
LICENSE_ID = "CC-BY-4.0"
LICENSE_URL = "https://creativecommons.org/licenses/by/4.0/"
# Derived embeddings are model-specific and a consumer concern (ADR-0054).
FORBIDDEN_NAME_PARTS = ("embedding", "vector")


class BundleError(RuntimeError):
    pass


def _read_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def consumer_payload() -> list[tuple[str, str]]:
    """One bundle per consumer in schema/consumer-registry.yaml (sorted)."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import export_consumers as _ec  # noqa: E402  (aliased: no shadowing)
    out = []
    for cid in sorted(_ec.load_registry()):
        rel = f"exports/consumers/{cid}/knowledge.{cid}.json"
        if not (ROOT / rel).exists():
            raise BundleError(f"missing consumer bundle {rel} (run scripts/export_consumers.py --all)")
        out.append((rel, f"knowledge.{cid}.json"))
    return out


def payload() -> list[tuple[str, str]]:
    items = STATIC_PAYLOAD + consumer_payload()
    for src, dst in items:
        guard_payload(src, dst)
    return items


def guard_payload(src: str, dst: str) -> None:
    """Refuse embeddings/vector stores/placeholders and stale consumer bundles."""
    lowered = (src + " " + dst).lower()
    if any(part in lowered for part in FORBIDDEN_NAME_PARTS):
        raise BundleError(f"refusing to ship derived embeddings/vector data: {src}")
    if not dst.endswith(".json"):
        return
    data = _read_json(src)
    if dst.endswith(".json") and not dst.endswith(".jsonld"):
        text = json.dumps(data)
        if '"stemma:placeholder-hash"' in text or '"placeholder": true' in text:
            raise BundleError(f"refusing to ship placeholder vectors: {src}")
    if src.startswith("exports/consumers/"):
        base = _read_json(BASE_EXPORT)
        for key in ("export_version", "schema_version"):
            if data.get(key) != base.get(key):
                raise BundleError(f"stale consumer bundle {src}: {key} {data.get(key)!r} != "
                                  f"base {base.get(key)!r} (run scripts/export_consumers.py --all)")


def file_kind(name: str) -> str:
    """What each asset is, so consumers load the right thing. Only `export`
    files are complete exports that load with `python -m stemma_adapter validate`."""
    if name == "knowledge.json" or (name.startswith("knowledge.") and name.endswith(".json")
                                    and name.split(".")[1] in _consumer_ids()):
        return "export"
    return {
        "connections.canonical.json": "connections-view",  # review-aware view: connections only, no entities
        "knowledge.hash.json": "hash-pointer",
        "knowledge.jsonld": "jsonld-projection",
        "stemma-shapes.ttl": "shacl-shapes",
    }.get(name, "other")


def _consumer_ids() -> set[str]:
    return {dst.split(".")[1] for _src, dst in consumer_payload()}


def file_entry(path: pathlib.Path, digest: str) -> dict:
    """sha256 + size, plus counts for JSON exports (the legacy top-level
    entity_count/assertion_count describe the canonical JSON-LD projection)."""
    entry: dict = {"sha256": digest, "bytes": path.stat().st_size, "kind": file_kind(path.name)}
    if path.suffix == ".json":
        data = json.loads(path.read_text(encoding="utf-8"))
        for key in ("entity_count", "connection_count", "source_count"):
            if isinstance(data.get(key), int):
                entry[key] = data[key]
    return entry


def source_time() -> tuple[str | None, str | None]:
    """(ISO commit time, commit sha): deterministic per commit, never the wall clock."""
    sha = None
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True,
                             text=True, check=True).stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        pass
    epoch = os.environ.get("SOURCE_DATE_EPOCH")
    if not epoch:
        try:
            epoch = subprocess.run(["git", "log", "-1", "--format=%ct"], cwd=ROOT, capture_output=True,
                                   text=True, check=True).stdout.strip()
        except (OSError, subprocess.CalledProcessError):
            epoch = None
    if not epoch:
        return None, sha
    return datetime.fromtimestamp(int(epoch), timezone.utc).isoformat().replace("+00:00", "Z"), sha


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(out_root: pathlib.Path | None = None, release_tag: str | None = None) -> pathlib.Path:
    out_root = out_root or (ROOT / "release")
    items = payload()
    base = _read_json(BASE_EXPORT)
    pointer = {
        "file": "knowledge.json",
        "sha256": sha256(ROOT / BASE_EXPORT),
        "content_hash": base.get("content_hash"),
        "export_version": base.get("export_version"),
        "schema_version": base.get("schema_version"),
    }
    pointer_bytes = (json.dumps(pointer, indent=2, sort_keys=True) + "\n").encode("utf-8")
    digests = {dst: sha256(ROOT / src) for src, dst in items}
    digests[HASH_POINTER] = hashlib.sha256(pointer_bytes).hexdigest()
    for n in digests:  # `knowledge.*.json` promises a loadable export (only the pointer is exempt)
        if n.startswith("knowledge.") and n.endswith(".json") and n != HASH_POINTER and file_kind(n) != "export":
            raise BundleError(f"{n} is named like an export but is {file_kind(n)!r}; rename it")
    sums = "".join(f"{digests[name]}  {name}\n" for name in sorted(digests))
    payload_hash = hashlib.sha256(sums.encode("utf-8")).hexdigest()
    name = f"R6-bundle-{payload_hash[:12]}"
    bundle = out_root / name
    if bundle.exists():
        shutil.rmtree(bundle)
    bundle.mkdir(parents=True)
    for src, dst in items:
        shutil.copyfile(ROOT / src, bundle / dst)
    (bundle / HASH_POINTER).write_bytes(pointer_bytes)
    (bundle / "SHA256SUMS.txt").write_text(sums, encoding="utf-8")
    generated_at, commit = source_time()
    decided = DECISION_RECORD.exists()
    proj = json.loads((ROOT / "exports/knowledge.jsonld").read_text(encoding="utf-8"))
    manifest = {
        "bundle": name,
        "release_tag": release_tag,
        "release_status": ("PUBLISHABLE (identifier-base decision recorded)" if decided else
                           "PENDING-PUBLICATION (identifier-base decision not recorded; "
                           "pre-releases only — scripts/publication_gate.py)"),
        "export_version": base.get("export_version"),
        "schema_version": base.get("schema_version"),
        "content_hash": base.get("content_hash"),
        "generated_at": generated_at,
        "source_commit": commit,
        "license": LICENSE_ID,
        "license_url": LICENSE_URL,
        "files": {n: file_entry(bundle / n, digests[n]) for n in sorted(digests)},
        "release_phase": "R6 projection publication — candidate",
        "payload_hash_sha256": payload_hash,
        "entity_count": sum(1 for n in proj["@graph"] if isinstance(n.get("@type"), list)),
        "assertion_count": sum(1 for n in proj["@graph"] if n.get("@type") == "stemma:Assertion"),
        "identifier_base": "STAGED-WITHOUT-DECISION (stemma: URNs bound; external base NOT claimed)",
        "amendment_0001_gate": ("BLOCKED until docs/decisions/r6-identifier-base.md exists with"
                                " decided_by human:* + decision per ADR-0053 candidate set"
                                " (w3id | datacite-doi | ark-n2t | stemma-urn-only-as-declared)"),
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
    listed = {line.partition("  ")[2] for line in sums}
    for fname, meta in (manifest.get("files") or {}).items():
        if fname not in listed:
            errors.append(f"manifest lists {fname} not in SHA256SUMS.txt")
        elif (bundle / fname).exists() and sha256(bundle / fname) != meta.get("sha256"):
            errors.append(f"manifest sha256 mismatch: {fname}")
    for f in bundle.iterdir():
        if any(part in f.name.lower() for part in FORBIDDEN_NAME_PARTS):
            errors.append(f"forbidden derived artifact in bundle: {f.name}")
        if f.is_file() and f.name not in listed | {"SHA256SUMS.txt", "manifest.json", "SHA256SUMS.sig"}:
            errors.append(f"unlisted file in bundle: {f.name}")
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
    ap.add_argument("--out", metavar="DIR", help="output root (default: release/, git-ignored staging)")
    ap.add_argument("--release-tag", metavar="TAG", help="record the git tag being released in manifest.json")
    args = ap.parse_args()
    if args.verify:
        sys.path.insert(0, str(pathlib.Path(args.verify).parent))
        return verify(ROOT / args.verify if not args.verify.startswith("/") else pathlib.Path(args.verify))
    out_root = pathlib.Path(args.out).resolve() if args.out else None
    try:
        bundle = build(out_root, release_tag=args.release_tag)
    except BundleError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    print(f"OK: built {bundle.relative_to(ROOT) if bundle.is_relative_to(ROOT) else bundle}")
    rc = verify(bundle)
    if args.print_name:
        print(bundle.name)  # last line on stdout: the bundle directory name
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
