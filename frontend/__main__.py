"""CLI entry point: python -m frontend build|status [options]

Subcommands write a per-command log to pipeline/output/logs/frontend_<cmd>.log
(overwritten on every run). Set the environment variable PIPELINE_NO_LOG=1
to suppress logging.
"""

import argparse
import sys

from frontend.build import build_single, build_all
from pipeline.utils.run_log import run_logged


def _dispatch(args, parser):
    if args.command == "build":
        if args.single:
            build_single(args.single)
        else:
            build_all()
    elif args.command == "status":
        from frontend.status import run
        cli_args = []
        if args.json:
            cli_args.append("--json")
        if args.test:
            cli_args.append("--test")
        run(cli_args)
    else:
        parser.print_help()
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="frontend",
        description="Build the digital edition HTML pages from TEI-XML sources.",
    )
    sub = parser.add_subparsers(dest="command")

    build_cmd = sub.add_parser("build", help="Build HTML edition")
    build_cmd.add_argument(
        "--single",
        type=str,
        default=None,
        help="Build a single file (relative path from repo root)",
    )

    status_cmd = sub.add_parser("status", help="Show project status dashboard")
    status_cmd.add_argument(
        "--json", action="store_true",
        help="Output as JSON instead of formatted text",
    )
    status_cmd.add_argument(
        "--test", action="store_true",
        help="Run edition tests and include results",
    )

    args = parser.parse_args()

    if args.command in ("build", "status"):
        run_logged(f"frontend_{args.command}", lambda: _dispatch(args, parser))
    else:
        _dispatch(args, parser)


if __name__ == "__main__":
    main()
