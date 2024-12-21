FROM python:3.13-slim-bookworm AS builder

# Set the working directory
WORKDIR /app

# Install system dependencies for mysqlclient
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev \
    libmariadb-dev-compat \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir --target=/app/dependencies -r requirements.txt

# Stage 2
FROM python:alpine3.21


# Install system dependencies for mariadb-connector-c
RUN apk add --no-cache --force-overwrite gcc mariadb-connector-c-dev musl-dev && \
    pip install --no-cache-dir mysqlclient

# Set the working directory
WORKDIR /app

# Copy the dependencies from the builder image
COPY --from=builder /app/dependencies /usr/local/lib/python3.13/site-packages

# Copy the application files
COPY . /app

# Set PYTHONPATH
ENV PYTHONPATH=/usr/local/lib/python3.13/site-packages

# Set the secret key. This is use for the hashing of the password of db
ENV SECRET_KEY=jlnjfnsfnbft358134k

RUN addgroup -S nonroot \
    && adduser -S nonroot -G nonroot

# Expose the application port
EXPOSE 5000

USER nonroot

# Command to run the application
CMD ["python", "main.py"]