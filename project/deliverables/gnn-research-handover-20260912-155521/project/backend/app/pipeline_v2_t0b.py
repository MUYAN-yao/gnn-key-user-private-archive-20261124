"""Strict timestamp-grouped v2-T0b influence pipeline."""
from __future__ import annotations

from dataclasses import asdict
import time

import networkx as nx
import numpy as np
import pandas as pd

from . import pipeline_v2_t0 as t0
from .baselines import greedy_mc, ris_approximation, select_ranked
from .contracts import AnalysisConfig
from .graph import build_snapshot
from .optimizer import evaluate_seed_set, gnn_guided_robust_greedy, simulation_seed_sequence
from .validation import NetworkDataset


def split_at_timestamp_group(edges: pd.DataFrame, target_fraction: float) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    counts = edges.groupby("timestamp", sort=True).size()
    if len(counts) < 2:
        raise ValueError("At least two unique timestamps are required")
    target = target_fraction * len(edges)
    candidates = [(abs(float(count) - target), timestamp) for timestamp, count in counts.cumsum().iloc[:-1].items()]
    _, cutoff = min(candidates, key=lambda item: (item[0], item[1]))
    earlier = edges[edges.timestamp < cutoff].copy()
    later = edges[edges.timestamp >= cutoff].copy()
    if earlier.empty or later.empty or not earlier.timestamp.max() < later.timestamp.min():
        raise AssertionError("Timestamp group crossed a v2-T0b boundary")
    return earlier, later, cutoff.isoformat()


def _windows(dataset: NetworkDataset, fraction: float) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    outer_train, outer_test, _ = split_at_timestamp_group(dataset.edges, fraction)
    fit, calibration, _ = split_at_timestamp_group(outer_train, 0.80)
    history, supervised, _ = split_at_timestamp_group(fit, 0.80)
    return history, supervised, calibration, outer_test, outer_train


def run_analysis_v2_t0b(dataset: NetworkDataset, config: AnalysisConfig) -> dict:
    started = time.perf_counter()
    history, supervised, calibration, outer_test, outer_train = _windows(dataset, config.train_fraction)
    decision_snapshot = build_snapshot(dataset, outer_train)
    probabilities, uses_pyg = t0._calibrated_probabilities(
        dataset, history, supervised, calibration, decision_snapshot, config.random_seed
    )
    if set(probabilities) != set(decision_snapshot.graph.edges()):
        raise AssertionError("Every v2-T0b decision edge must receive a probability")
    prior = t0._node_prior(decision_snapshot.graph, probabilities)
    streams = simulation_seed_sequence(config.random_seed, config.simulations)
    selection_started = time.perf_counter()
    result = gnn_guided_robust_greedy(
        decision_snapshot.graph, probabilities, prior, decision_snapshot.communities,
        config.seed_count, config.horizon, config.risk_lambda, config.community_weight,
        config.diffusion_model, config.simulations, config.random_seed, config.candidate_pool_size,
    )
    selection_seconds = time.perf_counter() - selection_started
    degree = {node: float(decision_snapshot.graph.out_degree(node, weight="weight")) for node in decision_snapshot.node_ids}
    pagerank = nx.pagerank(decision_snapshot.graph, weight="weight")
    core_graph = decision_snapshot.graph.to_undirected()
    core_graph.remove_edges_from(nx.selfloop_edges(core_graph))
    core = nx.core_number(core_graph) if core_graph.number_of_edges() else {node: 0 for node in decision_snapshot.node_ids}
    sets = {
        "degree": select_ranked(degree, config.seed_count),
        "pagerank": select_ranked(pagerank, config.seed_count),
        "k_shell": select_ranked({node: float(value) for node, value in core.items()}, config.seed_count),
        "gnn_top_k": select_ranked(prior, config.seed_count),
        "greedy_mc": greedy_mc(decision_snapshot.graph, probabilities, config.seed_count, config.horizon, config.diffusion_model, config.random_seed, min(20, config.simulations)),
        "ris_approx": ris_approximation(decision_snapshot.graph, probabilities, config.seed_count, max(100, len(decision_snapshot.graph) * 20), config.random_seed),
    }
    baselines = {
        name: evaluate_seed_set(decision_snapshot.graph, probabilities, decision_snapshot.communities, seeds, config.horizon, config.risk_lambda, config.community_weight, config.diffusion_model, streams)
        for name, seeds in sets.items()
    }
    window_rows = {"history": len(history), "supervised": len(supervised), "calibration": len(calibration), "outer_test": len(outer_test)}
    return {
        "config": asdict(config),
        "reproducibility": {
            "random_seed": config.random_seed, "train_fraction": config.train_fraction,
            "achieved_outer_train_fraction": len(outer_train) / len(dataset.edges),
            "window_rows": window_rows,
            "encoder_history_cutoff": history.timestamp.max().isoformat(),
            "supervised_cutoff": supervised.timestamp.max().isoformat(),
            "calibration_cutoff": calibration.timestamp.max().isoformat(),
            "outer_test_start": outer_test.timestamp.min().isoformat(),
            "evaluation_protocol": "common_random_numbers",
            "probability_protocol": "v2_t0b_timestamp_grouped_isotonic",
            "backend": "torch-geometric GATv2" if uses_pyg else "PyTorch temporal GAT fallback",
        },
        "result": {"method": "gnn_guided_robust_greedy_v2_t0b", "top_k": result.seeds, "mean_spread": round(result.mean_spread, 3), "spread_std": round(result.std_spread, 3), "robust_objective": round(result.objective, 3), "community_coverage": result.community_coverage, "selection_seconds": round(selection_seconds, 3)},
        "optimizer_audit": {"gnn_lower_bound_objective": round(baselines["gnn_top_k"].objective, 3), "greedy_improved_over_gnn": result.objective > baselines["gnn_top_k"].objective},
        "baselines": {name: {"seeds": scored.seeds, "mean_spread": round(scored.mean_spread, 3), "spread_std": round(scored.std_spread, 3), "robust_objective": round(scored.objective, 3), "community_coverage": scored.community_coverage} for name, scored in baselines.items()},
        "runtime_seconds": round(time.perf_counter() - started, 3),
    }
