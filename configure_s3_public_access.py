#!/usr/bin/env python3
"""
Script to configure S3 bucket for public static file access
This script will:
1. Configure CORS on the bucket
2. Set bucket policy for public read access
3. Verify the CSS file is accessible
"""

import boto3
import json
import os
import sys
from botocore.exceptions import ClientError

# Get configuration from environment variables
BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'kouekam-hub-assets')
REGION = os.getenv('AWS_S3_REGION_NAME', 'eu-north-1')
ALLOWED_ORIGINS = [
    'https://kouekamkamgou.uk',
    'https://www.kouekamkamgou.uk',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

def get_s3_client():
    """Get S3 client with credentials from environment"""
    access_key = os.getenv('AWS_ACCESS_KEY_ID')
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    if not access_key or not secret_key:
        print("❌ ERROR: AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY must be set")
        sys.exit(1)
    
    return boto3.client(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=REGION
    )

def configure_cors(s3_client):
    """Configure CORS on the S3 bucket"""
    print(f"🔧 Configuring CORS for bucket: {BUCKET_NAME}")
    
    cors_configuration = {
        'CORSRules': [
            {
                'AllowedHeaders': ['*'],
                'AllowedMethods': ['GET', 'HEAD'],
                'AllowedOrigins': ALLOWED_ORIGINS,
                'ExposeHeaders': ['ETag', 'Content-Length', 'Content-Type'],
                'MaxAgeSeconds': 3000
            }
        ]
    }
    
    try:
        s3_client.put_bucket_cors(
            Bucket=BUCKET_NAME,
            CORSConfiguration=cors_configuration
        )
        print("✅ CORS configuration updated successfully!")
        return True
    except ClientError as e:
        print(f"❌ ERROR: Failed to configure CORS: {e}")
        return False

def configure_bucket_policy(s3_client):
    """Configure bucket policy for public read access to static and media files"""
    print(f"🔧 Configuring bucket policy for public read access...")
    
    # Bucket policy that allows public read access to static and media files
    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "PublicReadGetObjectStatic",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{BUCKET_NAME}/static/*"
            },
            {
                "Sid": "PublicReadGetObjectMedia",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{BUCKET_NAME}/media/*"
            }
        ]
    }
    
    try:
        s3_client.put_bucket_policy(
            Bucket=BUCKET_NAME,
            Policy=json.dumps(bucket_policy)
        )
        print("✅ Bucket policy updated successfully!")
        return True
    except ClientError as e:
        print(f"❌ ERROR: Failed to configure bucket policy: {e}")
        print("   Note: You may need to enable 'Block public access' settings in S3 console")
        return False

def check_block_public_access(s3_client):
    """Check and warn about block public access settings"""
    print(f"🔍 Checking block public access settings...")
    
    try:
        response = s3_client.get_public_access_block(Bucket=BUCKET_NAME)
        settings = response['PublicAccessBlockConfiguration']
        
        if settings.get('BlockPublicAcls', False) or \
           settings.get('IgnorePublicAcls', False) or \
           settings.get('BlockPublicPolicy', False) or \
           settings.get('RestrictPublicBuckets', False):
            print("⚠️  WARNING: Public access is blocked on this bucket!")
            print("   You need to disable 'Block public access' in S3 console:")
            print(f"   1. Go to: https://console.aws.amazon.com/s3/buckets/{BUCKET_NAME}")
            print("   2. Click 'Permissions' tab")
            print("   3. Click 'Edit' on 'Block public access'")
            print("   4. Uncheck all 4 options")
            print("   5. Save changes")
            return False
        else:
            print("✅ Public access is not blocked")
            return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
            print("✅ No public access block configuration (public access allowed)")
            return True
        else:
            print(f"⚠️  Could not check public access block: {e}")
            return True  # Assume it's OK

def verify_css_file(s3_client):
    """Verify the CSS file exists and is accessible"""
    print(f"🔍 Verifying CSS file exists in S3...")
    
    css_path = 'static/css/output.css'
    
    try:
        # Check if file exists
        response = s3_client.head_object(Bucket=BUCKET_NAME, Key=css_path)
        file_size = response.get('ContentLength', 0)
        content_type = response.get('ContentType', '')
        
        print(f"✅ CSS file found:")
        print(f"   Path: {css_path}")
        print(f"   Size: {file_size} bytes")
        print(f"   Content-Type: {content_type}")
        
        # Try to get the file (public access test)
        try:
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': BUCKET_NAME, 'Key': css_path},
                ExpiresIn=0
            )
            # Remove query string to get public URL
            public_url = url.split('?')[0]
            print(f"   Public URL: {public_url}")
        except Exception as e:
            print(f"⚠️  Could not generate public URL: {e}")
        
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            print(f"❌ ERROR: CSS file not found at {css_path}")
            print("   Run 'python manage.py collectstatic' to upload files to S3")
        else:
            print(f"❌ ERROR: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("S3 Public Access Configuration Script")
    print("=" * 60)
    print()
    
    s3_client = get_s3_client()
    
    # Step 1: Check block public access
    if not check_block_public_access(s3_client):
        print()
        print("⚠️  Please fix the block public access settings first!")
        print("   Then run this script again.")
        sys.exit(1)
    
    print()
    
    # Step 2: Configure CORS
    if not configure_cors(s3_client):
        sys.exit(1)
    
    print()
    
    # Step 3: Configure bucket policy
    if not configure_bucket_policy(s3_client):
        print()
        print("⚠️  Bucket policy configuration failed.")
        print("   You may need to configure it manually in AWS Console")
    
    print()
    
    # Step 4: Verify CSS file
    verify_css_file(s3_client)
    
    print()
    print("=" * 60)
    print("✅ Configuration complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Clear your browser cache (Ctrl+Shift+Delete)")
    print("2. Hard refresh the page (Ctrl+F5)")
    print("3. Check browser console for any remaining errors")
    print()
    print(f"Test the CSS URL directly:")
    print(f"https://{BUCKET_NAME}.s3.{REGION}.amazonaws.com/static/css/output.css")

if __name__ == '__main__':
    main()

