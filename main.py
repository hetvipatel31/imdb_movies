from fastapi import FastAPI, HTTPException
from services.movie_services import fetch_and_store_movies, get_movies_from_db
from models.movies import MovieUpdate

app = FastAPI()

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Movie API! Use /fetch_and_store to populate movies."}

@app.get("/fetch_and_store/{title}")
async def fetch_and_store_movies_api(title: str):
    """
    Fetches movies for a given title from the external API and stores them in the database.
    """
    print(f"API endpoint /fetch_and_store/{title} called.")
    result = fetch_and_store_movies(title)
    if result["fetched_count"] > 0:
        return {
            "status": "success",
            "fetched_count": result["fetched_count"],
            "title": title,
            "message": "Movies fetched and attempted to store."
        }
    else:
        return {
            "status": "failed",
            "fetched_count": 0,
            "title": title,
            "message": "No movies fetched. Check API response or query."
        }

@app.get("/movies_in_db")
async def get_movies():
    """
    Retrieves all movies currently stored in the database.
    """
    return get_movies_from_db()

@app.delete("/delete_movie/{imdb_id}")
async def delete_movie(imdb_id: str):
    """
    Deletes a movie from the database by imdb_id.
    """
    from database.repository import delete_movie_from_db
    return delete_movie_from_db(imdb_id)

@app.patch("/update_movie/{imdb_id}")
async def update_movie(imdb_id: str, movie: MovieUpdate):
    """
    Updates a movie in the database by imdb_id.
    """
    from database.repository import update_movie_in_db
    return update_movie_in_db(imdb_id, movie)