"""Strict read-only validator and paired-statistics audit for v4 formal runs.

The command never writes to the study directory.  It refuses incomplete,
smoke, mixed-version, or schema-inconsistent batches before calculating the
pre-registered contrasts.  It is intentionally independent of the formal
runner so that a changed runner cannot silently relax the audit rules.
"""
from __future__ import annotations

import argparse
import csv
from itertools import product
import hashlib
import json
from pathlib import Path
from statistics import mean

import numpy as np
from scipy import stats


STUDY = "v4-screening-formal"
ARTIFACT_SCHEMA = "v4-screening-formal-1"
ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT / "data" / "processed" / "higgs-twitter" / "pilot-50000"
FROZEN_MANIFEST = ROOT / "reproducibility" / "frozen-study-manifest-v1.json"
FRACTIONS = (0.60, 0.65, 0.70)
SEEDS = tuple(range(52, 62))
ARMS = ("gnn_prior", "weighted_out_degree", "pagerank", "uniform_random")
POOL_SIZE = 120
SELECTION_WORLDS = 20
EVALUATION_WORLDS = 20
SELECTION_NAMESPACE = 101
EVALUATION_NAMESPACE = 202
RANDOM_MEMBERSHIP_NAMESPACE = 303
ARM_ORDER_NAMESPACE = 404
RUN_REQUIRED_CONFIG = {
    "pool_size": POOL_SIZE,
    "seed_count": 2,
    "horizon": 4,
    "selection_world_count": SELECTION_WORLDS,
    "evaluation_world_count": EVALUATION_WORLDS,
    "risk_lambda": 0.35,
    "community_weight": 0.25,
}
METRIC_COLUMNS = {
    "run_id", "train_fraction", "random_seed", "method", "mean_spread",
    "spread_std", "robust_objective", "community_coverage", "top_k",
    "selection_mean_spread", "selection_spread_std",
    "selection_robust_objective", "selection_community_coverage",
    "candidate_count", "membership_generation_seconds",
    "candidate_sorting_seconds", "search_seconds", "selection_score_seconds",
    "evaluation_seconds", "total_arm_seconds", "not_eligible_for_inference",
}


def expected_source_paths() -> dict[str, Path]:
    return {
        "run_v4_screening_formal.py": ROOT / "experiments" / "run_v4_screening_formal.py",
        "influence_v4_screening_formal_preregistration.md": ROOT / "protocols" / "influence_v4_screening_formal_preregistration.md",
        "run_rolling_study_v2_t0.py": ROOT / "experiments" / "run_rolling_study_v2_t0.py",
        "run_v4_screening_diagnostic.py": ROOT / "experiments" / "run_v4_screening_diagnostic.py",
        "run_v3_fairness_sensitivity.py": ROOT / "experiments" / "run_v3_fairness_sensitivity.py",
        "pipeline_v2_t0.py": ROOT / "backend" / "app" / "pipeline_v2_t0.py",
        "pipeline_v2_t0b.py": ROOT / "backend" / "app" / "pipeline_v2_t0b.py",
        "model_v2.py": ROOT / "backend" / "app" / "model_v2.py",
        "graph.py": ROOT / "backend" / "app" / "graph.py",
        "validation.py": ROOT / "backend" / "app" / "validation.py",
    }


def expected_input_hashes() -> dict[str, str]:
    frozen = json.loads(FROZEN_MANIFEST.read_text(encoding="utf-8"))
    for study in frozen.get("studies", []):
        if study.get("study_directory", "").replace("/", "\\").endswith(
            "results\\large-robust-greedy-higgs-50000-v1"
        ):
            return {
                Path(path).name: digest
                for path, digest in study.get("dataset_sha256", {}).items()
            }
    raise ValueError("Frozen Higgs study input hashes are missing")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, separators=(",", ":"), sort_keys=True).encode("utf-8")
    ).hexdigest()


def world_sequence(seed: int, namespace: int, count: int) -> list[int]:
    generator = np.random.default_rng(np.random.SeedSequence([seed, namespace, 3]))
    return [int(value) for value in generator.integers(0, 2**63 - 1, size=count)]


