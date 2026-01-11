# Multi-stage build: Stage 1 - Node.js for building CSS and JS
FROM node:20-slim AS node-builder

WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install Node.js dependencies (including devDependencies for building)
RUN npm ci

# Copy source files needed for building
COPY static/css/input.css ./static/css/
COPY static/js/tiptap-editor-source.js ./static/js/
COPY tailwind.config.js ./

# Build CSS and JS
RUN npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify
RUN npx esbuild ./static/js/tiptap-editor-source.js --bundle --format=iife --global-name=TiptapEditor --outfile=./static/js/tiptap-editor.js --minify

# Stage 2 - Python application
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
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies (including Brevo SDK for email service)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Copy built CSS and JS from node-builder stage
COPY --from=node-builder /app/static/css/output.css ./static/css/output.css
COPY --from=node-builder /app/static/js/tiptap-editor.js ./static/js/tiptap-editor.js

# Create necessary directories
RUN mkdir -p staticfiles media logs

# Copy and set permissions for entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "-c", "gunicorn_config.py", "kouekam_hub.wsgi:application"]

