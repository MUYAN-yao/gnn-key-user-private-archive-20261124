from experiments.run_v8_candidate_truncation_development import BUDGETS, DATASETS, METHOD_IDS, SEEDS


def test_frozen_development_matrix_has_the_declared_number_of_method_runs():
    assert len(DATASETS) * len(BUDGETS) * len(SEEDS) * len(METHOD_IDS) == 144
    assert METHOD_IDS[0] == "full"
    assert "degree_doubling" in METHOD_IDS
