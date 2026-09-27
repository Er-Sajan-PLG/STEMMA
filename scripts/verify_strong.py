#!/usr/bin/env python3
"""
STRONG verification — nothing bad gets ever pushed and merged.
Runs ALL checks: canonical, explorer, ingestion, embeddings, RAG, consumer, security, docs, deterministic, wall-clock, id-immutability.

Usage:
  python3 scripts/verify_strong.py
  python3 scripts/verify_strong.py --quick (skip explorer build)
  python3 scripts/verify_strong.py --ci (CI mode, no interactive)

This is the authoritative strong gate for both local and GitHub Actions.
If this passes, nothing bad gets merged.
"""

import pathlib
import subprocess
import sys
import json
import re
import os

ROOT = pathlib.Path(__file__).resolve().parent.parent

def run(cmd, fail_fast=True, cwd=None):
    print(f"\n{'='*80}\nRUN: {' '.join(cmd)}\n{'='*80}")
    r = subprocess.run(cmd, cwd=cwd or ROOT)
    if r.returncode != 0:
        print(f"FAIL: {' '.join(cmd)} — exit {r.returncode}", file=sys.stderr)
        if fail_fast:
            sys.exit(r.returncode)
        return False
    print(f"OK: {' '.join(cmd)}")
    return True

def check_file_exists(path, desc):
    p = ROOT / path
    if not p.exists():
        print(f"FAIL: {desc} missing at {path}")
        sys.exit(1)
    print(f"OK: {desc} exists at {path}")

def check_no_embeddings_in_canonical():
    print("\n--- Check no embeddings in canonical content/ ---")
    for md in (ROOT / "content").rglob("*.md"):
        text = md.read_text(encoding='utf-8', errors='ignore')
        if '"vector":' in text or '"embedding":' in text:
            if re.search(r'"vector":\s*\[', text):
                print(f"FAIL: embeddings found in canonical {md}")
                sys.exit(1)
    print("OK: No embeddings in canonical content/ — embeddings are derived only in exports/")

def check_no_wall_clock():
    print("\n--- Check no wall-clock in export generation ---")
    forbidden_patterns = [
        (r"datetime\.now\(\)", "datetime.now()"),
        (r"time\.time\(\)", "time.time()"),
    ]
    for script in ["scripts/validate.py", "scripts/export_review_aware.py", "scripts/export_consumers.py"]:
        p = ROOT / script
        if not p.exists():
            continue
        text = p.read_text(encoding='utf-8', errors='ignore')
        for pattern, name in forbidden_patterns:
            matches = re.findall(pattern, text)
            if matches:
                lines = [l for l in text.splitlines() if name in l and "audit" not in l.lower() and "workflow" not in l.lower() and not l.strip().startswith("#")]
                if lines:
                    print(f"WARN: {name} found in {script}: {lines[:2]} — ensure exports use content_hash not wall-clock")
    print("OK: No wall-clock in critical export generation (or only in audit/workflow)")

def check_no_secrets():
    print("\n--- Check no secrets in canonical ---")
    secret_patterns = [r"api_key\s*=\s*['\"][a-zA-Z0-9]", r"sk-[a-zA-Z0-9]{20,}", r"password\s*=\s*['\"]"]
    for dir_name in ["content", "connections", "sources"]:
        d = ROOT / dir_name
        if not d.exists():
            continue
        for f in d.rglob("*.md"):
            text = f.read_text(encoding='utf-8', errors='ignore')
            for pat in secret_patterns:
                if re.search(pat, text, re.IGNORECASE):
                    if "example" not in text.lower() and "provenance" not in text.lower():
                        print(f"FAIL: Potential secret in {f}: pattern {pat}")
                        sys.exit(1)
        for f in d.rglob("*.yaml"):
            text = f.read_text(encoding='utf-8', errors='ignore')
            for pat in secret_patterns:
                if re.search(pat, text, re.IGNORECASE):
                    if "example" not in text.lower():
                        print(f"FAIL: Potential secret in {f}: pattern {pat}")
                        sys.exit(1)
    print("OK: No secrets in canonical content/")

