""" This file is part of cinechroma.
See README.md for:
- project structure
- workflow
- responsibilities
- data model
"""

import json
import numpy as np
from pathlib import Path
from PIL import Image
from skimage.color import lab2rgb

from cinechroma.ui import console


def _lab_to_rgb(lab):
    rgb = lab2rgb(np.array(lab).reshape(1, 1, 3))[0, 0]
    return (np.clip(rgb, 0, 1) * 255).astype(np.uint8)


def render_palette_bars(json_path: str, height_per_bar: int = 100, out_path: str = None) -> None:
    """
    Render movie-level palette bars (Light, Medium, Dark, Overall).
    Each bar shows dominant colors for that luminance range.
    """
    json_path = Path(json_path)
    if out_path is None:
        out_path = Path("output/palette.png")
    else:
        out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    console.print(
        "[bold cyan]▶ Rendering palette bars[/bold cyan]\n"
        f"  Input : {json_path}\n"
        f"  Height: {height_per_bar * 4}"
    )

    with open(json_path) as f:
        data = json.load(f)

    # Check if palettes exist in the JSON
    if "palettes" not in data:
        console.print("[red]✖ No palettes found in analysis JSON. Re-run analysis.[/red]")
        raise SystemExit(1)

    palettes = data["palettes"]
    categories = ["light", "medium", "dark", "overall"]
    
    bars = []
    
    for category in categories:
        palette = palettes.get(category, [])
        
        if not palette:
            # Create a gray bar if category is empty
            gray = [50, 0, 0]  # Neutral gray in Lab
            palette = [gray]
        
        # Convert each color to RGB
        colors = [_lab_to_rgb(lab) for lab in palette]
        
        # Create horizontal bar with equal-width blocks
        bar_width = len(colors) * 100  # 100px per color
        bar = np.zeros((height_per_bar, bar_width, 3), dtype=np.uint8)
        
        block_width = bar_width // len(colors)
        for idx, color in enumerate(colors):
            start_x = idx * block_width
            end_x = (idx + 1) * block_width if idx < len(colors) - 1 else bar_width
            bar[:, start_x:end_x, :] = color
        
        bars.append(bar)
    
    # Stack all bars vertically
    final_image = np.vstack(bars)
    
    Image.fromarray(final_image).save(out_path)
    
    console.print(f"[green]✔ Palette bars saved to {out_path}[/green]")


def render_color_strip(json_path: str, height: int = 400, out_path: str = None) -> None:
    """
    Render a full-film color strip from analysis JSON.
    """
    json_path = Path(json_path)
    if out_path is None:
        out_path = Path("output/strip.png")
    else:
        out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    console.print(
        "[bold cyan]▶ Rendering color strip[/bold cyan]\n"
        f"  Input : {json_path}\n"
        f"  Height: {height}"
    )

    with open(json_path) as f:
        data = json.load(f)
    
    # Handle both old and new JSON formats
    if "frames" in data:
        frames_data = data["frames"]
    else:
        frames_data = data

    strip = []
    for entry in frames_data:
        rgb = _lab_to_rgb(entry["dominant_lab"])
        strip.append(rgb)

    strip = np.array(strip).reshape(1, -1, 3)
    strip = np.repeat(strip, height, axis=0)

    Image.fromarray(strip).save(out_path)

    console.print(f"[green]✔ Color strip saved to {out_path}[/green]")
