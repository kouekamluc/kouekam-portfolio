# Password Reset with Email - Production Setup Guide

This guide explains how the password reset workflow is configured for production deployment.

## Overview

The password reset workflow uses django-allauth and includes:
- Email-based password reset requests
- Secure token-based password reset links
- Custom email templates
- Site configuration for proper URL generation

## What Runs Automatically in Production

### During Deployment (`entrypoint.sh`)

1. **Database Migrations**: `python manage.py migrate --noinput`
   - Includes Sites framework migrations
   - Creates necessary database tables

2. **Site Initialization**: `python manage.py init_site`
   - Creates/updates the Site object required for django-allauth
   - Uses `SITE_DOMAIN` environment variable or auto-detects from `ALLOWED_HOSTS`
   - Required for generating correct password reset URLs in emails

3. **Superuser Creation**: `python create_superuser.py`

4. **Static Files Collection**: `python manage.py collectstatic`

## Environment Variables for Production

### Required for Password Reset Emails

Set these environment variables in your production environment (Railway, Heroku, etc.):

```bash
# Site Configuration (for password reset email URLs)
SITE_DOMAIN=yourdomain.com                    # Your production domain
SITE_NAME=Kouekam Portfolio                   # Your site name (optional)

# Email Configuration (choose one)
# Option 1: SMTP (Gmail, SendGrid, etc.)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com

# Option 2: Brevo (Sendinblue) - if using Brevo API
BREVO_API_KEY=your-brevo-api-key
BREVO_SENDER_EMAIL=noreply@yourdomain.com
BREVO_SENDER_NAME=Kouekam Portfolio

# Or use the built-in Brevo email backend if configured
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-brevo-smtp-user
EMAIL_HOST_PASSWORD=your-brevo-smtp-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com
```

### Site Domain Auto-Detection

If `SITE_DOMAIN` is not set, the `init_site` command will:
1. Check `ALLOWED_HOSTS` environment variable
2. Use the first host from `ALLOWED_HOSTS` as the domain
3. Fall back to `localhost:8000` for development

Example:
- If `ALLOWED_HOSTS=kouekamkamgou.uk,www.kouekamkamgou.uk`
- Then `SITE_DOMAIN` will default to `kouekamkamgou.uk`

## Production Deployment Steps

### Railway/Heroku

The deployment happens automatically via `entrypoint.sh`, but you can verify:

1. **Check migrations ran**:
   ```bash
   python manage.py migrate --plan
   ```

2. **Verify Site is configured**:
   ```bash
   python manage.py shell
   >>> from django.contrib.sites.models import Site
   >>> site = Site.objects.get_current()
   >>> print(f"Site: {site.name} at {site.domain}")
   ```

3. **Test password reset email**:
   - Go to `/accounts/password/reset/`
   - Enter an email address
   - Check that email is sent (check your email backend logs)

### Manual Deployment Script

You can also use the production management script:

```bash
./manage_production.sh deploy
```

This runs:
- `python manage.py check --deploy`
- `python manage.py migrate`
- `python manage.py init_site` (auto-detects domain)
- `python manage.py collectstatic --noinput`

## Email Templates

Custom email templates are located at:
- `templates/account/email/password_reset_key_subject.txt`
- `templates/account/email/password_reset_key_message.txt`
- `templates/account/email/password_reset_key_message.html`

These templates include:
- Branded HTML email design
- Plain text fallback
- Clear instructions
- Secure reset link
- 24-hour expiration notice

## Password Reset URLs

The password reset workflow uses these URLs:
- Request reset: `/accounts/password/reset/`
- Reset done (email sent): `/accounts/password/reset/done/`
- Change password (from email link): `/accounts/password/reset/key/<token>/`
- Password changed: `/accounts/password/reset/key/<token>/done/`

All URLs are automatically configured via `path("accounts/", include("allauth.urls"))` in `kouekam_hub/urls.py`.

## Settings Configuration

Relevant settings in `kouekam_hub/settings.py`:

```python
# Sites framework (required for django-allauth)
SITE_ID = 1

# Password reset settings
ACCOUNT_PASSWORD_RESET_EXPIRE_HOURS = 24  # Reset links valid for 24 hours

# Email settings
EMAIL_BACKEND = os.getenv('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
# ... other email settings from environment variables
```

## Troubleshooting

### Password reset emails not sending

1. **Check email backend configuration**:
   ```bash
   python manage.py shell
   >>> from django.conf import settings
   >>> print(f"Email Backend: {settings.EMAIL_BACKEND}")
   >>> print(f"Email Host: {settings.EMAIL_HOST}")
   >>> print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
   ```

2. **Verify Site domain is correct**:
   ```bash
   python manage.py shell
   >>> from django.contrib.sites.models import Site
   >>> site = Site.objects.get_current()
   >>> print(f"Site Domain: {site.domain}")
   ```
   The domain should match your production domain (without `http://` or `https://`)

3. **Test email sending manually**:
   ```bash
   python manage.py shell
   >>> from django.core.mail import send_mail
   >>> send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])
   ```

### Reset links have wrong domain

- Ensure `SITE_DOMAIN` environment variable is set correctly
- Or ensure `ALLOWED_HOSTS` includes your production domain
- Run `python manage.py init_site` to update the Site object

### Migrations not running

- Check `entrypoint.sh` includes `python manage.py migrate --noinput`
- Verify database connection is working
- Check deployment logs for migration errors

## Security Notes

- Password reset tokens expire after 24 hours
- Tokens are single-use (invalidated after use)
- Email addresses are checked for validity before sending
- No information disclosure: same message shown whether email exists or not
