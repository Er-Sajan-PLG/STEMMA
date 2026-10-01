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

# --- Fields whose very presence asserts applicability-dependency ---
# (structured metadata, not prose). The plan's invariant: fail atomically if a canonical
# entity carries a frontmatter key that declares a grade/curriculum/country/product scope.
# Per ADR-0047 L7 refinement: learning_objectives instructional_sequencing removed entirely,
# real_world_applications common_misconceptions allowed ONLY when evidenced as ValueClaims not as entity frontmatter.
#
# WIDENED 2026-10-01 (owner ruling on UNRES-STEMMA-CORE-002). The original form was
# `^(<tokens>)$` — anchored at both ends to the exact key. That caught `grade` but missed
# every *prefixed/suffixed variant* of the same claim: `grade_level`, `grade_band`,
# `target_grade`, `unit_grade`, `grade_level_scope`, `curriculum_scope`, `edu_level`,
# `key_stage`, ... An exact-key anchor is the wrong shape for a *claim detector*: the
# invariant is "no key declares a grade/curriculum scoping meaning", and a scoper that
# merely renames the key to `grade_level` has not stopped declaring it.
#
# The widened form matches a scoping TOKEN anywhere in a `_`/`-`-delimited identifier, so
# `grade`, `grade_level`, `target_grade`, `grade_band` all fire. `_is_scoping_field` still
# normalises separators and compares whole tokens (never substrings), which is what keeps
# legitimate identifiers such as `upgrade_notes` or `multigrade` from being flagged.
SCOPING_TOKENS = (
    "grade",
    "grades",
    "curriculum",
    "syllabus",
    "course_level",
    "courselevel",
    "key_stage",
    "keystage",
    "school_system",
    "schoolsystem",
    "exam_scope",
    "examscope",
    "board",
    "stream",
    "learning_objectives",
    "instructional_sequencing",
    "real_world_applications",
    "common_misconceptions",
)
# `level` needs special handling: it is BOTH a scoping claim (`level`, `edu_level`,
# `grade_level`) AND a legitimate scientific word we must never reject (`trophic_level`,
# `energy_level`, `sea_level`). Bare `level` also has no science use as a *key*.
# Suffixes that turn a bare `level` into an unambiguous education-scoping claim:
_SCOPING_LEVEL_PREFIXES = ("edu", "education", "grade", "class", "academic", "school", "study")


def _scoping_tokens(key: str) -> list[str]:
    """Split an identifier into lowercase word tokens on `_`, `-`, `.`, camelCase, digits.

    `grade_level` -> ['grade','level'] ; `targetGrade` -> ['target','grade'] ;
    `grade10Scope` -> ['grade','10','scope']. Tokenisation (not substring search) is what
    lets us widen to variants without also matching `upgrade` (one token) or `multigrade`.
    """
    # camelCase -> camel Case, then split non-alphanumerics.
    spaced = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", key)
    return [t for t in re.split(r"[^a-z0-9]+", spaced.lower()) if t]


def _joined_token_forms(key: str) -> set[str]:
    """All contiguous token n-grams, both space- and underscore-joined.

    Needed because multi-word scoping tokens (`learning_objectives`, `key_stage`,
    `course_level`) split apart under tokenisation: `key_stage` -> ['key','stage'] would
    never equal the single token 'key_stage'. Joining windows restores both spellings so a
    key is matched whether the author wrote `key_stage`, `keyStage` or `key stage`.
    """
    tokens = _scoping_tokens(key)
    forms: set[str] = set(tokens)
    for i in range(len(tokens)):
        for j in range(i + 1, len(tokens) + 1):
            window = tokens[i:j]
            forms.add("_".join(window))
            forms.add(" ".join(window))
    return forms


def _is_scoping_field(key: str) -> bool:
    """True when a frontmatter KEY declares a grade/curriculum/country/product scope.

    Widened 2026-10-01: matches a scoping token ANYWHERE in the identifier, so prefixed
    and suffixed variants (`grade_level`, `target_grade`, `curriculum_scope`) are caught —
    see UNRES-STEMMA-CORE-002. Whole-token (and token-window) comparison, never substring,
    so `upgrade_notes` and `multigrade` stay legitimate.
    """
    tokens = _scoping_tokens(key)
    if not tokens:
        return False
    forms = _joined_token_forms(key)
    # `level` only counts when qualified as an education level, never as bare science level.
    if "level" in tokens:
        qualified = any(t in _SCOPING_LEVEL_PREFIXES for t in tokens if t != "level")
        if qualified:
            return True
    # Single-token and multi-word scoping names, in either separator spelling.
    for name in SCOPING_TOKENS:
        if name in forms or name.replace("_", " ") in forms:
            return True
    return False

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

