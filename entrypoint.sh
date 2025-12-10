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
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from django.conf import settings
from django.core.management import call_command
from kouekam_hub.storage import StaticStorage

print(f"STATICFILES_STORAGE: {getattr(settings, 'STATICFILES_STORAGE', 'Not set')}")
print(f"AWS_STORAGE_BUCKET_NAME: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'Not set')}")
print(f"AWS_ACCESS_KEY_ID: {'Set' if getattr(settings, 'AWS_ACCESS_KEY_ID', '') else 'Not set'}")

# Test storage initialization
try:
    storage = StaticStorage()
    print(f"✓ S3 storage initialized successfully")
    print(f"  Bucket: {storage.bucket_name}")
    print(f"  Location: {storage.location}")
    
    # Verify the storage is actually being used by collectstatic
    from django.contrib.staticfiles.storage import staticfiles_storage
    print(f"  Django staticfiles_storage type: {type(staticfiles_storage).__name__}")
    print(f"  Django staticfiles_storage module: {type(staticfiles_storage).__module__}")
    
    if 'StaticStorage' not in type(staticfiles_storage).__name__:
        print(f"  ⚠ WARNING: staticfiles_storage is not StaticStorage!")
        print(f"     This means collectstatic will not use S3!")
except Exception as e:
    print(f"❌ ERROR: Failed to initialize S3 storage: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
EOF
    if [ $? -ne 0 ]; then
        echo "❌ ERROR: S3 storage initialization failed!"
        exit 1
    fi
fi

# Run collectstatic with verbose output
# When using S3, collectstatic should upload directly to S3
# Note: "Copying" messages are normal - they mean copying from source to storage backend
echo "Running collectstatic (this will collect Django admin static files)..."
python manage.py collectstatic --noinput --clear --verbosity 2 2>&1 | tee /tmp/collectstatic.log | head -100

# Always run force upload as fallback for admin files when using S3
# This ensures admin files are uploaded even if collectstatic has issues
if [ "$USE_S3_RAW" = "true" ] || [ "$USE_S3_RAW" = "1" ] || [ "$USE_S3_RAW" = "yes" ]; then
    echo "Running force upload for admin files (ensures all files are in S3)..."
    python force_upload_admin_s3.py 2>&1 | grep -E "(Uploaded|Skipped|Failed|Summary|✓|✗|⚠)" || true
    
    # Upload favicon to S3 (ensures it's available in production)
    echo "Uploading favicon to S3..."
    python upload_favicon_to_s3.py 2>&1 | grep -E "(Uploaded|Skipped|Failed|✓|✗|⚠|ERROR|WARNING)" || true
    
    # Verify favicon was uploaded
    echo "Verifying favicon in S3..."
    python << EOF
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from kouekam_hub.storage import StaticStorage

storage = StaticStorage()
favicon_path = 'favicon.svg'

if storage.exists(favicon_path):
    favicon_url = storage.url(favicon_path)
    print(f"✓ Favicon found in S3: {favicon_url}")
else:
    print(f"⚠ WARNING: Favicon NOT found in S3 at: {favicon_path}")
    print(f"   The favicon may not appear in browser tabs!")
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

# Verify admin static files were collected
echo "Verifying Django admin static files were collected..."
python << EOF
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

# After collectstatic, verify files were uploaded to S3 (not just copied locally)
if [ "$USE_S3_RAW" = "true" ] || [ "$USE_S3_RAW" = "1" ] || [ "$USE_S3_RAW" = "yes" ]; then
    echo "Verifying files were uploaded to S3..."
    python << EOF
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from kouekam_hub.storage import StaticStorage

storage = StaticStorage()
css_path = 'css/output.css'

if storage.exists(css_path):
    print(f"✓ CSS file exists in S3: static/{css_path}")
else:
    print(f"⚠ WARNING: CSS file NOT found in S3 after collectstatic!")
    print(f"   This means collectstatic did not upload to S3.")
EOF
fi

# If using S3 and collectstatic didn't upload, try manual upload as fallback
USE_S3_RAW=$(echo "${USE_S3:-False}" | tr '[:upper:]' '[:lower:]')
if [ "$USE_S3_RAW" = "true" ] || [ "$USE_S3_RAW" = "1" ] || [ "$USE_S3_RAW" = "yes" ]; then
    echo "Attempting to manually upload CSS to S3 as fallback..."
    python << EOF
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
            print(f"  Deleted old file at: {old_path}")
        # Upload to correct path
        with open(css_source, 'rb') as f:
            storage.save(css_dest, f)
        print(f"✓ CSS file manually uploaded to S3: {css_dest}")
        print(f"  Full S3 path: static/{css_dest}")
        print(f"  URL: {storage.url(css_dest)}")
        # Verify it's accessible
        if storage.exists(css_dest):
            print(f"✓ Verified: File exists and is accessible")
        else:
            print(f"⚠ Warning: File uploaded but not found when checking")
    except Exception as e:
        print(f"⚠ Failed to manually upload CSS to S3: {e}")
        import traceback
        traceback.print_exc()
else:
    print(f"⚠ CSS source file not found: {css_source}")
EOF
fi

# Verify S3 configuration and check if files are actually uploaded
echo "Verifying S3 configuration..."
python << EOF
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from django.conf import settings

print(f"USE_S3: {getattr(settings, 'USE_S3', False)}")
print(f"STATICFILES_STORAGE: {getattr(settings, 'STATICFILES_STORAGE', 'Not set')}")
print(f"STATIC_URL: {getattr(settings, 'STATIC_URL', 'Not set')}")
print(f"AWS_STORAGE_BUCKET_NAME: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'Not set')}")

if getattr(settings, 'USE_S3', False):
    # Try to verify S3 connection and check if CSS file exists
    try:
        from kouekam_hub.storage import StaticStorage
        storage = StaticStorage()
        print(f"✓ S3 storage initialized")
        print(f"  Bucket: {storage.bucket_name}")
        print(f"  Location: {storage.location}")
        
        # Check if CSS file exists in S3
        # Storage location is 'static', so we check with 'css/output.css'
        # The full S3 path will be 'static/css/output.css'
        css_path = 'css/output.css'
        if storage.exists(css_path):
            print(f"✓ CSS file found in S3: static/{css_path}")
            # Get the URL
            css_url = storage.url(css_path)
            print(f"  CSS URL: {css_url}")
            
            # Check Content-Type and fix if needed
            try:
                import boto3
                s3_client = boto3.client('s3',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_S3_REGION_NAME
                )
                full_path = f"{storage.location}/{css_path}"
                response = s3_client.head_object(Bucket=storage.bucket_name, Key=full_path)
                content_type = response.get('ContentType', '')
                print(f"  Current Content-Type: {content_type}")
                
                # Check file size
                file_size = response.get('ContentLength', 0)
                print(f"  File size: {file_size} bytes")
                
                if content_type != 'text/css':
                    print(f"  ⚠ Content-Type is incorrect! Re-uploading with correct type...")
                    # Re-upload with correct Content-Type
                    local_css = 'static/css/output.css'
                    if os.path.exists(local_css):
                        with open(local_css, 'rb') as f:
                            s3_client.put_object(
                                Bucket=storage.bucket_name,
                                Key=full_path,
                                Body=f,
                                ContentType='text/css',
                                CacheControl='max-age=86400'
                            )
                        print(f"  ✓ Re-uploaded with correct Content-Type: text/css")
                    else:
                        print(f"  ⚠ Local CSS file not found for re-upload")
                else:
                    print(f"  ✓ Content-Type is correct")
                
                # Verify file is not empty and has content
                if file_size < 1000:
                    print(f"  ⚠ WARNING: CSS file is very small ({file_size} bytes), might be empty!")
                    # Try to download and check first few bytes
                    try:
                        obj_response = s3_client.get_object(Bucket=storage.bucket_name, Key=full_path)
                        first_bytes = obj_response['Body'].read(100)
                        if not first_bytes or len(first_bytes.strip()) == 0:
                            print(f"  ⚠ ERROR: CSS file appears to be empty!")
                        else:
                            print(f"  ✓ CSS file has content (first 100 bytes: {first_bytes[:50]}...)")
                    except Exception as e:
                        print(f"  ⚠ Could not verify CSS content: {e}")
                else:
                    print(f"  ✓ CSS file size looks good ({file_size} bytes)")
            except Exception as e:
                print(f"  ⚠ Could not check/fix Content-Type: {e}")
                import traceback
                traceback.print_exc()
        else:
            # Try the full path as fallback (in case it was saved differently)
            css_path_full = 'static/css/output.css'
            if storage.exists(css_path_full):
                print(f"✓ CSS file found in S3: {css_path_full}")
                css_url = storage.url(css_path_full)
                print(f"  CSS URL: {css_url}")
            else:
                print(f"⚠ WARNING: CSS file NOT found in S3")
                print(f"  Tried: {css_path} and {css_path_full}")
                print(f"  This means collectstatic didn't upload to S3!")
    except Exception as e:
        print(f"⚠ Warning: Could not verify S3 storage: {e}")
        import traceback
        traceback.print_exc()
EOF

# Verify CSS file was properly collected
if [ -f "staticfiles/css/output.css" ]; then
    CSS_SIZE=$(wc -c < staticfiles/css/output.css)
    echo "✓ CSS collected to staticfiles ($CSS_SIZE bytes)"
    if [ "$CSS_SIZE" -eq 0 ]; then
        echo "⚠ WARNING: Collected CSS file is empty! This will cause a blank page."
        echo "   Checking source file..."
        if [ -f "static/css/output.css" ]; then
            SOURCE_SIZE=$(wc -c < static/css/output.css)
            echo "   Source CSS file size: $SOURCE_SIZE bytes"
            if [ "$SOURCE_SIZE" -gt 0 ]; then
                echo "   Attempting to manually copy CSS file..."
                mkdir -p staticfiles/css
                cp static/css/output.css staticfiles/css/output.css
                echo "   CSS file manually copied ($(wc -c < staticfiles/css/output.css) bytes)"
            fi
        fi
    else
        # Verify file is readable and has content
        FIRST_LINE=$(head -c 100 staticfiles/css/output.css)
        if [ -z "$FIRST_LINE" ]; then
            echo "⚠ WARNING: CSS file exists but appears to be empty or unreadable"
        else
            echo "✓ CSS file verified and readable"
        fi
    fi
else
    echo "⚠ WARNING: CSS file not found in staticfiles directory"
    echo "   Listing staticfiles/css directory:"
    ls -la staticfiles/css/ 2>/dev/null || echo "   Directory does not exist"
    echo "   Attempting to manually copy CSS file..."
    if [ -f "static/css/output.css" ]; then
        mkdir -p staticfiles/css
        cp static/css/output.css staticfiles/css/output.css
        echo "   CSS file manually copied ($(wc -c < staticfiles/css/output.css) bytes)"
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

