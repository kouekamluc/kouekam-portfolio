"""
Script to verify Django admin files are actually in S3.
Run this after collectstatic to verify files were uploaded correctly.
"""
import os
import sys
import django
import time

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from django.conf import settings

if not getattr(settings, 'USE_S3', False):
    print("Not using S3. This script is for S3 verification only.")
    sys.exit(0)

print("=" * 70)
print("S3 Admin Files Verification")
print("=" * 70)

# Wait a moment for any pending uploads
print("\nWaiting 3 seconds for S3 uploads to complete...")
time.sleep(3)

try:
    import boto3
    from kouekam_hub.storage import StaticStorage
    
    s3_client = boto3.client('s3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    
    storage = StaticStorage()
    bucket_name = storage.bucket_name
    
    print(f"\nChecking S3 bucket: {bucket_name}")
    print(f"Location prefix: {storage.location}")
    
    # Check admin CSS files
    print("\n1. Admin CSS Files:")
    css_prefix = f"{storage.location}/admin/css/"
    response = s3_client.list_objects_v2(
        Bucket=bucket_name,
        Prefix=css_prefix,
        MaxKeys=20
    )
    
    if 'Contents' in response:
        css_files = [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.css')]
        print(f"   Found {len(css_files)} CSS files:")
        for key in sorted(css_files)[:10]:
            size = next((obj['Size'] for obj in response['Contents'] if obj['Key'] == key), 0)
            print(f"   ✓ {key} ({size} bytes)")
        
        # Check for base.css specifically
        base_css = f"{storage.location}/admin/css/base.css"
        if base_css in css_files:
            print(f"\n   ✓ base.css found: {base_css}")
            # Get URL
            url = storage.url('admin/css/base.css')
            print(f"   URL: {url}")
        else:
            print(f"\n   ✗ base.css NOT found at: {base_css}")
    else:
        print(f"   ✗ No files found in {css_prefix}")
    
    # Check admin JS files
    print("\n2. Admin JS Files:")
    js_prefix = f"{storage.location}/admin/js/"
    response = s3_client.list_objects_v2(
        Bucket=bucket_name,
        Prefix=js_prefix,
        MaxKeys=20
    )
    
    if 'Contents' in response:
        js_files = [obj['Key'] for obj in response['Contents'] if obj['Key'].endswith('.js')]
        print(f"   Found {len(js_files)} JS files:")
        for key in sorted(js_files)[:10]:
            size = next((obj['Size'] for obj in response['Contents'] if obj['Key'] == key), 0)
            print(f"   ✓ {key} ({size} bytes)")
        
        # Check for core.js specifically
        core_js = f"{storage.location}/admin/js/core.js"
        if core_js in js_files:
            print(f"\n   ✓ core.js found: {core_js}")
            # Get URL
            url = storage.url('admin/js/core.js')
            print(f"   URL: {url}")
        else:
            print(f"\n   ✗ core.js NOT found at: {core_js}")
    else:
        print(f"   ✗ No files found in {js_prefix}")
    
    # Test URL accessibility
    print("\n3. Testing URL Generation:")
    test_files = [
        ('admin/css/base.css', 'Admin Base CSS'),
        ('admin/css/dashboard.css', 'Admin Dashboard CSS'),
        ('admin/css/forms.css', 'Admin Forms CSS'),
        ('admin/css/login.css', 'Admin Login CSS'),
        ('admin/css/responsive.css', 'Admin Responsive CSS'),
        ('admin/js/core.js', 'Admin Core JS'),
    ]
    
    for file_path, description in test_files:
        try:
            url = storage.url(file_path)
            # Check if file exists
            if storage.exists(file_path):
                print(f"   ✓ {description}: {url}")
            else:
                print(f"   ✗ {description}: File not found (URL would be: {url})")
        except Exception as e:
            print(f"   ✗ {description}: Error - {e}")
    
    # Summary
    print("\n4. Summary:")
    css_count = len(css_files) if 'Contents' in s3_client.list_objects_v2(Bucket=bucket_name, Prefix=css_prefix, MaxKeys=1) else 0
    js_count = len(js_files) if 'Contents' in s3_client.list_objects_v2(Bucket=bucket_name, Prefix=js_prefix, MaxKeys=1) else 0
    
    if css_count > 0 and js_count > 0:
        print(f"   ✓ Admin files are in S3 ({css_count} CSS, {js_count} JS files)")
        print("   ✓ URLs should be accessible")
        print("\n   Next steps:")
        print("   1. Test URLs in browser")
        print("   2. Check browser console for 404 errors")
        print("   3. Verify admin page loads with styling")
        return 0
    else:
        print("   ✗ Admin files are missing from S3")
        print("\n   Troubleshooting:")
        print("   1. Run: python manage.py collectstatic --noinput --clear")
        print("   2. Check S3 bucket permissions")
        print("   3. Verify AWS credentials")
        return 1

except ImportError:
    print("✗ boto3 not available. Install with: pip install boto3")
    return 1
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    return 1

if __name__ == '__main__':
    sys.exit(verify_s3_admin_files())

