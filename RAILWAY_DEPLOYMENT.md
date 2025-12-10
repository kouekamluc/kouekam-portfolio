# Railway Deployment Guide

This guide explains how the application is automatically configured for Railway deployment.

## Automatic CSS Building

The Dockerfile is configured to automatically build CSS during the Docker build process:

1. **Multi-stage Build**: 
   - Stage 1 (node-builder): Builds Tailwind CSS using Node.js
   - Stage 2 (python): Copies the built CSS and runs the Django application

2. **CSS Build Process**:
   - CSS is built in the `node-builder` stage: `npx tailwindcss -i ./static/css/input.css -o ./static/css/output.css --minify`
   - Built CSS is copied to the Python stage: `COPY --from=node-builder /app/static/css/output.css ./static/css/output.css`
   - CSS is verified and rebuilt if needed as a fallback
   - Entrypoint script also rebuilds CSS if missing (double safety)

3. **Static Files Collection**:
   - Runs automatically in `entrypoint.sh` before the server starts
   - Command: `python manage.py collectstatic --noinput --clear`

## What Runs Automatically

When Railway builds and deploys your Docker container:

1. **Docker Build Stage**:
   - ✅ Installs Node.js dependencies
   - ✅ Builds Tailwind CSS (minified)
   - ✅ Installs Python dependencies
   - ✅ Verifies CSS file exists and has content
   - ✅ Creates necessary directories

2. **Container Startup (entrypoint.sh)**:
   - ✅ Waits for PostgreSQL (if using DATABASE_URL)
   - ✅ Runs database migrations
   - ✅ Creates superuser (if needed)
   - ✅ Rebuilds CSS if missing (fallback safety)
   - ✅ Collects static files (including CSS)
   - ✅ Starts Gunicorn server

## Railway Configuration

### Environment Variables

Set these in Railway dashboard:

**Required:**
- `SECRET_KEY` - Django secret key
- `DEBUG=False` - Production mode
- `ALLOWED_HOSTS` - Your Railway domain (e.g., `yourapp.railway.app`)
- `DATABASE_URL` - Automatically provided by Railway if you add a PostgreSQL service

**Optional:**
- `USE_S3=True` - If using AWS S3 for static files
- `AWS_ACCESS_KEY_ID` - AWS credentials
- `AWS_SECRET_ACCESS_KEY` - AWS credentials
- `AWS_STORAGE_BUCKET_NAME` - S3 bucket name
- `AWS_S3_REGION_NAME` - S3 region (default: `us-east-1`)

### Static Files

**Option 1: WhiteNoise (Default)**
- No additional configuration needed
- Static files are served by WhiteNoise middleware
- CSS is automatically included in `collectstatic`

**Option 2: AWS S3**
- Set `USE_S3=True` and AWS credentials
- Static files (including CSS) are uploaded to S3 during `collectstatic`

## Deployment Steps

1. **Connect Repository**:
   - Connect your GitHub repository to Railway
   - Railway will detect the Dockerfile automatically

2. **Add PostgreSQL Service** (if needed):
   - Add a PostgreSQL service in Railway
   - Railway automatically sets `DATABASE_URL`

3. **Set Environment Variables**:
   - Go to Variables tab
   - Set all required environment variables

4. **Deploy**:
   - Railway automatically builds and deploys on push
   - Or manually trigger deployment from dashboard

## Verification

After deployment, verify:

1. **CSS is Working**:
   - Visit your Railway URL
   - Check browser console for CSS file loading
   - Verify styling is applied

2. **Check Logs**:
   - In Railway dashboard, check deployment logs
   - Look for: `✓ CSS file verified and ready`
   - Look for: `Collecting static files...`

3. **Verify Static Files**:
   - Check that `collectstatic` ran successfully
   - CSS file should be in staticfiles or S3

## Troubleshooting

### CSS Not Loading

1. **Check Build Logs**:
   - Look for CSS build messages in Railway build logs
   - Should see: `✓ CSS file verified and ready`

2. **Check Runtime Logs**:
   - Look for CSS build messages in entrypoint logs
   - Should see: `✓ CSS built successfully`

3. **Verify File Exists**:
   - Check that `collectstatic` found the CSS file
   - Should see: `Copying '/app/static/css/output.css'`

4. **Check Browser Console**:
   - Look for 404 errors on `/static/css/output.css`
   - Verify the URL is correct

### Static Files Not Collecting

1. **Check Environment Variables**:
   - Verify `DEBUG=False` is set
   - Check S3 configuration if using S3

2. **Check Logs**:
   - Look for errors in `collectstatic` output
   - Check for permission issues

3. **Manual Verification**:
   - SSH into container (if possible)
   - Check `staticfiles/css/output.css` exists

## Files Involved

- **Dockerfile**: Builds CSS and sets up the container
- **entrypoint.sh**: Runs migrations, builds CSS (fallback), collects static files
- **package.json**: Contains CSS build script (`build:css:prod`)
- **kouekam_hub/settings.py**: Configures static files (WhiteNoise or S3)

## Notes

- CSS is built **during Docker build** (primary method)
- CSS is rebuilt **in entrypoint** if missing (safety fallback)
- Static files are collected **automatically** before server starts
- No manual steps required - everything is automatic!

