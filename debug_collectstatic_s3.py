"""
Debug script to understand why admin files aren't being uploaded to S3.
This will check the storage configuration and test uploading a file.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage

print("=" * 70)
print("Debug: collectstatic S3 Upload Issue")
print("=" * 70)

print("\n1. Configuration Check:")
print(f"   USE_S3: {getattr(settings, 'USE_S3', False)}")
print(f"   STATICFILES_STORAGE: {getattr(settings, 'STATICFILES_STORAGE', 'Not set')}")
print(f"   STATIC_ROOT: {settings.STATIC_ROOT}")
print(f"   STATIC_URL: {settings.STATIC_URL}")

if not getattr(settings, 'USE_S3', False):
    print("\n⚠ Not using S3. This script is for S3 debugging only.")
    sys.exit(0)

print("\n2. Storage Backend Check:")
print(f"   Storage type: {type(staticfiles_storage).__name__}")
print(f"   Storage module: {type(staticfiles_storage).__module__}")

from kouekam_hub.storage import StaticStorage
storage = StaticStorage()
print(f"   Bucket: {storage.bucket_name}")
print(f"   Location: {storage.location}")

print("\n3. Testing File Upload:")
# Find an admin CSS file
admin_css_path = 'admin/css/base.css'
found_path = finders.find(admin_css_path)

if found_path and os.path.exists(found_path):
    print(f"   ✓ Found admin CSS at: {found_path}")
    size = os.path.getsize(found_path)
    print(f"   File size: {size} bytes")
    
    # Try to upload it manually
    print("\n   Attempting to upload to S3...")
    try:
        with open(found_path, 'rb') as f:
            # The storage location is 'static', so we save as 'admin/css/base.css'
            # It will be stored at 'static/admin/css/base.css' in S3
            saved_name = storage.save('admin/css/base.css', f)
            print(f"   ✓ Uploaded successfully!")
            print(f"   Saved as: {saved_name}")
            
            # Check if it exists now
            if storage.exists('admin/css/base.css'):
                url = storage.url('admin/css/base.css')
                print(f"   ✓ Verified: File exists in S3")
                print(f"   URL: {url}")
            else:
                print(f"   ✗ File uploaded but not found when checking")
        except Exception as e:
            print(f"   ✗ Upload failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"   ✗ Could not open file for reading")
else:
    print(f"   ✗ Admin CSS file not found")

print("\n4. Checking What's Actually in S3:")
try:
    import boto3
    s3_client = boto3.client('s3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    
    # List all files in static/admin/
    prefix = f"{storage.location}/admin/"
    print(f"   Listing files in: s3://{storage.bucket_name}/{prefix}")
    
    response = s3_client.list_objects_v2(
        Bucket=storage.bucket_name,
        Prefix=prefix,
        MaxKeys=50
    )
    
    if 'Contents' in response:
        files = response['Contents']
        print(f"   Found {len(files)} files:")
        for obj in sorted(files, key=lambda x: x['Key'])[:20]:
            size = obj['Size']
            print(f"   - {obj['Key']} ({size} bytes)")
        
        # Check specifically for base.css
        base_css_key = f"{storage.location}/admin/css/base.css"
        if any(obj['Key'] == base_css_key for obj in files):
            print(f"\n   ✓ base.css IS in S3: {base_css_key}")
        else:
            print(f"\n   ✗ base.css NOT in S3: {base_css_key}")
    else:
        print(f"   ✗ No files found in {prefix}")
        print("   This means collectstatic did NOT upload admin files to S3")
        
except Exception as e:
    print(f"   ✗ Error checking S3: {e}")
    import traceback
    traceback.print_exc()

print("\n5. Recommendations:")
print("   If files are NOT in S3:")
print("   1. Check S3 bucket permissions")
print("   2. Verify AWS credentials are correct")
print("   3. Check collectstatic output for errors")
print("   4. Try running collectstatic with --verbosity 3")
print("   5. Check if STATICFILES_STORAGE is actually being used")

print("\n" + "=" * 70)

