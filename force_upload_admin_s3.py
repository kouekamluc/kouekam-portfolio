"""
Force upload Django admin files to S3.
This bypasses collectstatic and uploads files directly.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from django.conf import settings
from django.contrib.staticfiles import finders
from kouekam_hub.storage import StaticStorage
import boto3

if not getattr(settings, 'USE_S3', False):
    print("Not using S3. This script is for S3 uploads only.")
    sys.exit(1)

print("=" * 70)
print("Force Upload Django Admin Files to S3")
print("=" * 70)

storage = StaticStorage()
s3_client = boto3.client('s3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME
)

print(f"\nS3 Configuration:")
print(f"  Bucket: {storage.bucket_name}")
print(f"  Location: {storage.location}")
print(f"  Static URL: {settings.STATIC_URL}")

# Get all admin files from Django
print("\nFinding admin files...")
admin_files = []

# Find all admin CSS files
css_files = [
    'admin/css/base.css',
    'admin/css/dashboard.css',
    'admin/css/forms.css',
    'admin/css/login.css',
    'admin/css/responsive.css',
    'admin/css/changelists.css',
    'admin/css/autocomplete.css',
    'admin/css/nav_sidebar.css',
    'admin/css/widgets.css',
    'admin/css/dark_mode.css',
    'admin/css/rtl.css',
    'admin/css/responsive_rtl.css',
    'admin/css/unusable_password_field.css',
]

# Find all admin JS files
js_files = [
    'admin/js/core.js',
    'admin/js/actions.js',
    'admin/js/calendar.js',
    'admin/js/cancel.js',
    'admin/js/change_form.js',
    'admin/js/filters.js',
    'admin/js/inlines.js',
    'admin/js/nav_sidebar.js',
    'admin/js/popup_response.js',
    'admin/js/prepopulate.js',
    'admin/js/prepopulate_init.js',
    'admin/js/SelectBox.js',
    'admin/js/SelectFilter2.js',
    'admin/js/autocomplete.js',
    'admin/js/urlify.js',
    'admin/js/jquery.init.js',
    'admin/js/theme.js',
    'admin/js/unusable_password_field.js',
]

all_files = css_files + js_files

print(f"Checking {len(all_files)} admin files...")

uploaded = 0
skipped = 0
failed = 0

for file_path in all_files:
    # Find the file
    found_path = finders.find(file_path)
    
    if not found_path or not os.path.exists(found_path):
        print(f"✗ {file_path} - Source file not found")
        failed += 1
        continue
    
    # Determine S3 key (with location prefix)
    s3_key = f"{storage.location}/{file_path}"
    
    # Check if file already exists in S3
    try:
        s3_client.head_object(Bucket=storage.bucket_name, Key=s3_key)
        print(f"⊘ {file_path} - Already exists in S3")
        skipped += 1
        continue
    except s3_client.exceptions.from_code('404'):
        # File doesn't exist, proceed with upload
        pass
    except Exception as e:
        print(f"⚠ {file_path} - Error checking S3: {e}")
    
    # Upload file directly using boto3
    try:
        # Determine content type
        content_type = 'text/css' if file_path.endswith('.css') else 'application/javascript' if file_path.endswith('.js') else None
        
        with open(found_path, 'rb') as f:
            upload_kwargs = {
                'Bucket': storage.bucket_name,
                'Key': s3_key,
                'Body': f,
                'CacheControl': 'max-age=86400',
            }
            
            if content_type:
                upload_kwargs['ContentType'] = content_type
            
            s3_client.put_object(**upload_kwargs)
        
        size = os.path.getsize(found_path)
        url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{s3_key}"
        print(f"✓ {file_path} - Uploaded ({size} bytes)")
        print(f"  S3 Key: {s3_key}")
        print(f"  URL: {url}")
        uploaded += 1
        
        # Verify upload
        try:
            s3_client.head_object(Bucket=storage.bucket_name, Key=s3_key)
            print(f"  ✓ Verified: File exists in S3")
        except:
            print(f"  ⚠ Warning: Could not verify upload")
            
    except Exception as e:
        print(f"✗ {file_path} - Upload failed: {e}")
        import traceback
        traceback.print_exc()
        failed += 1

print("\n" + "=" * 70)
print("Summary:")
print(f"  Uploaded: {uploaded}")
print(f"  Skipped (already exists): {skipped}")
print(f"  Failed: {failed}")
print("=" * 70)

# Verify critical files
print("\nVerifying critical files:")
critical_files = ['admin/css/base.css', 'admin/js/core.js']
for file_path in critical_files:
    s3_key = f"{storage.location}/{file_path}"
    try:
        response = s3_client.head_object(Bucket=storage.bucket_name, Key=s3_key)
        size = response['ContentLength']
        content_type = response.get('ContentType', 'Not set')
        url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}/{s3_key}"
        print(f"  ✓ {file_path}")
        print(f"    Size: {size} bytes")
        print(f"    Content-Type: {content_type}")
        print(f"    URL: {url}")
    except Exception as e:
        print(f"  ✗ {file_path} - NOT in S3: {e}")

if uploaded > 0:
    print("\n✓ Admin files uploaded successfully!")
    print("\nNext steps:")
    print("1. Test URLs in browser:")
    print(f"   - https://{settings.AWS_S3_CUSTOM_DOMAIN}/static/admin/css/base.css")
    print(f"   - https://{settings.AWS_S3_CUSTOM_DOMAIN}/static/admin/js/core.js")
    print("2. Clear browser cache (Ctrl+Shift+R)")
    print("3. Check admin page styling")
    print("4. Verify no 404 errors in browser console")

if failed > 0:
    print(f"\n⚠ {failed} files failed to upload.")
    print("Check errors above and verify:")
    print("1. AWS credentials are correct")
    print("2. S3 bucket permissions allow uploads")
    print("3. Network connectivity to S3")

sys.exit(0 if failed == 0 else 1)

