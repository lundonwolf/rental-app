# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies if needed (e.g., for specific Python packages)
# RUN apt-get update && apt-get install -y --no-install-recommends some-package && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# Use --no-cache-dir to reduce image size
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the application code into the container at /app
# Copy src directory and the main entrypoint if it were outside src
COPY src/ ./src/
# Copy the venv activate script - might not be strictly needed if not sourcing directly, but good practice
# COPY venv/bin/activate ./venv/bin/activate 

# Create the instance directory where the SQLite DB will live
# Ensure the directory exists and has correct permissions if needed
RUN mkdir -p /app/instance

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variables (optional, can be set in docker-compose)
# ENV FLASK_APP=src.main:app
# ENV FLASK_RUN_HOST=0.0.0.0
ENV SECRET_KEY="change_this_in_production_env_variable"

# Define the command to run the application
# First, run the initialization function within the app context
# Then, use Gunicorn to serve the app
CMD ["sh", "-c", "python -c 	'from src.main import initialize_app; initialize_app()	' && gunicorn --bind 0.0.0.0:5000 src.main:app"]

