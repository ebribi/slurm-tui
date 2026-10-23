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

    result = subprocess.run(
        ["sacct", "-j", job_id, "--parseable2", f"--format={SACCT_FORMAT}"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout

def get_job(job_id: str | None) -> JobRecord:
    if job_id is None:
        raise ValueError("please give a job id (finding your latest job comes later)")
    return parse_sacct(_run_sacct(job_id))
