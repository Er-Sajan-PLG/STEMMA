# GOVERNANCE — STEMMA

**Status:** STEMMA repository governance (Level 2).
**Applies to:** Humans and AI agents working inside this repository.
**Related:** `AGENTS.md` (routing), `docs/NORTHSTAR.md` (north star),
`docs/MASTER-VISION.md` (vision), `docs/STEMMA-SPECIFICATION.md`
(technical spec), `docs/STEMMA-ROADMAP.md` (phasing),
`docs/decisions/` (STEMMA decision records), `docs/REVIEW-RESPONSE.md`
(reconciliation record).

---

## 1. Governance precedence

```
LEVEL 1 — STEMMA INVARIANTS (non-overridable)
          ↓
LEVEL 2 — PROJECT / REPOSITORY GOVERNANCE
          ↓
LEVEL 3 — IMPLEMENTATION DETAILS
```

### Level 1 — STEMMA invariants (never overridden)

- STEMMA is an **independent, open, structured, reusable STEM knowledge foundation**.
- STEMMA is **not** owned by, subordinate to, or a backend of any product.
- **Curriculum is external.** It is a consumer of the foundation, never a component of it.
- **Products are consumers.** LearningHub, JARVIS, STEM-GAME, STEM Lab, and unknown future
  products all sit **below** STEMMA in the dependency direction.
- **Knowledge order ≠ curriculum order.** Relationships live in the knowledge layer;
  sequencing is a curriculum decision.
- Canonical knowledge cannot depend on a specific product, curriculum, database, or country.
- **AI output is not canonical** without appropriate human review.
- Derived artifacts are **regenerable** and are never the source of truth.

A repository's governance may refine how these apply, but may **not** silently redefine them.

### Level 2 — Project / repository governance

A repository decides its own framework, language, folder structure, testing, deployment,
internal APIs, and workflow. For example `LearningHub/AGENTS.md` and
`LearningHub/docs/CONSTITUTION.md` are authoritative inside that repository.

### Level 3 — Implementation details

Agent discretion: variable names, internal structure, test structure, small refactors,
non-breaking documentation, bug fixes within established boundaries.

---

## 2. The ecosystem view

STEMMA is the open foundation. Consumers build on top of it. There is **no**
"shared platform services" layer between the foundation and its consumers, and STEMMA
is **not** an application-services backend.

```
                    STEMMA
                 OPEN STEM FOUNDATION
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
     Consumer A       LearningHub      Consumer C
     / Research       / Curriculum      / Future Tool
          │                │                │
          ▼                ▼                ▼
       Product          Product          Product
```

Dependency direction is always **consumer → foundation**. Nothing depends on STEMMA
from above; STEMMA depends on nothing.

### Status honesty

Distinguish **existing**, **planned**, and **possible** integrations. Today:

| Project | Status |
|---------|--------|
| `LearningHub` | ACTIVE (flagship product; a consumer today by intent, not by code) |
| `JARVIS` | ACTIVE (AI platform; **planned** consumer) |
| `3D-Ludo` | PROTOTYPE (independent game; not a consumer) |
| `STEMMA` | SEED ONLY (minimal proof; full MVP **not** activated) |
| `STEM-GAME` | DEFERRED (empty folder; planned consumer) |

Do not describe planned integrations as existing ones.

---

## 3. Scope discipline

Classify every significant piece of work:

| Class | Meaning | Action |
|-------|---------|--------|
| **NOW** | Required by the current milestone | Implement |
| **SEAM** | Small interface/adapter/contract protecting a known future change | Implement only when inexpensive and useful |
| **LATER** | Described by the architecture but not required now | Document if useful; do not implement |
| **OUT OF SCOPE** | Not relevant now | Do not implement |

**Deferred / not current scope** unless the human explicitly activates it:

- STEM-GAME production, STEM Lab, JARVIS ↔ STEMMA integration
- Full STEMMA MVP (activation phrase: **"ACTIVATE LEARNINGHUBSTEM MVP"**)
- Microservices, cloud infrastructure, auth, payments, analytics, recommendation engines,
  vector/graph databases, generalized AI orchestration, shared platform services, cross-product
  identity or databases.

---

## 4. Canonical vs derived

```text
Canonical source (docs/STEMMA-SPECIFICATION.md defines the format)
      ↓
Derived artifacts: JSON exports, search indexes, embeddings, graph representations,
                   APIs, caches, recommendations
```

Rule: **derived artifacts are regenerable from canonical content and are never the source of truth.**

---

## 5. Rules that always apply

1. **Respect per-project governance** (Level 2 overrides within a repository).
2. Preserve the **Knowledge ≠ Curriculum ≠ Pedagogy ≠ Product** boundary.
3. **Build small.** Small verified increment + clean boundary + tests + docs beats speculative
   architecture.
4. **Do not expand scope silently.** When in doubt, ask the human.
5. **Products stay independent** — integration via explicit contracts/adapters, never embedding.
6. **AI output requires review** before becoming canonical.
7. **No secrets in code or docs.**
8. **Document decisions** (ADRs / decision records); leave a clear trail.
9. **Don't create infra just because a review suggested it** — verify against this repository's governance.

---

## 6. Definition of Done (canonical entity)

A canonical entity must have:

- stable ID (namespace + format per specification)
- valid schema
- required metadata
- provenance (source and/or reviewer record)
- valid relationships (whitelisted, no dangling targets)
- appropriate review status
- human review where required
- **no curriculum dependency, no product dependency**
- passing validation

---

## 7. Enforcement direction

Prose rules → schemas → validation → tests → CI enforcement.

Implement only what is justified **NOW** (see specification §15). Do not build a generalized
policy engine. Long-term candidate checks (documented, not built):

- no STEMMA → product dependency
- no product → STEMMA internal import coupling
- no curriculum-specific canonical entities
- no duplicate / dangling IDs, no content without provenance

---

## 8. Freeze rule (STEMMA foundation)

**Frozen does not mean "never change".** It means: foundational changes require an explicit
governance decision rather than accidental implementation drift.

The following require a documented decision record (in `docs/decisions/`) and, where the
human-decision list in the specification §16 says so, human approval:

- entity type changes
- relationship semantics changes
- ID rules changes
- canonical representation changes
- lifecycle semantics changes
- export contract changes
- schema version major bumps

Minor editorial / documentation improvements do **not** require a governance event.

---

## 9. Session protocol (cross-project)

1. Read `AGENTS.md`, `docs/NORTHSTAR.md`, and this file.
2. Read the affected repository's own governance.
3. Classify work NOW / SEAM / LATER / OUT OF SCOPE.
4. State a short plan before changing anything.
5. Run the affected repository's verification commands.
6. Finish with a short session summary and flag human decisions.

---

*If a rule must be violated, do not violate it silently — record the exception and get human
approval first.*