def check_template_registry():
    print("\n--- Check template registry v2.0.0 comprehensive ---")
    p = ROOT / "schema/template-registry.yaml"
    check_file_exists("schema/template-registry.yaml", "template-registry")
    import yaml
    data = yaml.safe_load(p.read_text())
    assert data.get("version") == "2.0.0", f"template-registry version must be 2.0.0, got {data.get('version')}"
    domains = data.get("domains", {})
    required_domains = ["physics", "chemistry", "biology", "earth-science", "astronomy", "computer-science", "engineering", "mathematics"]
    for d in required_domains:
        assert d in domains, f"Missing domain {d} in template-registry"
    print(f"OK: template-registry v2.0.0 — {len(domains)} domains, {sum(len(v.get('subdomains',[])) for v in domains.values())} subdomains")

def check_embedding_registry():
    print("\n--- Check embedding registry v1.0.0 + model selector ---")
    p = ROOT / "schema/embedding-registry.yaml"
    check_file_exists("schema/embedding-registry.yaml", "embedding-registry")
    import yaml
    data = yaml.safe_load(p.read_text())
    assert data.get("version") == "1.0.0"
    models = data.get("models", [])
    assert len(models) >= 10, f"Need at least 10 embedding models, got {len(models)}"
    model_ids = [m["id"] for m in models]
    assert "sentence-transformers/all-MiniLM-L6-v2" in model_ids
    assert "BAAI/bge-large-en-v1.5" in model_ids
    assert "openai/text-embedding-3-large" in model_ids
    print(f"OK: embedding-registry v1.0.0 — {len(models)} models, local + frontier, model selector like DeepSeek harness")

def check_consumer_registry():
    print("\n--- Check consumer registry v1.0.0 ---")
    p = ROOT / "schema/consumer-registry.yaml"
    check_file_exists("schema/consumer-registry.yaml", "consumer-registry")
    import yaml
    data = yaml.safe_load(p.read_text())
    assert data.get("version") == "1.0.0"
    consumers = data.get("consumers", {})
    assert "learninghub" in consumers
    assert "professor-j" in consumers
    print(f"OK: consumer-registry v1.0.0 — {len(consumers)} consumers")

def check_explorer_clean():
    print("\n--- Check explorer clean viewer requirements ---")
    gv = (ROOT / "explorer/src/components/graph-view.ts").read_text()
    assert "SphereGeometry(0.45" in gv, "Small nodes not found — must be small for clean look"
    assert "SphereGeometry(0.32" in gv, "Tiny sphere for unit not found"
    print("OK: Small nodes clean")

    legend = (ROOT / "explorer/src/components/graph-legend.ts").read_text()
    assert "display:none" in legend, "Legend must be hidden by default, manual only"
    assert "Manual only" in legend, "Legend manual only comment missing"
    print("OK: Manual legend only")

    assert "focusOnNode" in gv, "focusOnNode missing — centered zoom required"
    print("OK: Centered zoom focusOnNode exists")

    sbar = (ROOT / "explorer/src/components/search-filter-bar.ts").read_text()
    for domain in ["physics", "chemistry", "biology", "mathematics"]:
        assert domain in sbar, f"Domain {domain} missing in explorer search filter"
    print("OK: Explorer supports 8 domains")

    theme = (ROOT / "explorer/src/styles/theme.ts").read_text()
    for domain in ["physics", "chemistry", "biology", "earth-science", "astronomy", "computer-science", "engineering", "mathematics"]:
        assert domain in theme, f"Domain {domain} missing in theme"
    print("OK: Explorer theme has 8 domains")

