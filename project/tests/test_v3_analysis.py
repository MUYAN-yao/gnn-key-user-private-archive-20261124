import pandas as pd

from experiments.build_v3_fairness_sensitivity_analysis import (
    FRACTIONS,
    SEEDS,
    descriptive_markdown,
    descriptive_sensitivity,
    expected_methods,
    jaccard,
)


def test_v3_jaccard_handles_sets_and_empty_selection():
    assert jaccard(["a", "b"], ["b", "c"]) == 1 / 3
    assert jaccard([], []) == 1.0


def test_v3_descriptive_summary_covers_all_registered_methods():
    rows = []
    for fraction in FRACTIONS:
        for method in expected_methods():
            for _seed in SEEDS:
                rows.append(
                    {
                        "train_fraction": fraction,
                        "method": method,
                        "mean_spread": 10.0,
                        "spread_std": 2.0,
                        "community_coverage": 1.0,
                        "selection_seconds": 3.0,
                        "jaccard_with_full_candidate": 1.0,
                        "jaccard_with_base_screened": 1.0,
                        "top_k": '["1", "2"]',
                    }
                )
    summary = descriptive_sensitivity(pd.DataFrame(rows))
    assert len(summary) == len(FRACTIONS) * len(expected_methods())
    assert set(summary["paired_run_count"]) == {len(SEEDS)}
    assert "Jaccard vs full" in descriptive_markdown(summary)
