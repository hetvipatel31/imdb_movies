# IMDb Movies Docker Setup

This guide explains how to build, run, and push the Docker image for the IMDb Movies application.

## Build the Docker Image

1. Open your terminal in the project directory.
2. Build the Docker image:

    ```powershell
    docker build -t dhruv_senkusha .
    ```

## Run the Container

Run the container and map port 8000 to access the application:

```powershell
docker run -p 8000:8000 dhruv_senkusha


## Push Docker Image to Docker Hub

1. Tag your image:
    ```bash
    docker tag dhruv_senkusha <your-dockerhub-username>/dhruv_senkusha
    ```

2. Log in to Docker Hub:
    ```bash
    docker login
    ```

3. Push the image:
    ```bash
    docker push <your-dockerhub-username>/dhruv_senkusha
    ```

You can now pull this image using:
```bash
docker pull dhruvvthaker/dhruv_senkusha:latest
