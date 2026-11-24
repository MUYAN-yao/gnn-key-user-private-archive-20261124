from pathlib import Path
import shutil
import pytest

from app.validation import DatasetValidationError, load_dataset


def test_sample_dataset_is_valid():
    dataset = load_dataset(Path("sample_data"))
    assert len(dataset.nodes) == 8
    assert len(dataset.edges) == 12


def test_missing_required_file_is_rejected(tmp_path):
    shutil.copy(Path("sample_data/nodes.csv"), tmp_path / "nodes.csv")
    with pytest.raises(DatasetValidationError, match="Missing required file"):
        load_dataset(tmp_path)
