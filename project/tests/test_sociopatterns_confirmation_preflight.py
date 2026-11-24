import pytest

from experiments.sociopatterns_confirmation_preflight import DATASETS, worlds


def test_worlds_are_deterministic_and_nonrepeating():
    assert worlds("invs2013", 4) == worlds("invs2013", 4)
    assert len(set(worlds("invs2013", 4))) == 4


def test_invalid_dataset_is_rejected():
    assert "sfhh2009" in DATASETS
    with pytest.raises(ValueError):
        from experiments.sociopatterns_confirmation_preflight import run_preflight
        run_preflight("unknown")
