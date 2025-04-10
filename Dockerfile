# Stage 1: Build environment
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install system dependencies and Python packages (including build tools like setuptools, wheel, and build)
RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev build-essential \
    && pip install --no-cache-dir setuptools wheel build \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*  # Clean up after install

# Stage 2: Production image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy only required files from builder stage (installed Python packages)
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application source code
COPY . .

# Expose port 5000
EXPOSE 5000

# Run the Flask app with Gunicorn for production
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
