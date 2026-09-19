# STEMMA Knowledge Graph Architecture

**Status:** Proposed
**Author:** Sajan (Principal Architect)
**Date:** 2026-09-19
**Version:** 1.0.0

---

## Executive Summary

STEMMA evolves from a static knowledge base into a **Semantic Web Knowledge Graph** built on three state-of-the-art foundations:

1. **BFO (Basic Formal Ontology)** — The conceptual foundation (what exists)
2. **JSON-LD / URIs** — The identity foundation (what it's called everywhere)
3. **Description Logic (OWL)** — The mathematical foundation (what can be inferred)

These foundations enable an **AI-accelerated curation pipeline** where experts review AI-generated drafts, corrections feed back into the system, and accuracy increases with every cycle.

---

## Part 1: The Three Foundations

### 1.1 BFO — The Conceptual Foundation

**Source:** Basic Formal Ontology 2020 (ISO/IEC 21838-2)
**License:** CC BY 4.0
**Repository:** https://github.com/bfo-ontology/BFO-2020

BFO defines what exists in the universe. It prevents category errors (e.g., "a process cannot have mass").

#### Top-Level BFO Classes for STEMMA

```
BFO Entity
├── Continuant (exists at a point in time)
│   ├── Independent Continuant
│   │   ├── Object (electron, atom, cell)
│   │   ├── Object Aggregate (molecule, crystal)
│   │   └── Fiat Object Part (system, component)
│   ├── Specifically Dependent Continuant
│   │   ├── Quality (mass, temperature, velocity)
│   │   └── Realizable Entity
│   │       ├── Role (student, catalyst)
│   │       ├── Function (to accelerate, to catalyze)
│   │       └── Disposition (solubility, conductivity)
│   └── Generically Dependent Continuant
│       └── Information Content Entity (equation, law, definition)
└── Occurrent (unfolds over time)
    ├── Process (acceleration, reaction, diffusion)
    ├── Process Boundary (start of reaction, end of measurement)
    ├── Temporal Interval (duration, instant)
    └── Spatiotemporal Interval (trajectory, wave propagation)
```

#### STEMMA Entity Type Mapping

| STEMMA Type | BFO Class | Example |
|-------------|-----------|---------|
| concept | `bfo:GenericallyDependentContinuant` | Force, Energy |
| quantity | `bfo:Quality` | Mass, Velocity, Temperature |
| unit | `bfo:GenericallyDependentContinuant` | Kilogram, m/s |
| law | `bfo:GenericallyDependentContinuant` | Newton's Second Law |
| equation | `bfo:GenericallyDependentContinuant` | F = m · a |
| misconception | `bfo:GenericallyDependentContinuant` | "Heavier objects fall faster" |
| process | `bfo:Process` | Acceleration, Chemical Reaction |
| phenomenon | `bfo:Process` | Gravity, Diffusion |

### 1.2 JSON-LD / URIs — The Identity Foundation

**Source:** W3C JSON-LD 1.1 Recommendation
**License:** Open standard
**Specification:** https://www.w3.org/TR/json-ld11/

Every entity gets a **dereferenceable URI** that serves as its universal identifier.

#### URI Convention

```
https://stemma.org/entity/{id}
```

Where `{id}` follows the pattern: `lhs:{domain}.{slug}`

Examples:
- `https://stemma.org/entity/lhs:phys.force`
- `https://stemma.org/entity/lhs:chem.chemical-bond`
- `https://stemma.org/entity/lhs:math.derivative`

#### @context Vocabulary

```json
{
  "@context": {
    "bfo": "http://purl.obolibrary.org/obo/bfo.owl#",
    "obo": "http://purl.obolibrary.org/obo/",
    "stemma": "https://stemma.org/vocab#",
    "schema": "https://schema.org/",
    "dcterms": "http://purl.org/dc/terms/",
    "owl": "http://www.w3.org/2002/07/owl#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xsd": "http://www.w3.org/2001/XMLSchema#",

    "id": "@id",
    "type": "@type",
    "name": "schema:name",
    "definition": "stemma:definition",
    "domain": "stemma:domain",
    "status": "stemma:reviewStatus",
    "provenance": "stemma:provenance",
    "source": "dcterms:source",
    "confidence": "stemma:confidenceScore",
    "reviewedBy": "stemma:reviewedBy",
    "createdAt": "dcterms:created",
    "updatedAt": "dcterms:modified"
  }
}
```

### 1.3 Description Logic — The Mathematical Foundation

**Source:** W3C OWL 2 Web Ontology Language
**License:** Open standard
**Specification:** https://www.w3.org/TR/owl2-overview/

DL provides formal semantics for relationships, enabling automated reasoning.

#### Property Characteristics

| Characteristic | Symbol | Meaning | Example |
|----------------|--------|---------|---------|
| Transitive | `∀x,y,z: R(x,y) ∧ R(y,z) → R(x,z)` | Chains | `part_of` |
| Symmetric | `∀x,y: R(x,y) ↔ R(y,x)` | Bidirectional | `adjacent_to` |
| Asymmetric | `∀x,y: R(x,y) → ¬R(y,x)` | One-way | `is_a` |
| Functional | `∀x: ∃!y: R(x,y)` | Unique value | `has_SI_unit` |
| InverseFunctional | `∀y: ∃!x: R(x,y)` | Unique identifier | `has_URI` |
| Reflexive | `∀x: R(x,x)` | Self-related | `is_equivalent_to` |

#### STEMMA Relationship Vocabulary (OWL-Aligned)

| Predicate | BFO/OBO Mapping | Transitive | Domain | Range |
|-----------|-----------------|------------|--------|-------|
| `is_a` | `rdfs:subClassOf` | Yes | Entity | Entity |
| `part_of` | `bfo:BFO_0000050` | Yes | Continuant | Continuant |
| `has_part` | `bfo:BFO_0000051` | Yes | Continuant | Continuant |
| `participates_in` | `bfo:BFO_0000056` | No | Continuant | Process |
| `has_participant` | `bfo:BFO_0000057` | No | Process | Continuant |
| `derives_from` | `bfo:BFO_0000066` | Yes | Process | Process |
| `precedes` | `bfo:BFO_0000063` | Yes | Occurrent | Occurrent |
| `immediately_precedes` | `bfo:BFO_0000062` | No | Occurrent | Occurrent |
| `has_quality` | `bfo:BFO_0000111` | No | IndependentContinuant | Quality |
| `has_disposition` | `bfo:BFO_0000054` | No | IndependentContinuant | Disposition |
| `realizes` | `bfo:BFO_0000055` | No | Process | RealizableEntity |
| `has_output` | — | No | Process | Continuant |
| `has_input` | — | No | Process | Continuant |
| `mathematically_equivalent_to` | — | Yes | Equation | Equation |
| `logically_requires` | — | Yes | Concept | Concept |
| `common_misconception` | — | No | Concept | Misconception |
| `has_formula` | — | No | Law | Equation |
| `has_unit` | — | No | Quantity | Unit |
| `measured_in` | — | No | Quantity | Unit |

---

## Part 2: Schema — The Shared Contract

### 2.1 Role of Schema

Schema is the **tangible contract** that makes BFO, JSON-LD, and DL enforceable. Both STEMMA and consumers validate against it.

```
BFO (Conceptual) ──→ Schema (Serialization) ←── JSON-LD (Identity)
                                    │
                                    ↓
                        Description Logic (Reasoning)
```

### 2.2 Entity Schema (concept.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://stemma.org/schema/concept/v1.0",
  "title": "STEMMA Entity",
  "description": "A canonical knowledge entity conforming to BFO, JSON-LD, and OWL standards",
  "type": "object",
  "required": ["id", "type", "name", "domain", "status", "definition", "provenance"],
  "properties": {
    "id": {
      "type": "string",
      "pattern": "^lhs:[a-z]+\\.[a-z0-9\\-]+$",
      "description": "Unique identifier (e.g., lhs:phys.force)"
    },
    "type": {
      "type": "string",
      "enum": ["concept", "quantity", "unit", "law", "equation", "misconception", "process", "phenomenon"],
      "description": "STEMMA entity type"
    },
    "bfo_class": {
      "type": "string",
      "format": "uri",
      "description": "BFO class URI (e.g., http://purl.obolibrary.org/obo/BFO_0000031)"
    },
    "uri": {
      "type": "string",
      "format": "uri",
      "description": "Dereferenceable URI (e.g., https://stemma.org/entity/lhs:phys.force)"
    },
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 200
    },
    "definition": {
      "type": "string",
      "minLength": 10,
      "maxLength": 2000
    },
    "domain": {
      "type": "string",
      "enum": ["physics", "chemistry", "biology", "math", "computing", "engineering", "earth-space", "scientific-practice"]
    },
    "status": {
      "type": "string",
      "enum": ["draft", "proposed", "reviewed", "canonical", "deprecated"],
      "description": "Review status"
    },
    "provenance": {
      "type": "object",
      "required": ["source"],
      "properties": {
        "source": {
          "type": "string",
          "description": "Citation or reference"
        },
        "confidence": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "AI confidence score at generation time"
        },
        "reviewed_by": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Expert reviewers"
        },
        "cycle": {
          "type": "integer",
          "description": "AI correction cycle number"
        }
      }
    },
    "relationships": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["predicate", "target"],
        "properties": {
          "predicate": {
            "type": "string",
            "description": "OWL-aligned relationship predicate"
          },
          "target": {
            "type": "string",
            "description": "Target entity ID"
          },
          "metadata": {
            "type": "object",
            "properties": {
              "confidence": { "type": "number" },
              "source": { "type": "string" },
              "notes": { "type": "string" }
            }
          }
        }
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "grade_levels": {
          "type": "array",
          "items": { "type": "integer", "minimum": 1, "maximum": 16 }
        },
        "curriculum_refs": {
          "type": "array",
          "items": { "type": "string" }
        },
        "tags": {
          "type": "array",
          "items": { "type": "string" }
        },
        "language": {
          "type": "string",
          "default": "en"
        }
      }
    }
  },
  "additionalProperties": false
}
```

### 2.3 Connection Schema (connection.schema.json)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://stemma.org/schema/connection/v1.0",
  "title": "STEMMA Relationship Assertion",
  "type": "object",
  "required": ["source", "predicate", "target"],
  "properties": {
    "source": {
      "type": "string",
      "pattern": "^lhs:[a-z]+\\.[a-z0-9\\-]+$"
    },
    "predicate": {
      "type": "string",
      "description": "OWL-aligned predicate from relation registry"
    },
    "target": {
      "type": "string",
      "pattern": "^lhs:[a-z]+\\.[a-z0-9\\-]+$"
    },
    "transitive": {
      "type": "boolean",
      "description": "Whether this relationship is transitive per OWL semantics"
    },
    "provenance": {
      "type": "object",
      "properties": {
        "source": { "type": "string" },
        "confidence": { "type": "number" }
      }
    }
  }
}
```

