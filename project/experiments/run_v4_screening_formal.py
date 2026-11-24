"""Run the preregistered v4 GNN-versus-screening formal comparison.

The runner is deliberately separate from the diagnostic and all archived
study runners.  It writes one trace-rich JSON artifact per paired block and a
flat evaluation table for the later strict statistical analysis.
"""
from __future__ import annotations

import argparse
import csv
import json
import platform
from pathlib import Path
import shutil
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
    REPORTING_OBJECTIVE,
    simulate_ic_common_world,
    stable_digest,
    world_sequence,
)


STUDY = "v4-screening-formal"
ARTIFACT_SCHEMA = "v4-screening-formal-1"
PROTOCOL_NAME = "influence_v4_screening_formal_preregistration.md"
FRACTIONS = (0.60, 0.65, 0.70)
SEEDS = tuple(range(52, 62))
ARMS = ("gnn_prior", "weighted_out_degree", "pagerank", "uniform_random")
POOL_SIZE = 120
SMOKE_POOL_SIZE = 16
SELECTION_NAMESPACE = 101
EVALUATION_NAMESPACE = 202
RANDOM_MEMBERSHIP_NAMESPACE = 303
ARM_ORDER_NAMESPACE = 404


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
            mean
            - REPORTING_OBJECTIVE["risk_lambda"] * std
            + REPORTING_OBJECTIVE["community_weight"] * coverage,
            6,
        ),
        "community_coverage": coverage,
        "world_spreads": values,
    }


def trace_greedy_formal(graph, probabilities, communities, candidates, config, worlds, codes):
    """Trace robust greedy with explicit search and final-score timings."""
    ordered = sorted(map(str, candidates))
    selected: list[str] = []
    rounds = []
    search_started = time.perf_counter()
    for step in range(config.seed_count):
        candidate_scores = []
        for order, node in enumerate(ordered):
            if node in selected:
                continue
            result = score_with_world_values(
                graph,
                probabilities,
                communities,
                selected + [node],
                config,
                worlds,
                codes,
            )
            candidate_scores.append(
                {"stable_order": order, "candidate": node, **result}
            )
        # Objectives are already rounded to six decimals by the score helper.
        candidate_scores.sort(
            key=lambda item: (-float(item["robust_objective"]), item["stable_order"])
        )
        winner = candidate_scores[0]
        best_value = float(winner["robust_objective"])
        tie_count = int(
            sum(
                np.isclose(float(item["robust_objective"]), best_value, rtol=0, atol=0)
                for item in candidate_scores
            )
        )
        runner_up = candidate_scores[1] if len(candidate_scores) > 1 else None
        rounds.append(
            {
                "round": step + 1,
                "selected_before": list(selected),
                "winner": winner["candidate"],
                "runner_up": runner_up["candidate"] if runner_up else None,
                "winner_objective": best_value,
                "runner_up_objective": float(runner_up["robust_objective"])
                if runner_up
                else None,
                "winner_margin": best_value - float(runner_up["robust_objective"])
                if runner_up
                else None,
                "exact_best_tie_count": tie_count,
                "candidate_scores": candidate_scores,
            }
        )
        selected.append(winner["candidate"])
    search_seconds = time.perf_counter() - search_started
    selection_score, selection_score_seconds = timed(
        lambda: score_with_world_values(
            graph, probabilities, communities, selected, config, worlds, codes
        )
    )
    return {
        "candidate_count": len(ordered),
        "canonical_candidate_order": ordered,
        "rounds": rounds,
        "selection": selection_score,
        "search_seconds": search_seconds,
        "selection_score_seconds": selection_score_seconds,
    }


def arm_execution_order(seed: int) -> tuple[list[str], int]:
    order_seed = int(world_sequence(seed, ARM_ORDER_NAMESPACE, 1)[0])
    rng = np.random.default_rng(order_seed)
    permutation = [int(value) for value in rng.permutation(len(ARMS))]
    return [ARMS[index] for index in permutation], order_seed


