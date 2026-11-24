import pytest

from experiments.analyze_v8_candidate_truncation_development import analyze, expected_blocks


def test_expected_development_block_count_is_fixed():
    assert len(expected_blocks()) == 12


def test_analysis_requires_a_manifest(tmp_path):
    with pytest.raises(FileNotFoundError):
        analyze(tmp_path)
