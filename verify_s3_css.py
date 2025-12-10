#!/usr/bin/env python3
"""
Quick script to verify what's actually in the S3 CSS file
Run this to check if the CSS on S3 has the classes you need
"""

import os
import django
import boto3

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from django.conf import settings

def verify_s3_css():
    """Download and verify CSS from S3"""
    print("=" * 60)
    print("Verifying CSS File on S3")
    print("=" * 60)
    print()
    
    if not getattr(settings, 'USE_S3', False):
        print("❌ USE_S3 is False")
        return
    
    bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
    if not bucket_name:
        print("❌ AWS_STORAGE_BUCKET_NAME not set")
        return
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        css_path = 'static/css/output.css'
        
        print(f"📥 Downloading CSS from S3...")
        print(f"   Bucket: {bucket_name}")
        print(f"   Path: {css_path}")
        print()
        
        # Download CSS
        response = s3_client.get_object(
            Bucket=bucket_name,
            Key=css_path
        )
        
        css_content = response['Body'].read().decode('utf-8')
        file_size = len(css_content)
        
        print(f"✅ CSS downloaded successfully")
        print(f"   Size: {file_size:,} bytes")
        print()
        
        # Check for key classes
        classes_to_check = [
            '.bg-gray-50',
            '.bg-gray-900',
            '.text-gray-900',
            '.text-white',
            '.flex',
            '.flex-col',
            '.min-h-screen',
            '.dark:bg-gray-900',
            '.dark:text-white',
        ]
        
        print("🔍 Checking for Tailwind classes:")
        print()
        
        found_classes = []
        missing_classes = []
        
        for class_name in classes_to_check:
            if class_name in css_content:
                found_classes.append(class_name)
                print(f"   ✅ {class_name}")
            else:
                missing_classes.append(class_name)
                print(f"   ❌ {class_name} - NOT FOUND")
        
        print()
        
        if missing_classes:
            print("⚠️  WARNING: Some classes are missing!")
            print(f"   Missing: {', '.join(missing_classes)}")
            print()
            print("   This means the CSS on S3 is outdated or incomplete.")
            print("   Solution: Rebuild CSS and re-upload to S3")
            print("   Run: python rebuild_and_upload_css.py")
        else:
            print("✅ All expected classes found in CSS!")
            print()
            print("   If styling still doesn't work, it's likely a browser cache issue.")
            print("   Try:")
            print("   1. Hard refresh: Ctrl + Shift + R")
            print("   2. Clear cache: Ctrl + Shift + Delete")
            print("   3. Test in incognito: Ctrl + Shift + N")
        
        print()
        print("=" * 60)
        print("First 500 characters of CSS:")
        print("=" * 60)
        print(css_content[:500])
        print("...")
        print()
        
        # Check if it looks like valid Tailwind CSS
        if '--tw-border-spacing-x' in css_content or '.bg-gray-50' in css_content:
            print("✅ CSS appears to be valid Tailwind CSS")
        else:
            print("⚠️  WARNING: CSS doesn't look like valid Tailwind CSS")
            print("   The file might be corrupted or empty")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    verify_s3_css()

