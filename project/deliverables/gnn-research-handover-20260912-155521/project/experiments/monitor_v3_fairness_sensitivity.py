"""Read-only progress and integrity monitor for the separately versioned v3 study."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from run_v3_fairness_sensitivity import FRACTIONS, SEEDS, run_id


EXPECTED_RUNS = {run_id(fraction, seed) for fraction in FRACTIONS for seed in SEEDS}


def tail(path: Path, lines: int = 30) -> list[str]:
    if not path.is_file() or not path.stat().st_size:
        return []
    return path.read_text(encoding="utf-8", errors="replace").splitlines()[-lines:]


def audit_artifact(path: Path) -> list[str]:
    try:
        artifact = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [f"unreadable artifact: {error}"]
    issues: list[str] = []
    if artifact.get("study_version") != "v3-fairness-sensitivity":
        issues.append("unexpected study_version")
    if artifact.get("smoke_test", {}).get("is_smoke"):
        issues.append("smoke artifact in formal study")
    reproducibility = artifact.get("reproducibility", {})
    if not reproducibility.get("selection_evaluation_worlds_disjoint"):
        issues.append("selection/evaluation worlds are not disjoint")
    if reproducibility.get("calibration_cutoff", "") >= reproducibility.get("outer_test_start", ""):
        issues.append("calibration/test timestamp ordering violation")
    methods = artifact.get("methods", {})
    if methods.get("full_candidate_robust_greedy", {}).get("selection_scope") != "full_decision_graph":
        issues.append("full-candidate comparator is missing full_decision_graph scope")
    if methods.get("gnn_top_k_protected_lower_bound_audit", {}).get("interpretation") != "protected_lower_bound_audit_not_independent_baseline":
        issues.append("GNN Top-K lower-bound label is missing")
    if len(methods.get("candidate_pool_sensitivity", {})) != 4:
        issues.append("candidate-pool sensitivity is incomplete")
    if len(methods.get("objective_weight_sensitivity", {})) != 9:
        issues.append("objective-weight sensitivity is incomplete")
    return issues


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--study-dir", required=True)
    parser.add_argument("--stdout-log")
    parser.add_argument("--stderr-log")
    args = parser.parse_args()
    study_dir = Path(args.study_dir)
    artifacts = {path.stem: path for path in study_dir.glob("split-*.json")}
    issues = {identifier: audit_artifact(path) for identifier, path in sorted(artifacts.items())}
    issues = {identifier: values for identifier, values in issues.items() if values}
    missing = sorted(EXPECTED_RUNS.difference(artifacts))
    stderr_tail = tail(Path(args.stderr_log)) if args.stderr_log else []
    manifest = study_dir / "manifest.json"
    status = "failed" if issues or stderr_tail else "complete" if manifest.is_file() and not missing else "running"
    print(json.dumps({
        "study_version": "v3-fairness-sensitivity",
        "status": status,
        "completed_runs": len(artifacts),
        "expected_runs": len(EXPECTED_RUNS),
        "missing_runs": missing,
        "integrity_issues": issues,
        "manifest_present": manifest.is_file(),
        "stdout_tail": tail(Path(args.stdout_log)) if args.stdout_log else [],
        "stderr_tail": stderr_tail,
    }, ensure_ascii=False, indent=2))
    if status == "failed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
