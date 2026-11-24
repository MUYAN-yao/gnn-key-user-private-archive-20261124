"""Run the preregistered v5 candidate-reduction validation from a source snapshot.

This runner has no path into v1--v4 result directories.  Formal execution is
accepted only from the source snapshot created by ``create_v5_source_snapshot``.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
from pathlib import Path
import shutil
import sys
import time
from typing import Any

import numpy as np
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT))

from app import pipeline_v2_t0 as t0
from app.contracts import AnalysisConfig
from app.graph import build_snapshot
from app.pipeline_v2_t0b import _windows
from app.validation import load_dataset
from experiments.v5_source_snapshot import MANIFEST_NAME, sha256, verify_snapshot


STUDY = "v5-candidate-reduction"
ARTIFACT_SCHEMA = "v5-candidate-reduction-1"
PROTOCOL_NAME = "influence_v5_candidate_reduction_preregistration.md"
FRACTION = 0.65
FORMAL_SEEDS = tuple(range(63, 73))
PREFLIGHT_SEED = 62
SMOKE_SEED = 61
ARMS = (
    "full_candidate",
    "gnn_pool_30",
    "gnn_pool_60",
    "gnn_pool_120",
    "weighted_out_degree_pool_120",
)
POOL_SIZES = {
    "gnn_pool_30": 30,
    "gnn_pool_60": 60,
    "gnn_pool_120": 120,
    "weighted_out_degree_pool_120": 120,
}
SELECTION_NAMESPACE = 501
PRIMARY_NAMESPACE = 502
STABILITY_NAMESPACE = 503
ARM_ORDER_NAMESPACE = 504
SELECTION_WORLD_COUNT = 20
PRIMARY_WORLD_COUNT = 100
STABILITY_WORLD_COUNT = 100
REPORTING_OBJECTIVE = {"risk_lambda": 0.35, "community_weight": 0.25}
EXPECTED_INPUTS = {
    "higgs": {
        "nodes.csv": "04560116149c19d1bd7f0dcdaad6b70dbbaa32cf1932cab9221c2aeebfac8e57",
        "edges.csv": "5178d5be13faf6b0875b584e936d24d8043112dcc1b25b0b49ea95dc17f5b7f9",
        "cascades.csv": "d503d39922201baa8dd018c187beb7500c5cf5910ce745c948478525f867b552",
    },
    "digg": {
        "nodes.csv": "b1ee9740805a04f594c8e0f1ee102131f7ba1db661fef4992d83a9f80769cb56",
        "edges.csv": "95b4163488e4ae690eba7e42f839db27c0a61cda0d13f6733783694152b16d67",
        "cascades.csv": "18fe5afa3196de05e6757e6c1015d6dcc434f4740d28db51be44021ce778c246",
    },
}
MASK64 = (1 << 64) - 1


def json_default(value: object) -> object:
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, np.floating):
        return float(value)
    if isinstance(value, np.ndarray):
        return value.tolist()
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def stable_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def world_sequence(seed: int, namespace: int, count: int) -> list[int]:
    generator = np.random.default_rng(np.random.SeedSequence([seed, namespace, 3]))
    return [int(value) for value in generator.integers(0, 2**63 - 1, size=count)]


def uniform(world_seed: int, step: int, source: int, target: int) -> float:
    """A process-independent uniform for a canonical edge-time trial."""
    value = (
        (world_seed + 0x9E3779B97F4A7C15)
        ^ ((step + 1) * 0xBF58476D1CE6E5B9)
        ^ ((source + 1) * 0x94D049BB133111EB)
        ^ ((target + 1) * 0xBF58476D1CE6E93)
    ) & MASK64
    value = ((value ^ (value >> 30)) * 0xBF58476D1CE6E5B9) & MASK64
    value = ((value ^ (value >> 27)) * 0x94D049BB133111EB) & MASK64
    value ^= value >> 31
    return (value >> 11) * (1.0 / (1 << 53))


def simulate_ic_common_world(graph, seeds, probabilities, horizon, world, codes) -> int:
    active, frontier = set(seeds), set(seeds)
    for step in range(horizon):
        next_frontier = set()
        for source in sorted(frontier, key=codes.__getitem__):
            for target in sorted(graph.successors(source), key=codes.__getitem__):
                if target in active:
                    continue
                if uniform(world, step, codes[source], codes[target]) < probabilities[(source, target)]:
                    active.add(target)
                    next_frontier.add(target)
        frontier = next_frontier
        if not frontier:
            break
    return len(active)


def sync_cuda() -> None:
    if torch.cuda.is_available():
        torch.cuda.synchronize()


def timed(callable_):
    sync_cuda()
    started = time.perf_counter()
    result = callable_()
    sync_cuda()
    return result, time.perf_counter() - started


def score_with_world_values(graph, probabilities, communities, nodes, config, worlds, codes) -> dict[str, Any]:
    values = [
        simulate_ic_common_world(graph, nodes, probabilities, config.horizon, world, codes)
        for world in worlds
    ]
    mean, std = float(np.mean(values)), float(np.std(values))
    coverage = len({communities[node] for node in nodes})
    return {
        "top_k": list(nodes),
        "mean_spread": round(mean, 6),
        "spread_std": round(std, 6),
        "robust_objective": round(
            mean - REPORTING_OBJECTIVE["risk_lambda"] * std
            + REPORTING_OBJECTIVE["community_weight"] * coverage,
            6,
        ),
        "community_coverage": coverage,
        "world_spreads": values,
    }


def trace_greedy(graph, probabilities, communities, candidates, config, worlds, codes) -> dict[str, Any]:
    """Run exact robust greedy while retaining a compact, auditable trace."""
    ordered = sorted(map(str, candidates))
    if len(ordered) < config.seed_count:
        raise ValueError("Candidate pool is smaller than the fixed seed budget")
    selected: list[str] = []
    rounds: list[dict[str, Any]] = []
    search_started = time.perf_counter()
    for step in range(config.seed_count):
        candidate_scores: list[tuple[int, str, dict[str, Any]]] = []
        for stable_order, node in enumerate(ordered):
            if node in selected:
                continue
            result = score_with_world_values(
                graph, probabilities, communities, selected + [node], config, worlds, codes
            )
            # Only the summary is retained. The deterministic worlds and snapshot
            # make the exact candidate scores independently reconstructible.
            result.pop("world_spreads")
            candidate_scores.append((stable_order, node, result))
        candidate_scores.sort(key=lambda item: (-float(item[2]["robust_objective"]), item[0]))
        _, winner_node, winner = candidate_scores[0]
        runner_up = candidate_scores[1] if len(candidate_scores) > 1 else None
        best_objective = float(winner["robust_objective"])
        rounds.append(
            {
                "round": step + 1,
                "selected_before": list(selected),
                "trial_count": len(candidate_scores),
                "winner": winner_node,
                "winner_summary": winner,
                "runner_up": runner_up[1] if runner_up else None,
                "runner_up_summary": runner_up[2] if runner_up else None,
                "winner_margin": round(
                    best_objective - float(runner_up[2]["robust_objective"]), 6
                ) if runner_up else None,
                "exact_best_tie_count": int(
                    sum(float(result["robust_objective"]) == best_objective for _, _, result in candidate_scores)
                ),
            }
        )
        selected.append(winner_node)
    search_seconds = time.perf_counter() - search_started
    selection, selection_score_seconds = timed(
        lambda: score_with_world_values(
            graph, probabilities, communities, selected, config, worlds, codes
        )
    )
    return {
        "candidate_count": len(ordered),
        "canonical_candidate_order": ordered,
        "rounds": rounds,
        "selection": selection,
        "search_seconds": search_seconds,
        "selection_score_seconds": selection_score_seconds,
    }


def ranked(scores: dict[str, float]) -> list[str]:
    return [str(node) for node in sorted(scores, key=lambda node: (-float(scores[node]), str(node)))]


def arm_execution_order(seed: int) -> tuple[list[str], int]:
    order_seed = world_sequence(seed, ARM_ORDER_NAMESPACE, 1)[0]
    permutation = np.random.default_rng(order_seed).permutation(len(ARMS))
    return [ARMS[int(index)] for index in permutation], order_seed


def input_hashes(dataset_name: str, dataset_dir: Path) -> dict[str, str]:
    observed = {name: sha256(dataset_dir / name) for name in EXPECTED_INPUTS[dataset_name]}
    if observed != EXPECTED_INPUTS[dataset_name]:
        raise ValueError(f"Frozen {dataset_name} input hash mismatch")
    return observed


def _source_snapshot_metadata(snapshot_dir: Path) -> dict[str, Any]:
    manifest = verify_snapshot(snapshot_dir)
    expected_runner = (snapshot_dir / "experiments" / "run_v5_candidate_reduction.py").resolve()
    if Path(__file__).resolve() != expected_runner or ROOT.resolve() != snapshot_dir.resolve():
        raise ValueError("The v5 runner must be executed from the verified source snapshot")
    return {
        "snapshot_dir": str(snapshot_dir.resolve()),
        "snapshot_id": manifest["snapshot_id"],
        "manifest_name": MANIFEST_NAME,
        "manifest_sha256": sha256(snapshot_dir / MANIFEST_NAME),
        "file_count": len(manifest["files"]),
    }


def run_one(dataset_path: Path, dataset_name: str, seed: int, mode: str, smoke_limit: int | None) -> dict[str, Any]:
    block_started = time.perf_counter()
    timings: dict[str, float] = {}
    dataset, timings["load_and_validate_seconds"] = timed(lambda: load_dataset(dataset_path))
    (history, supervised, calibration, outer_test, outer_train), timings["window_partition_seconds"] = timed(
        lambda: _windows(dataset, FRACTION)
    )
    if not (history.timestamp.max() < supervised.timestamp.min() < calibration.timestamp.min() < outer_test.timestamp.min()):
        raise AssertionError("Timestamp windows are not strictly ordered")
    snapshot, timings["decision_graph_seconds"] = timed(lambda: build_snapshot(dataset, outer_train))
    (probabilities, uses_pyg), timings["training_calibration_inference_seconds"] = timed(
        lambda: t0._calibrated_probabilities(dataset, history, supervised, calibration, snapshot, seed)
    )
    if set(probabilities) != set(snapshot.graph.edges()):
        raise AssertionError("Every decision edge must receive one calibrated probability")
    prior, timings["learned_prior_scoring_seconds"] = timed(
        lambda: t0._node_prior(snapshot.graph, probabilities)
    )
    weighted_degree, timings["weighted_degree_scoring_seconds"] = timed(
        lambda: {
            str(node): float(snapshot.graph.out_degree(node, weight="weight"))
            for node in snapshot.graph.nodes
        }
    )
    node_universe = sorted(map(str, snapshot.graph.nodes))
    if len(node_universe) < 120:
        raise ValueError("Decision graph has fewer than the fixed 120 screened candidates")
    gnn_ranking = ranked({str(node): float(value) for node, value in prior.items()})
    degree_ranking = ranked(weighted_degree)
    full_candidates = node_universe if smoke_limit is None else node_universe[:smoke_limit]
    if len(full_candidates) < 120 and mode != "smoke":
        raise AssertionError("Formal/preflight full candidate pool was unexpectedly truncated")
    memberships = {
        "full_candidate": full_candidates,
        "gnn_pool_30": gnn_ranking[:30],
        "gnn_pool_60": gnn_ranking[:60],
        "gnn_pool_120": gnn_ranking[:120],
        "weighted_out_degree_pool_120": degree_ranking[:120],
    }
    if any(len(memberships[name]) != len(set(memberships[name])) for name in ARMS):
        raise AssertionError("Candidate membership contains duplicate nodes")
    selection_worlds = world_sequence(seed, SELECTION_NAMESPACE, SELECTION_WORLD_COUNT)
    primary_worlds = world_sequence(seed, PRIMARY_NAMESPACE, PRIMARY_WORLD_COUNT)
    stability_worlds = world_sequence(seed, STABILITY_NAMESPACE, STABILITY_WORLD_COUNT)
    world_families = (set(selection_worlds), set(primary_worlds), set(stability_worlds))
    if any(world_families[left] & world_families[right] for left in range(3) for right in range(left + 1, 3)):
        raise AssertionError("Selection, primary, and stability worlds must be disjoint")
    codes = {node: index for index, node in enumerate(node_universe)}
    config = AnalysisConfig(
        seed_count=5,
        horizon=4,
        risk_lambda=REPORTING_OBJECTIVE["risk_lambda"],
        community_weight=REPORTING_OBJECTIVE["community_weight"],
        diffusion_model="ic",
        random_seed=seed,
        epochs=10,
        ants=3,
        iterations=2,
        simulations=SELECTION_WORLD_COUNT,
        train_fraction=FRACTION,
        optimizer="robust_greedy",
        candidate_pool_size=120,
    )
    execution_order, order_seed = arm_execution_order(seed)
    arms: dict[str, Any] = {}
    for name in execution_order:
        arm_started = time.perf_counter()
        membership_started = time.perf_counter()
        membership = list(memberships[name])
        membership_seconds = time.perf_counter() - membership_started
        sorting_started = time.perf_counter()
        canonical_membership = sorted(membership)
        sorting_seconds = time.perf_counter() - sorting_started
        traced = trace_greedy(
            snapshot.graph, probabilities, snapshot.communities, membership,
            config, selection_worlds, codes,
        )
        primary, primary_seconds = timed(
            lambda traced=traced: score_with_world_values(
                snapshot.graph, probabilities, snapshot.communities,
                traced["selection"]["top_k"], config, primary_worlds, codes,
            )
        )
        stability, stability_seconds = timed(
            lambda traced=traced: score_with_world_values(
                snapshot.graph, probabilities, snapshot.communities,
                traced["selection"]["top_k"], config, stability_worlds, codes,
            )
        )
        arms[name] = {
            **traced,
            "membership_rank_order": membership,
            "canonical_candidate_order": canonical_membership,
            "membership_generation_seconds": membership_seconds,
            "candidate_sorting_seconds": sorting_seconds,
            "primary_evaluation": primary,
            "primary_evaluation_seconds": primary_seconds,
            "stability_evaluation": stability,
            "stability_evaluation_seconds": stability_seconds,
            "total_arm_seconds": time.perf_counter() - arm_started,
        }
    full_top_k = arms["full_candidate"]["selection"]["top_k"]
    for name, arm in arms.items():
        top_k = arm["selection"]["top_k"]
        shared = len(set(top_k) & set(full_top_k))
        union = len(set(top_k) | set(full_top_k))
        arm["agreement_with_full_candidate"] = {
            "ordered_top_k_match": top_k == full_top_k,
            "top_k_jaccard": round(shared / union if union else 1.0, 6),
            "primary_robust_objective_delta": round(
                float(arm["primary_evaluation"]["robust_objective"])
                - float(arms["full_candidate"]["primary_evaluation"]["robust_objective"]), 6,
            ),
            "stability_robust_objective_delta": round(
                float(arm["stability_evaluation"]["robust_objective"])
                - float(arms["full_candidate"]["stability_evaluation"]["robust_objective"]), 6,
            ),
        }
    probability_rows = [
        [str(source), str(target), round(float(value), 12)]
        for (source, target), value in sorted(probabilities.items(), key=lambda item: (str(item[0][0]), str(item[0][1])))
    ]
    return {
        "study_version": STUDY,
        "artifact_schema": ARTIFACT_SCHEMA,
        "dataset_id": dataset_name,
        "execution_mode": mode,
        "formal_batch": mode == "formal",
        "not_eligible_for_inference": mode != "formal",
        "config": {
            "fraction": FRACTION,
            "seed": seed,
            "seed_count": 5,
            "horizon": 4,
            "selection_world_count": SELECTION_WORLD_COUNT,
            "primary_evaluation_world_count": PRIMARY_WORLD_COUNT,
            "stability_evaluation_world_count": STABILITY_WORLD_COUNT,
            "full_candidate_limit": smoke_limit,
            **REPORTING_OBJECTIVE,
        },
        "limitations": [
            "All arms share one learned probability graph within a paired block.",
            "Calibration negative eligibility uses the fixed dataset-wide observed-edge set.",
            "The protocol is transductive and retrospective, not a strictly online probability pipeline.",
            "Digg is a conditional simulated-selection setting with inferred exposure-proxy flow links.",
            "Formal seeds are paired protocol repetitions, not independent network samples.",
        ],
        "windows": {
            "history_end": history.timestamp.max().isoformat(),
            "supervised_end": supervised.timestamp.max().isoformat(),
            "calibration_end": calibration.timestamp.max().isoformat(),
            "outer_test_start": outer_test.timestamp.min().isoformat(),
            "row_counts": {
                "history": len(history), "supervised": len(supervised),
                "calibration": len(calibration), "outer_test": len(outer_test),
            },
        },
        "reproducibility": {
            "selection_worlds": selection_worlds,
            "selection_worlds_sha256": stable_digest(selection_worlds),
            "selection_namespace": SELECTION_NAMESPACE,
            "primary_evaluation_worlds": primary_worlds,
            "primary_evaluation_worlds_sha256": stable_digest(primary_worlds),
            "primary_evaluation_namespace": PRIMARY_NAMESPACE,
            "stability_evaluation_worlds": stability_worlds,
            "stability_evaluation_worlds_sha256": stable_digest(stability_worlds),
            "stability_evaluation_namespace": STABILITY_NAMESPACE,
            "world_families_disjoint": True,
            "arm_order_namespace": ARM_ORDER_NAMESPACE,
            "arm_order_seed": order_seed,
            "arm_execution_order": execution_order,
            "canonical_node_universe": node_universe,
            "canonical_node_universe_sha256": stable_digest(node_universe),
            "probability_edge_count": len(probability_rows),
            "probabilities_sha256": stable_digest(probability_rows),
            "backend": "torch-geometric GATv2" if uses_pyg else "PyTorch temporal GAT fallback",
        },
        "block_elapsed_seconds": time.perf_counter() - block_started,
        "timings": timings,
        "arms": arms,
    }


def run_id(seed: int) -> str:
    return f"seed-{seed}"


def _validate_existing_artifact(artifact: dict[str, Any], dataset_name: str, seed: int, mode: str, inputs: dict[str, str], source_snapshot: dict[str, Any]) -> None:
    if artifact.get("study_version") != STUDY or artifact.get("artifact_schema") != ARTIFACT_SCHEMA:
        raise ValueError("Existing artifact belongs to another study or schema")
    if artifact.get("dataset_id") != dataset_name or artifact.get("execution_mode") != mode:
        raise ValueError("Existing artifact dataset or mode does not match")
    if artifact.get("formal_batch") is not (mode == "formal") or artifact.get("not_eligible_for_inference") is not (mode != "formal"):
        raise ValueError("Existing artifact eligibility flags do not match")
    config = artifact.get("config", {})
    if config.get("fraction") != FRACTION or config.get("seed") != seed or config.get("seed_count") != 5:
        raise ValueError("Existing artifact configuration does not match")
    provenance = artifact.get("artifact_manifest", {})
    if provenance.get("inputs") != inputs or provenance.get("source_snapshot") != source_snapshot:
        raise ValueError("Existing artifact provenance does not match")
    if artifact.get("integrity", {}).get("status") != "passed":
        raise ValueError("Existing artifact did not pass its integrity status")


def metric_rows(identifier: str, artifact: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for method in ARMS:
        arm = artifact["arms"][method]
        agreement = arm["agreement_with_full_candidate"]
        primary, stability = arm["primary_evaluation"], arm["stability_evaluation"]
        rows.append({
            "dataset_id": artifact["dataset_id"], "run_id": identifier,
            "random_seed": artifact["config"]["seed"], "method": method,
            "candidate_count": arm["candidate_count"],
            "top_k": json.dumps(arm["selection"]["top_k"], ensure_ascii=False),
            "primary_mean_spread": primary["mean_spread"],
            "primary_spread_std": primary["spread_std"],
            "primary_robust_objective": primary["robust_objective"],
            "primary_community_coverage": primary["community_coverage"],
            "stability_mean_spread": stability["mean_spread"],
            "stability_spread_std": stability["spread_std"],
            "stability_robust_objective": stability["robust_objective"],
            "stability_community_coverage": stability["community_coverage"],
            "ordered_top_k_match_with_full": agreement["ordered_top_k_match"],
            "top_k_jaccard_with_full": agreement["top_k_jaccard"],
            "primary_objective_delta_vs_full": agreement["primary_robust_objective_delta"],
            "stability_objective_delta_vs_full": agreement["stability_robust_objective_delta"],
            "membership_generation_seconds": arm["membership_generation_seconds"],
            "candidate_sorting_seconds": arm["candidate_sorting_seconds"],
            "search_seconds": arm["search_seconds"],
            "selection_score_seconds": arm["selection_score_seconds"],
            "primary_evaluation_seconds": arm["primary_evaluation_seconds"],
            "stability_evaluation_seconds": arm["stability_evaluation_seconds"],
            "total_arm_seconds": arm["total_arm_seconds"],
            "formal_batch": artifact["formal_batch"],
            "not_eligible_for_inference": artifact["not_eligible_for_inference"],
        })
    return rows


def environment_metadata() -> dict[str, Any]:
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "torch": torch.__version__,
        "cuda": torch.version.cuda,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset-name", choices=sorted(EXPECTED_INPUTS), required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--source-snapshot", required=True)
    parser.add_argument("--mode", choices=("preflight", "formal", "smoke"), required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--smoke-full-candidate-limit", type=int, default=64)
    args = parser.parse_args()
    output = Path(args.output_dir)
    if "candidate-reduction-v5" not in str(output).lower():
        parser.error("Output directory must identify the separately versioned candidate-reduction-v5 study")
    if args.smoke_full_candidate_limit < 5:
        parser.error("--smoke-full-candidate-limit must be at least the fixed k=5 budget")
    source_snapshot = _source_snapshot_metadata(Path(args.source_snapshot))
    dataset_dir = Path(args.dataset).resolve()
    inputs = input_hashes(args.dataset_name, dataset_dir)
    seed_list = list(FORMAL_SEEDS if args.mode == "formal" else (PREFLIGHT_SEED,) if args.mode == "preflight" else (SMOKE_SEED,))
    smoke_limit = args.smoke_full_candidate_limit if args.mode == "smoke" else None
    if args.dry_run:
        print(json.dumps({
            "status": "dry-run passed", "study_version": STUDY,
            "dataset_id": args.dataset_name, "execution_mode": args.mode,
            "expected_run_ids": [run_id(seed) for seed in seed_list],
            "source_snapshot": source_snapshot, "inputs": inputs,
            "writes_nothing": True,
        }, ensure_ascii=False, indent=2))
        return
    if output.exists() and any(output.iterdir()) and not args.resume:
        parser.error(f"Refusing to overwrite non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    protocol_source = ROOT / "protocols" / PROTOCOL_NAME
    protocol_copy = output / PROTOCOL_NAME
    if not protocol_copy.exists():
        shutil.copy2(protocol_source, protocol_copy)
    rows: list[dict[str, Any]] = []
    run_hashes: dict[str, str] = {}
    stopped_for_time_limit = False
    for seed in seed_list:
        identifier = run_id(seed)
        path = output / f"{identifier}.json"
        if path.exists():
            if not args.resume:
                raise FileExistsError(f"Refusing to replace existing run: {path}")
            artifact = json.loads(path.read_text(encoding="utf-8"))
            _validate_existing_artifact(artifact, args.dataset_name, seed, args.mode, inputs, source_snapshot)
        else:
            artifact = run_one(dataset_dir, args.dataset_name, seed, args.mode, smoke_limit)
            time_limit_exceeded = args.mode == "formal" and artifact["block_elapsed_seconds"] > 18_000
            artifact["integrity"] = {
                "status": "failed_block_time_limit" if time_limit_exceeded else "passed",
                "probability_graph_complete": True,
                "world_families_disjoint": True,
                "formal_block_time_limit_seconds": 18_000,
                "block_time_limit_exceeded": time_limit_exceeded,
            }
            if time_limit_exceeded:
                artifact["not_eligible_for_inference"] = True
            artifact["artifact_manifest"] = {
                "inputs": inputs,
                "source_snapshot": source_snapshot,
                "environment": environment_metadata(),
            }
            path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2, default=json_default) + "\n", encoding="utf-8")
            print(identifier, flush=True)
        rows.extend(metric_rows(identifier, artifact))
        run_hashes[path.name] = sha256(path)
        if artifact.get("integrity", {}).get("block_time_limit_exceeded") is True:
            stopped_for_time_limit = True
            break
    with (output / "method_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "study_version": STUDY,
        "artifact_schema": ARTIFACT_SCHEMA,
        "dataset_id": args.dataset_name,
        "dataset_path": str(dataset_dir),
        "execution_mode": args.mode,
        "formal_batch": args.mode == "formal" and not stopped_for_time_limit and len(run_hashes) == len(seed_list),
        "not_eligible_for_inference": args.mode != "formal" or stopped_for_time_limit or len(run_hashes) != len(seed_list),
        "protocol": {PROTOCOL_NAME: sha256(protocol_source)},
        "inputs": inputs,
        "source_snapshot": source_snapshot,
        "run_parameters": {
            "fraction": FRACTION, "seeds": seed_list, "seed_count": 5,
            "horizon": 4, "selection_world_count": SELECTION_WORLD_COUNT,
            "primary_evaluation_world_count": PRIMARY_WORLD_COUNT,
            "stability_evaluation_world_count": STABILITY_WORLD_COUNT,
            "arms": list(ARMS), "smoke_full_candidate_limit": smoke_limit,
            **REPORTING_OBJECTIVE,
        },
        "expected_run_ids": [run_id(seed) for seed in seed_list],
        "runs": run_hashes,
        "environment": environment_metadata(),
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(output)
    if stopped_for_time_limit:
        raise RuntimeError("Formal block exceeded 18,000 seconds; batch stopped and marked ineligible")


if __name__ == "__main__":
    main()
