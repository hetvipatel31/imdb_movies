import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

load_dotenv()

# Database configuration from .env
DB_CONFIG = {
    "dbname": os.getenv("DB_NAME", "sampledb"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "hetvi31"),
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432")
}

def init_db():
    """
    Initialize the database by connecting to the default 'postgres' database
    and creating 'sampledb' if it doesn't exist.
    """
    conn = None
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"]
        )
        conn.autocommit = True
        cur = conn.cursor()

        db_name = DB_CONFIG["dbname"]
        cur.execute(sql.SQL("CREATE DATABASE {}").format(
            sql.Identifier(db_name)
        ))
        print(f"Database '{db_name}' created.")
    except psycopg2.errors.DuplicateDatabase:
        print(f"Database '{db_name}' already exists.")
    except psycopg2.Error as e:
        print(f"Error creating database: {e}")
    finally:
        if conn:
            if 'cur' in locals():
                cur.close()
            conn.close()

def get_db_connection():
    """
    Returns a connection to the 'sampledb' database.
    """
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None