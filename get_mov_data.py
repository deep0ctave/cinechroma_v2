import os
import requests

def get_movie_details(movie_title):

    api_key = "59af6ad7"
    rel_date = "None"
    # Construct the OMdb API endpoint URL with the parameters
    url = f"http://www.omdbapi.com/?apikey={api_key}&t={movie_title}"

    # Make an HTTP GET request to the OMdb API endpoint
    response = requests.get(url)

    # Check if the request was successful (HTTP status code 200)
    if response.status_code == 200:
        # Convert the response data (JSON) to a Python dictionary
        movie_data = response.json()
        rel_date = movie_data.get("Year")
        genere = movie_data.get("Genre")
        # Print the movie data
        print(str(rel_date))
        print(str(genere))
    else:
        print(f"Error: {response.status_code}")
    return movie_data       
        
