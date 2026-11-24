"""Run the preregistered timestamp-grouped Higgs v2-T0b study."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
import shutil
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "backend"))

from app.contracts import AnalysisConfig
from app.pipeline_v2_t0b import run_analysis_v2_t0b
from app.validation import load_dataset
from run_rolling_study_v2_t0 import expected_higgs_hashes, method_rows, sha256


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--fractions", type=float, nargs="+", default=[0.60, 0.65, 0.70])
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(42, 52)))
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--frozen-manifest", default="reproducibility/frozen-study-manifest-v1.json")
    args = parser.parse_args()
    dataset_dir = Path(args.dataset)
    input_hashes = {name: sha256(dataset_dir / name) for name in ("nodes.csv", "edges.csv", "cascades.csv")}
    if input_hashes != expected_higgs_hashes(Path(args.frozen_manifest)):
        raise ValueError("Dataset hashes differ from the frozen Higgs 50k manifest")
    output = Path(args.output_dir)
    if output.exists() and any(output.iterdir()) and not args.resume:
        parser.error(f"Refusing to overwrite non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    protocol = Path(__file__).parents[1] / "protocols" / "influence_v2_t0b_timestamp_preregistration.md"
    if not (output / protocol.name).exists():
        shutil.copy2(protocol, output / protocol.name)
    dataset = load_dataset(dataset_dir)
    rows: list[dict] = []
    hashes: dict[str, str] = {}
    for fraction in args.fractions:
        for seed in args.seeds:
            run_id = f"split-{fraction:.2f}-seed-{seed}"
            path = output / f"{run_id}.json"
            if path.exists():
                if not args.resume:
                    raise FileExistsError(f"Refusing to replace existing run: {path}")
                result = json.loads(path.read_text(encoding="utf-8"))
            else:
                result = run_analysis_v2_t0b(dataset, AnalysisConfig(seed_count=2, horizon=4, risk_lambda=0.35, community_weight=0.25, diffusion_model="ic", random_seed=seed, epochs=10, ants=3, iterations=2, simulations=20, train_fraction=fraction, optimizer="robust_greedy", candidate_pool_size=120))
                path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
                print(run_id)
            rows.extend(method_rows(run_id, result))
            hashes[path.name] = sha256(path)
    with (output / "method_metrics.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]) if rows else [])
        writer.writeheader(); writer.writerows(rows)
    manifest = {"protocol": {protocol.name: sha256(protocol)}, "inputs": input_hashes, "frozen_input_verification": {"manifest": str(Path(args.frozen_manifest)), "verified": True}, "source": {"pipeline_v2_t0b.py": sha256(Path(__file__).parents[1] / "backend" / "app" / "pipeline_v2_t0b.py"), "model_v2.py": sha256(Path(__file__).parents[1] / "backend" / "app" / "model_v2.py"), "run_rolling_study_v2_t0b.py": sha256(Path(__file__))}, "runs": hashes}
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
