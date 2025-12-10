"""
Custom storage backends for AWS S3
Separates static files and media files into different S3 locations
"""
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """Storage backend for static files (CSS, JS, images)"""
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = False
    querystring_auth = False
    
    def __init__(self, *args, **kwargs):
        # Ensure bucket name is set
        if not hasattr(settings, 'AWS_STORAGE_BUCKET_NAME') or not settings.AWS_STORAGE_BUCKET_NAME:
            raise ValueError("AWS_STORAGE_BUCKET_NAME must be set in settings")
        super().__init__(*args, **kwargs)


class MediaStorage(S3Boto3Storage):
    """Storage backend for media files (user uploads)"""
    location = 'media'
    default_acl = 'public-read'
    file_overwrite = True
    querystring_auth = False
    
    def __init__(self, *args, **kwargs):
        # Ensure bucket name is set
        if not hasattr(settings, 'AWS_STORAGE_BUCKET_NAME') or not settings.AWS_STORAGE_BUCKET_NAME:
            raise ValueError("AWS_STORAGE_BUCKET_NAME must be set in settings")
        super().__init__(*args, **kwargs)

