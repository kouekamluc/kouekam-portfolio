# Production Deployment Checklist

Use this checklist before deploying to production to ensure everything is configured correctly.

## Pre-Deployment

### Environment Configuration
- [ ] `.env` file created with all required variables
- [ ] `SECRET_KEY` generated (not the default one)
- [ ] `DEBUG=False` set
- [ ] `ALLOWED_HOSTS` includes your domain(s)
- [ ] Database URL configured (PostgreSQL recommended)
- [ ] Email backend configured with valid credentials
- [ ] OpenAI API key set (if using AI features)
- [ ] AWS S3 credentials configured (if using S3)

### Code & Dependencies
- [ ] All dependencies up to date in `requirements.txt`
- [ ] Virtual environment activated
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] No hardcoded secrets or credentials in code
- [ ] `.gitignore` properly configured
- [ ] Sensitive files not committed to git

### Database
- [ ] Database server accessible
- [ ] Database user has correct permissions
- [ ] All migrations applied: `python manage.py migrate`
- [ ] Test database connection works
- [ ] Backup strategy in place

### Static & Media Files
- [ ] Static files collected: `python manage.py collectstatic --noinput`
- [ ] Static files accessible (check STATIC_ROOT)
- [ ] If using S3: Bucket created and configured
- [ ] If using S3: CORS configured on bucket
- [ ] If using S3: Static files uploaded to S3
- [ ] Media files storage configured (local or S3)

### Security
- [ ] `DEBUG=False` verified
- [ ] Strong `SECRET_KEY` generated
- [ ] HTTPS/SSL certificate obtained
- [ ] Security headers configured (HSTS, etc.)
- [ ] CSRF protection enabled (default)
- [ ] File upload size limits set appropriately
- [ ] Allowed file extensions validated
- [ ] Password validators configured

### Server Configuration
- [ ] Web server installed (Nginx/Apache)
- [ ] Application server configured (Gunicorn/uWSGI)
- [ ] Process manager configured (systemd/supervisor)
- [ ] Reverse proxy configured
- [ ] SSL/TLS configured
- [ ] Firewall rules set
- [ ] Ports opened (80, 443, application port)

### Testing
- [ ] Test all major features locally with `DEBUG=False`
- [ ] Test user registration/login
- [ ] Test file uploads
- [ ] Test email sending
- [ ] Test error pages (404, 500, 403)
- [ ] Test static files loading
- [ ] Test media files loading
- [ ] Load test performed

## Deployment

### Initial Setup
- [ ] Server provisioned and secured
- [ ] Domain DNS configured
- [ ] SSL certificate installed
- [ ] Code deployed to server
- [ ] Environment variables set on server
- [ ] Virtual environment created on server

### Application Setup
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Database migrations run: `python manage.py migrate`
- [ ] Static files collected: `python manage.py collectstatic --noinput`
- [ ] Superuser created: `python manage.py createsuperuser`
- [ ] Application server started
- [ ] Web server configured and started

### Verification
- [ ] Homepage loads correctly
- [ ] All pages accessible
- [ ] Static files loading (CSS, JS, images)
- [ ] Media files loading (user uploads)
- [ ] User registration works
- [ ] Email verification works (if enabled)
- [ ] Login/logout works
- [ ] All app features functional
- [ ] Error pages display correctly
- [ ] HTTPS redirect working
- [ ] No console errors in browser

### Monitoring
- [ ] Logging configured and working
- [ ] Error logging to file configured
- [ ] Email error notifications working (if configured)
- [ ] Uptime monitoring set up
- [ ] Performance monitoring set up (optional)

### Maintenance Setup
- [ ] Backup script created
- [ ] Backup schedule configured (cron/systemd timer)
- [ ] Update procedure documented
- [ ] Rollback procedure documented
- [ ] Team access configured

## Post-Deployment

### Immediate (Within 24 hours)
- [ ] Monitor error logs
- [ ] Check server resource usage (CPU, memory, disk)
- [ ] Verify backups are running
- [ ] Test all critical user flows
- [ ] Monitor user feedback

### First Week
- [ ] Review error logs daily
- [ ] Check performance metrics
- [ ] Verify backups are successful
- [ ] Test recovery procedure
- [ ] Document any issues encountered

### Ongoing
- [ ] Regular security updates
- [ ] Dependency updates (monthly)
- [ ] Database maintenance (weekly backups, monthly optimization)
- [ ] Log rotation working
- [ ] Disk space monitoring

## Security Review

- [ ] All passwords changed from defaults
- [ ] SSH key authentication enabled (not passwords)
- [ ] Firewall configured correctly
- [ ] Unnecessary services disabled
- [ ] Regular security updates scheduled
- [ ] Security headers verified in browser
- [ ] SSL certificate valid and not expiring soon
- [ ] Rate limiting considered (optional)

## Performance Optimization

- [ ] Database queries optimized
- [ ] Caching implemented (optional but recommended)
- [ ] Static files served efficiently
- [ ] Image optimization considered
- [ ] CDN configured (if applicable)

## Documentation

- [ ] Deployment process documented
- [ ] Environment variables documented
- [ ] Backup/restore procedures documented
- [ ] Troubleshooting guide available
- [ ] Team trained on deployment process

## Rollback Plan

- [ ] Previous version backed up
- [ ] Database backup before deployment
- [ ] Rollback procedure tested
- [ ] Team knows how to rollback

---

## Quick Commands Reference

```bash
# Collect static files
python manage.py collectstatic --noinput

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Check configuration
python manage.py check --deploy

# Start server (test)
gunicorn -c gunicorn_config.py kouekam_hub.wsgi:application

# View logs
tail -f logs/django.log

# Backup database (PostgreSQL)
pg_dump -U user dbname > backup_$(date +%Y%m%d).sql

# Restore database (PostgreSQL)
psql -U user dbname < backup_file.sql
```

---

## Emergency Contacts

Document key contacts for production issues:
- Server administrator: ___________
- Database administrator: ___________
- DNS administrator: ___________
- Application developer: ___________

