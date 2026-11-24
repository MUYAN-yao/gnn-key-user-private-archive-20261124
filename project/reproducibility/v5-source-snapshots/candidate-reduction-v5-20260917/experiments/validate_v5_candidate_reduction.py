"""Read-only integrity validator for the preregistered v5 candidate study.

By default this accepts only a complete formal batch.  ``--mode preflight``
checks the reserved seed-62 cost gate without treating it as inferential data.
It never writes into the supplied study directory.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from experiments.v5_source_snapshot import MANIFEST_NAME, sha256, verify_snapshot


STUDY = "v5-candidate-reduction"
ARTIFACT_SCHEMA = "v5-candidate-reduction-1"
PROTOCOL_NAME = "influence_v5_candidate_reduction_preregistration.md"
FRACTION = 0.65
FORMAL_SEEDS = tuple(range(63, 73))
PREFLIGHT_SEED = 62
ARMS = (
    "full_candidate", "gnn_pool_30", "gnn_pool_60", "gnn_pool_120",
    "weighted_out_degree_pool_120",
)
POOL_SIZES = {
    "gnn_pool_30": 30, "gnn_pool_60": 60,
    "gnn_pool_120": 120, "weighted_out_degree_pool_120": 120,
}
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
SELECTION_NAMESPACE = 501
PRIMARY_NAMESPACE = 502
STABILITY_NAMESPACE = 503
ARM_ORDER_NAMESPACE = 504
SELECTION_WORLD_COUNT = 20
PRIMARY_WORLD_COUNT = 100
STABILITY_WORLD_COUNT = 100
METRIC_COLUMNS = {
    "dataset_id", "run_id", "random_seed", "method", "candidate_count", "top_k",
    "primary_mean_spread", "primary_spread_std", "primary_robust_objective",
    "primary_community_coverage", "stability_mean_spread", "stability_spread_std",
    "stability_robust_objective", "stability_community_coverage",
    "ordered_top_k_match_with_full", "top_k_jaccard_with_full",
    "primary_objective_delta_vs_full", "stability_objective_delta_vs_full",
    "membership_generation_seconds", "candidate_sorting_seconds", "search_seconds",
    "selection_score_seconds", "primary_evaluation_seconds",
    "stability_evaluation_seconds", "total_arm_seconds", "formal_batch",
    "not_eligible_for_inference",
}


def stable_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def world_sequence(seed: int, namespace: int, count: int) -> list[int]:
    generator = np.random.default_rng(np.random.SeedSequence([seed, namespace, 3]))
    return [int(value) for value in generator.integers(0, 2**63 - 1, size=count)]


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _finite_nonnegative(value: object) -> bool:
    try:
        return bool(np.isfinite(float(value)) and float(value) >= 0.0)
    except (TypeError, ValueError):
        return False


def _finite(value: object) -> bool:
    try:
        return bool(np.isfinite(float(value)))
    except (TypeError, ValueError):
        return False


def expected_seeds(mode: str) -> tuple[int, ...]:
    if mode == "formal":
        return FORMAL_SEEDS
    if mode == "preflight":
        return (PREFLIGHT_SEED,)
    raise ValueError(f"Unsupported validator mode: {mode}")


def expected_run_ids(mode: str) -> set[str]:
    return {f"seed-{seed}" for seed in expected_seeds(mode)}


def _validate_snapshot(manifest: dict[str, Any], errors: list[str]) -> dict[str, Any] | None:
    reference = manifest.get("source_snapshot")
    if not isinstance(reference, dict):
        errors.append("manifest source_snapshot is missing")
        return None
    try:
        snapshot_dir = Path(reference["snapshot_dir"])
        snapshot = verify_snapshot(snapshot_dir)
        _require(reference.get("manifest_name") == MANIFEST_NAME, "source snapshot manifest name mismatch", errors)
        _require(reference.get("manifest_sha256") == sha256(snapshot_dir / MANIFEST_NAME), "source snapshot manifest digest mismatch", errors)
        _require(reference.get("snapshot_id") == snapshot.get("snapshot_id"), "source snapshot ID mismatch", errors)
        _require(reference.get("file_count") == len(snapshot.get("files", {})), "source snapshot file count mismatch", errors)
        return snapshot
    except (KeyError, OSError, ValueError) as exc:
        errors.append(f"source snapshot verification failed: {exc}")
        return None


def _validate_inputs(manifest: dict[str, Any], errors: list[str]) -> str | None:
    dataset_id = manifest.get("dataset_id")
    if dataset_id not in EXPECTED_INPUTS:
        errors.append("manifest dataset_id is unknown")
        return None
    expected = EXPECTED_INPUTS[dataset_id]
    _require(manifest.get("inputs") == expected, "manifest input hashes differ from preregistration", errors)
    try:
        dataset_dir = Path(manifest["dataset_path"])
        observed = {name: sha256(dataset_dir / name) for name in expected}
        _require(observed == expected, "current dataset input hashes differ from preregistration", errors)
    except (KeyError, OSError) as exc:
        errors.append(f"unable to verify current dataset inputs: {exc}")
    return str(dataset_id)


def _check_worlds(reproducibility: dict[str, Any], run_id: str, seed: int, errors: list[str]) -> None:
    world_specs = (
        ("selection", SELECTION_NAMESPACE, SELECTION_WORLD_COUNT),
        ("primary_evaluation", PRIMARY_NAMESPACE, PRIMARY_WORLD_COUNT),
        ("stability_evaluation", STABILITY_NAMESPACE, STABILITY_WORLD_COUNT),
    )
    lists: list[list[int]] = []
    for label, namespace, count in world_specs:
        worlds = reproducibility.get(f"{label}_worlds")
        _require(isinstance(worlds, list) and len(worlds) == count, f"{run_id}: {label} world count mismatch", errors)
        if isinstance(worlds, list):
            _require(worlds == world_sequence(seed, namespace, count), f"{run_id}: {label} worlds/namespace mismatch", errors)
            _require(reproducibility.get(f"{label}_worlds_sha256") == stable_digest(worlds), f"{run_id}: {label} world digest mismatch", errors)
            lists.append(worlds)
        _require(reproducibility.get(f"{label}_namespace") == namespace, f"{run_id}: {label} namespace mismatch", errors)
    if len(lists) == 3:
        _require(not (set(lists[0]) & set(lists[1]) or set(lists[0]) & set(lists[2]) or set(lists[1]) & set(lists[2])), f"{run_id}: world families overlap", errors)
    _require(reproducibility.get("world_families_disjoint") is True, f"{run_id}: world disjointness flag missing", errors)
    order_seed = world_sequence(seed, ARM_ORDER_NAMESPACE, 1)[0]
    expected_order = [ARMS[int(index)] for index in np.random.default_rng(order_seed).permutation(len(ARMS))]
    _require(reproducibility.get("arm_order_namespace") == ARM_ORDER_NAMESPACE, f"{run_id}: arm order namespace mismatch", errors)
    _require(reproducibility.get("arm_order_seed") == order_seed, f"{run_id}: arm order seed mismatch", errors)
    _require(reproducibility.get("arm_execution_order") == expected_order, f"{run_id}: arm execution order mismatch", errors)


def _check_score(score: object, top_k: list[str], count: int, prefix: str, errors: list[str]) -> None:
    _require(isinstance(score, dict), f"{prefix}: score is missing", errors)
    if not isinstance(score, dict):
        return
    _require(score.get("top_k") == top_k, f"{prefix}: score Top-K differs from selection", errors)
    spreads = score.get("world_spreads")
    _require(isinstance(spreads, list) and len(spreads) == count and all(_finite(value) for value in spreads), f"{prefix}: world spread values are invalid", errors)
    for field in ("mean_spread", "spread_std", "robust_objective", "community_coverage"):
        _require(_finite(score.get(field)), f"{prefix}: non-finite {field}", errors)


def _check_arm(arm: object, name: str, universe: list[str], mode: str, run_id: str, errors: list[str]) -> None:
    prefix = f"{run_id}/{name}"
    _require(isinstance(arm, dict), f"{prefix}: arm payload is missing", errors)
    if not isinstance(arm, dict):
        return
    membership = arm.get("membership_rank_order")
    canonical = arm.get("canonical_candidate_order")
    expected_count = len(universe) if name == "full_candidate" else POOL_SIZES[name]
    _require(isinstance(membership, list) and len(membership) == expected_count, f"{prefix}: membership count mismatch", errors)
    if isinstance(membership, list):
        members = list(map(str, membership))
        _require(len(members) == len(set(members)), f"{prefix}: duplicate candidate", errors)
        _require(set(members).issubset(set(universe)), f"{prefix}: candidate outside node universe", errors)
        if name == "full_candidate" and mode != "smoke":
            _require(members == universe, f"{prefix}: formal full pool differs from node universe", errors)
    _require(canonical == sorted(map(str, membership)) if isinstance(membership, list) else False, f"{prefix}: canonical candidate order mismatch", errors)
    _require(arm.get("candidate_count") == expected_count, f"{prefix}: candidate_count mismatch", errors)
    selection = arm.get("selection")
    top_k = selection.get("top_k") if isinstance(selection, dict) else []
    _require(isinstance(top_k, list) and len(top_k) == 5 and len(set(top_k)) == 5, f"{prefix}: selected Top-K is invalid", errors)
    if isinstance(membership, list) and isinstance(top_k, list):
        _require(set(top_k).issubset(set(map(str, membership))), f"{prefix}: selected node is outside membership", errors)
    _check_score(selection, top_k, SELECTION_WORLD_COUNT, f"{prefix}/selection", errors)
    _check_score(arm.get("primary_evaluation"), top_k, PRIMARY_WORLD_COUNT, f"{prefix}/primary", errors)
    _check_score(arm.get("stability_evaluation"), top_k, STABILITY_WORLD_COUNT, f"{prefix}/stability", errors)
    rounds = arm.get("rounds")
    _require(isinstance(rounds, list) and len(rounds) == 5, f"{prefix}: greedy trace round count mismatch", errors)
    if isinstance(rounds, list) and isinstance(membership, list):
        selected_before: list[str] = []
        for index, entry in enumerate(rounds):
            _require(isinstance(entry, dict), f"{prefix}: malformed trace entry {index + 1}", errors)
            if not isinstance(entry, dict):
                continue
            _require(entry.get("round") == index + 1 and entry.get("selected_before") == selected_before, f"{prefix}: trace history mismatch at round {index + 1}", errors)
            winner = entry.get("winner")
            _require(winner in membership and winner not in selected_before, f"{prefix}: invalid winner at round {index + 1}", errors)
            _require(entry.get("trial_count") == len(membership) - index, f"{prefix}: trace trial count mismatch at round {index + 1}", errors)
            _require(isinstance(entry.get("exact_best_tie_count"), int) and entry["exact_best_tie_count"] >= 1, f"{prefix}: invalid tie count at round {index + 1}", errors)
            if winner is not None:
                selected_before.append(str(winner))
        _require(selected_before == top_k, f"{prefix}: trace winners differ from selected Top-K", errors)
    agreement = arm.get("agreement_with_full_candidate")
    _require(isinstance(agreement, dict), f"{prefix}: full-arm agreement is missing", errors)
    if isinstance(agreement, dict):
        _require(isinstance(agreement.get("ordered_top_k_match"), bool), f"{prefix}: ordered Top-K agreement invalid", errors)
        _require(_finite(agreement.get("top_k_jaccard")) and 0.0 <= float(agreement["top_k_jaccard"]) <= 1.0, f"{prefix}: Jaccard invalid", errors)
        _require(_finite(agreement.get("primary_robust_objective_delta")), f"{prefix}: primary delta invalid", errors)
        _require(_finite(agreement.get("stability_robust_objective_delta")), f"{prefix}: stability delta invalid", errors)
    for field in ("membership_generation_seconds", "candidate_sorting_seconds", "search_seconds", "selection_score_seconds", "primary_evaluation_seconds", "stability_evaluation_seconds", "total_arm_seconds"):
        _require(_finite_nonnegative(arm.get(field)), f"{prefix}: invalid timing {field}", errors)


def _validate_artifact(path: Path, manifest: dict[str, Any], dataset_id: str, mode: str, errors: list[str]) -> dict[str, Any] | None:
    run_id = path.stem
    try:
        artifact = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{run_id}: unreadable JSON ({exc})")
        return None
    _require(manifest.get("runs", {}).get(path.name) == sha256(path), f"{run_id}: artifact hash mismatch", errors)
    _require(artifact.get("study_version") == STUDY and artifact.get("artifact_schema") == ARTIFACT_SCHEMA, f"{run_id}: study/schema mismatch", errors)
    _require(artifact.get("dataset_id") == dataset_id and artifact.get("execution_mode") == mode, f"{run_id}: dataset/mode mismatch", errors)
    expected_formal = mode == "formal"
    _require(artifact.get("formal_batch") is expected_formal and artifact.get("not_eligible_for_inference") is not expected_formal, f"{run_id}: eligibility flags mismatch", errors)
    try:
        seed = int(run_id.removeprefix("seed-"))
    except ValueError:
        errors.append(f"{run_id}: malformed run ID")
        return artifact
    config = artifact.get("config")
    required_config = {
        "fraction": FRACTION, "seed": seed, "seed_count": 5, "horizon": 4,
        "selection_world_count": SELECTION_WORLD_COUNT,
        "primary_evaluation_world_count": PRIMARY_WORLD_COUNT,
        "stability_evaluation_world_count": STABILITY_WORLD_COUNT,
        "risk_lambda": 0.35, "community_weight": 0.25,
    }
    _require(isinstance(config, dict), f"{run_id}: config missing", errors)
    if isinstance(config, dict):
        for field, value in required_config.items():
            _require(config.get(field) == value, f"{run_id}: config {field} mismatch", errors)
        _require(config.get("full_candidate_limit") is None, f"{run_id}: full pool was truncated", errors)
    provenance = artifact.get("artifact_manifest")
    _require(isinstance(provenance, dict), f"{run_id}: artifact_manifest missing", errors)
    if isinstance(provenance, dict):
        _require(provenance.get("inputs") == manifest.get("inputs"), f"{run_id}: input provenance mismatch", errors)
        _require(provenance.get("source_snapshot") == manifest.get("source_snapshot"), f"{run_id}: source snapshot provenance mismatch", errors)
        _require(isinstance(provenance.get("environment"), dict), f"{run_id}: environment metadata missing", errors)
    integrity = artifact.get("integrity")
    _require(isinstance(integrity, dict) and integrity.get("status") == "passed" and integrity.get("block_time_limit_exceeded") is False, f"{run_id}: artifact integrity status failed", errors)
    _require(_finite_nonnegative(artifact.get("block_elapsed_seconds")), f"{run_id}: invalid block elapsed time", errors)
    if mode == "formal":
        _require(float(artifact.get("block_elapsed_seconds", float("inf"))) <= 18_000, f"{run_id}: formal block exceeded 18,000 seconds", errors)
    reproducibility = artifact.get("reproducibility")
    _require(isinstance(reproducibility, dict), f"{run_id}: reproducibility block missing", errors)
    if not isinstance(reproducibility, dict):
        return artifact
    _check_worlds(reproducibility, run_id, seed, errors)
    universe = reproducibility.get("canonical_node_universe")
    _require(isinstance(universe, list) and universe == sorted(map(str, universe)) and len(universe) == len(set(universe)), f"{run_id}: canonical node universe invalid", errors)
    if not isinstance(universe, list):
        universe = []
    _require(reproducibility.get("canonical_node_universe_sha256") == stable_digest(universe), f"{run_id}: node universe digest mismatch", errors)
    _require(isinstance(reproducibility.get("probability_edge_count"), int) and reproducibility["probability_edge_count"] > 0, f"{run_id}: probability edge count invalid", errors)
    digest = reproducibility.get("probabilities_sha256")
    _require(isinstance(digest, str) and len(digest) == 64, f"{run_id}: probability digest invalid", errors)
    arms = artifact.get("arms")
    _require(isinstance(arms, dict) and set(arms) == set(ARMS), f"{run_id}: arm set mismatch", errors)
    if isinstance(arms, dict):
        for name in ARMS:
            _check_arm(arms.get(name), name, universe, mode, run_id, errors)
        full = arms.get("full_candidate")
        if isinstance(full, dict):
            full_top_k = full.get("selection", {}).get("top_k") if isinstance(full.get("selection"), dict) else []
            for name in ARMS:
                arm = arms.get(name)
                if not isinstance(arm, dict):
                    continue
                agreement = arm.get("agreement_with_full_candidate", {})
                observed = arm.get("selection", {}).get("top_k") if isinstance(arm.get("selection"), dict) else []
                _require(agreement.get("ordered_top_k_match") == (observed == full_top_k), f"{run_id}/{name}: ordered agreement mismatch", errors)
    return artifact


def _validate_metrics(study_dir: Path, artifacts: dict[str, dict[str, Any]], dataset_id: str, mode: str, errors: list[str]) -> list[dict[str, str]]:
    path = study_dir / "method_metrics.csv"
    if not path.is_file():
        errors.append("method_metrics.csv is missing")
        return []
    try:
        with path.open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as exc:
        errors.append(f"method_metrics.csv is unreadable: {exc}")
        return []
    expected_ids = expected_run_ids(mode)
    _require(bool(rows) and METRIC_COLUMNS.issubset(rows[0]), "method_metrics.csv columns mismatch", errors)
    _require(len(rows) == len(expected_ids) * len(ARMS), "method_metrics.csv row count mismatch", errors)
    seen = {(row.get("run_id"), row.get("method")) for row in rows}
    _require(len(seen) == len(rows), "method_metrics.csv contains duplicate run/method rows", errors)
    _require({row.get("run_id") for row in rows} == expected_ids and {row.get("method") for row in rows} == set(ARMS), "method_metrics.csv identity set mismatch", errors)
    for row in rows:
        run_id, method = row.get("run_id"), row.get("method")
        artifact = artifacts.get(str(run_id))
        _require(row.get("dataset_id") == dataset_id, f"{run_id}/{method}: dataset ID mismatch in metrics", errors)
        if artifact is None or method not in ARMS:
            continue
        arm = artifact["arms"][method]
        try:
            _require(json.loads(row["top_k"]) == arm["selection"]["top_k"], f"{run_id}/{method}: Top-K metrics mismatch", errors)
            _require(int(row["candidate_count"]) == arm["candidate_count"], f"{run_id}/{method}: candidate count metrics mismatch", errors)
            _require(int(row["random_seed"]) == artifact["config"]["seed"], f"{run_id}/{method}: seed metrics mismatch", errors)
            _require(row["formal_batch"].lower() == str(artifact["formal_batch"]).lower(), f"{run_id}/{method}: formal flag metrics mismatch", errors)
            _require(row["not_eligible_for_inference"].lower() == str(artifact["not_eligible_for_inference"]).lower(), f"{run_id}/{method}: eligibility metrics mismatch", errors)
            for csv_name, source in (
                ("primary_robust_objective", arm["primary_evaluation"]["robust_objective"]),
                ("stability_robust_objective", arm["stability_evaluation"]["robust_objective"]),
                ("primary_objective_delta_vs_full", arm["agreement_with_full_candidate"]["primary_robust_objective_delta"]),
                ("stability_objective_delta_vs_full", arm["agreement_with_full_candidate"]["stability_robust_objective_delta"]),
                ("search_seconds", arm["search_seconds"]),
                ("total_arm_seconds", arm["total_arm_seconds"]),
            ):
                _require(round(float(row[csv_name]), 6) == round(float(source), 6), f"{run_id}/{method}: metrics mismatch for {csv_name}", errors)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            errors.append(f"{run_id}/{method}: invalid metrics value")
    return rows


def validate_study(study_dir: Path, mode: str = "formal") -> dict[str, Any]:
    """Validate a formal batch or a preflight, returning a JSON-safe report."""
    errors: list[str] = []
    if mode not in {"formal", "preflight"}:
        return {"status": "FAIL", "errors": ["Validator accepts formal or preflight mode only"]}
    manifest_path = study_dir / "manifest.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "errors": [f"manifest.json unreadable: {exc}"]}
    expected_formal = mode == "formal"
    _require(manifest.get("study_version") == STUDY and manifest.get("artifact_schema") == ARTIFACT_SCHEMA, "manifest study/schema mismatch", errors)
    _require(manifest.get("execution_mode") == mode, "manifest execution mode mismatch", errors)
    _require(manifest.get("formal_batch") is expected_formal and manifest.get("not_eligible_for_inference") is not expected_formal, "manifest eligibility flags mismatch", errors)
    dataset_id = _validate_inputs(manifest, errors)
    snapshot = _validate_snapshot(manifest, errors)
    if snapshot is not None:
        expected_protocol_hash = snapshot.get("files", {}).get(f"protocols/{PROTOCOL_NAME}")
        _require(manifest.get("protocol") == {PROTOCOL_NAME: expected_protocol_hash}, "manifest protocol hash does not match snapshot", errors)
        copy_path = study_dir / PROTOCOL_NAME
        _require(copy_path.is_file() and sha256(copy_path) == expected_protocol_hash, "output protocol copy/hash mismatch", errors)
    expected_ids = expected_run_ids(mode)
    _require(set(manifest.get("expected_run_ids", [])) == expected_ids, "manifest expected run IDs mismatch", errors)
    _require(set(manifest.get("runs", {})) == {f"{run_id}.json" for run_id in expected_ids}, "manifest run-hash set mismatch", errors)
    artifact_paths = {path.stem: path for path in study_dir.glob("seed-*.json")}
    _require(set(artifact_paths) == expected_ids, "artifact run set mismatch", errors)
    artifacts: dict[str, dict[str, Any]] = {}
    if dataset_id is not None:
        for run_id in sorted(expected_ids):
            if run_id in artifact_paths:
                artifact = _validate_artifact(artifact_paths[run_id], manifest, dataset_id, mode, errors)
                if artifact is not None:
                    artifacts[run_id] = artifact
    metrics = _validate_metrics(study_dir, artifacts, dataset_id or "", mode, errors) if len(artifacts) == len(expected_ids) else []
    cost_gate: dict[str, Any] | None = None
    if mode == "preflight" and len(artifacts) == 1:
        full_seconds = float(artifacts["seed-62"]["arms"]["full_candidate"]["total_arm_seconds"])
        cost_gate = {
            "full_candidate_seconds": full_seconds,
            "per_dataset_limit_seconds": 14_400,
            "ten_block_projection_seconds": full_seconds * 10,
            "ten_block_limit_seconds": 72 * 3600,
            "passed": full_seconds <= 14_400 and full_seconds * 10 <= 72 * 3600,
        }
    return {
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "study_dir": str(study_dir),
        "mode": mode,
        "dataset_id": dataset_id,
        "cost_gate": cost_gate,
        "validated_run_count": len(artifacts),
        "metrics_row_count": len(metrics),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study-dir", required=True)
    parser.add_argument("--mode", choices=("formal", "preflight"), default="formal")
    args = parser.parse_args()
    report = validate_study(Path(args.study_dir), args.mode)
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
