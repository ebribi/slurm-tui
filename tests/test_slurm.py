from pathlib import Path

import pytest
import subprocess

from slurm_tui import slurm

FIX = Path(__file__).parent / "fixtures"


def test_get_job_from_fixture(monkeypatch):
    monkeypatch.setenv("SLURM_TUI_FIXTURES", str(FIX))
    assert slurm.get_job("completed").state == "COMPLETED"


def test_missing_fixture(monkeypatch):
    monkeypatch.setenv("SLURM_TUI_FIXTURES", str(FIX))
    with pytest.raises(ValueError):
        slurm.get_job("does_not_exist")


def test_latest_job_id(monkeypatch):
    out = "100|2026-10-22T10:00:00\n102|2026-10-22T12:00:00\n101|2026-10-22T11:00:00\n"
    monkeypatch.delenv("SLURM_TUI_FIXTURES", raising=False)
    monkeypatch.setattr(
        slurm.subprocess, "run",
        lambda *a, **k: subprocess.CompletedProcess(a, 0, stdout=out, stderr=""),
    )
    assert slurm.latest_job_id() == "102"