---

## Part 3: AI-Accelerated Curation Pipeline

### 3.1 Pipeline Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SOURCES                                          │
│  Textbooks │ Papers │ Wikipedia │ Curriculum docs │ Expert submissions  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  AI EXTRACTION (Cycle N)                                                │
│                                                                          │
│  Input: Raw text + Correction Database (cycles 1..N-1)                  │
│  Output: Draft entities, relationships, provenance                      │
│                                                                          │
│  Components:                                                             │
│  • Entity extractor (identifies concepts, laws, equations)               │
│  • BFO classifier (maps to BFO classes)                                  │
│  • Relationship extractor (identifies predicates)                        │
│  • Provenance extractor (captures citations)                             │
│  • Confidence scorer (flags low-confidence for review)                   │
│                                                                          │
│  Confidence: 60-70% (cycle 1) → 95%+ (cycle 20+)                       │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  AUTOMATED VALIDATION (Deterministic)                                    │
│                                                                          │
│  • Schema conformance check                                              │
│  • BFO category validation (no process with mass)                        │
│  • URI format verification                                               │
│  • Dangling reference detection                                          │
│  • Transitivity consistency check                                        │
│  • Duplicate detection                                                   │
│                                                                          │
│  Pass → Route to expert review                                           │
│  Fail → Return to AI for re-extraction                                   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  EXPERT REVIEW                                                           │
│                                                                          │
│  Routes by confidence:                                                   │
│  • < 70%  → Full review (read, correct, annotate)                        │
│  • 70-90% → Spot-check (verify key fields)                               │
│  • > 90%  → Audit sample (random 5% check)                               │
│                                                                          │
│  Actions:                                                                │
│  ✓ Approve → status: canonical                                           │
│  ✗ Reject  → Log correction → status: draft                             │
│  ✎ Modify  → Log diff → status: reviewed                                │
│                                                                          │
│  Every rejection/modification → Correction Database                      │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  CORRECTION DATABASE (The Training Asset)                                │
│                                                                          │
│  Stores:                                                                 │
│  • Original AI draft                                                     │
│  • Expert correction                                                     │
│  • Error classification                                                 │
│  • Entity metadata (domain, cycle, confidence)                           │
│                                                                          │
│  Usage:                                                                  │
│  • Fine-tune AI model for next cycle                                     │
│  • Generate negative examples                                            │
│  • Track accuracy metrics per domain                                     │
│  • Identify systematic errors                                            │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                            Cycle N+1 begins
```

### 3.2 Correction Taxonomy

| Error Type | Description | AI Fix Strategy |
|------------|-------------|-----------------|
| `factual` | Wrong definition/value | Retrain on corrected pairs |
| `category_error` | Wrong BFO class | Update mapping rules |
| `relationship_error` | Wrong predicate | Update relation constraints |
| `provenance_error` | Missing/bad source | Learn source preferences |
| `incompleteness` | Missing required field | Update schema prompts |
| `hallucination` | Fabricated information | Add source verification step |
| `format_error` | Schema non-conformance | Fix serializer |
| `dangling_ref` | Target entity doesn't exist | Validate before output |

### 3.3 Correction Log Schema

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://stemma.org/schema/correction/v1.0",
  "title": "Expert Correction Log Entry",
  "type": "object",
  "required": ["id", "entity_id", "cycle", "ai_draft", "expert_correction", "error_type", "timestamp"],
  "properties": {
    "id": { "type": "string" },
    "entity_id": { "type": "string" },
    "cycle": { "type": "integer" },
    "ai_draft": {},
    "expert_correction": {},
    "error_type": {
      "type": "string",
      "enum": ["factual", "category_error", "relationship_error", "provenance_error", "incompleteness", "hallucination", "format_error", "dangling_ref"]
    },
    "domain": { "type": "string" },
    "ai_confidence": { "type": "number" },
    "reviewed_by": { "type": "string" },
    "timestamp": { "type": "string", "format": "date-time" }
  }
}
```

