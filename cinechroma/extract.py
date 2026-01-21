""" This file is part of cinechroma.
See README.md for:
- project structure
- workflow
- responsibilities
- data model
"""


def extract_every_n(video_path, output_dir, n):
	print(f"[extract] Would extract every {n}th frame from {video_path} to {output_dir}")

def extract_keyframes(video_path, output_dir):
	print(f"[extract] Would extract keyframes from {video_path} to {output_dir}")
