"""Tiny CLI so data building is one reproducible command, not a notebook cell."""

from __future__ import annotations

import argparse
import sys

from cricketml.config import PATHS
from cricketml.data import cricsheet


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cricketml", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build-data", help="Download and flatten a Cricsheet source.")
    build.add_argument("--source", default="ipl", choices=sorted(cricsheet.SOURCES))
    build.add_argument("--force-download", action="store_true")

    sub.add_parser("paths", help="Print where the project expects things to live.")

    args = parser.parse_args(argv)

    if args.command == "build-data":
        print(f"Building {args.source!r} from Cricsheet…", file=sys.stderr)
        written = cricsheet.build(args.source, force_download=args.force_download)
        for name, path in written.items():
            print(f"  {name:<11} {path.relative_to(PATHS.root)}")
        return 0

    if args.command == "paths":
        for name in ("root", "raw", "interim", "processed", "lessons"):
            print(f"{name:<11} {getattr(PATHS, name)}")
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
