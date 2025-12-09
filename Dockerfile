# Multi-stage build for Django application with Tailwind CSS
FROM node:20-alpine AS node-builder

WORKDIR /app

# Copy package files and install Node dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy Tailwind config and source CSS
COPY tailwind.config.js postcss.config.js ./
COPY static/css/input.css ./static/css/input.css

# Build Tailwind CSS
RUN npm run build:css || npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify

# Python stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    libpq-dev \
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

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "Waiting for PostgreSQL..."\n\
while ! nc -z $DB_HOST $DB_PORT; do\n\
  sleep 0.1\n\
done\n\
echo "PostgreSQL started"\n\
\n\
echo "Running migrations..."\n\
python manage.py migrate --noinput\n\
\n\
echo "Collecting static files..."\n\
python manage.py collectstatic --noinput --clear\n\
\n\
echo "Starting server..."\n\
exec "$@"' > /entrypoint.sh && chmod +x /entrypoint.sh

# Install netcat for health checks
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "-c", "gunicorn_config.py", "kouekam_hub.wsgi:application"]

