import argparse
from . import slurm, analyze, ui

def main(argv=None) -> None:
    parser = argparse.ArgumentParser(prog="slurm-tui")
    sub = parse.add_subparses(dest="command", required=True)
    last = sub.add_parser("last", help="post-mortem of a job")
    last.add_argument("job_id", nargs="?")
    args = parser.parse_args(argv)
    if args.command == "last":
        job = slurm.get_job(args.job_id)
        ui.show_job(job, analyze.analyze(job))
