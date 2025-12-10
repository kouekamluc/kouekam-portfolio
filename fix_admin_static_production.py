"""
Emergency script to fix Django admin static files in production.
Run this script in your production environment to immediately fix admin styling.

Usage:
    python fix_admin_static_production.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from django.conf import settings
from django.core.management import call_command
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.storage import staticfiles_storage

def fix_admin_static():
    """Fix Django admin static files in production"""
    print("=" * 70)
    print("Django Admin Static Files - Production Fix")
    print("=" * 70)
    
    # Check current configuration
    print("\n1. Current Configuration:")
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   STATIC_URL: {settings.STATIC_URL}")
    print(f"   STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"   STATICFILES_STORAGE: {getattr(settings, 'STATICFILES_STORAGE', 'Not set')}")
    print(f"   USE_S3: {getattr(settings, 'USE_S3', False)}")
    
    # Check if WhiteNoise middleware is configured
    print("\n2. Middleware Check:")
    middleware_list = getattr(settings, 'MIDDLEWARE', [])
    whitenoise_found = any('whitenoise' in str(m).lower() for m in middleware_list)
    if whitenoise_found:
        print("   ✓ WhiteNoise middleware is configured")
    else:
        print("   ✗ WhiteNoise middleware NOT found!")
        print("   ⚠ This is required for serving static files in production")
    
    # Check if admin files exist before collection
    print("\n3. Checking Admin Files Before Collection:")
    admin_css_path = 'admin/css/base.css'
    admin_js_path = 'admin/js/core.js'
    
    found_css = finders.find(admin_css_path)
    found_js = finders.find(admin_js_path)
    
    if found_css:
        print(f"   ✓ Admin CSS found at: {found_css}")
    else:
        print(f"   ✗ Admin CSS NOT found - this is a problem!")
        return 1
    
    if found_js:
        print(f"   ✓ Admin JS found at: {found_js}")
    else:
        print(f"   ✗ Admin JS NOT found - this is a problem!")
        return 1
    
    # Run collectstatic
    print("\n4. Running collectstatic...")
    print("   This will collect ALL static files including Django admin files...")
    try:
        call_command('collectstatic', '--noinput', '--clear', verbosity=2)
        print("   ✓ collectstatic completed successfully")
    except Exception as e:
        print(f"   ✗ collectstatic failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Verify files were collected
    print("\n5. Verifying Admin Files Were Collected:")
    
    if getattr(settings, 'USE_S3', False):
        # Check S3
        from kouekam_hub.storage import StaticStorage
        storage = StaticStorage()
        
        if storage.exists(admin_css_path):
            css_url = storage.url(admin_css_path)
            print(f"   ✓ Admin CSS in S3: {css_url}")
        else:
            print(f"   ✗ Admin CSS NOT in S3!")
            return 1
        
        if storage.exists(admin_js_path):
            js_url = storage.url(admin_js_path)
            print(f"   ✓ Admin JS in S3: {js_url}")
        else:
            print(f"   ✗ Admin JS NOT in S3!")
            return 1
    else:
        # Check STATIC_ROOT
        admin_css_collected = os.path.join(settings.STATIC_ROOT, admin_css_path)
        admin_js_collected = os.path.join(settings.STATIC_ROOT, admin_js_path)
        
        if os.path.exists(admin_css_collected):
            size = os.path.getsize(admin_css_collected)
            print(f"   ✓ Admin CSS collected: {admin_css_collected} ({size} bytes)")
        else:
            print(f"   ✗ Admin CSS NOT collected: {admin_css_collected}")
            return 1
        
        if os.path.exists(admin_js_collected):
            size = os.path.getsize(admin_js_collected)
            print(f"   ✓ Admin JS collected: {admin_js_collected} ({size} bytes)")
        else:
            print(f"   ✗ Admin JS NOT collected: {admin_js_collected}")
            return 1
    
    # Test URL generation
    print("\n6. Testing URL Generation:")
    try:
        css_url = staticfiles_storage.url(admin_css_path)
        js_url = staticfiles_storage.url(admin_js_path)
        print(f"   Admin CSS URL: {css_url}")
        print(f"   Admin JS URL: {js_url}")
    except Exception as e:
        print(f"   ✗ Error generating URLs: {e}")
        return 1
    
    # Final recommendations
    print("\n7. Next Steps:")
    print("   ✓ Static files have been collected")
    print("   ⚠ IMPORTANT: Restart your application server!")
    print("   ⚠ This is required for changes to take effect")
    print("\n   After restarting:")
    print("   1. Visit your Django admin: https://yourdomain.com/admin/")
    print("   2. Open browser Developer Tools (F12)")
    print("   3. Check Console tab for any 404 errors")
    print("   4. Test static file URL directly:")
    print(f"      {css_url}")
    print("      Should return CSS content (not 404)")
    
    print("\n" + "=" * 70)
    print("✓ Fix completed! Restart your server now.")
    print("=" * 70)
    
    return 0

if __name__ == '__main__':
    sys.exit(fix_admin_static())

