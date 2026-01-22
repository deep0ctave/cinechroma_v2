""" This file is part of cinechroma.
See README.md for:
- project structure
- workflow
- responsibilities
- data model
"""


import subprocess
from pathlib import Path
from cinechroma.ui import console


def extract_every_n(video: str, out_dir: str, n: int) -> None:
    """
    Extract every Nth frame from a video using ffmpeg.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    console.print(
        "[bold cyan]▶ Extracting frames[/bold cyan]\n"
        f"  Video : {video}\n"
        f"  Mode  : every {n} frames\n"
        f"  Output: {out}"
    )

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-i", video,
        "-vf", f"select=not(mod(n\\,{n}))",
        "-vsync", "vfr",
        f"{out}/%06d.png",
    ]

    subprocess.run(cmd, check=True)

    console.print("[green]✔ Frame extraction complete[/green]")


def extract_keyframes(video: str, out_dir: str) -> None:
    """
    Extract keyframes (I-frames only).
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    console.print(
        "[bold cyan]▶ Extracting keyframes[/bold cyan]\n"
        f"  Video : {video}\n"
        f"  Output: {out}"
    )

    cmd = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel", "error",
        "-skip_frame", "nokey",
        "-i", video,
        "-vsync", "vfr",
        f"{out}/%06d.png",
    ]

    subprocess.run(cmd, check=True)

    console.print("[green]✔ Keyframe extraction complete[/green]")
