# Stage 1: Build environment
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Install system dependencies needed for building wheels (e.g., gcc)
# Only install build-essential if necessary for your dependencies
# psutil usually builds fine without it on slim images if wheel is available
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install build tools first (best practice)
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Copy requirements file
COPY requirements.txt .

# Install Python packages using wheels where possible
# This installs dependencies needed at runtime AND build time in this stage
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Production image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variable for Python (optional but good practice)
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install only runtime system dependencies if any (often none needed if using slim)
# RUN apt-get update && apt-get install -y --no-install-recommends <runtime-deps> && rm -rf /var/lib/apt/lists/*

# Copy installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source code (respects .dockerignore)
COPY . .

# Create log and model directories and set permissions if needed
# Run as non-root user for better security
RUN groupadd -r flaskuser && useradd --no-log-init -r -g flaskuser flaskuser \
    && mkdir -p /app/logs /app/models \
    && chown -R flaskuser:flaskuser /app \
    && chmod -R 755 /app # Ensure execute permissions if needed

# Switch to non-root user
USER flaskuser

# Expose the port the app runs on
EXPOSE 5000

# Command to run the application using Gunicorn
# Use environment variables for Gunicorn settings if preferred
# Example: CMD ["gunicorn", "-b", "0.0.0.0:5000", "--workers", "2", "run:app"]
CMD ["gunicorn", "-b", "0.0.0.0:5000", "run:app"]