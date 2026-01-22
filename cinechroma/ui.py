""" This file is part of cinechroma.
See README.md for:
- project structure
- workflow
- responsibilities
- data model
"""

from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.table import Table
from rich.align import Align
from rich.layout import Layout
from rich.columns import Columns
import pyfiglet

console = Console()


def show_banner() -> None:
    """
    Display the cinechroma ASCII banner with professional styling.
    """
    # Use pyfiglet with doom font for bold 3D effect
    ascii_logo = pyfiglet.figlet_format("CINECHROMA", font="doom")

    # Create gradient text with Rich - neon cyan/green/yellow gradient
    text = Text()
    lines = ascii_logo.split("\n")
    
    # Apply neon gradient colors - cyan to green to yellow
    gradient_colors = [
        "bright_cyan",
        "cyan",
        "bright_green",
        "green",
        "bright_yellow",
        "yellow"
    ]
    
    for i, line in enumerate(lines):
        if line.strip():
            color = gradient_colors[min(i, len(gradient_colors) - 1)]
            text.append(line + "\n", style=f"bold {color}")
    
    # Create subtitle section with neon styling
    subtitle = Text.from_markup(
        "\n" + "━" * 60 + "\n" +
        "[bold bright_green] Film Color Analysis Tool [/bold bright_green]\n" +
        "[bright_cyan]Extract • Analyze • Visualize[/bright_cyan]\n" +
        "━" * 60,
        justify="center"
    )
    
    # Combine logo and subtitle
    content = Text()
    content.append(text)
    content.append(subtitle)

    # Create main panel with neon styling
    panel = Panel(
        Align.center(content),
        border_style="bold bright_cyan",
        padding=(1, 4),
        title="[bold bright_yellow]⚡ Welcome ⚡[/bold bright_yellow]",
        title_align="center",
    )
    
    console.print()
    console.print(panel)
    console.print()
    console.print()


def progress_bar():
    """
    Enhanced progress bar with professional styling.
    """
    return Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[bold bright_green]{task.description}[/bold bright_green]"),
        BarColumn(complete_style="bright_cyan", finished_style="bright_green"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("•"),
        TextColumn("{task.completed}/{task.total}"),
        TimeRemainingColumn(),
        transient=True,
        console=console,
    )
