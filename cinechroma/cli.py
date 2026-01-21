"""
This file is part of cinechroma.

See README.md for:
- project structure
- workflow
- responsibilities
- data model
"""

import argparse
import sys

from cinechroma.ui import show_banner, console
from cinechroma.utils import check_ffmpeg
from cinechroma import extract, analyze, render


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cinechroma",
        description="Film color analysis from the command line",
    )

    parser.add_argument("--quiet", action="store_true")
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("--version", action="store_true")

    sub = parser.add_subparsers(dest="command")

    # extract
    extract_p = sub.add_parser("extract")
    extract_p.add_argument("video")
    extract_p.add_argument("--every-n", type=int)
    extract_p.add_argument("--keyframes", action="store_true")

    # analyze
    analyze_p = sub.add_parser("analyze")
    analyze_p.add_argument("video")
    analyze_p.add_argument("--every-n", type=int)
    analyze_p.add_argument("--keyframes", action="store_true")
    analyze_p.add_argument("--k", type=int, default=5)

    # render
    render_p = sub.add_parser("render")
    render_p.add_argument("type", choices=["strip"])
    render_p.add_argument("input")

    return parser


def dispatch(args) -> int:
    if args.version:
        console.print("cinechroma v0.1.0")
        return 0

    if args.command in ("extract", "analyze"):
        check_ffmpeg()

    if args.command == "extract":
        if args.keyframes:
            extract.extract_keyframes(args.video, "frames")
        else:
            extract.extract_every_n(args.video, "frames", args.every_n or 24)

    elif args.command == "analyze":
        analyze.run_analysis(args)

    elif args.command == "render":
        if args.type == "strip":
            render.render_color_strip(args.input)

    else:
        console.print("[red]No command specified.[/]")
        return 1

    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.quiet and args.command:
        show_banner()

    exit_code = dispatch(args)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()