def expected_run_ids() -> set[str]:
    return {f"split-{fraction:.2f}-seed-{seed}" for fraction in FRACTIONS for seed in SEEDS}


def is_finite(value: object) -> bool:
    try:
        return bool(np.isfinite(float(value)))
    except (TypeError, ValueError):
        return False


def exact_sign_flip_pvalue(differences: list[float]) -> float:
    if not differences or len(differences) > 20:
        raise ValueError("The exact sign-flip audit supports 1--20 paired values")
    observed = abs(mean(differences))
    null_means = (
        abs(sum(sign * value for sign, value in zip(signs, differences)) / len(differences))
        for signs in product((-1, 1), repeat=len(differences))
    )
    return float(sum(value >= observed - 1e-12 for value in null_means) / (2 ** len(differences)))


def holm_adjust(pvalues: list[float]) -> list[float]:
    order = np.argsort(np.asarray(pvalues, dtype=float), kind="stable")
    adjusted = np.empty(len(pvalues), dtype=float)
    running = 0.0
    for rank, index in enumerate(order):
        running = max(running, (len(pvalues) - rank) * float(pvalues[index]))
        adjusted[index] = min(1.0, running)
    return adjusted.tolist()


def paired_summary(differences: list[float]) -> dict[str, object]:
    values = np.asarray(differences, dtype=float)
    if len(values) != len(SEEDS):
        raise ValueError(f"Expected {len(SEEDS)} paired differences, found {len(values)}")
    average = float(values.mean())
    sd = float(values.std(ddof=1))
    half = float(stats.t.ppf(0.975, len(values) - 1) * sd / np.sqrt(len(values)))
    # Values in formal artifacts are six-decimal objectives; equality here is
    # intentional and avoids inheriting a hidden np.isclose tolerance.
    ties = int(np.sum(values == 0.0))
    return {
        "n": len(values),
        "mean_difference": average,
        "sd_difference": sd,
        "ci_low": average - half,
        "ci_high": average + half,
        "cohen_dz": None if sd == 0.0 else average / sd,
        "cohen_dz_status": "undefined_zero_variance" if sd == 0.0 else "defined",
        "exact_two_sided_sign_flip_p": exact_sign_flip_pvalue(values.tolist()),
        "wins": int(np.sum(values > 0.0)),
        "ties": ties,
        "losses": int(np.sum(values < 0.0)),
        "differences": values.tolist(),
    }


def _require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def _check_worlds(reproducibility: dict, run_id: str, seed: int, errors: list[str]) -> None:
    selection = reproducibility.get("selection_worlds")
    evaluation = reproducibility.get("evaluation_worlds")
    _require(isinstance(selection, list) and len(selection) == SELECTION_WORLDS,
             f"{run_id}: selection worlds must contain {SELECTION_WORLDS} values", errors)
    _require(isinstance(evaluation, list) and len(evaluation) == EVALUATION_WORLDS,
             f"{run_id}: evaluation worlds must contain {EVALUATION_WORLDS} values", errors)
    if isinstance(selection, list) and isinstance(evaluation, list):
        _require(not set(selection).intersection(evaluation), f"{run_id}: world families overlap", errors)
        _require(reproducibility.get("selection_worlds_sha256") == stable_digest(selection),
                 f"{run_id}: selection world digest mismatch", errors)
        _require(reproducibility.get("evaluation_worlds_sha256") == stable_digest(evaluation),
                 f"{run_id}: evaluation world digest mismatch", errors)
        _require(selection == world_sequence(seed, SELECTION_NAMESPACE, SELECTION_WORLDS),
                 f"{run_id}: selection worlds do not match namespace {SELECTION_NAMESPACE}", errors)
        _require(evaluation == world_sequence(seed, EVALUATION_NAMESPACE, EVALUATION_WORLDS),
                 f"{run_id}: evaluation worlds do not match namespace {EVALUATION_NAMESPACE}", errors)
    _require(reproducibility.get("selection_evaluation_worlds_disjoint") is True,
             f"{run_id}: disjoint-world flag is missing or false", errors)
    _require(reproducibility.get("selection_namespace") == SELECTION_NAMESPACE,
             f"{run_id}: selection namespace is missing or changed", errors)
    _require(reproducibility.get("evaluation_namespace") == EVALUATION_NAMESPACE,
             f"{run_id}: evaluation namespace is missing or changed", errors)
    _require(reproducibility.get("random_membership_namespace") == RANDOM_MEMBERSHIP_NAMESPACE,
             f"{run_id}: random-membership namespace is missing or changed", errors)
    _require(reproducibility.get("arm_order_namespace") == ARM_ORDER_NAMESPACE,
             f"{run_id}: arm-order namespace is missing or changed", errors)
    _require(isinstance(reproducibility.get("random_membership_seed"), int),
             f"{run_id}: random-membership seed is missing", errors)
    _require(isinstance(reproducibility.get("arm_order_seed"), int),
             f"{run_id}: arm-order seed is missing", errors)


