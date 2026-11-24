"""Outcome-blind resource preflight for the CC0 SocioPatterns confirmation set."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

from app.validation import load_dataset
from experiments.v7_exact_search import full_greedy
from experiments.v8_candidate_truncation_preflight import build_history_graph, grouped_history, sha256


STUDY = "sociopatterns-resolution-confirmation-preflight-v0_1"
DATA_ROOT = ROOT / "data" / "processed" / "sociopatterns-confirmation-v0_1"
DATASETS = ("invs2013", "invs2015", "sfhh2009", "kenya2012")


def worlds(dataset: str, count: int) -> tuple[int, ...]:
    return tuple(int.from_bytes(hashlib.sha256(f"{STUDY}|{dataset}|{index}".encode()).digest()[:8], "big") & ((1 << 63) - 1) for index in range(count))


def run_preflight(dataset_id: str, world_count: int = 4) -> dict:
    if dataset_id not in DATASETS or world_count <= 0:
        raise ValueError("invalid data set or world count")
    dataset_dir = DATA_ROOT / dataset_id
    dataset = load_dataset(dataset_dir)
    history, cutoff, groups = grouped_history(dataset.edges)
    graph, communities, probabilities, metadata = build_history_graph(history)
    started = time.perf_counter()
    result = full_greedy(graph, probabilities, communities, worlds(dataset_id, world_count), horizon=4, seed_count=5, codes={node: index for index, node in enumerate(sorted(graph))}, risk_lambda=0, community_weight=0)
    return {
        "schema": "sociopatterns-confirmation-preflight-0.1",
        "study": STUDY,
        "dataset": dataset_id,
        "outcome_blind": True,
        "status": "COMPLETED_NO_SELECTION_RECORDED",
        "input_sha256": {name: sha256(dataset_dir / name) for name in ("nodes.csv", "edges.csv", "cascades.csv", "data_card.json")},
        "history_cutoff": cutoff,
        "timestamp_group_count": groups,
        "graph": metadata,
        "selection_world_count": world_count,
        "selection_world_sha256": hashlib.sha256(json.dumps(worlds(dataset_id, world_count)).encode()).hexdigest(),
        "full_candidate_world_evaluations": result["world_evaluations"],
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "warnings": dataset.warnings,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=DATASETS, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")
    report = run_preflight(args.dataset)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"dataset": args.dataset, "elapsed_seconds": report["elapsed_seconds"]}))


if __name__ == "__main__":
    main()
