from .models import JobRecord

def show_job(job: JobRecord, findings: list[str]) -> None:
    print(f"{job.job_id} {job.name}: {job.state}")
    for f in findings:
        print(" -", f)
