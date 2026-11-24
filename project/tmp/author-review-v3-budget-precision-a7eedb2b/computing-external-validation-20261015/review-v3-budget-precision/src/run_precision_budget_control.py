"""Write-once post-hoc strict-PageRank budget sensitivity control.

Run ``--freeze-only`` before ``--execute``. The former creates an immutable
source manifest and reads no new utility values. The latter reuses the frozen full
reference/evaluation worlds and calculates only the two restricted PageRank arms.
"""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import time

import networkx as nx
import numpy as np
import pandas as pd

R = Path(__file__).resolve().parents[1]
B = R.parent
D = R / "supplement-pr-budget-precision"
sys.path.insert(0, str(B / "snapshot"))
import engine  # noqa: E402
import run_experiment as runner  # noqa: E402


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_once(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def manifest_expected() -> dict:
    return {
        "protocol.md": sha(D / "protocol.md"),
        "src/run_precision_budget_control.py": sha(Path(__file__)),
        "external_snapshot_manifest": sha(B / "snapshot/source_manifest.json"),
        "external_config.json": sha(B / "config.json"),
        "external_data_manifest.json": sha(B / "data/source_manifest.json"),
        "main_audit.json": sha(R / "audit/full_validation.json"),
        "v2_precision_manifest.json": sha(B / "review-v2/supplement-pr-precision/source_manifest.json"),
    }


def require_frozen_manifest() -> str:
    path = D / "source_manifest.json"
    if not path.exists():
        raise RuntimeError("run --freeze-only before calculating utility outputs")
    expected = manifest_expected()
    actual = json.loads(path.read_text(encoding="utf-8"))
    if actual != expected:
        raise RuntimeError("post-hoc source/protocol manifest mismatch")
    return sha(path)


def strict_ranking(graph_data: dict, tolerance: float) -> np.ndarray:
    nodes = graph_data["nodes"]
    graph = nx.DiGraph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(
        (nodes[int(source)], nodes[int(target)])
        for source, target in zip(graph_data["sources"], graph_data["targets"])
    )
    scores = nx.pagerank(graph, alpha=0.85, tol=tolerance, max_iter=1000, weight=None)
    return np.asarray(
        sorted(range(len(nodes)), key=lambda i: (-scores[nodes[i]], nodes[i])), dtype=np.int64
    )


def metadata_for_pools(graph_data: dict, ranking: np.ndarray, tighter: np.ndarray) -> dict:
    nodes = graph_data["nodes"]
    record = {}
    for name, count in (("pagerank_4k", 20), ("pagerank_5pct", int(np.ceil(.05 * len(nodes))))):
        strict = {nodes[i] for i in ranking[:count]}
        high_precision = {nodes[i] for i in tighter[:count]}
        default = {nodes[i] for i in graph_data["rankings"]["pagerank"][:count]}
        if strict != high_precision:
            raise RuntimeError(f"strict pool unstable at tighter tolerance: {graph_data['metadata']['dataset']} {name}")
        record[name] = {
            "candidate_count": count,
            "default_vs_strict_overlap": len(default & strict),
            "default_vs_strict_jaccard": len(default & strict) / len(default | strict),
            "strict_vs_tighter_same_pool": True,
            "strict_added_ids": sorted(strict - default),
            "strict_removed_ids": sorted(default - strict),
            "strict_candidate_ids": sorted(strict),
            "default_candidate_ids": sorted(default),
        }
    return record


def run_condition(cfg: dict, graph_data: dict, pool_meta: dict, dataset: str, path_id: int, worlds_count: int, frozen_hash: str) -> dict:
    stem = f"{dataset}__p{path_id}__w{worlds_count}"
    folder = D / "conditions"
    folder.mkdir(exist_ok=True)
    json_path = folder / f"{stem}.json"
    npz_path = folder / f"{stem}.npz"
    if json_path.exists() or npz_path.exists():
        raise FileExistsError(f"output already exists: {stem}")

    old_path = B / "results/main/conditions" / f"resolution__{dataset}__p{path_id}__w{worlds_count}__step.json"
    old = json.loads(old_path.read_text(encoding="utf-8"))
    if old["source_manifest_sha256"] != sha(B / "snapshot/source_manifest.json"):
        raise RuntimeError(f"frozen source mismatch in {old_path.name}")
    if old["graph"]["graph_sha256"] != graph_data["metadata"]["graph_sha256"]:
        raise RuntimeError(f"graph mismatch in {old_path.name}")

    selection_ids = engine.world_ids(dataset, path_id, "selection", worlds_count, cfg["namespace"])
    evaluation_ids = engine.world_ids(dataset, path_id, "evaluation", cfg["evaluation_worlds"], cfg["namespace"])
    if hashlib.sha256(selection_ids.tobytes()).hexdigest() != old["selection_world_sha256"]:
        raise RuntimeError(f"selection IDs mismatch in {old_path.name}")
    if hashlib.sha256(evaluation_ids.tobytes()).hexdigest() != old["evaluation_world_sha256"]:
        raise RuntimeError(f"evaluation IDs mismatch in {old_path.name}")
    if set(selection_ids) & set(evaluation_ids):
        raise RuntimeError("selection/evaluation world collision")

    started = time.perf_counter()
    worlds = engine.make_worlds(selection_ids, graph_data["sources"], graph_data["targets"], .01, 3, False)
    nodes = graph_data["nodes"]
    node_index = {node: i for i, node in enumerate(nodes)}
    output_arrays, arms = {}, {}
    with np.load(old_path.with_suffix(".npz")) as previous:
        if previous["full_evaluation"].shape != (cfg["evaluation_worlds"],):
            raise RuntimeError("unexpected frozen full-evaluation length")
        for method in ("pagerank_4k", "pagerank_5pct"):
            details = pool_meta[method]
            pool = np.asarray([node_index[node] for node in details["strict_candidate_ids"]], dtype=np.int64)
            default_pool = old["arms"][method]["candidate_ids"]
            if sorted(default_pool) != details["default_candidate_ids"]:
                raise RuntimeError(f"default pool mismatch: {stem} {method}")
            seeds, round_totals = engine.greedy(
                graph_data["indptr"], graph_data["targets"], worlds, pool, 5, 3
            )
            values = []
            for offset in range(0, len(evaluation_ids), 256):
                eval_worlds = engine.make_worlds(
                    evaluation_ids[offset:offset + 256], graph_data["sources"], graph_data["targets"], .01, 3, False
                )
                values.append(engine.evaluate(graph_data["indptr"], graph_data["targets"], eval_worlds, seeds, 3))
            evaluation = np.concatenate(values)
            selected = [nodes[i] for i in seeds]
            if set(selected) == set(old["arms"][method]["selected"]):
                if not np.array_equal(evaluation, previous[method + "_evaluation"]):
                    raise RuntimeError(f"same default seed set changed evaluation: {stem} {method}")
            if set(selected) == set(old["arms"]["full"]["selected"]):
                if not np.array_equal(evaluation, previous["full_evaluation"]):
                    raise RuntimeError(f"same full seed set changed evaluation: {stem} {method}")
            difference = evaluation - previous["full_evaluation"]
            default_difference = evaluation - previous[method + "_evaluation"]
            output_arrays[method + "_evaluation"] = evaluation
            output_arrays[method + "_round_totals"] = round_totals
            arms[method] = {
                "candidate_count": details["candidate_count"],
                "candidate_ids": details["strict_candidate_ids"],
                "selected": selected,
                "mean_spread": float(evaluation.mean()),
                "delta_vs_full": float(difference.mean()),
                "mc_se_vs_full": float(difference.std(ddof=1) / np.sqrt(len(difference))),
                "loss_percent": float(-100 * difference.mean() / (previous["full_evaluation"].mean() - 5)),
                "delta_vs_default": float(default_difference.mean()),
                "same_order_as_default": selected == old["arms"][method]["selected"],
                "same_set_as_default": set(selected) == set(old["arms"][method]["selected"]),
                "same_order_as_full": selected == old["arms"]["full"]["selected"],
                "same_set_as_full": set(selected) == set(old["arms"]["full"]["selected"]),
            }
    with npz_path.open("xb") as handle:
        np.savez_compressed(handle, **output_arrays)
    report = {
        "scope": "post-hoc strict-PageRank budget sensitivity; original paths only; not independent replication",
        "dataset": dataset,
        "path": path_id,
        "W": worlds_count,
        "coupling": "step",
        "tolerance": 1e-12,
        "max_iter": 1000,
        "graph_sha256": graph_data["metadata"]["graph_sha256"],
        "source_manifest_sha256": frozen_hash,
        "frozen_reference_json_sha256": sha(old_path),
        "selection_world_sha256": old["selection_world_sha256"],
        "evaluation_world_sha256": old["evaluation_world_sha256"],
        "array_sha256": sha(npz_path),
        "pool_diagnostics": pool_meta,
        "arms": arms,
        "elapsed_seconds": time.perf_counter() - started,
    }
    write_once(json_path, report)
    return {"key": stem, "json_sha256": sha(json_path), "npz_sha256": sha(npz_path), "elapsed_seconds": report["elapsed_seconds"]}


def freeze_only() -> None:
    D.mkdir(exist_ok=True)
    path = D / "source_manifest.json"
    if path.exists():
        raise FileExistsError("source manifest already exists; inspect it rather than refreezing")
    write_once(path, manifest_expected())
    (D / "freeze_status.json").write_text(
        json.dumps({"status": "frozen-before-new-utility-inspection", "expected_conditions": 30, "expected_arms": 60, "source_manifest_sha256": sha(path)}, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"frozen {path}")


def execute() -> None:
    frozen_hash = require_frozen_manifest()
    if (D / "run_status.json").exists():
        raise FileExistsError("run status exists; do not overwrite or resume in place")
    if json.loads((R / "audit/full_validation.json").read_text(encoding="utf-8"))["status"] != "PASS":
        raise RuntimeError("main audit is not passing")
    runner.verify(B)
    cfg = json.loads((B / "config.json").read_text(encoding="utf-8"))
    source_data = json.loads((B / "data/source_manifest.json").read_text(encoding="utf-8"))["datasets"]
    engine.warmup()
    complete, diagnostic_rows = [], []
    try:
        for dataset in cfg["datasets"]:
            graph_data = engine.load_external_graph(B / "data/raw/snap", dataset)
            if graph_data["metadata"] != source_data[dataset]:
                raise RuntimeError(f"raw input/metadata mismatch: {dataset}")
            ranking = strict_ranking(graph_data, 1e-12)
            tighter = strict_ranking(graph_data, 1e-14)
            pool_meta = metadata_for_pools(graph_data, ranking, tighter)
            for method, details in pool_meta.items():
                diagnostic_rows.append({"dataset": dataset, "method": method, **details})
            for path_id in cfg["resolution"]["paths"]:
                for worlds_count in (80, 320):
                    complete.append(run_condition(cfg, graph_data, pool_meta, dataset, path_id, worlds_count, frozen_hash))
                    (D / "run_status.json").write_text(
                        json.dumps({"status": "running", "completed": complete, "expected_conditions": 30, "expected_arms": 60}, indent=2) + "\n",
                        encoding="utf-8",
                    )
                    print(f"strict budget {len(complete)}/30: {complete[-1]['key']}", flush=True)
    except Exception as error:
        (D / "run_status.json").write_text(
            json.dumps({"status": "failed", "error": repr(error), "completed": complete, "expected_conditions": 30, "expected_arms": 60}, indent=2) + "\n",
            encoding="utf-8",
        )
        raise
    pd.DataFrame(diagnostic_rows).to_csv(D / "pool_diagnostics.csv", index=False)
    (D / "run_status.json").write_text(
        json.dumps({"status": "complete", "conditions": 30, "arms": 60, "completed": complete, "source_manifest_sha256": frozen_hash}, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--freeze-only", action="store_true")
    mode.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.freeze_only:
        freeze_only()
    else:
        execute()
