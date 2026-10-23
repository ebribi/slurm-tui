from dataclasses import replace
from pathlib import Path

from slurm_tui.analyze import analyze
from slurm_tui.models import JobRecord
from slurm_tui.parsing import parse_sacct

FIX = Path(__file__).parent / "fixtures"

BASE = JobRecord(
    job_id="1", name="test", state="COMPLETED", exit_code=0, signal=0,
    elapsed_s=600, timelimit_s=3600, req_mem_mb=4096, alloc_cpus=1,
    total_cpu_s=500, max_rss_mb=1000, node="compute02",
)


def run(name):
    return analyze(parse_sacct((FIX / name).read_text()))


def has(findings, level, text):
    return any(f.level == level and text in f.message for f in findings)


# --- real fixtures ---
def test_completed_short_job():
    f = run("completed.txt")
    assert has(f, "info", "too short to measure")
    assert not any(x.level in ("warn", "error") for x in f)

def test_failed_command_not_found():
    f = run("failed_127.txt")
    assert f[0].level == "error" and "command not found" in f[0].message

def test_timeout():
    assert has(run("timeout.txt"), "error", "time limit")

def test_cancelled():
    assert run("cancelled.txt")[0].level == "warn"

def test_running_gets_no_resource_advice():
    f = run("running.txt")
    assert len(f) == 1 and "still running" in f[0].message

def test_near_memory_limit():
    assert has(run("completed_near_memlimit.txt"), "warn", "--mem")


# --- built from BASE with one change each ---
def test_out_of_memory():
    assert has(analyze(replace(BASE, state="OUT_OF_MEMORY")), "error", "--mem")

def test_over_requested_memory():
    assert has(analyze(replace(BASE, max_rss_mb=200)), "info", "request less")

def test_near_time_limit():
    assert has(analyze(replace(BASE, elapsed_s=3400)), "warn", "--time")

def test_low_cpu_efficiency():
    job = replace(BASE, alloc_cpus=4, total_cpu_s=100)
    assert has(analyze(job), "info", "CPUs")
