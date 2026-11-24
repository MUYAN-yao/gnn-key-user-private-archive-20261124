import json

from experiments.audit_v3_manuscript_consistency import audit


def test_v3_manuscript_consistency_accepts_registered_null_families(tmp_path):
    analysis = tmp_path / "analysis"
    analysis.mkdir()
    rows = []
    rows.extend({"family": "primary_fairness", "mean_difference": 0.0, "ties": 10, "holm_adjusted_p": 1.0} for _ in range(3))
    rows.extend({"family": "candidate_pool_sensitivity", "mean_difference": 0.0, "ties": 10, "holm_adjusted_p": 1.0} for _ in range(9))
    rows.extend({"family": "objective_weight_sensitivity", "mean_difference": 0.0, "ties": 10, "holm_adjusted_p": 1.0} for _ in range(21))
    rows.extend({"family": "objective_weight_sensitivity", "mean_difference": 10.751, "ties": 9, "holm_adjusted_p": 1.0} for _ in range(3))
    (analysis / "paired_comparisons.json").write_text(json.dumps(rows), encoding="utf-8")
    manuscript = tmp_path / "manuscript.md"
    manuscript.write_text("6.5 v3；10 次平局；10.751；Holm $p=1.000$", encoding="utf-8")
    abstract = tmp_path / "abstract.md"
    abstract.write_text("v3 null Holm-supported utility difference", encoding="utf-8")
    ledger = tmp_path / "ledger.md"
    ledger.write_text("completed confirmatory null result; exactly zero; protocol-conditional negative findings", encoding="utf-8")
    assert audit(analysis, manuscript, abstract, ledger) == []
