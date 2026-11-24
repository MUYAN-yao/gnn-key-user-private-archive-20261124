import json

from experiments.validate_v4_screening_formal import (
    exact_sign_flip_pvalue,
    holm_adjust,
    paired_summary,
    validate,
)


def test_zero_variance_difference_has_undefined_dz():
    summary = paired_summary([0.0] * 10)
    assert summary["cohen_dz"] is None
    assert summary["cohen_dz_status"] == "undefined_zero_variance"
    assert summary["exact_two_sided_sign_flip_p"] == 1.0


def test_sign_flip_and_holm_are_exact_for_small_family():
    assert exact_sign_flip_pvalue([1.0] * 10) == 0.001953125
    assert holm_adjust([0.01, 0.04, 0.50]) == [0.03, 0.08, 0.50]


def test_validator_rejects_smoke_or_incomplete_manifest(tmp_path):
    study = tmp_path / "v4-screening-formal"
    study.mkdir()
    (study / "manifest.json").write_text(json.dumps({
        "study_version": "v4-screening-formal",
        "formal_batch": False,
        "smoke_test": True,
        "not_eligible_for_inference": True,
    }), encoding="utf-8")
    report = validate(study)
    assert report["status"] == "FAIL"
    assert report["comparisons"] == {}
    assert any("complete formal batch" in error for error in report["errors"])
