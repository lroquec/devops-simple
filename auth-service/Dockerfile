# Build stage
FROM python:3.12-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libmariadb-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.12-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libmariadb3 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable:
ENV PATH=/root/.local/bin:$PATH

# Copy application
COPY . .

# Create non-root user
RUN useradd -m appuser && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 5000

# Start gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]