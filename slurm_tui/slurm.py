import os
import subprocess
from pathlib import Path

from .models import JobRecord
from .parsing import parse_sacct

SACCT_FORMAT = (
    "JobID,JobName,State,ExitCode,Elapsed,Timelimit,"
    "ReqMem,AllocCPUS,TotalCPU,MaxRSS,NodeList"
)
FIXTURE_ENV = "SLURM_TUI_FIXTURES"

# Only function that communicates with Slurm (or fixture dir)
def _run_sacct(job_id: str) -> str:
    fixture_dir = os.environ.get(FIXTURE_ENV)
    if fixture_dir:
        path = Path(fixture_dir) / f"{job_id}.txt"
        if not path.exists():
            raise ValueError(f"no fixture named {path.name} in {fixture_dir}")
        return path.read_text()

    try:
        result = subprocess.run(
            ["sacct", "-j", job_id, "--parsable2", f"--format={SACCT_FORMAT}"],
            capture_output=True, text=True, check=True,
        )
    except subprocess.CalledProcessError as e:
        raise ValueError(f"sacct failed: {e.stderr.strip() or f'exit {e.returncode}'}") from e
    return result.stdout

def get_job(job_id: str | None) -> JobRecord:
    if job_id is None:
        job_id = latest_job_id()
    return parse_sacct(_run_sacct(job_id))

# Returns most recent job from the last 14 days
def latest_job_id() -> str:
    if os.environ.get(FIXTURE_ENV):
        raise ValueError("'latest' isn't available in fixture mode; pass a fixture name")
    result = subprocess.run(
        ["sacct", "-X", "-n", "--parsable2", "-S", "now-14days", "--format=JobID,Submit"],
        capture_output=True, text=True, check=True,
    )
    rows = [line.split("|") for line in result.stdout.splitlines() if line.strip()]
    if not rows:
        raise ValueError("no jobs found in the last 14 days")
    rows.sort(key=lambda r: r[1])       # Submit times are ISO string, sort correctly
    return rows[-1][0]