def run_one(dataset_path: str | Path, fraction: float, seed: int, pool_size: int, smoke: bool = False) -> dict:
    timings = {}
    dataset, timings["load_and_validate_seconds"] = timed(lambda: load_dataset(dataset_path))
    (history, supervised, calibration, outer_test, outer_train), timings["window_partition_seconds"] = timed(
        lambda: _windows(dataset, fraction)
    )
    if not (
        history.timestamp.max()
        < supervised.timestamp.min()
        < calibration.timestamp.min()
        < outer_test.timestamp.min()
    ):
        raise AssertionError("Timestamp windows are not strictly ordered")
    snapshot, timings["decision_graph_seconds"] = timed(
        lambda: build_snapshot(dataset, outer_train)
    )
    probabilities, timings["training_calibration_inference_seconds"] = timed(
        lambda: t0._calibrated_probabilities(
            dataset, history, supervised, calibration, snapshot, seed
        )
    )
    probabilities, uses_pyg = probabilities
    if set(probabilities) != set(snapshot.graph.edges()):
        raise AssertionError("Probability graph is incomplete")

    node_scores_started = time.perf_counter()
    prior = t0._node_prior(snapshot.graph, probabilities)
    weighted_degree = {
        str(node): float(snapshot.graph.out_degree(node, weight="weight"))
        for node in snapshot.graph.nodes
    }
    pagerank = nx.pagerank(snapshot.graph, weight="weight")
    timings["node_score_generation_seconds"] = time.perf_counter() - node_scores_started
    rank_maps = {
        "gnn_prior": ranked(prior),
        "weighted_out_degree": ranked(weighted_degree),
        "pagerank": ranked(pagerank),
    }
    random_world = int(world_sequence(seed, RANDOM_MEMBERSHIP_NAMESPACE, 1)[0])
    canonical_node_universe = sorted(map(str, snapshot.graph.nodes))
    node_universe = np.array(canonical_node_universe, dtype=object)
    node_universe_sha256 = stable_digest(canonical_node_universe)
    selection_worlds = world_sequence(seed, SELECTION_NAMESPACE, 20)
    evaluation_worlds = world_sequence(seed, EVALUATION_NAMESPACE, 20)
    if set(selection_worlds) & set(evaluation_worlds):
        raise AssertionError("Selection and evaluation worlds overlap")
    codes = {node: index for index, node in enumerate(sorted(snapshot.graph.nodes, key=str))}
    config = AnalysisConfig(
        seed_count=2,
        horizon=4,
        risk_lambda=0.35,
        community_weight=0.25,
        diffusion_model="ic",
        random_seed=seed,
        epochs=10,
        ants=3,
        iterations=2,
        simulations=20,
        train_fraction=fraction,
        optimizer="robust_greedy",
        candidate_pool_size=pool_size,
    )

    memberships = {}
    membership_timing = {}
    sorting_timing = {}
    for name in ARMS:
        started = time.perf_counter()
        if name == "uniform_random":
            members = np.random.default_rng(random_world).choice(
                node_universe, size=pool_size, replace=False
            ).tolist()
        else:
            members = rank_maps[name][:pool_size]
        membership_timing[name] = time.perf_counter() - started
        started = time.perf_counter()
        canonical = sorted(map(str, members))
        sorting_timing[name] = time.perf_counter() - started
        memberships[name] = {
            "membership_rank_order": list(map(str, members)),
            "canonical_candidate_order": canonical,
        }

    execution_order, arm_order_seed = arm_execution_order(seed)
    arms = {}
    for name in execution_order:
        started = time.perf_counter()
        traced = trace_greedy_formal(
            snapshot.graph,
            probabilities,
            snapshot.communities,
            memberships[name]["membership_rank_order"],
            config,
            selection_worlds,
            codes,
        )
        evaluation, evaluation_seconds = timed(
            lambda traced=traced: score_with_world_values(
                snapshot.graph,
                probabilities,
                snapshot.communities,
                traced["selection"]["top_k"],
                config,
                evaluation_worlds,
                codes,
            )
        )
        arms[name] = {
            **traced,
            **memberships[name],
            "membership_generation_seconds": membership_timing[name],
            "candidate_sorting_seconds": sorting_timing[name],
            "reporting_evaluation": evaluation,
            "evaluation_seconds": evaluation_seconds,
            "total_arm_seconds": time.perf_counter() - started,
        }

    return {
        "study_version": STUDY,
        "artifact_schema": ARTIFACT_SCHEMA,
        "formal_batch": not smoke,
        "not_eligible_for_inference": bool(smoke),
        "config": {
            "fraction": fraction,
            "seed": seed,
            "pool_size": pool_size,
            "seed_count": 2,
            "horizon": 4,
            "selection_world_count": 20,
            "evaluation_world_count": 20,
            **REPORTING_OBJECTIVE,
        },
        "limitations": [
            "all four arms share one learned probability graph within a block",
            "calibration negative eligibility uses the fixed dataset-wide observed-edge set",
            "fixed transductive node universe",
            "formal seeds are paired protocol repetitions, not independent network samples",
        ],
        "windows": {
            "history_end": history.timestamp.max().isoformat(),
            "supervised_end": supervised.timestamp.max().isoformat(),
            "calibration_end": calibration.timestamp.max().isoformat(),
            "outer_test_start": outer_test.timestamp.min().isoformat(),
            "row_counts": {
                "history": len(history),
                "supervised": len(supervised),
                "calibration": len(calibration),
                "outer_test": len(outer_test),
            },
        },
        "reproducibility": {
            "selection_worlds": selection_worlds,
            "selection_worlds_sha256": stable_digest(selection_worlds),
            "selection_namespace": SELECTION_NAMESPACE,
            "evaluation_worlds": evaluation_worlds,
            "evaluation_worlds_sha256": stable_digest(evaluation_worlds),
            "evaluation_namespace": EVALUATION_NAMESPACE,
            "selection_evaluation_worlds_disjoint": True,
            "random_membership_namespace": RANDOM_MEMBERSHIP_NAMESPACE,
            "random_membership_seed": random_world,
            "arm_order_namespace": ARM_ORDER_NAMESPACE,
            "arm_order_seed": arm_order_seed,
            "arm_execution_order": execution_order,
            "canonical_node_universe_sha256": node_universe_sha256,
            "canonical_node_universe_digest_algorithm": "sha256(canonical JSON list)",
            "node_universe_count": len(canonical_node_universe),
            "node_universe_sort": "ascending string representation",
            "node_universe_first": canonical_node_universe[0] if canonical_node_universe else None,
            "node_universe_last": canonical_node_universe[-1] if canonical_node_universe else None,
            "backend": "torch-geometric GATv2" if uses_pyg else "PyTorch temporal GAT fallback",
        },
        "timings": timings,
        "arms": arms,
        "tables": {
            "probabilities": [
                {"source": source, "target": target, "probability": probability}
                for (source, target), probability in probabilities.items()
            ],
            "node_scores": [
                {
                    "node": str(node),
                    "community": int(snapshot.communities[node]),
                    "gnn_prior": float(prior[node]),
                    "weighted_out_degree": weighted_degree[str(node)],
                    "pagerank": float(pagerank[node]),
                }
                for node in sorted(snapshot.graph.nodes, key=str)
            ],
        },
    }


