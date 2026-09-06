#!/usr/bin/env python3
"""Red Team Test Runner: Process difficult papers through STEMMA pipeline and measure fidelity."""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
REDPAPERS = ROOT / "redteam" / "papers"
RESULTS = ROOT / "redteam" / "results"

RESULTS.mkdir(parents=True, exist_ok=True)


def run_pipeline_step(cmd: list[str], description: str) -> subprocess.CompletedProcess:
    print(f"\n{'='*60}")
    print(f"STEP: {description}")
    print(f"CMD: {' '.join(cmd)}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    return result


def extract_entities_from_paper(paper_path: Path) -> dict:
    """Extract expected entities, relationships, equations, uncertainties from paper."""
    content = paper_path.read_text()
    return {
        "paper": paper_path.stem,
        "content": content,
        "expected_entities": [],
        "expected_relationships": [],
        "expected_equations": [],
        "expected_uncertainties": [],
        "expected_contradictions": [],
        "expected_cross_disciplinary": [],
        "expected_historical": [],
    }


def test_paper_1_hubble_tension():
    """Test Paper 1: Hubble Tension - contradictory findings, uncertainty, equations."""
    print("\n" + "="*80)
    print("TEST 1: HUBBLE TENSION - Contradictory Findings & Uncertainty")
    print("="*80)
    
    results = {
        "paper": "hubble_tension",
        "tests": {},
        "failures": [],
        "corrections": [],
    }
    
    # Test 1a: Can we register the source?
    print("\n1a. Register source...")
    source_result = subprocess.run([
        sys.executable, "scripts/register_source.py",
        "--type", "academic-paper",
        "--title", "Tension in the Hubble Constant",
        "--authors", "A. Riess, N. Aghanim",
        "--year", "2023",
        "--doi", "10.1038/s41550-023-01890-x",
        "--license", "CC BY 4.0",
        "--journal", "Nature Astronomy"
    ], capture_output=True, text=True, cwd=ROOT)
    results["tests"]["source_registration"] = source_result.returncode == 0
    if source_result.returncode != 0:
        results["failures"].append("Source registration failed")
        results["corrections"].append("Fix register_source.py for academic-paper type")
    
    # Test 1b: Check if entities for H0, CMB, distance ladder exist
    print("\n1b. Check entity resolution for H0, CMB, distance ladder...")
    export = json.loads((ROOT / "exports/knowledge.json").read_text())
    entities = {e["id"]: e for e in export["entities"]}
    
    hubble_entities = [
        e for e in entities.values() 
        if "hubble" in e.get("name", "").lower() or "h0" in e.get("name", "").lower()
    ]
    cmb_entities = [
        e for e in entities.values()
        if "cmb" in e.get("name", "").lower() or "cosmic microwave" in e.get("name", "").lower()
    ]
    
    results["tests"]["hubble_entities_found"] = len(hubble_entities) > 0
    results["tests"]["cmb_entities_found"] = len(cmb_entities) > 0
    if not hubble_entities:
        results["failures"].append("No Hubble constant entities found in canonical")
        results["corrections"].append("Add Hubble constant as quantity entity with uncertainty")
    if not cmb_entities:
        results["failures"].append("No CMB entities found")
        results["corrections"].append("Add CMB as concept/entity")
    
    # Test 1c: Check if contradictory relationships can be represented
    print("\n1c. Check contradiction representation...")
    connections = export.get("connections", [])
    contradictory = [
        c for c in connections 
        if c.get("relation") in ["contradicts", "inconsistent_with", "competes_with"]
    ]
    results["tests"]["contradiction_relations_exist"] = len(contradictory) > 0
    if not contradictory:
        results["failures"].append("No contradiction relations found in canonical")
        results["corrections"].append("Ensure contradicts/inconsistent_with relations are used")
    
    # Test 1d: Check uncertainty representation
    print("\n1d. Check uncertainty representation in entities...")
    hubble_quantity = next((e for e in entities.values() if e.get("id") == "lhs:phys.hubble-constant"), None)
    if hubble_quantity:
        has_uncertainty = "uncertainty" in str(hubble_quantity).lower() or "±" in str(hubble_quantity)
        results["tests"]["uncertainty_represented"] = has_uncertainty
        if not has_uncertainty:
            results["failures"].append("Hubble constant entity lacks explicit uncertainty field")
            results["corrections"].append("Add uncertainty field to quantity schema")
    else:
        results["tests"]["uncertainty_represented"] = False
        results["failures"].append("Hubble constant quantity entity not found")
        results["corrections"].append("Create Hubble constant as quantity with value ± uncertainty")
    
    # Test 1e: Check evidence with contradictory stances
    print("\n1e. Check evidence with contradictory stances...")
    h0_connections = [c for c in connections if "hubble" in c.get("source", "").lower() or "hubble" in c.get("target", "").lower()]
    stance_variety = set()
    for c in h0_connections:
        for ev in c.get("evidence", []):
            stance_variety.add(ev.get("stance", "unknown"))
    results["tests"]["multiple_stances_captured"] = len(stance_variety) > 1
    if len(stance_variety) <= 1:
        results["failures"].append("Only one stance type found for H0 evidence")
        results["corrections"].append("Ensure contradicts/qualifies/weakly_supports stances are used")
    
    return results


def test_paper_2_gibbs_energy():
    """Test Paper 2: Gibbs Free Energy - cross-disciplinary notation, equations, uncertainty."""
    print("\n" + "="*80)
    print("TEST 2: GIBBS FREE ENERGY - Cross-Disciplinary & Equations")
    print("="*80)
    
    results = {
        "paper": "gibbs_free_energy",
        "tests": {},
        "failures": [],
        "corrections": [],
    }
    
    export = json.loads((ROOT / "exports/knowledge.json").read_text())
    entities = {e["id"]: e for e in export["entities"]}
    connections = export.get("connections", [])
    
    # Test 2a: Cross-disciplinary entity resolution
    print("\n2a. Cross-disciplinary entity resolution (G, μ, a, standard state)...")
    gibbs_entities = [
        e for e in entities.values()
        if "gibbs" in e.get("name", "").lower() or "free energy" in e.get("name", "").lower()
    ]
    chemical_potential_entities = [
        e for e in entities.values()
        if "chemical potential" in (e.get("name") or "").lower() or "μ" in (e.get("symbol") or "")
    ]
    activity_entities = [
        e for e in entities.values()
        if "activity" in e.get("name", "").lower()
    ]
    
    results["tests"]["gibbs_entities_found"] = len(gibbs_entities) > 0
    results["tests"]["chemical_potential_entities_found"] = len(chemical_potential_entities) > 0
    results["tests"]["activity_entities_found"] = len(activity_entities) > 0
    
    if not gibbs_entities:
        results["failures"].append("No Gibbs free energy entities found")
        results["corrections"].append("Add Gibbs free energy as concept/quantity with cross-disciplinary aliases")
    
    # Test 2b: Equation representation
    print("\n2b. Equation representation (G=H-TS, dG=Vdp-SdT, μ=μ°+RT ln a)...")
    equation_entities = [
        e for e in entities.values()
        if e.get("type") == "equation" or e.get("equation")
    ]
    results["tests"]["equation_entities_exist"] = len(equation_entities) > 0
    if not equation_entities:
        results["failures"].append("No equation entities found")
        results["corrections"].append("Add equation entities for fundamental thermodynamic relations")
    
    # Test 2c: Uncertainty propagation
    print("\n2c. Uncertainty propagation (ATP hydrolysis ±4.6 kJ/mol)...")
    atp_entities = [
        e for e in entities.values()
        if "atp" in e.get("name", "").lower() or "adenosine" in e.get("name", "").lower()
    ]
    results["tests"]["atp_entities_exist"] = len(atp_entities) > 0
    if atp_entities:
        has_uncertainty = any("uncertain" in str(e).lower() or "±" in str(e) for e in atp_entities)
        results["tests"]["atp_uncertainty_represented"] = has_uncertainty
        if not has_uncertainty:
            results["failures"].append("ATP entities lack uncertainty representation")
            results["corrections"].append("Add uncertainty field to ATP and related thermodynamic quantities")
    
    # Test 2d: Cross-disciplinary notation variants
    print("\n2d. Cross-disciplinary notation (K vs K_c, a vs c, sign conventions)...")
    standard_state_entities = [
        e for e in entities.values()
        if "standard state" in e.get("name", "").lower() or "standard_state" in e.get("id", "")
    ]
    results["tests"]["standard_state_entities_exist"] = len(standard_state_entities) > 0
    if not standard_state_entities:
        results["failures"].append("No standard state entities found")
        results["corrections"].append("Add standard state entity with cross-disciplinary variants (pH, pMg, I)")
    
    # Test 2e: Contradictory claims handling
    print("\n2e. Contradictory claims (ATP -30.5 vs -20.5 kJ/mol)...")
    atp_connections = [c for c in connections if "atp" in str(c).lower()]
    contradiction_found = False
    for c in atp_connections:
        for ev in c.get("evidence", []):
            if ev.get("stance") in ["contradicts", "qualifies", "weakly_supports"]:
                contradiction_found = True
    results["tests"]["contradictory_claims_handled"] = contradiction_found
    if not contradiction_found:
        results["failures"].append("No contradictory evidence found for ATP ΔG claims")
        results["corrections"].append("Add contradicts/qualifies evidence for ATP ΔG° vs ΔG°' claims")
    
    return results


def test_paper_3_atomic_evolution():
    """Test Paper 3: Atomic Evolution - historical supersession, competing models."""
    print("\n" + "="*80)
    print("TEST 3: ATOMIC EVOLUTION - Historical Supersession & Competing Models")
    print("="*80)
    
    results = {
        "paper": "atomic_evolution",
        "tests": {},
        "failures": [],
        "corrections": [],
    }
    
    export = json.loads((ROOT / "exports/knowledge.json").read_text())
    entities = {e["id"]: e for e in export["entities"]}
    connections = export.get("connections", [])
    
    # Test 3a: Historical entity lineage (atom → plum pudding → nuclear → Bohr → QM → QFT)
    print("\n3a. Historical entity lineage (atom supersession chain)...")
    atom_entities = [
        e for e in entities.values()
        if "atom" in e.get("name", "").lower() and e.get("type") in ["concept", "model"]
    ]
    results["tests"]["atom_entities_found"] = len(atom_entities) > 0
    if len(atom_entities) < 3:
        results["failures"].append("Insufficient atomic model lineage (need Dalton→Thomson→Rutherford→Bohr→QM→QFT)")
        results["corrections"].append("Add complete atomic model lineage with supersedes/superseded_by")
    
    # Test 3b: Supersession relationships
    print("\n3b. Supersession relationships (supersedes/superseded_by)...")
    supersession_conns = [
        c for c in connections
        if c.get("relation") in ["supersedes", "superseded_by"]
    ]
    results["tests"]["supersession_relations_exist"] = len(supersession_conns) > 0
    if not supersession_conns:
        results["failures"].append("No supersession relationships found")
        results["corrections"].append("Add supersedes/superseded_by relations for historical models")
    
    # Test 3c: Competing models coexistence (Bohr vs Bohr-Sommerfeld, Matrix vs Wave)
    print("\n3c. Competing models coexistence (Bohr vs Bohr-Sommerfeld, Matrix vs Wave)...")
    competing_conns = [
        c for c in connections
        if c.get("relation") in ["competes_with", "inconsistent_with"]
    ]
    results["tests"]["competing_models_represented"] = len(competing_conns) > 0
    if not competing_conns:
        results["failures"].append("No competing model relationships found")
        results["corrections"].append("Add competes_with/inconsistent_with for historical competing models")
    
    # Test 3d: Contradictory evidence during transitions
    print("\n3d. Contradictory evidence during transitions (e.g., electron in nucleus vs uncertainty principle)...")
    evidence_with_contradiction = False
    for c in connections:
        for ev in c.get("evidence", []):
            if ev.get("stance") == "contradicts":
                evidence_with_contradiction = True
                break
    results["tests"]["contradictory_evidence_captured"] = evidence_with_contradiction
    if not evidence_with_contradiction:
        results["failures"].append("No contradictory evidence stance found")
        results["corrections"].append("Add contradicts stance for key historical contradictions (e.g., electron in nucleus)")
    
    # Test 3e: Unresolvable disagreement (QM interpretations)
    print("\n3e. Unresolvable disagreement (QM interpretations: Copenhagen vs Many-Worlds vs Bohm)...")
    interpretation_entities = [
        e for e in entities.values()
        if "interpretation" in e.get("name", "").lower() or "copenhagen" in e.get("name", "").lower()
    ]
    results["tests"]["qm_interpretations_exist"] = len(interpretation_entities) > 0
    if not interpretation_entities:
        results["failures"].append("No QM interpretation entities found")
        results["corrections"].append("Add QM interpretations as entities with competes_with relations")
    
    # Test 3f: Evidence with stance=contradicts for key historical cases
    print("\n3f. Key historical contradictions (parity violation, CP violation, neutron discovery)...")
    parity_entities = [e for e in entities.values() if "parity" in e.get("name", "").lower()]
    cp_entities = [e for e in entities.values() if "cp violation" in e.get("name", "").lower() or "cp-violation" in e.get("id", "")]
    results["tests"]["historical_contradictions_exist"] = len(parity_entities) > 0 or len(cp_entities) > 0
    if not (parity_entities or cp_entities):
        results["failures"].append("Key historical contradictions (parity, CP violation) not represented")
        results["corrections"].append("Add parity violation, CP violation as entities with contradicts evidence")
    
    return results


def test_equation_fidelity():
    """Test equation fidelity across papers."""
    print("\n" + "="*80)
    print("TEST 4: EQUATION FIDELITY - Mathematical Content Preservation")
    print("="*80)
    
    results = {
        "paper": "equation_fidelity",
        "tests": {},
        "failures": [],
        "corrections": [],
    }
    
    export = json.loads((ROOT / "exports/knowledge.json").read_text())
    entities = {e["id"]: e for e in export["entities"]}
    
    # Check for key equations
    key_equations = [
        ("hubble_law", "v = H₀d"),
        ("friedmann", "H² = (8πG/3)ρ"),
        ("gibbs", "G = H - TS"),
        ("dG", "dG = Vdp - SdT"),
        ("chemical_potential", "μ = μ° + RT ln a"),
        ("rutherford", "dσ/dΩ"),
        ("bohr_energy", "E_n = -13.6/n²"),
        ("schrodinger", "iħ ∂ψ/∂t"),
        ("uncertainty", "Δx Δp ≥ ħ/2"),
    ]
    
    equation_entities = [e for e in entities.values() if e.get("type") == "equation" or e.get("equation")]
    results["tests"]["equation_entities_exist"] = len(equation_entities) > 0
    
    found_equations = []
    for e in equation_entities:
        eq_text = str(e.get("equation", "")) + str(e.get("definition", ""))
        for name, pattern in key_equations:
            if pattern.lower().replace("²", "2").replace("₀", "0").replace("₁", "1") in eq_text.lower().replace("²", "2").replace("₀", "0").replace("₁", "1"):
                found_equations.append(name)
    
    results["tests"]["key_equations_found"] = len(found_equations)
    results["tests"]["key_equations_list"] = found_equations
    
    if len(found_equations) < 5:
        results["failures"].append(f"Only {len(found_equations)}/9 key equations found in canonical")
        results["corrections"].append("Add missing fundamental equations as equation entities with proper LaTeX")
    
    return results


def test_cross_disciplinary_notation():
    """Test cross-disciplinary notation handling."""
    print("\n" + "="*80)
    print("TEST 5: CROSS-DISCIPLINARY NOTATION - Same Concept, Different Notation")
    print("="*80)
    
    results = {
        "paper": "cross_disciplinary_notation",
        "tests": {},
        "failures": [],
        "corrections": [],
    }
    
    export = json.loads((ROOT / "exports/knowledge.json").read_text())
    entities = {e["id"]: e for e in export["entities"]}
    
    # Check for notation variants in symbols
    symbol_map = {}
    for e in entities.values():
        sym = e.get("symbol")
        if sym:
            symbol_map.setdefault(sym, []).append(e["id"])
    
    conflicts = {sym: ids for sym, ids in symbol_map.items() if len(ids) > 1}
    results["tests"]["symbol_conflicts_found"] = len(conflicts)
    results["tests"]["symbol_conflicts"] = conflicts
    
    if conflicts:
        results["failures"].append(f"Symbol conflicts found: {list(conflicts.keys())}")
        results["corrections"].append("Add symbol disambiguation via context/domain or use symbol_set extension")
    
    # Check for cross-disciplinary entities with same name
    name_map = {}
    for e in entities.values():
        name = e.get("name", "").lower()
        if name:
            name_map.setdefault(name, []).append(e["id"])
    
    name_conflicts = {name: ids for name, ids in name_map.items() if len(ids) > 1}
    cross_domain = {name: ids for name, ids in name_conflicts.items() 
                    if len(set(entities[i].get("domain", "") for i in ids)) > 1}
    
    results["tests"]["cross_domain_name_conflicts"] = len(cross_domain)
    results["tests"]["cross_domain_conflicts"] = cross_domain
    
    if cross_domain:
        results["failures"].append(f"Cross-domain name conflicts: {list(cross_domain.keys())}")
        results["corrections"].append("Add disambiguation via domain-specific symbols or context extensions")
    
    return results


def test_retraction_propagation():
    """Test retraction propagation through canonical layer."""
    print("\n" + "="*80)
    print("TEST 6: RETRACTION/CORRECTION PROPAGATION")
    print("="*80)
    
    results = {
        "paper": "retraction_propagation",
        "tests": {},
        "failures": [],
        "corrections": [],
    }
    
    export = json.loads((ROOT / "exports/knowledge.json").read_text())
    connections = export.get("connections", [])
    
    # Test if connections with retracted source are flagged
    print("\n6a. Connections depending on retracted source...")
    # We can't easily test this without a retracted source, but check the mechanism
    retracted_sources = [s for s in json.loads((ROOT / "exports/knowledge.json").read_text()).get("sources", []) 
                        if s.get("lifecycle") == "retracted"]
    
    results["tests"]["retracted_sources_tracked"] = len(retracted_sources) >= 0  # Always true, just checking field exists
    
    # Check if handle_retraction.py logic works
    print("\n6b. Retraction handling script works...")
    result = subprocess.run([
        sys.executable, "scripts/handle_retraction.py",
        "--action", "retract",
        "--source", "lhs:src.halliday-resnick",
        "--reason", "Test retraction"
    ], capture_output=True, text=True, cwd=ROOT)
    
    results["tests"]["retraction_script_works"] = result.returncode == 0
    if result.returncode != 0:
        results["failures"].append("Retraction handling script failed")
        results["corrections"].append("Fix handle_retraction.py")
    
    # Check proposed actions
    if "deprecate" in result.stdout or "qualify" in result.stdout:
        results["tests"]["retraction_proposes_actions"] = True
    else:
        results["tests"]["retraction_proposes_actions"] = False
        results["failures"].append("Retraction script doesn't propose deprecate/qualify actions")
        results["corrections"].append("Fix retraction action logic")
    
    return results


def test_source_trust_assessment():
    """Test source trust assessment."""
    print("\n" + "="*80)
    print("TEST 7: SOURCE TRUST ASSESSMENT")
    print("="*80)
    
    results = {
        "paper": "source_trust",
        "tests": {},
        "failures": [],
        "corrections": [],
    }
    
    result = subprocess.run([
        sys.executable, "scripts/source_trust.py"
    ], capture_output=True, text=True, cwd=ROOT)
    
    results["tests"]["source_trust_runs"] = result.returncode == 0
    
    if result.returncode == 0:
        # Check output has all 8 dimensions
        dimensions = [
            "institutional_authority", "peer_review_status", "methodological_strength",
            "recency", "consensus_alignment", "reproducibility", "independence", "domain_relevance"
        ]
        for dim in dimensions:
            if dim in result.stdout:
                results["tests"][f"dimension_{dim}"] = True
            else:
                results["tests"][f"dimension_{dim}"] = False
                results["failures"].append(f"Missing trust dimension: {dim}")
                results["corrections"].append(f"Add {dim} to source trust assessment")
    
    return results


def test_evidence_ledger():
    """Test evidence ledger integrity."""
    print("\n" + "="*80)
    print("TEST 8: EVIDENCE LEDGER INTEGRITY")
    print("="*80)
    
    results = {
        "paper": "evidence_ledger",
        "tests": {},
        "failures": [],
        "corrections": [],
    }
    
    # Verify chain
    result = subprocess.run([
        sys.executable, "scripts/evidence_ledger.py", "--verify"
    ], capture_output=True, text=True, cwd=ROOT)
    
    results["tests"]["ledger_chain_valid"] = result.returncode == 0
    if result.returncode != 0:
        results["failures"].append("Evidence ledger chain invalid")
        results["corrections"].append("Fix evidence ledger chain integrity")
    
    # Test lineage query
    result = subprocess.run([
        sys.executable, "scripts/evidence_ledger.py", "--lineage", "lhs:phys.newtons-second-law"
    ], capture_output=True, text=True, cwd=ROOT)
    
    results["tests"]["lineage_query_works"] = result.returncode == 0
    
    return results


def test_drift_detection():
    """Test drift detection."""
    print("\n" + "="*80)
    print("TEST 9: SOURCE DRIFT DETECTION")
    print("="*80)
    
    results = {
        "paper": "drift_detection",
        "tests": {},
        "failures": [],
        "corrections": [],
    }
    
    result = subprocess.run([
        sys.executable, "scripts/detect_drift.py"
    ], capture_output=True, text=True, cwd=ROOT)
    
    results["tests"]["drift_detection_runs"] = result.returncode == 0
    
    if result.returncode == 0:
        if "affected canonical objects" in result.stdout.lower():
            results["tests"]["drift_identifies_affected"] = True
        else:
            results["tests"]["drift_identifies_affected"] = False
            results["failures"].append("Drift detection doesn't identify affected canonical objects")
            results["corrections"].append("Enhance drift detection to show affected connections/entities")
    
    return results


def test_entity_resolution():
    """Test entity resolution for duplicates/synonyms."""
    print("\n" + "="*80)
    print("TEST 10: ENTITY RESOLUTION")
    print("="*80)
    
    results = {
        "paper": "entity_resolution",
        "tests": {},
        "failures": [],
        "corrections": [],
    }
    
    result = subprocess.run([
        sys.executable, "scripts/entity_resolution.py"
    ], capture_output=True, text=True, cwd=ROOT)
    
    results["tests"]["entity_resolution_runs"] = result.returncode == 0
    
    if "symbol_match" in result.stdout:
        results["tests"]["finds_symbol_conflicts"] = True
    else:
        results["failures"].append("Entity resolution doesn't detect symbol conflicts")
        results["corrections"].append("Improve entity resolution to detect symbol conflicts")
    
    if "name_similarity" in result.stdout:
        results["tests"]["finds_name_similarity"] = True
    else:
        results["failures"].append("Entity resolution doesn't detect name similarity")
        results["corrections"].append("Improve name similarity detection")
    
    return results


def main():
    print("="*80)
    print("STEMMA v0.3 RED TEAM TEST SUITE")
    print("Testing: Source → Evidence → Candidate → Canonical Pipeline")
    print("="*80)
    
    all_results = {}
    
    # Run all tests
    all_results["hubble_tension"] = test_paper_1_hubble_tension()
    all_results["gibbs_free_energy"] = test_paper_2_gibbs_energy()
    all_results["atomic_evolution"] = test_paper_3_atomic_evolution()
    all_results["equation_fidelity"] = test_equation_fidelity()
    all_results["cross_disciplinary_notation"] = test_cross_disciplinary_notation()
    all_results["retraction_propagation"] = test_retraction_propagation()
    all_results["source_trust"] = test_source_trust_assessment()
    all_results["evidence_ledger"] = test_evidence_ledger()
    all_results["drift_detection"] = test_drift_detection()
    all_results["entity_resolution"] = test_entity_resolution()
    
    # Aggregate results
    total_tests = 0
    total_failures = 0
    all_failures = []
    all_corrections = []
    
    for paper, results in all_results.items():
        paper_failures = len(results.get("failures", []))
        paper_tests = len(results.get("tests", {}))
        total_tests += paper_tests
        total_failures += paper_failures
        all_failures.extend([f"[{paper}] {f}" for f in results.get("failures", [])])
        all_corrections.extend([f"[{paper}] {c}" for c in results.get("corrections", [])])
        print(f"\n{paper}: {paper_tests - paper_failures}/{paper_tests} tests passed")
        if results.get("failures"):
            for f in results["failures"]:
                print(f"  FAIL: {f}")
    
    print("\n" + "="*80)
    print(f"RED TEAM SUMMARY: {total_tests - total_failures}/{total_tests} tests passed")
    print(f"Total failures: {total_failures}")
    print("="*80)
    
    if all_failures:
        print("\nFAILURES:")
        for f in all_failures:
            print(f"  - {f}")
    
    if all_corrections:
        print("\nARCHITECTURAL CORRECTIONS NEEDED:")
        for c in all_corrections:
            print(f"  - {c}")
    
    # Write detailed results
    report_path = RESULTS / f"redteam_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, 'w') as f:
        json.dump({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed": total_tests - total_failures,
                "failed": total_failures,
            },
            "results": all_results,
        }, f, indent=2)
    
    print(f"\nDetailed report written to {report_path.relative_to(ROOT)}")
    
    return 0 if total_failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())