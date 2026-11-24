"""Audit temporal edge-prediction validity without touching frozen study outputs.

The study pipeline trains an encoder to reconstruct edges observed before a
temporal cutoff, then uses its scores on later edges.  This script repeats
that isolated model step for explicit diagnostics: train reconstruction,
future-edge prediction, calibration, and the AUC of the inverted score.  The
last metric distinguishes a genuinely weak ranker from a score-direction
reversal.

Example:
    python experiments/audit_edge_prediction.py \
        --dataset data/processed/higgs-twitter/pilot-50000 \
        --output-dir audits/higgs-edge-prediction-v1 \
        --fractions 0.60 0.65 0.70 --seeds 42 43 44 45 46 47 48 49 50 51 \
        --epochs 10
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import sys
import time

import numpy as np
import torch
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from app.graph import build_snapshot, time_split
from app.model import predict_edge_probabilities, train_edge_model
from app.validation import load_dataset


def sample_non_edges(
    node_count: int, excluded: set[tuple[int, int]], count: int, seed: int
) -> list[tuple[int, int]]:
    """Match the pipeline's balanced absent-pair sampling, with an exhaustion guard."""
    available = node_count * (node_count - 1) - len(excluded)
    if count > available:
        raise ValueError(f"Requested {count} negatives but only {available} non-self absent pairs remain")
    rng = np.random.default_rng(seed)
    negatives: list[tuple[int, int]] = []
    selected: set[tuple[int, int]] = set()
    while len(negatives) < count:
        pair = (int(rng.integers(node_count)), int(rng.integers(node_count)))
        if pair[0] != pair[1] and pair not in excluded and pair not in selected:
            negatives.append(pair)
            selected.add(pair)
    return negatives


def expected_calibration_error(labels: np.ndarray, predicted: np.ndarray, bins: int = 10) -> float:
    boundaries = np.linspace(0, 1, bins + 1)
    error = 0.0
    for index in range(bins):
        if index == bins - 1:
            mask = (predicted >= boundaries[index]) & (predicted <= boundaries[index + 1])
        else:
            mask = (predicted >= boundaries[index]) & (predicted < boundaries[index + 1])
        if mask.any():
            error += abs(float(labels[mask].mean()) - float(predicted[mask].mean())) * float(mask.mean())
    return error


