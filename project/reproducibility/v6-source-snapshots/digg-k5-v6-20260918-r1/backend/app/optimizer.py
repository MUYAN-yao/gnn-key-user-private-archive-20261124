from __future__ import annotations

from dataclasses import dataclass
import networkx as nx
import numpy as np

from .diffusion import simulate_ic, simulate_sir


@dataclass
class SearchResult:
    seeds: list[str]
    mean_spread: float
    std_spread: float
    objective: float
    community_coverage: int


def simulation_seed_sequence(seed: int, simulations: int) -> list[int]:
    """Return the common random-number streams used for one robust comparison."""
    return [int(value) for value in np.random.default_rng(seed).integers(0, 2**31, size=simulations)]


def evaluate_seed_set(
    graph: nx.DiGraph,
    probabilities: dict[tuple[str, str], float],
    communities: dict[str, int],
    nodes: list[str],
    horizon: int,
    risk_lambda: float,
    community_weight: float,
    diffusion_model: str,
    simulation_seeds: list[int],
) -> SearchResult:
    """Evaluate one seed set with fixed random streams for fair comparisons."""
    sim = simulate_ic if diffusion_model == "ic" else simulate_sir
    values = [
        sim(graph, nodes, probabilities, horizon, np.random.default_rng(run_seed))
        for run_seed in simulation_seeds
    ]
    mean, std = float(np.mean(values)), float(np.std(values))
    coverage = len({communities[node] for node in nodes})
    objective = mean - risk_lambda * std + community_weight * coverage
    return SearchResult(nodes, mean, std, objective, coverage)


def robust_aco(
    graph: nx.DiGraph,
    probabilities: dict[tuple[str, str], float],
    node_prior: dict[str, float],
    communities: dict[str, int],
    k: int,
    horizon: int,
    risk_lambda: float,
    community_weight: float,
    diffusion_model: str,
    ants: int,
    iterations: int,
    simulations: int,
    seed: int,
) -> SearchResult:
    rng = np.random.default_rng(seed)
    ranked = sorted(node_prior, key=node_prior.get, reverse=True)
    candidates = ranked[: max(k * 6, min(80, len(ranked)))]
    pheromone = {node: 1.0 for node in candidates}
    if not candidates:
        raise ValueError("Cannot optimize an empty candidate pool")
    simulation_seeds = simulation_seed_sequence(seed, simulations)
    gnn_seed_set = candidates[: min(k, len(candidates))]
    # Pure GNN is a protected lower bound. ACO may only replace it with a
    # candidate that has a strictly higher robust objective under identical runs.
    best = evaluate_seed_set(
        graph, probabilities, communities, gnn_seed_set, horizon, risk_lambda,
        community_weight, diffusion_model, simulation_seeds,
    )

    def score(nodes: list[str]) -> SearchResult:
        return evaluate_seed_set(
            graph, probabilities, communities, nodes, horizon, risk_lambda,
            community_weight, diffusion_model, simulation_seeds,
        )

    for _ in range(iterations):
        round_best: SearchResult | None = None
        for _ in range(ants):
            selected: list[str] = []
            while len(selected) < min(k, len(candidates)):
                weights = []
                for node in candidates:
                    if node in selected:
                        weights.append(0.0)
                        continue
                    new_community = communities[node] not in {communities[s] for s in selected}
                    heuristic = 0.05 + node_prior[node] + (0.35 if new_community else 0.0)
                    weights.append((pheromone[node] ** 1.0) * (heuristic ** 2.0))
                chosen = candidates[int(rng.choice(len(candidates), p=np.array(weights) / np.sum(weights)))]
                selected.append(chosen)
            result = score(selected)
            if round_best is None or result.objective > round_best.objective:
                round_best = result
            if result.objective > best.objective:
                best = result
        for node in pheromone:
            pheromone[node] *= 0.88
        assert round_best is not None
        for node in round_best.seeds:
            pheromone[node] += max(0.1, round_best.objective / max(len(graph), 1))
    return best


def gnn_guided_robust_greedy(
    graph: nx.DiGraph,
    probabilities: dict[tuple[str, str], float],
    node_prior: dict[str, float],
    communities: dict[str, int],
    k: int,
    horizon: int,
    risk_lambda: float,
    community_weight: float,
    diffusion_model: str,
    simulations: int,
    seed: int,
    candidate_pool_size: int,
) -> SearchResult:
    """Greedily optimize the robust cross-community objective in a GNN pool.

    The learned prior limits expensive evaluation, but every selected seed set
    is scored by the same possible worlds as every baseline.  Returning the
    better of greedy and pure-GNN candidates protects against non-monotonicity
    introduced by the variance penalty.
    """
    ranked = sorted(node_prior, key=lambda node: (-node_prior[node], str(node)))
    candidates = ranked[: min(max(k, candidate_pool_size), len(ranked))]
    if not candidates:
        raise ValueError("Cannot optimize an empty candidate pool")
    simulation_seeds = simulation_seed_sequence(seed, simulations)

    def score(nodes: list[str]) -> SearchResult:
        return evaluate_seed_set(
            graph, probabilities, communities, nodes, horizon, risk_lambda,
            community_weight, diffusion_model, simulation_seeds,
        )

    selected: list[str] = []
    for _ in range(min(k, len(candidates))):
        best_step: SearchResult | None = None
        for node in candidates:
            if node in selected:
                continue
            trial = score(selected + [node])
            if best_step is None or trial.objective > best_step.objective:
                best_step = trial
        assert best_step is not None
        selected = best_step.seeds
    greedy_result = score(selected)
    gnn_result = score(candidates[: min(k, len(candidates))])
    return greedy_result if greedy_result.objective > gnn_result.objective else gnn_result
