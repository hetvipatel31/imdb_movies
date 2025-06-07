# Movie Project

This is a FastAPI-based movie project.

## Requirements

- Docker

## Build and Run with Docker

1. **Clone the repository** (if not already done):

    ```sh
    git clone https://github.com/hetvipatel31/movieproject.git
    cd movieproject
    ```

2. **Build the Docker image:**

    ```sh
    docker build -t hetvipatel31/movieproject .
    ```

3. **Run the Docker container:**

    ```sh
    docker run -p 8000:8000 hetvipatel31/movieproject
    ```

4. **Access the API:**

    Open your browser and go to: [http://localhost:8000/docs](http://localhost:8000/docs)

## Docker Hub

You can find the published Docker image here:  
[https://hub.docker.com/repository/docker/hetvipatel31/movieproject/general](https://hub.docker.com/repository/docker/hetvipatel31/movieproject/general)

## Project Structure

- `main.py` - FastAPI application entry point
- `req.txt` - Python dependencies
- `dockerfile` - Docker build instructions

## Notes

- Make sure port 8000 is available on your machine.
- You can push the image to Docker Hub with:

    ```sh
    docker push hetvipatel31/movieproject:latest
    ```