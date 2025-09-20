# Dockerfile

# Start from a slim, official Python base image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies needed by FFmpeg and OpenCV
# Using libgl1 instead of libgl1-mesa-glx for better compatibility
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file first to leverage Docker's layer caching
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application's source code into the container
COPY . .

# Expose the port that Gunicorn will run on inside the container
EXPOSE 8080

# The default command to run when the container starts.
# This will be used by our 'app' service in docker-compose.
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "wsgi:app"]