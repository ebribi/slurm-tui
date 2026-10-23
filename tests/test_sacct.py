from pathlib import Path

import pytest

from slurm_tui.parsing import parse_sacct

FIX = Path(__file__).parent / "fixtures"

# file, state, exit, signal, elapsed, limit, req_mem, max_rss
CASES = [
    ("completed.txt", "COMPLETED", 0, 0, 6, 300, 4096, 0.4296875),
    ("failed_127.txt", "FAILED", 127, 0, 0, 300, 4096, 0.3671875),
    ("failed_exit3.txt", "FAILED", 3, 0, 1, 300, 4096, 0.43359375),
    ("timeout.txt", "TIMEOUT", 0, 0, 89, 60, 4096, 0.51953125),
    ("cancelled.txt", "CANCELLED", 0, 0, 5, 300, 4096, 0.375),
    ("running.txt", "RUNNING", 0, 0, 20, 300, 4096, None),
    ("completed_mem_unmeasured.txt", "COMPLETED", 0, 0, 1, 300, 50, 2.0703125),
    ("completed_near_memlimit.txt", "COMPLETED", 0, 0, 91, 300, 50, 44.75),
]


@pytest.mark.parametrize("name,state,code,sig,elapsed,limit,req,rss", CASES)
def test_parse_sacct(name, state, code, sig, elapsed, limit, req, rss):
    job = parse_sacct((FIX / name).read_text())
    assert job.state == state
    assert job.exit_code == code
    assert job.signal == sig
    assert job.elapsed_s == elapsed
    assert job.timelimit_s == limit
    assert job.req_mem_mb == req
    assert job.max_rss_mb == rss


def test_empty_input():
    with pytest.raises(ValueError):
        parse_sacct("")
