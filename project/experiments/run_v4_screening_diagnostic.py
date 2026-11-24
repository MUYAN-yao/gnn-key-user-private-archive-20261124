"""Run one versioned screening-mechanism diagnostic with exhaustive traces."""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
from pathlib import Path
import sys
import time

import networkx as nx
import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT))

from app import pipeline_v2_t0 as t0
from app.contracts import AnalysisConfig
from app.graph import build_snapshot
from app.pipeline_v2_t0b import _windows
from app.validation import load_dataset
from experiments.run_rolling_study_v2_t0 import expected_higgs_hashes, sha256
from experiments.run_v3_fairness_sensitivity import (
    REPORTING_OBJECTIVE, simulate_ic_common_world, stable_digest, world_sequence,
)

STUDY = "v4-screening-diagnostic"
POOL_SIZE = 120
RANDOM_NAMESPACE = 303


def json_default(value):
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def sync_cuda() -> None:
    if torch.cuda.is_available():
        torch.cuda.synchronize()


def timed(callable_):
    sync_cuda()
    started = time.perf_counter()
    result = callable_()
    sync_cuda()
    return result, time.perf_counter() - started


def ranked(scores: dict[str, float]) -> list[str]:
    return sorted(scores, key=lambda node: (-float(scores[node]), str(node)))


def score_with_world_values(graph, probabilities, communities, nodes, config, worlds, codes):
    values = [simulate_ic_common_world(graph, nodes, probabilities, config.horizon, world, codes)
              for world in worlds]
    mean, std = float(np.mean(values)), float(np.std(values))
    coverage = len({communities[node] for node in nodes})
    return {"top_k": list(nodes), "mean_spread": round(mean, 6),
            "spread_std": round(std, 6),
            "robust_objective": round(mean - REPORTING_OBJECTIVE["risk_lambda"] * std
                                      + REPORTING_OBJECTIVE["community_weight"] * coverage, 6),
            "community_coverage": coverage, "world_spreads": values}


def trace_greedy(graph, probabilities, communities, candidates, config, worlds, codes):
    ordered = sorted(map(str, candidates))
    selected: list[str] = []
    rounds = []
    started = time.perf_counter()
    for step in range(config.seed_count):
        candidate_scores = []
        for order, node in enumerate(ordered):
            if node in selected:
                continue
            result = score_with_world_values(graph, probabilities, communities,
                                             selected + [node], config, worlds, codes)
            candidate_scores.append({"stable_order": order, "candidate": node, **result})
        candidate_scores.sort(key=lambda item: (-float(item["robust_objective"]), item["stable_order"]))
        winner = candidate_scores[0]
        best_value = float(winner["robust_objective"])
        tie_count = sum(np.isclose(float(item["robust_objective"]), best_value, rtol=0, atol=0)
                        for item in candidate_scores)
        runner_up = candidate_scores[1] if len(candidate_scores) > 1 else None
        rounds.append({
            "round": step + 1, "selected_before": list(selected),
            "winner": winner["candidate"],
            "runner_up": runner_up["candidate"] if runner_up else None,
            "winner_objective": best_value,
            "runner_up_objective": float(runner_up["robust_objective"]) if runner_up else None,
            "winner_margin": best_value - float(runner_up["robust_objective"]) if runner_up else None,
            "exact_best_tie_count": tie_count, "candidate_scores": candidate_scores,
        })
        selected.append(winner["candidate"])
    selected_score = score_with_world_values(graph, probabilities, communities,
                                             selected, config, worlds, codes)
    return {"candidate_count": len(ordered), "canonical_candidate_order": ordered,
            "rounds": rounds, "selection": selected_score,
            "search_and_final_score_seconds": time.perf_counter() - started}


