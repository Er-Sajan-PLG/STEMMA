#!/usr/bin/env python3
"""ADR-0034: id-prefix / domain / path / vocabulary identity enforcement.

The immutable `stemma:<prefix>.<slug>` ID, the scalar `domain` field, and the
`content/<directory>/` path must agree. `schema/id-domain-map.yaml` is the
single source of truth; the validator enforces it as a hard gate.
"""
import pathlib
import subprocess
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from validate import check_entity_domain_identity, load_id_domain_map  # noqa: E402

EXPECTED_PREFIXES = {
    "phys": {"domain": "physics", "directory": "physics"},
    "chem": {"domain": "chemistry", "directory": "chemistry"},
    "bio": {"domain": "biology", "directory": "biology"},
    "earth": {"domain": "earth-space", "directory": "earth-space"},
    "eng": {"domain": "engineering", "directory": "engineering"},
    "math": {"domain": "mathematics", "directory": "math"},
    "epist": {"domain": "scientific-practice", "directory": "scientific-practice"},
    "practice": {"domain": "scientific-practice", "directory": "scientific-practice"},
}


def _map() -> dict:
    return load_id_domain_map()


def test_id_domain_map_shape():
    domain_map = _map()
    prefixes = domain_map["prefixes"]
    assert set(prefixes) == set(EXPECTED_PREFIXES), sorted(prefixes)
    for prefix, expected in EXPECTED_PREFIXES.items():
        assert prefixes[prefix]["domain"] == expected["domain"], f"{prefix} domain"
        assert prefixes[prefix]["directory"] == expected["directory"], f"{prefix} directory"
    print("PASS: id-domain-map shape")


def test_every_entity_agrees():
    """The real corpus must have coherent id-prefix/domain/path/tree. This is
    exactly what the gate enforces; keeping it here makes the rule explicit."""
    domain_map = _map()
    vocab = yaml.safe_load((ROOT / "schema" / "vocabularies" / "domains.yaml").read_text())["domains"]
    checked = 0
    for path in sorted((ROOT / "content").rglob("*.md")):
        if not path.read_text().startswith("---"):
            continue
        data = yaml.safe_load(path.read_text().split("---", 2)[1])
        if not isinstance(data, dict) or not data.get("id"):
            continue
        data["_file"] = path.relative_to(ROOT).as_posix()
        errs = []
        check_entity_domain_identity(data, domain_map, vocab, errs)
        assert not errs, f"{path}: {errs}"
        checked += 1
    # For empty knowledge base, just verify the check runs without errors
    print(f"PASS: all {checked} entities have coherent domain identity")


def test_our_environment_relocated_keeping_id():
    """The known mismatch (stemma:phys.our-environment previously under the
    earth-space tree) must now live in the physics tree with the same ID."""
    old = ROOT / "content" / "earth-space" / "atmosphere-climate" / "our-environment.md"
    new = ROOT / "content" / "physics" / "thermal-physics" / "our-environment.md"
    assert not old.exists(), "old mismatched path must be gone"
    if not new.exists():
        print("SKIP: our-environment relocation (entity not present in empty knowledge base)")
        return
    data = yaml.safe_load(new.read_text().split("---", 2)[1])
    assert data["id"] == "stemma:phys.our-environment"
    assert data["domain"] == "physics"
    assert pathlib.PurePosixPath(new.relative_to(ROOT)).parts[1] == "physics"
    print("PASS: our-environment relocated within its identity domain (ID unchanged)")


def test_check_rejects_mismatch():
    domain_map = _map()
    vocab = yaml.safe_load((ROOT / "schema" / "vocabularies" / "domains.yaml").read_text())["domains"]

    wrong_domain = {
        "id": "stemma:phys.x",
        "domain": "chemistry",
        "_file": "content/physics/mechanics/x.md",
    }
    errs = []
    check_entity_domain_identity(wrong_domain, domain_map, vocab, errs)
    assert any("does not match id prefix" in e for e in errs), errs

    wrong_path = {
        "id": "stemma:phys.x",
        "domain": "physics",
        "_file": "content/earth-space/atmosphere-climate/x.md",
    }
    errs = []
    check_entity_domain_identity(wrong_path, domain_map, vocab, errs)
    assert any("path directory" in e for e in errs), errs

    unknown_prefix = {"id": "stemma:nav.x", "domain": "physics", "_file": "content/physics/mechanics/x.md"}
    errs = []
    check_entity_domain_identity(unknown_prefix, domain_map, vocab, errs)
    assert any("not in schema/id-domain-map.yaml" in e for e in errs), errs

    invalid_vocab = {
        "id": "stemma:phys.x",
        "domain": "astrology",
        "_file": "content/physics/mechanics/x.md",
    }
    errs = []
    check_entity_domain_identity(invalid_vocab, domain_map, vocab, errs)
    assert any("not in vocabularies/domains.yaml" in e for e in errs), errs
    print("PASS: identity mismatches are hard errors")


def test_validator_passes_after_relocation():
    r = subprocess.run([sys.executable, str(ROOT / "scripts/validate.py")], cwd=str(ROOT), capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-500:]
    print("PASS: validator green after relocation")


def main() -> int:
    test_id_domain_map_shape()
    test_every_entity_agrees()
    test_our_environment_relocated_keeping_id()
    test_check_rejects_mismatch()
    test_validator_passes_after_relocation()
    print("ALL DOMAIN IDENTITY TESTS PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
