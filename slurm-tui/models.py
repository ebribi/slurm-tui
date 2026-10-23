from dataclasses import dataclass

@dataclass(frozen=True)
class JobRecord:
    job_id: str
    name: str
    state: str                  # COMPLETED, FAILED, TIMEOUT, ...
    elapsed_s: int
    timelimit_s: int
    req_mem_mb: init
    max_rss_mb: int | None      # None while running
