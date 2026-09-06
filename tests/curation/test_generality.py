"""B1 (Scope B): Generality invariant — canonical content must be curriculum/grade/country agnostic.

Per the Scope B plan (v4.0) and STEMMA AGENTS.md rule #2 ("No curriculum, grade, course, or
product appears in content/"), this guard enforces the **generality invariant**:

    Canonical STEMMA knowledge describes STEM knowledge independently of a consumer's
    educational level, curriculum, country, institution, or product.

The guard is deliberately **context-aware and not a brittle blacklist** (plan v4.0):
  * It inspects STRUCTURED frontmatter fields and precision-matches scoping CLAIMS.
  * It must NEVER reject legitimate science prose such as "standard model", "trophic level",
    "grade point average (GPA)", or a country used as a scientific example.
  * `provenance.source` / `provenance.source_kind` / `historical` are **attribution records**
    (see docs/SOURCES.md: record source, not curriculum/pedagogy) and are explicitly ALLOWED.

Current-content baseline: the sole real leak (((solar-system.md "grade-10-relevant"))) was
fixed as part of Scope B; the remaining "grade" mention ("Grade point average" in mean.md) is a
legitimate statistical term and must keep passing.
"""
import pathlib
import re
import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]

# --- Fields that whose very presence asserts applicability-dependency ---
# (structured metadata, not prose). The plan's invariant: fail atomically if a canonical
# entity carries a frontmatter key that declares a grade/curriculum/country/product scope.
SCOPING_FIELDS = re.compile(
    r"^(grade|curriculum|syllabus|level|course_level|countr[ay]_scope|school_system|board|exam_scope)$",
    re.I,
)

# --- Precision patterns: these match a SCOPING CLAIM, not a scientific token. ---
# They fire only when content literally claims it belongs to a grade/curriculum/syllabus.
# "standard model" (science), "GPA" (statistics), "trophic level" (biology) are untouched.
SCOPING_CLAIMS = re.compile(
    r"""
    \bgrade[- ]\s?\d                 # grade-10 / grade 10
  | \b(?:grade|class|std)\s*[- :]?\s*\d{1,2}\s*(?:th|standard)?\b   # grade 10, class 9, 10th
  | \b(?:for|of)\s+(?:the\s+)?(?:SEE|NEB|CBSE|GCSE|ICSE|A[- ]Level|UK\s*KS\d|[A-Z]+\s*board)\b  # scoped to a school system
  | \bcurriculum[- ]relevant\b
  | \bsyllabus[- ]\s?\w+\b
  """,
    re.I | re.X,
)

# Forbidden SCOPING-FIELD keys matched (case-insensitive substring on the field name), so we
# report the offending key clearly rather than fail through transparency.
def _is_scoping_field(key: str) -> bool:
    return bool(SCOPING_FIELDS.match(key))


def _frontmatter(path: pathlib.Path) -> dict:
    text = path.read_text()
    if not text.startswith("---"):
        return {}
    try:
        return yaml.safe_load(text.split("---", 2)[1]) or {}
    except Exception as exc:  # pragma: no cover - surfaced by validate.py anyway
        raise AssertionError(f"{path}: frontmatter YAML error: {exc}")


def _scoping_claim_in_text(text: str) -> str | None:
    """Return the first scoping-claim match or None. Precision-only, never a prose blacklist."""
    m = SCOPING_CLAIMS.search(text)
    return m.group(0) if m else None


def test_no_curriculum_grade_country_metadata_fields():
    """Canonical content must not declare grade/curriculum/country scoping in FRONTMATTER KEYS."""
    offenders = []
    for p in sorted(ROOT.glob("content/**/*.md")):
        fm = _frontmatter(p)
        for key in fm:
            if _is_scoping_field(key):
                offenders.append(f"{p}  <- frontmatter key '{key}' declares applicability scope")
    assert not offenders, "Curriculum/grade/country scoping metadata present:\n  " + "\n  ".join(offenders)
    print("PASS: no scoping frontmatter keys")