### 3.4 Cycle Metrics

| Metric | Cycle 1 | Cycle 5 | Cycle 10 | Cycle 20 |
|--------|---------|---------|----------|----------|
| AI draft accuracy | 60% | 80% | 90% | 95% |
| Expert rejections/entity | 3.2 | 1.5 | 0.7 | 0.3 |
| Review time/entity | 12 min | 6 min | 3 min | 1 min |
| Corrections needed | 45% | 20% | 10% | 5% |

---

## Part 4: Distribution Architecture

### 4.1 Deployment Topology

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         STEMMA SERVICE                                   │
│                                                                          │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐                 │
│  │  Authoring   │    │  Validation │    │  API Gateway │                │
│  │  (Git + MD) │───▶│  (Schema)   │───▶│  (REST/SPARQL)│               │
│  └─────────────┘    └─────────────┘    └──────┬──────┘                 │
│                                                │                         │
│  ┌─────────────┐    ┌─────────────┐           │                         │
│  │  Graph DB   │◀───│  Full-Text  │◀──────────┘                         │
│  │  (Neo4j/    │    │  (Meilisearch│                                    │
│  │   Dgraph)   │    │  /ES)       │                                     │
│  └─────────────┘    └─────────────┘                                     │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │  Polyglot Storage                                                │    │
│  │  • Graph: relationships, reasoning, traversal                    │    │
│  │  • Search: fuzzy, autocomplete, typo-tolerant                    │    │
│  │  • Time-series: provenance history, review audit                 │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  CLOUDFLARE CDN (Global Edge)                                           │
│                                                                          │
│  • Cache hot entities at 300+ PoPs                                       │
│  • Sub-50ms response for cached data                                     │
│  • Stale-while-revalidate for updates                                    │
│  • Webhook-triggered cache invalidation                                  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
   LearningHub               STEM-GAME              PROFESSOR-J
   (pre-build +              (runtime API           (runtime API
    runtime API)              + cache)                + cache)
