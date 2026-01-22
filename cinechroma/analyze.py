""" This file is part of cinechroma.
See README.md for:
- project structure
- workflow
- responsibilities
- data model
"""


import json
import subprocess
import shutil
from pathlib import Path

import cv2
import numpy as np
from sklearn.cluster import KMeans
from skimage.color import rgb2lab

from cinechroma.ui import console, progress_bar


def get_video_info(video_path: str) -> None:
    """
    Display video metadata using ffprobe.
    """
    if shutil.which("ffprobe") is None:
        console.print(
            "[bold red]✖ ffprobe not found[/bold red]\n"
            "Please install ffmpeg/ffprobe and ensure it is available in PATH."
        )
        raise SystemExit(1)

    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,avg_frame_rate,codec_name,pix_fmt,color_primaries,color_transfer",
        "-show_entries", "format=duration",
        "-of", "json",
        video_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]✖ ffprobe failed: {e}[/red]")
        raise SystemExit(1)
    except json.JSONDecodeError:
        console.print("[red]✖ Failed to parse ffprobe output[/red]")
        raise SystemExit(1)

    # Extract metadata
    stream = data.get("streams", [{}])[0]
    format_info = data.get("format", {})

    width = stream.get("width", "N/A")
    height = stream.get("height", "N/A")
    codec = stream.get("codec_name", "N/A")
    pix_fmt = stream.get("pix_fmt", "N/A")
    color_primaries = stream.get("color_primaries", "N/A")
    color_transfer = stream.get("color_transfer", "N/A")
    
    # Parse FPS (avg_frame_rate is a fraction like "24000/1001")
    fps_str = stream.get("avg_frame_rate", "0/1")
    try:
        num, denom = map(int, fps_str.split("/"))
        fps = num / denom if denom != 0 else 0
    except (ValueError, ZeroDivisionError):
        fps = 0

    # Parse duration
    duration_str = format_info.get("duration", "0")
    try:
        duration = float(duration_str)
    except ValueError:
        duration = 0

    # Display using Rich
    console.print("\n[bold cyan]📹 Video Information[/bold cyan]\n")
    console.print(f"  [bold]Resolution:[/bold]       {width} × {height}")
    console.print(f"  [bold]Duration:[/bold]         {duration:.2f} seconds")
    console.print(f"  [bold]FPS:[/bold]              {fps:.2f}")
    console.print(f"  [bold]Codec:[/bold]            {codec}")
    console.print(f"  [bold]Pixel Format:[/bold]    {pix_fmt}")
    console.print(f"  [bold]Color Primaries:[/bold] {color_primaries}")
    console.print(f"  [bold]Color Transfer:[/bold]  {color_transfer}")
    console.print()


def _get_fps(video_path: str) -> float:
    """
    Get the FPS of a video using ffprobe.
    Returns 24.0 as fallback if detection fails.
    """
    if shutil.which("ffprobe") is None:
        console.print("[yellow]⚠ ffprobe not found, assuming 24 FPS[/yellow]")
        return 24.0

    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=avg_frame_rate",
        "-of", "json",
        video_path
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        fps_str = data.get("streams", [{}])[0].get("avg_frame_rate", "24/1")
        num, denom = map(int, fps_str.split("/"))
        fps = num / denom if denom != 0 else 24.0
        return fps
    except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError, ZeroDivisionError, KeyError):
        console.print("[yellow]⚠ Could not detect FPS, assuming 24 FPS[/yellow]")
        return 24.0


def _load_frame(path: Path) -> np.ndarray:
    """
    Load an image, resize, convert to RGB float array.
    """
    img = cv2.imread(str(path))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (64, 64))
    return img.astype(np.float32) / 255.0


def _filter_luminance(lab_pixels: np.ndarray, min_l: float = 5, max_l: float = 95) -> np.ndarray:
    """
    Filter out extreme blacks and whites in Lab color space.
    Returns only pixels with luminance in [min_l, max_l].
    """
    mask = (lab_pixels[:, 0] >= min_l) & (lab_pixels[:, 0] <= max_l)
    filtered = lab_pixels[mask]
    # Return original if filtering removes everything
    return filtered if len(filtered) > 0 else lab_pixels


