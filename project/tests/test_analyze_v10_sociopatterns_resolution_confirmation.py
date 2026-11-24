import json

import pytest

import experiments.analyze_v10_sociopatterns_resolution_confirmation as module


def test_summarize_rejects_incomplete_matrix(tmp_path, monkeypatch):
    monkeypatch.setattr(module, "expected_keys", lambda: [("a", 1, 5, 20), ("a", 1, 5, 80)])
    report = {"dataset": "a", "world_path": 1, "k": 5, "selection_world_count": 20, "arms": {}}
    (tmp_path / "row.json").write_text(json.dumps(report), encoding="utf-8")
    with pytest.raises(ValueError, match="expected 2 conditions"):
        module.summarize(tmp_path)
