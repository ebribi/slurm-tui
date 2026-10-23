from .models import Finding, JobRecord

# Tunable thresholds
NEAR_MEM_LIMIT = 0.85            # memory use at or above this = "near the limit"
OVER_REQUESTED_MEM = 0.25        # at or below this = "asked for far too much"
OVER_REQUESTED_MIN_MB = 2048     # only fag when the request was >= 2G
MEASURE_MIN_S = 30               # Slurm samples memory every ~30s
NEAR_TIME_LIMIT = 0.90
OVER_REQUESTED_TIME = 0.10
OVER_REQUESTED_TIME_MIN_S = 3600
LOW_CPU_EFFICIENCY = 0.25

ACTIVE_STATES = {"PENDING", "RUNNING", "SUSPENDED", "REQUEUED"}

EXIT_HINTS = {
    1: "general error in the script or program",
    2: "command-line usage error",
    126: "command found but could not be run",
    127: "command not found (check the command, your PATH and that the venv is activated)",
    137: "killed (SIGKILL), often for using too much memory",
    139: "crashed (segmentation fault)",
    143: "terminated (SIGTERM)",
}


def _fmt_time(seconds: float) -> str:
    s = int(round(seconds))
    h, rem = divmod(s, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h{m:02d}m"
    if m:
        return f"{m}m{s:02d}s"
    return f"{s}s"

# Format like Slurm's --mem syntax (G / M)
def _fmt_mb(mb: float) -> str:
    if mb >= 1024:
        return f"{mb / 1024:.1f}G"
    if mb >= 10:
        return f"{mb:.0f}M"
    return f"{mb:.1f}M"


def _outcome(job: JobRecord) -> list[Finding]:
    state = job.state
    if state in ACTIVE_STATES:
        return [Finding("info", f"Job is still {state.lower()}.")]
    if state == "COMPLETED":
        return [Finding("info", f"Completed successfully in {_fmt_time(job.elapsed_s)}.")]
    if state == "TIMEOUT":
        limit = _fmt_time(job.timelimit_s) if job.timelimit_s else "its limit"
        return [Finding("error", f"Hit its time limit ({limit}). Raise --time, "
                                 "or check whether the job was making progress.")]
    if state == "OUT_OF_MEMORY":
        req = _fmt_mb(job.req_mem_mb) if job.req_mem_mb else "the requested amount"
        return [Finding("error", f"Killed for using too much memory (requested {req}). "
                                 "Raise --mem.")]
    if state == "FAILED":
        msg = f"Failed with exit code {job.exit_code}"
        hint = EXIT_HINTS.get(job.exit_code)
        if hint:
            msg += f": {hint}"
        if job.signal:
            msg += f" (signal {job.signal})"
        return [Finding("error", msg + ". Check the job's .err log.")]
    if state == "CANCELLED":
        return [Finding("warn", "Cancelled before it finished.")]
    return [Finding("warn", f"Ended with state {state}.")]


def _memory(job: JobRecord) -> list[Finding]:
    if not job.req_mem_mb:
        return []
    if job.elapsed_s < MEASURE_MIN_S:
        if job.state == "COMPLETED":
            return [Finding("info", f"Ran only {_fmt_time(job.elapsed_s)}: too short to "
                                    "measure memory. Slurm samples ~30s.")]
        return []
    if job.max_rss_mb is None:
        return [Finding("info", "No memory measurement was recorded for this job.")]

    ratio = job.max_rss_mb / job.req_mem_mb
    used = f"{_fmt_mb(job.max_rss_mb)} of {_fmt_mb(job.req_mem_mb)}"
    if ratio >= NEAR_MEM_LIMIT:
        return [Finding("warn", f"Memory peaked at {used} ({ratio:.0%}). Raise --mem: a job "
                                "over its limit slows down (swaps) before it is killed.")]
    if ratio <= OVER_REQUESTED_MEM and job.req_mem_mb >= OVER_REQUESTED_MIN_MB:
        return [Finding("info", f"Used only {used} ({ratio:.0%}). You could request less memory.")]
    return [Finding("info", f"Memory use looks fine: {used} ({ratio:.0%}).")]


def _time(job: JobRecord) -> list[Finding]:
    if job.state == "TIMEOUT" or not job.timelimit_s:
        return []
    ratio = job.elapsed_s / job.timelimit_s
    used = f"{_fmt_time(job.elapsed_s)} of {_fmt_time(job.timelimit_s)}"
    if ratio >= NEAR_TIME_LIMIT:
        return [Finding("warn", f"Used {used} ({ratio:.0%}). Raise --time before a longer "
                                "run hits the limit.")]
    if ratio <= OVER_REQUESTED_TIME and job.timelimit_s >= OVER_REQUESTED_TIME_MIN_S:
        return [Finding("info", f"Used only {used}. A shorter --time may let the job start sooner.")]
    return []


def _cpu(job: JobRecord) -> list[Finding]:
    if job.alloc_cpus <= 1 or not job.total_cpu_s or job.elapsed_s < MEASURE_MIN_S:
        return []
    efficiency = job.total_cpu_s / (job.elapsed_s * job.alloc_cpus)
    if efficiency < LOW_CPU_EFFICIENCY:
        return [Finding("info", f"Requested {job.alloc_cpus} CPUs but used about "
                                f"{efficiency:.0%} of them. The job may be waiting on network "
                                "or disk, or the code may be single-threaded.")]
    return []


def analyze(job: JobRecord) -> list[Finding]:
    findings = _outcome(job)
    if job.state in ACTIVE_STATES:
        return findings          # no resource advice until the job has finished
    findings += _memory(job)
    findings += _time(job)
    findings += _cpu(job)
    return findings