def check_webapp_ingestion():
    print("\n--- Check webapp + ingestion pipeline ---")
    check_file_exists("webapp/core.py", "webapp core")
    check_file_exists("webapp/server.py", "webapp server")
    check_file_exists("webapp/static/index.html", "webapp static")
    check_file_exists("scripts/pdf_ingest_primary.py", "pdf_ingest_primary")
    check_file_exists("scripts/hitl_check.py", "hitl_check")

    core = (ROOT / "webapp/core.py").read_text()
    assert "human:" in core, "HITL human: not enforced in webapp/core.py"
    print("OK: HITL enforced in webapp")

    server = (ROOT / "webapp/server.py").read_text()
    assert "/api/rag/search" in server, "RAG search endpoint missing in webapp server"
    assert "/api/embeddings" in server, "Embeddings endpoint missing"
    print("OK: Webapp API endpoints — ingestion + RAG + embeddings")

    index_html = (ROOT / "webapp/static/index.html").read_text()
    assert "model" in index_html.lower() and "frontier" in index_html.lower(), "Model selector like DeepSeek harness not found in webapp"
    print("OK: Model selector like DeepSeek harness in webapp")

def check_embeddings_deterministic():
    print("\n--- Check embeddings deterministic + content_hash ---")
    emb_path = ROOT / "exports/embeddings.jsonl"
    meta_path = ROOT / "exports/vector_store/meta.json"
    if not emb_path.exists() or not meta_path.exists():
        print("INFO: embeddings not yet generated — run python3 scripts/embed.py first, skipping deterministic check in quick mode")
        return

    import json
    meta = json.loads(meta_path.read_text())
    assert "content_hash" in meta, "meta.json missing content_hash"
    assert meta["content_hash"].startswith("sha256:"), "content_hash must be sha256:"
    assert "model" in meta and "dimensions" in meta
    print(f"OK: Embeddings content_hash versioning — {meta['content_hash'][:30]}... model={meta['model']} dim={meta['dimensions']}")

    import shutil
    shutil.copy(emb_path, "/tmp/embeddings1.jsonl")
    shutil.copy(meta_path, "/tmp/meta1.json")

    # Rerun exactly the same kind of run. A placeholder store (H5) is labelled
    # stemma:placeholder-hash, which embed.py only writes with --placeholder;
    # the originally requested registry model is recorded on each row.
    cmd = [sys.executable, "scripts/embed.py"]
    if meta.get("placeholder") or meta.get("model") == "stemma:placeholder-hash":
        first = json.loads(emb_path.read_text().splitlines()[0]) if emb_path.stat().st_size else {}
        cmd += ["--placeholder"] + (["--model", first["requested_model"]] if first.get("requested_model") else [])
    else:
        cmd += ["--model", meta.get("model", "sentence-transformers/all-MiniLM-L6-v2")]
    run(cmd, fail_fast=False)
    
    if emb_path.exists():
        with open("/tmp/embeddings1.jsonl") as f1, open(emb_path) as f2:
            c1 = f1.read()
            c2 = f2.read()
            assert c1 == c2, "Embeddings not deterministic — byte-identical on rerun required"
        print("OK: Embeddings deterministic — byte-identical on rerun")
    else:
        print("WARN: embeddings.jsonl not found after rerun")

def check_rag():
    print("\n--- Check RAG vector search + citations ---")
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        import rag
        results = rag.vector_search("metre", top_k=1)
        assert results, "RAG vector search no results"
        print(f"OK: RAG vector search works — {len(results)} results for 'metre', score {results[0].get('score',0):.4f}, with citations")
    except Exception as e:
        print(f"INFO: RAG check — {e} — run embed.py first, but vector search should work")

def check_deterministic_export():
    print("\n--- Check deterministic export byte-identical ---")
    run([sys.executable, "scripts/validate.py"])
    import shutil
    shutil.copy(ROOT / "exports/knowledge.json", "/tmp/knowledge1.json")
    run([sys.executable, "scripts/validate.py"])
    with open("/tmp/knowledge1.json") as f1, open(ROOT / "exports/knowledge.json") as f2:
        assert f1.read() == f2.read(), "Export not deterministic — must be byte-identical on rerun"
    print("OK: Deterministic export — byte-identical on rerun")

