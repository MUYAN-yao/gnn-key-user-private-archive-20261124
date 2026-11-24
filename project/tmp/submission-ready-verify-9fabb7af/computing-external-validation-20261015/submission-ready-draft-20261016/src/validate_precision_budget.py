"""Independently validate hashes, stored metrics and greedy argmax semantics."""
from pathlib import Path
import hashlib
import json
import sys

import numpy as np

R = Path(__file__).resolve().parents[1]
B = R.parent
D = R / "supplement-pr-budget-precision"
sys.path.insert(0, str(B / "snapshot"))
import engine  # noqa: E402


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    status = json.loads((D / "run_status.json").read_text())
    assert status["status"] == "complete" and status["conditions"] == 30 and status["arms"] == 60
    manifest = sha(D / "source_manifest.json")
    checks = {"conditions": 0, "arms": 0, "evaluation_values": 0, "round_score_positions": 0, "same_default_vector_checks": 0, "same_full_vector_checks": 0}
    for completed in status["completed"]:
        json_path = D / "conditions" / (completed["key"] + ".json")
        npz_path = json_path.with_suffix(".npz")
        assert sha(json_path) == completed["json_sha256"] and sha(npz_path) == completed["npz_sha256"]
        record = json.loads(json_path.read_text())
        assert record["source_manifest_sha256"] == manifest and record["array_sha256"] == sha(npz_path)
        frozen_path = B / "results/main/conditions" / f"resolution__{record['dataset']}__p{record['path']}__w{record['W']}__step.json"
        frozen = json.loads(frozen_path.read_text())
        assert record["frozen_reference_json_sha256"] == sha(frozen_path)
        with np.load(npz_path) as current, np.load(frozen_path.with_suffix(".npz")) as original:
            for method, arm in record["arms"].items():
                values = current[method + "_evaluation"]
                totals = current[method + "_round_totals"]
                assert values.shape == (10000,) and values.dtype.kind in "iu" and values.min() >= 5
                assert totals.shape == (5, len(arm["candidate_ids"]))
                pool = arm["candidate_ids"]
                for round_id in range(5):
                    assert pool[int(np.argmax(totals[round_id]))] == arm["selected"][round_id]
                delta = values - original["full_evaluation"]
                assert abs(delta.mean() - arm["delta_vs_full"]) < 1e-12
                assert abs(delta.std(ddof=1) / np.sqrt(len(delta)) - arm["mc_se_vs_full"]) < 1e-12
                if arm["same_set_as_default"]:
                    assert np.array_equal(values, original[method + "_evaluation"])
                    checks["same_default_vector_checks"] += 1
                if arm["same_set_as_full"]:
                    assert np.array_equal(values, original["full_evaluation"])
                    checks["same_full_vector_checks"] += 1
                checks["arms"] += 1
                checks["evaluation_values"] += len(values)
                checks["round_score_positions"] += totals.size
        checks["conditions"] += 1
    checks["status"] = "PASS"
    (R / "audit/precision_budget_validation.json").write_text(json.dumps(checks, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(checks, indent=2))


if __name__ == "__main__":
    main()
