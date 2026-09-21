# CONTRIBUTING — STEMMA

Thank you for contributing to STEMMA, an open, structured, reusable STEM
knowledge foundation. Every contribution keeps the foundation
**curriculum-agnostic, product-independent, identity-stable, and honest about
provenance**.

Start here: [docs/VISION.md](docs/VISION.md) ·
[docs/GOVERNANCE.md](docs/GOVERNANCE.md) ·
[docs/CONTRIBUTING.md](docs/CONTRIBUTING.md) (detailed guide).

## The five ground rules

1. **Canonical knowledge lives only in `content/`, `connections/`, and
   `sources/`.** Everything under `exports/` and `reports/` is derived —
   regenerate, never hand-edit.
2. **No curriculum, grade, course, country, or product appears in canonical
   data.** Scientific terminology is welcome; applicability scoping is not.
   (Machine-checked; `tests/curation/test_generality.py`.)
3. **IDs are a stability contract.** `stemma:` identifiers are never reused
   or reassigned; assertion triples are immutable — correct via supersession,
   never by editing (see `docs/RELATIONSHIP-SPECIFICATION.md` §3).
4. **Relationships are objects.** Add relationships as connection files; the
   relation must exist in the registry (or arrive with a promotion ADR).
5. **AI output is a draft.** Review status only advances through the human
   curation protocol with a registered reviewer.

## Workflow

```bash
# 1. verify everything (the same chain CI runs)
python3 scripts/verify_all.py

# 2. after changing canonical content, regenerate derived artifacts
python3 scripts/validate.py        # exports/knowledge.json + validation report
python3 scripts/export_review_aware.py && python3 scripts/graph_analysis.py

# 3. explorer consumers: re-verify the projection
npm --prefix explorer run verify
```

- Branches: `feat|fix|docs|chore|ci|task|refactor|test/<slug>`; Conventional
  Commits (CI-enforced).
- Derived artifacts are committed fresh in the same change (CI fails on a
  stale export).
- New provenance agents, relation uses, or extension dimensions: register in
  the same PR (`schema/*-registry.yaml`).
- Anything touching identity, schemas, relation semantics, or the export
  contract requires an ADR — see `docs/GOVERNANCE.md` §3–4 for the decision
  process and the human-review gates.

## Adding knowledge

- **Entity**: `content/<domain>/<subdomain>/<slug>.md`, YAML frontmatter per
  `docs/SCHEMA-SPECIFICATION.md` §3, `status: draft`, honest provenance.
- **Connection**: `connections/conn.NNNNNN.yaml` (next free number),
  registry-conformant relation, context + evidence + provenance per the
  schema.
- **Source**: `sources/src.<slug>.yaml` when evidence should cite a record.
- Then run the chain. A failing gate message names the rule and the file.

## Reviewing knowledge

Human review is the authority track — see
[docs/CURATION-PROTOCOL.md](docs/CURATION-PROTOCOL.md) for states,
transitions, evidence standards per relation family, and the campaign
worksheet workflow. AI agents may propose and prepare; they never decide.

## Licensing

By contributing you agree your content contributions are licensed under
**CC BY 4.0** (knowledge content) and code contributions under **MIT**
(`LICENSE`, `LICENSE-CODE`; ADR-0001).
