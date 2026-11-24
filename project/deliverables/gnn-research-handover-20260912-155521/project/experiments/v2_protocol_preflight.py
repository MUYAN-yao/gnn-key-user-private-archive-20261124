"""Determinism preflight required by protocols/edge_prediction_v2_preregistration.md."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import random
import shutil
import sys

# CUDA requires this before the first CUDA context is created.
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG", ":4096:8")

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from app.graph import build_snapshot, time_split
from app.model import predict_edge_probabilities, train_edge_model
from app.validation import load_dataset


def configure_determinism(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True)


def train_scores(dataset: object, fraction: float, inner_ratio: float, seed: int, epochs: int) -> np.ndarray:
    fit_fraction = fraction * inner_ratio
    fit_edges, held_out = time_split(dataset.edges, fit_fraction)
    snapshot = build_snapshot(dataset, fit_edges)
    index = {node: position for position, node in enumerate(snapshot.node_ids)}
    model_edges = [
        (index[str(row.src)], index[str(row.dst)], float(snapshot.graph[str(row.src)][str(row.dst)]["weight"]))
        for _, row in fit_edges.drop_duplicates(["src", "dst"]).iterrows()
    ]
    pairs = [
        (index[str(row.src)], index[str(row.dst)])
        for _, row in held_out.drop_duplicates(["src", "dst"]).head(1000).iterrows()
    ]
    configure_determinism(seed)
    model, embeddings, _ = train_edge_model(snapshot.features, model_edges, epochs, seed)
    return predict_edge_probabilities(model, embeddings, pairs)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--outer-fraction", type=float, default=0.60)
    parser.add_argument("--inner-ratio", type=float, default=0.80)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--epochs", type=int, default=10)
    args = parser.parse_args()
    output = Path(args.output_dir)
    if output.exists() and any(output.iterdir()):
        parser.error(f"Refusing to overwrite non-empty preflight directory: {output}")
    output.mkdir(parents=True, exist_ok=False)
    dataset = load_dataset(args.dataset)
    protocol = Path(__file__).parents[1] / "protocols/edge_prediction_v2_preregistration.md"
    shutil.copy2(protocol, output / protocol.name)
    try:
        first = train_scores(dataset, args.outer_fraction, args.inner_ratio, args.seed, args.epochs)
        second = train_scores(dataset, args.outer_fraction, args.inner_ratio, args.seed, args.epochs)
        max_abs_difference = float(np.max(np.abs(first - second))) if len(first) else 0.0
        result = {
            "status": "pass" if max_abs_difference <= 1e-7 else "fail",
            "max_abs_prediction_difference": max_abs_difference,
            "threshold": 1e-7,
            "device": os.environ.get("RIL_DEVICE", "auto"),
            "cuda_available": torch.cuda.is_available(),
            "outer_fraction": args.outer_fraction,
            "inner_ratio": args.inner_ratio,
            "seed": args.seed,
            "epochs": args.epochs,
            "scored_held_out_pairs": int(len(first)),
        }
    except Exception as error:
        result = {
            "status": "error",
            "error_type": type(error).__name__,
            "error": str(error),
            "device": os.environ.get("RIL_DEVICE", "auto"),
            "cuda_available": torch.cuda.is_available(),
        }
    (output / "determinism_preflight.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False))
    if result["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