```

### 4.2 API Endpoints

| Endpoint | Method | Purpose | Cache |
|----------|--------|---------|-------|
| `/entities/{id}` | GET | Get entity by URI | 1 hour |
| `/entities` | GET | Paginated list | 5 min |
| `/entities/search?q=` | GET | Fuzzy search | 10 min |
| `/entities/{id}/related` | GET | Traverse relationships | 30 min |
| `/query` | POST | SPARQL endpoint | No cache |
| `/export/knowledge.json` | GET | Full export | 24 hour |
| `/health` | GET | Health check | No cache |
| `/webhook/invalidate` | POST | Cache purge | No cache |

### 4.3 Consumer SDK

```typescript
// @stemma/client
import { STEMMAClient } from '@stemma/client';

const stemma = new STEMMAClient({
  endpoint: 'https://stemma.org',
  cache: { type: 'lru', maxSize: 10000 },
  retry: { attempts: 3, backoff: 'exponential' }
});

// Type-safe, cached entity lookup
const force = await stemma.getEntity('lhs:phys.force');

// Relationship traversal
const related = await stemma.getRelated('lhs:phys.force', {
  predicate: 'part_of',
  depth: 2
});

// Search
const results = await stemma.search('newton law', { limit: 10 });
```

---

## Part 5: Cost Model

### 5.1 Cost by Scale

| Scale | Entities | Users | Monthly Cost |
|-------|----------|-------|--------------|
| Seed | 1-1K | 100 | $0 (free tiers) |
| Growth | 1K-100K | 1K-10K | $50-200 |
| Scale | 100K-1M | 10K-100K | $200-1,000 |
| Massive | 1M-1B | 100K-10M | $1,000-10,000 |
| Global | 1B+ | 10M+ | $10,000+ |

### 5.2 Service Costs (Estimated)

| Service | Free Tier | At Scale |
|---------|-----------|----------|
| Cloudflare Workers | 100K req/day | $5+/mo |
| Cloudflare CDN | Unlimited bandwidth | $0 (included) |
| Neo4j AuraDB | 200K nodes | $50-500/mo |
| Meilisearch Cloud | 100K docs | $50-200/mo |
| GitHub Actions | 2,000 min/mo | $0.008/min |

### 5.3 AI Curation Costs

| Phase | AI Cost | Expert Cost | Total/mo |
|-------|---------|-------------|----------|
| Cycle 1-5 | $200-500 | $2,000-5,000 | $2,500-5,500 |
| Cycle 6-10 | $100-200 | $1,000-2,000 | $1,200-2,200 |
| Cycle 11+ | $50-100 | $500-1,000 | $600-1,100 |

---

## Part 6: Implementation Phases

### Phase 1: Foundation (Current Quarter)
- [ ] Adopt BFO-2020 as upper ontology
- [ ] Define JSON-LD @context and URI scheme
- [ ] Align relation-registry with OWL predicates
- [ ] Update concept.schema.json and connection.schema.json

### Phase 2: Pipeline (Next Quarter)
- [ ] Build AI extraction pipeline with correction logging
- [ ] Implement expert review UI
- [ ] Create feedback loop (corrections → retraining)
- [ ] Deploy to Cloudflare Workers

### Phase 3: Scale (6-12 months)
- [ ] Add graph database (Neo4j/Dgraph)
- [ ] Add search index (Meilisearch)
- [ ] Build consumer SDK (@stemma/client)
- [ ] Onboard first external consumer

### Phase 4: Community (12-24 months)
- [ ] Open-source the pipeline
- [ ] Onboard external expert reviewers
- [ ] Integrate with Wikidata/DBpedia
- [ ] Publish SPARQL endpoint

---

## Part 7: Example Entity (New Format)

```json
{
  "@context": "https://stemma.org/context/v1.0.jsonld",
  "@id": "https://stemma.org/entity/lhs:phys.force",
  "@type": "stemma:concept",
  "bfo:class": "http://purl.obolibrary.org/obo/BFO_0000031",
  "name": "Force",
  "definition": "A push or pull upon an object resulting from its interaction with another object. Force is a vector quantity with both magnitude and direction.",
  "domain": "physics",
  "status": "canonical",
  "provenance": {
    "source": "Halliday, Resnick & Walker. Fundamentals of Physics, 10ed. Chapter 4.",
    "confidence": 0.97,
    "reviewed_by": ["expert_001"],
    "cycle": 5
  },
  "relationships": [
    {
      "predicate": "mathematically_equivalent_to",
      "target": "lhs:phys.equation.newtons-second-law",
      "metadata": { "confidence": 0.95 }
    },
    {
      "predicate": "has_quality",
      "target": "lhs:phys.quantity.mass",
      "metadata": { "confidence": 0.92 }
    },
    {
      "predicate": "participates_in",
      "target": "lhs:phys.process.acceleration",
      "metadata": { "confidence": 0.88 }
    }
  ],
  "metadata": {
    "grade_levels": [9, 10, 11, 12],
    "curriculum_refs": ["NEB-G10-PHYS", "SEE-SCIENCE"],
    "tags": ["mechanics", "classical-physics", "vector-quantity"]
  }
}
```

---

## Appendix: Standards Reference

| Standard | URL | License |
|----------|-----|---------|
| BFO-2020 | https://github.com/bfo-ontology/BFO-2020 | CC BY 4.0 |
| OWL 2 | https://www.w3.org/TR/owl2-overview/ | W3C (open) |
| JSON-LD 1.1 | https://www.w3.org/TR/json-ld11/ | W3C (open) |
| RDF 1.1 | https://www.w3.org/TR/rdf11-concepts/ | W3C (open) |
| Schema.org | https://schema.org/ | CC BY-SA |
| OBO Foundry | https://obofoundry.org/ | CC BY 4.0 |
| Wikidata | https://wikidata.org/ | CC0 |
