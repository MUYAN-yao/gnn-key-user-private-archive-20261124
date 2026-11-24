"""Read-only integrity and resource validator for the preregistered v6 study.

The validator never writes into a study directory.  In preflight mode it
checks the reserved seed 73 solely for provenance and the fixed cost gate; it
does not use outcome values for inference.  Formal mode requires all ten
predeclared paired blocks before any later analysis may read their outcomes.
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

from experiments.v6_digg_snapshot import MANIFEST, sha256, verify


STUDY = "v6-digg-k5-candidate-reduction"
SCHEMA = "v6-digg-k5-1"
PROTOCOL = "influence_v6_digg_k5_preregistration.md"
PREFLIGHT_SEED = 73
FORMAL_SEEDS = tuple(range(74, 84))
ARMS = (
    "full_candidate", "gnn_pool_30", "gnn_pool_60", "gnn_pool_120",
    "weighted_out_degree_pool_120",
)
POOL_SIZES = {"gnn_pool_30": 30, "gnn_pool_60": 60,
              "gnn_pool_120": 120, "weighted_out_degree_pool_120": 120}
EXPECTED_INPUTS = {
    "nodes.csv": "b1ee9740805a04f594c8e0f1ee102131f7ba1db661fef4992d83a9f80769cb56",
    "edges.csv": "95b4163488e4ae690eba7e42f839db27c0a61cda0d13f6733783694152b16d67",
    "cascades.csv": "18fe5afa3196de05e6757e6c1015d6dcc434f4740d28db51be44021ce778c246",
}
NAMESPACES = (("selection", 501, 20), ("primary_evaluation", 502, 100),
              ("stability_evaluation", 503, 100))
ARM_ORDER_NAMESPACE = 504


def stable_digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def world_sequence(seed: int, namespace: int, count: int) -> list[int]:
    rng = np.random.default_rng(np.random.SeedSequence([seed, namespace, 3]))
    return [int(value) for value in rng.integers(0, 2**63 - 1, size=count)]


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _finite_nonnegative(value: object) -> bool:
    try:
        return bool(np.isfinite(float(value)) and float(value) >= 0.0)
    except (TypeError, ValueError):
        return False


def _expected_seeds(mode: str) -> tuple[int, ...]:
    if mode == "preflight":
        return (PREFLIGHT_SEED,)
    if mode == "formal":
        return FORMAL_SEEDS
    raise ValueError(f"unsupported mode: {mode}")


def _validate_source(reference: object, errors: list[str]) -> dict[str, Any] | None:
    if not isinstance(reference, dict):
        errors.append("manifest source_snapshot is missing")
        return None
    try:
        snapshot_dir = Path(reference["snapshot_dir"])
        snapshot = verify(snapshot_dir)
        _require(reference.get("manifest_name") == MANIFEST, "source snapshot manifest name mismatch", errors)
        _require(reference.get("manifest_sha256") == sha256(snapshot_dir / MANIFEST), "source snapshot manifest digest mismatch", errors)
        _require(reference.get("snapshot_id") == snapshot.get("snapshot_id"), "source snapshot ID mismatch", errors)
        _require(reference.get("file_count") == len(snapshot.get("files", {})), "source snapshot file count mismatch", errors)
        return snapshot
    except (KeyError, OSError, ValueError) as exc:
        errors.append(f"source snapshot verification failed: {exc}")
        return None


def _validate_inputs(manifest: dict[str, Any], errors: list[str]) -> None:
    _require(manifest.get("dataset_id") == "digg", "manifest dataset must be Digg", errors)
    _require(manifest.get("inputs") == EXPECTED_INPUTS, "manifest input hashes differ from preregistration", errors)
    dataset = ROOT / "data" / "processed" / "digg" / "pilot-20000"
    try:
        observed = {name: sha256(dataset / name) for name in EXPECTED_INPUTS}
        _require(observed == EXPECTED_INPUTS, "current Digg input hashes differ from preregistration", errors)
    except OSError as exc:
        errors.append(f"unable to verify current Digg inputs: {exc}")


def _validate_worlds(repro: object, run_id: str, seed: int, errors: list[str]) -> None:
    if not isinstance(repro, dict):
        errors.append(f"{run_id}: reproducibility metadata missing")
        return
    families: list[list[int]] = []
    for label, namespace, count in NAMESPACES:
        worlds = repro.get(f"{label}_worlds")
        _require(isinstance(worlds, list) and worlds == world_sequence(seed, namespace, count), f"{run_id}: {label} worlds mismatch", errors)
        if isinstance(worlds, list):
            _require(repro.get(f"{label}_worlds_sha256") == stable_digest(worlds), f"{run_id}: {label} world digest mismatch", errors)
            families.append(worlds)
        _require(repro.get(f"{label}_namespace") == namespace, f"{run_id}: {label} namespace mismatch", errors)
    if len(families) == 3:
        _require(not (set(families[0]) & set(families[1]) or set(families[0]) & set(families[2]) or set(families[1]) & set(families[2])), f"{run_id}: world families overlap", errors)
    order_seed = world_sequence(seed, ARM_ORDER_NAMESPACE, 1)[0]
    order = [ARMS[int(index)] for index in np.random.default_rng(order_seed).permutation(len(ARMS))]
    _require(repro.get("world_families_disjoint") is True, f"{run_id}: disjointness flag missing", errors)
    _require(repro.get("arm_order_namespace") == ARM_ORDER_NAMESPACE, f"{run_id}: arm-order namespace mismatch", errors)
    _require(repro.get("arm_order_seed") == order_seed and repro.get("arm_execution_order") == order, f"{run_id}: arm order mismatch", errors)


def _validate_arm(arm: object, name: str, universe: list[str], run_id: str, errors: list[str]) -> None:
    prefix = f"{run_id}/{name}"
    if not isinstance(arm, dict):
        errors.append(f"{prefix}: arm missing")
        return
    expected_count = len(universe) if name == "full_candidate" else POOL_SIZES[name]
    members = arm.get("membership_rank_order")
    _require(isinstance(members, list) and len(members) == expected_count, f"{prefix}: candidate count mismatch", errors)
    if isinstance(members, list):
        _require(len(members) == len(set(members)) and set(members).issubset(set(universe)), f"{prefix}: invalid candidates", errors)
        _require(arm.get("canonical_candidate_order") == sorted(members), f"{prefix}: candidate ordering mismatch", errors)
    _require(arm.get("candidate_count") == expected_count, f"{prefix}: declared candidate count mismatch", errors)
    selected = arm.get("selection", {}).get("top_k") if isinstance(arm.get("selection"), dict) else None
    _require(isinstance(selected, list) and len(selected) == 5 and len(set(selected)) == 5, f"{prefix}: invalid Top-K", errors)
    if isinstance(members, list) and isinstance(selected, list):
        _require(set(selected).issubset(set(members)), f"{prefix}: Top-K outside pool", errors)
    for phase, expected_worlds in (("selection", 20), ("primary_evaluation", 100), ("stability_evaluation", 100)):
        score = arm.get(phase)
        _require(isinstance(score, dict), f"{prefix}: {phase} score missing", errors)
        if isinstance(score, dict):
            _require(score.get("top_k") == selected, f"{prefix}: {phase} Top-K mismatch", errors)
            values = score.get("world_spreads")
            _require(isinstance(values, list) and len(values) == expected_worlds and all(_finite_nonnegative(v) for v in values), f"{prefix}: {phase} spreads invalid", errors)
    for field in ("membership_generation_seconds", "candidate_sorting_seconds", "search_seconds", "selection_score_seconds", "primary_evaluation_seconds", "stability_evaluation_seconds", "total_arm_seconds"):
        _require(_finite_nonnegative(arm.get(field)), f"{prefix}: invalid timing {field}", errors)


def _validate_run(path: Path, manifest: dict[str, Any], mode: str, errors: list[str]) -> dict[str, Any] | None:
    run_id = path.stem
    try:
        seed = int(run_id.removeprefix("seed-"))
        artifact = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"{run_id}: unreadable artifact ({exc})")
        return None
    _require(manifest.get("runs", {}).get(path.name) == sha256(path), f"{run_id}: artifact hash mismatch", errors)
    _require(artifact.get("study_version") == STUDY and artifact.get("artifact_schema") == SCHEMA, f"{run_id}: study/schema mismatch", errors)
    _require(artifact.get("dataset_id") == "digg" and artifact.get("execution_mode") == mode, f"{run_id}: dataset/mode mismatch", errors)
    formal = mode == "formal"
    _require(artifact.get("formal_batch") is formal and artifact.get("not_eligible_for_inference") is not formal, f"{run_id}: eligibility flags mismatch", errors)
    config = artifact.get("config")
    required = {"fraction": 0.65, "seed": seed, "seed_count": 5, "horizon": 4,
                "selection_world_count": 20, "primary_evaluation_world_count": 100,
                "stability_evaluation_world_count": 100, "full_candidate_limit": None,
                "risk_lambda": 0.35, "community_weight": 0.25}
    _require(isinstance(config, dict) and all(config.get(k) == v for k, v in required.items()), f"{run_id}: fixed configuration mismatch", errors)
    provenance = artifact.get("artifact_manifest")
    _require(isinstance(provenance, dict) and provenance.get("inputs") == manifest.get("inputs") and provenance.get("source_snapshot") == manifest.get("source_snapshot"), f"{run_id}: provenance mismatch", errors)
    integrity = artifact.get("integrity")
    _require(isinstance(integrity, dict) and integrity.get("status") == "passed" and integrity.get("block_time_limit_exceeded") is False, f"{run_id}: integrity flag failed", errors)
    _require(_finite_nonnegative(artifact.get("block_elapsed_seconds")), f"{run_id}: invalid block elapsed time", errors)
    if formal:
        _require(float(artifact.get("block_elapsed_seconds", float("inf"))) <= 18_000, f"{run_id}: formal block exceeded 18,000 seconds", errors)
    repro = artifact.get("reproducibility")
    _validate_worlds(repro, run_id, seed, errors)
    universe = repro.get("canonical_node_universe") if isinstance(repro, dict) else None
    _require(isinstance(universe, list) and universe == sorted(universe) and len(universe) == len(set(universe)), f"{run_id}: invalid node universe", errors)
    if not isinstance(universe, list):
        universe = []
    arms = artifact.get("arms")
    _require(isinstance(arms, dict) and set(arms) == set(ARMS), f"{run_id}: arm set mismatch", errors)
    if isinstance(arms, dict):
        for name in ARMS:
            _validate_arm(arms.get(name), name, universe, run_id, errors)
    return artifact


def _validate_metrics(study_dir: Path, runs: dict[str, dict[str, Any]], expected_ids: set[str], errors: list[str]) -> None:
    try:
        with (study_dir / "method_metrics.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
    except OSError as exc:
        errors.append(f"method_metrics.csv unreadable: {exc}")
        return
    _require(len(rows) == len(expected_ids) * len(ARMS), "method_metrics.csv row count mismatch", errors)
    identities = {(row.get("run_id"), row.get("method")) for row in rows}
    _require(len(identities) == len(rows) and {item[0] for item in identities} == expected_ids and {item[1] for item in identities} == set(ARMS), "method_metrics.csv identities mismatch", errors)
    for row in rows:
        artifact = runs.get(str(row.get("run_id")))
        method = row.get("method")
        if artifact is None or method not in ARMS:
            continue
        arm = artifact["arms"][method]
        try:
            _require(json.loads(row["top_k"]) == arm["selection"]["top_k"], f"{row['run_id']}/{method}: metrics Top-K mismatch", errors)
            _require(int(row["candidate_count"]) == arm["candidate_count"], f"{row['run_id']}/{method}: metrics candidate count mismatch", errors)
            _require(round(float(row["total_arm_seconds"]), 6) == round(float(arm["total_arm_seconds"]), 6), f"{row['run_id']}/{method}: metrics timing mismatch", errors)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            errors.append(f"{row.get('run_id')}/{method}: invalid metric row")


def validate_study(study_dir: Path, mode: str = "formal") -> dict[str, Any]:
    errors: list[str] = []
    try:
        manifest = json.loads((study_dir / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "errors": [f"manifest.json unreadable: {exc}"]}
    formal = mode == "formal"
    seeds = _expected_seeds(mode)
    ids = {f"seed-{seed}" for seed in seeds}
    _require(manifest.get("study_version") == STUDY and manifest.get("artifact_schema") == SCHEMA, "manifest study/schema mismatch", errors)
    _require(manifest.get("execution_mode") == mode, "manifest execution mode mismatch", errors)
    _require(manifest.get("formal_batch") is formal and manifest.get("not_eligible_for_inference") is not formal, "manifest eligibility flags mismatch", errors)
    _validate_inputs(manifest, errors)
    snapshot = _validate_source(manifest.get("source_snapshot"), errors)
    if snapshot is not None:
        protocol_hash = snapshot.get("files", {}).get(f"protocols/{PROTOCOL}")
        _require(manifest.get("protocol") == {PROTOCOL: protocol_hash}, "manifest protocol hash mismatch", errors)
        copy = study_dir / PROTOCOL
        _require(copy.is_file() and sha256(copy) == protocol_hash, "output protocol copy/hash mismatch", errors)
    _require(set(manifest.get("expected_run_ids", [])) == ids, "manifest run ID plan mismatch", errors)
    _require(set(manifest.get("runs", {})) == {f"{run_id}.json" for run_id in ids}, "manifest run hash plan mismatch", errors)
    paths = {path.stem: path for path in study_dir.glob("seed-*.json")}
    _require(set(paths) == ids, "artifact run set mismatch", errors)
    runs: dict[str, dict[str, Any]] = {}
    for run_id in sorted(ids):
        if run_id in paths:
            artifact = _validate_run(paths[run_id], manifest, mode, errors)
            if artifact is not None:
                runs[run_id] = artifact
    if len(runs) == len(ids):
        _validate_metrics(study_dir, runs, ids, errors)
    gate: dict[str, Any] | None = None
    if mode == "preflight" and "seed-73" in runs:
        full_seconds = float(runs["seed-73"]["arms"]["full_candidate"]["total_arm_seconds"])
        gate = {"full_candidate_seconds": full_seconds, "per_block_limit_seconds": 14_400,
                "ten_block_projection_seconds": full_seconds * 10, "ten_block_limit_seconds": 72 * 3600,
                "passed": full_seconds <= 14_400 and full_seconds * 10 <= 72 * 3600}
        _require(gate["passed"], "preflight resource gate failed", errors)
    return {"status": "PASS" if not errors else "FAIL", "mode": mode,
            "validated_runs": sorted(runs), "cost_gate": gate, "errors": errors}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study-dir", required=True)
    parser.add_argument("--mode", choices=("preflight", "formal"), default="formal")
    args = parser.parse_args()
    report = validate_study(Path(args.study_dir), args.mode)
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
