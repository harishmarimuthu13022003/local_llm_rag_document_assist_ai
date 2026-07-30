# Multi-stage production Dockerfile for FastAPI Backend
FROM python:3.10-slim as base

WORKDIR /app

# Prevent Python from writing .pyc files and enable unbuffered logging stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Install system dependencies needed for compiling python dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy python requirements and install wheel packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . /app/backend

# Create runtime log and storage directories
RUN mkdir -p /app/logs /app/storage/chroma /app/storage/uploads

EXPOSE 8000

CMD ["python", "-m", "backend.main"]
