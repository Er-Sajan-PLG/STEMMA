# DECISION 0026 — Claim identity: derived claim signature, duplicate-claim gate, immutable connection triples

- **Date:** 2026-09-04
- **Status:** decided (implemented with this change — the gate, the guard and their tests land
  together, per plan v2 §1: "governance by document must stop outrunning governance by
  mechanism")
- **Related:** ADR-0003 (stable IDs), ADR-0011 (connection assertion model), ADR-0016 (metadata
  rework — `claim signature` named but never defined), ADR-0019 (freeze), ADR-0020
  (connections-only truth), ADR-0022 (deterministic exports), ADR-0023 (export contract v1.0,
  agent registry), ADR-0025 (activation phrase — numbering note: this record is 0026 because
  0025 was taken on the remote branch while this work was in flight), plan v2 **E4.3 / E4.5**,
  `docs/ARCHITECTURE-AUDIT-v1.0.md` (F7, F11, R12)

## Context

1. **A connection is a record; the claim is the proposition.** `lhs:conn.NNNNNN` asserts
   *source –relation→ target* under a polarity and qualifiers. Nothing in the repository could
   answer "are these two connections the same claim?" — ADR-0016 named a "claim signature" but
   never defined one, and the audit found no duplicate-claim detection anywhere (F7). With 654
   machine-migrated connections that is how silent double-assertions survive.
2. **Connection records were editable in place.** Changing `target` on an existing connection
   rewrites what that id *means* for every consumer that stored it, without a trace: unlike
   entities (ADR-0003 + `check_id_immutability.py`), connections had no immutability guard
   (F11, R12). The only legal edit path that preserves history — supersede and re-assert under a
   new id — was documented nowhere and enforced nowhere.
3. **Deletion was equally invisible.** A connection file could simply disappear, leaving
   consumers with a dangling reference and no successor.

## Decision

### 1. Claim signature (derived, E4.3)

```
claim_signature = sha256( source | relation | target | polarity | sorted(qualifiers) )
```

- Derived **only**: never written into canonical YAML, never part of a connection's identity.
  It is emitted into the export as `connections[].claim_signature` (and into the review-aware
  policy exports) so consumers can deduplicate claims without recomputing the hash.
- `polarity` defaults to `positive` (the `connection.schema.json` default); `qualifiers` are
  order-insensitive (canonically serialised and sorted), so re-ordering a list is not a new claim.
- **In the hash:** what the claim *says* — endpoints, relation, polarity, qualifiers.
  **Not in the hash:** evidence, provenance, confidence, review status, context regime/scale —
  two sources supporting the same proposition are the same claim, which is exactly what
  duplicate detection is for.

### 2. Duplicate-claim gate (E4.3)

Two **active** connections with the same signature are a **validator error** (exit 1), not a
warning. Remedy: keep one connection, and retire the rest with
`assertion.status: superseded` + `lifecycle.replaced_by: <kept id>`. Retired connections are
excluded, so superseded history never trips the gate. The audited tree has **0** duplicates, so
no grandfathering or allowlist was needed — the rule starts clean.

### 3. Connection-triple immutability (E4.5)

The `(source, relation, target)` triple recorded under a connection id is **immutable for the
life of the id**, reconstructed from git history by `scripts/check_id_immutability.py`
(CI checks out with `fetch-depth: 0`). Two further rules follow:

- **Correcting a claim is a supersession, not an edit.** Set `assertion.status: superseded` +
  `lifecycle.replaced_by` on the old connection and assert the corrected claim under a
  **new** `lhs:conn.NNNNNN`. Editing a triple in place fails the gate with that remediation in
  the message.
- **Deleting a connection requires retirement.** An id present in history but absent from HEAD
  must have last been seen as `superseded`/`deprecated` or with `lifecycle.replaced_by` set;
  otherwise it fails as `[connection-deleted-without-supersession]`.

Metadata edits (review status, evidence, confidence, context) remain free — only the claim
itself is frozen. The history walker follows renames, so the pending E4.6 colon-filename
migration cannot be mistaken for a deletion.

### 4. Enforcement map (landed with this record)

| Rule | Enforced by | Test |
|------|-------------|------|
| signature definition, determinism, qualifier-order insensitivity | `scripts/validate.py::claim_signature` | `tests/provenance/test_claim_identity.py` |
| no duplicate active claims | `scripts/validate.py::check_duplicate_claims` (in `verify_all`) | same + canonical-tree case |
| export carries the derived signature | `schema/export.schema.json` (documented, pattern-checked) | export + policy-view cases |
| triple immutability / supersession / no silent deletion | `scripts/check_id_immutability.py::detect_connection_violations` | `tests/curation/test_connection_immutability.py` (6 TDD cases + parser + live-tree) |

No export-contract bump: `claim_signature` is an **additive derived** member in v1.x.

## Alternatives considered

- **Store the signature in the connection file** — rejected: derived data in canonical YAML
  churns on every content edit and can drift from its own inputs. The export is the right place.
- **Include evidence/provenance in the hash** — rejected: two textbook citations for the same
  dependency are one claim supported twice; hashing them separately would hide the duplicate
  (and ADR-0015 already separates evidence from assertion).
- **Warn instead of fail on duplicates** — rejected: the audited tree is clean today, so a hard
  gate costs nothing and prevents the first duplicate. Warnings in this gate have historically
  been ignored (audit F6).
- **Allow duplicates now, disambiguate with assertion `rank` (E6.6)** — deferred to gate G-H.
  If a rank is adopted later, the gate can be relaxed to "duplicates must carry distinct ranks";
  the signature is the mechanism that decision will need.
- **Enforce immutability with a datastore constraint or an immutability service** — OUT OF
  SCOPE (plan v2 §1/§5): git is already the immutable, append-only store, and it is the source
  of truth for history here.
- **Freeze the whole connection record (all fields)** — rejected: curation *must* be able to
  add evidence and promote review status without minting new ids; freezing only the claim
  content is the narrow invariant that protects consumers.

## Consequences

- Consumers (STEM-TUITION, AI agents, the explorer) can now deduplicate and diff claims
  mechanically, and can detect that a claim they cached was superseded rather than edited.
- Correcting a wrong edge costs one new id and one supersession — more ceremony than a text
  edit, which is the point: claim corrections become part of the auditable record.
- Cost: the guard walks `connections/` history (654 files → ~15 s in CI, in addition to the
  entity walk). It runs once per verify chain.
- The signature is stable **by construction**: it is computed from canonical fields, so the same
  content always yields the same hash across machines (ADR-0022 determinism).
- Open item: `scripts/apply_review_decisions.py` and any future bulk-repair tooling must
  supersede-and-recreate rather than rewrite triples in place — enforced from now on by CI.
