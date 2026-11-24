"""Record the exact simulation-call budget before launching a v3 full batch."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))
from run_rolling_study_v2_t0 import expected_higgs_hashes, sha256


def greedy_evaluations(candidate_count: int, k: int) -> int:
    if candidate_count < k:
        raise ValueError("Candidate count must be at least the seed budget")
    return sum(candidate_count - step for step in range(k))


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            result.update(chunk)
    return result.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--frozen-manifest", default="reproducibility/frozen-study-manifest-v1.json")
    args = parser.parse_args()
    output = Path(args.output_dir)
    if output.exists() and any(output.iterdir()):
        parser.error("Refusing to overwrite a non-empty audit directory")
    dataset_dir = Path(args.dataset)
    inputs = {name: sha256(dataset_dir / name) for name in ("nodes.csv", "edges.csv", "cascades.csv")}
    if inputs != expected_higgs_hashes(Path(args.frozen_manifest)):
        raise ValueError("Dataset hashes differ from the frozen Higgs manifest")
    with (dataset_dir / "nodes.csv").open("r", encoding="utf-8") as handle:
        node_count = sum(1 for _ in handle) - 1
    seed_budget, worlds, runs = 2, 20, 30
    full_sets = greedy_evaluations(node_count, seed_budget)
    screened_sets = greedy_evaluations(120, seed_budget)
    pool_sets = sum(greedy_evaluations(pool, seed_budget) for pool in (60, 120, 240, 480))
    weight_sets = 9 * screened_sets
    per_run = (full_sets + screened_sets + pool_sets + weight_sets) * worlds
    batch = per_run * runs
    payload = {
        "study_version": "v3-fairness-sensitivity",
        "input_hashes": inputs,
        "node_count": node_count,
        "seed_budget": seed_budget,
        "worlds_per_selection": worlds,
        "planned_runs": runs,
        "candidate_set_evaluations_per_run": {
            "full_candidate": full_sets,
            "screened_120": screened_sets,
            "candidate_pool_sensitivity": pool_sets,
            "objective_weight_sensitivity": weight_sets,
        },
        "diffusion_calls_per_run": per_run,
        "diffusion_calls_full_batch": batch,
        "source": {"v3_full_candidate_cost_preflight.py": digest(Path(__file__))},
    }
    output.mkdir(parents=True, exist_ok=False)
    (output / "cost_preflight.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    (output / "cost_preflight.md").write_text(
        "# v3 Full-Candidate Cost Preflight\n\n"
        f"- Decision-graph nodes: {node_count:,}\n"
        f"- Exact robust-greedy candidate-set evaluations per run: {full_sets:,} full-candidate, {screened_sets:,} screened-120, {pool_sets:,} pool-sensitivity, and {weight_sets:,} weight-sensitivity.\n"
        f"- Deterministic diffusion calls: {per_run:,} per run and {batch:,} for all {runs} runs.\n"
        "- This is an operation-count budget, not a wall-clock estimate. A full batch must not start until the available compute allocation can cover this budget without modifying frozen studies.\n",
        encoding="utf-8",
    )
    print(f"Wrote v3 full-candidate cost preflight to {output}")


if __name__ == "__main__":
    main()
