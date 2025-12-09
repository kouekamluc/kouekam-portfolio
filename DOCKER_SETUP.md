# Docker Setup Guide

This project is configured to run automatically with Docker and Docker Compose. All necessary commands (migrations, static file collection, server startup) run automatically.

## Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose)
- Git

## Quick Start

1. **Copy environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file** with your configuration (at minimum, set `SECRET_KEY`)

3. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```

   Or run in detached mode:
   ```bash
   docker-compose up -d --build
   ```

4. **Access the application:**
   - Web: http://localhost:8000
   - Database: localhost:5432

## What Runs Automatically

When you start Docker Compose, the following happens automatically:

1. **PostgreSQL Database** starts and becomes healthy
2. **Django Application** waits for database
3. **Migrations** run automatically (`python manage.py migrate`)
4. **Superuser** is created automatically (username: `kouekam`, password: `kklkinkklk`) if it doesn't exist
5. **Static Files** are collected automatically (`python manage.py collectstatic`)
6. **Tailwind CSS** is built during Docker image build
7. **Gunicorn Server** starts and serves the application

## Docker Services

- **`db`**: PostgreSQL 15 database
- **`web`**: Django application with Gunicorn

## Common Commands

### Start services
```bash
docker-compose up
```

### Start in background
```bash
docker-compose up -d
```

### Stop services
```bash
docker-compose down
```

### Stop and remove volumes (deletes database data)
```bash
docker-compose down -v
```

### View logs
```bash
docker-compose logs -f
```

### View logs for specific service
```bash
docker-compose logs -f web
docker-compose logs -f db
```

### Rebuild after code changes
```bash
docker-compose up --build
```

### Run Django management commands
```bash
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py shell
docker-compose exec web python manage.py collectstatic
```

### Default Superuser

A superuser is automatically created on first startup:
- **Username**: `kouekam`
- **Password**: `kklkinkklk`
- **Email**: Set via `SUPERUSER_EMAIL` environment variable (defaults to `kouekam@example.com`)

You can log in to the Django admin at `/admin/` using these credentials.

### Access database
```bash
docker-compose exec db psql -U kouekam_user -d kouekam_db
```

## Environment Variables

Key environment variables (set in `.env` file):

- `SECRET_KEY`: Django secret key (required)
- `DEBUG`: Set to `True` for development, `False` for production
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Database credentials
- `DATABASE_URL`: Full database URL (auto-generated in docker-compose.yml)
- `OPENAI_API_KEY`: For AI assistant features (optional)
- `EMAIL_*`: Email configuration (optional)
- `SUPERUSER_EMAIL`: Email for the auto-created superuser (defaults to `kouekam@example.com`)

## Volumes

The following directories are mounted as volumes (persist between container restarts):

- `./media` → `/app/media` (user uploads)
- `./staticfiles` → `/app/staticfiles` (collected static files)
- `./logs` → `/app/logs` (application logs)
- `postgres_data` → PostgreSQL data (Docker volume)

## Troubleshooting

### Port already in use
If port 8000 or 5432 is already in use, change them in `.env`:
```
PORT=8001
DB_PORT=5433
```

### Database connection errors
Ensure the database service is healthy:
```bash
docker-compose ps
```

### Static files not loading
Rebuild the container to regenerate Tailwind CSS:
```bash
docker-compose up --build
```

### Permission errors
On Linux/Mac, you may need to fix permissions:
```bash
sudo chown -R $USER:$USER media staticfiles logs
```

## Production Deployment

For production:

1. Set `DEBUG=False` in `.env`
2. Set a strong `SECRET_KEY`
3. Configure proper `ALLOWED_HOSTS`
4. Set up proper email configuration
5. Consider using AWS S3 for media/static files (set `USE_S3=True`)
6. Use environment-specific `.env` file
7. Consider using Docker secrets for sensitive data

## Development vs Production

- **Development**: Uses SQLite if `DATABASE_URL` is not set
- **Production**: Uses PostgreSQL (configured via `DATABASE_URL`)

The entrypoint script automatically detects which database to use based on environment variables.

