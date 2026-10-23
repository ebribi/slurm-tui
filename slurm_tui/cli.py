import sys
import argparse
from . import slurm, analyze, ui

def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="slurm-tui")
    sub = parser.add_subparsers(dest="command", required=True)
    last = sub.add_parser("last", help="post-mortem of a job")
    last.add_argument("job_id", nargs="?")
    args = parser.parse_args(argv)
    if args.command == "last":
        try:
            job = slurm.get_job(args.job_id)
        except FileNotFoundError:
            sys.exit(
                "sacct not found. Are you on the cluster? On a laptop, set "
                "SLURM_TUI_FIXTURES=tests/fixtures and use a fixture name, "
                "ex. `slurm-tui last completed`."
            )
        except ValueError as e:
            sys.exit(f"error: {e}")
        ui.show_job(job, analyze.analyze(job))

