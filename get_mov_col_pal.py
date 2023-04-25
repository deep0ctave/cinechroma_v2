from PIL import Image, ImageDraw, ImageFont
import os
import numpy as np
from sklearn.cluster import KMeans
import subprocess

def get_color_palette(video_file,movie_title,frame_directory,movie_data):
    # Initialize an empty list to store the colors for all images
    all_colors = []

    # Loop through all the images in the directory
    for filename in sorted(os.listdir(frame_directory)):
        if filename.endswith('.jpg') or filename.endswith('.png'): 
            # Open the image
            image_path = os.path.join(frame_directory, filename)
            image = Image.open(image_path)
            
            print(image_path)
            
            # Convert the image to a numpy array
            np_image = np.array(image)
            
            # Flatten the array to a 2D array
            np_image = np_image.reshape((np_image.shape[0] * np_image.shape[1], np_image.shape[2]))
            
            # Use KMeans clustering to find the 10 most common colors in the image
            kmeans = KMeans(n_clusters=10)
            kmeans.fit(np_image)
            colors = kmeans.cluster_centers_
            
            # Add the colors to the list of all colors
            all_colors.extend(colors)
    
    # Use KMeans clustering again to find the 10 most common colors across all images
    kmeans = KMeans(n_clusters=10)
    kmeans.fit(all_colors)
    dominant_colors = kmeans.cluster_centers_
    
    # Create a new image with the 10 dominant colors
    dominant_image = Image.new('RGB', (1000, 150), color=None)
    draw = ImageDraw.Draw(dominant_image) 
    x = 0
    ft = ImageFont.truetype("arial.ttf", 18, encoding="unic")
    
    rel_date = movie_data.get("Year")
    genre = movie_data.get("Genre")
    text = movie_title + " | " + rel_date + " | " + genre
    csv_col_hex = ","
    
    draw.text((x + 5, 5), text, fill=(255, 255, 255), font=ft, align ="left")
    for color in dominant_colors:
        color_tuple = tuple(map(int, color))
        dominant_image.paste(color_tuple, (x, 30, x + 100, 130))
        hex_value = '#' + ''.join([format(c, '02x') for c in color_tuple])
        csv_col_hex = csv_col_hex + hex_value + ","
        draw.text((x + 3, 133), hex_value, fill=(255, 255, 255))
        x += 100
    
    print(movie_title+","+csv_col_hex)
    
    width, height = dominant_image.size
    dominant_image= dominant_image.resize([width*2,height*2])
    dominant_image.save(movie_title + '_color_palette.png',dpi=(500,500))
    
    subprocess.call('rm -rf /home/avinash/cinechroma/frames/*', shell=True)
    
    
