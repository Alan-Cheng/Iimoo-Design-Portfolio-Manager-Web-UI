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

# Make port 30678 available to the world outside this container
EXPOSE 8080

# Define environment variable for demo mode
ENV ADMIN_PASSWORD=demo123
ENV SECRET_KEY=demo-secret-key

# Run app_demo.py when the container launches (Demo version)
CMD ["python", "app_demo.py"]