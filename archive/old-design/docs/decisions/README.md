# DECISIONS — LearningHubSTEM Foundation

Decision records for the LearningHubSTEM foundation (Phase 1 — Foundation Definition & Freeze).

Each record follows the same shape:

- Context
- Decision
- Alternatives considered
- Reason
- Consequences
- Status (`decided` or `pending` + human approval required)
- Related

| # | Record | Subject | Status |
|---|--------|---------|--------|
| 0001 | [license.md](0001-license.md) | Knowledge + code licensing | PENDING human approval |
| 0002 | [canonical-representation.md](0002-canonical-representation.md) | Markdown + YAML frontmatter; canonical vs derived | decided (documented) |
| 0003 | [identity.md](0003-identity.md) | Stable ID rules and lifecycle | decided (documented) |
| 0004 | [entity-model.md](0004-entity-model.md) | Six entity types | decided (documented) |
| 0005 | [relationship-vocabulary.md](0005-relationship-vocabulary.md) | Core relationship vocabulary | decided (documented) |
| 0006 | [lifecycle-and-provenance.md](0006-lifecycle-and-provenance.md) | Lifecycle + provenance model | decided (documented) |
| 0007 | [export-contract.md](0007-export-contract.md) | Versioned export / consumer contract | decided (documented) |
| 0008 | [versioning.md](0008-versioning.md) | Schema / export / content versioning | decided (documented) |
| 0009 | [multilingual-principle.md](0009-multilingual-principle.md) | Language-independent identity | decided (documented) |
| 0010 | [0010-entity-metadata-extension.md](0010-entity-metadata-extension.md) | Optional equation/symbol/unit/common_misconceptions fields (Phase 2) | decided (documented) |
| 0011 | [0011-connection-assertion-model.md](0011-connection-assertion-model.md) | First-class connection (source–relation–target + assertion) objects | decided (documented) |
| 0012 | [0012-relation-vocabulary.md](0012-relation-vocabulary.md) | Controlled relation vocabulary + registry | decided (documented) |
| 0013 | [0013-confidence-semantics.md](0013-confidence-semantics.md) | Confidence / uncertainty semantics | decided (documented) |
| 0014 | [0014-inference-semantics.md](0014-inference-semantics.md) | Inferred vs asserted knowledge semantics | decided (documented) |
| 0015 | [0015-evidence-provenance.md](0015-evidence-provenance.md) | Evidence vs provenance separation; canonical sources | decided (Phase A) |
| 0016 | [0016-metadata-urgent-rework.md](0016-metadata-urgent-rework.md) | Urgent additive metadata v0.2 (polarity, timestamps, rights...) | decided |
| 0017 | [0017-adaptive-metadata-extensions.md](0017-adaptive-metadata-extensions.md) | Adaptive extension registry — governed open metadata seam | decided (implemented) |
| 0018 | [0018-historical-attribution.md](0018-historical-attribution.md) | Historical scientific attribution — who stated it + when (who/when/timeline) | decided (implemented) |

| 0019 | [0019-rename-and-freeze.md](0019-rename-and-freeze.md) | Rename foundation to STEMMA; freeze lhs identity + schema/export contracts | decided (implemented) |
| 0020 | [0020-extended-entity-model.md](0020-extended-entity-model.md) | Extended canonical entity model (15 types: 6 core + 9 extended) | decided (implemented) |
| 0021 | [0021-multilevel-validation.md](0021-multilevel-validation.md) | Multi-level validation pipeline with ERROR/WARNING/INFO severity | decided (implemented) |
| 0022 | [0022-subset-exports.md](0022-subset-exports.md) | Deterministic subset export system for consumer-specific views | decided (implemented) |
| 0023 | [0023-export-contract-v1-identity-hardening.md](0023-export-contract-v1-identity-hardening.md) | Export contract v1 identity hardening | decided |
| 0024 | [0024-math-layer.md](0024-math-layer.md) | STEM math layer: LaTeX, symbol bindings, dimensions, unit refs | PROPOSED — awaiting G-C, now linked to physics-first |
| 0025 | [0025-activation-phrase.md](0025-activation-phrase.md) | Activation phrase | decided |
| 0026 | [0026-claim-identity.md](0026-claim-identity.md) | Claim identity / signature | decided |
| 0027 | [0027-ecosystem-decoupling-and-namespace.md](0027-ecosystem-decoupling-and-namespace.md) | Ecosystem decoupling + stemma: namespace | decided |
| 0028 | [0028-single-relationship-source-contract-v2.md](0028-single-relationship-source-contract-v2.md) | Single relationship source contract v2 | decided |
| 0029 | [0029-refoundation-baseline-and-freeze.md](0029-refoundation-baseline-and-freeze.md) | Refoundation baseline and freeze | decided |
| 0030 | [0030-first-party-consumer-adapter.md](0030-first-party-consumer-adapter.md) | First-party consumer adapter | decided |
| 0031 | [0031-rejected-lifecycle.md](0031-rejected-lifecycle.md) | Rejected lifecycle | decided |
| 0032 | [0032-export-contract-v2.1-relation-registry.md](0032-export-contract-v2.1-relation-registry.md) | Export contract v2.1 relation registry | decided |
| 0033 | [0033-validation-report.md](0033-validation-report.md) | Validation report | decided |
| 0034 | [0034-domain-identity.md](0034-domain-identity.md) | Domain identity | decided |
| 0035 | [0035-ingest-proposal-correctness.md](0035-ingest-proposal-correctness.md) | Ingest proposal correctness | decided |
| 0036 | [0036-ingestion-review-webapp.md](0036-ingestion-review-webapp.md) | Ingestion review webapp | decided |
| 0037 | [0037-phase-b-trust-review-activation.md](0037-phase-b-trust-review-activation.md) | Phase B trust review activation | decided |
| 0038 | [0038-antigravity-provider-abstraction.md](0038-antigravity-provider-abstraction.md) | Antigravity provider abstraction | decided |
| 0039 | [0039-ingestion-webapp-consolidation.md](0039-ingestion-webapp-consolidation.md) | Ingestion webapp consolidation | decided |
| 0040 | [0040-physics-first-strategy.md](0040-physics-first-strategy.md) | Physics-first minimal canonicalization strategy | PROPOSED — NOW per PHYSICS-FIRST plan |
| 0041 | [0041-minimal-entity-profile.md](0041-minimal-entity-profile.md) | Minimal entity profile and deprecation of pedagogical fields | PROPOSED |
| 0042 | [0042-minimal-relation-set-physics.md](0042-minimal-relation-set-physics.md) | Minimal relation set for physics foundation (7 adopted) | PROPOSED |

**Freeze rule:** a change to any subject above requires a documented decision (see specification
§17). Minor editorial improvements do not. Physics-first ADRs 0040-0042 are the current focus (see PHYSICS-FIRST-IMPLEMENTATION-PLAN.md).
