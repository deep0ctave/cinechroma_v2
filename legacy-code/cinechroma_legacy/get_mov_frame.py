from PIL import Image, ImageDraw, ImageFont
from colorthief import ColorThief
import os
import subprocess

def get_frames(mode,video_file,frame_directory,video_directory):
	
    command_type = mode

    # Execute the appropriate ffmpeg command based on the user input
    if command_type == 'normal':
        ffmpeg_cmd = f"ffmpeg -i ./videos/{video_file} -vf 'select=gt(scene\,0.5),showinfo' -vsync vfr {frame_directory}/%04d.jpg"
    elif command_type == 'detailed':
        ffmpeg_cmd = f"ffmpeg -i ./videos/{video_file} -vf 'select=e=not(mod(n\,2700))' -vsync 0 -frame_pts 1 -q:v 1 -an -f image2 {frame_directory}/%04d.jpg"
    elif command_type == 'fast':
        ffmpeg_cmd = f"ffmpeg -i ./videos/{video_file} -vf 'select=e=not(mod(n\,2700))' -vsync 0 -frame_pts 1 -s 640x480 -q:v 32 -an -f image2 {frame_directory}/%04d.jpg"
    else:
        print("Invalid command type. Please enter either 'normal', 'detailed', or 'fast'.")
    # Run the ffmpeg command to extract frames from the input video
    subprocess.call(ffmpeg_cmd, shell=True)