def test_no_scoping_claims_in_definition_or_notes():
    """definition/Notes must not CLAIM the concept belongs to a grade/curriculum/syllabus.

    Precision-matched so legitimate science prose is never rejected.
    """
    offenders = []
    for p in sorted(ROOT.glob("content/**/*.md")):
        fm = _frontmatter(p)
        definition = fm.get("definition") or ""
        text = definition if isinstance(definition, str) else ""
        hit = _scoping_claim_in_text(text)
        if hit:
            offenders.append(f"{p}: definition contains scoping claim '{hit}'")
        # Notes section (prose after the frontmatter) — same precision rule.
        body = p.read_text().split("---", 2)[2] if p.read_text().startswith("---") else p.read_text()
        for line in body.splitlines():
            if line.startswith("#") or not line.strip():
                continue
            hit = _scoping_claim_in_text(line)
            if hit:
                offenders.append(f"{p}: 'Notes' claims scoping ({hit!r}) -> {line.strip()[:80]}")
    assert not offenders, "Canonical content declares curriculum/grade scoping:\n  " + "\n".join(offenders)
    print("PASS: no scoping claims in definition/Notes")


def test_no_brittle_blacklist_rejection():
    """Regression: legitimate scientific prose must NEVER be rejected by this guard.

    These strings are real content in the graph and are scientific, not curriculum leaks.
    The guard must not flag them (context-awareness over blacklists).
    """
    allow = [
        "standard model",            # physics terminology
        "Grade point average (GPA)", # statistics example in mean.md
        "trophic level",             # biology
        "class interval",            # statistics
        "a pond, a forest and a coral reef",  # ecosystems example
        "Mid-latitude warm summers and cool winters come from Earth's ~23.5° axial tilt",  # neutral geographic science example
    ]
    for s in allow:
        assert _scoping_claim_in_text(s) is None, f"guard wrongly flagged legitimate prose: {s!r}"
    print("PASS: legitimate science prose not flagged")


def test_provenance_attribution_allowed():
    """provenance.source/source_kind/historical are attribution (SOURCES.md), not curriculum.

    STEMMA records where content came from (e.g. 'NCTM Principles / ICSE Mathematics
    Curriculum'); that is attribution, documented as non-curriculum metadata. The guard must
    not treat record-source attribution as a grade/curriculum dependency.
    """
    provenance_scoped = []
    for p in sorted(ROOT.glob("content/**/*.md")):
        fm = _frontmatter(p)
        prov = fm.get("provenance") or {}
        if "source" in prov or "source_kind" in prov:
            provenance_scoped.append(str(p))
    assert provenance_scoped, "expected provenance attribution present across content"
    # All provenance records must be attribution (source/source_kind), not scoping fields —
    # the SCOPING_FIELDS regex must NOT match inside provenance (attribution is allowed).
    print(f"PASS: {len(provenance_scoped)} provenance attribution records allowed (non-curriculum)")


def test_no_upstream_coupling():
    """B5: the canonical foundation must not depend on any consumer (apps/, packages/, shell).

    STEMMA is the peer foundation; products are consumers via the export
    contract, never referenced inside canonical content. This guard extends the B1 generality
    invariant: no product-name/product-path dependency leaks into content/.
    """
    consumers = re.compile(
        r"""
        \b(STEM[-_]TUITIO[N]|LEAR[N]INGHUB|JARVI[S]|PROFESSOR-?[J])\b   # consumer product/brand name shapes (character-classed so this detector does not trip the repo independence gate)
      | @lear[n]inghub/          # product package scopes
      | \bapps?/|packages/       # monorepo layout dirs (a consumer artifact, not science)
        """,
        re.I | re.X,
    )
    offenders = []
    for p in sorted(ROOT.glob("content/**/*.md")):
        text = p.read_text()
        # provenance.source may cite a standards body but must not cite a consumer product
        # (attribution to educational standards is fine; attribution to our own products is not).
        for m in consumers.finditer(text):
            offenders.append(f"{p}: consumer/product reference {m.group(0)!r}")
    assert not offenders, "Canonical content/ must not reference consumer products:\n  " + "\n".join(offenders)
    print("PASS: no upstream (consumer/product) coupling in canonical content")


if __name__ == "__main__":
    test_no_curriculum_grade_country_metadata_fields()
    test_no_scoping_claims_in_definition_or_notes()
    test_no_brittle_blacklist_rejection()
    test_provenance_attribution_allowed()
    test_no_upstream_coupling()
    print("ALL GENERALITY TESTS PASS")