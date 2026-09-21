# REQUIREMENTS — CORE-GATE-EXPORT slice

Canonical records: `spec/machine-readable/requirements.yaml` (full §8.6 schema).
This file is the readable summary. **Status of every requirement: `PROPOSED`** —
the executor has no approval authority (Constraint D). Approval owner: Sajan
(SOLE_OWNER). Only APPROVED requirements authorize conformance judgments
(§21.1); until then all gap findings are preliminary observations.

Legend — validation_status: `SUPPORTED` (evidence-backed intent),
`PARTIALLY_SUPPORTED` (intent partly claim-level), `NEEDS_AUTHORITY` (approval
path the only missing piece).

| ID | Type | P | Strength | Origin | Validation | Verification method | Core evidence |
|---|---|---|---|---|---|---|---|
| REQ-STEMMA-CORE-001 | FUNCTIONAL | P0 | SHALL | RECOVERED | SUPPORTED | INSPECTION + gate run | EVID-GATE-003, CORE-001 |
| REQ-STEMMA-CORE-002 | DATA | P0 | SHALL | RECOVERED | SUPPORTED | STATIC_ANALYSIS (check_id_immutability, test_id_immutability) | EVID-CORE-003 |
| REQ-STEMMA-CORE-003 | CONSTRAINT | P0 | SHALL NOT | RECOVERED | SUPPORTED | STATIC_ANALYSIS (CI grep) | EVID-SEC-002 |
| REQ-STEMMA-CORE-004 | CONSTRAINT | P0 | SHALL NOT | RECOVERED | SUPPORTED | UNIT_TEST (test_generality) | gate chain |
| REQ-STEMMA-SCH-001 | DATA | P0 | SHALL | RECOVERED | SUPPORTED | UNIT_TEST (validate.py) | EVID-GATE-003 |
| REQ-STEMMA-SCH-002 | INTERFACE | P1 | SHALL | RECOVERED | SUPPORTED | UNIT_TEST (no_version_literals, docs-consistency) | EVID-SCH-001 |
| REQ-STEMMA-SCH-003 | DATA | P1 | SHALL | RECOVERED | SUPPORTED | UNIT_TEST (registry coherence) | EVID-SCH-003 |
| REQ-STEMMA-GATE-001 | BEHAVIORAL | P0 | SHALL | RECOVERED | SUPPORTED | INTEGRATION_TEST (negative-run; observed EVID-GATE-002) | EVID-GATE-002 |
| REQ-STEMMA-GATE-002 | BEHAVIORAL | P0 | SHALL | RECOVERED | SUPPORTED | UNIT_TEST (status_truth check) | EVID-GATE-006 |
| REQ-STEMMA-GATE-003 | OPERATIONAL | P1 | SHALL | RECOVERED | SUPPORTED | INSPECTION (ci.yml) | EVID-GATE-005, GATE-009 |
| REQ-STEMMA-GATE-004 | CONSTRAINT | P1 | SHALL | RECOVERED | SUPPORTED | UNIT_TEST (docs consistency) | EVID-GATE-007 |
| REQ-STEMMA-GATE-005 | CONSTRAINT | P1 | SHALL | RECOVERED | SUPPORTED | UNIT_TEST (independence) | EVID-GATE-008 |
| REQ-STEMMA-EXP-001 | BEHAVIORAL | P0 | SHALL | RECOVERED | SUPPORTED | UNIT_TEST + CI (byte-identical, no wall clock) | EVID-EXP-002 |
| REQ-STEMMA-EXP-002 | INTERFACE | P0 | SHALL | RECOVERED | SUPPORTED | UNIT_TEST (registry+vocab sidecar, VERSION match) | EVID-EXP-001, SCH-001 |
| REQ-STEMMA-EXP-003 | BEHAVIORAL | P1 | SHALL | RECOVERED | SUPPORTED | INTEGRATION_TEST (CI freshness diff) | EVID-GATE-005 |
| REQ-STEMMA-EXP-004 | INTERFACE | P1 | SHOULD | RECOVERED | PARTIALLY_SUPPORTED | INTEGRATION_TEST (consumer filter run) | EVID-EXP-006/-007, UNRES-STEMMA-EXP-001 |
| REQ-STEMMA-HITL-001 | SECURITY | P0 | SHALL | RECOVERED | SUPPORTED | INTEGRATION_TEST (hitl_check in gate) | EVID-HITL-001/-002, UNRES-STEMMA-HITL-001 |
| REQ-STEMMA-HITL-002 | CONSTRAINT | P1 | SHALL NOT | RECOVERED | SUPPORTED | INTEGRATION_TEST (hitl_check) | EVID-HITL-001 |
| REQ-STEMMA-SEC-001 | SECURITY | P1 | SHALL | RECOVERED | SUPPORTED | STATIC_ANALYSIS (gitleaks + grep CI) | EVID-SEC-001 |
| REQ-STEMMA-SEC-002 | SECURITY | P2 | SHALL NOT | EXTERNAL (XC-5) | NEEDS_AUTHORITY | INSPECTION (webapp key handling) | XC-5; webapp NOT_YET_ASSESSED |
| REQ-STEMMA-OPS-001 | OPERATIONAL | P1 | SHALL | DERIVED (from GATE-009) | SUPPORTED | MEASUREMENT (clean-env install+run) | EVID-GATE-004 |
| REQ-STEMMA-OPS-002 | OPERATIONAL | P2 | SHOULD | PROPOSED | NEEDS_AUTHORITY | INSPECTION (drift pattern) | EVID-OPS-004 (INFERENCE) |