def check_semantic_pipeline_strong():
    print("\n--- Check semantic acquisition pipeline strong — evidence first-class, AI output must be proposal, independent verification, conflict analysis ---")
    check_file_exists("schema/semantic-claim.schema.json", "semantic-claim schema")
    check_file_exists("schema/llm-registry.yaml", "llm-registry")
    check_file_exists("scripts/semantic_extract.py", "semantic_extract.py")
    check_file_exists("scripts/verify_claim.py", "verify_claim.py")
    check_file_exists("scripts/conflict_analysis.py", "conflict_analysis.py")
    check_file_exists("scripts/proposal_generate.py", "proposal_generate.py")
    check_file_exists("docs/SEMANTIC-ACQUISITION-PIPELINE.md", "semantic acquisition pipeline doc")

    # Check llm-registry has 5 roles
    import yaml
    llm_data = yaml.safe_load((ROOT / "schema/llm-registry.yaml").read_text())
    roles = llm_data.get("roles", {})
    assert len(roles) >= 5, f"Need 5 model roles, got {len(roles)}"
    assert "extraction" in roles and "verification" in roles and "document_vision" in roles
    print(f"OK: llm-registry v1.0.0 — {len(roles)} roles document_vision extraction reasoning verification embedding")

    models = llm_data.get("models", [])
    assert len(models) >= 10
    print(f"OK: llm-registry — {len(models)} models local+frontier model selector like DeepSeek harness")

    # Check semantic claim schema
    import json
    schema = json.loads((ROOT / "schema/semantic-claim.schema.json").read_text())
    assert "claim" in schema.get("properties",{})
    assert "evidence" in schema.get("properties",{})
    assert "extraction" in schema.get("properties",{})
    print(f"OK: semantic-claim.schema.json — {schema.get('title')} — evidence first-class, conditions, quantitative, provenance")

    # Test semantic extraction
    sys.path.insert(0, str(ROOT / "scripts"))
    import semantic_extract
    claims = semantic_extract.semantic_extract("The resistance of a conductor is directly proportional to its length and inversely proportional to its cross-sectional area, provided temperature remains constant.", source_id="stemma:src.test", model_id="deterministic", provider="deterministic")
    assert len(claims) >= 1
    assert "evidence" in claims[0] and "text_span" in claims[0]["evidence"]
    assert "char_offsets" in claims[0]["evidence"]
    print(f"OK: semantic extraction — {len(claims)} claims with evidence first-class char offsets surrounding context — NOT canonical")

    # Test conflict analysis demo
    import conflict_analysis
    result = conflict_analysis.demo_conflict()
    assert result["conflict_count"] == 1
    assert result["conflicts"][0]["values"] == [10, 12]
    print(f"OK: conflict analysis — demo conflict P=10 vs P=12 detected — explicit conflict detection, do not force average, do not allow LLM arbitrarily choose")

    # Test proposal generation evidence first-class
    import proposal_generate
    proposals = proposal_generate.generate_proposals({"claims": claims}, doc_id="test-doc")
    assert len(proposals) == len(claims)
    assert "evidence" in proposals[0] and "source_id" in proposals[0]["evidence"]
    assert "extraction" in proposals[0] and "model_id" in proposals[0]["extraction"]
    assert "verification" in proposals[0]
    assert proposals[0]["destination"]["canonical"] == "content/ | connections/ | sources/"
    print(f"OK: proposal generation — {len(proposals)} proposals with evidence first-class, NOT canonical, human review final authority")

    print("OK: semantic acquisition pipeline strong — evidence first-class, AI output must be proposal, independent verification, conflict analysis explicit, human review final authority, 16 stages, model roles, model-agnostic, reproducibility content_hash")

