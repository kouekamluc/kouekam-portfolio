# CSS Verification and Troubleshooting Steps

Since the CSS file is now accessible, but styling isn't applying, follow these steps:

## Step 1: Clear Browser Cache Completely

1. **Hard Refresh**:
   - Windows: `Ctrl + Shift + R` or `Ctrl + F5`
   - Mac: `Cmd + Shift + R`

2. **Clear Cache**:
   - Press `Ctrl + Shift + Delete` (Windows) or `Cmd + Shift + Delete` (Mac)
   - Select "Cached images and files"
   - Select "All time" or "Everything"
   - Click "Clear data"

3. **Disable Cache in DevTools** (for testing):
   - Open DevTools (F12)
   - Go to Network tab
   - Check "Disable cache"
   - Keep DevTools open while testing

## Step 2: Verify CSS is Loading in Browser

1. Open your website: https://kouekamkamgou.uk
2. Open DevTools (F12)
3. Go to **Network** tab
4. Refresh the page
5. Look for `output.css`:
   - ✅ **Status 200** = CSS is loading correctly
   - ❌ **Status 403** = S3 access issue (check bucket policy)
   - ❌ **Status 404** = File not found (run collectstatic)
   - ❌ **CORS error** = CORS not configured

6. Click on `output.css` in the Network tab
7. Check the **Response** tab - you should see CSS code
8. Check **Headers** tab:
   - `Content-Type: text/css` ✅
   - `Access-Control-Allow-Origin: https://kouekamkamgou.uk` ✅

## Step 3: Verify CSS is Applied

1. In DevTools, go to **Elements** tab
2. Select an element (like `<body>` or a `<div>`)
3. Check the **Styles** panel on the right
4. Look for Tailwind classes:
   - You should see styles like `.bg-gray-50`, `.text-gray-900`, etc.
   - If you see "No styles" or only inline styles, CSS isn't loading

## Step 4: Check for Console Errors

1. In DevTools, go to **Console** tab
2. Look for errors:
   - ❌ "Failed to load resource" = File not accessible
   - ❌ "CORS policy" = CORS issue
   - ❌ "Content Security Policy" = CSP blocking CSS
   - ❌ "MIME type" = Wrong Content-Type

## Step 5: Verify Template is Using Correct Path

1. Right-click on your page → "View Page Source"
2. Search for `output.css`
3. Check the URL:
   - ✅ Should be: `https://kouekam-hub-assets.s3.eu-north-1.amazonaws.com/static/css/output.css`
   - ❌ If it's `/static/css/output.css` = STATIC_URL not configured correctly

## Step 6: Test CSS URL Directly

1. Open this URL in a new tab:
   ```
   https://kouekam-hub-assets.s3.eu-north-1.amazonaws.com/static/css/output.css
   ```
2. You should see CSS code (not an error page)
3. If you see "Access Denied" → S3 bucket policy issue
4. If you see "CORS error" → CORS configuration issue

## Step 7: Check Content Security Policy (CSP)

If your site has CSP headers, they might be blocking the CSS:

1. In DevTools → Network tab
2. Click on the main page request (your domain)
3. Check **Response Headers**
4. Look for `Content-Security-Policy`
5. If present, make sure it includes:
   ```
   style-src 'self' https://kouekam-hub-assets.s3.eu-north-1.amazonaws.com;
   ```

## Step 8: Verify Django Static URL Configuration

Check that Django is generating the correct URL:

1. SSH into your server or use Railway shell
2. Run:
   ```python
   python manage.py shell
   ```
3. In the shell:
   ```python
   from django.templatetags.static import static
   print(static('css/output.css'))
   ```
4. Should output: `https://kouekam-hub-assets.s3.eu-north-1.amazonaws.com/static/css/output.css`

## Step 9: Force CSS Reload

Add a version parameter to force browser to reload:

1. Edit `templates/base.html`
2. Change line 9 from:
   ```html
   <link href="{% static 'css/output.css' %}?v=2.0" rel="stylesheet" crossorigin="anonymous">
   ```
   To:
   ```html
   <link href="{% static 'css/output.css' %}?v=3.0" rel="stylesheet" crossorigin="anonymous">
   ```

## Step 10: Check if CSS Classes are in the HTML

1. View page source
2. Look for elements with Tailwind classes like:
   - `class="bg-gray-50"`
   - `class="text-gray-900"`
   - `class="flex flex-col"`
3. If classes are missing, the template might not be using Tailwind classes

## Common Issues and Solutions

### Issue: CSS loads but no styling applies
**Solution**: 
- Clear browser cache completely
- Check if HTML elements have Tailwind classes
- Verify CSS file size is > 50KB (not empty)

### Issue: CORS error in console
**Solution**: 
- Configure CORS on S3 bucket (see `S3_BUCKET_SETUP.md`)
- Make sure your domain is in AllowedOrigins

### Issue: 403 Forbidden
**Solution**: 
- Check S3 bucket policy allows public read
- Verify "Block public access" is disabled

### Issue: CSS loads but styles are wrong
**Solution**: 
- Rebuild CSS: `npm run build:css:prod`
- Re-upload: `python manage.py collectstatic --noinput --clear`

### Issue: CSS URL is wrong in HTML
**Solution**: 
- Check `STATIC_URL` in settings.py
- Verify `USE_S3=True` is set
- Restart the server after changing settings

## Quick Test

Run this in browser console (F12 → Console):

```javascript
// Check if CSS is loaded
const link = document.querySelector('link[href*="output.css"]');
if (link) {
    console.log('CSS link found:', link.href);
    fetch(link.href)
        .then(r => r.text())
        .then(css => console.log('CSS loaded:', css.length, 'bytes'))
        .catch(e => console.error('CSS failed to load:', e));
} else {
    console.error('CSS link not found in HTML');
}
```

This will tell you if:
- CSS link exists in HTML
- CSS file is accessible
- CSS content is loaded



