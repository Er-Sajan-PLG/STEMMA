# webapp/ — stdlib HITL ingestion & review UI

Local-only stdlib Python webapp: PDF-primary ingestion (deterministic template
extraction, LLM frontier fallback), markdown preview with explicit human edit,
proposals for review, RAG playground, model selector, consumer export.

- **Run:** `python3 webapp/app.py` then open http://localhost:8000 (local machine)
- **Config:** `webapp/config/{rules,settings}.yaml` (synced; CI-enforced) + root `.env` for provider keys (see ../.env.example)
- **HITL boundary:** nothing here writes canonical content directly — candidates
  flow through `workflow/` audit + `scripts/hitl_check.py` before `content/`
- Full docs: [../docs/WEBAPP.md](../docs/WEBAPP.md) · Protocol: [../docs/INGESTION-PRIMARY.md](../docs/INGESTION-PRIMARY.md)
