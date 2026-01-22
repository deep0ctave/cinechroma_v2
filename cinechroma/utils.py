""" This file is part of cinechroma.
See README.md for:
- project structure
- workflow
- responsibilities
- data model
"""


import shutil
from cinechroma.ui import console


def check_ffmpeg() -> None:
    """
    Ensure ffmpeg is available in PATH.
    Exit immediately with a user-friendly error if not found.
    """
    if shutil.which("ffmpeg") is None:
        console.print(
            "[bold red] ffmpeg not found[/bold red]\n"
            "Please install ffmpeg and ensure it is available in PATH."
        )
        raise SystemExit(1)

    console.print("[green]✔ ffmpeg found[/green]")
