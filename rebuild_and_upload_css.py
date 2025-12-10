#!/usr/bin/env python3
"""
Script to rebuild CSS and force re-upload to S3
This ensures the CSS on S3 is up-to-date with all Tailwind classes
"""

import os
import subprocess
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from django.conf import settings
from kouekam_hub.storage import StaticStorage
import boto3

def rebuild_css():
    """Rebuild the CSS file using Tailwind"""
    print("🔨 Rebuilding CSS...")
    
    # Check if npm is available
    try:
        subprocess.run(['npm', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ ERROR: npm is not installed or not in PATH")
        print("   Please install Node.js and npm")
        return False
    
    # Check if node_modules exists
    if not os.path.exists('node_modules'):
        print("📦 Installing npm dependencies...")
        try:
            subprocess.run(['npm', 'ci'], check=True)
        except subprocess.CalledProcessError:
            print("⚠️  npm ci failed, trying npm install...")
            subprocess.run(['npm', 'install'], check=True)
    
    # Build CSS
    print("🎨 Compiling Tailwind CSS...")
    try:
        result = subprocess.run(
            ['npx', 'tailwindcss', '-i', './static/css/input.css', '-o', './static/css/output.css', '--minify'],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Verify CSS file was created
        if os.path.exists('static/css/output.css'):
            file_size = os.path.getsize('static/css/output.css')
            print(f"✅ CSS built successfully: {file_size:,} bytes")
            
            # Verify it has content
            with open('static/css/output.css', 'r', encoding='utf-8') as f:
                content = f.read()
                if '.bg-gray-50' in content and '.flex' in content:
                    print("✅ CSS contains expected classes (.bg-gray-50, .flex)")
                    return True
                else:
                    print("⚠️  WARNING: CSS file doesn't contain expected classes!")
                    return False
        else:
            print("❌ ERROR: CSS file was not created")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR: CSS build failed")
        print(f"   Error: {e.stderr}")
        return False

def upload_to_s3():
    """Upload CSS file to S3"""
    print("\n📤 Uploading CSS to S3...")
    
    if not getattr(settings, 'USE_S3', False):
        print("⚠️  USE_S3 is False, skipping S3 upload")
        return False
    
    if not getattr(settings, 'AWS_STORAGE_BUCKET_NAME', ''):
        print("⚠️  AWS_STORAGE_BUCKET_NAME not set, skipping S3 upload")
        return False
    
    try:
        storage = StaticStorage()
        css_path = 'css/output.css'
        local_css = 'static/css/output.css'
        
        if not os.path.exists(local_css):
            print(f"❌ ERROR: Local CSS file not found: {local_css}")
            return False
        
        # Read the CSS file
        with open(local_css, 'rb') as f:
            css_content = f.read()
        
        print(f"   Local file size: {len(css_content):,} bytes")
        
        # Upload to S3
        print(f"   Uploading to S3: static/{css_path}")
        storage.save(css_path, open(local_css, 'rb'))
        
        # Verify upload
        if storage.exists(css_path):
            # Get the URL
            css_url = storage.url(css_path)
            print(f"✅ CSS uploaded successfully!")
            print(f"   S3 URL: {css_url}")
            
            # Verify with boto3
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            
            full_path = f"{storage.location}/{css_path}"
            response = s3_client.head_object(
                Bucket=storage.bucket_name,
                Key=full_path
            )
            
            s3_size = response.get('ContentLength', 0)
            content_type = response.get('ContentType', '')
            
            print(f"   S3 file size: {s3_size:,} bytes")
            print(f"   Content-Type: {content_type}")
            
            if s3_size == len(css_content):
                print("✅ File sizes match - upload verified!")
            else:
                print(f"⚠️  WARNING: File sizes don't match (local: {len(css_content)}, S3: {s3_size})")
            
            # Check Content-Type
            if content_type != 'text/css':
                print(f"⚠️  WARNING: Content-Type is '{content_type}', should be 'text/css'")
                print("   Re-uploading with correct Content-Type...")
                
                s3_client.put_object(
                    Bucket=storage.bucket_name,
                    Key=full_path,
                    Body=css_content,
                    ContentType='text/css',
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
    print("CSS Rebuild and S3 Upload Script")
    print("=" * 60)
    print()
    
    # Step 1: Rebuild CSS
    if not rebuild_css():
        print("\n❌ CSS rebuild failed. Exiting.")
        sys.exit(1)
    
    # Step 2: Upload to S3 (if configured)
    if getattr(settings, 'USE_S3', False):
        if not upload_to_s3():
            print("\n⚠️  S3 upload failed, but CSS was rebuilt locally")
            print("   You can manually run: python manage.py collectstatic --noinput")
    else:
        print("\n📝 S3 not configured, CSS rebuilt locally only")
        print("   Run: python manage.py collectstatic --noinput")
    
    print()
    print("=" * 60)
    print("✅ Process complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Clear browser cache (Ctrl+Shift+Delete)")
    print("2. Hard refresh the page (Ctrl+F5)")
    print("3. Test the CSS URL directly in browser")
    print()

if __name__ == '__main__':
    main()

