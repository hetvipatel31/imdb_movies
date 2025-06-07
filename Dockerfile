FROM python:3.11-slim


WORKDIR /app

# Copy all project files into the container
COPY . .


RUN pip install --no-cache-dir -r req.txt


EXPOSE 8000


CMD ["uvicorn", "api.app:app", "--reload", "--host", "0.0.0.0"]