#!/bin/bash
# Production management script for Kouekam Portfolio Hub
# Usage: ./manage_production.sh [command]

set -e

case "$1" in
    collectstatic)
        echo "Collecting static files..."
        python manage.py collectstatic --noinput
        ;;
    migrate)
        echo "Running database migrations..."
        python manage.py migrate
        ;;
    createsuperuser)
        echo "Creating superuser..."
        python manage.py createsuperuser
        ;;
    check)
        echo "Checking deployment configuration..."
        python manage.py check --deploy
        ;;
    shell)
        python manage.py shell
        ;;
    backup)
        if [ -z "$DATABASE_URL" ]; then
            echo "DATABASE_URL not set. Cannot backup."
            exit 1
        fi
        echo "Backing up database..."
        BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
        pg_dump $DATABASE_URL > $BACKUP_FILE
        echo "Backup saved to: $BACKUP_FILE"
        ;;
    deploy)
        echo "Running production deployment..."
        python manage.py check --deploy
        python manage.py migrate
        python manage.py collectstatic --noinput
        echo "Deployment complete! Restart your application server."
        ;;
    *)
        echo "Usage: $0 {collectstatic|migrate|createsuperuser|check|shell|backup|deploy}"
        echo ""
        echo "Commands:"
        echo "  collectstatic    - Collect static files"
        echo "  migrate          - Run database migrations"
        echo "  createsuperuser  - Create a superuser account"
        echo "  check            - Check deployment configuration"
        echo "  shell            - Open Django shell"
        echo "  backup           - Backup database (requires DATABASE_URL)"
        echo "  deploy           - Run full deployment (check, migrate, collectstatic)"
        exit 1
        ;;
esac

