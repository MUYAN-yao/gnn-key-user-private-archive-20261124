from experiments.run_v9_candidate_truncation_resolution import DATASETS
from experiments.v9_candidate_truncation_resolution import BUDGETS, SEEDS, WORLD_COUNTS


def test_v9_matrix_size_is_fixed():
    assert len(DATASETS) * len(SEEDS) * len(BUDGETS) * len(WORLD_COUNTS) == 16
