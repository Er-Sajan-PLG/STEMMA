# ADR-0055: Explorer & AI Chat as the Product Layer — Boundary from the STEMMA Core

Status: Decided — 2026-10-01
Date: 2026-10-01
Decided by: Sajan (sole owner), ruling on a boundary question raised while recording
REQ-STEMMA-INTEG-001.
Relates to: ADR-0054 (consumer access surface), ADR-0044 (integrated foundation v2),
ADR-0053 / R6 (identifier base), REQ-STEMMA-CORE-001, REQ-STEMMA-CORE-003,
REQ-STEMMA-INTEG-001
Amends: ADR-0054 §5 (explorer's role), docs/ARCHITECTURE-V2.md §5.3 (consumer surface)

## Context

Recording the explorer's AI-chat requirement (REQ-STEMMA-INTEG-001) surfaced a boundary
question the owner had already half-answered elsewhere and that no single record states:

> The 3D visual explorer and its AI chat are the most **product-facing** parts of STEMMA.
> They risk pulling product concerns — presentation, hosted chat, model selection, and
> (by implication) retrieval/RAG — into a core whose whole design principle is that it is
> **not** a product and **not** a RAG system.

The tension is real and structural:

- STEMMA's core is intentionally a **linkable schema + canonical corpus** (ADR-0044;
  `REQ-STEMMA-CORE-001`, `REQ-STEMMA-CORE-003`). Embeddings, vectors, and RAG are declared a
  **consumer's job**, not STEMMA's (GOVERNANCE, `docs/RAG.md`, `docs/EMBEDDINGS.md`).
- Yet the explorer is *ours*, it is *the reference consumer*, and its `dist/` build is what
  the owner actually **hosts** for people. ADR-0054 §5 already names it "the public site" —
  the family/tester-facing artifact — while §2/§3 push RAG and hosting out of the core.
- So the explorer is simultaneously (a) the closest thing STEMMA has to an executable
  conformance test of its export, and (b) the most product-shaped thing in the repo. Those
  two facts must be separated on purpose, or the core will drift toward being a product.

The owner's principle, stated directly: **the 3D visual and the chat are indeed the product
aspects of STEMMA — they must not leak into the STEMMA core.**

## Decision

**The core STEMMA is a knowledge foundation. The explorer and its chat are a product layer
built *on top of* that foundation. The boundary is enforced by direction of dependency:
the product layer depends on the core; the core never depends on the product layer.**

Concretely:

1. **Direction of dependency is one-way.** The core (`content/`, `connections/`, `sources/`,
   `schema/`, `scripts/`, `exports/`) must contain **no** reference to the explorer, its UI,
   its chat, its model selection, or its hosting. The explorer (`explorer/`) is a consumer
   and reads the derived export like any other consumer (ADR-0054 §1). A core file that
   mentions the explorer's chat is a boundary violation.
   - **Already enforced in spirit:** `REQ-STEMMA-CORE-001` (canonical is only the three
     dirs), `REQ-STEMMA-CORE-003` (no embeddings/RAG in canonical), and the independence
     invariant (`REQ-STEMMA-GATE-005`). This ADR makes the *product* direction of that same
     rule explicit.

2. **Presentation is not canonical.** Everything about the explorer's look — node sizes,
   line thickness, legend behaviour, camera, layout, colour — is a **presentation concern**
   that lives only in `explorer/`. It must never be asserted as a property of canonical
   data, and no canonical schema or gate may encode a visual fact. (This is the concrete
   reading of "product aspect": appearance is not knowledge.)

3. **The chat is a consumer, not a core capability.** The AI chat is implemented inside the
   explorer as a consumer of the export. It:
   - reads **derived exports only**, never canonical markdown (`REQ-STEMMA-CORE-001`);
   - grounds every answer in the export with citations to entity ids + `source_refs`
     (`REQ-STEMMA-INTEG-001`), and declines when there is no grounding;
   - owns its own model selection and any provider keys, exactly as any external consumer
     would (ADR-0054 §2/§4). **No chat, model-selector, or retrieval code may move into
     `scripts/` or otherwise into the core.**

4. **Retrieval/RAG stays the consumer's job — including ours.** The chat may use retrieval
   (vector search over derived embeddings) because the explorer *is* a consumer. That does
   **not** make RAG a STEMMA capability. The reference embedding/RAG code
   (`scripts/embed.py`, `scripts/rag.py`, `docs/RAG.md`) remains a **reference
   implementation the core may ship as an example**, with production embedding/RAG owned by
   whomever runs the consumer. Adopting a real model into the core's gate is out of scope
   and needs its own ADR.

5. **The product layer is not part of the spec's conformance claim.** The
   specification-recovery pilot's slice is CORE–GATE–EXPORT. The explorer is assessed
   precisely to the extent it *tests* the core (REQ-STEMMA-INTEG-001: does it render the
   export faithfully, and does a grounded chat work against the export?). The explorer's
   product qualities — is the UI nice, is the chat engaging — are **not** conformance
   criteria and must not be smuggled into the spec as such. The webapp is the mirror case:
   it is the private admin (authoring) tool, not a consumer, and not part of the core either
   (ADR-0054 §3).

6. **Hosting the product is separate from publishing the core.** The explorer's static build
   on GitHub Pages (ADR-0054 §5) is product hosting. It does not obligate the core to be
   hosted, resolved, or served — consistent with the R6 decision that the core publishes no
   resolvable base yet (`docs/decisions/r6-identifier-base.md`).

## Consequences

- **Clear rule for future work:** if a change to the explorer requires touching the core to
  work, the change is wrong — invert it. The explorer must be able to be deleted and
  rebuilt without the core noticing, except that `REQ-STEMMA-INTEG-001` would lose its
  reference-conformance host.
- **The core's test suite must not depend on the explorer's product code.** The existing
  separation (explorer has its own `package.json`, `verify` script, and CI job) is the
  right shape and is now normative.
- **Webapp/explorer refactors are product work, not spec work.** The owner's planned
  webapp redesign (UI + model selection + canonical-engine steps) is a product-layer
  effort; it does not change core requirements, and it does not belong in the recovery
  pilot's approval scope.
- **RAG adoption into the core is explicitly deferred** and requires a new ADR. Until then,
  `REQ-STEMMA-CORE-003` stands: no embeddings/vectors/RAG artifacts in canonical.
- **Documented, accepted consequence:** the product layer will, over time, want features
  (accounts, hosted chat, analytics) that the core deliberately does not provide. Those are
  product decisions; this ADR is the pointer that keeps them from redefining the core.
- **Enforcement is by review + the independence invariant**, not (yet) by a new automated
  check. A future cheap check — "no core file references `explorer/`" — is a natural
  candidate if the boundary is ever crossed in practice; it is not added now (no observed
  violation).

## What this ADR is *not*

- It is **not** a decision to build the chat UI a particular way (that is product design).
- It is **not** a decision about the explorer's hosting provider or URL.
- It is **not** a RAG-adoption decision for the core — that is deferred to its own ADR.
- It does **not** renumber or supersede ADR-0054; it clarifies §5 and adds the explicit
  core/product direction of dependency that ADR-0054 left implicit.
