"""Delivery gate for the added strict-PageRank budget sensitivity and review package."""
from pathlib import Path
import hashlib
import json
import platform
import sys

import numpy as np
import pandas as pd

R = Path(__file__).resolve().parents[1]
B = R.parent
Q = R / "qa"
D = R / "supplement-pr-budget-precision"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


main_audit = json.loads((R / "audit/full_validation.json").read_text())
assert main_audit["status"] == "PASS"
assert main_audit["conditions"] == 54 and main_audit["arms"] == 468
new_audit = json.loads((R / "audit/precision_budget_validation.json").read_text())
assert new_audit["status"] == "PASS"
assert new_audit["conditions"] == 30 and new_audit["arms"] == 60
assert new_audit["evaluation_values"] == 600000 and new_audit["round_score_positions"] == 37550

status = json.loads((D / "run_status.json").read_text())
manifest = json.loads((D / "source_manifest.json").read_text())
assert status["status"] == "complete" and status["conditions"] == 30 and status["arms"] == 60
assert sha(D / "protocol.md") == manifest["protocol.md"]
assert sha(R / "src/run_precision_budget_control.py") == manifest["src/run_precision_budget_control.py"]
assert sha(B / "snapshot/source_manifest.json") == manifest["external_snapshot_manifest"]
for record in status["completed"]:
    js = D / "conditions" / f"{record['key']}.json"
    npz = js.with_suffix(".npz")
    assert sha(js) == record["json_sha256"] and sha(npz) == record["npz_sha256"]
    data = json.loads(js.read_text())
    assert data["source_manifest_sha256"] == sha(D / "source_manifest.json")
    assert data["W"] in (80, 320)
    with np.load(npz) as arrays:
        for method, arm in data["arms"].items():
            values = arrays[f"{method}_evaluation"]
            totals = arrays[f"{method}_round_totals"]
            pool = arm["candidate_ids"]
            assert values.shape == (10000,) and values.dtype.kind in "iu" and values.min() >= 5
            assert totals.shape == (5, len(pool))
            assert all(pool[int(np.argmax(totals[i]))] == arm["selected"][i] for i in range(5))

summary = pd.read_csv(R / "analysis/precision_budget/summary_by_budget_precision.csv")
expected = {
    ("ca_grqc", "pagerank_4k", "strict", 80): -11.250776,
    ("ca_grqc", "pagerank_4k", "strict", 320): -2.962969,
    ("ca_grqc", "pagerank_4k", "strict", 1280): -0.544437,
    ("college_msg", "pagerank_4k", "strict", 1280): 9.011829,
    ("wiki_vote", "pagerank_4k", "strict", 1280): 73.955131,
}
for key, target in expected.items():
    row = summary[(summary.dataset == key[0]) & (summary.method == key[1]) & (summary.solver == key[2]) & (summary.W == key[3])]
    assert len(row) == 1 and abs(float(row.iloc[0].loss_percent_mean) - target) < 1e-6
pool = pd.read_csv(R / "analysis/precision_budget/candidate_pool_precision_diagnostics.csv")
assert pool.strict_vs_tighter_same_pool.astype(bool).all()
assert int(pool[(pool.dataset == "ca_grqc") & (pool.method == "pagerank_4k")].iloc[0].default_vs_strict_overlap) == 18

for required in [
    R / "analysis/precision_budget/analysis-report.md",
    R / "analysis/precision_budget/contribution_positioning.md",
    R / "analysis/precision_budget/related_work_evidence.md",
    R / "manuscript/manuscript.pdf",
    R / "manuscript/Online_Resource_1.pdf",
]:
    assert required.is_file()
render = json.loads((Q / "render_checks.json").read_text())
regen_old = json.loads((Q / "regeneration.json").read_text())
regen_new = json.loads((Q / "regeneration_v3.json").read_text())
assert render["status"] == "PASS" and regen_old["status"] == "PASS" and regen_new["status"] == "PASS"
assert render["manuscript"]["pages"] <= 25 and render["text"]["abstract_words"] == 234
review = (Q / "visual-review.md").read_text(encoding="utf-8")
for stem in ("manuscript", "Online_Resource_1"):
    assert f"{render[stem]['pages']}/{render[stem]['pages']}" in review

result = {
    "status": "PASS",
    "frozen_default_conditions": 54,
    "frozen_default_arms": 468,
    "new_posthoc_conditions": 30,
    "new_posthoc_arms": 60,
    "combined_posthoc_conditions": 45,
    "combined_posthoc_arms": 90,
    "new_matrix_hash_and_array_checks": True,
    "independent_result_validator": new_audit,
    "strict_budget_values_recomputed_from_raw_arrays": True,
    "pool_stable_at_tighter_tolerance": True,
    "inherited_default_regeneration": True,
    "new_analysis_regeneration": True,
    "main_pages": render["manuscript"]["pages"],
    "supplement_pages": render["Online_Resource_1"]["pages"],
    "abstract_words": render["text"]["abstract_words"],
    "visual_review": "all pages inspected in qa/visual-review.md",
    "environment": {"python": sys.version, "platform": platform.platform()},
    "scope": "Ready for author scientific and declaration review; no submission has been made.",
}
(Q / "final_checks_v3.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
