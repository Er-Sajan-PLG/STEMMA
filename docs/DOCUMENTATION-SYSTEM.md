# DOCUMENTATION-SYSTEM — docs sync, impact & enforcement

> Core invariant: **repository state = source + tests + documentation + generated
> artifacts, all mutually consistent.** A relevant change must surface its
> documentation impact and fail locally and in CI when the contract is violated.
> Scope: tailored to this repository against the 14-category / 220-artifact
> taxonomy (`docs/meta/doc-taxonomy.yaml`) — many enterprise artifacts are
> deliberately N/A for a public, file-based, sole-owner knowledge foundation,
> and each N/T decision is recorded and reviewable (not implicit).

## Architecture (layered, not monolithic)

```
docs/docs-contract.yaml          ownership + sources + generators + checks (declarative)
docs/meta/doc-taxonomy.yaml      220-artifact census with per-artifact disposition (audit)
        │
        ▼
scripts/docs.py                  engine — 5 layers, each independently callable
  ├─ model     load contract/taxonomy; match_source; dependency graph
  ├─ impact    changed files → affected docs (direct + transitive + unmapped report)
  ├─ sync      run declared generators (write mode) — idempotent by construction
  ├─ validate  invariants: contract integrity, link resolution, generated freshness
  └─ check     validate + declared external checks = CI-equivalent gate
```

## Commands (single canonical command set, same locally and in CI)

| Command | Mutates? | Purpose |
|---|---|---|
| `python3 scripts/docs.py impact` | No | Explain what is affected by the current diff (`--all`, `--paths F…`, `--base REF`) |
| `python3 scripts/docs.py sync` | Yes | Run generators: README status block + coverage census |
| `python3 scripts/docs.py validate` | No | Contract invariants + broken links + generated drift |
| `python3 scripts/docs.py check` | No | **CI-equivalent gate**: validate + docs-consistency + independence + recovery-validator |
| `python3 scripts/docs.py coverage [--write\|--check]` | Flag | Render the taxonomy census deterministically |

CI pattern (`.github/workflows/ci.yml`, `verify-docs` job):

```bash
python3 scripts/docs.py sync
git diff --exit-code
python3 scripts/docs.py check
```

## Source-of-truth model (ownership kinds)

| Kind | Meaning | Examples |
|---|---|---|
| CANONICAL | human-owned prose, source of truth | docs/ARCHITECTURE-V2.md, spec/REQUIREMENTS.md |
| GENERATED | produced by a declared generator, drift-gated | README status block, docs/meta/documentation-coverage.md |
| DERIVED | produced by the knowledge pipeline (own gate: verify-knowledge-base freshness) | exports/, reports/ |
| REFERENCE | external-standard or machine data | schema/*.yaml registries |
| INDEX | navigation only | docs/README.md, docs/decisions/README.md |

Machine-owned facts are generated, never hand-copied: canonical counts
(`scripts/status_truth.py`), taxonomy census (`docs.py coverage`), export &
versions (`schema/VERSION.yaml` single source).

## Impact detection (deterministic, conservative)

Direct: changed file matches an artifact's `sources` prefix/glob, or the file *is*
the artifact. Transitive: closure over `depends_on` edges (e.g. `PROGRESS.md →
docs/ROADMAP.md`). Unmapped changed files are reported explicitly and validation
runs fully anyway — **false positives over false negatives**. Textual proximity
is never used; the graph is declared in the contract.

Example:

```bash
$ python3 scripts/docs.py impact --paths schema/api.yaml
  - docs/API.md                    [schema/api.yaml]      # §5 API reference
  - docs/SCHEMA-SPECIFICATION.md   [schema/api.yaml]      # §2 — cross-category
  - docs/VISION.md                 [schema/api.yaml]
  - PROGRESS.md                    (transitive via depends_on)
  - docs/ROADMAP.md                (transitive)
```

## Adding a new obligation (how-to)

1. Create/update the doc; **classify** it in `docs/docs-contract.yaml`
   (path, category, tier, kind, `sources` it describes).
2. If the fact is machine-knowable, add a generator instead of prose (see
   `generators:` block; outputs + marker).
3. If it encodes an external standard artifact, record disposition in
   `docs/meta/doc-taxonomy.yaml` (status + note).
4. Run `python3 scripts/docs.py sync && python3 scripts/docs.py check`.
5. New top-level `docs/*.md` files must also be linked from `docs/README.md`
   (ADR-0029 index parity — enforced by docs-consistency).

## Failure format (actionable, never "docs failed")

`docs check` prints per failing check: **Check / Invariant / Actual**, then
global **Repair** (`docs sync`) and **Verify** (`docs check`) lines.

## Tests

`tests/repo/test_docs_engine.py` — contract loads and parses, taxonomy 220 unique
ids, deterministic + idempotent coverage rendering, sync idempotency on the real
repo, impact detection (incl. transitive + unmapped conservative behavior),
broken-link and missing-file negative detection on temp fixtures.

## Structural invariants enforced (Phase 5B)

Beyond contract integrity + links + generated freshness, `validate` mechanically enforces:

| Invariant | Declared in contract | Rule |
|---|---|---|
| `api_surface` | `invariants.api_surface` | every OpenAPI path in `schema/api.yaml` must appear in `docs/API.md` and `adapters/README.md` (§5 undocumented public interface) |
| `env_surface` | `invariants.env_surface` | env vars captured by declared regexes in declared source files must appear in `.env.example` and `docs/WEBAPP.md` (§6 undocumented config) |
| `tier_strict` | `enforcement.strict_tiers: [0, 1]` | a taxonomy artifact at Tier 0/1 with status `missing` fails validation (Tier 2+ missing = reported, not failed — progressive enforcement per Phase 8) |

The first run of these invariants found real gaps (since fixed): `/v2/stats` missing
from `adapters/README.md`; four provider env vars undocumented anywhere;
`OPENAI_API_KEY` absent from `.env.example`; two taxonomy rows pointing at
git-ignored runtime state.

## Workflow integration (Phase 6)

| Mode | Command | Where | Enforced? |
|---|---|---|---|
| Fast local | `docs impact` (advisory) + `docs validate` | `make install-hooks` pre-commit | yes (install opt-in; CI remains backstop) |
| Full validation | `docs sync && git diff --exit-code && docs check` | pre-push hook + CI `verify-docs` | yes (CI unconditional) |
| Full regeneration | `docs sync` | on demand | idempotent |

Agents: see the "Documentation Contract" section in [../AGENTS.md](../AGENTS.md) —
a task is not complete while the contract is violated.

## Known limitations (honest)

- Markdown **anchor** targets are not verified (file-existence only) — heading
  slugs vary between renderers.
- Impact sources are declared globs; a source pattern that is too narrow yields
  the *unmapped* report rather than silence (by design).
- No taxonomy of content agreement beyond the existing repo gates: prose that is
  *substantively* stale but internally consistent is a review responsibility
  (docs review checklist is taxonomy #217, currently missing by plan).
- Coverage census reflects the declared disposition in the taxonomy file; it is
  not an independent auditor.

## Gate provenance

This system **integrates** — not replaces — the pre-existing enforcement set:
ADR-0029 docs-consistency (12 checks), ADR-0027/0051 independence, recovery
registry validator (9 checks), verify-knowledge-base exports/reports freshness,
pytest suite (133). The previous verify-docs shell "required docs" list was
removed in favor of this single canonical command (deleted duplicated logic —
the exact drift class ADR-0029 guards against).
