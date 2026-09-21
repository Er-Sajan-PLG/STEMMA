# ADR-0045: Value-Slot on Connection Kind

Status: Decided
Date: 2026-09-21
Baseline: ADR-0044
Related: docs/ARCHITECTURE-V2.md Part 3.2, schema/connection.schema.json, schema/semantic-claim.schema.json

## Context

Measurements, prevalence, typed literals need first-class evidence-bearing representation. Previous flat connection model only had target field for entity-entity relations. Need to express "metre = 1.0" or "42% students think..." as ValueClaim with evidence, not inline string.

Options:
- Separate claims/ directory — escapes immutability guard check_id_immutability.py walks only content/ and connections/, creates fourth truth surface, re-creates ADR-0020 two truths defect.
- Value-slot on connections — target XOR value, inherits immutability guard, duplicate detection, evidence requirements, export machinery.

## Decision

Adopt value-slot on connections/conn.NNNNNN.yaml:

- target and value mutually exclusive XOR
- value: {amount decimal string Wikibase-aligned, lowerBound optional, upperBound optional, unit IRI per ADR-0024 or "1" dimensionless interim allowlist QUDT/UCUM/SI symbols m kg s A K mol cd documented}
- claim_signature extends to cover value-slot: sha256(source|relation|value_canonical|polarity|sorted(qualifiers))
- check_id_immutability.py covers connections/ so no new root needed
- Unit field interim allowlist: "1" OR QUDT/UCUM anchor strings OR SI symbols until ADR-0024, documented in schema

Example:
```yaml
id: stemma:conn.NNNNNN
type: connection
source: stemma:phys.metre
relation: has_value
value:
  amount: "1.0"
  unit: "qudt:unit-Meter"
evidence: [{source_id: src.si-brochure-9th, document_hash: sha256:..., page: 20, text_span: "The metre is defined as...", char_offsets: {start: 1024, end: 1150}, surrounding_context: "..."}]
```

## Consequences

Easier: expressing measurements, misconception prevalence, physical quantities as first-class evidence-bearing value-claims with warrant definitional/experimental.

Harder: value-slot XOR logic adds schema complexity over simple target field, migration from flat entities to value-slot when content exists requires careful scripting.

Hard to undo: once value-claims exist removing requires migrating all measurements back to inline strings.

## Verification

- Connection with both target and value → schema error
- Connection with neither → schema error
- Value without evidence at canonical → gate error
- claim_signature covers value-slot

## Related

- ADR-0044 L1-L8, Part 3.2
- docs/ARCHITECTURE-V2.md Part 3.2
- schema/semantic-claim.schema.json for candidate
