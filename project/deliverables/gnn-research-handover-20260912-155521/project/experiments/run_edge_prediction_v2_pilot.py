"""Run one preregistered v2 edge-model configuration under isolated time splits."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import random
import sys

os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
import torch

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from app.graph import build_snapshot, time_split
from app.model_v2 import predict_edge_probabilities_v2, train_edge_model_v2
from app.validation import load_dataset


def set_determinism(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True)


def sample_never_observed(node_count: int, observed: set[tuple[int, int]], count: int, seed: int) -> list[tuple[int, int]]:
    if count > node_count * (node_count - 1) - len(observed):
        raise ValueError("Not enough never-observed directed pairs for balanced evaluation")
    rng = np.random.default_rng(seed)
    result: list[tuple[int, int]] = []
    selected: set[tuple[int, int]] = set()
    while len(result) < count:
        pair = (int(rng.integers(node_count)), int(rng.integers(node_count)))
        if pair[0] != pair[1] and pair not in observed and pair not in selected:
            result.append(pair)
            selected.add(pair)
    return result


def ece(labels: np.ndarray, scores: np.ndarray) -> float:
    value = 0.0
    boundaries = np.linspace(0, 1, 11)
    for index in range(10):
        mask = (scores >= boundaries[index]) & (scores <= boundaries[index + 1] if index == 9 else scores < boundaries[index + 1])
        if mask.any():
            value += abs(float(labels[mask].mean()) - float(scores[mask].mean())) * float(mask.mean())
    return value


def metrics(labels: np.ndarray, scores: np.ndarray) -> dict[str, float]:
    return {
        "auc": float(roc_auc_score(labels, scores)),
        "average_precision": float(average_precision_score(labels, scores)),
        "brier": float(brier_score_loss(labels, scores)),
        "ece_10_bins": float(ece(labels, scores)),
        "inverse_probability_auc": float(roc_auc_score(labels, 1.0 - scores)),
    }


def indexed_pairs(frame: object, index: dict[str, int]) -> list[tuple[int, int]]:
    return [(index[str(row.src)], index[str(row.dst)]) for _, row in frame.drop_duplicates(["src", "dst"]).iterrows()]


def train_on_window(
    dataset: object, history_edges: object, supervised_edges: object, config: dict[str, object], seed: int
) -> tuple[object, object, dict[str, int]]:
    snapshot = build_snapshot(dataset, history_edges)
    index = {node: position for position, node in enumerate(snapshot.node_ids)}
    model_edges = [
        (index[str(row.src)], index[str(row.dst)], float(snapshot.graph[str(row.src)][str(row.dst)]["weight"]))
        for _, row in history_edges.drop_duplicates(["src", "dst"]).iterrows()
    ]
    supervised_pairs = indexed_pairs(supervised_edges, index)
    set_determinism(seed)
    model, embeddings, _ = train_edge_model_v2(
        snapshot.features, model_edges, seed=seed, supervised_positive_pairs=supervised_pairs, **config
    )
    return model, embeddings, index


def labeled_scores(model: object, embeddings: object, positives: list[tuple[int, int]], observed: set[tuple[int, int]], seed: int, calibrator: object | None = None) -> tuple[np.ndarray, np.ndarray]:
    negatives = sample_never_observed(int(embeddings.shape[0]), observed, len(positives), seed)
    labels = np.concatenate([np.ones(len(positives), dtype=np.int8), np.zeros(len(negatives), dtype=np.int8)])
    scores = predict_edge_probabilities_v2(model, embeddings, positives + negatives).astype(np.float64)
    if calibrator is not None:
        scores = calibrator.predict(scores)
    return labels, scores


def run_one(dataset: object, all_observed: set[tuple[str, str]], fraction: float, seed: int, config: dict[str, object], mode: str) -> dict[str, object]:
    outer_train, outer_test = time_split(dataset.edges, fraction)
    first_80 = max(1, int(len(outer_train) * 0.80))
    if mode == "selection":
        fit_end = max(1, int(len(outer_train) * 0.64))
        history_end = max(1, int(fit_end * 0.80))
        history_edges = outer_train.iloc[:history_end].copy()
        supervised_edges = outer_train.iloc[history_end:fit_end].copy()
        evaluation_edges = outer_train.iloc[fit_end:first_80].copy()
        model, embeddings, index = train_on_window(dataset, history_edges, supervised_edges, config, seed)
        observed = {(index[source], index[target]) for source, target in all_observed}
        positives = indexed_pairs(evaluation_edges, index)
        labels, scores = labeled_scores(model, embeddings, positives, observed, seed)
        return {"mode": mode, "train_fraction": fraction, "seed": seed, "config": config, "metrics": metrics(labels, scores), "positives": len(positives)}

    history_end = max(1, int(first_80 * 0.80))
    history_edges = outer_train.iloc[:history_end].copy()
    supervised_edges = outer_train.iloc[history_end:first_80].copy()
    calibration_edges = outer_train.iloc[first_80:].copy()
    model, embeddings, index = train_on_window(dataset, history_edges, supervised_edges, config, seed)
    observed = {(index[source], index[target]) for source, target in all_observed}
    calibration_positive = indexed_pairs(calibration_edges, index)
    calibration_labels, calibration_scores = labeled_scores(model, embeddings, calibration_positive, observed, seed)
    calibrator = IsotonicRegression(out_of_bounds="clip").fit(calibration_scores, calibration_labels)
    test_positive = indexed_pairs(outer_test, index)
    test_labels, test_scores = labeled_scores(model, embeddings, test_positive, observed, seed)
    calibrated_scores = calibrator.predict(test_scores)
    return {
        "mode": mode,
        "train_fraction": fraction,
        "seed": seed,
        "config": config,
        "calibration_metrics": metrics(calibration_labels, calibrator.predict(calibration_scores)),
        "metrics": metrics(test_labels, calibrated_scores),
        "positives": len(test_positive),
        "calibration_positives": len(calibration_positive),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--mode", choices=("selection", "outer_test"), required=True)
    parser.add_argument("--fractions", type=float, nargs="+", default=[0.60, 0.65, 0.70])
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 43, 44, 45, 46, 47, 48, 49, 50, 51])
    parser.add_argument("--epochs", type=int, required=True)
    parser.add_argument("--hidden-channels", type=int, required=True)
    parser.add_argument("--layers", type=int, choices=(1, 2), required=True)
    parser.add_argument("--learning-rate", type=float, required=True)
    parser.add_argument("--decoder", choices=("concat_mlp", "bilinear"), required=True)
    args = parser.parse_args()
    output = Path(args.output_dir)
    if output.exists() and any(output.iterdir()):
        parser.error(f"Refusing to overwrite non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=False)
    dataset = load_dataset(args.dataset)
    all_observed = {(str(row.src), str(row.dst)) for _, row in dataset.edges.drop_duplicates(["src", "dst"]).iterrows()}
    config = {"epochs": args.epochs, "hidden_channels": args.hidden_channels, "layers": args.layers, "learning_rate": args.learning_rate, "decoder": args.decoder}
    results = []
    for fraction in args.fractions:
        for seed in args.seeds:
            result = run_one(dataset, all_observed, fraction, seed, config, args.mode)
            (output / f"split-{fraction:.2f}-seed-{seed}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
            results.append(result)
            print(f"split-{fraction:.2f}-seed-{seed}: AUC={result['metrics']['auc']:.4f}")
    report = {"mode": args.mode, "config": config, "runs": results}
    (output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
