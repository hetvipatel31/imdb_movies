# Movie IMDb Ratings API

This project is a FastAPI-based web service for working with IMDb movie ratings. It uses PostgreSQL for data storage and is containerized with Docker.

## Features

- FastAPI backend
- PostgreSQL database support
- Dockerized for easy deployment

## Requirements

- Docker
- Docker Compose (optional, if you want to run a database as well)

## Setup

### 1. Clone the repository

```sh
git clone <your-repo-url>
cd imdb_movies
```

### 2. Build the Docker image

```sh
docker build -t manaanshshah/movie_final_assginment .
```

### 3. Run the Docker container

```sh
docker run -p 8000:8000 manaanshshah/movie_final_assginment
```

The API will be available at [http://localhost:8000](http://localhost:8000).

### 4. Environment Variables

If your app uses environment variables (e.g., for database connection), create a `.env` file in the project root. Example:

```
DATABASE_URL=postgresql://user:password@host:port/dbname
```
## Docker Hub Repositiory
DockerHub url= https://hub.docker.com/repository/docker/manaanshshah/movie_final_assginment/general

## API Documentation

Once running, visit [http://localhost:8000/docs](http://localhost:8000/docs) for the interactive Swagger UI.

## Development

To run locally without Docker:

1. Install Python 3.11
2. Install dependencies:
    ```sh
    pip install -r req.txt
    ```
3. Start the server:
    ```sh
    uvicorn main:app --reload
    ```

## License

MIT

