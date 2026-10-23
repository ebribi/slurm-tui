from .models import JobRecord

def get_job(job_id: str | None) -> JobRecord:
    # STUB: later this calls _run_sacct and parse_sacct
    return JobRecord("123", "demo", "COMPLETED", 300, 7200, 2048, 1900)
