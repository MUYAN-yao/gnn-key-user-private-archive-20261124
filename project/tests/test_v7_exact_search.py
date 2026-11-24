from fractions import Fraction

import pytest

from experiments.v7_exact_search import (
    CandidateEvaluator,
    SearchLimitExceeded,
    SimulationCache,
    exact_score_micro,
    full_greedy,
    partial_upper_micro,
    risk_bound_greedy,
    round_half_even_fraction,
)
from experiments.v7_micrograph_harness import WORLDS, fixed_micrographs, run_check


def test_half_even_fraction_including_negative_boundaries():
    assert round_half_even_fraction(Fraction(1, 2), 1) == 0
    assert round_half_even_fraction(Fraction(3, 2), 1) == 2
    assert round_half_even_fraction(Fraction(-1, 2), 1) == 0
    assert round_half_even_fraction(Fraction(-3, 2), 1) == -2


def test_completed_score_has_no_numpy_round_dependency_and_handles_negative_objective():
    score = exact_score_micro([0, 0, 8], 0, risk_lambda=Fraction(1), community_weight=Fraction(0))
    assert score < 0
    assert exact_score_micro([1, 1], 0, risk_lambda=Fraction(1), community_weight=Fraction(0)) == 1_000_000


def test_partial_bound_is_conservative_at_zero_and_full_prefixes():
    final_score = exact_score_micro([0, 0, 8], 0, risk_lambda=Fraction(1), community_weight=Fraction(0))
    assert partial_upper_micro([], 3, 8, 0, risk_lambda=Fraction(1), community_weight=Fraction(0)) >= final_score
    assert partial_upper_micro([0, 0, 8], 3, 8, 0, risk_lambda=Fraction(1), community_weight=Fraction(0)) >= final_score


def test_micrograph_harness_exhaustively_matches_full_search():
    report = run_check()
    assert report["status"] == "PASS"
    assert report["checked_structural_cases"] > 0
    assert report["checked_partial_cases"] > report["checked_structural_cases"]
    assert report["checked_trajectories"] > 0
    assert report["unsafe_prunes"] == 0
    assert report["trajectory_mismatches"] == 0


def test_node_id_tie_break_is_canonical_and_equal_bound_is_not_pruned():
    fixture = fixed_micrographs()["exact_and_near_ties"]
    result = risk_bound_greedy(
        fixture["graph"], fixture["probabilities"], fixture["communities"], WORLDS,
        horizon=1, seed_count=1, ranking=tuple(reversed(sorted(fixture["graph"]))), initial_count=1,
        risk_lambda=Fraction(0), community_weight=Fraction(0),
    )
    reference = full_greedy(
        fixture["graph"], fixture["probabilities"], fixture["communities"], WORLDS,
        horizon=1, seed_count=1, risk_lambda=Fraction(0), community_weight=Fraction(0),
    )
    assert result["selected"] == reference["selected"]
    assert reference["selected"][0] == "10"


def test_cache_reuse_clear_and_limit_are_explicit():
    fixture = fixed_micrographs()["directed_chain"]
    cache = SimulationCache()
    evaluator = CandidateEvaluator(fixture["graph"], fixture["probabilities"], 4, {node: index for index, node in enumerate(sorted(fixture["graph"]))}, cache)
    first = evaluator.values(["0"], WORLDS)
    assert evaluator.values(["0"], WORLDS) == first
    assert cache.hits == len(WORLDS)
    cache.clear()
    assert not cache.values and cache.hits == cache.misses == 0
    limited = CandidateEvaluator(fixture["graph"], fixture["probabilities"], 4, {node: index for index, node in enumerate(sorted(fixture["graph"]))}, SimulationCache(), max_world_evaluations=1)
    with pytest.raises(SearchLimitExceeded):
        limited.values(["0"], WORLDS)


def test_full_reference_can_restrict_only_the_candidate_universe():
    fixture = fixed_micrographs()["out_star"]
    result = full_greedy(
        fixture["graph"], fixture["probabilities"], fixture["communities"], WORLDS,
        horizon=1, seed_count=1, candidate_universe=["1", "2"],
        risk_lambda=Fraction(0), community_weight=Fraction(0),
    )
    assert result["selected"] == ["1"]
