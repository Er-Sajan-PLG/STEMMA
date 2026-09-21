# ADR-0049: Delegated Authority Tier v2 Audited Federation

Status: Decided
Date: 2026-09-21
Baseline: ADR-0044
Related: docs/ARCHITECTURE-V2.md Part 4

## Context

Canonicalization is human-only per L2. Per-claim re-review of external institutional work is redundant labor. Their verified work was reviewed by qualified humans under published standards. Need to extend "human" to include credentialed external review bodies operating under published standards with safeguards, not weaken L2.

Previous proposal had delegated authority without audit, sample, versioning, revocation — trust model underspecified, risk of trust dilution, heterogeneity, revocation workload, liability.

Need audited federation.

## Decision

Adopt delegated authority v2:

**Provenance extension** authority field internal|delegated in reviewed_by[] and review_history[] plus delegated_provenance block institution_id review_standard_url review_standard_version audit_date sample_audit_rate.

```yaml
provenance:
  reviewed_by:
    - type: human
      id: human:institution.wikidata-community
      authority: delegated
      delegated_provenance:
        institution_id: human:institution.wikidata-community
        review_standard_url: "https://www.wikidata.org/wiki/Wikidata:Verifiability"
        review_standard_version: "v3.2"
        audit_date: "2026-09-20"
        sample_audit_rate: 0.1
```

**Trusted Institution Registration** schema/agent-registry.yaml entry type institution:

```yaml
agents:
  - id: human:institution.biologists-kb
    type: institution
    name: "International Biological Knowledge Consortium"
    authority: delegated
    review_standard_url: "https://..."
    review_standard_version: "v2.1"
    contact: "review-board@..."
    registered_at: "2026-09-21"
    registered_by: "human:admin.sajan"
    status: active # active | revoked | suspended
    audit_frequency: annual
    sample_audit_rate: 0.1
    last_audit: "2026-09-20"
    next_audit: "2027-09-20"
```

Adding institution requires ADR-level governance decision per-institution human gate replacing per-claim gate with audit safeguards.

**Audit and Sample:**
- Every delegated import must pass L4 deterministic gates schema identity references vocabularies cycles
- Sample re-review 10% first 100 claims 5% ongoing
- Annual audit of institution review standard URL versioning
- Translation layer external evidence chains mapped to STEMMA Source/Document/Observation
- Unit translation via interim allowlist QUDT/UCUM/SI symbols
- Conflict detection still runs P=10 vs P=12 CONFLICT explicit do not force average
- Audit report reports/delegated-audit-<institution>.{md,json} gate-generated freshness-checked

**Import Semantics:**
- External verified claims enter canonical with authority delegated
- L4 deterministic gates still run on every import
- Original IDs preserved as external_ids anchors
- Original evidence chains preserved as source_ref pointers translated to STEMMA schema
- Revocation if revoked/suspended claims transition to unreviewed require re-review consumers notified via exports/views/changelog.json integrity manifest
- Revocation cost re-review 10% sample Hours per 100 claims full revocation Days per 1000

**Consumer Surface:**
Export contract exposes authority field consumers filter:
- review.status == canonical AND authority == internal STEMMA-reviewed
- review.status == canonical AND authority == delegated institution-verified
- Both canonical both trustworthy but different audit trails consumers choose trust threshold trust score based on audit recency sample pass rate LearningHub may choose internal only for physics-core PROFESSOR-J may choose both for mediocre all 8 domains

## Consequences

Easier: importing verified work from trusted institutions without redundant review but with audit sample versioning, scaling to 10^5–10^6, preserving credit.

Harder: delegated authority v2 requires maintaining institution registry audit_frequency sample_audit_rate last_audit next_audit revocation procedures translation layer, maintaining audit sample re-review workload.

Hard to undo: once delegated authority granted revoking requires transitioning claims to unreviewed re-review consumers notified.

## Verification

- authority delegated without registered institution → error
- Unknown institution ID → error
- Institution without review_standard_url/version → error
- Sample audit rate <5% → warning
- Institution status revoked/suspended claims still canonical → error
- L4 deterministic gates still run on every import

## Related

- ADR-0044 L2, Part 4
- docs/ARCHITECTURE-V2.md Part 4
- schema/agent-registry.yaml
