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
import shutil
from pathlib import Path

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

    extract_p = sub.add_parser("extract")
    extract_p.add_argument("video")
    extract_p.add_argument("--every-n", type=int)
    extract_p.add_argument("--keyframes", action="store_true")
    extract_p.add_argument("--frames-dir", type=str, default="frames")

    analyze_p = sub.add_parser("analyze")
    analyze_p.add_argument("video")
    analyze_p.add_argument("--every-n", type=int)
    analyze_p.add_argument("--keyframes", action="store_true")
    analyze_p.add_argument("--k", type=int, default=5)
    analyze_p.add_argument("--frames-dir", type=str, default="frames")
    analyze_p.add_argument("--out", type=str, default="output/analysis.json")

    info_p = sub.add_parser("info")
    info_p.add_argument("video")

    render_p = sub.add_parser("render")
    render_p.add_argument("type", choices=["strip", "palette"])
    render_p.add_argument("input")
    render_p.add_argument("--height", type=int, default=400)
    render_p.add_argument("--out", type=str)

    clean_p = sub.add_parser("clean", help="Remove generated frames and output files")
    clean_p.add_argument("--frames-dir", type=str, default="frames")
    clean_p.add_argument("--out-dir", type=str, default="output")
    clean_p.add_argument("--all", action="store_true", help="Remove both frames and output")

    return parser


def dispatch(args) -> int:
    if args.version:
        console.print("cinechroma v0.1.0")
        return 0

    if args.command in ("extract", "analyze"):
        check_ffmpeg()

    if args.command == "extract":
        if args.keyframes:
            extract.extract_keyframes(args.video, args.frames_dir)
        else:
            extract.extract_every_n(args.video, args.frames_dir, args.every_n or 24)

    elif args.command == "analyze":
        analyze.run_analysis(args)

    elif args.command == "info":
        analyze.get_video_info(args.video)

    elif args.command == "render":
        out_path = args.out if hasattr(args, 'out') and args.out else None
        if args.type == "strip":
            render.render_color_strip(args.input, height=args.height, out_path=out_path)
        elif args.type == "palette":
            render.render_palette_bars(args.input, out_path=out_path)

    elif args.command == "clean":
        removed = []
        
        if args.all:
            # Remove both frames and output
            frames_path = Path(args.frames_dir)
            out_path = Path(args.out_dir)
            
            if frames_path.exists():
                shutil.rmtree(frames_path)
                removed.append(str(frames_path))
            
            if out_path.exists():
                shutil.rmtree(out_path)
                removed.append(str(out_path))
        else:
            # Remove only specified directories if they exist
            if args.frames_dir != "frames":
                frames_path = Path(args.frames_dir)
                if frames_path.exists():
                    shutil.rmtree(frames_path)
                    removed.append(str(frames_path))
            
            if args.out_dir != "output":
                out_path = Path(args.out_dir)
                if out_path.exists():
                    shutil.rmtree(out_path)
                    removed.append(str(out_path))
            
            # If using defaults and no specific path given, clean both
            if args.frames_dir == "frames" and args.out_dir == "output":
                frames_path = Path("frames")
                out_path = Path("output")
                
                if frames_path.exists():
                    shutil.rmtree(frames_path)
                    removed.append("frames")
                
                if out_path.exists():
                    shutil.rmtree(out_path)
                    removed.append("output")
        
        if removed:
            console.print(f"[green]✔ Removed: {', '.join(removed)}[/green]")
        else:
            console.print("[yellow]⚠ Nothing to clean[/yellow]")

    else:
        console.print("[red]✖ No command specified[/red]")
        return 1

    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.quiet and args.command:
        show_banner()

    sys.exit(dispatch(args))

if __name__ == "__main__":
    main()
