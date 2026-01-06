"""
Script to verify Django admin static files are properly collected and accessible.
Run this in production to diagnose admin styling issues.
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

def check_admin_static_files():
    """Check if Django admin static files are accessible"""
    print("=" * 60)
    print("Django Admin Static Files Verification")
    print("=" * 60)
    
    # Check settings
    print("\n1. Static Files Configuration:")
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   STATIC_URL: {settings.STATIC_URL}")
    print(f"   STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"   STATICFILES_STORAGE: {getattr(settings, 'STATICFILES_STORAGE', 'Not set')}")
    print(f"   USE_S3: {getattr(settings, 'USE_S3', False)}")
    
    if getattr(settings, 'USE_S3', False):
        print(f"   AWS_STORAGE_BUCKET_NAME: {getattr(settings, 'AWS_STORAGE_BUCKET_NAME', 'Not set')}")
        print(f"   AWS_S3_CUSTOM_DOMAIN: {getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', 'Not set')}")
    
    # Check if staticfiles_storage is configured
    print(f"\n2. Static Files Storage:")
    print(f"   Storage type: {type(staticfiles_storage).__name__}")
    print(f"   Storage module: {type(staticfiles_storage).__module__}")
    
    # Test finding admin CSS file
    print("\n3. Finding Admin Static Files:")
    admin_css_path = 'admin/css/base.css'
    admin_js_path = 'admin/js/core.js'
    
    # Try to find using finders (development mode)
    found_css = finders.find(admin_css_path)
    found_js = finders.find(admin_js_path)
    
    print(f"   Admin CSS (base.css):")
    if found_css:
        print(f"     ✓ Found at: {found_css}")
        if os.path.exists(found_css):
            size = os.path.getsize(found_css)
            print(f"     ✓ File exists ({size} bytes)")
        else:
            print(f"     ✗ File path exists but file not found")
    else:
        print(f"     ✗ Not found using finders")
    
    print(f"   Admin JS (core.js):")
    if found_js:
        print(f"     ✓ Found at: {found_js}")
        if os.path.exists(found_js):
            size = os.path.getsize(found_js)
            print(f"     ✓ File exists ({size} bytes)")
        else:
            print(f"     ✗ File path exists but file not found")
    else:
        print(f"     ✗ Not found using finders")
    
    # Check STATIC_ROOT for collected files
    print("\n4. Checking STATIC_ROOT for collected files:")
    static_root = settings.STATIC_ROOT
    if static_root and os.path.exists(static_root):
        admin_css_collected = os.path.join(static_root, admin_css_path)
        admin_js_collected = os.path.join(static_root, admin_js_path)
        
        print(f"   STATIC_ROOT exists: {static_root}")
        if os.path.exists(admin_css_collected):
            size = os.path.getsize(admin_css_collected)
            print(f"   ✓ Admin CSS collected: {admin_css_collected} ({size} bytes)")
        else:
            print(f"   ✗ Admin CSS NOT collected: {admin_css_collected}")
            # Check if admin directory exists
            admin_dir = os.path.join(static_root, 'admin')
            if os.path.exists(admin_dir):
                print(f"   Admin directory exists, listing contents:")
                try:
                    for root, dirs, files in os.walk(admin_dir):
                        level = root.replace(admin_dir, '').count(os.sep)
                        indent = ' ' * 2 * level
                        print(f"{indent}{os.path.basename(root)}/")
                        subindent = ' ' * 2 * (level + 1)
                        for file in files[:10]:  # Limit to first 10 files
                            print(f"{subindent}{file}")
                        if len(files) > 10:
                            print(f"{subindent}... and {len(files) - 10} more files")
                except Exception as e:
                    print(f"   Error listing directory: {e}")
            else:
                print(f"   ✗ Admin directory does not exist in STATIC_ROOT")
        
        if os.path.exists(admin_js_collected):
            size = os.path.getsize(admin_js_collected)
            print(f"   ✓ Admin JS collected: {admin_js_collected} ({size} bytes)")
        else:
            print(f"   ✗ Admin JS NOT collected: {admin_js_collected}")
    else:
        print(f"   ✗ STATIC_ROOT does not exist: {static_root}")
    
    # Check storage backend (for S3 or WhiteNoise)
    print("\n5. Checking Storage Backend:")
    try:
        # Try to get URL for admin CSS
        css_url = staticfiles_storage.url(admin_css_path)
        print(f"   Admin CSS URL: {css_url}")
        
        # Try to check if file exists in storage
        if hasattr(staticfiles_storage, 'exists'):
            exists = staticfiles_storage.exists(admin_css_path)
            print(f"   Admin CSS exists in storage: {exists}")
        else:
            print(f"   Storage backend doesn't support 'exists' method")
    except Exception as e:
        print(f"   ✗ Error checking storage: {e}")
        import traceback
        traceback.print_exc()
    
    # Recommendations
    print("\n6. Recommendations:")
    if not settings.DEBUG:
        if getattr(settings, 'USE_S3', False):
            print("   - Using S3 for static files")
            print("   - Run: python manage.py collectstatic --noinput")
            print("   - Verify files are uploaded to S3 bucket")
        else:
            print("   - Using WhiteNoise for static files")
            print("   - Run: python manage.py collectstatic --noinput")
            print("   - Verify files are in STATIC_ROOT directory")
            print("   - Ensure WhiteNoise middleware is in MIDDLEWARE")
    else:
        print("   - DEBUG=True: Static files should be served automatically")
    
    print("\n" + "=" * 60)
    
    # Return success/failure
    if not settings.DEBUG:
        if static_root and os.path.exists(static_root):
            admin_css_collected = os.path.join(static_root, admin_css_path)
            if os.path.exists(admin_css_collected):
                print("✓ Admin static files appear to be collected correctly")
                return 0
            else:
                print("✗ Admin static files are NOT collected. Run collectstatic!")
                return 1
        else:
            print("✗ STATIC_ROOT does not exist. Run collectstatic!")
            return 1
    else:
        print("✓ Development mode - static files should work automatically")
        return 0

if __name__ == '__main__':
    sys.exit(check_admin_static_files())