def _check_arm(arm: dict, name: str, run_id: str, errors: list[str]) -> None:
    prefix = f"{run_id}/{name}"
    candidates = arm.get("membership_rank_order")
    canonical = arm.get("canonical_candidate_order")
    _require(isinstance(candidates, list) and len(candidates) == POOL_SIZE,
             f"{prefix}: membership must contain {POOL_SIZE} nodes", errors)
    if isinstance(candidates, list):
        _require(len(set(map(str, candidates))) == POOL_SIZE, f"{prefix}: membership has duplicates", errors)
    if isinstance(candidates, list) and isinstance(canonical, list):
        _require(canonical == sorted(map(str, candidates)), f"{prefix}: canonical order mismatch", errors)
    else:
        _require(False, f"{prefix}: canonical candidate order is missing", errors)
    _require(arm.get("candidate_count") == POOL_SIZE, f"{prefix}: candidate_count mismatch", errors)

    rounds = arm.get("rounds")
    _require(isinstance(rounds, list) and len(rounds) == 2, f"{prefix}: exactly two greedy rounds required", errors)
    if isinstance(rounds, list) and len(rounds) == 2:
        for round_index, expected_count in enumerate((POOL_SIZE, POOL_SIZE - 1), start=1):
            row = rounds[round_index - 1]
            _require(isinstance(row, dict), f"{prefix}: malformed round {round_index}", errors)
            if isinstance(row, dict):
                for field in ("round", "winner", "runner_up", "winner_objective",
                              "runner_up_objective", "winner_margin", "exact_best_tie_count"):
                    _require(field in row, f"{prefix}: round {round_index} missing {field}", errors)
                _require(row.get("round") == round_index, f"{prefix}: round index mismatch", errors)
                _require(isinstance(row.get("selected_before"), list),
                         f"{prefix}: round {round_index} selected_before is missing", errors)
                _require(isinstance(row.get("exact_best_tie_count"), int)
                         and row["exact_best_tie_count"] >= 1,
                         f"{prefix}: round {round_index} tie count is invalid", errors)
            scores = row.get("candidate_scores") if isinstance(row, dict) else None
            _require(isinstance(scores, list) and len(scores) == expected_count,
                     f"{prefix}: round {round_index} must contain {expected_count} candidate rows", errors)
            if isinstance(scores, list):
                names = [str(item.get("candidate")) for item in scores if isinstance(item, dict)]
                _require(len(names) == len(set(names)), f"{prefix}: round {round_index} has duplicate candidates", errors)
                canonical_nodes = set(map(str, canonical)) if isinstance(canonical, list) else set()
                expected_names = canonical_nodes - set(map(str, row.get("selected_before", []))) if isinstance(row, dict) else set()
                _require(set(names) == expected_names, f"{prefix}: round {round_index} candidate set mismatch", errors)
                if isinstance(row, dict):
                    _require(str(row.get("winner")) in set(names), f"{prefix}: round {round_index} winner is not scored", errors)
                    _require(row.get("runner_up") is None or str(row.get("runner_up")) in set(names),
                             f"{prefix}: round {round_index} runner-up is not scored", errors)
                    for field in ("winner_objective", "runner_up_objective", "winner_margin"):
                        _require(row.get(field) is None or is_finite(row.get(field)),
                                 f"{prefix}: round {round_index} invalid {field}", errors)
                for item in scores:
                    if not isinstance(item, dict):
                        errors.append(f"{prefix}: malformed round {round_index} candidate row")
                        continue
                    _require(all(key in item for key in ("candidate", "robust_objective", "world_spreads")),
                             f"{prefix}: incomplete round {round_index} score row", errors)
                    world_spreads = item.get("world_spreads")
                    _require(isinstance(world_spreads, list) and len(world_spreads) == SELECTION_WORLDS,
                             f"{prefix}: round {round_index} world values must contain {SELECTION_WORLDS}", errors)
                    for value in world_spreads or []:
                        _require(is_finite(value), f"{prefix}: non-finite round world value", errors)
                    for field in ("mean_spread", "spread_std", "robust_objective", "community_coverage"):
                        _require(is_finite(item.get(field)), f"{prefix}: non-finite score field {field}", errors)
    selection = arm.get("selection")
    evaluation = arm.get("reporting_evaluation")
    for label, values in (("selection", selection), ("evaluation", evaluation)):
        _require(isinstance(values, dict), f"{prefix}: {label} score is missing", errors)
        if not isinstance(values, dict):
            continue
        world_spreads = values.get("world_spreads")
        expected = SELECTION_WORLDS if label == "selection" else EVALUATION_WORLDS
        _require(isinstance(world_spreads, list) and len(world_spreads) == expected,
                 f"{prefix}: {label} world values must contain {expected}", errors)
        for value in world_spreads or []:
            _require(is_finite(value), f"{prefix}: non-finite {label} world value", errors)
        for field in ("mean_spread", "spread_std", "robust_objective", "community_coverage"):
            _require(is_finite(values.get(field)), f"{prefix}: non-finite {label} field {field}", errors)
        top_k = values.get("top_k")
        _require(isinstance(top_k, list) and len(top_k) == 2 and len(set(map(str, top_k))) == 2,
                 f"{prefix}: {label} selected set must contain two distinct nodes", errors)
        if isinstance(top_k, list) and isinstance(canonical, list):
            _require(set(map(str, top_k)).issubset(set(map(str, canonical))),
                     f"{prefix}: {label} selected nodes are outside the candidate pool", errors)
    if isinstance(selection, dict) and isinstance(evaluation, dict):
        _require(list(map(str, selection.get("top_k", []))) == list(map(str, evaluation.get("top_k", []))),
                 f"{prefix}: selection and evaluation selected sets differ", errors)
    for field in ("membership_generation_seconds", "candidate_sorting_seconds", "search_seconds",
                  "selection_score_seconds", "evaluation_seconds", "total_arm_seconds"):
        _require(is_finite(arm.get(field)) and float(arm[field]) >= 0.0,
                 f"{prefix}: invalid timing field {field}", errors)


