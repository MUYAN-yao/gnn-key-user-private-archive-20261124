from pathlib import Path

from experiments.run_v6_digg_k5 import FORMAL_SEEDS, PREFLIGHT_SEED
from experiments.v6_digg_snapshot import FILES, expected_paths
from experiments.validate_v6_digg_k5 import validate_study
from experiments.analyze_v6_digg_k5 import paired_summary


def test_v6_seed_sets_are_fixed_and_disjoint():
    assert PREFLIGHT_SEED == 73
    assert FORMAL_SEEDS == tuple(range(74, 84))
    assert PREFLIGHT_SEED not in FORMAL_SEEDS


def test_v6_snapshot_contract_has_all_live_sources():
    paths = expected_paths(Path.cwd())
    assert set(paths) == set(FILES)
    assert all(path.is_file() for path in paths.values())


def test_v6_validator_rejects_preflight_when_formal_is_requested(tmp_path):
    study = tmp_path / "candidate-reduction-v6-empty"
    study.mkdir()
    (study / "manifest.json").write_text("{}", encoding="utf-8")
    report = validate_study(study, "formal")
    assert report["status"] == "FAIL"
    assert any("execution mode mismatch" in error for error in report["errors"])


def test_v6_exact_zero_is_not_recast_as_an_effect_size():
    summary = paired_summary([0.0] * 10)
    assert summary["cohen_dz"] is None
    assert summary["cohen_dz_status"] == "undefined_zero_variance"
