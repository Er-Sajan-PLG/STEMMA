# Canonical Content Validator Skill

**Purpose**: Teach an agent how to validate STEMMA canonical content across multiple layers (syntax, schema, semantic, referential, provenance, lifecycle, export readiness).

**When to Use**: When running validation, debugging validation failures, adding new validation rules, or reviewing canonical content quality.

**Mental Model**: Validation is a multi-stage pipeline. Each stage catches different classes of errors. The validator must be deterministic and produce machine-readable reports.

---

## Required Inputs
- STEMMA repository with `content/`, `connections/`, `sources/`, `schema/`
- Python 3 with PyYAML (jsonschema optional)

---

## Validation Pipeline Stages

### Stage 1: Syntax & Parse
- YAML frontmatter must be valid YAML
- No duplicate keys (deterministically rejected)
- Frontmatter delimiters `---` present and correct
- File encoding UTF-8

### Stage 2: Schema Conformance
- JSON Schema validation against `schema/concept.schema.json`
- Required fields present: `id`, `type`, `name`, `domain`, `status`, `definition`, `provenance`
- Enum values valid: type, status, relationship types, provenance.source_kind
- Extensions keys registered in `schema/extension-registry.yaml`

### Stage 3: ID & Identity
- ID format: `^lhs:[a-z][a-z0-9-]*\.[a-z0-9][a-z0-9-]*$`
- ID uniqueness across all entities
- Filename matches ID slug (`lhs:phys.force` → `force.md`)
- Aliases are valid IDs, not equal to own ID

### Stage 4: Semantic Constraints
- `applies_to` source must be `law` type
- `appears_in_law` target must be `law` type
- Quantity entities should have `unit` (INFO)
- Misconception entities should `related_to` a concept (WARNING)

### Stage 5: Referential Integrity
- All relationship targets resolve to existing entities
- No dangling references
- Connection source/target resolve to entities
- Evidence source_ref resolves to sources

### Stage 6: Provenance & Lifecycle
- `provenance.ai_drafted` is boolean
- `human_reviewed`/`canonical` require `provenance.reviewer`
- Deprecated/superseded entities have `deprecated_by`
- Connection provenance has `asserted_by`, `generated_by`, `method`
- Historical attribution: `stated_by` + `year` required when present

### Stage 7: Structural Validation
- **Cycle detection**: Structural transitive relations (`part_of`, `is_a`, `special_case_of`, `generalizes`, `equivalent_to`, `broader_than`, `narrower_than`) must not have cycles of length > 2
- **Inverse relationships**: For inverse pairs (generalizes↔special_case_of, part_of↔has_part, etc.), missing inverse is INFO (legacy data) but new content should include both
- **Entity-Connection consistency**: Inline `relationships[]` should be represented in first-class `connections/` (WARNING for drift)

### Stage 8: Extension Registry
- Every `extensions` key registered in `extension-registry.yaml`
- Registered dimension applies to this object kind (entity/connection/source)
- Controlled enum values respected
- Value type matches declaration

### Stage 9: Export Readiness
- All validation passes (exit 0)
- Export regenerates deterministically (same input → same output)
- Content hash computed from all canonical files
- Version metadata correct: `export_version`, `schema_version`, `kernel_version`

---

## Severity Levels

| Severity | Meaning | Blocks Export |
|----------|---------|---------------|
| **ERROR** | Invalid canonical content | YES |
| **WARNING** | Data quality issue, should fix | NO |
| **INFO** | Improvement suggestion | NO |

---

## Running Validation

```bash
# Full validation + export regeneration
python3 scripts/validate.py

# Check validation report
cat reports/validation-report.json
```

---

## Validation Report Format (SHACL-style)

```json
{
  "conforms": true|false,
  "results": [
    {
      "resultSeverity": "Violation|WARNING|INFO",
      "focusNode": "path/to/file.md",
      "resultPath": null,
      "resultMessage": "description of issue",
      "sourceConstraintComponent": "STEMMAValidator"
    }
  ],
  "generated_at": "ISO timestamp",
  "kernel_version": "1.0.0",
  "content_hash": "sha256"
}
```

---

## Common Fixes

| Error | Fix |
|-------|-----|
| "invalid stable ID format" | Check ID matches `lhs:<domain>.<slug>` pattern |
| "filename does not match id slug" | Rename file to match ID slug |
| "dangling relationship target" | Add missing entity or fix target ID |
| "applies_to requires law source" | Change source to law type or use different relationship |
| "missing inverse relationship" | Add inverse relationship to target entity (or accept as INFO) |
| "extension not registered" | Run `python3 scripts/register_extension.py add ...` |
| "duplicate YAML key" | Remove duplicate key in frontmatter |
| "status canonical requires reviewer" | Add `provenance.reviewer` |

---

## Extending Validation

To add new validation rules:
1. Add check function in `scripts/validate.py`
2. Call it in the appropriate phase in `main()`
3. Use `add_error(errors, message, severity)` 
4. Add test in `tests/metadata/` or `tests/curation/`
5. Document in this skill

---

## Escalation Conditions
- Validation exits 1 with unclear error → Check `reports/validation-report.json` for structured output
- False positive WARNING → Refine validation rule, don't just suppress
- New entity type needs validation → Add to TYPES enum, update semantic checks
- Schema change needed → Follow ADR process, bump schema_version