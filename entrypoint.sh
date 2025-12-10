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