## Requirement texts (normative statements)

- **REQ-STEMMA-CORE-001:** Canonical knowledge SHALL live only in `content/`,
  `connections/`, `sources/`; every other artifact SHALL be regenerable derived
  output or tooling. Acceptance: no consumer-guided reads of canonical markdown
  directly; consumers use the export (IFACE-STEMMA-EXP-001).
- **REQ-STEMMA-CORE-002:** Entity/source/connection IDs SHALL match the
  `stemma:` schema patterns and SHALL never be reused or reassigned; corrected
  claims are superseded, never edited in place (ADR-0014 lineage).
- **REQ-STEMMA-CORE-003:** Canonical data SHALL NOT contain embeddings,
  vectors, or RAG artifacts (derived-only, L6).
- **REQ-STEMMA-CORE-004:** Canonical data SHALL NOT contain curriculum, grade,
  course, country, or product semantics (L7 machine-checked).
- **REQ-STEMMA-SCH-001:** Every canonical object SHALL validate against its
  JSON Schema (concept/connection/source) in the gate.
- **REQ-STEMMA-SCH-002:** All version literals in derived artifacts SHALL be
  produced from `schema/VERSION.yaml`; hardcoded export/schema versions in
  producers are forbidden.
- **REQ-STEMMA-SCH-003:** The relation registry SHALL remain coherent: named
  inverses mutual and mirrored, symmetric relations carry no inverse,
  domain/range reference known entity types.
- **REQ-STEMMA-GATE-001:** The verification chain SHALL fail closed: any failed
  step terminates the chain with a non-zero exit.
- **REQ-STEMMA-GATE-002:** The README status block SHALL be regenerated from
  live canonical counts; drift fails CI.
- **REQ-STEMMA-GATE-003:** CI SHALL execute the full pytest suite and the
  all-green gate SHALL require its success.
- **REQ-STEMMA-GATE-004 / -005:** The docs-consistency (ADR-0029) and
  independence (ADR-0027/0051) invariants SHALL be executable gates, never
  documentation-only rules.
- **REQ-STEMMA-EXP-001:** Derived exports SHALL be deterministic:
  byte-identical regeneration, content-hash stamped, no wall clock.
- **REQ-STEMMA-EXP-002:** The export contract SHALL be versioned
  (`export_version`, currently 2.2.0) and evolve additively within a major
  version; the export SHALL carry relation-registry and vocabulary sidecars so
  consumers can introspect without cloning the producer.
- **REQ-STEMMA-EXP-003:** Committed derived artifacts (`exports/`, `reports/`)
  SHALL be fresh: CI regenerates and diffs them.
- **REQ-STEMMA-EXP-004:** Consumer exports SHOULD honor each consumer's
  declared `review_policy` (e.g., learninghub = canonical only). Caveat:
  UNRES-STEMMA-EXP-001 (empty-export intent unconfirmed).
- **REQ-STEMMA-HITL-001:** AI-drafted content SHALL remain `draft` until a
  named human reviews it; canonical objects declare `writer: human:*`.
- **REQ-STEMMA-HITL-002:** No object SHALL become canonical without an explicit
  human markdown edit recorded in the audit trail. Limitation:
  UNRES-STEMMA-HITL-001 (audit locality).
- **REQ-STEMMA-SEC-001:** The canonical layer SHALL be free of secrets;
  machine-checked on every change.
- **REQ-STEMMA-SEC-002:** Provider API keys SHALL NOT be committed; key
  material lives only in runtime configuration/credentials stores.
- **REQ-STEMMA-OPS-001:** A clean clone SHALL run the full gate after
  installing declared dependencies only.
- **REQ-STEMMA-OPS-002:** Living documents SHOULD NOT hardcode machine-owned
  counts/versions; single sources (status_truth, VERSION.yaml) own them.

## Gate 3 checklist (§31)

- [x] IDs valid (`REQ-STEMMA-<DOMAIN>-NNN`, domains registered)
- [x] domain registry complete (spec/DOMAIN_REGISTRY.md)
- [x] quality gate satisfied (per-requirement fields in requirements.yaml)
- [x] authority known (SOLE_OWNER; approver fields `null` = pending, not assumed)
- [x] acceptance criteria present
- [x] verification methods identified (none left permanently NOT_YET_DETERMINED;
      REQ-STEMMA-SEC-002 method = INSPECTION, scope-flagged)
- [x] requirement status correct (all PROPOSED; nothing silently APPROVED)
