"""
Complete fix for Django admin styling issue in production.
This script diagnoses and fixes all potential issues.
"""
import os
import sys
import django

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("⚠ requests library not available. URL testing will be skipped.")
    print("   Install with: pip install requests")

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from django.conf import settings
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage
from kouekam_hub.storage import StaticStorage

print("=" * 70)
print("Complete Django Admin Styling Fix")
print("=" * 70)

# Step 1: Check configuration
print("\n1. Configuration Check:")
print(f"   DEBUG: {settings.DEBUG}")
print(f"   USE_S3: {getattr(settings, 'USE_S3', False)}")
print(f"   STATIC_URL: {settings.STATIC_URL}")
print(f"   STATICFILES_STORAGE: {getattr(settings, 'STATICFILES_STORAGE', 'Not set')}")

if not getattr(settings, 'USE_S3', False):
    print("\n⚠ Not using S3. Admin files should be in STATIC_ROOT.")
    print("   Run: python manage.py collectstatic --noinput --clear")
    sys.exit(0)

# Step 2: Check if files exist in S3
print("\n2. Checking Files in S3:")
storage = StaticStorage()

admin_css = 'admin/css/base.css'
admin_js = 'admin/js/core.js'

css_exists = storage.exists(admin_css)
js_exists = storage.exists(admin_js)

print(f"   Admin CSS (base.css): {'✓ EXISTS' if css_exists else '✗ NOT FOUND'}")
print(f"   Admin JS (core.js): {'✓ EXISTS' if js_exists else '✗ NOT FOUND'}")

if not css_exists or not js_exists:
    print("\n   ⚠ Admin files are missing from S3!")
    print("   → Running upload script...")
    try:
        # Import and run upload script
        import upload_admin_to_s3
        upload_admin_to_s3.upload_admin_to_s3()
        # Re-check
        css_exists = storage.exists(admin_css)
        js_exists = storage.exists(admin_js)
        if css_exists and js_exists:
            print("   ✓ Files uploaded successfully!")
        else:
            print("   ✗ Upload failed. Check errors above.")
            sys.exit(1)
    except Exception as e:
        print(f"   ✗ Could not upload files: {e}")
        sys.exit(1)

# Step 3: Check URL generation
print("\n3. URL Generation Check:")
try:
    css_url = staticfiles_storage.url(admin_css)
    js_url = staticfiles_storage.url(admin_js)
    print(f"   CSS URL: {css_url}")
    print(f"   JS URL: {js_url}")
    
    # Verify URLs match expected format
    expected_domain = getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', '')
    if expected_domain and expected_domain not in css_url:
        print(f"   ⚠ WARNING: URL doesn't match expected domain!")
        print(f"   Expected: {expected_domain}")
        print(f"   Got: {css_url}")
except Exception as e:
    print(f"   ✗ Error generating URLs: {e}")
    sys.exit(1)

# Step 4: Test URL accessibility
print("\n4. Testing URL Accessibility:")
if not HAS_REQUESTS:
    print("   ⚠ Skipping URL test (requests not available)")
else:
    try:
        response = requests.get(css_url, timeout=10)
    if response.status_code == 200:
        print(f"   ✓ CSS URL is accessible (Status: {response.status_code})")
        print(f"   Content-Type: {response.headers.get('Content-Type', 'Not set')}")
        print(f"   Content-Length: {len(response.content)} bytes")
        
        # Check if it's actually CSS
        if 'text/css' in response.headers.get('Content-Type', '') or response.content.startswith(b'/*') or b'body' in response.content[:500]:
            print("   ✓ File contains CSS content")
        else:
            print("   ⚠ WARNING: File doesn't appear to be CSS!")
    elif response.status_code == 403:
        print(f"   ✗ CSS URL returns 403 Forbidden")
        print("   → S3 bucket policy doesn't allow public access!")
        print("   → Fix: Update S3 bucket policy to allow public read access")
    elif response.status_code == 404:
        print(f"   ✗ CSS URL returns 404 Not Found")
        print("   → File path is incorrect or file doesn't exist")
    else:
        print(f"   ⚠ CSS URL returns unexpected status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Could not access CSS URL: {e}")
        print("   → Check network connectivity or S3 bucket configuration")