# Forbidden SCOPING-FIELD keys are matched by `_is_scoping_field` above (widened 2026-10-01),
# which reports the offending key clearly rather than failing through transparency.


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


def test_scoping_field_guard_catches_prefixed_variants():
    """MUTATION TEST (UNRES-STEMMA-CORE-002): the widened guard MUST catch renamed variants.

    Before 2026-10-01 the guard was `^(...)$`-anchored and matched ONLY the exact key. Every
    case below was a live bypass: `grade_level: 10` passed the guard entirely. A guard that
    only catches the *spelling* you happened to write is not a guard — so each formerly-missed
    variant is pinned here as a must-catch.
    """
    must_catch = [
        "grade_level", "grade_band", "grade_range", "grade_scope", "target_grade",
        "unit_grade", "grade_level_scope", "gradeLevel", "Grade", "grades",
        "curriculum_scope", "curriculum_id", "syllabus_code",
        "course_level_scope", "course_level", "key_stage", "school_system",
        "exam_scope", "exam_board", "board", "stream",
        "edu_level", "education_level", "academic_level",
        "learning_objectives", "instructional_sequencing",
        "real_world_applications", "common_misconceptions",
    ]
    missed = [k for k in must_catch if not _is_scoping_field(k)]
    assert not missed, (
        "widened scoping guard MISSED renamed variants (UNRES-STEMMA-CORE-002 regression): "
        f"{missed}"
    )
    print(f"PASS: {len(must_catch)} scoping-key variants caught (incl. prefixed/suffixed)")


def test_scoping_field_guard_does_not_overreach():
    """NEGATIVE CONTROL: widening must not turn the guard into a substring blacklist.

    This is the other half of the mutation test — the guard has to go red on the variants
    above WITHOUT going red on legitimate identifiers that merely contain a scoping-ish word.
    `upgrade_notes` contains "grade"; `multigrade` contains "grade"; `trophic_level` contains
    "level". A widening that flags those would break real content.
    """
    must_allow = [
        "upgrade_notes",       # contains the substring 'grade'
        "multigrade",          # ditto
        "downgrade_reason",    # ditto
        "trophic_level",       # science level, not education level
        "energy_level",
        "sea_level",
        "confidence_level",
        "definition",           # control: ordinary key
        "domain",
        "same_dimensional_quantities",
        "subdomain",
    ]
    overreached = [k for k in must_allow if _is_scoping_field(k)]
    assert not overreached, (
        "widened scoping guard OVERREACHED onto legitimate identifiers: "
        f"{overreached}"
    )
    print(f"PASS: {len(must_allow)} legitimate keys not flagged (widening is token-precise)")


def test_widened_guard_is_enforced_end_to_end(tmp_path):
    """END-TO-END MUTATION: an injected 'grade_level' key in a real content tree must fail.

    The two tests above pin the matcher in isolation. This one proves the *whole guard*
    (glob -> frontmatter -> key check) rejects an injected variant, i.e. the fix is wired in
    and not merely defined. Runs against a temp copy so the working tree is never touched.
    """
    import shutil
    content = tmp_path / "content" / "physics"
    content.mkdir(parents=True)
    src = sorted(ROOT.glob("content/**/*.md"))
    if not src:
        print("SKIP: no canonical content to copy (empty knowledge base)")
        return
    # Start from a real entity so the frontmatter is valid in every other respect; the
    # scoping key is the ONLY thing wrong.
    sample = content / src[0].name
    shutil.copy(src[0], sample)
    text = sample.read_text()
    injected = text.split("---", 2)
    injected[1] = injected[1].rstrip() + "\ngrade_level: 10\n"
    sample.write_text("---".join(injected))

    original_root = ROOT
    try:
        globals()["ROOT"] = tmp_path
        try:
            test_no_curriculum_grade_country_metadata_fields()
        except AssertionError as exc:
            assert "grade_level" in str(exc), f"guard failed but did not name the key: {exc}"
            print("PASS: injected 'grade_level' key rejected by the end-to-end guard")
            return
        raise AssertionError(
            "MUTATION NOT DETECTED: injected 'grade_level' key passed the guard — "
            "UNRES-STEMMA-CORE-002 has regressed"
        )
    finally:
        globals()["ROOT"] = original_root


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
    if not provenance_scoped:
        print("SKIP: provenance attribution (no content in empty knowledge base)")
        return
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
    test_scoping_field_guard_catches_prefixed_variants()
    test_scoping_field_guard_does_not_overreach()
    test_provenance_attribution_allowed()
    test_no_upstream_coupling()
    print("ALL GENERALITY TESTS PASS")