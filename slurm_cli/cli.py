import sys
import argparse
from . import slurm, analyze, ui

def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="slc")
    sub = parser.add_subparsers(dest="command", required=True)
    last = sub.add_parser("job", aliases=["last"], help="post-mortem of a job (default: your latest)")
    last.add_argument("job_id", nargs="?")
    args = parser.parse_args(argv)
    if args.command in ("job", "last"):
        try:
            job = slurm.get_job(args.job_id)
        except FileNotFoundError:
            sys.exit(
                "sacct not found. Are you on the cluster? On a laptop, set "
                "SLURM_CLI_FIXTURES=tests/fixtures and use a fixture name, "
                "ex. `slc last completed`."
            )
        except ValueError as e:
            sys.exit(f"error: {e}")
        ui.show_job(job, analyze.analyze(job))

