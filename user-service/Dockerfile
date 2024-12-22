FROM python:3.13-slim-bookworm AS builder

# Set the working directory
WORKDIR /user-service

# Install system dependencies for mysqlclient
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev \
    libmariadb-dev-compat \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy application files
COPY . /user-service

# Install Python dependencies
RUN pip install --no-cache-dir --target=/user-service/dependencies -r requirements.txt

# Stage 2
FROM python:alpine3.21

# Install system dependencies for mariadb-connector-c
RUN apk add --no-cache --force-overwrite gcc mariadb-connector-c-dev musl-dev && \
    pip install --no-cache-dir mysqlclient

# Set the working directory
WORKDIR /user-service

# Copy the dependencies from the builder image
COPY --from=builder /user-service/dependencies /usr/local/lib/python3.13/site-packages

# Copy the application files
COPY . /user-service

# Set PYTHONPATH
ENV PYTHONPATH=/usr/local/lib/python3.13/site-packages

RUN addgroup -S nonroot \
    && adduser -S nonroot -G nonroot

# Expose the application port
EXPOSE 5000

USER nonroot

# Command to run the application
CMD ["python", "main.py"]