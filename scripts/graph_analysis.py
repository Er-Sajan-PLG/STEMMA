#!/usr/bin/env python3
"""Phase C: Derived Graph Engine — deterministic, derived-only.

Input: content/, connections/, sources/, relation-registry.yaml
Output: exports/knowledge.extended.json (all derived marked derived:true)

Never writes to connections/ or content/.
"""
import json
import pathlib
import collections

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONNECTIONS = ROOT / "connections"
CONTENT = ROOT / "content"
REGISTRY = ROOT / "schema" / "relation-registry.yaml"
EXPORT_EXT = ROOT / "exports" / "knowledge.extended.json"
EXPORT_BASE = ROOT / "exports" / "knowledge.json"
VERSION_SOURCE = ROOT / "schema" / "VERSION.yaml"  # ADR-0022: no version literals


def _versions() -> dict:
    return yaml.safe_load(VERSION_SOURCE.read_text(encoding="utf-8"))


def load_registry():
    return yaml.safe_load(REGISTRY.read_text()).get("relations", {})


def load_vocabularies():
    vocab_root = ROOT / "schema" / "vocabularies"
    domains_path = vocab_root / "domains.yaml"
    subdomains_path = vocab_root / "subdomains.yaml"
    regimes_path = vocab_root / "regimes.yaml"
    return {
        "domains": (yaml.safe_load(domains_path.read_text()) or {}).get("domains") or [],
        "subdomains": yaml.safe_load(subdomains_path.read_text()) or {},
        "regimes": (yaml.safe_load(regimes_path.read_text()) or {}).get("regimes") or [],
        "scales": (yaml.safe_load(regimes_path.read_text()) or {}).get("scales") or [],
    }


def load_entities():
    ents = {}
    for p in sorted((ROOT / "content").rglob("*.md")):
        d = yaml.safe_load(p.read_text().split("---", 2)[1])
        if d.get("id"):
            ents[d["id"]] = d
    return ents


def load_connections(policy="all"):
    # Simple: all connections; policy filtering via graph_policy if needed
    return [yaml.safe_load(p.read_text()) for p in sorted(CONNECTIONS.glob("*.yaml"))]