def run(args):
    timings = {}
    dataset, timings["load_and_validate_seconds"] = timed(lambda: load_dataset(args.dataset))
    history, supervised, calibration, outer_test, outer_train = _windows(dataset, args.fraction)
    if not history.timestamp.max() < supervised.timestamp.min() < calibration.timestamp.min() < outer_test.timestamp.min():
        raise AssertionError("Timestamp windows overlap")
    snapshot, timings["decision_graph_seconds"] = timed(lambda: build_snapshot(dataset, outer_train))
    probabilities, timings["training_calibration_inference_seconds"] = timed(
        lambda: t0._calibrated_probabilities(dataset, history, supervised, calibration, snapshot, args.seed))
    probabilities, uses_pyg = probabilities
    if set(probabilities) != set(snapshot.graph.edges()):
        raise AssertionError("Probability graph is incomplete")
    prior, timings["learned_prior_seconds"] = timed(lambda: t0._node_prior(snapshot.graph, probabilities))
    weighted_degree = {str(n): float(snapshot.graph.out_degree(n, weight="weight")) for n in snapshot.graph.nodes}
    pagerank, timings["pagerank_seconds"] = timed(lambda: nx.pagerank(snapshot.graph, weight="weight"))
    ranks = {"gnn_prior": ranked(prior), "weighted_out_degree": ranked(weighted_degree),
             "pagerank": ranked(pagerank)}
    random_world = world_sequence(args.seed, RANDOM_NAMESPACE, 1)[0]
    random_candidates = np.random.default_rng(random_world).choice(
        np.array(sorted(map(str, snapshot.graph.nodes)), dtype=object), size=POOL_SIZE, replace=False).tolist()
    memberships = {name: values[:POOL_SIZE] for name, values in ranks.items()}
    memberships["uniform_random"] = random_candidates
    selection_worlds = world_sequence(args.seed, 101, 20)
    evaluation_worlds = world_sequence(args.seed, 202, 20)
    if set(selection_worlds) & set(evaluation_worlds):
        raise AssertionError("Selection and evaluation worlds overlap")
    codes = {node: i for i, node in enumerate(sorted(snapshot.graph.nodes, key=str))}
    config = AnalysisConfig(seed_count=2, horizon=4, risk_lambda=.35, community_weight=.25,
                            diffusion_model="ic", random_seed=args.seed, epochs=10, ants=3,
                            iterations=2, simulations=20, train_fraction=args.fraction,
                            optimizer="robust_greedy", candidate_pool_size=POOL_SIZE)
    arms = {}
    for name, members in memberships.items():
        traced = trace_greedy(snapshot.graph, probabilities, snapshot.communities,
                              members, config, selection_worlds, codes)
        chosen = traced["selection"]["top_k"]
        traced["reporting_evaluation"] = score_with_world_values(
            snapshot.graph, probabilities, snapshot.communities, chosen, config,
            evaluation_worlds, codes)
        traced["membership_rank_order"] = members
        arms[name] = traced
    return {
        "study_version": STUDY, "diagnostic_only_not_for_inference": True,
        "config": {"fraction": args.fraction, "seed": args.seed, "pool_size": POOL_SIZE,
                   "seed_count": 2, "horizon": 4, "selection_world_count": 20,
                   "evaluation_world_count": 20, **REPORTING_OBJECTIVE},
        "limitations": [
            "single post-hoc diagnostic run",
            "shared learned probability graph means this isolates candidate membership, not removal of GNN",
            "calibration negative eligibility uses the fixed dataset-wide observed-edge set",
            "fixed transductive node universe",
        ],
        "windows": {"history_end": history.timestamp.max().isoformat(),
                    "supervised_end": supervised.timestamp.max().isoformat(),
                    "calibration_end": calibration.timestamp.max().isoformat(),
                    "outer_test_start": outer_test.timestamp.min().isoformat(),
                    "row_counts": {"history": len(history), "supervised": len(supervised),
                                   "calibration": len(calibration), "outer_test": len(outer_test)}},
        "reproducibility": {"selection_worlds": selection_worlds,
                            "selection_worlds_sha256": stable_digest(selection_worlds),
                            "evaluation_worlds": evaluation_worlds,
                            "evaluation_worlds_sha256": stable_digest(evaluation_worlds),
                            "random_membership_namespace": RANDOM_NAMESPACE,
                            "random_membership_seed": random_world,
                            "backend": "torch-geometric GATv2" if uses_pyg else "PyTorch temporal GAT fallback"},
        "timings": timings, "arms": arms,
        "tables": {"probabilities": [{"source": s, "target": d, "probability": p}
                                      for (s, d), p in probabilities.items()],
                   "node_scores": [{"node": str(n), "community": int(snapshot.communities[n]),
                                    "gnn_prior": float(prior[n]),
                                    "weighted_out_degree": weighted_degree[n],
                                    "pagerank": float(pagerank[n])} for n in sorted(snapshot.graph.nodes, key=str)]},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--fraction", type=float, default=.70)
    parser.add_argument("--seed", type=int, default=48)
    parser.add_argument("--frozen-manifest", default="reproducibility/frozen-study-manifest-v1.json")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    output = Path(args.output_dir)
    if STUDY not in output.name.lower():
        parser.error(f"Output directory name must contain {STUDY}")
    inputs = {name: sha256(Path(args.dataset) / name) for name in ("nodes.csv", "edges.csv", "cascades.csv")}
    if inputs != expected_higgs_hashes(Path(args.frozen_manifest)):
        raise ValueError("Frozen Higgs input hash mismatch")
    protocol = ROOT / "protocols/influence_v4_screening_diagnostic.md"
    sources = {path.name: sha256(path) for path in (
        Path(__file__), protocol, ROOT/"experiments/run_v3_fairness_sensitivity.py",
        ROOT/"backend/app/pipeline_v2_t0.py", ROOT/"backend/app/pipeline_v2_t0b.py",
        ROOT/"backend/app/model_v2.py", ROOT/"backend/app/graph.py", ROOT/"backend/app/validation.py")}
    if args.dry_run:
        dataset = load_dataset(args.dataset)
        windows = _windows(dataset, args.fraction)
        assert windows[0].timestamp.max() < windows[1].timestamp.min() < windows[2].timestamp.min() < windows[3].timestamp.min()
        print(json.dumps({"status":"dry-run passed", "inputs":inputs, "sources":sources}, indent=2))
        return
    if output.exists() and any(output.iterdir()):
        parser.error(f"Refusing to overwrite non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    artifact = run(args)
    artifact["manifest"] = {"inputs": inputs, "sources": sources,
                            "environment": {"python":sys.version,"platform":platform.platform(),
                                            "numpy":np.__version__,"torch":torch.__version__,
                                            "cuda":torch.version.cuda}}
    path = output / f"diagnostic-fraction-{args.fraction:.2f}-seed-{args.seed}.json"
    path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2, default=json_default), encoding="utf-8")
    (output/"manifest.json").write_text(json.dumps({"study_version":STUDY,"diagnostic_only":True,
        "artifact":{path.name:sha256(path)},"inputs":inputs,"sources":sources},ensure_ascii=False,indent=2),encoding="utf-8")
    print(path)


if __name__ == "__main__":
    main()
