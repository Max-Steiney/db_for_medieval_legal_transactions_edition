"""Baut die ausgewaehlten Stufen am Stueck.

Pro Stufe wird zuerst die Pipeline mit der passenden FRONTEND_STAGE-Env-Var
gestartet, danach das Frontend mit ``--stage N``. Die Stufen werden
hintereinander gebaut, weil sie sich pipeline/output/ teilen.

Aufruf:

    python scripts/build_all_stages.py            # alle vier Stufen
    python scripts/build_all_stages.py --only 1 3 # nur Stufen 1 und 3

Voraussetzung: Pipeline-Repo (Schwester-Repo) ist nebenan geklont.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

FRONTEND_REPO = Path(__file__).resolve().parent.parent
PIPELINE_REPO = FRONTEND_REPO.parent / "db_for_medieval_legal_transactions"


def _check_pipeline_repo() -> None:
    if not PIPELINE_REPO.exists():
        sys.exit(
            f"Pipeline-Repo nicht gefunden unter {PIPELINE_REPO}.\n"
            "Bitte das Schwester-Repo nebenan klonen."
        )


def _run(cmd: list[str], cwd: Path, stage: int) -> None:
    """Fuehrt cmd mit FRONTEND_STAGE im Env aus, bricht bei Exitcode != 0."""
    env = os.environ.copy()
    env["FRONTEND_STAGE"] = str(stage)
    print(f"  -> {' '.join(cmd)}  (cwd={cwd.name}, FRONTEND_STAGE={stage})")
    result = subprocess.run(cmd, cwd=cwd, env=env)
    if result.returncode != 0:
        sys.exit(f"Abgebrochen: Exitcode {result.returncode} fuer {cmd}")


def build_stage(stage: int) -> None:
    print(f"\n=== Stufe {stage} ===")
    python = shutil.which("python") or sys.executable
    _run([python, "-m", "pipeline", "transform"], PIPELINE_REPO, stage)
    _run([python, "-m", "frontend", "build", "--stage", str(stage)],
         FRONTEND_REPO, stage)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--only", nargs="+", type=int, choices=[1, 2, 3, 4],
        help="Nur die angegebenen Stufen bauen (Default: alle vier).",
    )
    args = parser.parse_args()

    _check_pipeline_repo()
    stages = args.only or [1, 2, 3, 4]
    for stage in stages:
        build_stage(stage)

    print("\nFertig.")


if __name__ == "__main__":
    main()
