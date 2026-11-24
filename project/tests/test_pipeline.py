from pathlib import Path
import pandas as pd

from app.contracts import AnalysisConfig
from app.optimizer import evaluate_seed_set, gnn_guided_robust_greedy, robust_aco, simulation_seed_sequence
from app.pipeline import run_analysis
from app.validation import load_dataset


def test_analysis_returns_reproducible_top_k():
    dataset = load_dataset(Path("sample_data"))
    config = AnalysisConfig(seed_count=2, epochs=5, ants=3, iterations=2, simulations=5)
    result = run_analysis(dataset, config)
    assert len(result["result"]["top_k"]) == 2
    assert len(set(result["result"]["top_k"])) == 2
    assert result["reproducibility"]["random_seed"] == 42
    assert result["reproducibility"]["train_fraction"] == 0.70
    assert result["reproducibility"]["evaluation_protocol"] == "common_random_numbers"
    assert result["result"]["robust_objective"] >= result["optimizer_audit"]["gnn_lower_bound_objective"]
    assert result["graph"]["nodes"]
    assert {"degree", "pagerank", "k_shell", "gnn_top_k", "greedy_mc", "ris_approx"} <= set(result["baselines"])
    assert all({"mean_spread", "spread_std", "robust_objective", "community_coverage"} <= set(values) for values in result["baselines"].values())
    assert result["baselines"]["gnn_top_k"]["robust_objective"] == result["optimizer_audit"]["gnn_lower_bound_objective"]


def test_analysis_accepts_self_loops_in_input():
    dataset = load_dataset(Path("sample_data"))
    dataset.edges = pd.concat([dataset.edges, pd.DataFrame([{
        "src": "u1", "dst": "u1", "timestamp": dataset.edges.timestamp.iloc[0], "event_type": "retweet", "weight": 1,
    }])], ignore_index=True)
    result = run_analysis(dataset, AnalysisConfig(seed_count=2, epochs=5, ants=3, iterations=2, simulations=5))
    assert result["baselines"]["k_shell"]["seeds"]


def test_aco_preserves_pure_gnn_robust_lower_bound():
    graph = __import__("networkx").DiGraph()
    graph.add_edges_from([("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")])
    probabilities = {edge: 0.8 for edge in graph.edges}
    prior = {"a": 1.0, "b": 0.7, "c": 0.6, "d": 0.1}
    communities = {"a": 0, "b": 0, "c": 1, "d": 1}
    result = robust_aco(graph, probabilities, prior, communities, 2, 3, 0.35, 0.25, "ic", 3, 2, 8, 42)
    simulation_seeds = simulation_seed_sequence(42, 8)
    gnn = evaluate_seed_set(graph, probabilities, communities, ["a", "b"], 3, 0.35, 0.25, "ic", simulation_seeds)
    assert result.objective >= gnn.objective


def test_gnn_guided_robust_greedy_preserves_pure_gnn_lower_bound():
    graph = __import__("networkx").DiGraph()
    graph.add_edges_from([("a", "b"), ("a", "c"), ("b", "d"), ("c", "d")])
    probabilities = {edge: 0.8 for edge in graph.edges}
    prior = {"a": 1.0, "b": 0.7, "c": 0.6, "d": 0.1}
    communities = {"a": 0, "b": 0, "c": 1, "d": 1}
    result = gnn_guided_robust_greedy(graph, probabilities, prior, communities, 2, 3, 0.35, 0.25, "ic", 8, 42, 4)
    gnn = evaluate_seed_set(graph, probabilities, communities, ["a", "b"], 3, 0.35, 0.25, "ic", simulation_seed_sequence(42, 8))
    assert result.objective >= gnn.objective


def test_validation_preserves_numeric_ids_when_parents_are_blank(tmp_path):
    (tmp_path / "nodes.csv").write_text("node_id\n1\n2\n", encoding="utf-8")
    (tmp_path / "edges.csv").write_text("src,dst,timestamp\n1,2,2020-01-01T00:00:00Z\n2,1,2020-01-02T00:00:00Z\n", encoding="utf-8")
    (tmp_path / "cascades.csv").write_text("cascade_id,user_id,parent_user_id,event_time\nc1,1,,2020-01-01T00:00:00Z\nc1,2,1,2020-01-02T00:00:00Z\n", encoding="utf-8")
    dataset = load_dataset(tmp_path)
    assert dataset.cascades.parent_user_id.dropna().tolist() == ["1"]