def _detect_letterbox(rgb: np.ndarray) -> tuple[int, int]:
    """
    Detect letterbox bars (black bars) at top and bottom of frame.
    Returns (top_crop, bottom_crop) in pixels.
    Uses simple heuristic: check if top/bottom 10% regions are very dark.
    """
    h, w = rgb.shape[:2]
    crop_region = int(h * 0.1)
    
    if crop_region == 0:
        return (0, 0)
    
    # Convert to grayscale for luminance check
    gray = rgb.mean(axis=2)
    
    top_region = gray[:crop_region, :]
    bottom_region = gray[-crop_region:, :]
    
    # Check if regions are very dark (mean < 0.05) and have low variance
    top_is_black = (top_region.mean() < 0.05) and (top_region.std() < 0.02)
    bottom_is_black = (bottom_region.mean() < 0.05) and (bottom_region.std() < 0.02)
    
    top_crop = crop_region if top_is_black else 0
    bottom_crop = crop_region if bottom_is_black else 0
    
    return (top_crop, bottom_crop)


def _remove_letterbox(rgb: np.ndarray) -> np.ndarray:
    """
    Remove letterbox bars if detected.
    Returns cropped image or original if no letterbox detected.
    """
    try:
        top_crop, bottom_crop = _detect_letterbox(rgb)
        
        if top_crop == 0 and bottom_crop == 0:
            return rgb
        
        h = rgb.shape[0]
        start = top_crop
        end = h - bottom_crop
        
        if end <= start:
            # Safety: if crop would remove everything, return original
            return rgb
            
        return rgb[start:end, :, :]
    except Exception:
        # On any error, return original image
        return rgb


def _dominant_colors(rgb: np.ndarray, k: int):
    """
    Extract dominant colors using KMeans in Lab space.
    Filters extreme blacks and whites before clustering.
    """
    pixels = rgb.reshape(-1, 3)
    lab = rgb2lab(pixels.reshape(1, -1, 3)).reshape(-1, 3)
    
    # Filter extreme luminance values
    lab = _filter_luminance(lab)
    
    # Adjust k if we don't have enough pixels
    n_samples = len(lab)
    actual_k = min(k, n_samples)
    
    if actual_k < 1:
        # Fallback to a neutral gray if no valid pixels
        return [[50, 0, 0]]

    km = KMeans(n_clusters=actual_k, n_init='auto', random_state=0)
    labels = km.fit_predict(lab)

    counts = np.bincount(labels)
    order = np.argsort(-counts)

    return km.cluster_centers_[order].tolist()


def _mean_color(rgb: np.ndarray):
    """
    Compute mean color in Lab space, filtering extreme luminance.
    """
    lab = rgb2lab(rgb)
    lab_pixels = lab.reshape(-1, 3)
    
    # Filter extreme luminance values
    lab_pixels = _filter_luminance(lab_pixels)
    
    if len(lab_pixels) == 0:
        # Fallback to neutral gray if all pixels filtered
        return [50, 0, 0]
    
    return lab_pixels.mean(axis=0).tolist()


