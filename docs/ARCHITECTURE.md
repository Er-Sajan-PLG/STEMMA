# STEMMA — System Architecture — DEPRECATED, See ARCHITECTURE-V2.md

Status: Deprecated — authoritative is docs/ARCHITECTURE-V2.md clean constitutional foundation single part L1-L8 refined.

This file previously described comprehensive all-STEM mediocre coverage with HITL, PDF primary, evolvable templates v2.0.0, model selector like DeepSeek harness, embeddings, RAG, consumer export. Old 74 entities archived to archive/beginning-74-entities/. Now 1 entity (metre) via PDF primary ingestion with HITL, will grow to mediocre 400-800 across 8 domains.

New architecture v2 is in docs/ARCHITECTURE-V2.md — constitutional foundation clean single part L1-L8 refined, data model value-slot XOR target/value interim allowlist QUDT/UCUM/SI, semantic primitives, delegated authority v2 audited federation audit_frequency sample_audit_rate 10%/5% versioning revocation, scale 10^2–10^6 sharded YAML+LFS now content-addressed design later, 16-stage semantic acquisition pipeline evidence first-class AI output must be proposal independent verification deterministic+Verifier Model B conflict analysis explicit P=10 vs P=12 human review final authority, embedding and RAG producer vs consumer separation deterministic derived embeddings reference implementation export mechanism LearningHub PROFESSOR-J via OpenAPI file/API/SDK content_hash, standards alignment pluggable BFO schema.org SKOS QUDT Wikidata JSON-LD SHACL PROV-O Wikidata anchors, consumption contract deterministic export content-hash consumer views explorer clean small nodes thin lines manual legend centered zoom 8 domains.

Implementation plan is in docs/IMPLEMENTATION-PLAN-V2.md Phases 0-8 ideal order architecture → plan → work integrating early work.

Decisions are in docs/decisions/README.md 0040-0052 beginning no legacy.

Roadmap is in docs/ROADMAP.md Phases 0-8 ideal order.

Implementation status is in docs/IMPLEMENTATION-STATUS.md architecture v2 ideal order current counts 1 entity metre via HITL 0 connections 3 sources checks all green.

For new engineers, start with docs/ARCHITECTURE-V2.md then docs/IMPLEMENTATION-PLAN-V2.md then docs/decisions/README.md then docs/README.md reading order.

This file kept for historical reference but authoritative is ARCHITECTURE-V2.md.

## Old content preserved below for reference — see ARCHITECTURE-V2.md for authoritative

Previous content was comprehensive all-STEM mediocre coverage with HITL, PDF primary, evolvable templates v2.0.0, model selector like DeepSeek harness (local + frontier models), embeddings, RAG, consumer export for LearningHub, PROFESSOR-J. Old 74 entities archived to archive/beginning-74-entities/. Will grow to mediocre coverage across 8 domains: physics, chemistry, biology, earth-science, astronomy, computer-science, engineering, mathematics.

System layers previously:

```
CANONICAL LAYER (source of truth, in git, only after HITL)
  content/<domain>/**/*.md (1 entity now metre via HITL, will grow to mediocre all-domain)
  connections/*.yaml (0 now, will grow, 8 relations only, mandatory evidence)
  sources/*.yaml (3 canonical records)

INGESTION LAYER (PRIMARY — PDF, deterministic scales, evolvable, git-ignored workflow/)
  workflow/documents/<doc_id>/ (PDF uploads)
  workflow/extraction/<doc_id>.txt (deterministic poppler/tesseract)
  workflow/candidates/<doc_id>/<slug>.md (markdown preview deterministic templates v2.0.0 regex + exact constants OR AI draft frontier model)
  workflow/proposals/<slug>.md (human-approved markdown after explicit edit)
  workflow/audit/audit.jsonl (HITL audit)
  workflow/meta/<doc_id>.json

GATE (deterministic, no LLM, includes HITL)
  scripts/validate.py, physics_core_profile_check.py, physics_governing_check.py, hitl_check.py, evolvable_template.py, pdf_ingest_primary.py, embed.py, rag.py, export_consumers.py

DERIVED LAYER (regenerable, deterministic, content-hash, no wall clock)
  exports/knowledge.json v2.1.0 deterministic content-hash
  exports/embeddings.jsonl, vector_store/ FAISS, consumers/<consumer>/knowledge.<consumer>.json, openapi.yaml, reports/

CONSUMERS + EXPORT MECHANISM + RAG
  explorer/ clean 3D small nodes thin lines legend manual zoom centered domain filter 8 domains
  adapters/python/ v0.2.0 embeddings + RAG + consumer export
  webapp/ ingestion & review UI + RAG playground PDF primary deterministic draft + AI draft frontier model selector
  LearningHub, PROFESSOR-J

EMBEDDING + RAG LAYER
  embedding-registry.yaml 12 models, consumer-registry.yaml 4 consumers, api.yaml OpenAPI 3.0.3
```

Now authoritative is docs/ARCHITECTURE-V2.md.
