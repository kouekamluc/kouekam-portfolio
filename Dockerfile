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

# Install system dependencies (including netcat for health checks and Node.js for CSS building)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
    netcat-traditional \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy package files and install npm dependencies first
# This ensures npm is available for CSS building if needed
COPY package.json package-lock.json ./
COPY tailwind.config.js postcss.config.js ./

# Install npm dependencies for runtime CSS building (if needed)
# Note: We need devDependencies for tailwindcss
RUN npm ci --silent || npm install --silent

# Copy built CSS from node-builder stage (ensures CSS is always available)
# This is the primary CSS file that will be used
COPY --from=node-builder /app/static/css/output.css ./static/css/output.css

# Copy project files (excluding node_modules and output.css which are in .dockerignore)
# This must come after npm install to avoid overwriting node_modules
COPY . .

# Verify CSS file exists and has content, rebuild if needed
RUN if [ ! -f "static/css/output.css" ] || [ ! -s "static/css/output.css" ]; then \
        echo "⚠ WARNING: CSS file is missing or empty after Docker build!" && \
        echo "Rebuilding CSS as fallback..." && \
        npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify || exit 1; \
    fi && \
    CSS_SIZE=$(wc -c < static/css/output.css 2>/dev/null || echo "0") && \
    if [ "$CSS_SIZE" -lt 1000 ]; then \
        echo "⚠ WARNING: CSS file is too small ($CSS_SIZE bytes), rebuilding..." && \
        npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify || exit 1; \
    fi && \
    echo "✓ CSS file verified and ready ($(wc -c < static/css/output.css) bytes)"

# Create necessary directories
RUN mkdir -p staticfiles media logs

# Copy and set permissions for entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "-c", "gunicorn_config.py", "kouekam_hub.wsgi:application"]

