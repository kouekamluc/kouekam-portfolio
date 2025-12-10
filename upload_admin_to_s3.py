"""
Manually upload Django admin static files to S3.
Use this if collectstatic isn't uploading admin files to S3 correctly.
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

def upload_admin_to_s3():
    if not getattr(settings, 'USE_S3', False):
        print("Not using S3. This script is for S3 uploads only.")
        return 1

    print("=" * 70)
    print("Uploading Django Admin Files to S3")
    print("=" * 70)

    storage = StaticStorage()
    print(f"\nS3 Configuration:")
    print(f"  Bucket: {storage.bucket_name}")
    print(f"  Location: {storage.location}")
    print(f"  Static URL: {settings.STATIC_URL}")

    # Admin files to upload
    admin_files = [
        # CSS files
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
        # JS files
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

    print(f"\nUploading {len(admin_files)} admin files...")

    uploaded = 0
    failed = 0
    skipped = 0

    for file_path in admin_files:
        # Find the file
        found_path = finders.find(file_path)
        
        if not found_path or not os.path.exists(found_path):
            print(f"✗ {file_path} - Source file not found")
            failed += 1
            continue
        
        # Check if already exists in S3
        if storage.exists(file_path):
            print(f"⊘ {file_path} - Already exists in S3, skipping")
            skipped += 1
            continue
        
        # Upload the file
        try:
            with open(found_path, 'rb') as f:
                saved_name = storage.save(file_path, f)
                size = os.path.getsize(found_path)
                url = storage.url(file_path)
                print(f"✓ {file_path} - Uploaded ({size} bytes)")
                print(f"  URL: {url}")
                uploaded += 1
        except Exception as e:
            print(f"✗ {file_path} - Upload failed: {e}")
            failed += 1

    print("\n" + "=" * 70)
    print("Summary:")
    print(f"  Uploaded: {uploaded}")
    print(f"  Skipped (already exists): {skipped}")
    print(f"  Failed: {failed}")
    print("=" * 70)

    if uploaded > 0:
        print("\n✓ Admin files uploaded successfully!")
        print("  Test URLs:")
        print(f"  - {settings.STATIC_URL}admin/css/base.css")
        print(f"  - {settings.STATIC_URL}admin/js/core.js")
        print("\n  Next steps:")
        print("  1. Test URLs in browser")
        print("  2. Check admin page styling")
        print("  3. Verify no 404 errors in browser console")

    if failed > 0:
        print(f"\n⚠ {failed} files failed to upload. Check errors above.")
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(upload_admin_to_s3())
