import os
import sys
import requests
from PIL import Image, ImageDraw, ImageFont
import subprocess
import numpy as np
from sklearn.cluster import KMeans
import get_mov_title
import get_mov_data
import get_mov_frame
import get_mov_col_pal

# Set the directory to scan
mov_directory = './videos'
frame_directory='./frames'

# List of video file extensions to look for
video_extensions = ['.mp4', '.mov', '.avi', '.mkv']

# List to store the video file names found
video_files = []

# Get the command line argument (if provided)
if len(sys.argv) > 1:
    mode = sys.argv[1]
else:
    mode = 'default'    

# Recursively search the directory for video files
for root, dirs, files in os.walk(mov_directory):
    for file in files:
        if os.path.splitext(file)[1] in video_extensions:
            video_files.append(os.path.basename(file))

print(video_files)
for video_file in video_files:
    movie_title=get_mov_title.get_movie_title(video_file)
    movie_data=get_mov_data.get_movie_details(movie_title)
    get_mov_frame.get_frames(mode,video_file,frame_directory,mov_directory)
    get_mov_col_pal.get_color_palette(video_file,movie_title,frame_directory,movie_data)

