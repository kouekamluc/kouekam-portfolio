# Multi-stage build for Django application with Tailwind CSS
FROM node:20-alpine AS node-builder

WORKDIR /app

# Copy package files and install Node dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy Tailwind config
COPY tailwind.config.js postcss.config.js ./
# Copy input.css (Docker will create directory structure automatically)
COPY static/css/input.css ./static/css/

# Build Tailwind CSS (without watch mode for Docker build)
RUN npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify

# Python stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies (including netcat for health checks)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    netcat-traditional \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Copy built CSS from node-builder stage
COPY --from=node-builder /app/static/css/output.css ./static/css/output.css

# Create necessary directories
RUN mkdir -p staticfiles media logs

# Copy and set permissions for entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "-c", "gunicorn_config.py", "kouekam_hub.wsgi:application"]