# Step 5: Check S3 bucket policy
print("\n5. S3 Bucket Policy Check:")
try:
    import boto3
    s3_client = boto3.client('s3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )
    
    try:
        policy = s3_client.get_bucket_policy(Bucket=storage.bucket_name)
        print("   ✓ Bucket policy exists")
        # Check if policy allows public read
        policy_json = policy.get('Policy', '{}')
        if 's3:GetObject' in policy_json and 'Principal' in policy_json:
            print("   ✓ Policy appears to allow public access")
        else:
            print("   ⚠ Policy might not allow public access")
            print("   → Verify policy allows 's3:GetObject' for '*' principal")
    except s3_client.exceptions.from_code('NoSuchBucketPolicy'):
        print("   ⚠ No bucket policy found")
        print("   → Add bucket policy to allow public read access")
    except Exception as e:
        print(f"   ⚠ Could not check bucket policy: {e}")
except Exception as e:
    print(f"   ⚠ Could not check S3 configuration: {e}")

# Step 6: Check CORS
print("\n6. CORS Configuration Check:")
try:
    cors = s3_client.get_bucket_cors(Bucket=storage.bucket_name)
    print("   ✓ CORS configuration exists")
    for rule in cors.get('CORSRules', []):
        print(f"   Allowed Origins: {rule.get('AllowedOrigins', [])}")
        print(f"   Allowed Methods: {rule.get('AllowedMethods', [])}")
except s3_client.exceptions.from_code('NoSuchCORSConfiguration'):
    print("   ⚠ No CORS configuration found")
    print("   → Add CORS configuration to allow GET/HEAD from your domain")
except Exception as e:
    print(f"   ⚠ Could not check CORS: {e}")

# Step 7: Verify file paths in S3
print("\n7. Verifying File Paths in S3:")
try:
    # List files in static/admin/css/
    response = s3_client.list_objects_v2(
        Bucket=storage.bucket_name,
        Prefix=f"{storage.location}/admin/css/",
        MaxKeys=10
    )
    
    if 'Contents' in response:
        files = [obj['Key'] for obj in response['Contents']]
        print(f"   Found {len(files)} CSS files:")
        for key in sorted(files)[:5]:
            print(f"   - {key}")
        
        # Check for base.css
        base_css_key = f"{storage.location}/admin/css/base.css"
        if base_css_key in files:
            print(f"   ✓ base.css found at correct path: {base_css_key}")
        else:
            print(f"   ✗ base.css NOT found at expected path: {base_css_key}")
            print(f"   Found files: {files[:3]}")
    else:
        print(f"   ✗ No files found in {storage.location}/admin/css/")
except Exception as e:
    print(f"   ⚠ Could not list files: {e}")

# Step 8: Recommendations
print("\n8. Recommendations:")
issues_found = []

if not css_exists or not js_exists:
    issues_found.append("Admin files missing from S3")

try:
    response = requests.get(css_url, timeout=5)
    if response.status_code != 200:
        issues_found.append(f"CSS URL returns {response.status_code}")
except:
    issues_found.append("CSS URL not accessible")

if issues_found:
    print("   Issues found:")
    for issue in issues_found:
        print(f"   - {issue}")
    print("\n   Fix steps:")
    print("   1. Run: python upload_admin_to_s3.py")
    print("   2. Verify S3 bucket policy allows public read")
    print("   3. Check CORS configuration")
    print("   4. Test URLs in browser")
    print("   5. Check browser console for errors")
else:
    print("   ✓ All checks passed!")
    print("\n   If admin is still not styled:")
    print("   1. Clear browser cache (Ctrl+Shift+R)")
    print("   2. Check browser console for errors")
    print("   3. Verify STATIC_URL is correct in settings")
    print("   4. Check if Django admin template is using {% static %} correctly")

print("\n" + "=" * 70)
print("Diagnosis complete!")
print("=" * 70)

if issues_found:
    sys.exit(1)
else:
    sys.exit(0)

