import pandas as pd

from experiments.v8_candidate_truncation_preflight import fixed_worlds, grouped_history


def test_grouped_history_never_splits_a_timestamp_group():
    edges = pd.DataFrame(
        {
            "src": ["a", "b", "c", "d", "e"],
            "dst": ["b", "c", "d", "e", "f"],
            "timestamp": pd.to_datetime(["2020-01-01", "2020-01-02", "2020-01-02", "2020-01-03", "2020-01-04"], utc=True),
        }
    )
    history, cutoff, groups = grouped_history(edges, fraction=0.5)
    assert groups == 4
    assert cutoff.startswith("2020-01-02")
    assert len(history) == 3


def test_fixed_worlds_are_deterministic_and_unique():
    assert fixed_worlds("digg_pilot5000", 4) == fixed_worlds("digg_pilot5000", 4)
    assert len(set(fixed_worlds("digg_pilot5000", 8))) == 8
    assert fixed_worlds("digg_pilot5000", 4) != fixed_worlds("higgs_pilot1500", 4)
