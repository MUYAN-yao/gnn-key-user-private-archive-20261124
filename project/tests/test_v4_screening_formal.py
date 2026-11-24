import pytest

from experiments.run_v4_screening_formal import (
    ARMS,
    ARTIFACT_SCHEMA,
    POOL_SIZE,
    PROTOCOL_NAME,
    SMOKE_POOL_SIZE,
    arm_execution_order,
    run_id,
    validate_existing_artifact,
    validate_existing_manifest,
)


def test_formal_run_ids_and_arm_order_are_deterministic():
    assert run_id(0.60, 52) == "split-0.60-seed-52"
    first, first_seed = arm_execution_order(52)
    second, second_seed = arm_execution_order(52)
    assert first == second
    assert first_seed == second_seed
    assert set(first) == set(ARMS)


def test_resume_guard_rejects_smoke_artifact_in_formal_mode():
    artifact = {
        "study_version": "v4-screening-formal",
        "artifact_schema": ARTIFACT_SCHEMA,
        "formal_batch": False,
        "not_eligible_for_inference": True,
        "artifact_manifest": {},
        "config": {"fraction": 0.60, "seed": 52, "pool_size": SMOKE_POOL_SIZE},
        "arms": {
            arm: {
                "candidate_count": SMOKE_POOL_SIZE,
                "membership_rank_order": [str(i) for i in range(SMOKE_POOL_SIZE)],
                "canonical_candidate_order": [str(i) for i in range(SMOKE_POOL_SIZE)],
            }
            for arm in ARMS
        },
    }
    with pytest.raises(ValueError, match="formal_batch"):
        validate_existing_artifact(artifact, 0.60, 52, POOL_SIZE, smoke=False)


def test_resume_guard_accepts_matching_smoke_artifact():
    artifact = {
        "study_version": "v4-screening-formal",
        "artifact_schema": ARTIFACT_SCHEMA,
        "formal_batch": False,
        "not_eligible_for_inference": True,
        "artifact_manifest": {},
        "config": {"fraction": 0.60, "seed": 52, "pool_size": SMOKE_POOL_SIZE},
        "arms": {
            arm: {
                "candidate_count": SMOKE_POOL_SIZE,
                "membership_rank_order": [str(i) for i in range(SMOKE_POOL_SIZE)],
                "canonical_candidate_order": [str(i) for i in range(SMOKE_POOL_SIZE)],
            }
            for arm in ARMS
        },
    }
    validate_existing_artifact(artifact, 0.60, 52, SMOKE_POOL_SIZE, smoke=True)


def test_manifest_guard_checks_protocol_and_schema():
    manifest = {
        "study_version": "v4-screening-formal",
        "artifact_schema": ARTIFACT_SCHEMA,
        "formal_batch": False,
        "not_eligible_for_inference": True,
        "inputs": {"nodes.csv": "n"},
        "source": {"runner.py": "s"},
        "protocol": {PROTOCOL_NAME: "p"},
        "run_parameters": {"pool_size": SMOKE_POOL_SIZE},
    }
    validate_existing_manifest(
        manifest,
        {"nodes.csv": "n"},
        {"runner.py": "s"},
        "p",
        SMOKE_POOL_SIZE,
        smoke=True,
    )
    manifest["artifact_schema"] = "wrong"
    with pytest.raises(ValueError, match="schema"):
        validate_existing_manifest(
            manifest,
            {"nodes.csv": "n"},
            {"runner.py": "s"},
            "p",
            SMOKE_POOL_SIZE,
            smoke=True,
        )
