#!/bin/bash
set -e

# Wait for PostgreSQL if DB_HOST is set (Docker Compose sets this)
# Railway uses DATABASE_URL, so check for that too
if [ -n "$DB_HOST" ]; then
    echo "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT:-5432}..."
    while ! nc -z ${DB_HOST} ${DB_PORT:-5432}; do
        sleep 0.1
    done
    echo "PostgreSQL started"
elif [ -n "$DATABASE_URL" ]; then
    echo "DATABASE_URL detected, using PostgreSQL (Railway/Heroku style)"
    # Extract host from DATABASE_URL if needed for health check
    # For Railway, the database is usually already available
else
    echo "No database configuration detected, using SQLite database"
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

# Check if using S3
if [ -n "$USE_S3" ] && [ "$USE_S3" = "True" ]; then
    echo "Using AWS S3 for static files..."
    echo "  Bucket: ${AWS_STORAGE_BUCKET_NAME:-not set}"
    echo "  Region: ${AWS_S3_REGION_NAME:-us-east-1}"
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Verify CSS file was properly collected
if [ -f "staticfiles/css/output.css" ]; then
    CSS_SIZE=$(wc -c < staticfiles/css/output.css)
    echo "✓ CSS collected to staticfiles ($CSS_SIZE bytes)"
    if [ "$CSS_SIZE" -eq 0 ]; then
        echo "⚠ WARNING: Collected CSS file is empty! This will cause a blank page."
        echo "   Checking source file..."
        if [ -f "static/css/output.css" ]; then
            SOURCE_SIZE=$(wc -c < static/css/output.css)
            echo "   Source CSS file size: $SOURCE_SIZE bytes"
            if [ "$SOURCE_SIZE" -gt 0 ]; then
                echo "   Attempting to manually copy CSS file..."
                mkdir -p staticfiles/css
                cp static/css/output.css staticfiles/css/output.css
                echo "   CSS file manually copied ($(wc -c < staticfiles/css/output.css) bytes)"
            fi
        fi
    else
        # Verify file is readable and has content
        FIRST_LINE=$(head -c 100 staticfiles/css/output.css)
        if [ -z "$FIRST_LINE" ]; then
            echo "⚠ WARNING: CSS file exists but appears to be empty or unreadable"
        else
            echo "✓ CSS file verified and readable"
        fi
    fi
else
    echo "⚠ WARNING: CSS file not found in staticfiles directory"
    echo "   Listing staticfiles/css directory:"
    ls -la staticfiles/css/ 2>/dev/null || echo "   Directory does not exist"
    echo "   Attempting to manually copy CSS file..."
    if [ -f "static/css/output.css" ]; then
        mkdir -p staticfiles/css
        cp static/css/output.css staticfiles/css/output.css
        echo "   CSS file manually copied ($(wc -c < staticfiles/css/output.css) bytes)"
    fi
fi

# Check ALLOWED_HOSTS configuration
if [ -z "$ALLOWED_HOSTS" ] || [ "$ALLOWED_HOSTS" = "localhost,127.0.0.1" ]; then
    echo "⚠️  WARNING: ALLOWED_HOSTS is not configured for production!"
    echo "   Set ALLOWED_HOSTS environment variable to include your domain(s)"
    echo "   Example: ALLOWED_HOSTS=kouekamkamgou.uk,www.kouekamkamgou.uk"
    echo "   Without this, you will get HTTP 400 errors when accessing your site."
fi

echo "Starting server..."
exec "$@"

