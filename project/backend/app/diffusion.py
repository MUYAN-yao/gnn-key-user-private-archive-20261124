from __future__ import annotations

import networkx as nx
import numpy as np


def simulate_ic(graph: nx.DiGraph, seeds: list[str], probabilities: dict[tuple[str, str], float], horizon: int, rng: np.random.Generator) -> int:
    active = set(seeds)
    frontier = set(seeds)
    for _ in range(horizon):
        next_frontier: set[str] = set()
        for source in frontier:
            for target in graph.successors(source):
                if target in active:
                    continue
                probability = probabilities.get((source, target), 0.01)
                if rng.random() < probability:
                    next_frontier.add(target)
        active.update(next_frontier)
        frontier = next_frontier
        if not frontier:
            break
    return len(active)


def simulate_sir(graph: nx.DiGraph, seeds: list[str], probabilities: dict[tuple[str, str], float], horizon: int, rng: np.random.Generator, recovery: float = 0.20) -> int:
    infected, recovered = set(seeds), set()
    ever_infected = set(seeds)
    for _ in range(horizon):
        new: set[str] = set()
        for source in infected:
            for target in graph.successors(source):
                if target not in infected and target not in recovered and rng.random() < probabilities.get((source, target), 0.01):
                    new.add(target)
        recovered.update(node for node in infected if rng.random() < recovery)
        infected.difference_update(recovered)
        infected.update(new)
        ever_infected.update(new)
    return len(ever_infected)
