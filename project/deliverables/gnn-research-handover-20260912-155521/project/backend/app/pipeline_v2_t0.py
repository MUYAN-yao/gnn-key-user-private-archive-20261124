"""Leakage-checked v2-T0 influence pipeline isolated from frozen v1 code."""
from __future__ import annotations

from dataclasses import asdict
import random
import time

import networkx as nx
import numpy as np
from sklearn.isotonic import IsotonicRegression
import torch

from .baselines import greedy_mc, ris_approximation, select_ranked
from .contracts import AnalysisConfig
from .graph import build_snapshot, time_split
from .model_v2 import predict_edge_probabilities_v2, train_edge_model_v2
from .optimizer import (
    evaluate_seed_set,
    gnn_guided_robust_greedy,
    simulation_seed_sequence,
)
from .validation import NetworkDataset


T0_CONFIG = {
    "epochs": 10,
    "hidden_channels": 32,
    "layers": 1,
    "learning_rate": 0.01,
    "decoder": "concat_mlp",
}
PROBABILITY_BOUNDS = (0.02, 0.98)


def _set_determinism(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True)


def _sample_never_observed(
    node_count: int, observed: set[tuple[int, int]], count: int, seed: int
) -> list[tuple[int, int]]:
    if count > node_count * (node_count - 1) - len(observed):
        raise ValueError("Not enough never-observed directed pairs for calibration")
    rng = np.random.default_rng(seed)
    pairs: list[tuple[int, int]] = []
    selected: set[tuple[int, int]] = set()
    while len(pairs) < count:
        pair = (int(rng.integers(node_count)), int(rng.integers(node_count)))
        if pair[0] != pair[1] and pair not in observed and pair not in selected:
            pairs.append(pair)
            selected.add(pair)
    return pairs


def _indexed_pairs(frame: object, index: dict[str, int]) -> list[tuple[int, int]]:
    return [
        (index[str(row.src)], index[str(row.dst)])
        for _, row in frame.drop_duplicates(["src", "dst"]).iterrows()
    ]


def _assert_windows(history: object, supervised: object, calibration: object, outer_test: object) -> None:
    windows = (history, supervised, calibration, outer_test)
    if any(window.empty for window in windows):
        raise ValueError("Each v2-T0 temporal window must contain at least one edge")
    if not (
        history.timestamp.max() <= supervised.timestamp.min()
        and supervised.timestamp.max() <= calibration.timestamp.min()
        and calibration.timestamp.max() <= outer_test.timestamp.min()
    ):
        raise AssertionError("Temporal v2-T0 windows overlap out of order")


def _temporal_windows(dataset: NetworkDataset, fraction: float) -> tuple[object, object, object, object]:
    outer_train, outer_test = time_split(dataset.edges, fraction)
    fit_end = max(1, int(len(outer_train) * 0.80))
    history_end = max(1, int(fit_end * 0.80))
    history = outer_train.iloc[:history_end].copy()
    supervised = outer_train.iloc[history_end:fit_end].copy()
    calibration = outer_train.iloc[fit_end:].copy()
    _assert_windows(history, supervised, calibration, outer_test)
    return history, supervised, calibration, outer_test


def _calibrated_probabilities(
    dataset: NetworkDataset,
    history_edges: object,
    supervised_edges: object,
    calibration_edges: object,
    decision_snapshot: object,
    seed: int,
) -> tuple[dict[tuple[str, str], float], bool]:
    history_snapshot = build_snapshot(dataset, history_edges)
    if history_snapshot.node_ids != decision_snapshot.node_ids:
        raise AssertionError("Decision and encoder snapshots must use the same node universe")
    index = {node: position for position, node in enumerate(history_snapshot.node_ids)}
    history_model_edges = [
        (
            index[str(row.src)],
            index[str(row.dst)],
            float(history_snapshot.graph[str(row.src)][str(row.dst)]["weight"]),
        )
        for _, row in history_edges.drop_duplicates(["src", "dst"]).iterrows()
    ]
    supervised_pairs = _indexed_pairs(supervised_edges, index)
    _set_determinism(seed)
    model, embeddings, uses_pyg = train_edge_model_v2(
        history_snapshot.features,
        history_model_edges,
        seed=seed,
        supervised_positive_pairs=supervised_pairs,
        **T0_CONFIG,
    )
    all_observed = {
        (index[str(row.src)], index[str(row.dst)])
        for _, row in dataset.edges.drop_duplicates(["src", "dst"]).iterrows()
    }
    calibration_positive = _indexed_pairs(calibration_edges, index)
    calibration_negative = _sample_never_observed(
        len(index), all_observed, len(calibration_positive), seed
    )
    calibration_pairs = calibration_positive + calibration_negative
    calibration_labels = np.concatenate(
        [np.ones(len(calibration_positive), dtype=np.int8), np.zeros(len(calibration_negative), dtype=np.int8)]
    )
    calibration_scores = predict_edge_probabilities_v2(model, embeddings, calibration_pairs)
    calibrator = IsotonicRegression(out_of_bounds="clip").fit(calibration_scores, calibration_labels)
    decision_pairs = [
        (index[str(source)], index[str(target)])
        for source, target in decision_snapshot.graph.edges()
    ]
    decision_scores = predict_edge_probabilities_v2(model, embeddings, decision_pairs)
    probabilities = np.clip(calibrator.predict(decision_scores), *PROBABILITY_BOUNDS)
    return {
        (str(source), str(target)): float(probability)
        for (source, target), probability in zip(decision_snapshot.graph.edges(), probabilities)
    }, uses_pyg