def _validate_artifact(path: Path, manifest: dict, errors: list[str]) -> dict | None:
    run_id = path.stem
    try:
        artifact = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{run_id}: unreadable JSON ({exc})")
        return None
    manifest_runs = manifest.get("runs", {})
    _require(isinstance(manifest_runs, dict) and manifest_runs.get(path.name) == sha256(path),
             f"{run_id}: artifact hash does not match manifest", errors)
    artifact_manifest = artifact.get("artifact_manifest")
    _require(isinstance(artifact_manifest, dict),
             f"{run_id}: artifact_manifest is missing", errors)
    if isinstance(artifact_manifest, dict):
        _require(artifact_manifest.get("inputs") == manifest.get("inputs"),
                 f"{run_id}: artifact input hashes do not match batch manifest", errors)
        _require(artifact_manifest.get("sources") == manifest.get("source"),
                 f"{run_id}: artifact source hashes do not match batch manifest", errors)
    _require(artifact.get("study_version") == STUDY, f"{run_id}: study version mismatch", errors)
    _require(artifact.get("artifact_schema") == ARTIFACT_SCHEMA,
             f"{run_id}: artifact schema mismatch", errors)
    _require(artifact.get("formal_batch") is True and artifact.get("not_eligible_for_inference") is False,
             f"{run_id}: artifact is not marked as eligible formal output", errors)
    artifact_manifest = artifact.get("artifact_manifest")
    _require(isinstance(artifact_manifest, dict), f"{run_id}: artifact_manifest is missing", errors)
    if isinstance(artifact_manifest, dict):
        _require(artifact_manifest.get("inputs") == manifest.get("inputs"),
                 f"{run_id}: artifact input hashes differ from batch manifest", errors)
        _require(artifact_manifest.get("sources") == manifest.get("source"),
                 f"{run_id}: artifact source hashes differ from batch manifest", errors)
        _require(isinstance(artifact_manifest.get("environment"), dict),
                 f"{run_id}: artifact environment metadata is missing", errors)
    config = artifact.get("config", {})
    _require(isinstance(config, dict), f"{run_id}: config block is missing", errors)
    fraction_text = run_id.split("-")[1] if run_id.startswith("split-") else ""
    seed_text = run_id.split("-")[-1] if run_id.startswith("split-") else ""
    try:
        expected_fraction, expected_seed = float(fraction_text), int(seed_text)
    except ValueError:
        expected_fraction, expected_seed = None, None
    _require(expected_fraction is not None and expected_seed is not None,
             f"{run_id}: malformed run identifier", errors)
    if isinstance(config, dict) and expected_fraction is not None:
        try:
            identifier_matches = (float(config.get("fraction", -1)) == expected_fraction
                                  and config.get("seed") == expected_seed)
        except (TypeError, ValueError):
            identifier_matches = False
        _require(identifier_matches, f"{run_id}: config identifier mismatch", errors)
        for key, value in RUN_REQUIRED_CONFIG.items():
            _require(config.get(key) == value, f"{run_id}: config {key} mismatch", errors)
    reproducibility = artifact.get("reproducibility", {})
    _require(isinstance(reproducibility, dict), f"{run_id}: reproducibility block is missing", errors)
    if not isinstance(reproducibility, dict):
        reproducibility = {}
    _check_worlds(reproducibility, run_id, expected_seed, errors)
    arms = artifact.get("arms", {})
    _require(isinstance(arms, dict) and set(arms) == set(ARMS), f"{run_id}: arm set mismatch", errors)
    if not isinstance(arms, dict):
        arms = {}
    execution_order = reproducibility.get("arm_execution_order")
    _require(isinstance(execution_order, list) and sorted(execution_order) == sorted(ARMS),
             f"{run_id}: arm execution order is not a permutation", errors)
    for name in ARMS:
        arm = arms.get(name)
        if isinstance(arm, dict):
            _check_arm(arm, name, run_id, errors)
    tables = artifact.get("tables", {})
    if not isinstance(tables, dict):
        tables = {}
    node_scores = tables.get("node_scores")
    _require(isinstance(node_scores, list) and bool(node_scores),
             f"{run_id}: node score table is missing", errors)
    node_universe = []
    if isinstance(node_scores, list):
        node_universe = [str(row.get("node")) for row in node_scores if isinstance(row, dict)]
        _require(len(node_universe) == len(node_scores) and len(set(node_universe)) == len(node_universe),
                 f"{run_id}: node score table has duplicate or malformed nodes", errors)
        canonical_node_universe = sorted(node_universe)
        _require(reproducibility.get("canonical_node_universe_sha256") == stable_digest(canonical_node_universe),
                 f"{run_id}: canonical node-universe digest mismatch", errors)
        _require(reproducibility.get("canonical_node_universe_digest_algorithm") == "sha256(canonical JSON list)",
                 f"{run_id}: node-universe digest algorithm is missing or changed", errors)
        _require(reproducibility.get("node_universe_count") == len(canonical_node_universe),
                 f"{run_id}: node-universe count mismatch", errors)
        _require(reproducibility.get("node_universe_first") == (canonical_node_universe[0] if canonical_node_universe else None),
                 f"{run_id}: node-universe first-node marker mismatch", errors)
        _require(reproducibility.get("node_universe_last") == (canonical_node_universe[-1] if canonical_node_universe else None),
                 f"{run_id}: node-universe last-node marker mismatch", errors)
        node_set = set(node_universe)
        for name in ARMS:
            arm = arms.get(name)
            if isinstance(arm, dict):
                membership = [str(node) for node in arm.get("membership_rank_order", [])]
                _require(set(membership).issubset(node_set),
                         f"{run_id}/{name}: candidate outside node universe", errors)
    if isinstance(arms.get("uniform_random"), dict) and node_universe and expected_seed is not None:
        random_seed = world_sequence(expected_seed, RANDOM_MEMBERSHIP_NAMESPACE, 1)[0]
        expected_random = np.random.default_rng(random_seed).choice(
            np.array(sorted(node_universe), dtype=object), size=POOL_SIZE, replace=False
        ).tolist()
        observed_random = list(map(str, arms["uniform_random"].get("membership_rank_order", [])))
        _require(observed_random == expected_random,
                 f"{run_id}: uniform-random membership does not match namespace {RANDOM_MEMBERSHIP_NAMESPACE}", errors)
        _require(reproducibility.get("random_membership_seed") == random_seed,
                 f"{run_id}: random-membership seed mismatch", errors)
    if isinstance(execution_order, list) and expected_seed is not None:
        arm_seed = world_sequence(expected_seed, ARM_ORDER_NAMESPACE, 1)[0]
        expected_order = [ARMS[index] for index in np.random.default_rng(arm_seed).permutation(len(ARMS))]
        _require(execution_order == expected_order,
                 f"{run_id}: arm execution order does not match namespace {ARM_ORDER_NAMESPACE}", errors)
        _require(reproducibility.get("arm_order_seed") == arm_seed,
                 f"{run_id}: arm-order seed mismatch", errors)
    _require(isinstance(tables.get("probabilities"), list) and bool(tables.get("probabilities")),
             f"{run_id}: probability table is missing", errors)
    probabilities = tables.get("probabilities")
    if isinstance(probabilities, list):
        edge_keys = []
        for row in probabilities:
            _require(isinstance(row, dict) and all(key in row for key in ("source", "target", "probability")),
                     f"{run_id}: malformed probability row", errors)
            if isinstance(row, dict):
                edge_keys.append((str(row.get("source")), str(row.get("target"))))
                _require(is_finite(row.get("probability")) and 0.0 <= float(row["probability"]) <= 1.0,
                         f"{run_id}: probability outside [0,1] or non-finite", errors)
        _require(len(edge_keys) == len(set(edge_keys)), f"{run_id}: duplicate probability edge", errors)
    if isinstance(node_scores, list):
        for row in node_scores:
            _require(isinstance(row, dict) and all(key in row for key in ("node", "community", "gnn_prior", "weighted_out_degree", "pagerank")),
                     f"{run_id}: malformed node score row", errors)
            if isinstance(row, dict):
                for key in ("gnn_prior", "weighted_out_degree", "pagerank"):
                    _require(is_finite(row.get(key)), f"{run_id}: non-finite node score {key}", errors)
    return artifact