def score_metrics(labels: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    inverted = 1.0 - predicted
    return {
        "auc": float(roc_auc_score(labels, predicted)),
        "average_precision": float(average_precision_score(labels, predicted)),
        "brier": float(brier_score_loss(labels, predicted)),
        "ece_10_bins": float(expected_calibration_error(labels, predicted)),
        "inverse_probability_auc": float(roc_auc_score(labels, inverted)),
        "mean_positive_score": float(predicted[labels == 1].mean()),
        "mean_negative_score": float(predicted[labels == 0].mean()),
    }


def evaluate_pairs(
    model: object,
    embeddings: torch.Tensor,
    positives: list[tuple[int, int]],
    negatives: list[tuple[int, int]],
) -> dict[str, object]:
    labels = np.concatenate([np.ones(len(positives), dtype=np.int8), np.zeros(len(negatives), dtype=np.int8)])
    predicted = predict_edge_probabilities(model, embeddings, positives + negatives).astype(np.float64)
    return {
        "positive_edges": len(positives),
        "negative_edges": len(negatives),
        **score_metrics(labels, predicted),
    }


def audit_run(dataset: object, fraction: float, seed: int, epochs: int) -> dict[str, object]:
    train_edges, future_edges = time_split(dataset.edges, fraction)
    snapshot = build_snapshot(dataset, train_edges)
    index = {node: position for position, node in enumerate(snapshot.node_ids)}
    train_model_edges = [
        (index[str(row.src)], index[str(row.dst)], float(snapshot.graph[str(row.src)][str(row.dst)]["weight"]))
        for _, row in train_edges.drop_duplicates(["src", "dst"]).iterrows()
    ]
    train_pairs = [(source, target) for source, target, _ in train_model_edges]
    future_pairs = [
        (index[str(row.src)], index[str(row.dst)])
        for _, row in future_edges.drop_duplicates(["src", "dst"]).iterrows()
    ]
    if not train_pairs or not future_pairs:
        raise ValueError("Temporal split must contain at least one unique training and future edge")

    started = time.perf_counter()
    model, embeddings, uses_pyg = train_edge_model(snapshot.features, train_model_edges, epochs, seed)
    train_excluded = set(train_pairs)
    future_excluded = train_excluded | set(future_pairs)
    train_negatives = sample_non_edges(len(index), train_excluded, len(train_pairs), seed)
    # This exactly follows the frozen pipeline: negatives exclude both past and future positives.
    future_negatives = sample_non_edges(len(index), future_excluded, len(future_pairs), seed)
    return {
        "train_fraction": fraction,
        "random_seed": seed,
        "epochs": epochs,
        "training_cutoff": snapshot.cutoff,
        "node_count": len(index),
        "training_event_count": int(len(train_edges)),
        "future_event_count": int(len(future_edges)),
        "unique_training_edges": len(train_pairs),
        "unique_future_edges": len(future_pairs),
        "backend": "torch-geometric GATv2" if uses_pyg else "PyTorch temporal GAT fallback",
        "train_reconstruction": evaluate_pairs(model, embeddings, train_pairs, train_negatives),
        "future_edge_prediction": evaluate_pairs(model, embeddings, future_pairs, future_negatives),
        "runtime_seconds": time.perf_counter() - started,
    }


def mean_metrics(runs: list[dict[str, object]], section: str) -> dict[str, float]:
    metric_names = [
        "auc", "average_precision", "brier", "ece_10_bins", "inverse_probability_auc",
        "mean_positive_score", "mean_negative_score",
    ]
    return {
        name: float(np.mean([run[section][name] for run in runs]))
        for name in metric_names
    }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, help="Directory containing nodes.csv, edges.csv, cascades.csv")
    parser.add_argument("--output-dir", required=True, help="New directory for this audit's artifacts")
    parser.add_argument("--fractions", type=float, nargs="+", default=[0.60, 0.65, 0.70])
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 43, 44, 45, 46, 47, 48, 49, 50, 51])
    parser.add_argument("--epochs", type=int, default=10)
    args = parser.parse_args()
    if any(not 0.0 < fraction < 1.0 for fraction in args.fractions):
        parser.error("Each fraction must be strictly between zero and one.")
    if args.epochs < 1:
        parser.error("--epochs must be positive.")

    dataset_path = Path(args.dataset)
    output_dir = Path(args.output_dir)
    if output_dir.exists() and any(output_dir.iterdir()):
        parser.error(f"Refusing to overwrite non-empty audit directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=False)
    dataset = load_dataset(dataset_path)
    runs: list[dict[str, object]] = []
    for fraction in args.fractions:
        for seed in args.seeds:
            run = audit_run(dataset, fraction, seed, args.epochs)
            run_id = f"split-{fraction:.2f}-seed-{seed}"
            (output_dir / f"{run_id}.json").write_text(json.dumps(run, ensure_ascii=False, indent=2), encoding="utf-8")
            runs.append(run)
            future_auc = run["future_edge_prediction"]["auc"]
            print(f"{run_id}: future AUC={future_auc:.4f}")

    report = {
        "purpose": "Independent temporal edge-probability audit; frozen study outputs are read-only and were not modified.",
        "protocol": {
            "dataset": str(dataset_path),
            "dataset_sha256": {name: sha256_file(dataset_path / name) for name in ("nodes.csv", "edges.csv", "cascades.csv")},
            "fractions": args.fractions,
            "seeds": args.seeds,
            "epochs": args.epochs,
            "negative_sampling": "Balanced uniformly sampled directed non-edges; future negatives exclude training and future positives, matching pipeline.py.",
            "train_evaluation": "Observed unique training edges versus sampled absent directed pairs.",
            "future_evaluation": "Observed unique future edges versus sampled absent directed pairs.",
            "inverse_probability_auc": "AUC after replacing every probability p with 1-p; values above 0.5 indicate score-direction reversal.",
        },
        "environment": {"python": sys.version, "platform": platform.platform(), "torch": torch.__version__, "cuda_available": torch.cuda.is_available()},
        "runs": runs,
        "by_fraction": {
            f"{fraction:.2f}": {
                "run_count": sum(run["train_fraction"] == fraction for run in runs),
                "train_reconstruction_mean": mean_metrics([run for run in runs if run["train_fraction"] == fraction], "train_reconstruction"),
                "future_edge_prediction_mean": mean_metrics([run for run in runs if run["train_fraction"] == fraction], "future_edge_prediction"),
            }
            for fraction in args.fractions
        },
    }
    (output_dir / "audit_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {output_dir / 'audit_report.json'}")


if __name__ == "__main__":
    main()
