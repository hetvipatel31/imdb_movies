import requests
import json
from database.repository import store_movies

API_ENDPOINT = "https://imdb.iamidiotareyoutoo.com/search"

def fetch_movies(query: str):
    """
    Fetch movie data by title search from the external API.
    """
    print(f"Fetching movies for query: '{query}' from {API_ENDPOINT}")
    try:
        resp = requests.get(API_ENDPOINT, params={"q": query})
        resp.raise_for_status()
        json_response = resp.json()
        print("\n--- Raw API Response (JSON) ---")
        print(json.dumps(json_response, indent=2))
        print("-------------------------------\n")

        if isinstance(json_response, dict) and "description" in json_response:
            movies_list = json_response["description"]
            if isinstance(movies_list, list):
                print(f"Found {len(movies_list)} movies under 'description' key.")
                return movies_list
            else:
                print(f"Warning: 'description' key does not contain a list. Type: {type(movies_list)}")
                return []
        else:
            print(f"Warning: 'description' key not found or response is not a dictionary. Response type: {type(json_response)}")
            return []
    except requests.exceptions.RequestException as e:
        print(f"Error fetching movies: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"API Error Response Text: {e.response.text}")
        return []

def fetch_and_store_movies(title: str):
    """
    Fetches movies for a given title and stores them in the database.
    """
    movies = fetch_movies(title)
    if movies:
        store_movies(movies)
    return {"fetched_count": len(movies), "title": title}

def get_movies_from_db():
    """
    Retrieves all movies from the database (wrapper for repository function).
    """
    from database.repository import get_movies_from_db
    return get_movies_from_db()