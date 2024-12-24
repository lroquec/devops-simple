# Base image
FROM python:3.13-slim-bookworm AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /admin-service

# Install system dependencies
RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --target=/admin-service/dependencies -r requirements.txt

# Copy application code
COPY . .

# Stage 2
FROM python:alpine3.21

# Install system dependencies for mariadb-connector-c
RUN apk add --no-cache --force-overwrite gcc mariadb-connector-c-dev musl-dev && \
    pip install --no-cache-dir mysqlclient

# Create non-root user with explicit numeric IDs
RUN addgroup -S -g 1000 nonroot && \
    adduser -S -u 1000 -G nonroot nonroot

# Set the working directory
WORKDIR /admin-service

# Copy the dependencies from the builder image with correct ownership
COPY --from=builder --chown=1000:1000 /admin-service/dependencies /usr/local/lib/python3.13/site-packages

# Copy the application files with correct ownership
COPY --chown=1000:1000 . .

# Set PYTHONPATH
ENV PYTHONPATH=/usr/local/lib/python3.13/site-packages

# Switch to non-root user (use numeric ID for Kubernetes compatibility)
USER 1000

# Expose port 5000
EXPOSE 5000

# Command to run the application
CMD ["python", "main.py"]
