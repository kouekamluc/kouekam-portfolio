#!/usr/bin/env python
"""
Script to update S3 bucket policy to allow public read access to media files.
This fixes the issue where uploaded images are not showing on the site.
"""
import os
import sys
import json
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from django.conf import settings
import boto3
from botocore.exceptions import ClientError

def update_bucket_policy():
    """Update S3 bucket policy to allow public read access to media files"""
    
    bucket_name = getattr(settings, 'AWS_STORAGE_BUCKET_NAME', '')
    if not bucket_name:
        print("❌ ERROR: AWS_STORAGE_BUCKET_NAME not set in settings")
        return False
    
    aws_access_key = getattr(settings, 'AWS_ACCESS_KEY_ID', '')
    aws_secret_key = getattr(settings, 'AWS_SECRET_ACCESS_KEY', '')
    region = getattr(settings, 'AWS_S3_REGION_NAME', 'us-east-1')
    
    if not aws_access_key or not aws_secret_key:
        print("❌ ERROR: AWS credentials not configured")
        print("   Set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY environment variables")
        return False
    
    print(f"🔧 Updating bucket policy for: {bucket_name}")
    print(f"   Region: {region}")
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=region
        )
        
        # Get current bucket policy
        try:
            current_policy = s3_client.get_bucket_policy(Bucket=bucket_name)
            current_policy_json = json.loads(current_policy['Policy'])
            print("   Current policy found, updating...")
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                print("   No existing policy, creating new one...")
                current_policy_json = {"Version": "2012-10-17", "Statement": []}
            else:
                raise
        
        # Check if media policy already exists
        has_media_policy = False
        for statement in current_policy_json.get('Statement', []):
            if statement.get('Sid') == 'PublicReadGetObjectMedia':
                has_media_policy = True
                print("   Media policy already exists, updating...")
                break
        
        # Add or update media policy
        if not has_media_policy:
            # Add new statement for media
            current_policy_json['Statement'].append({
                "Sid": "PublicReadGetObjectMedia",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{bucket_name}/media/*"
            })
        else:
            # Update existing statement
            for statement in current_policy_json['Statement']:
                if statement.get('Sid') == 'PublicReadGetObjectMedia':
                    statement['Resource'] = f"arn:aws:s3:::{bucket_name}/media/*"
                    break
        
        # Update bucket policy
        s3_client.put_bucket_policy(
            Bucket=bucket_name,
            Policy=json.dumps(current_policy_json)
        )
        
        print("✅ Bucket policy updated successfully!")
        print(f"   Media files at s3://{bucket_name}/media/* are now publicly readable")
        return True
        
    except ClientError as e:
        print(f"❌ ERROR: Failed to update bucket policy: {e}")
        print("\n   Manual steps:")
        print("   1. Go to AWS S3 Console")
        print(f"   2. Select bucket: {bucket_name}")
        print("   3. Go to Permissions > Bucket policy")
        print("   4. Add this statement to allow media access:")
        print(f'      {{"Sid": "PublicReadGetObjectMedia", "Effect": "Allow",')
        print(f'       "Principal": "*", "Action": "s3:GetObject",')
        print(f'       "Resource": "arn:aws:s3:::{bucket_name}/media/*"}}')
        return False
    except Exception as e:
        print(f"❌ ERROR: Unexpected error: {e}")
        return False

if __name__ == '__main__':
    success = update_bucket_policy()
    sys.exit(0 if success else 1)



