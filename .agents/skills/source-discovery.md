# Source Discovery Skill

**Purpose:** Teaches an agent how to find appropriate sources for a STEM domain or topic.

**When to Use:** When acquiring knowledge for a new domain, expanding coverage, or updating existing content.

**Mental Model:** Sources are the raw material of canonical knowledge. Discovery must be systematic, not opportunistic.

---

## Required Inputs
- Target domain/topic
- Current coverage gaps (from export analysis)
- Source type requirements

---

## Workflow

### 1. Identify Coverage Gaps
```bash
# Analyze export for domains with few entities
python3 -c "
import json
data = json.load(open('exports/knowledge.json'))
from collections import Counter
domains = Counter(e['domain'] for e in data['entities'])
for d, c in sorted(domains.items(), key=lambda x: x[1]):
    print(f'{d}: {c}')
"
```

### 2. Source Discovery Strategies

| Strategy | Tools | Use Case |
|----------|-------|----------|
| **Textbook survey** | WorldCat, Library of Congress, publisher catalogs | Foundational domain coverage |
| **Standard specifications** | IUPAC, ISO, SI Brochure, NIST | Authoritative definitions |
| **Review articles** | PubMed, arXiv, Google Scholar | State-of-the-art summaries |
| **Open educational resources** | MIT OCW, Khan Academy, OpenStax | Freely licensed content |
| **Institutional publications** | NIST, NASA, WHO, national labs | Authoritative data |
| **Structured datasets** | NIST Chemistry WebBook, PDB, UniProt | Quantitative data |

### 3. Source Evaluation Checklist
Before registering a source, verify:
- [ ] Authoritative publisher/institution
- [ ] Clear licensing (prefer open)
- [ ] Stable identifiers (DOI, ISBN)
- [ ] Recent enough for domain
- [ ] Peer-reviewed or equivalent authority
- [ ] Accessible (PDF, web, API)

### 4. Registration
```bash
# Register source manually
python3 scripts/register_source.py --type textbook --title "..." --authors "..." --year 2023 --doi "..." --license "CC BY 4.0"
```

---

## Anti-Patterns
| Don't | Do |
|-------|----|
| Use random web pages as sources | Prefer institutional/authoritative sources |
| Ignore license terms | Check and record license for every source |
| Register without DOI/ISBN | Always capture stable identifiers |
| Assume accessibility = reusability | Verify license terms explicitly |

---

## Escalation Conditions
- No authoritative source found for a domain → Document gap, flag for human expert
- License unclear → Flag for legal review
- Source paywalled with no open alternative → Flag for budget/access decision