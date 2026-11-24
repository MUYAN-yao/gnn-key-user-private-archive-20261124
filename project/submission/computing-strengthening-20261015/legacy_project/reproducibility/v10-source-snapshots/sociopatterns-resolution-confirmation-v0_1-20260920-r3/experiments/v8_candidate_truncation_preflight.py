"""Outcome-blind local resource preflight for the evaluation-study pivot.

This is not a method comparison and deliberately writes no selected seed,
objective, rank, or independent-evaluation value.  It only establishes whether
the full-candidate mean-spread reference can complete on two already-local,
development-only inputs under a stated small world budget.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
import time

import networkx as nx
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

from app.validation import load_dataset
from experiments.v7_exact_search import full_greedy


STUDY = "candidate-truncation-evaluation-preflight-v0_1"
DATASETS = {
    "digg_pilot5000": ROOT / "data" / "processed" / "digg" / "pilot-5000",
    "higgs_pilot1500": ROOT / "data" / "processed" / "higgs-twitter" / "pilot-1500",
}
HISTORY_FRACTION = 0.65
HORIZON = 4
PROBABILITY = 0.05
SEED_BUDGET = 5
DEFAULT_SELECTION_WORLDS = 4


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def fixed_worlds(dataset_name: str, count: int) -> tuple[int, ...]:
    if count <= 0:
        raise ValueError("selection world count must be positive")
    worlds: list[int] = []
    for index in range(count):
        payload = f"{STUDY}|{dataset_name}|selection|{index}".encode("utf-8")
        worlds.append(int.from_bytes(hashlib.sha256(payload).digest()[:8], "big") & ((1 << 63) - 1))
    if len(set(worlds)) != len(worlds):
        raise AssertionError("world ID collision")
    return tuple(worlds)


def grouped_history(edges: pd.DataFrame, fraction: float = HISTORY_FRACTION) -> tuple[pd.DataFrame, str, int]:
    """Keep complete timestamp groups in the first fraction of a sorted history."""
    if not 0 < fraction <= 1:
        raise ValueError("fraction must be in (0, 1]")
    ordered = edges.sort_values(["timestamp", "src", "dst"], kind="mergesort").copy()
    groups = list(ordered.timestamp.drop_duplicates())
    if not groups:
        raise ValueError("cannot build a history from an empty edge table")
    keep = max(1, min(len(groups), int(len(groups) * fraction)))
    cutoff = groups[keep - 1]
    history = ordered.loc[ordered.timestamp <= cutoff].copy()
    if history.empty or history.timestamp.max() != cutoff:
        raise AssertionError("timestamp-group history construction failed")
    return history, cutoff.isoformat(), len(groups)


def build_history_graph(history: pd.DataFrame) -> tuple[dict[str, tuple[str, ...]], dict[str, str], dict[tuple[str, str], float], dict]:
    """Construct only the historical endpoint graph required by this preflight."""
    cleaned = history.loc[history.src != history.dst, ["src", "dst"]].copy()
    grouped = cleaned.groupby(["src", "dst"], sort=True).size().rename("events").reset_index()
    nodes = sorted(set(grouped.src.astype(str)) | set(grouped.dst.astype(str)))
    if len(nodes) < SEED_BUDGET:
        raise ValueError("history graph has fewer nodes than the fixed seed budget")
    graph = {node: [] for node in nodes}
    for row in grouped.itertuples(index=False):
        graph[str(row.src)].append(str(row.dst))
    graph = {node: tuple(sorted(targets)) for node, targets in graph.items()}
    undirected = nx.Graph()
    undirected.add_nodes_from(nodes)
    for row in grouped.itertuples(index=False):
        undirected.add_edge(str(row.src), str(row.dst), weight=int(row.events))
    partitions = list(nx.algorithms.community.greedy_modularity_communities(undirected, weight="weight"))
    communities = {str(node): str(index) for index, group in enumerate(partitions) for node in group}
    if set(communities) != set(nodes):
        raise AssertionError("community construction omitted a historical node")
    probabilities = {(source, target): PROBABILITY for source, targets in graph.items() for target in targets}
    metadata = {
        "historical_nodes": len(nodes),
        "historical_edges": int(len(grouped)),
        "self_loops_removed": int((history.src == history.dst).sum()),
        "duplicate_events_collapsed": int(len(cleaned) - len(grouped)),
        "community_count": len(partitions),
    }
    return graph, communities, probabilities, metadata


def run_preflight(dataset_name: str, selection_world_count: int, dry_run: bool) -> dict:
    if dataset_name not in DATASETS:
        raise ValueError(f"unknown dataset: {dataset_name}")
    dataset_dir = DATASETS[dataset_name]
    dataset = load_dataset(dataset_dir)
    history, cutoff, timestamp_group_count = grouped_history(dataset.edges)
    graph, communities, probabilities, metadata = build_history_graph(history)
    worlds = fixed_worlds(dataset_name, selection_world_count)
    inputs = {name: sha256(dataset_dir / name) for name in ("nodes.csv", "edges.csv", "cascades.csv")}
    report = {
        "schema": "candidate-truncation-preflight-0.1",
        "study": STUDY,
        "dataset": dataset_name,
        "development_only": True,
        "outcome_blind": True,
        "status": "DRY_RUN" if dry_run else "COMPLETED_NO_OUTCOME_RECORDED",
        "input_sha256": inputs,
        "history_fraction": HISTORY_FRACTION,
        "history_cutoff": cutoff,
        "timestamp_group_count": timestamp_group_count,
        "selection_world_count": selection_world_count,
        "selection_world_sha256": hashlib.sha256(json.dumps(worlds).encode("utf-8")).hexdigest(),
        "horizon": HORIZON,
        "edge_probability": PROBABILITY,
        "seed_budget": SEED_BUDGET,
        "graph": metadata,
        "warnings": dataset.warnings,
    }
    if dry_run:
        return report
    started = time.perf_counter()
    codes = {node: index for index, node in enumerate(sorted(graph))}
    completed = full_greedy(
        graph,
        probabilities,
        communities,
        worlds,
        horizon=HORIZON,
        seed_count=SEED_BUDGET,
        codes=codes,
        risk_lambda=0,
        community_weight=0,
    )
    report["full_reference"] = {
        "completed": True,
        "candidate_world_evaluations": completed["world_evaluations"],
        "elapsed_seconds": round(time.perf_counter() - started, 6),
        "selection_or_objective_recorded": False,
    }
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", choices=sorted(DATASETS), required=True)
    parser.add_argument("--selection-worlds", type=int, default=DEFAULT_SELECTION_WORLDS)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(f"refusing to overwrite {args.output}")
    report = run_preflight(args.dataset, args.selection_worlds, args.dry_run)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
