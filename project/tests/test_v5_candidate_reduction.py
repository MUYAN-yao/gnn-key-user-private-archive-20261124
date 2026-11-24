import json

import pytest

from experiments.analyze_v5_candidate_reduction import exact_sign_flip_pvalue, paired_summary
from experiments.run_v5_candidate_reduction import (
    ARMS,
    FORMAL_SEEDS,
    PREFLIGHT_SEED,
    arm_execution_order,
    run_id,
    world_sequence,
    _validate_existing_artifact,
)
from experiments.validate_v5_candidate_reduction import validate_study
from experiments.v5_source_snapshot import SNAPSHOT_FILES, expected_source_paths


def test_frozen_v5_seed_ids_worlds_and_arm_order_are_deterministic():
    assert FORMAL_SEEDS == tuple(range(63, 73))
    assert PREFLIGHT_SEED not in FORMAL_SEEDS
    assert run_id(63) == "seed-63"
    selection = world_sequence(63, 501, 20)
    primary = world_sequence(63, 502, 100)
    stability = world_sequence(63, 503, 100)
    assert not (set(selection) & set(primary) or set(selection) & set(stability) or set(primary) & set(stability))
    first, first_seed = arm_execution_order(63)
    second, second_seed = arm_execution_order(63)
    assert first == second
    assert first_seed == second_seed
    assert set(first) == set(ARMS)


def test_resume_guard_rejects_ineligible_formal_artifact():
    artifact = {
        "study_version": "v5-candidate-reduction",
        "artifact_schema": "v5-candidate-reduction-1",
        "dataset_id": "higgs",
        "execution_mode": "preflight",
        "formal_batch": False,
        "not_eligible_for_inference": True,
        "config": {"fraction": 0.65, "seed": 62, "seed_count": 5},
        "artifact_manifest": {"inputs": {"nodes.csv": "n"}, "source_snapshot": {"snapshot_id": "s"}},
        "integrity": {"status": "passed"},
    }
    with pytest.raises(ValueError, match="dataset or mode"):
        _validate_existing_artifact(
            artifact, "higgs", 63, "formal", {"nodes.csv": "n"}, {"snapshot_id": "s"}
        )


def test_snapshot_contract_lists_existing_live_sources():
    paths = expected_source_paths(__import__("pathlib").Path.cwd())
    assert set(paths) == set(SNAPSHOT_FILES)
    assert all(path.is_file() for path in paths.values())


def test_validator_rejects_smoke_manifest_when_formal_is_requested(tmp_path):
    study = tmp_path / "candidate-reduction-v5-smoke"
    study.mkdir()
    (study / "manifest.json").write_text(json.dumps({
        "study_version": "v5-candidate-reduction",
        "artifact_schema": "v5-candidate-reduction-1",
        "execution_mode": "smoke",
        "formal_batch": False,
        "not_eligible_for_inference": True,
    }), encoding="utf-8")
    report = validate_study(study)
    assert report["status"] == "FAIL"
    assert any("execution mode mismatch" in error for error in report["errors"])


def test_exact_zero_difference_is_not_converted_to_effect_size():
    summary = paired_summary([0.0] * 10)
    assert summary["cohen_dz"] is None
    assert summary["cohen_dz_status"] == "undefined_zero_variance"
    assert exact_sign_flip_pvalue([0.0] * 10) == 1.0
