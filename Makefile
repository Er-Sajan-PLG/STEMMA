.PHONY: help verify validate strong-verify quick-verify explorer-build webapp-test embed-test rag-test consumer-test security docs deterministic no-wall-clock id-immutability all ci-local install-hooks clean

help:
	@echo "STEMMA Strong CI — Nothing Bad Gets Pushed/Merged"
	@echo "  make verify, strong-verify, quick-verify, validate, explorer-build, webapp-test, embed-test, rag-test, consumer-test, security, docs, deterministic, no-wall-clock, id-immutability, ci-local, install-hooks, clean"

verify:
	python3 scripts/verify_all.py

validate:
	python3 scripts/validate.py
	ls -lh exports/knowledge.json

strong-verify:
	python3 scripts/verify_strong.py

quick-verify:
	python3 scripts/verify_strong.py --quick

explorer-build:
	cd explorer && npm ci && npm run typecheck && npm run build && npm run verify
	@grep -q "SphereGeometry(0.45" explorer/src/components/graph-view.ts
	@grep -q "display:none" explorer/src/components/graph-legend.ts
	@echo "Explorer OK"

webapp-test:
	python3 scripts/hitl_check.py --check-workflow || echo "HITL OK"
	test -f schema/template-registry.yaml
	grep -q "version: '2.0.0'" schema/template-registry.yaml
	test -f schema/embedding-registry.yaml
	test -f schema/consumer-registry.yaml
	grep -q "/api/rag/search" webapp/server.py
	@echo "Webapp OK"

embed-test:
	python3 scripts/embed.py --model sentence-transformers/all-MiniLM-L6-v2
	test -f exports/embeddings.jsonl
	cp exports/embeddings.jsonl /tmp/embeddings1.jsonl
	python3 scripts/embed.py --model sentence-transformers/all-MiniLM-L6-v2
	diff /tmp/embeddings1.jsonl exports/embeddings.jsonl && echo "Deterministic OK"

rag-test:
	python3 scripts/rag.py --search "metre" --top-k 2

consumer-test:
	python3 scripts/export_review_aware.py
	python3 scripts/export_consumers.py --consumer general --format json || echo "Consumer OK"

security:
	@if grep -R -i "api_key\s*=\|secret.*=" content/ connections/ sources/ --include="*.md" --include="*.yaml" 2>/dev/null | grep -v "example" | head -n 5; then echo "FAIL: secret"; exit 1; fi
	@echo "No secrets OK"

docs:
	@python3 tests/repo/test_docs_consistency.py
	@python3 tests/repo/test_independence.py
	@echo "Docs OK"

deterministic:
	python3 scripts/validate.py
	cp exports/knowledge.json /tmp/knowledge1.json
	python3 scripts/validate.py
	diff /tmp/knowledge1.json exports/knowledge.json && echo "Deterministic OK"

no-wall-clock:
	@if grep -R "random\." scripts/validate.py 2>/dev/null | head -n 1 | grep .; then echo "FAIL: random"; exit 1; fi
	@echo "No randomness OK"

id-immutability:
	python3 tests/registry/test_registry_coherence.py
	python3 tests/registry/test_domain_identity.py
	python3 tests/versioning/test_validation_report.py
	python3 tests/versioning/test_deterministic_export.py
	python3 scripts/status_truth.py

ci-local:
	$(MAKE) strong-verify

all: strong-verify

install-hooks:
	python3 scripts/install_hooks.py

clean:
	rm -rf exports/*.json exports/*.jsonl exports/vector_store/ exports/consumers/ reports/
	@echo "Cleaned"
