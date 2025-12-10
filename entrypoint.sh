#!/bin/bash
set -e

# Wait for PostgreSQL if DB_HOST is set (Docker Compose sets this)
# Railway uses DATABASE_URL, so check for that too
if [ -n "$DB_HOST" ]; then
    echo "Waiting for PostgreSQL at ${DB_HOST}:${DB_PORT:-5432}..."
    while ! nc -z ${DB_HOST} ${DB_PORT:-5432}; do
        sleep 0.1
    done
    echo "PostgreSQL started"
elif [ -n "$DATABASE_URL" ]; then
    echo "DATABASE_URL detected, using PostgreSQL (Railway/Heroku style)"
    # Extract host from DATABASE_URL if needed for health check
    # For Railway, the database is usually already available
else
    echo "No database configuration detected, using SQLite database"
fi

echo "Running migrations..."
python manage.py migrate --noinput

echo "Creating superuser (if not exists)..."
python create_superuser.py

echo "✓ Using Tailwind CSS CDN (no build step needed)"

# Check if using S3 (case-insensitive check)
USE_S3_RAW=$(echo "${USE_S3:-False}" | tr '[:upper:]' '[:lower:]')
if [ "$USE_S3_RAW" = "true" ] || [ "$USE_S3_RAW" = "1" ] || [ "$USE_S3_RAW" = "yes" ]; then
    echo "✓ AWS S3 enabled for static files"
    echo "  Bucket: ${AWS_STORAGE_BUCKET_NAME:-not set}"
    echo "  Region: ${AWS_S3_REGION_NAME:-us-east-1}"
    echo "  Static URL will be: https://${AWS_STORAGE_BUCKET_NAME:-bucket}.s3.${AWS_S3_REGION_NAME:-us-east-1}.amazonaws.com/static/"
else
    echo "Using local static files (WhiteNoise)"
fi

echo "Collecting static files..."
# Verify S3 storage is properly configured before collectstatic
if [ "$USE_S3_RAW" = "true" ] || [ "$USE_S3_RAW" = "1" ] || [ "$USE_S3_RAW" = "yes" ]; then
    echo "Verifying S3 storage configuration before collectstatic..."
    python << EOF
import os
import django
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from django.conf import settings
from kouekam_hub.storage import StaticStorage

# Test storage initialization - only print errors
# Note: We just verify StaticStorage can be instantiated
# Django will use STATICFILES_STORAGE from settings during collectstatic
try:
    storage = StaticStorage()
    # Verify STATICFILES_STORAGE is set correctly in settings
    if not hasattr(settings, 'STATICFILES_STORAGE'):
        print(f"WARNING: STATICFILES_STORAGE not set in settings", file=sys.stderr)
    elif 'StaticStorage' not in settings.STATICFILES_STORAGE:
        print(f"WARNING: STATICFILES_STORAGE is '{settings.STATICFILES_STORAGE}', expected StaticStorage", file=sys.stderr)
