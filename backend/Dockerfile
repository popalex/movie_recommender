# Use an official Python runtime as a parent image
FROM python:3.13-slim

# Set the working directory in the container
WORKDIR /app/backend

# Copy the requirements file into the container at /app/backend
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
# --no-cache-dir reduces image size
# --default-timeout=100 to prevent timeouts on slow connections
# --retries=5 to retry on transient network issues
RUN pip install --no-cache-dir --default-timeout=100 --retries=5 -r requirements.txt

# Copy the rest of the backend application code into the container at /app/backend
COPY ./app /app/backend/app

# Make port 8000 available to the world outside this container
# This is the port Uvicorn will run on, matching API_PORT in .env
EXPOSE 8000

# Define environment variable (can be overridden by docker-compose)
ENV PYTHONPATH=/app

# Run main.py when the container launches
# The host 0.0.0.0 makes it accessible from other Docker containers and the host machine
# The port should match API_PORT from .env and the EXPOSE instruction
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]