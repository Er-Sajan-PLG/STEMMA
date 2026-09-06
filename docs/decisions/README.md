# DECISIONS — STEMMA

Architectural decision records (ADRs). Append-only; superseded records are
marked, never deleted. Each record: context → decision → alternatives →
consequences → status.

**Landing rule:** an ADR that adds or changes a rule lands **together with**
its enforcement (validator rule and/or test) in the same change set.

| # | Record | Subject | Status |
|---|--------|---------|--------|
| 0001 | [license.md](0001-license.md) | Knowledge (CC BY 4.0) + code (MIT) licensing | decided |
| 0002 | [0002-canonical-representation.md](0002-canonical-representation.md) | Markdown + YAML frontmatter; canonical vs derived | decided |
| 0003 | [identity.md](0003-identity.md) | Stable ID rules and lifecycle | decided (namespace superseded by 0027) |
| 0004 | [entity-model.md](0004-entity-model.md) | Entity types | decided |
| 0005 | [relationship-vocabulary.md](0005-relationship-vocabulary.md) | Core relationship vocabulary | decided (superseded by 0012) |
| 0006 | [lifecycle-and-provenance.md](0006-lifecycle-and-provenance.md) | Lifecycle + provenance model | decided |
| 0007 | [export-contract.md](0007-export-contract.md) | Versioned export / consumer contract | decided |
| 0008 | [versioning.md](0008-versioning.md) | Schema / export / content versioning | decided |
| 0009 | [multilingual-principle.md](0009-multilingual-principle.md) | Language-independent identity | decided |
| 0010 | [0010-entity-metadata-extension.md](0010-entity-metadata-extension.md) | Optional equation/symbol/unit/misconception fields | decided |
| 0011 | [0011-connection-assertion-model.md](0011-connection-assertion-model.md) | First-class connection (assertion) objects | decided |
| 0012 | [0012-relation-vocabulary.md](0012-relation-vocabulary.md) | Controlled relation registry | decided |
| 0013 | [0013-confidence-semantics.md](0013-confidence-semantics.md) | Confidence / uncertainty semantics | decided |
| 0014 | [0014-inference-semantics.md](0014-inference-semantics.md) | Inferred vs asserted knowledge | decided |
| 0015 | [0015-evidence-provenance.md](0015-evidence-provenance.md) | Evidence vs provenance separation; canonical sources | decided |
| 0016 | [0016-metadata-urgent-rework.md](0016-metadata-urgent-rework.md) | Additive metadata v0.2 (polarity, timestamps, rights) | decided |
| 0017 | [0017-adaptive-metadata-extensions.md](0017-adaptive-metadata-extensions.md) | Adaptive extension registry | decided |
| 0018 | [0018-historical-attribution.md](0018-historical-attribution.md) | Historical scientific attribution (who + when) | decided |
| 0019 | [0019-rename-and-freeze.md](0019-rename-and-freeze.md) | Rename to STEMMA; identity + contract freeze | decided (freeze clause re-scoped by 0027) |
| 0020 | [0020-connections-only-truth.md](0020-connections-only-truth.md) | Connections-only relationship truth | decided (endpoint executed by 0028) |
| 0021 | [0021-registry-integrity.md](0021-registry-integrity.md) | Registry integrity, vocabulary enforcement, honest context | decided |
| 0022 | [0022-version-source-deterministic-exports.md](0022-version-source-deterministic-exports.md) | Single version source + deterministic exports | decided |
| 0023 | [0023-export-contract-v1-identity-hardening.md](0023-export-contract-v1-identity-hardening.md) | Export contract v1.0; external_ids; agent registry | decided (v1.x window closed by 0027/0028) |
| 0024 | [0024-math-layer.md](0024-math-layer.md) | STEM math layer (LaTeX, bindings, dimensions, unit entities) | **PROPOSED — human gate open** |
| 0025 | [0025-activation-phrase.md](0025-activation-phrase.md) | Activation phrase housekeeping | decided |
| 0026 | [0026-claim-identity.md](0026-claim-identity.md) | Claim signatures; duplicate-claim gate; triple immutability | decided |
| 0027 | [0027-ecosystem-decoupling-and-namespace.md](0027-ecosystem-decoupling-and-namespace.md) | Ecosystem decoupling; `stemma:` namespace; doc refoundation | decided & implemented — **ratification requested** |
| 0028 | [0028-single-relationship-source-contract-v2.md](0028-single-relationship-source-contract-v2.md) | Entity projection removed; contract v2.0; registry v1.0 | decided & implemented |
| 0029 | [0029-refoundation-baseline-and-freeze.md](0029-refoundation-baseline-and-freeze.md) | Baseline 3.0.0 architectural freeze; open human decisions | decided |
| 0030 | [0030-first-party-consumer-adapter.md](0030-first-party-consumer-adapter.md) | First-party consumer adapter (Python SDK, CLI, local JSON API) | decided & implemented |
| 0031 | [0031-rejected-lifecycle.md](0031-rejected-lifecycle.md) | Rejected lifecycle (schema 1.1.0, review.status=rejected, reason-required, all-excludes) | decided & implemented |
| 0032 | [0032-export-contract-v2.1-relation-registry.md](0032-export-contract-v2.1-relation-registry.md) | Export contract v2.1; relation registry + vocabularies sidecar | decided & implemented |
| 0033 | [0033-validation-report.md](0033-validation-report.md) | Machine-readable validation report + `--json`; advisory anomalies | decided & implemented |
| 0034 | [0034-domain-identity.md](0034-domain-identity.md) | Domain identity enforcement (`id-domain-map.yaml`, hard gate, path relocation) | decided & implemented |
| 0035 | [0035-ingest-proposal-correctness.md](0035-ingest-proposal-correctness.md) | Ingest/proposal correctness (schema-valid source, fail-closed Draft seam, gate-before-stage) | decided & implemented |

## Historical note

ADRs 0001–0026 were written before the 2026-09 refoundation and may mention
projects, product names, or workspace paths from the creator's then-ecosystem
as historical context. They are preserved verbatim as decision history; the
standing independence rule (ADR-0027 §6, `docs/GOVERNANCE.md` §12) applies to
living documents, not to this historical record.
