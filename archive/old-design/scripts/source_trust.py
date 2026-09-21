#!/usr/bin/env python3
"""Source Trust / Evidence Quality Assessment for STEMMA.

Computes multi-dimensional trust scores for sources and evidence quality metrics.
Does NOT reduce to a single confidence score — preserves dimensional breakdown.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parent.parent
SOURCES_DIR = ROOT / "sources"
EXPORT = ROOT / "exports" / "knowledge.json"


# Authority dimension definitions
DIMENSIONS = {
    "institutional_authority": {
        "description": "Authority of publishing institution",
        "scale": "0.0-1.0",
        "examples": {"NIST": 1.0, "University press": 0.9, "Professional society": 0.8, "Personal blog": 0.2},
    },
    "peer_review_status": {
        "description": "Peer review status of source",
        "scale": "0.0-1.0",
        "examples": {"Peer-reviewed journal": 1.0, "Preprint server": 0.5, "Conference proceedings": 0.7, "Internal report": 0.3},
    },
    "methodological_strength": {
        "description": "Strength of methodology",
        "scale": "0.0-1.0",
        "examples": {"RCT/Meta-analysis": 1.0, "Controlled experiment": 0.9, "Observational study": 0.6, "Case study": 0.4, "Expert opinion": 0.3},
    },
    "recency": {
        "description": "Recency of source",
        "scale": "0.0-1.0",
        "examples": {"<2 years": 1.0, "2-5 years": 0.8, "5-10 years": 0.6, "10-20 years": 0.4, ">20 years": 0.2},
    },
    "consensus_alignment": {
        "description": "Alignment with scientific consensus",
        "scale": "0.0-1.0",
        "examples": {"Widely accepted textbook": 1.0, "Standard model": 0.9, "Established theory": 0.8, "Controversial claim": 0.3, "Fringe theory": 0.1},
    },
    "reproducibility": {
        "description": "Reproducibility of results",
        "scale": "0.0-1.0",
        "examples": {"Replicated independently": 1.0, "Single high-quality study": 0.6, "Preliminary result": 0.3, "Unreplicated": 0.2},
    },
    "independence": {
        "description": "Independence from conflicts of interest",
        "scale": "0.0-1.0",
        "examples": {"Independent academic": 1.0, "Government lab": 0.9, "Industry-funded": 0.5, "Marketing material": 0.2},
    },
    "domain_relevance": {
        "description": "Relevance to the specific domain/claim",
        "scale": "0.0-1.0",
        "examples": {"Exact domain match": 1.0, "Closely related": 0.8, "Tangential": 0.4, "Different field": 0.2},
    },
}


def load_sources() -> dict[str, dict]:
    """Load all source records."""
    sources = {}
    if not SOURCES_DIR.exists():
        return sources
    for path in SOURCES_DIR.glob("*.yaml"):
        try:
            data = yaml.safe_load(path.read_text())
            if isinstance(data, dict) and data.get("id"):
                sources[data["id"]] = data
        except Exception:
            pass
    return sources


def load_export() -> dict:
    """Load canonical export."""
    if not EXPORT.exists():
        return {"entities": [], "connections": [], "sources": []}
    return json.loads(EXPORT.read_text())


def infer_dimensions(source: dict) -> dict[str, float]:
    """Infer trust dimensions from source metadata (heuristic)."""
    dims = {}
    stype = source.get("type", "")
    source_role = source.get("source_role", "")
    publisher = (source.get("publisher") or "").lower()
    journal = (source.get("journal") or "").lower()
    
    # Institutional authority
    if any(kw in publisher for kw in ["nist", "ieee", "iso", "iupac", "who", "unesco", "nasa"]):
        dims["institutional_authority"] = 1.0
    elif "university" in publisher or "press" in publisher:
        dims["institutional_authority"] = 0.9
    elif stype == "standard":
        dims["institutional_authority"] = 1.0
    elif stype == "textbook":
        dims["institutional_authority"] = 0.8
    else:
        dims["institutional_authority"] = 0.5
    
    # Peer review status
    if stype == "academic-paper":
        dims["peer_review_status"] = 1.0
    elif stype in ["standard", "textbook"]:
        dims["peer_review_status"] = 1.0
    elif "preprint" in str(source).lower():
        dims["peer_review_status"] = 0.5
    elif stype == "web":
        dims["peer_review_status"] = 0.3
    else:
        dims["peer_review_status"] = 0.5
    
    # Methodological strength
    if stype == "dataset":
        dims["methodological_strength"] = 0.9
    elif stype == "academic-paper":
        dims["methodological_strength"] = 0.9
    elif stype == "standard":
        dims["methodological_strength"] = 1.0
    elif stype == "textbook":
        dims["methodological_strength"] = 0.7
    else:
        dims["methodological_strength"] = 0.5
    
    # Recency (from year if available)
    year = source.get("year") or source.get("publication_date", "")
    if year:
        try:
            y = int(str(year)[:4])
            from datetime import datetime
            current = datetime.now().year
            age = current - y
            if age <= 2:
                dims["recency"] = 1.0
            elif age <= 5:
                dims["recency"] = 0.8
            elif age <= 10:
                dims["recency"] = 0.6
            elif age <= 20:
                dims["recency"] = 0.4
            else:
                dims["recency"] = 0.2
        except:
            dims["recency"] = 0.5
    else:
        dims["recency"] = 0.5
    
    # Consensus alignment
    if stype in ["textbook", "standard"]:
        dims["consensus_alignment"] = 1.0
    elif stype == "academic-paper":
        dims["consensus_alignment"] = 0.7
    else:
        dims["consensus_alignment"] = 0.5
    
    # Reproducibility
    if stype == "dataset":
        dims["reproducibility"] = 0.9
    elif stype == "standard":
        dims["reproducibility"] = 1.0
    elif stype == "academic-paper":
        dims["reproducibility"] = 0.6
    else:
        dims["reproducibility"] = 0.5
    
    # Independence
    if "industry" in publisher or "corporate" in publisher:
        dims["independence"] = 0.5
    elif "government" in publisher or "nist" in publisher:
        dims["independence"] = 0.9
    else:
        dims["independence"] = 0.7
    
    # Domain relevance - default, would be set per-claim
    dims["domain_relevance"] = 0.8
    
    return dims


def compute_composite_score(dims: dict) -> float:
    """Compute weighted composite trust score (for reference only, not authoritative)."""
    weights = {
        "institutional_authority": 0.20,
        "peer_review_status": 0.15,
        "methodological_strength": 0.15,
        "recency": 0.10,
        "consensus_alignment": 0.15,
        "reproducibility": 0.10,
        "independence": 0.10,
        "domain_relevance": 0.05,
    }
    score = sum(dims.get(k, 0.5) * w for k, w in weights.items())
    return round(score, 3)


def assess_evidence_quality(evidence: dict) -> dict:
    """Assess quality of a single evidence item."""
    quality = {}
    
    # Extraction confidence
    extraction_conf = evidence.get("extraction_confidence")
    if extraction_conf is not None:
        quality["extraction_confidence"] = extraction_conf
    else:
        method = evidence.get("extraction_method", "")
        if method in ["pdftotext", "pdfplumber"]:
            quality["extraction_confidence"] = 0.95
        elif method == "tesseract":
            quality["extraction_confidence"] = 0.80
        elif method == "llm-extraction":
            quality["extraction_confidence"] = 0.85
        elif method == "manual":
            quality["extraction_confidence"] = 0.99
        else:
            quality["extraction_confidence"] = 0.70
    
    # Locator completeness
    locator = evidence.get("locator", {})
    if isinstance(locator, str):
        locator = {}
    locator_fields = ["page", "section", "equation", "figure", "table", "dataset", "code"]
    present = sum(1 for f in locator_fields if locator.get(f))
    quality["locator_completeness"] = min(1.0, present / 3.0)  # Expect at least 3
    
    # Evidence type strength
    etype = evidence.get("type", "")
    type_strength = {
        "empirical_measurement": 1.0,
        "experiment": 1.0,
        "mathematical_derivation": 1.0,
        "definition": 1.0,
        "standard": 1.0,
        "textbook": 0.9,
        "review": 0.8,
        "academic-paper": 0.8,
        "observation": 0.7,
        "simulation": 0.7,
        "derivation": 0.7,
        "expert_assessment": 0.6,
        "dataset": 0.8,
    }
    quality["type_strength"] = type_strength.get(etype, 0.5)
    
    # Stance clarity
    stance = evidence.get("stance", "supports")
    quality["stance_clarity"] = 1.0 if stance != "supports" else 0.8  # explicit non-support is clearer
    
    return quality


def main() -> int:
    sources = load_sources()
    export = load_export()
    
    print(f"Loaded {len(sources)} sources")
    
    # Assess source trust
    source_assessments = {}
    for sid, source in sources.items():
        dims = infer_dimensions(source)
        composite = compute_composite_score(dims)
        title = source.get("title") or "Unknown"
        source_assessments[sid] = {
            "source_id": sid,
            "title": title,
            "type": source.get("type", "unknown"),
            "dimensions": dims,
            "composite_trust_score": composite,
        }
        print(f"\n{sid}: {title[:60]}")
        print(f"  Composite trust: {composite}")
        for dim, val in dims.items():
            print(f"    {dim}: {val}")
    
    # Assess evidence quality
    print("\n\nEvidence Quality Assessment:")
    for conn in export.get("connections", []):
        cid = conn.get("id")
        ev_list = conn.get("evidence", [])
        if not ev_list:
            print(f"  {cid}: NO EVIDENCE")
            continue
        for i, ev in enumerate(ev_list):
            quality = assess_evidence_quality(ev)
            print(f"  {cid} evidence[{i}]: type={ev.get('type')}, stance={ev.get('stance')}")
            print(f"    extraction_confidence: {quality.get('extraction_confidence')}")
            print(f"    locator_completeness: {quality.get('locator_completeness')}")
            print(f"    type_strength: {quality.get('type_strength')}")
            print(f"    stance_clarity: {quality.get('stance_clarity')}")
    
    # Write assessments
    output = ROOT / "proposals" / "source_trust_assessment.yaml"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(yaml.safe_dump({
        "generated_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
        "source_assessments": source_assessments,
        "dimension_definitions": DIMENSIONS,
        "note": "Composite scores are for reference only. Do not use as single truth metric. Use dimensional breakdown for decisions.",
    }, sort_keys=False, allow_unicode=True))
    
    print(f"\nAssessments written to {output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())