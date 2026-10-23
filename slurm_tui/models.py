from dataclasses import dataclass

@dataclass(frozen=True)
class JobRecord:
    job_id: str
    name: str
    state: str                  # COMPLETED, FAILED, TIMEOUT, ...
    exit_code: int
    signal: int
    elapsed_s: int
    timelimit_s: int | None
    req_mem_mb: int | None
    alloc_cpus: int
    total_cpu_s: float | None
    max_rss_mb: int | None      # None if nothing was measured
    node: str

@dataclass(frozen=True)
class Finding:
    level: str                  # "error", "warn", or "info"
    message: str
