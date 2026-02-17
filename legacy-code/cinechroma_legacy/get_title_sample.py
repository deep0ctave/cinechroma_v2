import re

filename = "movie.2022.1080p.bluray.x264.title.with.dots.mkv"

title = re.search(r"^(.+?)\.\d{4}\.", filename).group(1)
title = re.sub(r"\.", " ", title)

print(title) # "movie"

