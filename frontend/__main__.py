"""CLI entry point: python -m frontend build|status [options]

Subcommands write a per-command log to pipeline/output/logs/frontend_<cmd>.log
(overwritten on every run). Set the environment variable PIPELINE_NO_LOG=1
to suppress logging.
"""

import argparse
import sys


def _dispatch(args, parser):
    # Deferred imports: the stage env vars must be set before
    # frontend.config picks the output directory.
    from frontend.build import build_single, build_all
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
    build_cmd.add_argument(
        "--stage",
        type=int,
        choices=[1, 2, 3, 4],
        default=None,
        help=(
            "Build-Stufe (siehe frontend/stages.py): 1=Publikation, "
            "2=Vergleich mit mentioned events, 3=voller _ready-Bestand, "
            "4=Maximalversion. Default 1."
        ),
    )
    build_cmd.add_argument(
        "--include-mentioned",
        action="store_true",
        help=(
            "Kurzform fuer --stage 2. Schreibt nach docs-with-mentioned/ "
            "und zaehlt verschachtelte rs-events als volle Events."
        ),
    )
    build_cmd.add_argument(
        "--audience",
        type=str,
        choices=["public", "private"],
        default=None,
        help=(
            "Zielpublikum (siehe frontend/audiences.py), Begriffsbildung "
            "analog zu GitHub-Repos: 'public' fuer den "
            "Veroeffentlichungs-Stand (Default, schreibt nach docs/), "
            "'private' fuer Projektpartner und interne Pruefung "
            "(schreibt nach docs-private/ und blendet experimentelle "
            "Sektionen und technische IDs ein)."
        ),
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

    # Stufe und Audience vor jedem Modulimport setzen: frontend.config und
    # die Pipeline-Transformer lesen die abgeleiteten Env-Vars beim Import
    # und leiten Output-Verzeichnis sowie Mentioned-Toggle daraus ab. Ohne
    # explizite Wahl bleiben Stufe 1 (Publikation) und Audience 'public'.
    if args.command == "build":
        from frontend import stages, audiences
        stage_id = getattr(args, "stage", None)
        if stage_id is None and getattr(args, "include_mentioned", False):
            stage_id = 2
        if stage_id is None:
            stage_id = stages.DEFAULT_STAGE_ID
        stages.set_stage_env(stage_id)

        audience_id = getattr(args, "audience", None)
        if audience_id is None:
            audience_id = audiences.DEFAULT_AUDIENCE_ID
        audiences.set_audience_env(audience_id)

    from pipeline.utils.run_log import run_logged

    if args.command in ("build", "status"):
        run_logged(f"frontend_{args.command}", lambda: _dispatch(args, parser))
    else:
        _dispatch(args, parser)


if __name__ == "__main__":
    main()
