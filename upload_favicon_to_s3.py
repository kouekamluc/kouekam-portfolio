#!/usr/bin/env python3
"""
Script to upload favicon to S3
This ensures the favicon is available in production
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from django.conf import settings
from kouekam_hub.storage import StaticStorage
import boto3

def upload_favicon():
    """Upload favicon file to S3"""
    print("📤 Uploading favicon to S3...")
    
    if not getattr(settings, 'USE_S3', False):
        print("⚠️  USE_S3 is False, skipping S3 upload")
        print("   Run: python manage.py collectstatic --noinput")
        return False
    
    if not getattr(settings, 'AWS_STORAGE_BUCKET_NAME', ''):
        print("⚠️  AWS_STORAGE_BUCKET_NAME not set, skipping S3 upload")
        return False
    
    try:
        storage = StaticStorage()
        favicon_path = 'favicon.svg'
        local_favicon = 'static/favicon.svg'
        
        if not os.path.exists(local_favicon):
            print(f"❌ ERROR: Local favicon file not found: {local_favicon}")
            return False
        
        # Read the favicon file
        with open(local_favicon, 'rb') as f:
            favicon_content = f.read()
        
        print(f"   Local file size: {len(favicon_content):,} bytes")
        
        # Upload to S3
        print(f"   Uploading to S3: static/{favicon_path}")
        storage.save(favicon_path, open(local_favicon, 'rb'))
        
        # Verify upload
        if storage.exists(favicon_path):
            # Get the URL
            favicon_url = storage.url(favicon_path)
            print(f"✅ Favicon uploaded successfully!")
            print(f"   S3 URL: {favicon_url}")
            
            # Verify with boto3
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            full_path = f"{storage.location}/{favicon_path}"
            response = s3_client.head_object(
                Bucket=storage.bucket_name,
                Key=full_path
            )
            
            s3_size = response.get('ContentLength', 0)
            content_type = response.get('ContentType', '')
            
            print(f"   S3 file size: {s3_size:,} bytes")
            print(f"   Content-Type: {content_type}")
            
            if s3_size == len(favicon_content):
                print("✅ File sizes match - upload verified!")
            else:
                print(f"⚠️  WARNING: File sizes don't match (local: {len(favicon_content)}, S3: {s3_size})")
            
            # Check Content-Type
            if content_type != 'image/svg+xml':
                print(f"⚠️  WARNING: Content-Type is '{content_type}', should be 'image/svg+xml'")
                print("   Re-uploading with correct Content-Type...")
                
                s3_client.put_object(
                    Bucket=storage.bucket_name,
                    Key=full_path,
                    Body=favicon_content,
                    ContentType='image/svg+xml',
                    CacheControl='max-age=86400'
                )
                print("✅ Re-uploaded with correct Content-Type")
            
            return True
        else:
            print("❌ ERROR: File not found in S3 after upload")
            return False
            
    except Exception as e:
        print(f"❌ ERROR: Failed to upload to S3: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("Favicon S3 Upload Script")
    print("=" * 60)
    print()
    
    if upload_favicon():
        print()
        print("=" * 60)
        print("✅ Process complete!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Clear browser cache (Ctrl+Shift+Delete)")
        print("2. Hard refresh the page (Ctrl+F5)")
        print("3. Check the favicon in browser tab")
        print()
    else:
        print()
        print("=" * 60)
        print("❌ Upload failed")
        print("=" * 60)
        print()
        print("Alternative: Run collectstatic to upload all static files:")
        print("  python manage.py collectstatic --noinput")
        print()
        sys.exit(1)

if __name__ == '__main__':
    main()

