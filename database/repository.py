import psycopg2
from database.connection import get_db_connection
from fastapi import HTTPException

def create_movies_table():
    """
    Creates the movies table if it doesn't exist.
    """
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database for table creation.")
        return

    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                imdb_id TEXT PRIMARY KEY,
                title TEXT,
                year TEXT,
                type TEXT,
                poster TEXT
            );
        """)
        conn.commit()
        print("Movies table created or already exists.")
    except psycopg2.Error as e:
        print(f"Error creating movies table: {e}")
        if conn:
            conn.rollback()
    finally:
        if 'cur' in locals():
            cur.close()
        if conn:
            conn.close()

def create_dummy_table():
    """
    Creates the dummy_table if it doesn't exist.
    """
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database for table creation.")
        return

    try:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS dummy_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                age INT
            );
        """)
        conn.commit()
        print("Dummy table created or already exists.")
    except psycopg2.Error as e:
        print(f"Error creating dummy table: {e}")
        if conn:
            conn.rollback()
    finally:
        if 'cur' in locals():
            cur.close()
        if conn:
            conn.close()

def store_movies(movies: list):
    """
    Insert movies into the movies table.
    """
    if not movies:
        print("No movies to store. Skipping DB insertion.")
        return

    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database for movie insertion.")
        return

    try:
        cur = conn.cursor()
        data_to_insert = []
        for i, m in enumerate(movies):
            imdb_id = m.get("#IMDB_ID")
            title = m.get("#TITLE")
            year = m.get("#YEAR")
            m_type = "Movie"  # Assuming 'Movie' as default
            poster = m.get("#IMG_POSTER")

            if year is not None:
                year = str(year)
            else:
                print(f"Warning: Year missing for movie {i+1}. Setting to 'N/A'.")
                year = "N/A"

            if all([imdb_id, title, year, poster]) and \
               all(isinstance(val, str) and val.strip() for val in [imdb_id, title, year, poster]):
                data_to_insert.append((imdb_id, title, year, m_type, poster))
            else:
                print(f"Skipping movie {i+1} due to missing or invalid data: "
                      f"imdbID='{imdb_id}', Title='{title}', Year='{year}', Type='{m_type}', Poster='{poster}'")

        if data_to_insert:
            cur.executemany("""
                INSERT INTO movies (imdb_id, title, year, type, poster)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (imdb_id) DO NOTHING;
            """, data_to_insert)
            conn.commit()
            print(f"Successfully committed {len(data_to_insert)} movie(s) to DB.")
        else:
            print("No valid movies to insert after filtering.")
    except psycopg2.Error as e:
        print(f"Error during movie insertion: {e}")
        if conn:
            conn.rollback()
    finally:
        if 'cur' in locals():
            cur.close()
        if conn:
            conn.close()

def get_movies_from_db():
    """
    Retrieves all movies from the database.
    """
    conn = get_db_connection()
    if not conn:
        return {"status": "error", "message": "Could not connect to database."}

    try:
        cur = conn.cursor()
        cur.execute("SELECT imdb_id, title, year, type, poster FROM movies;")
        columns = [desc[0] for desc in cur.description]
        movies_from_db = [dict(zip(columns, row)) for row in cur.fetchall()]
        cur.close()
        return {"status": "success", "count": len(movies_from_db), "movies": movies_from_db}
    except psycopg2.Error as e:
        print(f"Error retrieving movies from DB: {e}")
        return {"status": "error", "message": f"Could not retrieve movies: {e}"}
    finally:
        if conn:
            conn.close()

def delete_movie_from_db(imdb_id: str):
    """
    Deletes a movie from the database by imdb_id.
    """
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error.")

    try:
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

def update_movie_in_db(imdb_id: str, movie):
    """
    Updates a movie in the database by imdb_id.
    """
    update_fields = {k: v for k, v in movie.dict().items() if v is not None}
    if not update_fields:
        raise HTTPException(status_code=400, detail="No valid fields to update.")

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error.")

    try:
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

def insert_dummy_data(name: str, age: int):
    """
    Inserts dummy data into dummy_table.
    """
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database for dummy data insertion.")
        return

    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO dummy_table (name, age) VALUES (%s, %s);", (name, age))
        conn.commit()
        print(f"Inserted: {name}, {age}")
    except psycopg2.Error as e:
        print(f"Error inserting dummy data: {e}")
        if conn:
            conn.rollback()
    finally:
        if 'cur' in locals():
            cur.close()
        if conn:
            conn.close()

def read_dummy_data():
    """
    Reads dummy data from dummy_table where name = 'Alice'.
    """
    conn = get_db_connection()
    if not conn:
        print("Failed to connect to database for dummy data retrieval.")
        return

    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM dummy_table WHERE name = %s;", ("Alice",))
        rows = cur.fetchall()
        print("Data from dummy_table:")
        for row in rows:
            print(row)
    except psycopg2.Error as e:
        print(f"Error reading dummy data: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if conn:
            conn.close()