def _validate_metrics(study_dir: Path, artifacts: dict[str, dict], errors: list[str]) -> list[dict[str, str]]:
    path = study_dir / "method_metrics.csv"
    if not path.is_file():
        errors.append("method_metrics.csv is missing")
        return []
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if rows:
        _require(METRIC_COLUMNS.issubset(rows[0]), "method_metrics.csv is missing required columns", errors)
    expected_ids = expected_run_ids()
    _require(len(rows) == len(expected_ids) * len(ARMS),
             f"method_metrics.csv must contain {len(expected_ids) * len(ARMS)} rows", errors)
    seen = {(row.get("run_id"), row.get("method")) for row in rows}
    _require(len(seen) == len(rows), "method_metrics.csv contains duplicate run/method rows", errors)
    _require({row.get("run_id") for row in rows} == expected_ids,
             "method_metrics.csv run set mismatch", errors)
    _require({row.get("method") for row in rows} == set(ARMS),
             "method_metrics.csv arm set mismatch", errors)
    for row in rows:
        run_id, method = row.get("run_id"), row.get("method")
        artifact = artifacts.get(str(run_id))
        _require(artifact is not None, f"metrics row has no artifact: {run_id}", errors)
        if artifact is None or method not in ARMS:
            continue
        _require(row.get("not_eligible_for_inference", "").lower() in {"false", "0"},
                 f"{run_id}/{method}: metrics row is marked ineligible", errors)
        evaluation = artifact["arms"][method]["reporting_evaluation"]
        selection = artifact["arms"][method]["selection"]
        for field, key in (("mean_spread", "mean_spread"), ("spread_std", "spread_std"),
                           ("robust_objective", "robust_objective"), ("community_coverage", "community_coverage")):
            try:
                _require(round(float(row[field]), 6) == round(float(evaluation[key]), 6),
                         f"{run_id}/{method}: metrics mismatch for {field}", errors)
            except (KeyError, TypeError, ValueError):
                errors.append(f"{run_id}/{method}: invalid metric {field}")
        for field, values, key in (
            ("selection_mean_spread", selection, "mean_spread"),
            ("selection_spread_std", selection, "spread_std"),
            ("selection_robust_objective", selection, "robust_objective"),
            ("selection_community_coverage", selection, "community_coverage"),
        ):
            try:
                _require(round(float(row[field]), 6) == round(float(values[key]), 6),
                         f"{run_id}/{method}: metrics mismatch for {field}", errors)
            except (KeyError, TypeError, ValueError):
                errors.append(f"{run_id}/{method}: invalid metric {field}")
        try:
            _require(json.loads(row["top_k"]) == evaluation["top_k"],
                     f"{run_id}/{method}: metrics mismatch for top_k", errors)
            _require(int(row["candidate_count"]) == int(artifact["arms"][method]["candidate_count"]),
                     f"{run_id}/{method}: metrics mismatch for candidate_count", errors)
            _require(int(row["random_seed"]) == int(artifact["config"]["seed"]),
                     f"{run_id}/{method}: metrics mismatch for random_seed", errors)
            _require(float(row["train_fraction"]) == float(artifact["config"]["fraction"]),
                     f"{run_id}/{method}: metrics mismatch for train_fraction", errors)
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            errors.append(f"{run_id}/{method}: invalid identity or top_k metric")
        arm = artifact["arms"][method]
        for field in ("membership_generation_seconds", "candidate_sorting_seconds", "search_seconds",
                      "selection_score_seconds", "evaluation_seconds", "total_arm_seconds"):
            try:
                _require(round(float(row[field]), 6) == round(float(arm[field]), 6),
                         f"{run_id}/{method}: metrics mismatch for {field}", errors)
            except (KeyError, TypeError, ValueError):
                errors.append(f"{run_id}/{method}: invalid timing metric {field}")
        for field in ("robust_objective", "mean_spread", "spread_std", "community_coverage"):
            _require(is_finite(row.get(field)), f"{run_id}/{method}: non-finite metric {field}", errors)
    return rows


