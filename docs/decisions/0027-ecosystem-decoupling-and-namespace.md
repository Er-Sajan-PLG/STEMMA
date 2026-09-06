# DECISION 0027 — Ecosystem decoupling, `stemma:` namespace, and repository refoundation

- **Date:** 2026-09-04
- **Status:** decided & implemented (mechanical/structural); **ratification by
  the project owner explicitly requested** — this is a foundational,
  hard-to-reverse decision (see §"Human review").
- **Supersedes:** the namespace-freeze clause of ADR-0019 (rename-and-freeze);
  ADR-0019's freeze is re-scoped to "no *further* namespace changes without a
  new ADR".
- **Related:** ADR-0003 (identity), ADR-0019 (rename), ADR-0022 (versions),
  ADR-0028 (contract v2.0), ADR-0029 (baseline)

## Context

STEMMA originated inside a private multi-project ecosystem and inherited that
coupling in its most load-bearing places:

1. **Identity**: every canonical ID used the `lhs:` namespace (the project's
   former name), appearing in 881 objects and 654 filenames — including
   filenames illegal on Windows (`lhs:conn.NNNNNN.yaml`).
2. **Documentation**: vision/governance/roadmap documents described the
   systems of that ecosystem, its products, company plans, and private
   workspace paths as if they were STEMMA context.
3. **Provenance data**: some entity citations referenced curriculum bodies
   ("Nepal CDC SEE / CBSE / UK KS4…") contrary to the curriculum-agnostic
   invariant; one example was geography-specific.
4. **Process artifacts**: superseded audits/plans, one-shot repair scripts,
   campaign worksheets, and personal tooling config sat in the tree as if
   they were architecture.

The project's stated goal is to be an **independent open-source foundation**
understandable without any knowledge of the creator's other projects.

## Decision

1. **Namespace migration.** All canonical IDs move `lhs:` → `stemma:` in one
   governed bulk migration. Identity-defining fields (name, domain, triples)
   are unchanged; git history remains the audit trail; the immutability guard
   reconciles prefixes through one documented, non-extendable alias rule.
   Filenames become colon-free (`conn.NNNNNN.yaml`, `src.<slug>.yaml`).
2. **Versions.** `schema_version` 0.2 → **1.0.0** (breaking: ID grammar,
   schema `$id`s/titles, projection field removal per ADR-0028);
   `export_version` 1.0 → **2.0.0** (breaking: namespace + projection
   removal); registry 0.3 → **1.0.0**; repository `VERSION` → **3.0.0**.
   The v1.x legacy co-release artifact (`knowledge.compat-0.1.json`) is
   retired with the consumers that pinned it, which are external.
3. **Documentation refoundation.** A new authoritative set (VISION,
   ARCHITECTURE, DOMAIN-MODEL, SCHEMA/METADATA/RELATIONSHIP specifications,
   PIPELINES, TESTING, STANDARDS, GOVERNANCE, SECURITY, CONSUMERS, ROADMAP,
   IMPLEMENTATION-STATUS) replaces all pre-refoundation vision/plan/audit
   documents, which are deleted (git history + MIGRATIONS preserve them).
   ADRs remain as history.
4. **Content honesty fixes.** Curriculum-body citations normalized to the
   underlying knowledge authority or `null`; geography-specific example made
   neutral; the type-inconsistent `dimensions` extension on a law entity
   removed (dimensions belong to quantities; see ADR-0024).
5. **Cleanup.** Deleted: one-shot migration/repair scripts, process reports,
   superseded plans/audits, `.plan/`, personal tool config (`opencode.json`),
   `audit_empirical.py`. Nothing with architectural authority was lost: the
   gate, guards, and tests carry the invariants.
6. **Standing independence rule + gate.** No document, schema, script, test,
   or canonical object may encode a dependency on any private ecosystem.
   Historical names may appear only inside ADRs/MIGRATIONS and the single
   alias rule. Enforced by `tests/repo/test_independence.py`.

## Alternatives considered

- **Keep `lhs:` frozen** (zero migration cost) — rejected: every ID would
  permanently carry another project's brand, defeating the independence goal;
  the freeze (ADR-0019) served continuity across a *rename*, not permanence.
- **Dual namespace with permanent alias resolution** — rejected: permanent
  dual identity is exactly the "two sources of truth" defect class this
  codebase already eliminated once; a one-time migration with a frozen alias
  rule in one guard is strictly simpler.
- **Keep historical docs in an `archive/` directory** — rejected: git is the
  archive; an in-repo archive re-imports the noise the refoundation removes.

## Consequences

- Consumers must repoint to `stemma:` IDs and contract v2.0 (external
  adapters; migration note in `docs/MIGRATIONS.md`).
- Windows checkouts work (no colons in filenames).
- The guard's alias rule is permanent but load-bearing and tested; it must
  never be extended to other prefixes.
- Repository size and doc count shrink materially; authority is concentrated
  in the spec set + ADRs + gate.

## Human review (explicitly requested)

The owner's instruction authorized this refoundation, but three aspects are
flagged for explicit ratification rather than assumed:

1. **The namespace choice `stemma:`** (vs. a neutral/prefix-free scheme).
2. **Breaking export contract v2.0.0 now** (vs. a compatibility window for
   any consumer still pinned to 1.x).
3. **Deletion of pre-refoundation documents** from the tree (vs. in-repo
   archive).

If the owner disagrees with any of these, the remedy is a superseding ADR;
the migration itself is recoverable from git history.
