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
**Freeze rule:** a change to any subject above requires a documented decision (see specification
§17). Minor editorial improvements do not.
