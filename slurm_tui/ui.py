from .models import JobRecord

def show_job(job: JobRecord, findings: list[str]) -> None:
    print(f"{job.job_id} {job.name}: {job.state} (exit {job.exit_code}:{job.signal})")
    print(f"  elapsed {job.elapsed_s}s / limit {job.timelimit_s}s on {job.node}")
    print(f"  memory  {job.max_rss_mb} MB used / {job.req_mem_mb} MB requested")
    for f in findings:
        print(" -", f)
