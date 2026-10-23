import csv
import io

from .models import JobRecord

NO_VALUE = {"", "UNLIMITED", "PARTITION_LIMIT", "INVALID"}

_UNIT_MB = {"K": 1 / 1024, "M": 1, "G": 1024, "T": 1024 * 1024}

# Slurm time, string -> seconds
# '1-02:03:04', '00:01:29', '00:00.02'
def parse_duration(s: str) -> float | None:
    s = s.strip()
    if s.upper() in NO_VALUE:
        return None

    days = 0
    if "-" in s:
        day_part, s = s.split("-", 1)
        days = int(day_part)

    parts = s.split(":")
    if len(parts) > 3:
        raise ValueError(f"bad duration: {s!r}")

    total = 0.0
    for piece, factor in zip(reversed(parts), (1, 60, 3600)):
        total += float(piece) * factor
    return days * 86400 + total

# Slurm memory, string -> megabytes
# '4G', '50M', '440K'
def parse_mem_mb(s: str) -> float | None:
    s = s.strip()
    if not s:
        return None

    unit = s[-1].upper()
    if unit not in _UNIT_MB:
        raise ValueError(f"unknown memory unit in {s!r}")
    return float(s[:-1]) * _UNIT_MB[unit]

# Parse `sacct --parsable2` output for one job into a JobRecord
def parse_sacct(text: str) -> JobRecord:
    rows = list(csv.DictReader(io.StringIO(text), delimiter="|"))
    if not rows:
        raise ValueError("no job rows in sacct output")

    parents = [r for r in rows if "." not in r["JobID"]]
    steps = [r for r in rows if "." in r["JobID"]]
    if len(parents) != 1:
        raise ValueError(f"expected 1 job row, found {len(parents)}")
    job = parents[0]

    exit_code, sig = (int(x) for x in job["ExitCode"].split(":"))

    step_rss = [parse_mem_mb(r["MaxRSS"]) for r in steps]
    max_rss = max((m for m in step_rss if m is not None), default=None)

    return JobRecord(
        job_id=job["JobID"],
        name=job["JobName"],
        state=job["State"].split()[0],
        exit_code=exit_code,
        signal=sig,
        elapsed_s=parse_duration(job["Elapsed"]),
        timelimit_s=parse_duration(job["Timelimit"]),
        req_mem_mb=parse_mem_mb(job["ReqMem"]),
        alloc_cpus=int(job["AllocCPUS"]),
        total_cpu_s=parse_duration(job["TotalCPU"]),
        max_rss_mb=max_rss,
        node=job["NodeList"],
    )
