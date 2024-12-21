FROM python:3.13-slim-bookworm AS builder

# Set working directory
WORKDIR /app

# Install system dependencies for mysql
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev \
    libmariadb-dev-compat \
    pkg-config \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --target=/app/dependencies -r requirements.txt

# Stage 2
FROM python:3.13-slim-bookworm

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libmariadb3 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /app/dependencies /usr/local/lib/python3.13/site-packages

# Copy application files
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Environment variables
ENV PYTHONPATH=/usr/local/lib/python3.13/site-packages
ENV FLASK_APP=app/__init__.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Run the application with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--log-level", "info", "app:create_app()"]
