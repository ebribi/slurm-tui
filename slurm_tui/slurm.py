from .models import JobRecord


def get_job(job_id: str | None) -> JobRecord:
    # STUB: step 1b replaces this with real parsing
    return JobRecord(
        job_id="123", name="demo", state="COMPLETED", exit_code=0, signal=0,
        elapsed_s=300, timelimit_s=7200, req_mem_mb=2048, alloc_cpus=1,
        total_cpu_s=10, max_rss_mb=1900, node="compute02",
    )