def _node_prior(graph: nx.DiGraph, probabilities: dict[tuple[str, str], float]) -> dict[str, float]:
    outgoing = {node: [] for node in graph.nodes}
    for (source, _), probability in probabilities.items():
        outgoing[source].append(probability)
    prior = {
        node: float(np.mean(outgoing[node])) * np.log1p(graph.out_degree(node, weight="weight"))
        if outgoing[node]
        else 0.0
        for node in graph.nodes
    }
    maximum = max(prior.values(), default=0.0)
    return {node: value / maximum for node, value in prior.items()} if maximum > 0 else prior


def run_analysis_v2_t0(dataset: NetworkDataset, config: AnalysisConfig) -> dict:
    """Run one fixed-candidate v2-T0 comparison without accessing outer-test data."""
    started = time.perf_counter()
    history_edges, supervised_edges, calibration_edges, outer_test = _temporal_windows(
        dataset, config.train_fraction
    )
    decision_edges, _ = time_split(dataset.edges, config.train_fraction)
    decision_snapshot = build_snapshot(dataset, decision_edges)
    probabilities, uses_pyg = _calibrated_probabilities(
        dataset,
        history_edges,
        supervised_edges,
        calibration_edges,
        decision_snapshot,
        config.random_seed,
    )
    if set(probabilities) != set(decision_snapshot.graph.edges()):
        raise AssertionError("Every decision-graph edge must receive one calibrated T0 probability")
    prior = _node_prior(decision_snapshot.graph, probabilities)
    evaluation_seeds = simulation_seed_sequence(config.random_seed, config.simulations)
    selection_started = time.perf_counter()
    result = gnn_guided_robust_greedy(
        decision_snapshot.graph,
        probabilities,
        prior,
        decision_snapshot.communities,
        config.seed_count,
        config.horizon,
        config.risk_lambda,
        config.community_weight,
        config.diffusion_model,
        config.simulations,
        config.random_seed,
        config.candidate_pool_size,
    )
    selection_seconds = time.perf_counter() - selection_started
    degree = {node: float(decision_snapshot.graph.out_degree(node, weight="weight")) for node in decision_snapshot.node_ids}
    pagerank = nx.pagerank(decision_snapshot.graph, weight="weight")
    core_graph = decision_snapshot.graph.to_undirected()
    core_graph.remove_edges_from(nx.selfloop_edges(core_graph))
    core = nx.core_number(core_graph) if core_graph.number_of_edges() else {node: 0 for node in decision_snapshot.node_ids}
    baseline_sets = {
        "degree": select_ranked(degree, config.seed_count),
        "pagerank": select_ranked(pagerank, config.seed_count),
        "k_shell": select_ranked({node: float(value) for node, value in core.items()}, config.seed_count),
        "gnn_top_k": select_ranked(prior, config.seed_count),
        "greedy_mc": greedy_mc(decision_snapshot.graph, probabilities, config.seed_count, config.horizon, config.diffusion_model, config.random_seed, min(20, config.simulations)),
        "ris_approx": ris_approximation(decision_snapshot.graph, probabilities, config.seed_count, max(100, len(decision_snapshot.graph) * 20), config.random_seed),
    }
    baseline_results = {
        name: evaluate_seed_set(
            decision_snapshot.graph,
            probabilities,
            decision_snapshot.communities,
            seeds,
            config.horizon,
            config.risk_lambda,
            config.community_weight,
            config.diffusion_model,
            evaluation_seeds,
        )
        for name, seeds in baseline_sets.items()
    }
    return {
        "config": asdict(config),
        "reproducibility": {
            "random_seed": config.random_seed,
            "train_fraction": config.train_fraction,
            "training_cutoff": decision_snapshot.cutoff,
            "encoder_history_cutoff": history_edges.timestamp.max().isoformat(),
            "supervised_cutoff": supervised_edges.timestamp.max().isoformat(),
            "calibration_cutoff": calibration_edges.timestamp.max().isoformat(),
            "outer_test_start": outer_test.timestamp.min().isoformat(),
            "evaluation_protocol": "common_random_numbers",
            "probability_protocol": "v2_t0_temporal_isotonic",
            "backend": "torch-geometric GATv2" if uses_pyg else "PyTorch temporal GAT fallback",
        },
        "result": {
            "method": "gnn_guided_robust_greedy_v2_t0",
            "top_k": result.seeds,
            "mean_spread": round(result.mean_spread, 3),
            "spread_std": round(result.std_spread, 3),
            "robust_objective": round(result.objective, 3),
            "community_coverage": result.community_coverage,
            "selection_seconds": round(selection_seconds, 3),
        },
        "optimizer_audit": {
            "gnn_lower_bound_objective": round(baseline_results["gnn_top_k"].objective, 3),
            "greedy_improved_over_gnn": result.objective > baseline_results["gnn_top_k"].objective,
        },
        "baselines": {
            name: {
                "seeds": scored.seeds,
                "mean_spread": round(scored.mean_spread, 3),
                "spread_std": round(scored.std_spread, 3),
                "robust_objective": round(scored.objective, 3),
                "community_coverage": scored.community_coverage,
            }
            for name, scored in baseline_results.items()
        },
        "runtime_seconds": round(time.perf_counter() - started, 3),
    }
