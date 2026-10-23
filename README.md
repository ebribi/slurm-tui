# slurm-cli

A small command-line tool that explains how a Slurm job ended: its state, how much time and memory it used compared with what you asked for, and plain-English advice for the next run. Built to help students learn the Brooklyn College CIS cluster.

> **Status: early.** Only `job` is implemented. A `build` command for generating sbatch scripts is planned.

## Purpose

Run it after a job finishes (or while it runs) to see what happened and what to change:

```
╭─ Job 702  wrap ───────────────────────────────────────────────╮
│                                                               │
│  State   COMPLETED                                            │
│  Time    ██████░░░░░░░░░░░░░░  30%   1m31s of 5m00s           │
│  Memory  ██████████████████░░  90%   45M of 50M               │
│  CPUs    1                                                    │
│  Node    compute02                                            │
│                                                               │
│  • Completed successfully in 1m31s.                           │
│  ▲ Memory peaked at 45M of 50M (90%). Raise --mem: a job      │
│    over its limit slows down (it swaps) before it is killed.  │
╰───────────────────────────────────────────────────────────────╯
```
(Example; the real output is colored.)

## Install

You need Python 3.11 or newer and Slurm's `sacct` on your `PATH` (it is on the cluster's head node).

On the cluster, with your virtual environment active:

```
source ~/.venv/bin/activate
pip install git+https://github.com/ebribi/slurm-cli
```

Or from a clone:

```
git clone https://github.com/ebribi/slurm-cli.git ~/slurm-cli
cd ~/slurm-cli
pip install -e .
```

With `-e`, a later `git pull` takes effect without reinstalling. After changing `pyproject.toml`, reinstall.

## Usage

```
slc job            # your most recent job (last 14 days)
slc job 702        # a specific job
slc last           # "last" is an alias for "job"
python -m slurm_cli job  # same thing without the command
```

## Reading the output

| Row | Meaning |
|---|---|
| State | How the job ended: `COMPLETED`, `FAILED`, `TIMEOUT`, `OUT_OF_MEMORY`, `CANCELLED`, or `RUNNING` / `PENDING` while active |
| Time | Time used compared with the `--time` limit |
| Memory | Peak memory (`MaxRSS`) compared with `--mem` |
| CPUs, Node | Cores allocated and the machine the job ran on |

Findings are marked `✖` error, `▲` warning, `•` info. The advice rules:

| Situation | Advice |
|---|---|
| Timeout | Raise `--time`, or check whether the job was making progress |
| Out of memory | Raise `--mem` |
| Failed | Shows the exit code with a hint for common ones (127 = command not found) and points to the `.err` log |
| Memory at 85% or more of the request | Raise `--mem` |
| Memory at 25% or less of a request of 2G or more | You could request less |
| Time at 90% or more of the limit | Raise `--time` |
| Several CPUs requested but under 25% used | The job may be waiting on network or disk, or be single-threaded |
| Under 30 seconds | Too short to measure memory reliably |

The thresholds are constants at the top of `slurm_cli/analyze.py`.

### Good to know (BC CIS cluster)

- Slurm samples memory about every 30 seconds, so very short jobs show little or no memory use.
- A job that goes over `--mem` is held to its RAM limit but pushed into swap, so it slows down first and is not necessarily killed. A job that suddenly gets very slow may be short of memory.

## Development

```
python -m venv .venv && source .venv/bin/activate
pip install -e . pytest
python -m pytest
```

Only `slurm_cli/slurm.py` talks to Slurm. To work without a cluster, set `SLURM_CLI_FIXTURES` to a folder of saved `sacct` output and give a fixture name instead of a job ID:

```
SLURM_CLI_FIXTURES=tests/fixtures slc job timeout
```

### Layout

```
slurm_cli/
  cli.py        argument parsing and dispatch
  slurm.py      the only place that runs sacct (or reads a fixture)
  parsing.py    sacct text -> JobRecord (pure functions)
  models.py     dataclasses: JobRecord, Finding
  analyze.py    JobRecord -> findings (pure)
  formatting.py time and memory formatting
  ui.py         rich output
tests/
  fixtures/     saved real sacct output
```

### Fixtures

Captured from the cluster with:

```
sacct -j <id> --parsable2 \
  --format=JobID,JobName,State,ExitCode,Elapsed,Timelimit,ReqMem,AllocCPUS,TotalCPU,MaxRSS,NodeList
```

| File | Shows |
|---|---|
| `completed.txt` | A short successful job |
| `failed_127.txt` | Command not found |
| `failed_exit3.txt` | A job that exited with code 3 |
| `timeout.txt` | A job that hit its time limit |
| `cancelled.txt` | A job cancelled with `scancel` |
| `running.txt` | A job that was still running |
| `completed_mem_unmeasured.txt` | A 1-second job whose memory was never sampled |
| `completed_near_memlimit.txt` | A job at 90% of its memory request |

## Planned

- `build`: generate annotated sbatch scripts for pipeline stages (download, clean)
- Possible later: `lint` for existing scripts, a live job view, and data coverage and verification checks
