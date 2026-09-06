# STEMMA — Governance

**Status:** Authoritative (baseline 3.0.0). This document is the sole
governance reference for the repository.

---

## 1. Project invariants (Level 1 — never overridden)

1. STEMMA is an **independent, open, structured, reusable STEM knowledge
   foundation**. It is not owned by, subordinate to, or a backend of any
   product, company, or personal ecosystem.
2. **Curriculum is external.** No grade, course, syllabus, sequencing, or
   country semantics in canonical data.
3. **Products and consumers are external.** Dependency direction is always
   consumer → foundation. STEMMA depends on nothing upstream.
4. **Canonical knowledge lives only in `content/`, `connections/`, and
   `sources/`.** Everything derived is regenerable and never authoritative.
5. **Stable identity is a contract.** IDs are never reused or reassigned;
   assertion triples are immutable (supersession, not editing).
6. **AI output is not canonical** without named human review.
7. **Unknown is `null`, never fabricated.**
8. **The gate decides.** If `scripts/verify_all.py` fails, nothing ships.

## 2. Precedence

```
Level 1 invariants (§1)
  → this governance document
    → ADRs (docs/decisions/) — decision authority for their subject
      → specifications (docs/*-SPECIFICATION.md and friends)
        → implementation details (agent discretion)
```

## 3. Architectural decision process (ADRs)

- Significant changes to identity, schemas, relation semantics, contracts,
  licensing, or governance **require an ADR** (`docs/decisions/00NN-*.md`):
  context → decision → alternatives → consequences → status.
- **An ADR lands together with its enforcement** (validator rule + tests) in
  the same change — governance without a gate is prose.
- ADR statuses: `proposed` (awaiting human gate) → `decided`. Superseded ADRs
  are marked, never deleted.
- ADRs are append-only history: they may reference past names/projects as
  historical fact, but the living documents may not depend on that context.

## 4. Human review gates (decisions an agent may propose but never finalize)

| Domain | Gate |
|---|---|
| Canonical schema changes (any breaking change) | Human approval of the ADR |
| Relation semantics (new/changed relations, family semantics) | Human approval |
| Identity model (namespace, ID grammar, alias rules) | Human approval |
| Export contract major versions | Human approval |
| Licensing changes | Human approval |
| Adoption of external standards into canonical form | Human approval |
| Promotion of `reserved` relations / `proposed` extensions to adopted | Human approval |
| Marking content `canonical` | Named human reviewer (per object) |
| Public IRI / publishing identity (domain) | **Open — ADR-0029** |
| Math layer (ADR-0024) | **Open — proposed** |

Agents investigate, propose, implement, test, and document — and must flag,
not silently decide, the above.

## 5. Change management

- **Trivial** (typos, prose clarification): any contributor, normal review.
- **Content** (new/edited entities, connections): normal review + the gate;
  review-status advancement follows the curation protocol.
- **Contract** (schemas, registry semantics, export): ADR + version bump +
  MIGRATIONS entry + updated tests, one change set.
- **Breaking**: major version bump; old data's fate documented (rewrite or
  validates-unchanged); consumer impact stated.
- **Deprecation**: objects are deprecated with successors, never deleted;
  IDs and history are reserved forever.

## 6. Versioning policy

Three tracks, never collapsed (single source `schema/VERSION.yaml`; details in
`docs/VERSIONING.md`): `schema_version` (canonical schemas), `export_version`
(consumer contract), and the repository release line (`VERSION` file,
currently 3.0.0 = refoundation baseline). Content growth is never a contract
change.

## 7. Contribution expectations

See `docs/CONTRIBUTING.md`. Summary contract: run the full verify chain
locally; regenerate derived artifacts in the same change; no curriculum or
ecosystem coupling (machine-checked); agents/relations/extensions are
registered before use; commit messages follow Conventional Commits.

## 8. Testing expectations

Every behavioral change ships with tests that enforce an *invariant*, not
just a code path. Release gate = `scripts/verify_all.py` (CI runs exactly
this chain). New gates must be added to the chain and documented in
`docs/TESTING.md`.

## 9. Documentation expectations

- One authoritative document per subject (this set). Contradiction is a bug.
- Specifications describe implemented reality; aspirational work is marked
  `proposed`/`roadmap` and lives in ADRs or `docs/ROADMAP.md`.
- Migrations are logged append-only in `docs/MIGRATIONS.md`.

## 10. Security & integrity

`docs/SECURITY-INTEGRITY-PROVENANCE.md` governs: no secrets; least-privilege
CI; gitleaks; integrity via content hashes, claim signatures, and
history-based immutability guards; provenance as the trust model for content.

## 11. Experimental policy

- Experiments live in branches or gitignored staging (`proposals/`) — never
  as unreviewed additions to canonical directories or registries.
- Registry dimensions and reserved relations carry explicit
  `proposed`/`reserved` status with promotion gates.
- Nothing becomes architecture merely by existing: promotion is a decision
  (ADR) with enforcement attached.

## 12. Ecosystem independence (standing rule)

No document, schema, script, test, or canonical object may encode a
dependency on any private project ecosystem (products, platforms, personal
infrastructure). Historical names may appear **only** inside ADRs/MIGRATIONS
as history, and in the one alias rule of the immutability guard. This rule is
machine-checked (`tests/repo/test_independence.py`).
