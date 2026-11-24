from experiments.v9_candidate_truncation_resolution import worlds


def test_resolution_worlds_are_nested_and_family_separate():
    assert worlds("digg_pilot5000", 104, "selection", 20) == worlds("digg_pilot5000", 104, "selection", 80)[:20]
    assert worlds("digg_pilot5000", 104, "selection", 20) != worlds("digg_pilot5000", 104, "evaluation", 20)
