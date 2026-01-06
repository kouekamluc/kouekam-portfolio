# Fix: 5 Stylesheet URLs Failing to Load

## Problem
Browser console shows 5 stylesheet URLs failing to load. These are likely Django admin CSS files.

## The 5 Stylesheets (Django Admin)

Django admin uses 5 main CSS files:
1. `/static/admin/css/base.css` - Main admin styling
2. `/static/admin/css/dashboard.css` - Dashboard styling
3. `/static/admin/css/forms.css` - Form styling
4. `/static/admin/css/login.css` - Login page styling
5. `/static/admin/css/responsive.css` - Responsive styling

## Immediate Fix

### Step 1: Run collectstatic in Production
```bash
python manage.py collectstatic --noinput --clear
```

This will collect ALL Django admin CSS files.

### Step 2: Verify Files Were Collected

**For WhiteNoise:**
```bash
ls -lh staticfiles/admin/css/
```

Should show all 5 CSS files:
- base.css
- dashboard.css
- forms.css
- login.css
- responsive.css

**For S3:**
```bash
python verify_stylesheet_urls.py
```

Or check AWS S3 console for files in `static/admin/css/` directory.

### Step 3: RESTART SERVER ⚠️ CRITICAL
WhiteNoise loads static files at startup. You MUST restart after collectstatic.

- **Heroku:** `heroku restart`
- **Railway:** Restart from dashboard
- **Docker:** `docker-compose restart`
- **Manual:** Restart gunicorn/systemd

### Step 4: Test URLs Directly

Test each URL in your browser (replace `yourdomain.com` with your actual domain):

```
https://yourdomain.com/static/admin/css/base.css
https://yourdomain.com/static/admin/css/dashboard.css
https://yourdomain.com/static/admin/css/forms.css
https://yourdomain.com/static/admin/css/login.css
https://yourdomain.com/static/admin/css/responsive.css
```

Each should return CSS content (not 404).

## Diagnostic Script

Run this to verify all stylesheet URLs:
```bash
python verify_stylesheet_urls.py
```

This will:
- Check if all admin CSS files exist
- Verify they're collected
- Show the URLs
- Provide specific recommendations

## Common Issues

### Issue 1: Files Not Collected
**Symptom:** Files don't exist in `staticfiles/admin/css/`

**Fix:**
```bash
python manage.py collectstatic --noinput --clear
```

### Issue 2: Server Not Restarted
**Symptom:** Files exist but still get 404 errors

**Fix:** Restart your server after collectstatic

### Issue 3: Wrong STATIC_URL
**Symptom:** URLs are incorrect

**Check:** `STATIC_URL` should be `/static/` in settings.py

### Issue 4: WhiteNoise Not Active
**Symptom:** Files exist but not served

**Check:** WhiteNoise middleware must be in MIDDLEWARE:
```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Must be here
    # ...
]
```

### Issue 5: S3 Files Not Public
**Symptom:** Files in S3 but return 403/404

**Fix:**
- Check S3 bucket policy allows public read
- Verify CORS configuration
- Check file paths are correct

## Verification Checklist

After fix:
- [ ] `collectstatic` completed without errors
- [ ] All 5 admin CSS files exist in `staticfiles/admin/css/` (or S3)
- [ ] Server has been restarted
- [ ] All 5 URLs return CSS content (not 404)
- [ ] Browser console shows no 404 errors
- [ ] Admin page loads with full styling

## Quick Test

1. Visit: `https://yourdomain.com/admin/`
2. Open Developer Tools (F12)
3. Go to Network tab
4. Filter by "CSS"
5. Reload page
6. Check all 5 admin CSS files load successfully (Status 200)

## Still Not Working?

1. **Run diagnostic:**
   ```bash
   python verify_stylesheet_urls.py
   ```

2. **Check browser console:**
   - Look for exact URLs that are failing
   - Check if they're 404, 403, or network errors

3. **Check server logs:**
   - Look for errors related to static files
   - Check WhiteNoise logs

4. **Verify configuration:**
   - `DEBUG=False` in production
   - `STATIC_URL = "/static/"`
   - WhiteNoise middleware active
   - `collectstatic` has been run



