from __future__ import annotations

import heapq
import networkx as nx
import numpy as np

from .diffusion import simulate_ic, simulate_sir


def select_ranked(scores: dict[str, float], k: int) -> list[str]:
    return sorted(scores, key=scores.get, reverse=True)[:k]


def greedy_mc(graph: nx.DiGraph, probabilities: dict[tuple[str, str], float], k: int, horizon: int, model: str, seed: int, simulations: int = 20) -> list[str]:
    """CELF lazy-greedy baseline for expected influence maximization."""
    candidates, selected = list(graph.nodes), []
    simulator = simulate_ic if model == "ic" else simulate_sir
    rng = np.random.default_rng(seed)
    worlds = [int(value) for value in rng.integers(0, 2**31, size=simulations)]

    def score(nodes: list[str]) -> float:
        return float(np.mean([simulator(graph, nodes, probabilities, horizon, np.random.default_rng(world)) for world in worlds]))

    heap = [(-score([node]), str(node), 0) for node in candidates]
    heapq.heapify(heap)
    while heap and len(selected) < k:
        neg_score, node, updated_at = heapq.heappop(heap)
        if updated_at == len(selected):
            selected.append(node)
            continue
        heapq.heappush(heap, (-score(selected + [node]), node, len(selected)))
    return selected


def ris_approximation(graph: nx.DiGraph, probabilities: dict[tuple[str, str], float], k: int, samples: int, seed: int) -> list[str]:
    """Small-network RR-set approximation used as an IMM/RIS comparison point."""
    rng = np.random.default_rng(seed)
    rr_sets: list[set[str]] = []
    nodes = list(graph.nodes)
    for _ in range(samples):
        target, rr, frontier = nodes[int(rng.integers(len(nodes)))], set(), set()
        rr.add(target); frontier.add(target)
        while frontier:
            current = frontier.pop()
            for parent in graph.predecessors(current):
                if parent not in rr and rng.random() < probabilities.get((parent, current), 0.01):
                    rr.add(parent); frontier.add(parent)
        rr_sets.append(rr)
    selected: list[str] = []
    for _ in range(min(k, len(nodes))):
        node = max((n for n in nodes if n not in selected), key=lambda n: sum(n in rr for rr in rr_sets))
        selected.append(node)
        rr_sets = [rr for rr in rr_sets if node not in rr]
    return selected


def evaluate(graph: nx.DiGraph, seeds: list[str], probabilities: dict[tuple[str, str], float], horizon: int, model: str, simulations: int, seed: int) -> dict[str, float]:
    simulator = simulate_ic if model == "ic" else simulate_sir
    rng = np.random.default_rng(seed)
    values = [simulator(graph, seeds, probabilities, horizon, np.random.default_rng(int(rng.integers(2**31)))) for _ in range(simulations)]
    return {"mean_spread": round(float(np.mean(values)), 3), "spread_std": round(float(np.std(values)), 3)}
