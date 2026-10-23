from pathlib import Path

import pytest

from slurm_tui import slurm

FIX = Path(__file__).parent / "fixtures"


def test_get_job_from_fixture(monkeypatch):
    monkeypatch.setenv("SLURM_TUI_FIXTURES", str(FIX))
    assert slurm.get_job("completed").state == "COMPLETED"


def test_missing_fixture(monkeypatch):
    monkeypatch.setenv("SLURM_TUI_FIXTURES", str(FIX))
    with pytest.raises(ValueError):
        slurm.get_job("does_not_exist")
