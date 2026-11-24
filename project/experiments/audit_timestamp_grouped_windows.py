"""Audit strict timestamp-grouped temporal windows for v2-T0b."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from app.validation import load_dataset


def split_at_timestamp_group(edges: object, target_fraction: float) -> tuple[object, object, str]:
    if not 0 < target_fraction < 1:
        raise ValueError("target_fraction must be strictly between zero and one")
    counts = edges.groupby("timestamp", sort=True).size()
    if len(counts) < 2:
        raise ValueError("At least two unique timestamps are required")
    target = target_fraction * len(edges)
    cumulative = counts.cumsum().iloc[:-1]
    candidates = [(abs(float(count) - target), timestamp, int(count)) for timestamp, count in cumulative.items()]
    _, cutoff, _ = min(candidates, key=lambda item: (item[0], item[1]))
    earlier = edges[edges.timestamp < cutoff].copy()
    later = edges[edges.timestamp >= cutoff].copy()
    if earlier.empty or later.empty:
        raise AssertionError("Timestamp-grouped split produced an empty window")
    if not earlier.timestamp.max() < later.timestamp.min():
        raise AssertionError("Timestamp group crossed a temporal boundary")
    return earlier, later, cutoff.isoformat()


def describe(frame: object) -> dict[str, object]:
    return {
        "rows": int(len(frame)),
        "first_timestamp": frame.timestamp.min().isoformat(),
        "last_timestamp": frame.timestamp.max().isoformat(),
        "unique_timestamps": int(frame.timestamp.nunique()),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--fractions", type=float, nargs="+", default=[0.60, 0.65, 0.70])
    args = parser.parse_args()
    output = Path(args.output)
    if output.exists():
        parser.error(f"Refusing to overwrite existing audit: {output}")
    edges = load_dataset(args.dataset).edges
    report: dict[str, object] = {"total_rows": int(len(edges)), "fractions": {}}
    for fraction in args.fractions:
        outer_train, outer_test, outer_cutoff = split_at_timestamp_group(edges, fraction)
        fit, calibration, fit_cutoff = split_at_timestamp_group(outer_train, 0.80)
        history, supervised, history_cutoff = split_at_timestamp_group(fit, 0.80)
        report["fractions"][f"{fraction:.2f}"] = {
            "nominal_outer_fraction": fraction,
            "achieved_outer_fraction": len(outer_train) / len(edges),
            "achieved_history_fraction": len(history) / len(edges),
            "achieved_supervised_fraction": len(supervised) / len(edges),
            "achieved_calibration_fraction": len(calibration) / len(edges),
            "cutoffs": {"history": history_cutoff, "supervised": fit_cutoff, "outer": outer_cutoff},
            "windows": {
                "history": describe(history),
                "supervised": describe(supervised),
                "calibration": describe(calibration),
                "outer_test": describe(outer_test),
            },
        }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
