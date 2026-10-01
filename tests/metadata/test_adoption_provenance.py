"""Adoption provenance semantics (ADR-0056 / REQ-STEMMA-EXP-002 criterion 4).

Verifies the optional `adopted_from` field: the provenance record an entity MUST
carry when it adopts or re-identifies a term originating elsewhere.

Why this field exists: `external_ids` anchors IDENTITY (a QID says which external
thing this is) but records nothing about the act of adopting it. `provenance`
records where the *content* came from. Neither answers "was this term adopted,
from what, and how strongly matched?" — which is exactly what OBO Foundry
Principle 8 requires (`rdfs:isDefinedBy` when a term is adopted under a new
identifier). This suite pins the shape and proves the validator enforces it.

Design note (mutation discipline): a schema field that only *documents* an
intent is not an enforcement. So alongside the positive shape checks this file
contains negative cases that feed malformed records through the SAME validator
the gate uses, and assert each is rejected. If the validator stops rejecting
them, these tests go red.
"""
import copy
import importlib.util
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]

ADOPTION_RELATIONS = {
    "exact_match",
    "close_match",
    "broad_match",
    "narrow_match",
    "reidentification",
    "merge",
}


def _load_validator():
    """Import scripts/validate.py by path (it is a script, not an installed module)."""
    spec = importlib.util.spec_from_file_location("stemma_validate", ROOT / "scripts" / "validate.py")
    assert spec and spec.loader, "cannot load scripts/validate.py"
    module = importlib.util.module_from_spec(spec)
    sys.modules["stemma_validate"] = module
    spec.loader.exec_module(module)
    return module


def _entities():
    for p in (ROOT / "content").rglob("*.md"):
        text = p.read_text(encoding="utf-8")
        if not text.startswith("---"):
            continue
        try:
            d = yaml.safe_load(text.split("---", 2)[1])
        except Exception:
            continue
        if isinstance(d, dict) and d.get("id"):
            d["_file"] = str(p.relative_to(ROOT))
            yield d


# --- Positive: the field is well-shaped wherever it appears ------------------

def test_adopted_from_shape_valid():
    """Every present `adopted_from` block must satisfy the contract shape."""
    invalid = []
    for d in _entities():
        a = d.get("adopted_from")
        if a is None:
            continue
        if not isinstance(a, dict):
            invalid.append(f"{d['_file']}: adopted_from must be an object")
            continue
        if not isinstance(a.get("external_id"), str) or not a.get("external_id", "").strip():
            invalid.append(f"{d['_file']}: adopted_from.external_id required (non-empty string)")
        if a.get("relation") not in ADOPTION_RELATIONS:
            invalid.append(
                f"{d['_file']}: adopted_from.relation {a.get('relation')!r} not in {sorted(ADOPTION_RELATIONS)}"
            )
        for key in ("note", "adopted_at"):
            if a.get(key) is not None and not isinstance(a.get(key), str):
                invalid.append(f"{d['_file']}: adopted_from.{key} must be a string")
        if a.get("authority") is not None and a.get("authority") not in {"internal", "delegated"}:
            invalid.append(f"{d['_file']}: adopted_from.authority must be internal|delegated")
    assert not invalid, "\n".join(invalid)
    print("PASS: all adopted_from blocks well-formed")


def test_schema_declares_adopted_from():
    """The concept AND export schemas must both declare the field.

    Criterion 4 is an EXPORT criterion — a field enforced only in the canonical
    schema but never projected into exports would satisfy the letter of the
    canonical contract while failing consumers. Both are asserted deliberately.
    """
    import json

    concept = json.loads((ROOT / "schema" / "concept.schema.json").read_text())
    export = json.loads((ROOT / "schema" / "export.schema.json").read_text())
    assert "adopted_from" in concept["properties"], "concept.schema.json must declare adopted_from"
    entity_props = export["properties"]["entities"]["items"]["properties"]
    assert "adopted_from" in entity_props, "export.schema.json entities[] must declare adopted_from"
    # Both must be closed so an unknown adoption key cannot smuggle through.
    assert concept["properties"]["adopted_from"]["additionalProperties"] is False
    assert entity_props["adopted_from"]["additionalProperties"] is False
    print("PASS: adopted_from declared in concept + export schemas (closed shape)")


