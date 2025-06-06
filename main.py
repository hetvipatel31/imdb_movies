import requests
import psycopg2
import json
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional

# --- CONFIGURATION ---
API_ENDPOINT = "https://imdb.iamidiotareyoutoo.com/search"
DB_CONFIG = {
    "dbname": "sampledb",
    "user": "postgres",
    "password": "hetvi31",
    "host": "localhost",
    "port": "5432"
}

# --- FastAPI Setup ---
app = FastAPI()

# --- MODIFIED FETCH_MOVIES FUNCTION ---

def fetch_movies(query: str):
    """Fetch movie data by title search."""
    print(f"Fetching movies for query: '{query}' from {API_ENDPOINT}")
    try:
        resp = requests.get(API_ENDPOINT, params={"q": query})
        resp.raise_for_status() # Raises an HTTPError for bad responses (4xx or 5xx)

        json_response = resp.json()
        print("\n--- Raw API Response (JSON) ---")
        print(json.dumps(json_response, indent=2))
        print("-------------------------------\n")

        # --- CRITICAL CHANGE 1: Accessing the correct key for the movie list ---
        if isinstance(json_response, dict) and "description" in json_response:
            # The API returns a dictionary with an "ok" status and a "description" key containing the list.
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

# --- MODIFIED STORE_MOVIES FOR CORRECT KEY NAMES ---

