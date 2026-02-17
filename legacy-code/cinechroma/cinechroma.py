import subprocess
import matplotlib.pyplot as plt
import re
import numpy as np
from pathlib import Path

class VideoColorAnalyzer:
    def __init__(self, video_path, frame_color_num=16, video_color_num=5, scene_coeff=0.7, frame_extraction_mode="interval", interval=10):
        self.video_path = Path(video_path)
        self.video_name = self.video_path.stem
        self.video_format = self.video_path.suffix
        self.output_folder = self.create_output_folder()
        self.total_frames = None
        self.frames_info = {}
        self.frame_color_num = frame_color_num
        self.video_color_num = video_color_num
        self.scene_coeff = scene_coeff
        self.video_colors = []
        self.frame_extraction_mode = frame_extraction_mode
        self.interval = interval

    def create_output_folder(self):
        folder_name = f"Color_Analysis_{self.video_name}"
        output_folder = self.video_path.parent / folder_name
        output_folder.mkdir(parents=True, exist_ok=True)
        return output_folder

    def get_total_frames(self):
        ffprobe_command = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-count_packets', '-show_entries', 'stream=nb_read_packets',
            '-of', 'csv=p=0',
            str(self.video_path)
        ]
        try:
            ffprobe_output = subprocess.check_output(ffprobe_command, text=True).strip()
            self.total_frames = int(ffprobe_output) if ffprobe_output.isdigit() else 0
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")

    def extract_frames(self):
        if self.frame_extraction_mode == "scene":
            ffmpeg_command_extract_frames = [
                'ffmpeg',
                '-i', str(self.video_path),
                '-vf', "select='gt(scene\\," + str(self.scene_coeff) + ")'",
                '-start_number', '0',
                '-fps_mode', 'vfr',
                str(self.output_folder / 'frame_%d.bmp')
            ]
        elif self.frame_extraction_mode == "interval":
            ffmpeg_command_extract_frames = [
                'ffmpeg',
                '-i', str(self.video_path),
                '-vsync', '0',
                '-vf', f"fps=1/{self.interval},format=rgba,elbg=codebook_length={self.frame_color_num}",
                '-start_number', '0',
                str(self.output_folder / 'frame_%d.bmp')
            ]
        else:
            print("Invalid frame extraction mode")
            return

        try:
            subprocess.run(ffmpeg_command_extract_frames, check=True)
            print("Frame extraction completed.")
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")

    def extract_frame_info(self):
        if self.frame_extraction_mode == "scene":
            ffmpeg_command_showinfo = [
                'ffmpeg',
                '-i', str(self.video_path),
                '-vf', "select='gt(scene\\," + str(self.scene_coeff) + ")',showinfo",
                '-f', 'null', '-'
            ]
        elif self.frame_extraction_mode == "interval":
            ffmpeg_command_showinfo = [
                "ffmpeg",
                "-i", str(self.video_path),
                "-vsync", "0",
                "-vf", f"fps=1/{self.interval},format=rgba,elbg=codebook_length={self.frame_color_num},showinfo",
                "-f", "null", "-"
            ]
        else:
            print("Invalid frame extraction mode")
            return

        try:
            output = subprocess.run(ffmpeg_command_showinfo, capture_output=True, text=True, check=True)
            frames_info_str = output.stderr
            print("Frame info extraction completed.")
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")

        for line in frames_info_str.split('\n'):
            regex_pattern = r"\s*n:\s*(\d+)\s*pts:\s*(\d+)\s*pts_time:(\d*.\d*)"
            match = re.findall(regex_pattern, line)
            if match:
                frame_number, pts, timestamp = match[0]
                self.frames_info[frame_number] = [timestamp, []]

    def extract_colors(self):
        all_colors = []
        for frame_number, frame_details in self.frames_info.items():
            frame = str(self.output_folder / f'frame_{frame_number}.bmp')
            colors = self.extract_prominent_colors(frame)
            self.frames_info[frame_number][1] = colors
            print(colors)
            all_colors.extend(colors)

    
    def extract_prominent_colors(self,image_path):
        
        imagemagick_command = [
            "magick",
            "convert",
            image_path,
            "-format", "%c",
            "histogram:info:-"
        ]

        try:
            
            output = subprocess.run(imagemagick_command, capture_output=True, text=True, check=True).stdout

            
            color_pattern = re.compile(r'\s*(\d+):\s*\((\d+),(\d+),(\d+),\d+\)')
            print(output)
            
            color_matches = color_pattern.findall(output)

            
            prominent_colors = [((int(match[1]), int(match[2]), int(match[3])), int(match[0])) for match in color_matches]

            return prominent_colors
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")

    def process_video(self):
        
        self.extract_frames()
        self.extract_frame_info()
        self.extract_colors()


    def plot_color_spectrum(self):
        all_colors = []
        timestamps = []

        for frame_number, frame_details in self.frames_info.items():
            frame_colors = list(col[0] for col in frame_details[1])
            all_colors.append(frame_colors)
            timestamps.append(frame_details[0])

        num_frames = len(all_colors)
        max_colors = max(len(colors) for colors in all_colors)

        
        all_colors = [tuple(color) for color in all_colors]

        
        color_matrix = np.zeros((max_colors, num_frames, 3))
    
        for i, frame_colors in enumerate(all_colors):
            for j, color in enumerate(frame_colors):
                color_matrix[j, i, :] = np.array(color) / 255.0  

        
        plt.figure(figsize=(num_frames, max_colors))
        plt.imshow(color_matrix, aspect='auto')
        plt.xlabel('Timestamp (sec)')
        plt.ylabel('Colors')
        plt.title('Color Spectrum over Time')
        plt.xticks(np.arange(num_frames))
        plt.yticks(np.arange(max_colors))
        plt.grid(False)
        plt.show()

if __name__ == "__main__":
    video_path = r"Put your video path with the file extention here."
    video_analyzer = VideoColorAnalyzer(video_path)
    video_analyzer.process_video()
    video_analyzer.plot_color_spectrum()
