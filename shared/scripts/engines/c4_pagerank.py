"""
D4 — PageRank Utterance-DAG Ranking
Reference: Brin S. and Page L. (1998), "The anatomy of a large-scale hypertextual Web search engine", Stanford InfoLab.
Role: Rank which agent utterances actually shaped the final output vs. conversational noise.
"""
from __future__ import annotations


def pagerank(dag: dict, damping: float = 0.85, eps: float = 1e-6) -> dict:
    """Compute PageRank over an outgoing-adjacency dict: {node: [out_neighbor, ...]}.

    Returns {node: score} with sum(scores) == 1.0 (within float error). Dangling nodes
    (no outgoing edges) redistribute uniformly — the standard Brin-Page treatment.
    """
    nodes = list(dag.keys())
    # Include any dest-only nodes reachable but not listed as keys
    for outs in dag.values():
        for dst in outs:
            if dst not in dag:
                nodes.append(dst)
    nodes = list(dict.fromkeys(nodes))  # de-dup preserving order
    n = len(nodes)
    if n == 0:
        return {}

    idx = {node: i for i, node in enumerate(nodes)}
    outs = [list(dag.get(node, [])) for node in nodes]

    pr = [1.0 / n] * n
    teleport = (1.0 - damping) / n

    for _ in range(100):  # hard cap
        new = [teleport] * n
        dangling_mass = 0.0
        for i, out_list in enumerate(outs):
            if not out_list:
                dangling_mass += pr[i]
                continue
            share = damping * pr[i] / len(out_list)
            for dst in out_list:
                new[idx[dst]] += share
        dang_share = damping * dangling_mass / n
        for i in range(n):
            new[i] += dang_share
        # Convergence check
        delta = sum(abs(new[i] - pr[i]) for i in range(n))
        pr = new
        if delta < eps:
            break

    return {nodes[i]: pr[i] for i in range(n)}
