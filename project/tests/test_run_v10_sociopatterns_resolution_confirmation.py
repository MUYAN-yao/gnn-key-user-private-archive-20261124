from experiments.run_v10_sociopatterns_resolution_confirmation import expected_keys


def test_frozen_matrix_has_42_conditions_and_excludes_sfhh_k20():
    keys = expected_keys()
    assert len(keys) == 42
    assert not any(dataset == "sfhh2009" and budget == 20 for dataset, _, budget, _ in keys)
