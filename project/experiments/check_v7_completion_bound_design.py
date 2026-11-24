"""Bounded, training-free arithmetic check for the proposed v7 design.

This enumerates small integer spread vectors, not graph experiments. It does
not validate a production implementation, floating-point certification, or
novelty. The companion method note contains the mathematical derivation.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from pathlib import Path


def check() -> dict:
    cases = 0
    largest_violation = 0.0
    largest_terminal_error = 0.0
    for count in range(1, 7):
        for values in itertools.product(range(5), repeat=count):
            mean = math.fsum(values) / count
            std = math.sqrt(math.fsum((v - mean) ** 2 for v in values) / count)
            for observed_count in range(count + 1):
                observed = values[:observed_count]
                observed_mean = math.fsum(observed) / observed_count if observed_count else 0.0
                sse = math.fsum((v - observed_mean) ** 2 for v in observed)
                mean_upper = (math.fsum(observed) + (count - observed_count) * 4) / count
                for risk_lambda in (0.0, 0.35, 1.0):
                    bound = mean_upper - risk_lambda * math.sqrt(sse / count)
                    objective = mean - risk_lambda * std
                    largest_violation = max(largest_violation, objective - bound)
                    if observed_count == count:
                        largest_terminal_error = max(largest_terminal_error, abs(bound - objective))
                    cases += 1
    if largest_violation > 1e-12 or largest_terminal_error > 1e-12:
        raise AssertionError((largest_violation, largest_terminal_error))
    return {
        "status": "passed_small_vector_design_check",
        "study_status": "design_only_not_inferential",
        "graph_experiments": 0,
        "training_runs": 0,
        "vector_lengths": [1, 2, 3, 4, 5, 6],
        "value_support": [0, 1, 2, 3, 4],
        "completion_upper_bound": 4,
        "risk_lambdas": [0.0, 0.35, 1.0],
        "checked_vector_prefix_lambda_cases": cases,
        "largest_observed_bound_violation": largest_violation,
        "largest_complete_vector_equality_error": largest_terminal_error,
        "limits": [
            "Not a proof over all real vectors; use the accompanying derivation.",
            "Does not establish efficient pruning on any network.",
            "Does not verify topology bounds, tie handling or outward-rounded production arithmetic.",
            "Does not establish scientific novelty or publication readiness.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"Refusing to overwrite {args.output}")
    result = check()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, ensure_ascii=False, indent=2)
        stream.write("\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