def run_id(fraction: float, seed: int) -> str:
    return f"split-{fraction:.2f}-seed-{seed}"


def validate_existing_artifact(
    artifact: dict,
    fraction: float,
    seed: int,
    pool_size: int,
    smoke: bool,
    expected_inputs: dict[str, str] | None = None,
    expected_sources: dict[str, str] | None = None,
) -> None:
    """Reject foreign, stale, or smoke artifacts during resume."""
    expected_formal = not smoke
    if artifact.get("study_version") != STUDY:
        raise ValueError("Existing artifact has a different study_version")
    if artifact.get("artifact_schema") != ARTIFACT_SCHEMA:
        raise ValueError("Existing artifact has an unsupported artifact schema")
    if artifact.get("formal_batch") is not expected_formal:
        raise ValueError("Existing artifact formal_batch flag does not match this run")
    if artifact.get("not_eligible_for_inference") is not smoke:
        raise ValueError("Existing artifact eligibility flag does not match this run")
    metadata = artifact.get("artifact_manifest")
    if not isinstance(metadata, dict):
        raise ValueError("Existing artifact is missing artifact_manifest")
    if expected_inputs is not None and metadata.get("inputs") != expected_inputs:
        raise ValueError("Existing artifact input hashes do not match this run")
    if expected_sources is not None and metadata.get("sources") != expected_sources:
        raise ValueError("Existing artifact source hashes do not match this run")
    config = artifact.get("config")
    if not isinstance(config, dict):
        raise ValueError("Existing artifact is missing config")
    if float(config.get("fraction", -1)) != float(fraction):
        raise ValueError("Existing artifact fraction does not match its run id")
    if int(config.get("seed", -1)) != int(seed):
        raise ValueError("Existing artifact seed does not match its run id")
    if int(config.get("pool_size", -1)) != int(pool_size):
        raise ValueError("Existing artifact pool_size does not match this run")
    arms = artifact.get("arms")
    if not isinstance(arms, dict) or set(arms) != set(ARMS):
        raise ValueError("Existing artifact arms do not match the formal protocol")
    for name in ARMS:
        arm = arms[name]
        if int(arm.get("candidate_count", -1)) != pool_size:
            raise ValueError(f"Existing artifact {name} candidate_count mismatch")
        if len(arm.get("membership_rank_order", [])) != pool_size:
            raise ValueError(f"Existing artifact {name} membership order mismatch")
        if len(arm.get("canonical_candidate_order", [])) != pool_size:
            raise ValueError(f"Existing artifact {name} canonical order mismatch")