def _comparisons(rows: list[dict[str, str]]) -> dict[str, list[dict[str, object]]]:
    indexed = {(row["run_id"], row["method"]): row for row in rows}
    families = {
        "primary_gnn_vs_weighted_out_degree": ["weighted_out_degree"],
        "auxiliary_gnn_vs_pagerank_random": ["pagerank", "uniform_random"],
    }
    result: dict[str, list[dict[str, object]]] = {}
    for family, comparators in families.items():
        entries = []
        for fraction in FRACTIONS:
            for comparator in comparators:
                differences = []
                run_ids = []
                for seed in SEEDS:
                    run_id = f"split-{fraction:.2f}-seed-{seed}"
                    gnn = float(indexed[(run_id, "gnn_prior")]["robust_objective"])
                    baseline = float(indexed[(run_id, comparator)]["robust_objective"])
                    differences.append(round(gnn - baseline, 6))
                    run_ids.append(run_id)
                entries.append({
                    "fraction": fraction,
                    "reference": "gnn_prior",
                    "comparator": comparator,
                    "run_ids": run_ids,
                    **paired_summary(differences),
                })
        adjusted = holm_adjust([float(entry["exact_two_sided_sign_flip_p"]) for entry in entries])
        for entry, adjusted_p in zip(entries, adjusted):
            entry["holm_adjusted_p"] = adjusted_p
        result[family] = entries
    return result


