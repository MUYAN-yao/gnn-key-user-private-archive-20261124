from experiments.v8_candidate_truncation_development import first_divergence, pool, worlds


def test_pool_caps_at_available_candidates_and_preserves_rank_prefix():
    ranking = ("a", "b", "c")
    assert pool(ranking, 1, 2) == ("a", "b")
    assert pool(ranking, 16, 2) == ranking


def test_first_divergence_distinguishes_ties_and_changes():
    assert first_divergence(["a", "b"], ["a", "b"]) is None
    assert first_divergence(["a", "b"], ["a", "c"]) == 2


def test_development_world_families_are_separate():
    selection = worlds("digg_pilot5000", 101, "selection", 20)
    evaluation = worlds("digg_pilot5000", 101, "evaluation", 20)
    assert selection != evaluation
    assert len(set(selection)) == 20