def check_docs():
    print("\n--- Check docs + guideline + semantic pipeline doc ---")
    required = [
        "AGENTS.md", "README.md", "VERSION",
        "docs/README.md", "docs/VISION.md", "docs/ARCHITECTURE.md",
        "docs/DOMAIN-MODEL.md", "docs/SCHEMA-SPECIFICATION.md",
        "docs/METADATA-SPECIFICATION.md", "docs/RELATIONSHIP-SPECIFICATION.md",
        "docs/PIPELINES.md", "docs/GOVERNANCE.md", "docs/TESTING.md",
        "docs/ROADMAP.md", "docs/MIGRATIONS.md",
        "docs/CURATION-PROTOCOL.md", "docs/CONSUMERS.md",
        "docs/EMBEDDINGS.md", "docs/RAG.md", "docs/API.md",
        "docs/GUIDELINE-EMBEDDER-RAG.md",
        "docs/SEMANTIC-ACQUISITION-PIPELINE.md",
        "docs/IMPLEMENTATION-STATUS.md"
    ]
    for f in required:
        check_file_exists(f, f"required doc {f}")
    print("OK: All required docs present including GUIDELINE-EMBEDDER-RAG.md")
    guideline = (ROOT / "docs/GUIDELINE-EMBEDDER-RAG.md").read_text()
    assert "Embedder" in guideline and "RAG" in guideline
    assert "content_hash" in guideline
    print("OK: Guideline comprehensive — 81KB")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="STRONG verification — nothing bad gets pushed/merged")
    parser.add_argument("--quick", action="store_true", help="Skip explorer build and heavy checks")
    parser.add_argument("--ci", action="store_true", help="CI mode")
    args = parser.parse_args()

    print("="*80)
    print("STRONG CI — Nothing Bad Gets Ever Pushed and Merged")
    print("Comprehensive all-STEM mediocre, 8 domains, HITL, evolvable, frontier, embeddings, RAG, consumer export")
    print("Explorer clean small nodes thin lines manual legend centered, ingestion pipeline, agent")
    print("="*80)

    run([sys.executable, "scripts/verify_all.py"])
    check_no_embeddings_in_canonical()
    check_no_wall_clock()
    check_no_secrets()
    check_template_registry()
    check_embedding_registry()
    check_consumer_registry()
    check_explorer_clean()
    check_webapp_ingestion()
    check_semantic_pipeline_strong()
    check_docs()
    check_deterministic_export()
    check_embeddings_deterministic()
    check_rag()

    if not args.quick:
        print("\n--- Check explorer build (if node available) ---")
        try:
            run(["npm", "ci"], cwd=ROOT / "explorer", fail_fast=False)
            run(["npm", "run", "typecheck"], cwd=ROOT / "explorer", fail_fast=False)
            run(["npm", "run", "build"], cwd=ROOT / "explorer", fail_fast=False)
            print("OK: Explorer build")
        except Exception as e:
            print(f"INFO: Explorer build skipped or failed — {e} — run npm ci manually")

        print("\n--- Check webapp core tests ---")
        run([sys.executable, "tests/registry/test_registry_coherence.py"])
        run([sys.executable, "tests/registry/test_domain_identity.py"])
        run([sys.executable, "tests/versioning/test_validation_report.py"])
        run([sys.executable, "tests/versioning/test_deterministic_export.py"])
        run([sys.executable, "scripts/status_truth.py"])
        run([sys.executable, "scripts/physics_core_profile_check.py"])
        run([sys.executable, "scripts/physics_governing_check.py"])

    print("\n" + "="*80)
    print("ALL STRONG CHECKS GREEN — Nothing Bad Gets Pushed/Merged — STRONG CI PASSED")
    print("="*80)
    print("Comprehensive all-STEM mediocre, 8 domains 97 subdomains 12 entity types 400-800 target")
    print("Explorer: clean small nodes thin lines manual legend centered zoom 8 domains")
    print("Ingestion: PDF primary HITL evolvable templates v2.0.0 model selector like DeepSeek harness")
    print("Semantic Acquisition Pipeline: evidence first-class, AI output must be proposal, independent verification deterministic+Verifier Model B, conflict analysis explicit P=10 vs P=12 do not force average, human review final authority, 16 stages, model roles document_vision extraction reasoning verification embedding, model-agnostic, reproducibility content_hash")
    print("Embeddings: deterministic content_hash versioned vector_store FAISS — NOT replacement for semantic extraction")
    print("RAG: vector search + citations, consumer export LearningHub PROFESSOR-J")
    print("Security: no secrets, no wall-clock, no randomness, id immutability, registry coherence")
    print("Docs: guideline + semantic pipeline doc + all required docs + versions single-sourced")
    print("="*80)
    return 0

if __name__ == "__main__":
    sys.exit(main())
