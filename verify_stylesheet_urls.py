"""
Script to verify all stylesheet URLs in the application.
This helps identify which stylesheets are failing to load.
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
from django.template.loader import render_to_string
from django.template import Context

def verify_stylesheet_urls():
    """Verify all stylesheet URLs in the application"""
    print("=" * 70)
    print("Stylesheet URL Verification")
    print("=" * 70)
    
    # Check configuration
    print("\n1. Static Files Configuration:")
    print(f"   DEBUG: {settings.DEBUG}")
    print(f"   STATIC_URL: {settings.STATIC_URL}")
    print(f"   STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"   USE_S3: {getattr(settings, 'USE_S3', False)}")
    
    if getattr(settings, 'USE_S3', False):
        print(f"   AWS_S3_CUSTOM_DOMAIN: {getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', 'Not set')}")
    
    # Check Django admin stylesheets
    print("\n2. Django Admin Stylesheets:")
    admin_stylesheets = [
        'admin/css/base.css',
        'admin/css/dashboard.css',
        'admin/css/forms.css',
        'admin/css/login.css',
        'admin/css/responsive.css',
    ]
    
    admin_found = []
    admin_missing = []
    
    for stylesheet in admin_stylesheets:
        # Check if file exists in source
        found_path = finders.find(stylesheet)
        if found_path:
            admin_found.append(stylesheet)
            print(f"   ✓ {stylesheet} found at: {found_path}")
        else:
            admin_missing.append(stylesheet)
            print(f"   ✗ {stylesheet} NOT found in source")
        
        # Check if collected (for WhiteNoise)
        if not getattr(settings, 'USE_S3', False):
            collected_path = os.path.join(settings.STATIC_ROOT, stylesheet)
            if os.path.exists(collected_path):
                size = os.path.getsize(collected_path)
                print(f"     → Collected: {collected_path} ({size} bytes)")
            else:
                print(f"     → NOT collected: {collected_path}")
        
        # Check URL generation
        try:
            url = staticfiles_storage.url(stylesheet)
            print(f"     → URL: {url}")
        except Exception as e:
            print(f"     → URL generation failed: {e}")
    
    # Check custom static CSS
    print("\n3. Custom Static CSS:")
    custom_css = 'css/output.css'
    found_path = finders.find(custom_css)
    if found_path:
        print(f"   ✓ {custom_css} found at: {found_path}")
        if os.path.exists(found_path):
            size = os.path.getsize(found_path)
            print(f"     Size: {size} bytes")
    else:
        print(f"   ✗ {custom_css} NOT found")
    
    if not getattr(settings, 'USE_S3', False):
        collected_path = os.path.join(settings.STATIC_ROOT, custom_css)
        if os.path.exists(collected_path):
            size = os.path.getsize(collected_path)
            print(f"   → Collected: {collected_path} ({size} bytes)")
        else:
            print(f"   → NOT collected: {collected_path}")
    
    try:
        url = staticfiles_storage.url(custom_css)
        print(f"   → URL: {url}")
    except Exception as e:
        print(f"   → URL generation failed: {e}")
    
    # Check favicon
    print("\n4. Favicon:")
    favicon = 'favicon.svg'
    found_path = finders.find(favicon)
    if found_path:
        print(f"   ✓ {favicon} found at: {found_path}")
    else:
        print(f"   ✗ {favicon} NOT found")
    
    # Check external CDN resources
    print("\n5. External CDN Resources:")
    cdn_resources = [
        ('Font Awesome', 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css'),
        ('Tailwind CSS', 'https://cdn.tailwindcss.com'),  # This is a script, not stylesheet
    ]
    
    print("   Note: CDN resources require internet connection")
    print("   Font Awesome CSS: https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css")
    print("   (Tailwind is loaded as a script, not a stylesheet)")
    
    # Summary
    print("\n6. Summary:")
    print(f"   Admin stylesheets found: {len(admin_found)}/{len(admin_stylesheets)}")
    if admin_missing:
        print(f"   ⚠ Missing admin stylesheets: {', '.join(admin_missing)}")
        print("   → Run: python manage.py collectstatic --noinput --clear")
    
    # Recommendations
    print("\n7. Recommendations:")
    
    if admin_missing or (not getattr(settings, 'USE_S3', False) and not os.path.exists(os.path.join(settings.STATIC_ROOT, 'admin/css/base.css'))):
        print("   ⚠ Admin stylesheets are missing!")
        print("   → Run: python manage.py collectstatic --noinput --clear")
        print("   → Restart your server after collectstatic")
    
    if not found_path and not os.path.exists(os.path.join(settings.STATIC_ROOT, custom_css)):
        print("   ⚠ Custom CSS file is missing!")
        print("   → Build CSS: npm run build:css:prod")
        print("   → Run: python manage.py collectstatic --noinput")
    
    if not settings.DEBUG:
        print("   ⚠ DEBUG=False: Ensure collectstatic has been run")
        print("   ⚠ Ensure WhiteNoise middleware is active (if using WhiteNoise)")
        print("   ⚠ Restart server after collectstatic")
    
    print("\n8. Test URLs:")
    print("   Test these URLs in your browser:")
    if not getattr(settings, 'USE_S3', False):
        base_url = "https://yourdomain.com"  # Replace with your actual domain
    else:
        base_url = f"https://{getattr(settings, 'AWS_S3_CUSTOM_DOMAIN', 'your-s3-domain')}"
    
    print(f"   - {base_url}{settings.STATIC_URL}admin/css/base.css")
    print(f"   - {base_url}{settings.STATIC_URL}admin/css/dashboard.css")
    print(f"   - {base_url}{settings.STATIC_URL}admin/css/forms.css")
    print(f"   - {base_url}{settings.STATIC_URL}admin/css/login.css")
    print(f"   - {base_url}{settings.STATIC_URL}admin/css/responsive.css")
    print(f"   - {base_url}{settings.STATIC_URL}css/output.css")
    
    print("\n" + "=" * 70)
    
    # Return status
    if admin_missing:
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(verify_stylesheet_urls())

