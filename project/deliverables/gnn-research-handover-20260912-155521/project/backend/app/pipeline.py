from __future__ import annotations

from dataclasses import asdict
import time
import networkx as nx
import numpy as np
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

from .contracts import AnalysisConfig
from .graph import build_snapshot, time_split
from .model import predict_edge_probabilities, train_edge_model
from .optimizer import evaluate_seed_set, gnn_guided_robust_greedy, robust_aco, simulation_seed_sequence
from .baselines import greedy_mc, ris_approximation, select_ranked
from .validation import NetworkDataset


def run_analysis(dataset: NetworkDataset, config: AnalysisConfig) -> dict:
    started = time.perf_counter()
    train_edges, test_edges = time_split(dataset.edges, config.train_fraction)
    snapshot = build_snapshot(dataset, train_edges)
    index = {node: i for i, node in enumerate(snapshot.node_ids)}
    model_edges = [(index[str(row.src)], index[str(row.dst)], float(snapshot.graph[str(row.src)][str(row.dst)]["weight"])) for _, row in train_edges.drop_duplicates(["src", "dst"]).iterrows()]
    model, embeddings, uses_pyg = train_edge_model(snapshot.features, model_edges, config.epochs, config.random_seed)
    train_probability = predict_edge_probabilities(model, embeddings, [(u, v) for u, v, _ in model_edges])
    probability_by_edge = {(snapshot.node_ids[u], snapshot.node_ids[v]): float(np.clip(prob, 0.02, 0.98)) for (u, v, _), prob in zip(model_edges, train_probability)}
    outgoing = {node: [] for node in snapshot.node_ids}
    for (source, target), probability in probability_by_edge.items():
        outgoing[source].append(probability)
    prior = {node: float(np.mean(outgoing[node])) * np.log1p(snapshot.graph.out_degree(node, weight="weight")) if outgoing[node] else 0.0 for node in snapshot.node_ids}
    if max(prior.values(), default=0) > 0:
        maximum = max(prior.values())
        prior = {node: value / maximum for node, value in prior.items()}
    evaluation_seeds = simulation_seed_sequence(config.random_seed, config.simulations)
    selection_started = time.perf_counter()
    if config.optimizer == "aco":
        result = robust_aco(snapshot.graph, probability_by_edge, prior, snapshot.communities, config.seed_count, config.horizon, config.risk_lambda, config.community_weight, config.diffusion_model, config.ants, config.iterations, config.simulations, config.random_seed)
        method_name = "gnn_aco"
    else:
        result = gnn_guided_robust_greedy(
            snapshot.graph, probability_by_edge, prior, snapshot.communities,
            config.seed_count, config.horizon, config.risk_lambda,
            config.community_weight, config.diffusion_model, config.simulations,
            config.random_seed, config.candidate_pool_size,
        )
        method_name = "gnn_guided_robust_greedy"
    selection_seconds = time.perf_counter() - selection_started

    test_pairs = [(index[str(row.src)], index[str(row.dst)]) for _, row in test_edges.drop_duplicates(["src", "dst"]).iterrows()]
    existing = {(u, v) for u, v, _ in model_edges} | set(test_pairs)
    rng = np.random.default_rng(config.random_seed)
    negatives: list[tuple[int, int]] = []
    while len(negatives) < len(test_pairs):
        pair = (int(rng.integers(len(index))), int(rng.integers(len(index))))
        if pair[0] != pair[1] and pair not in existing:
            negatives.append(pair)
    labels = [1] * len(test_pairs) + [0] * len(negatives)
    predicted = predict_edge_probabilities(model, embeddings, test_pairs + negatives).tolist()
    metrics = {}
    if len(set(labels)) > 1:
        bins = np.linspace(0, 1, 11)
        ece = sum(abs(np.mean(np.array(labels)[(np.array(predicted) >= bins[i]) & (np.array(predicted) < bins[i + 1])]) - np.mean(np.array(predicted)[(np.array(predicted) >= bins[i]) & (np.array(predicted) < bins[i + 1])])) * np.mean((np.array(predicted) >= bins[i]) & (np.array(predicted) < bins[i + 1])) for i in range(10) if np.any((np.array(predicted) >= bins[i]) & (np.array(predicted) < bins[i + 1])))
        metrics = {"auc": round(float(roc_auc_score(labels, predicted)), 4), "average_precision": round(float(average_precision_score(labels, predicted)), 4), "brier": round(float(brier_score_loss(labels, predicted)), 4), "ece": round(float(ece), 4)}
    else:
        metrics = {"auc": None, "average_precision": None, "brier": round(float(brier_score_loss(labels, predicted)), 4), "ece": None, "note": "Test window contains one label class; ranking metrics omitted."}
    degree = {node: float(snapshot.graph.out_degree(node, weight="weight")) for node in snapshot.node_ids}
    pagerank = nx.pagerank(snapshot.graph, weight="weight")
    core_graph = snapshot.graph.to_undirected()
    core_graph.remove_edges_from(nx.selfloop_edges(core_graph))
    core = nx.core_number(core_graph) if core_graph.number_of_edges() else {node: 0 for node in snapshot.node_ids}
    baseline_sets = {
        "degree": select_ranked(degree, config.seed_count),
        "pagerank": select_ranked(pagerank, config.seed_count),
        "k_shell": select_ranked({node: float(value) for node, value in core.items()}, config.seed_count),
        "gnn_top_k": select_ranked(prior, config.seed_count),
        "greedy_mc": greedy_mc(snapshot.graph, probability_by_edge, config.seed_count, config.horizon, config.diffusion_model, config.random_seed, min(20, config.simulations)),
        "ris_approx": ris_approximation(snapshot.graph, probability_by_edge, config.seed_count, max(100, len(snapshot.graph) * 20), config.random_seed),
    }
    baseline_results = {
        name: evaluate_seed_set(
            snapshot.graph, probability_by_edge, snapshot.communities, seeds,
            config.horizon, config.risk_lambda, config.community_weight,
            config.diffusion_model, evaluation_seeds,
        )
        for name, seeds in baseline_sets.items()
    }
    baselines = {
        name: {
            "seeds": scored.seeds,
            "mean_spread": round(scored.mean_spread, 3),
            "spread_std": round(scored.std_spread, 3),
            "robust_objective": round(scored.objective, 3),
            "community_coverage": scored.community_coverage,
        }
        for name, scored in baseline_results.items()
    }
    nodes = [{"node_id": node, "score": round(prior[node], 5), "community": snapshot.communities[node], "is_seed": node in result.seeds} for node in sorted(snapshot.node_ids, key=prior.get, reverse=True)]
    edges = [{"source": str(source), "target": str(target), "probability": round(probability_by_edge[(source, target)], 5)} for source, target in snapshot.graph.edges()]
    return {
        "config": config.to_dict(),
        "reproducibility": {"random_seed": config.random_seed, "train_fraction": config.train_fraction, "training_cutoff": snapshot.cutoff, "evaluation_protocol": "common_random_numbers", "backend": "torch-geometric GATv2" if uses_pyg else "PyTorch temporal GAT fallback"},
        "result": {"method": method_name, "top_k": result.seeds, "mean_spread": round(result.mean_spread, 3), "spread_std": round(result.std_spread, 3), "robust_objective": round(result.objective, 3), "community_coverage": result.community_coverage, "selection_seconds": round(selection_seconds, 3)},
        "optimizer_audit": {"gnn_lower_bound_objective": round(baseline_results["gnn_top_k"].objective, 3), "aco_improved_over_gnn": result.objective > baseline_results["gnn_top_k"].objective},
        "calibration": metrics,
        "baselines": baselines,
        "graph": {"nodes": nodes, "edges": edges},
        "runtime_seconds": round(time.perf_counter() - started, 3),
    }
