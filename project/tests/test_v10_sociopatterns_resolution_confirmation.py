from experiments.v10_sociopatterns_resolution_confirmation import world_ids


def test_nested_selection_worlds_and_independent_evaluation_worlds():
    assert world_ids("invs2013", 301, "selection", 20) == world_ids("invs2013", 301, "selection", 80)[:20]
    assert world_ids("invs2013", 301, "selection", 20) != world_ids("invs2013", 301, "evaluation", 20)
