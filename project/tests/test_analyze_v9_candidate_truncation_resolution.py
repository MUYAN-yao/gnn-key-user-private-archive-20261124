import json

from experiments.analyze_v9_candidate_truncation_resolution import summarize


def _arm(top_k, margins, mean):
    return {
        "selection": {"top_k": top_k, "rounds": [{"winner_margin_micro": value, "exact_best_tie_count": 1 if value else 2} for value in margins]},
        "evaluation": {"mean_spread": mean},
        "comparison_to_full": {"same_ordered_top_k": False, "first_divergence": 1, "mean_spread_delta": mean - 10},
        "decision_seconds": 0.1,
    }


def _condition(dataset, seed, k, world_count, full_top_k, margins):
    report = {
        "development_only": True,
        "dataset": dataset,
        "seed": seed,
        "k": k,
        "selection_world_count": world_count,
        "arms": {
            "full": _arm(full_top_k, margins, 10),
            "degree_2k": _arm(["x", "b"], [1, 1], 9),
            "degree_4k": _arm(full_top_k, [1, 1], 10),
            "degree_8k": _arm(full_top_k, [1, 2], 10),
        },
    }
    for arm in report["arms"].values():
        arm["comparison_to_full"]["same_ordered_top_k"] = arm["selection"]["top_k"] == full_top_k
    return report


def test_summarize_pairs_nested_world_conditions_and_marks_ties(tmp_path):
    root = tmp_path / "run"
    root.mkdir()
    reports = [
        _condition("digg_pilot5000", 104, 5, 20, ["a", "b"], [0, 2]),
        _condition("digg_pilot5000", 104, 5, 80, ["c", "b"], [3, 4]),
    ]
    for index, report in enumerate(reports):
        path = root / f"{index}.json"
        path.write_text(json.dumps(report), encoding="utf-8")
    summary = summarize(root, expected_conditions=2)
    assert summary["condition_count"] == 2
    assert summary["full_cross_w"][0]["same_ordered_top_k"] is False
    assert summary["full_cross_w"][0]["w20"]["zero_margin_rounds"] == 1
    assert summary["method_by_w"]["20"]["degree_4k"]["same_as_full_count"] == 1