def validate(study_dir: Path) -> dict[str, object]:
    errors: list[str] = []
    manifest_path = study_dir / "manifest.json"
    if not manifest_path.is_file():
        return {"status": "FAIL", "errors": ["manifest.json is missing"], "comparisons": {}}
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "errors": [f"manifest.json unreadable: {exc}"], "comparisons": {}}
    _require(manifest.get("study_version") == STUDY, "manifest study_version mismatch", errors)
    _require(manifest.get("artifact_schema") == ARTIFACT_SCHEMA, "manifest artifact_schema mismatch", errors)
    _require(manifest.get("formal_batch") is True and manifest.get("smoke_test") is False,
             "manifest is not a complete formal batch", errors)
    _require(manifest.get("not_eligible_for_inference") is False,
             "manifest is marked ineligible for inference", errors)
    expected_ids = expected_run_ids()
    _require(set(manifest.get("expected_run_ids", [])) == expected_ids,
             "manifest expected_run_ids mismatch", errors)
    _require(set(manifest.get("runs", {})) == {f"{run_id}.json" for run_id in expected_ids},
             "manifest run hash set mismatch", errors)
    _require(isinstance(manifest.get("inputs"), dict) and len(manifest["inputs"]) == 3,
             "manifest input hashes are incomplete", errors)
    _require(isinstance(manifest.get("source"), dict) and len(manifest["source"]) >= 8,
             "manifest source hashes are incomplete", errors)
    for category in ("inputs", "source"):
        values = manifest.get(category, {})
        if isinstance(values, dict):
            for name, digest in values.items():
                _require(isinstance(digest, str) and len(digest) == 64 and all(char in "0123456789abcdef" for char in digest.lower()),
                         f"manifest {category} hash is malformed: {name}", errors)
    try:
        expected_inputs = expected_input_hashes()
        _require(manifest.get("inputs") == expected_inputs,
                 "manifest input hashes do not match the frozen Higgs inputs", errors)
        for name, expected_digest in expected_inputs.items():
            path = DATASET_DIR / name
            _require(path.is_file() and sha256(path) == expected_digest,
                     f"current Higgs input hash mismatch: {name}", errors)
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"unable to verify frozen Higgs input hashes: {exc}")
    source_paths = expected_source_paths()
    _require(set(manifest.get("source", {})) == set(source_paths),
             "manifest source hash set does not match the formal source set", errors)
    for name, path in source_paths.items():
        expected_digest = manifest.get("source", {}).get(name)
        _require(path.is_file() and sha256(path) == expected_digest,
                 f"current source hash mismatch: {name}", errors)
    protocol_entries = manifest.get("protocol", {})
    _require(isinstance(protocol_entries, dict) and len(protocol_entries) == 1,
             "manifest protocol hash is missing", errors)
    for protocol_name, digest in protocol_entries.items():
        protocol_path = study_dir / protocol_name
        _require(protocol_path.is_file() and sha256(protocol_path) == digest,
                 f"protocol copy/hash mismatch: {protocol_name}", errors)

    artifact_paths = {path.stem: path for path in study_dir.glob("split-*.json")}
    _require(set(artifact_paths) == expected_ids, "artifact run set mismatch", errors)
    artifacts: dict[str, dict] = {}
    for run_id in sorted(expected_ids):
        artifact = _validate_artifact(artifact_paths[run_id], manifest, errors) if run_id in artifact_paths else None
        if artifact is not None:
            artifacts[run_id] = artifact
    rows = _validate_metrics(study_dir, artifacts, errors) if len(artifacts) == len(expected_ids) else []
    comparisons = _comparisons(rows) if not errors and len(rows) == len(expected_ids) * len(ARMS) else {}
    return {"status": "PASS" if not errors else "FAIL", "errors": errors, "comparisons": comparisons}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--study-dir", required=True)
    args = parser.parse_args()
    report = validate(Path(args.study_dir))
    print(json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
