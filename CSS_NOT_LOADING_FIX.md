# CSS Not Loading - Quick Fix Guide

## The Problem

Your CSS file is uploaded to S3, but the browser can't load it because:
1. **S3 bucket is blocking public access** (most common)
2. **CORS is not configured** (browser blocks cross-origin requests)
3. **Bucket policy doesn't allow public read**

## Quick Fix (5 minutes)

### Step 1: Enable Public Access in AWS Console

1. Go to: https://console.aws.amazon.com/s3/buckets/kouekam-hub-assets
2. Click **"Permissions"** tab
3. Find **"Block public access (bucket settings)"**
4. Click **"Edit"**
5. **UNCHECK all 4 boxes**:
   - ☐ Block all public access
   - ☐ Block public access to buckets and objects granted through new access control lists (ACLs)
   - ☐ Block public access to buckets and objects granted through any access control lists (ACLs)
   - ☐ Block public access to buckets and objects granted through new public bucket or access point policies
6. Click **"Save changes"**
7. Type `confirm` when prompted

### Step 2: Configure CORS

1. Still in **"Permissions"** tab
2. Scroll to **"Cross-origin resource sharing (CORS)"**
3. Click **"Edit"**
4. Paste this:

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "HEAD"],
        "AllowedOrigins": [
            "https://kouekamkamgou.uk",
            "https://www.kouekamkamgou.uk",
            "http://localhost:8000",
            "http://127.0.0.1:8000"
        ],
        "ExposeHeaders": ["ETag", "Content-Length", "Content-Type"],
        "MaxAgeSeconds": 3000
    }
]
```

5. Click **"Save changes"**

### Step 3: Add Bucket Policy

1. Still in **"Permissions"** tab
2. Scroll to **"Bucket policy"**
3. Click **"Edit"**
4. Paste this (replace bucket name if different):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::kouekam-hub-assets/static/*"
        }
    ]
}
```

5. Click **"Save changes"**

### Step 4: Test and Clear Cache

1. **Test the CSS URL directly**:
   Open in browser: `https://kouekam-hub-assets.s3.eu-north-1.amazonaws.com/static/css/output.css`
   
   ✅ **Should show**: CSS code (lots of text starting with `*, ::before, ::after`)
   
   ❌ **If you see**: "Access Denied" or "403 Forbidden" → Go back to Step 1

2. **Clear browser cache**:
   - Press `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
   - Select "Cached images and files"
   - Click "Clear data"

3. **Hard refresh your website**:
   - Press `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)

## Verify It's Working

1. Open your website: https://kouekamkamgou.uk
2. Open browser DevTools (F12)
3. Go to **Network** tab
4. Refresh the page
5. Look for `output.css` in the list
6. Check the status:
   - ✅ **200 OK** = CSS is loading!
   - ❌ **403 Forbidden** = Public access not enabled (Step 1)
   - ❌ **CORS error** = CORS not configured (Step 2)
   - ❌ **404 Not Found** = File not uploaded (run `collectstatic`)

## Still Not Working?

### Check Browser Console

Press F12 → Console tab → Look for errors:

- **"Access to CSS stylesheet... blocked by CORS policy"**
  → Fix: Configure CORS (Step 2)

- **"403 Forbidden" or "Access Denied"**
  → Fix: Enable public access (Step 1) and add bucket policy (Step 3)

- **"404 Not Found"**
  → Fix: Run `python manage.py collectstatic --noinput` to upload files

### Verify File Exists in S3

1. Go to: https://console.aws.amazon.com/s3/buckets/kouekam-hub-assets
2. Navigate to: `static/css/`
3. Check if `output.css` exists
4. If missing, run: `python manage.py collectstatic --noinput`

## Automated Fix (If you have AWS CLI)

```bash
# Set your AWS credentials
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret

# Run the configuration script
python configure_s3_public_access.py
```

## Summary

The CSS file is on S3, but S3 is blocking public access. You need to:
1. ✅ Disable "Block public access" 
2. ✅ Configure CORS
3. ✅ Add bucket policy for public read
4. ✅ Clear browser cache

After these steps, your CSS will load! 🎉

