"""
WSGI config for kouekam_hub project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "kouekam_hub.settings")

# Suppress verbose output in production to avoid Railway rate limiting
if not os.getenv('DEBUG', 'False').lower() in ('true', '1', 'yes', 'on'):
    # Redirect stdout to devnull in production to prevent settings dumps
    # But keep stderr for error messages (especially for Brevo email debugging)
    import logging
    logging.getLogger().setLevel(logging.ERROR)
    # Suppress print statements that might dump settings to stdout
    class SuppressOutput:
        def write(self, s):
            pass
        def flush(self):
            pass
    
    # Only suppress stdout if we're not in a shell/interactive mode
    # Keep stderr open for error messages
    if not sys.stdin.isatty():
        sys.stdout = SuppressOutput()
        # Don't suppress stderr - we need it for error messages and email debugging

application = get_wsgi_application()
