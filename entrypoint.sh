#!/bin/bash
set -e

# Wait for PostgreSQL if DB_HOST is set (Docker Compose sets this)
if [ -n "$DB_HOST" ]; then
    echo "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT:-5432}..."
    while ! nc -z ${DB_HOST} ${DB_PORT:-5432}; do
        sleep 0.1
    done
    echo "PostgreSQL started"
else
    echo "No DB_HOST set, using SQLite database"
fi

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating superuser (if not exists)..."
python create_superuser.py

# Build Tailwind CSS if Node.js is available and output.css doesn't exist or is empty
if command -v node &> /dev/null && command -v npm &> /dev/null; then
    echo "Building Tailwind CSS..."
    # Check if output.css exists and has content
    if [ ! -f "static/css/output.css" ] || [ ! -s "static/css/output.css" ]; then
        # Ensure node_modules exists
        if [ ! -d "node_modules" ]; then
            echo "Installing Node.js dependencies..."
            npm ci --silent || npm install --silent
        fi
        echo "Compiling Tailwind CSS..."
        npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify
        if [ -f "static/css/output.css" ] && [ -s "static/css/output.css" ]; then
            echo "✓ CSS built successfully ($(wc -c < static/css/output.css) bytes)"
        else
            echo "⚠ Warning: CSS build may have failed, but continuing..."
        fi
    else
        echo "✓ CSS file already exists ($(wc -c < static/css/output.css) bytes), skipping build"
    fi
else
    echo "Node.js not available, skipping CSS build (assuming CSS was built during Docker build)"
    if [ ! -f "static/css/output.css" ] || [ ! -s "static/css/output.css" ]; then
        echo "⚠ Warning: CSS file is missing or empty and Node.js is not available!"
    fi
fi

# Verify CSS file exists and has content before collecting static files
if [ ! -f "static/css/output.css" ] || [ ! -s "static/css/output.css" ]; then
    echo "❌ ERROR: CSS file is missing or empty after build attempt!"
    echo "   This will cause a blank page. Please check the build logs above."
    exit 1
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Check ALLOWED_HOSTS configuration
if [ -z "$ALLOWED_HOSTS" ] || [ "$ALLOWED_HOSTS" = "localhost,127.0.0.1" ]; then
    echo "⚠️  WARNING: ALLOWED_HOSTS is not configured for production!"
    echo "   Set ALLOWED_HOSTS environment variable to include your domain(s)"
    echo "   Example: ALLOWED_HOSTS=kouekamkamgou.uk,www.kouekamkamgou.uk"
    echo "   Without this, you will get HTTP 400 errors when accessing your site."
fi

echo "Starting server..."
exec "$@"

