import pytest

from experiments.validate_v10_sociopatterns_resolution_confirmation import validate


def test_validator_rejects_missing_manifest(tmp_path):
    with pytest.raises(FileNotFoundError):
        validate(tmp_path)
