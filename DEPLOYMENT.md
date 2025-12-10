# Production Deployment Guide

This guide provides step-by-step instructions for deploying the Kouekam Portfolio Hub to production.

## Pre-Deployment Checklist

- [ ] All environment variables configured
- [ ] Database migrated and tested
- [ ] Static files collected
- [ ] Media files uploaded to S3 (if using)
- [ ] Email configuration tested
- [ ] Security settings reviewed
- [ ] SSL certificate configured
- [ ] Domain DNS configured
- [ ] Backup strategy in place

## Environment Variables Setup

Create a `.env` file in the project root with the following variables (see `.env.example` for template):

### Required Variables

```bash
# Django Core
SECRET_KEY=your-generated-secret-key-here  # Generate with: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL recommended for production)
DATABASE_URL=postgres://user:password@host:port/dbname

# Email (Required for account verification and notifications)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### Optional Variables

```bash
# OpenAI (for AI Assistant features)
OPENAI_API_KEY=your-openai-api-key

# AWS S3 (for static/media file storage)
USE_S3=True
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# Allauth
ACCOUNT_EMAIL_VERIFICATION=mandatory  # or 'optional', 'none'

# Logging
DJANGO_LOG_LEVEL=INFO  # or 'DEBUG', 'WARNING', 'ERROR'
```

## Database Setup

### PostgreSQL Setup

1. **Install PostgreSQL** (if not already installed)
2. **Create database and user**:
   ```sql
   CREATE DATABASE kouekam_hub;
   CREATE USER kouekam_user WITH PASSWORD 'secure_password';
   GRANT ALL PRIVILEGES ON DATABASE kouekam_hub TO kouekam_user;
   ALTER USER kouekam_user CREATEDB;  # Required for Django tests
   ```

3. **Update DATABASE_URL** in `.env`:
   ```
   DATABASE_URL=postgres://kouekam_user:secure_password@localhost:5432/kouekam_hub
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

## Static Files Configuration

### Important: Build CSS First

**Before collecting static files, you must build the Tailwind CSS:**

```bash
# Build CSS for production
npm ci
npm run build:css:prod

# Or use the build script
chmod +x build.sh
./build.sh
```

The CSS file (`static/css/output.css`) is gitignored and must be built during deployment.

### Option 1: Using WhiteNoise (Recommended for simpler deployments)

WhiteNoise is already configured in settings. Build CSS and collect static files:

```bash
# Build CSS first
npm ci && npm run build:css:prod

# Then collect static files
python manage.py collectstatic --noinput
```

### Option 2: Using AWS S3

1. **Create S3 bucket** with public read access
2. **Configure CORS** on the bucket:
   ```json
   [
       {
           "AllowedHeaders": ["*"],
           "AllowedMethods": ["GET", "HEAD"],
           "AllowedOrigins": ["https://yourdomain.com"],
           "ExposeHeaders": []
       }
   ]
   ```

3. **Set environment variables**:
   ```bash
   USE_S3=True
   AWS_ACCESS_KEY_ID=your-key
   AWS_SECRET_ACCESS_KEY=your-secret
   AWS_STORAGE_BUCKET_NAME=your-bucket-name
   AWS_S3_REGION_NAME=us-east-1
   ```

4. **Build CSS and collect static files**:
   ```bash
   # Build CSS first
   npm ci && npm run build:css:prod
   
   # Then collect and upload static files
   python manage.py collectstatic --noinput
   ```

## Server Configuration

### Using Gunicorn

1. **Install Gunicorn** (already in requirements.txt):
   ```bash
   pip install gunicorn
   ```

2. **Test locally**:
   ```bash
   gunicorn -c gunicorn_config.py kouekam_hub.wsgi:application
   ```

3. **Create systemd service** (Linux):

   Create `/etc/systemd/system/kouekam_hub.service`:
   ```ini
   [Unit]
   Description=Kouekam Hub Gunicorn daemon
   After=network.target

   [Service]
   User=www-data
   Group=www-data
   WorkingDirectory=/path/to/kouekam-portfolio-complete
   Environment="PATH=/path/to/venv/bin"
   ExecStart=/path/to/venv/bin/gunicorn -c gunicorn_config.py kouekam_hub.wsgi:application

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable kouekam_hub
   sudo systemctl start kouekam_hub
   ```

### Using Nginx as Reverse Proxy

Create `/etc/nginx/sites-available/kouekam_hub`:

