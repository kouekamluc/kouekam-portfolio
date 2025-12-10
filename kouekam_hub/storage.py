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
        # Ensure AWS credentials are set
        if not hasattr(settings, 'AWS_ACCESS_KEY_ID') or not settings.AWS_ACCESS_KEY_ID:
            raise ValueError("AWS_ACCESS_KEY_ID must be set in settings")
        if not hasattr(settings, 'AWS_SECRET_ACCESS_KEY') or not settings.AWS_SECRET_ACCESS_KEY:
            raise ValueError("AWS_SECRET_ACCESS_KEY must be set in settings")
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
        # Ensure SVG files have the correct content type
        elif name.endswith('.svg'):
            return 'image/svg+xml'
        # Default to the guessed type or binary
        return content_type or 'application/octet-stream'
    
    def _save(self, name, content):
        """Override save to set correct Content-Type"""
        # Get the content type
        content_type = self._get_content_type(name)
        
        # Ensure object_parameters dict exists
        if not hasattr(self, 'object_parameters') or self.object_parameters is None:
            self.object_parameters = {}
        
        # Temporarily update object_parameters to include ContentType
        original_params = self.object_parameters.copy()
        self.object_parameters = self.object_parameters.copy()  # Create a copy to avoid modifying shared dict
        self.object_parameters['ContentType'] = content_type
        
        try:
            # Save with correct content type
            result = super()._save(name, content)
        except Exception as e:
            # Log the error but don't fail silently
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to save {name} to S3: {e}")
            raise
        finally:
            # Restore original parameters
            self.object_parameters = original_params
        
        return result
    
    def url(self, name):
        """Override url method to ensure correct URL generation"""
        # Ensure name doesn't include the location prefix (it's already in self.location)
        # The storage location is 'static', so if name starts with 'static/', remove it
        if name.startswith('static/'):
            name = name[len('static/'):]
        elif name.startswith('/static/'):
            name = name[len('/static/'):]
        
        # Get the URL from the parent class
        url = super().url(name)
        
        # Ensure the URL is correct - should be https://bucket.s3.region.amazonaws.com/static/name
        # The super().url() should handle this, but let's verify
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
    
    def _get_content_type(self, name):
        """Get the correct Content-Type for the file"""
        content_type, _ = mimetypes.guess_type(name)
        # Ensure images have correct content types
        if name.endswith('.jpg') or name.endswith('.jpeg'):
            return 'image/jpeg'
        elif name.endswith('.png'):
            return 'image/png'
        elif name.endswith('.gif'):
            return 'image/gif'
        elif name.endswith('.webp'):
            return 'image/webp'
        elif name.endswith('.svg'):
            return 'image/svg+xml'
        # Default to the guessed type or binary
        return content_type or 'application/octet-stream'
    
    def _save(self, name, content):
        """Override save to set correct Content-Type for images"""
        # Get the content type
        content_type = self._get_content_type(name)
        
        # Ensure object_parameters dict exists
        if not hasattr(self, 'object_parameters') or self.object_parameters is None:
            self.object_parameters = {}
        
        # Temporarily update object_parameters to include ContentType
        original_params = self.object_parameters.copy()
        self.object_parameters = self.object_parameters.copy()
        self.object_parameters['ContentType'] = content_type
        
        try:
            # Save with correct content type
            result = super()._save(name, content)
        except Exception as e:
            # Log the error but don't fail silently
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to save {name} to S3: {e}")
            raise
        finally:
            # Restore original parameters
            self.object_parameters = original_params
        
        return result
    
    def url(self, name):
        """Override url method to ensure correct URL generation"""
        # Ensure name doesn't include the location prefix (it's already in self.location)
        # The storage location is 'media', so if name starts with 'media/', remove it
        if name.startswith('media/'):
            name = name[len('media/'):]
        elif name.startswith('/media/'):
            name = name[len('/media/'):]
        
        # Get the URL from the parent class
        url = super().url(name)
        
        # Ensure the URL is correct - should be https://bucket.s3.region.amazonaws.com/media/name
        return url

