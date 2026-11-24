import networkx as nx

from app.contracts import AnalysisConfig
from experiments.run_v4_screening_diagnostic import ranked, trace_greedy


def test_ranked_is_score_then_stable_id():
    assert ranked({"2": 1.0, "10": 1.0, "3": .5}) == ["10", "2", "3"]


def test_trace_records_all_candidates_and_world_values():
    graph = nx.DiGraph()
    graph.add_edges_from([("a", "x"), ("b", "y")])
    probabilities = {edge: 1.0 for edge in graph.edges}
    communities = {"a": 0, "b": 1, "x": 0, "y": 1}
    config = AnalysisConfig(seed_count=2, horizon=1, risk_lambda=.35, community_weight=.25,
                            diffusion_model="ic", random_seed=1, epochs=1, ants=1,
                            iterations=1, simulations=2, train_fraction=.7,
                            optimizer="robust_greedy", candidate_pool_size=2)
    result = trace_greedy(graph, probabilities, communities, ["b", "a"], config, [1, 2],
                          {node:i for i,node in enumerate(sorted(graph.nodes))})
    assert result["canonical_candidate_order"] == ["a", "b"]
    assert len(result["rounds"][0]["candidate_scores"]) == 2
    assert len(result["rounds"][1]["candidate_scores"]) == 1
    assert result["rounds"][0]["exact_best_tie_count"] == 2
    assert result["selection"]["world_spreads"] == [4, 4]