def _compute_movie_palettes(all_lab_pixels: np.ndarray, k: int = 6) -> dict:
    """
    Generate movie-level color palettes by luminance bands.
    
    Args:
        all_lab_pixels: Aggregated Lab pixels from all frames (Nx3)
        k: Number of clusters per band
    
    Returns:
        Dictionary with 'light', 'medium', 'dark', and 'overall' palettes
    """
    palettes = {}
    
    # Define luminance bands
    light_mask = all_lab_pixels[:, 0] > 70
    medium_mask = (all_lab_pixels[:, 0] > 30) & (all_lab_pixels[:, 0] <= 70)
    dark_mask = all_lab_pixels[:, 0] <= 30
    
    # Light palette
    light_pixels = all_lab_pixels[light_mask]
    if len(light_pixels) >= k:
        km = KMeans(n_clusters=k, n_init='auto', random_state=0)
        km.fit(light_pixels)
        counts = np.bincount(km.labels_)
        order = np.argsort(-counts)
        palettes['light'] = km.cluster_centers_[order].tolist()
    else:
        palettes['light'] = []
    
    # Medium palette
    medium_pixels = all_lab_pixels[medium_mask]
    if len(medium_pixels) >= k:
        km = KMeans(n_clusters=k, n_init='auto', random_state=0)
        km.fit(medium_pixels)
        counts = np.bincount(km.labels_)
        order = np.argsort(-counts)
        palettes['medium'] = km.cluster_centers_[order].tolist()
    else:
        palettes['medium'] = []
    
    # Dark palette
    dark_pixels = all_lab_pixels[dark_mask]
    if len(dark_pixels) >= k:
        km = KMeans(n_clusters=k, n_init='auto', random_state=0)
        km.fit(dark_pixels)
        counts = np.bincount(km.labels_)
        order = np.argsort(-counts)
        palettes['dark'] = km.cluster_centers_[order].tolist()
    else:
        palettes['dark'] = []
    
    # Overall palette (all pixels)
    if len(all_lab_pixels) >= k:
        km = KMeans(n_clusters=k, n_init='auto', random_state=0)
        km.fit(all_lab_pixels)
        counts = np.bincount(km.labels_)
        order = np.argsort(-counts)
        palettes['overall'] = km.cluster_centers_[order].tolist()
    else:
        palettes['overall'] = []
    
    return palettes


def run_analysis(args) -> None:
    """
    Run frame-by-frame color analysis and save JSON output.
    """
    frames_dir = Path(args.frames_dir)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    frames = sorted(frames_dir.glob("*.png"))
    if not frames:
        console.print(f"[red]✖ No frames found in {frames_dir}. Run extract first.[/red]")
        raise SystemExit(1)

    # Get FPS for accurate timestamps
    fps = _get_fps(args.video)

    console.print(
        "[bold cyan]▶ Analyzing frames[/bold cyan]\n"
        f"  Frames : {len(frames)}\n"
        f"  Clusters: {args.k}\n"
        f"  FPS    : {fps:.2f}"
    )

    data = []
    all_lab_pixels = []  # Collect all pixels for movie-level palettes

    with progress_bar() as progress:
        task = progress.add_task("Processing frames", total=len(frames))

        for i, frame in enumerate(frames):
            rgb = _load_frame(frame)
            
            # Remove letterbox bars
            rgb = _remove_letterbox(rgb)
            
            # Convert to Lab and filter
            pixels = rgb.reshape(-1, 3)
            lab = rgb2lab(pixels.reshape(1, -1, 3)).reshape(-1, 3)
            lab = _filter_luminance(lab)
            
            # Collect for movie palettes
            all_lab_pixels.append(lab)

            entry = {
                "frame": frame.name,
                "time": i / fps,  # Correct timestamp based on FPS
                "dominant_lab": _dominant_colors(rgb, args.k)[0],
                "palette_lab": _dominant_colors(rgb, args.k),
                "mean_lab": _mean_color(rgb),
            }

            data.append(entry)
            progress.advance(task)

    # Compute movie-level palettes
    console.print("\n[bold cyan]▶ Computing movie-level palettes[/bold cyan]")
    all_lab_pixels = np.vstack(all_lab_pixels)
    
    # Subsample if too many pixels (for performance)
    if len(all_lab_pixels) > 100000:
        indices = np.random.choice(len(all_lab_pixels), 100000, replace=False)
        all_lab_pixels = all_lab_pixels[indices]
    
    palettes = _compute_movie_palettes(all_lab_pixels, k=args.k)
    
    # Save results with palettes
    output = {
        "frames": data,
        "palettes": palettes
    }

    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)

    console.print(f"[green]✔ Analysis written to {out_path}[/green]")
