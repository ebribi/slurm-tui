import io
from pathlib import Path

from rich.console import Console

from slurm_tui import ui
from slurm_tui.analyze import analyze
from slurm_tui.parsing import parse_sacct

FIX = Path(__file__).parent / "fixtures"


def render(name: str) -> str:
    job = parse_sacct((FIX / name).read_text())
    buf = io.StringIO()
    console = Console(file=buf, width=100, force_terminal=False, color_system=None)
    ui.show_job(job, analyze(job), console=console)
    return buf.getvalue()


def test_near_memory_limit_panel():
    out = render("completed_near_memlimit.txt")
    assert "COMPLETED" in out
    assert "45M of 50M" in out
    assert "▲" in out

def test_timeout_panel():
    out = render("timeout.txt")
    assert "TIMEOUT" in out and "✖" in out

def test_running_job_has_no_memory():
    assert "not measured" in render("running.txt")