```nginx
upstream django {
    server unix:/path/to/gunicorn.sock;  # Or 127.0.0.1:8000
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    client_max_body_size 20M;

    location /static/ {
        alias /path/to/kouekam-portfolio-complete/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /path/to/kouekam-portfolio-complete/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    location / {
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $http_host;
        proxy_redirect off;
        proxy_pass http://django;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/kouekam_hub /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Deployment Platforms

### Heroku

1. **Install Heroku CLI** and login
2. **Create app**:
   ```bash
   heroku create your-app-name
   ```

3. **Set environment variables**:
   ```bash
   heroku config:set SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
   heroku config:set DEBUG=False
   heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
   heroku config:set DATABASE_URL=$(heroku config:get DATABASE_URL)  # Auto-set by Heroku
   ```

4. **Set all other environment variables** via `heroku config:set`

5. **Deploy**:
   ```bash
   git push heroku main
   # The Procfile release phase will automatically:
   # - Install npm dependencies
   # - Build CSS (npm run build:css:prod)
   # - Collect static files
   heroku run python manage.py migrate
   heroku run python manage.py createsuperuser
   ```

### DigitalOcean App Platform

1. **Connect repository** to DigitalOcean
2. **Configure environment variables** in App Platform dashboard
3. **Set build command**: 
   ```bash
   npm ci && npm run build:css:prod && pip install -r requirements.txt && python manage.py collectstatic --noinput
   ```
4. **Set run command**: `gunicorn -c gunicorn_config.py kouekam_hub.wsgi:application`
5. **Deploy** via dashboard or git push

### AWS Elastic Beanstalk

1. **Install EB CLI**: `pip install awsebcli`
2. **Initialize**: `eb init`
3. **Create environment**: `eb create production`
4. **Set environment variables**: `eb setenv KEY=value`
5. **Deploy**: `eb deploy`

### Docker (Alternative)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "-c", "gunicorn_config.py", "kouekam_hub.wsgi:application"]
```

Build and run:
```bash
docker build -t kouekam-hub .
docker run -p 8000:8000 --env-file .env kouekam-hub
```

## Post-Deployment Steps

1. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

2. **Load initial data** (if any):
   ```bash
   python manage.py loaddata fixtures/initial_data.json
   ```

3. **Verify deployment**:
   - Test all major features
   - Check static files loading
   - Test email functionality
   - Verify SSL certificate
   - Check error pages (404, 500, 403)

4. **Set up monitoring**:
   - Configure error logging (already set up)
   - Set up uptime monitoring
   - Configure backup schedule

5. **Set up backups**:
   ```bash
   # Database backup script
   pg_dump -U user dbname > backup_$(date +%Y%m%d).sql
   ```

## Security Checklist

- [ ] `DEBUG=False` in production
- [ ] Strong `SECRET_KEY` set
- [ ] `ALLOWED_HOSTS` configured correctly
- [ ] HTTPS/SSL enabled
- [ ] Security headers configured (HSTS, etc.)
- [ ] Database credentials secure
- [ ] API keys in environment variables, not code
- [ ] File upload size limits set
- [ ] CSRF protection enabled (default Django)
- [ ] Session security enabled
- [ ] Regular security updates scheduled

## Monitoring & Maintenance

### Logs

Logs are written to `logs/django.log` with rotation (15MB, 10 backups).

View logs:
```bash
tail -f logs/django.log
```

### Updates

1. **Update dependencies**:
   ```bash
   pip install --upgrade -r requirements.txt
   ```

2. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

3. **Build CSS and collect static files**:
   ```bash
   npm ci && npm run build:css:prod
   python manage.py collectstatic --noinput
   ```

4. **Restart server**:
   ```bash
   sudo systemctl restart kouekam_hub
   ```

### Backups

Set up automated backups for:
- Database (daily)
- Media files (if using local storage, daily)
- Static files (as needed)

## Troubleshooting

### Static files not loading / CSS not working
- **Most common issue**: CSS not built before deployment
  - Verify CSS was built: `ls -lh static/css/output.css` (should exist and have content)
  - Build CSS: `npm ci && npm run build:css:prod`
  - For Heroku: The Procfile release phase should handle this automatically
  - For Docker: CSS is built in the Dockerfile, but entrypoint.sh also builds it
- Verify `collectstatic` was run after building CSS
- Check `STATIC_ROOT` path
- Verify WhiteNoise middleware or S3 configuration
- Check browser console for 404 errors on CSS file
- Verify `static/css/output.css` exists and is not empty
- For S3: Verify CSS file was uploaded to S3 bucket

### Database connection errors
- Check `DATABASE_URL` format
- Verify database server is running
- Check firewall rules
- Verify credentials

### Email not sending
- Check SMTP credentials
- Verify `EMAIL_HOST`, `EMAIL_PORT`
- Check firewall allows SMTP connections
- Test with console backend first

### 500 errors
- Check logs: `tail -f logs/django.log`
- Verify `DEBUG=False` doesn't expose sensitive info
- Check all environment variables are set
- Verify database migrations are applied

## Performance Optimization

1. **Enable caching** (add to settings.py):
   ```python
   CACHES = {
       'default': {
           'BACKEND': 'django.core.cache.backends.redis.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
       }
   }
   ```

2. **Database optimization**:
   - Add database indexes where needed
   - Use `select_related` and `prefetch_related` in queries
   - Enable connection pooling

3. **Static files**:
   - Use CDN for static assets
   - Enable compression (WhiteNoise does this automatically)
   - Set appropriate cache headers

## Support

For issues or questions, refer to:
- Django deployment documentation: https://docs.djangoproject.com/en/stable/howto/deployment/
- Project documentation: `LLM_CONTEXT.md`




