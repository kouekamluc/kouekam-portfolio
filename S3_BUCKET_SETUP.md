# S3 Bucket Public Access Setup Guide

If your CSS is not loading from S3, it's likely because the bucket is not configured for public access. Follow these steps:

## Quick Fix (AWS Console)

### Step 1: Enable Public Access

1. **Go to AWS S3 Console**
   - Navigate to: https://console.aws.amazon.com/s3/
   - Click on your bucket: `kouekam-hub-assets`

2. **Disable Block Public Access**
   - Click on the "Permissions" tab
   - Scroll to "Block public access (bucket settings)"
   - Click "Edit"
   - **Uncheck all 4 options**:
     - ☐ Block all public access
     - ☐ Block public access to buckets and objects granted through new access control lists (ACLs)
     - ☐ Block public access to buckets and objects granted through any access control lists (ACLs)
     - ☐ Block public access to buckets and objects granted through new public bucket or access point policies
   - Click "Save changes"
   - Type `confirm` when prompted

### Step 2: Configure CORS

1. **Still in Permissions tab**
   - Scroll down to "Cross-origin resource sharing (CORS)"
   - Click "Edit"
   - Paste this configuration:

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

2. **Click "Save changes"**

### Step 3: Configure Bucket Policy

1. **Still in Permissions tab**
   - Scroll to "Bucket policy"
   - Click "Edit"
   - Paste this policy (replace `kouekam-hub-assets` with your bucket name if different):

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

2. **Click "Save changes"**

### Step 4: Verify

1. **Test the CSS URL directly in your browser**:
   ```
   https://kouekam-hub-assets.s3.eu-north-1.amazonaws.com/static/css/output.css
   ```
   
   You should see the CSS content (not an error page).

2. **Clear browser cache**:
   - Press `Ctrl+Shift+Delete` (Windows) or `Cmd+Shift+Delete` (Mac)
   - Select "Cached images and files"
   - Click "Clear data"

3. **Hard refresh your website**:
   - Press `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)

## Automated Setup (Python Script)

If you have AWS credentials configured, you can run:

```bash
# Set environment variables
export AWS_ACCESS_KEY_ID=your-key
export AWS_SECRET_ACCESS_KEY=your-secret
export AWS_STORAGE_BUCKET_NAME=kouekam-hub-assets
export AWS_S3_REGION_NAME=eu-north-1

# Run the configuration script
python configure_s3_public_access.py
```

## Troubleshooting

### CSS file returns 403 Forbidden

**Problem**: Bucket policy or block public access is preventing access.

**Solution**: 
1. Check "Block public access" is disabled (Step 1 above)
2. Verify bucket policy is set (Step 3 above)
3. Wait a few minutes for changes to propagate

### CSS file returns CORS error

**Problem**: CORS is not configured or origin is not allowed.

**Solution**:
1. Check CORS configuration (Step 2 above)
2. Make sure your domain is in `AllowedOrigins`
3. Clear browser cache and hard refresh

### CSS file returns 404 Not Found

**Problem**: File doesn't exist in S3.

**Solution**:
1. Run `python manage.py collectstatic --noinput` to upload files
2. Check the file exists in S3 console at path: `static/css/output.css`

### CSS loads but styling doesn't apply

**Problem**: CSS file might be empty or corrupted.

**Solution**:
1. Check file size in S3 (should be > 50KB)
2. Rebuild CSS: `npm run build:css:prod`
3. Re-upload: `python manage.py collectstatic --noinput --clear`

## Verification Checklist

- [ ] Block public access is disabled
- [ ] CORS is configured with your domain
- [ ] Bucket policy allows public read for `static/*`
- [ ] CSS file exists at `static/css/output.css` in S3
- [ ] CSS file is accessible via direct URL
- [ ] Browser cache is cleared
- [ ] Hard refresh performed

## Security Note

The bucket policy only allows public read access to files in the `static/` prefix. Media files in `media/` remain private. This is the recommended setup for static assets.

