# Base image
FROM python:3.13-slim-bookworm AS builder

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Set the working directory
WORKDIR /admin-service

# Install system dependencies
RUN apt-get update && apt-get install --no-install-recommends -y build-essential
RUN apt-get install default-libmysqlclient-dev -y
RUN apt-get install pkg-config -y && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /admin-service

# Copy application code
COPY . /admin-service/

# Install Python dependencies
COPY requirements.txt /admin-service/
RUN pip install --no-cache-dir --target=/admin-service/dependencies -r requirements.txt

# Stage 2
FROM python:alpine3.21

# Install system dependencies for mariadb-connector-c
RUN apk add --no-cache --force-overwrite gcc mariadb-connector-c-dev musl-dev && \
    pip install --no-cache-dir mysqlclient

# Set the working directory
WORKDIR /admin-service

# Copy the dependencies from the builder image
COPY --from=builder /admin-service/dependencies /usr/local/lib/python3.13/site-packages

# Copy the application files
COPY . /admin-service

# Set PYTHONPATH
ENV PYTHONPATH=/usr/local/lib/python3.13/site-packages

# Set the secret key. This is use for the hashing of the password of db
ENV SECRET_KEY=jlnjfnsfnbft358134k

RUN addgroup -S nonroot \
    && adduser -S nonroot -G nonroot

# Expose port 5000
EXPOSE 5000

# Command to run the application
CMD ["python", "main.py"]