def validate_existing_manifest(
    manifest: dict,
    inputs: dict[str, str],
    sources: dict[str, str],
    protocol_hash: str,
    pool_size: int,
    smoke: bool,
) -> None:
    """Reject a resume directory whose batch manifest belongs to another version."""
    if manifest.get("study_version") != STUDY:
        raise ValueError("Existing manifest has a different study_version")
    if manifest.get("artifact_schema") != ARTIFACT_SCHEMA:
        raise ValueError("Existing manifest has an unsupported artifact schema")
    if manifest.get("formal_batch") != (not smoke):
        raise ValueError("Existing manifest formal_batch flag does not match this run")
    if manifest.get("not_eligible_for_inference") != bool(smoke):
        raise ValueError("Existing manifest eligibility flag does not match this run")
    if manifest.get("inputs") != inputs:
        raise ValueError("Existing manifest input hashes do not match this run")
    if manifest.get("source") != sources:
        raise ValueError("Existing manifest source hashes do not match this run")
    if manifest.get("protocol") != {PROTOCOL_NAME: protocol_hash}:
        raise ValueError("Existing manifest protocol hash does not match this run")
    parameters = manifest.get("run_parameters")
    if not isinstance(parameters, dict) or int(parameters.get("pool_size", -1)) != pool_size:
        raise ValueError("Existing manifest pool_size does not match this run")


def metric_rows(identifier: str, artifact: dict) -> list[dict]:
    rows = []
    for method in ARMS:
        arm = artifact["arms"][method]
        selection = arm["selection"]
        evaluation = arm["reporting_evaluation"]
        rows.append(
            {
                "run_id": identifier,
                "train_fraction": artifact["config"]["fraction"],
                "random_seed": artifact["config"]["seed"],
                "method": method,
                "mean_spread": evaluation["mean_spread"],
                "spread_std": evaluation["spread_std"],
                "robust_objective": evaluation["robust_objective"],
                "community_coverage": evaluation["community_coverage"],
                "top_k": json.dumps(evaluation["top_k"], ensure_ascii=False),
                "selection_mean_spread": selection["mean_spread"],
                "selection_spread_std": selection["spread_std"],
                "selection_robust_objective": selection["robust_objective"],
                "selection_community_coverage": selection["community_coverage"],
                "candidate_count": arm["candidate_count"],
                "membership_generation_seconds": arm["membership_generation_seconds"],
                "candidate_sorting_seconds": arm["candidate_sorting_seconds"],
                "search_seconds": arm["search_seconds"],
                "selection_score_seconds": arm["selection_score_seconds"],
                "evaluation_seconds": arm["evaluation_seconds"],
                "total_arm_seconds": arm["total_arm_seconds"],
                "not_eligible_for_inference": artifact["not_eligible_for_inference"],
            }
        )
    return rows


def source_hashes() -> dict[str, str]:
    paths = {
        "run_v4_screening_formal.py": Path(__file__),
        PROTOCOL_NAME: ROOT / "protocols" / PROTOCOL_NAME,
        "run_rolling_study_v2_t0.py": ROOT / "experiments" / "run_rolling_study_v2_t0.py",
        "run_v4_screening_diagnostic.py": ROOT / "experiments" / "run_v4_screening_diagnostic.py",
        "run_v3_fairness_sensitivity.py": ROOT / "experiments" / "run_v3_fairness_sensitivity.py",
        "pipeline_v2_t0.py": ROOT / "backend" / "app" / "pipeline_v2_t0.py",
        "pipeline_v2_t0b.py": ROOT / "backend" / "app" / "pipeline_v2_t0b.py",
        "model_v2.py": ROOT / "backend" / "app" / "model_v2.py",
        "graph.py": ROOT / "backend" / "app" / "graph.py",
        "validation.py": ROOT / "backend" / "app" / "validation.py",
    }
    return {name: sha256(path) for name, path in paths.items()}


