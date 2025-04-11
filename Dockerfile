# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables for Python
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install git and other potential dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
# This respects the .dockerignore file
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable for the GitHub token (must be provided at runtime)
# We don't set a default value here to avoid leaking it if not provided.
# The application's load_dotenv() will handle it if .env exists locally, 
# but in Docker, it should rely on the runtime environment variable.
ENV GITHUB_TOKEN=dummy_token_placeholder 
# Note: The application code (git_operations.py) reads GITHUB_TOKEN via os.getenv.
# When running the container, use `docker run -e GITHUB_TOKEN="your_actual_token" ...`

# Run app.py when the container launches
# The app itself handles cloning the repo if needed on startup.
CMD ["python", "app.py"]