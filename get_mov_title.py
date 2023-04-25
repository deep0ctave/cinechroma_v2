import re


def get_movie_title(video_file):
    # Example video file names
    filename = video_file
    title = re.search(r"^(.+?)\.\d{4}\.", filename).group(1)
    title = re.sub(r"\.", " ", title)
    return title
