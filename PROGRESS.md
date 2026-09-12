# STEMMA Progress Tracker

## Current Sprint
**Goal**: Complete ingestion webapp + consolidate into upstream `webapp/`

---

## ✅ Done
- [x] Sync with origin/main (refoundation: ADR-0023-0038)
- [x] Clean canonical knowledge base (archived test content to `archive/`)
- [x] Fix ingestion webapp (port 8002, stemma: prefix)
- [x] Fix 3D Explorer (port 5176, v2.1.0 export)
- [x] Clean git branches (deleted 16 obsolete remote branches)
- [x] Create agent rules (.agent-rules.md)
- [x] Create pre-commit config (core validation only)
- [x] Create commit helper script (scripts/commit.sh)
- [x] Create GitHub Actions CI workflow
- [x] Fix all tests for empty knowledge base state
- [x] Pre-commit hooks installed and passing

## 🔄 In Progress
- [ ] Port ingestion webapp features to upstream `webapp/`
  - [x] Multi-provider LLM Studio (Google, OpenRouter, NVIDIA, OpenCode)
  - [x] Free model fetcher with API key management
  - [x] 5-stage review + side-by-side verification
  - [x] Proposal artifact editor with gate re-verification
  - [x] LLM Quick-Access Sidebar Panel
- [ ] Run full verify_all.py chain (requires campaign files)

## 📋 Backlog
- [x] Progress bar / spinner for long operations
- [x] Better error messages with actionable suggestions
- [x] Audit log UI in webapp
- [ ] Export version migration tooling
- [ ] Documentation: WEBAPP.md, INGESTION.md updates
- [ ] ADR for webapp consolidation

---

## Automation Status
| Feature | Status |
|---------|--------|
| Pre-commit hooks | ✅ Installed (core validation only) |
| GitHub Actions CI | ✅ Created (.github/workflows/ci.yml) |
| Commit helper script | ✅ Created (scripts/commit.sh) |
| Agent rules | ✅ Created (.agent-rules.md) |
| Pre-commit config | ✅ Created (.pre-commit-config.yaml) |
| Version bump reminder | ✅ In pre-commit |
| Doc sync on commit | ✅ Partial (commit.sh does AGENTS.md) |
| CI pipeline | ✅ GitHub Actions (validate, test, webapp, explorer, docs) |

---

## Next Actions (Priority)
1. Review `feat/adaptive-metadata-grade12` branch (69 Grade-12 entities + ADR-0017)
2. Port LLM Studio features to upstream `webapp/`
3. Push `feat/ingestion-webapp-sync` for PR
4. Run `python3 scripts/verify_all.py` to confirm full chain (requires campaign files)
5. Port ingestion webapp features to upstream `webapp/`

---

## Current State
- **Canonical Knowledge**: Empty (0 entities, 0 connections) - all test content archived to `archive/`
- **Validation**: Exit 0 ✅
- **Export**: v2.1.0, 0 entities, 0 connections
- **Webapp**: http://localhost:8002/ (ingestion), http://localhost:5176/ (explorer)
- **Git**: `feat/ingestion-webapp-sync` branch ready for PR