def environment_metadata() -> dict[str, object]:
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "torch": torch.__version__,
        "cuda": torch.version.cuda,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--fractions", type=float, nargs="+", default=list(FRACTIONS))
    parser.add_argument("--seeds", type=int, nargs="+", default=list(SEEDS))
    parser.add_argument("--frozen-manifest", default="reproducibility/frozen-study-manifest-v1.json")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()
    output = Path(args.output_dir)
    if STUDY not in output.name.lower():
        parser.error(f"Output directory name must contain {STUDY}")
    if not args.smoke and (
        tuple(args.fractions) != FRACTIONS or tuple(args.seeds) != SEEDS
    ):
        parser.error("Formal mode requires exactly fractions 0.60/0.65/0.70 and seeds 52--61")
    dataset_dir = Path(args.dataset)
    inputs = {
        name: sha256(dataset_dir / name)
        for name in ("nodes.csv", "edges.csv", "cascades.csv")
    }
    frozen_inputs = expected_higgs_hashes(Path(args.frozen_manifest))
    if inputs != frozen_inputs:
        raise ValueError("Frozen Higgs input hash mismatch")
    sources = source_hashes()
    environment = environment_metadata()
    protocol = ROOT / "protocols" / PROTOCOL_NAME
    if args.dry_run:
        expected = [run_id(fraction, seed) for fraction in args.fractions for seed in args.seeds]
        print(
            json.dumps(
                {
                    "status": "dry-run passed",
                    "study_version": STUDY,
                    "formal_batch": not args.smoke,
                    "expected_run_count": len(expected),
                    "expected_run_ids": expected,
                    "pool_size": SMOKE_POOL_SIZE if args.smoke else POOL_SIZE,
                    "inputs": inputs,
                    "sources": sources,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    if output.exists() and any(output.iterdir()) and not args.resume:
        parser.error(f"Refusing to overwrite non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    protocol_copy = output / PROTOCOL_NAME
    if not protocol_copy.exists():
        shutil.copy2(protocol, protocol_copy)
    fractions = [args.fractions[0]] if args.smoke else list(FRACTIONS)
    seeds = [args.seeds[0]] if args.smoke else list(SEEDS)
    pool_size = SMOKE_POOL_SIZE if args.smoke else POOL_SIZE
    manifest_path = output / "manifest.json"
    if args.resume and manifest_path.exists():
        validate_existing_manifest(
            json.loads(manifest_path.read_text(encoding="utf-8")),
            inputs,
            sources,
            sha256(protocol),
            pool_size,
            args.smoke,
        )
    rows: list[dict] = []
    run_hashes: dict[str, str] = {}
    for fraction in fractions:
        for seed in seeds:
            identifier = run_id(fraction, seed)
            path = output / f"{identifier}.json"
            if path.exists():
                if not args.resume:
                    raise FileExistsError(f"Refusing to replace existing run: {path}")
                artifact = json.loads(path.read_text(encoding="utf-8"))
                validate_existing_artifact(
                    artifact,
                    fraction,
                    seed,
                    pool_size,
                    args.smoke,
                    expected_inputs=inputs,
                    expected_sources=sources,
                )
            else:
                artifact = run_one(args.dataset, fraction, seed, pool_size, args.smoke)
                artifact["artifact_manifest"] = {
                    "inputs": inputs,
                    "sources": sources,
                    "environment": environment,
                }
                path.write_text(
                    json.dumps(artifact, ensure_ascii=False, indent=2, default=json_default),
                    encoding="utf-8",
                )
                print(identifier, flush=True)
            rows.extend(metric_rows(identifier, artifact))
            run_hashes[path.name] = sha256(path)
    with (output / "method_metrics.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    expected_ids = [run_id(fraction, seed) for fraction in fractions for seed in seeds]
    manifest = {
        "study_version": STUDY,
        "artifact_schema": ARTIFACT_SCHEMA,
        "formal_batch": not args.smoke and len(expected_ids) == 30,
        "smoke_test": bool(args.smoke),
        "not_eligible_for_inference": bool(args.smoke),
        "protocol": {PROTOCOL_NAME: sha256(protocol)},
        "inputs": inputs,
        "frozen_input_verification": {"manifest": str(Path(args.frozen_manifest)), "verified": True},
        "source": sources,
        "run_parameters": {
            "fractions": fractions,
            "seeds": seeds,
            "pool_size": pool_size,
            "selection_world_count": 20,
            "evaluation_world_count": 20,
            "arms": list(ARMS),
        },
        "expected_run_ids": expected_ids,
        "runs": run_hashes,
        "environment": environment,
    }
    (output / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(output)


if __name__ == "__main__":
    main()