except Exception as e:
    print(f"ERROR: Failed to initialize S3 storage: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF
    if [ $? -ne 0 ]; then
        echo "❌ ERROR: S3 storage initialization failed!"
        exit 1
    fi
fi

# Run collectstatic with minimal output in production
# When using S3, collectstatic should upload directly to S3
# Note: "Copying" messages are normal - they mean copying from source to storage backend
echo "Running collectstatic..."
# Use verbosity 0 in production to reduce log volume (Railway rate limit: 500 logs/sec)
COLLECTSTATIC_VERBOSITY=${COLLECTSTATIC_VERBOSITY:-0}
python manage.py collectstatic --noinput --clear --verbosity $COLLECTSTATIC_VERBOSITY 2>&1 | head -20 || true

# Always run force upload as fallback for admin files when using S3
# This ensures admin files are uploaded even if collectstatic has issues
if [ "$USE_S3_RAW" = "true" ] || [ "$USE_S3_RAW" = "1" ] || [ "$USE_S3_RAW" = "yes" ]; then
    echo "Running force upload for admin files..."
    python force_upload_admin_s3.py >/dev/null 2>&1 || true
    
    # Upload favicon to S3 (ensures it's available in production)
    echo "Uploading favicon to S3..."
    python upload_favicon_to_s3.py >/dev/null 2>&1 || true
    
    # Verify favicon was uploaded (silently)
    python << EOF >/dev/null 2>&1
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from kouekam_hub.storage import StaticStorage

storage = StaticStorage()
favicon_path = 'favicon.svg'
if not storage.exists(favicon_path):
    import sys
    print(f"WARNING: Favicon NOT found in S3", file=sys.stderr)
EOF
else
    # For WhiteNoise, verify favicon is in staticfiles
    echo "Verifying favicon for WhiteNoise..."
    if [ -f "staticfiles/favicon.svg" ]; then
        FAVICON_SIZE=$(wc -c < staticfiles/favicon.svg)
        echo "✓ Favicon collected to staticfiles ($FAVICON_SIZE bytes)"
    else
        echo "⚠ WARNING: Favicon not found in staticfiles directory"
        echo "   Attempting to copy favicon..."
        if [ -f "static/favicon.svg" ]; then
            cp static/favicon.svg staticfiles/favicon.svg
            echo "   ✓ Favicon copied to staticfiles"
        else
            echo "   ✗ ERROR: Source favicon not found at static/favicon.svg"
        fi
    fi
fi

# Verify admin static files were collected (minimal output)
python << EOF >/dev/null 2>&1
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from django.conf import settings
import time

admin_css = os.path.join(settings.STATIC_ROOT, 'admin', 'css', 'base.css')
admin_js = os.path.join(settings.STATIC_ROOT, 'admin', 'js', 'core.js')

if getattr(settings, 'USE_S3', False):
    # For S3, check if files exist in storage
    # Give S3 a moment for uploads to complete
    time.sleep(2)
    
    from kouekam_hub.storage import StaticStorage
    storage = StaticStorage()
    
    # Check multiple possible paths (with and without static/ prefix)
    css_paths = ['admin/css/base.css', 'static/admin/css/base.css']
    js_paths = ['admin/js/core.js', 'static/admin/js/core.js']
    
    css_found = False
    for path in css_paths:
        if storage.exists(path):
            css_url = storage.url(path)
            print(f"✓ Admin CSS found in S3: {path}")
            print(f"  URL: {css_url}")
            css_found = True
            break
    
    if not css_found:
        print("✗ Admin CSS NOT found in S3")
        print("  Tried paths: " + ", ".join(css_paths))
        print("  Note: Files may still be uploading. Check S3 console to verify.")
    
    js_found = False
    for path in js_paths:
        if storage.exists(path):
            js_url = storage.url(path)
            print(f"✓ Admin JS found in S3: {path}")
            print(f"  URL: {js_url}")
            js_found = True
            break
    
    if not js_found:
        print("✗ Admin JS NOT found in S3")
        print("  Tried paths: " + ", ".join(js_paths))
        print("  Note: Files may still be uploading. Check S3 console to verify.")
    
    # Also check using boto3 directly to list files
    try:
        import boto3
        s3_client = boto3.client('s3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        # List objects in static/admin/css/ prefix
        response = s3_client.list_objects_v2(
            Bucket=storage.bucket_name,
            Prefix='static/admin/css/',
            MaxKeys=5
        )
        if 'Contents' in response and len(response['Contents']) > 0:
            print(f"✓ Found {len(response['Contents'])} admin CSS files in S3")
            for obj in response['Contents'][:3]:
                print(f"  - {obj['Key']}")
        else:
            print("⚠ No admin CSS files found in S3 bucket")
            print("  → Attempting to force upload admin files...")
            # Try force upload as fallback
            try:
                import subprocess
                result = subprocess.run(['python', 'force_upload_admin_s3.py'], 
                                      capture_output=True, text=True, timeout=300)
                print(result.stdout)
                if result.stderr:
                    print("Errors:", result.stderr)
                if result.returncode == 0:
                    print("✓ Force upload completed")
                else:
                    print("⚠ Force upload had issues, but continuing...")
            except Exception as e:
                print(f"⚠ Could not run force upload: {e}")
    except Exception as e:
        print(f"⚠ Could not verify S3 files directly: {e}")
else:
    # For WhiteNoise, check STATIC_ROOT
    if os.path.exists(admin_css):
        size = os.path.getsize(admin_css)
        print(f"✓ Admin CSS collected: {admin_css} ({size} bytes)")
    else:
        print(f"✗ Admin CSS NOT collected: {admin_css}")
        print("  This will cause Django admin to be unstyled!")
    
    if os.path.exists(admin_js):
        size = os.path.getsize(admin_js)
        print(f"✓ Admin JS collected: {admin_js} ({size} bytes)")
    else:
        print(f"✗ Admin JS NOT collected: {admin_js}")
        print("  This will cause Django admin JavaScript to not work!")
EOF

# After collectstatic, verify files were uploaded to S3 (silently)
if [ "$USE_S3_RAW" = "true" ] || [ "$USE_S3_RAW" = "1" ] || [ "$USE_S3_RAW" = "yes" ]; then
    python << EOF >/dev/null 2>&1
import os
import django
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from kouekam_hub.storage import StaticStorage

storage = StaticStorage()
css_path = 'css/output.css'
if not storage.exists(css_path):
    print(f"WARNING: CSS file NOT found in S3 after collectstatic!", file=sys.stderr)
EOF
fi

# If using S3 and collectstatic didn't upload, try manual upload as fallback (silently)
USE_S3_RAW=$(echo "${USE_S3:-False}" | tr '[:upper:]' '[:lower:]')
if [ "$USE_S3_RAW" = "true" ] || [ "$USE_S3_RAW" = "1" ] || [ "$USE_S3_RAW" = "yes" ]; then
    python << EOF >/dev/null 2>&1
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from kouekam_hub.storage import StaticStorage
import os.path

css_source = 'static/css/output.css'
# Storage location is 'static', so we only need 'css/output.css' as the destination
css_dest = 'css/output.css'

if os.path.exists(css_source):
    try:
        storage = StaticStorage()
        # Delete old file if it exists at wrong path
        old_path = 'static/css/output.css'
        if storage.exists(old_path):
            storage.delete(old_path)
        # Upload to correct path
        with open(css_source, 'rb') as f:
            storage.save(css_dest, f)
    except Exception as e:
        import sys
        print(f"ERROR: Failed to manually upload CSS to S3: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
EOF
fi

# Verify S3 configuration (silently, only errors to stderr)
python << EOF >/dev/null 2>&1
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from django.conf import settings
import sys

if getattr(settings, 'USE_S3', False):
    # Try to verify S3 connection and check if CSS file exists
    try:
        from kouekam_hub.storage import StaticStorage
        storage = StaticStorage()
        
        # Check if CSS file exists in S3
        css_path = 'css/output.css'
        css_path_full = 'static/css/output.css'
        
        if not storage.exists(css_path) and not storage.exists(css_path_full):
            print(f"WARNING: CSS file NOT found in S3", file=sys.stderr)
    except Exception as e:
        print(f"ERROR: Could not verify S3 storage: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
EOF

# Verify CSS file was properly collected (only show errors)
if [ -f "staticfiles/css/output.css" ]; then
    CSS_SIZE=$(wc -c < staticfiles/css/output.css 2>/dev/null || echo 0)
    if [ "$CSS_SIZE" -eq 0 ]; then
        echo "WARNING: Collected CSS file is empty!" >&2
        if [ -f "static/css/output.css" ]; then
            SOURCE_SIZE=$(wc -c < static/css/output.css)
            if [ "$SOURCE_SIZE" -gt 0 ]; then
                mkdir -p staticfiles/css
                cp static/css/output.css staticfiles/css/output.css >/dev/null 2>&1
            fi
        fi
    fi
else
    if [ -f "static/css/output.css" ]; then
        mkdir -p staticfiles/css
        cp static/css/output.css staticfiles/css/output.css >/dev/null 2>&1
    fi
fi

# Check ALLOWED_HOSTS configuration
if [ -z "$ALLOWED_HOSTS" ] || [ "$ALLOWED_HOSTS" = "localhost,127.0.0.1" ]; then
    echo "⚠️  WARNING: ALLOWED_HOSTS is not configured for production!"
    echo "   Set ALLOWED_HOSTS environment variable to include your domain(s)"
    echo "   Example: ALLOWED_HOSTS=kouekamkamgou.uk,www.kouekamkamgou.uk"
    echo "   Without this, you will get HTTP 400 errors when accessing your site."
fi

echo "Starting server..."
exec "$@"