# --- Negative: the validator must actually REJECT malformed records ----------

def test_validator_rejects_malformed_adopted_from():
    """MUTATION: feed each malformed variant through the real validator.

    If any of these is accepted, the field is decorative — the test fails.
    """
    validator = _load_validator()
    base = {
        "id": "stemma:phys.metre",
        "type": "unit",
        "name": "metre",
        "domain": "physics",
        "status": "canonical",
        "definition": "x",
        "provenance": {"ai_drafted": False},
        "same_dimensional_quantities": ["length"],
    }
    malformed = [
        {"external_id": "wd:Q11402"},                                # missing relation
        {"relation": "exact_match"},                                  # missing external_id
        {"external_id": "", "relation": "exact_match"},               # empty external_id
        {"external_id": "wd:Q11402", "relation": "sort_of_ish"},      # relation outside enum
        {"external_id": "wd:Q11402", "relation": None},               # null relation
        {"external_id": "wd:Q11402", "relation": "exact_match", "authority": "god"},  # bad authority
        {"external_id": "wd:Q11402", "relation": "exact_match", "note": 5},           # note not a string
        {"external_id": "wd:Q11402", "relation": "exact_match", "unknown_key": 1},    # unknown key (schema-level)
        "not-an-object",                                               # wrong type entirely
    ]
    for bad in malformed:
        entity = copy.deepcopy(base)
        entity["adopted_from"] = bad
        errors: list[str] = []
        validator.check_adopted_from(entity, errors, "probe:")
        assert errors, f"validator ACCEPTED malformed adopted_from: {bad!r} — field is decorative"
    print(f"PASS: validator rejects {len(malformed)} malformed adopted_from variants")


def test_validator_accepts_wellformed_adopted_from():
    """NEGATIVE CONTROL: the validator must not reject valid records (no over-reach)."""
    validator = _load_validator()
    base = {"id": "stemma:phys.metre", "type": "unit"}
    good = [
        {"external_id": "wd:Q11402", "relation": "exact_match"},
        {"external_id": "obo:UO_0000008", "relation": "close_match", "authority": "internal"},
        {"external_id": "stemma:phys.metre-legacy", "relation": "reidentification",
         "note": "renamed after the 2019 redefinition", "adopted_at": "2026-10-01"},
        {"external_id": "wd:Q1", "relation": "merge", "source_external_ids": {"doi": "10.1000/x"}},
    ]
    for rec in good:
        entity = copy.deepcopy(base)
        entity["adopted_from"] = rec
        errors: list[str] = []
        validator.check_adopted_from(entity, errors, "probe:")
        assert not errors, f"validator WRONGLY rejected valid adopted_from {rec!r}: {errors}"
    # Absent field is the normal case and must stay silent.
    errors = []
    validator.check_adopted_from(base, errors, "probe:")
    assert not errors, "validator must not error when adopted_from is absent"
    print(f"PASS: validator accepts {len(good)} valid adopted_from records + absent")


def test_absent_adopted_from_is_not_fabricated():
    """Non-adoption is the majority case; absence must never be an error.

    Mirrors the ADR-0018 rule for `historical`: an absent record means "no
    adoption to report", never "unknown, fill it in". A guard that demanded the
    field everywhere would force fabricated provenance.
    """
    with_field = 0
    total = 0
    for d in _entities():
        total += 1
        if d.get("adopted_from") is not None:
            with_field += 1
    print(f"PASS: {total - with_field}/{total} entities carry no adopted_from (absence is legal)")


if __name__ == "__main__":
    test_adopted_from_shape_valid()
    test_schema_declares_adopted_from()
    test_validator_rejects_malformed_adopted_from()
    test_validator_accepts_wellformed_adopted_from()
    test_absent_adopted_from_is_not_fabricated()
    print("ALL ADOPTION-PROVENANCE TESTS PASS")