def store_movies(movies: list):
    """Insert movies into PostgreSQL table."""
    if not movies:
        print("No movies to store. Skipping DB insertion.")
        return

    conn = None
    try:
        print("Attempting to connect to the database...")
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        print("Successfully connected to the database.")

        print("Executing CREATE TABLE IF NOT EXISTS...")
        cur.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                imdb_id TEXT PRIMARY KEY,
                title TEXT,
                year TEXT,
                type TEXT,
                poster TEXT
            );
        """)
        print("CREATE TABLE IF NOT EXISTS command executed.")

        data_to_insert = []
        for i, m in enumerate(movies):
            # --- CRITICAL CHANGE 2: Using the correct hashed key names from API response ---
            imdb_id = m.get("#IMDB_ID")
            title = m.get("#TITLE")
            year = m.get("#YEAR") # Note: This is an int from API, will be converted to string for TEXT column
            m_type = "Movie" # The API output doesn't seem to have a specific 'Type' key. Assuming 'Movie' for simplicity.
                             # If API has a #TYPE key, use m.get("#TYPE")
            poster = m.get("#IMG_POSTER")

            # Basic validation
            # Convert year to string as our DB column is TEXT
            if year is not None:
                year = str(year)
            else:
                print(f"Warning: Year missing for movie {i+1}. Setting to 'N/A'.")
                year = "N/A" # Default for missing year

            # Check if all critical fields are present and valid for insertion
            if all([imdb_id, title, year, poster]) and \
               all(isinstance(val, str) and val.strip() for val in [imdb_id, title, year, poster]):
                data_to_insert.append((imdb_id, title, year, m_type, poster))
            else:
                print(f"Skipping movie {i+1} due to missing or invalid data after mapping: "
                      f"imdbID='{imdb_id}', Title='{title}', Year='{year}', Type='{m_type}', Poster='{poster}'")
                print(f"Original movie object: {m}")


        if data_to_insert:
            print(f"Prepared {len(data_to_insert)} valid movie(s) for insertion.")
            try:
                cur.executemany("""
                    INSERT INTO movies (imdb_id, title, year, type, poster)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (imdb_id) DO NOTHING;
                """, data_to_insert)
                print("executemany command executed.")
                conn.commit()
                print(f"Successfully committed {len(data_to_insert)} movie(s) to DB.")
            except psycopg2.IntegrityError as e:
                print(f"Integrity Error during insertion (e.g., primary key conflict): {e}")
                if conn: conn.rollback()
            except psycopg2.Error as e:
                print(f"Error during executemany or commit: {e}")
                if conn: conn.rollback()
        else:
            print("No valid movies to insert after filtering for missing data. Check API response structure and key mapping.")

        cur.close()
    except psycopg2.OperationalError as e:
        print(f"Database connection error (OperationalError): {e}")
        print("Please check your DB_CONFIG: dbname, user, password, host, port. Is PostgreSQL running?")
    except psycopg2.Error as e:
        print(f"General Database error: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

# --- MAIN FUNCTION (for direct script execution) ---
def run_script():
    title = "Spiderman"
    movies = fetch_movies(title)

    if movies:
        print(f"Fetched {len(movies)} movies for '{title}'. Attempting to store.")
        store_movies(movies)
        print("Finished storing movie data in DB (if any).")

        # Optional: display stored data from DB
        conn = None
        try:
            print("\n--- Retrieving all stored movies from DB ---")
            conn = psycopg2.connect(**DB_CONFIG)
            cur = conn.cursor()
            cur.execute("SELECT imdb_id, title, year, type, poster FROM movies;")
            for row in cur.fetchall():
                print(row)
            cur.close()
        except psycopg2.Error as e:
            print(f"Error retrieving stored movies: {e}")
        finally:
            if conn:
                conn.close()
                print("Database retrieval connection closed.")
    else:
        print(f"No movies fetched for '{title}'. Skipping database operations.")

# --- FastAPI Endpoints ---

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Movie API! Use /fetch_and_store to populate movies."}

@app.get("/fetch_and_store/{title}")
async def fetch_and_store_movies_api(title: str):
    """
    Fetches movies for a given title from the external API and stores them in the database.
    """
    print(f"API endpoint /fetch_and_store/{title} called.")
    movies = fetch_movies(title)
    if movies:
        store_movies(movies)
        return {"status": "success", "fetched_count": len(movies), "title": title, "message": "Movies fetched and attempted to store."}
    else:
        return {"status": "failed", "fetched_count": 0, "title": title, "message": "No movies fetched. Check API response or query."}

@app.get("/movies_in_db")
async def get_movies_from_db():
    """
    Retrieves all movies currently stored in the database.
    """
    conn = None
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT imdb_id, title, year, type, poster FROM movies;")
        columns = [desc[0] for desc in cur.description]
        movies_from_db = []
        for row in cur.fetchall():
            movies_from_db.append(dict(zip(columns, row)))
        cur.close()
        return {"status": "success", "count": len(movies_from_db), "movies": movies_from_db}
    except psycopg2.Error as e:
        print(f"Error retrieving movies from DB via API: {e}")
        return {"status": "error", "message": f"Could not retrieve movies from database: {e}"}
    finally:
        if conn:
            conn.close()
class MovieUpdate(BaseModel):
    title: Optional[str] = None
    year: Optional[str] = None
    type: Optional[str] = None
    poster: Optional[str] = None

@app.delete("/delete_movie/{imdb_id}")
async def delete_movie(imdb_id: str):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("DELETE FROM movies WHERE imdb_id = %s RETURNING *;", (imdb_id,))
        deleted = cur.fetchone()
        conn.commit()
        cur.close()
        if not deleted:
            raise HTTPException(status_code=404, detail="Movie not found.")
        return {"status": "success", "message": f"Movie with imdb_id {imdb_id} deleted."}
    except psycopg2.Error as e:
        print(f"Error deleting movie: {e}")
        raise HTTPException(status_code=500, detail="Database error.")
    finally:
        if conn:
            conn.close()

@app.patch("/update_movie/{imdb_id}")
async def update_movie(imdb_id: str, movie: MovieUpdate):
    update_fields = {k: v for k, v in movie.dict().items() if v is not None}
    if not update_fields:
        raise HTTPException(status_code=400, detail="No valid fields to update.")

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()

        set_clause = ", ".join([f"{key} = %s" for key in update_fields])
        values = list(update_fields.values())
        values.append(imdb_id)

        query = f"UPDATE movies SET {set_clause} WHERE imdb_id = %s RETURNING *;"
        cur.execute(query, values)
        updated = cur.fetchone()
        conn.commit()
        cur.close()

        if not updated:
            raise HTTPException(status_code=404, detail="Movie not found.")

        return {"status": "success", "message": f"Movie with imdb_id {imdb_id} updated."}
    except psycopg2.Error as e:
        print(f"Error updating movie: {e}")
        raise HTTPException(status_code=500, detail="Database error.")
    finally:
        if conn:
            conn.close()

# --- Conditional execution for direct script run vs. uvicorn ---
if __name__ == "__main__":
    print("Running script directly to test DB insertion...")
    run_script()
    # To run FastAPI, comment out `run_script()` and run uvicorn from your terminal:
    # uvicorn your_file_name:app --reload