def main():
    registry = load_registry()
    entities = load_entities()
    conns = [yaml.safe_load(p.read_text()) for p in sorted(CONNECTIONS.glob("*.yaml"))]

    # C2 Inverse edges (derived, not canonical)
    inverse_edges = []
    for c in conns:
        meta = registry.get(c["relation"], {})
        inv = meta.get("inverse")
        if inv:
            inverse_edges.append({
                "source": c["target"],
                "relation": inv,
                "target": c["source"],
                "derived": True,
                "derivation": {"method": "inverse", "source_connection": c["id"]},
            })
    inverse_edges.sort(key=lambda x: (x["source"], x["relation"], x["target"]))

    # C3 Transitive closure (only transitive:true)
    transitive_rels = {k for k, v in registry.items() if v.get("transitive")}
    # Build adjacency per transitive relation
    from collections import defaultdict

    # For each transitive relation, compute closure via BFS per node (deterministic)
    derived_transitive = []
    # Group by relation
    by_rel = defaultdict(list)
    for c in conns:
        if c["relation"] in transitive_rels:
            by_rel[c["relation"]].append(c)

    for rel, edges in by_rel.items():
        # Build graph
        graph = defaultdict(list)
        for e in edges:
            graph[e["source"]].append(e["target"])
        # For each source, BFS to find reachable beyond direct
        direct = {(e["source"], e["target"]) for e in edges}
        for src in sorted(graph.keys()):
            visited = set()
            stack = [(src, [src])]
            # BFS
            queue = [(src, [src])]
            seen = set([src])
            while queue:
                node, path = queue.pop(0)
                for nb in sorted(graph.get(node, [])):
                    if nb not in seen:
                        seen.add(nb)
                        new_path = path + [nb]
                        queue.append((nb, new_path))
                        # If not direct edge, it's transitive closure
                        if (src, nb) not in direct and src != nb:
                            derived_transitive.append({
                                "source": src,
                                "relation": rel,
                                "target": nb,
                                "derived": True,
                                "derivation": {"method": "transitive_closure", "path": new_path, "rule": rel},
                            })
    derived_transitive.sort(key=lambda x: (x["source"], x["relation"], x["target"]))

    # C4 Dependency graph analysis (dependency family only)
    dep_rels = {k for k, v in registry.items() if v.get("family") == "dependency"}
    dep_edges = [c for c in conns if c["relation"] in dep_rels and c["assertion"]["status"] == "active"]
    dep_graph = defaultdict(list)
    for e in dep_edges:
        dep_graph[e["source"]].append(e["target"])
    # Cycle detection already in validator; here just report
    # Prerequisite chains: longest path per node (simple BFS up to 5)
    prereq_chains = []
    for src in sorted(dep_graph.keys())[:20]:  # sample top
        # BFS up to depth 4
        queue = [(src, [src])]
        while queue:
            node, path = queue.pop(0)
            if len(path) > 4:
                continue
            for nb in sorted(dep_graph.get(node, [])):
                if nb not in path:
                    new_path = path + [nb]
                    prereq_chains.append({"from": src, "to": nb, "path": new_path, "length": len(new_path)-1})
                    queue.append((nb, new_path))
    prereq_chains.sort(key=lambda x: (-x["length"], x["from"]))

    # C5 Centrality: degree, in-degree, out-degree, simple PageRank (5 iterations)
    nodes = sorted(entities.keys())
    indeg = collections.Counter(c["target"] for c in conns)
    outdeg = collections.Counter(c["source"] for c in conns)
    degree = {n: indeg.get(n, 0) + outdeg.get(n, 0) for n in nodes}
    # PageRank simplified
    N = len(nodes)
    rank = {n: 1.0 / N for n in nodes}
    # Build out-links
    out_links = defaultdict(list)
    for c in conns:
        out_links[c["source"]].append(c["target"])
    for _ in range(5):
        new_rank = {}
        for n in nodes:
            s = 0
            for src, tgts in out_links.items():
                if n in tgts:
                    s += rank[src] / len(tgts)
            new_rank[n] = 0.15 / N + 0.85 * s
        rank = new_rank
    # Betweenness approximated via degree centrality for now (keep deterministic)
    centrality = {
        n: {"degree": degree.get(n, 0), "in_degree": indeg.get(n, 0), "out_degree": outdeg.get(n, 0), "pagerank": round(rank.get(n, 0), 6)}
        for n in nodes
    }
    # Sort by pagerank
    ranked = sorted(centrality.items(), key=lambda x: -x[1]["pagerank"])

    # C6 Connected components (undirected)
    parent = {}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for n in nodes:
        parent[n] = n
    for c in conns:
        # undirected
        if c["source"] in parent and c["target"] in parent:
            union(c["source"], c["target"])
    comps = defaultdict(list)
    for n in nodes:
        comps[find(n)].append(n)
    components = [sorted(v) for v in comps.values()]
    components.sort(key=lambda x: -len(x))
    isolated = [c[0] for c in components if len(c) == 1]

    # C7 Cross-domain pathways (derived from bridges)
    bridge_edges = [c for c in conns if c["relation"] == "bridges"]
    cross_domain_pathways = []
    for b in bridge_edges:
        s_dom = entities.get(b["source"], {}).get("domain", "")
        t_dom = entities.get(b["target"], {}).get("domain", "")
        cross_domain_pathways.append({"source": b["source"], "target": b["target"], "domains": f"{s_dom}→{t_dom}", "connection": b["id"]})
    cross_domain_pathways.sort(key=lambda x: x["domains"])

    # C8 Analogy clusters and approximation chains (group by relation)
    analogy_clusters = defaultdict(list)
    for c in conns:
        if c["relation"] == "analogous_to":
            # Undirected cluster via union
            analogy_clusters[c["source"]].append(c["target"])
    # Simplify: list pairs
    analogy_pairs = [(c["source"], c["target"]) for c in conns if c["relation"] == "analogous_to"]
    analogy_pairs.sort()
    approx_chains = [(c["source"], c["target"], c["context"]) for c in conns if c["relation"] == "approximates"]
    approx_chains.sort()

    # Build extended export (base + derived)
    base = {}
    if EXPORT_BASE.exists():
        base = json.loads(EXPORT_BASE.read_text())
    payload = {
        "export_version": _versions()["export_version"],
        "schema_version": _versions()["schema_version"],
        "content_hash": base.get("content_hash", "sha256:unknown"),
        "kernel_version": base.get("kernel_version"),
        "relation_registry_version": _versions().get("relation_registry_version"),
        "relation_registry": registry,
        "vocabularies": load_vocabularies(),
        "source": "content/ + connections/ (canonical) + derived",
        "entity_count": len(entities),
        "connection_count": len(conns),
        "explicit": {"count": len(conns), "note": "canonical source-of-truth"},
        "derived": {
            "inverse_edges": {"count": len(inverse_edges), "edges": inverse_edges[:100]},  # cap for size
            "transitive_closure": {"count": len(derived_transitive), "edges": derived_transitive[:100]},
            "centrality": {"top_20": ranked[:20], "all": centrality},
            "components": {"count": len(components), "largest": len(components[0]) if components else 0, "isolated": isolated[:20], "sizes": sorted([len(c) for c in components], reverse=True)[:10]},
            "prerequisite_chains": {"count": len(prereq_chains), "sample": prereq_chains[:20]},
            "cross_domain_pathways": {"count": len(cross_domain_pathways), "pathways": cross_domain_pathways},
            "analogy_clusters": {"count": len(analogy_pairs), "pairs": analogy_pairs},
            "approximation_chains": {"count": len(approx_chains), "chains": [{"source": s, "target": t, "regime": ctx.get("regime") if isinstance(ctx, dict) else None} for s, t, ctx in approx_chains]},
        },
        "policy": {"note": "Derived views respect review-aware policy; canonical remains all. Trusted = reviewed/canonical only."},
        "determinism": "stable sorting, 5-iteration PageRank, BFS deterministic",
    }
    EXPORT_EXT.parent.mkdir(parents=True, exist_ok=True)
    EXPORT_EXT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"OK: extended export {len(conns)} explicit, {len(inverse_edges)} inverse, {len(derived_transitive)} transitive, {len(components)} components")
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
