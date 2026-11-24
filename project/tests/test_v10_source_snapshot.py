from pathlib import Path

from experiments.v10_source_snapshot import create, verify


def test_v10_snapshot_copies_and_verifies_the_frozen_contract(tmp_path):
    source_root = Path(__file__).resolve().parents[1]
    snapshot = tmp_path / "snapshot"
    manifest = create(source_root, snapshot)
    assert verify(snapshot)["snapshot_id"] == manifest["snapshot_id"]
