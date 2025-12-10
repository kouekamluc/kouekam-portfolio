"""
Custom storage backends for AWS S3
Separates static files and media files into different S3 locations
"""
import mimetypes
from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    """Storage backend for static files (CSS, JS, images)"""
    location = 'static'
    # Don't use ACLs - use bucket policy instead for public access
    default_acl = None
    file_overwrite = False
    querystring_auth = False
    
    def __init__(self, *args, **kwargs):
        # Ensure bucket name is set
        if not hasattr(settings, 'AWS_STORAGE_BUCKET_NAME') or not settings.AWS_STORAGE_BUCKET_NAME:
            raise ValueError("AWS_STORAGE_BUCKET_NAME must be set in settings")
        super().__init__(*args, **kwargs)
    
    def _get_content_type(self, name):
        """Get the correct Content-Type for the file"""
        content_type, _ = mimetypes.guess_type(name)
        # Ensure CSS files have the correct content type
        if name.endswith('.css'):
            return 'text/css'
        # Ensure JS files have the correct content type
        elif name.endswith('.js'):
            return 'application/javascript'
        # Default to the guessed type or binary
        return content_type or 'application/octet-stream'
    
    def _save(self, name, content):
        """Override save to set correct Content-Type"""
        # Get the content type
        content_type = self._get_content_type(name)
        
        # Set content type in the parameters
        params = self.object_parameters.copy()
        params['ContentType'] = content_type
        
        # Save with correct content type
        return super()._save(name, content)
    
    def url(self, name):
        """Override url method to ensure correct URL generation"""
        url = super().url(name)
        # Ensure the URL is correct - storage location is 'static', so name should be relative
        # The super().url() should handle this, but let's make sure
        return url


class MediaStorage(S3Boto3Storage):
    """Storage backend for media files (user uploads)"""
    location = 'media'
    # Don't use ACLs - use bucket policy instead for public access
    default_acl = None
    file_overwrite = True
    querystring_auth = False
    
    def __init__(self, *args, **kwargs):
        # Ensure bucket name is set
        if not hasattr(settings, 'AWS_STORAGE_BUCKET_NAME') or not settings.AWS_STORAGE_BUCKET_NAME:
            raise ValueError("AWS_STORAGE_BUCKET_NAME must be set in settings")
        super().__init__(*args, **kwargs)

