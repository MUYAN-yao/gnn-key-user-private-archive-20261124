"""Run the separately preregistered fixed-candidate Higgs v2-T0 study."""
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
from app.pipeline_v2_t0 import run_analysis_v2_t0
from app.validation import load_dataset


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def expected_higgs_hashes(manifest_path: Path) -> dict[str, str]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for study in manifest["studies"]:
        if study["study_directory"].endswith("large-robust-greedy-higgs-50000-v1"):
            return {Path(path).name: value for path, value in study["dataset_sha256"].items()}
    raise ValueError("Frozen Higgs 50k study is missing from the provenance manifest")


def method_rows(run_id: str, result: dict) -> list[dict]:
    methods = {result["result"]["method"]: result["result"], **result["baselines"]}
    return [
        {
            "run_id": run_id,
            "train_fraction": result["config"]["train_fraction"],
            "random_seed": result["config"]["random_seed"],
            "method": name,
            "mean_spread": values["mean_spread"],
            "spread_std": values["spread_std"],
            "robust_objective": values["robust_objective"],
            "community_coverage": values["community_coverage"],
            "runtime_seconds": result["runtime_seconds"],
        }
        for name, values in methods.items()
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--fractions", type=float, nargs="+", default=[0.60, 0.65, 0.70])
    parser.add_argument("--seeds", type=int, nargs="+", default=list(range(42, 52)))
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--frozen-manifest", default="reproducibility/frozen-study-manifest-v1.json")
    args = parser.parse_args()
    if any(not 0.50 <= fraction <= 0.90 for fraction in args.fractions):
        parser.error("Each --fractions value must be between 0.50 and 0.90.")
    dataset_dir = Path(args.dataset)
    input_hashes = {name: sha256(dataset_dir / name) for name in ("nodes.csv", "edges.csv", "cascades.csv")}
    frozen_hashes = expected_higgs_hashes(Path(args.frozen_manifest))
    if input_hashes != frozen_hashes:
        raise ValueError("Dataset hashes differ from the frozen Higgs 50k manifest")
    dataset = load_dataset(dataset_dir)
    output = Path(args.output_dir)
    if output.exists() and any(output.iterdir()) and not args.resume:
        parser.error(f"Refusing to overwrite non-empty output directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    protocol = Path(__file__).parents[1] / "protocols" / "influence_v2_t0_preregistration.md"
    protocol_copy = output / protocol.name
    if not protocol_copy.exists():
        shutil.copy2(protocol, protocol_copy)
    rows: list[dict] = []
    run_hashes: dict[str, str] = {}
    for fraction in args.fractions:
        for seed in args.seeds:
            run_id = f"split-{fraction:.2f}-seed-{seed}"
            run_path = output / f"{run_id}.json"
            if run_path.exists():
                if not args.resume:
                    raise FileExistsError(f"Refusing to replace existing run: {run_path}")
                result = json.loads(run_path.read_text(encoding="utf-8"))
            else:
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
                    candidate_pool_size=120,
                )
                result = run_analysis_v2_t0(dataset, config)
                run_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
                print(run_id)
            rows.extend(method_rows(run_id, result))
            run_hashes[run_path.name] = sha256(run_path)
    with (output / "method_metrics.csv").open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]) if rows else [])
        writer.writeheader()
        writer.writerows(rows)
    manifest = {
        "protocol": {protocol.name: sha256(protocol)},
        "inputs": input_hashes,
        "frozen_input_verification": {"manifest": str(Path(args.frozen_manifest)), "verified": True},
        "source": {
            "pipeline_v2_t0.py": sha256(Path(__file__).parents[1] / "backend" / "app" / "pipeline_v2_t0.py"),
            "model_v2.py": sha256(Path(__file__).parents[1] / "backend" / "app" / "model_v2.py"),
            "run_rolling_study_v2_t0.py": sha256(Path(__file__)),
        },
        "runs": run_hashes,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
