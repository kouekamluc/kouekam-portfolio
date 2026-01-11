"""
Management command to initialize the Site object for django-allauth.
This is required for password reset emails and other allauth email functionality.
"""
import os
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings


class Command(BaseCommand):
    help = 'Initialize the Site object for django-allauth email URLs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--domain',
            type=str,
            help='Site domain (e.g., example.com or localhost:8000 for development)',
        )
        parser.add_argument(
            '--name',
            type=str,
            help='Site name (e.g., Kouekam Portfolio)',
        )

    def handle(self, *args, **options):
        # Get domain and name from options or environment variables
        # For production, prefer SITE_DOMAIN env var, or use first ALLOWED_HOSTS entry
        if options.get('domain'):
            domain = options.get('domain')
        elif os.getenv('SITE_DOMAIN'):
            domain = os.getenv('SITE_DOMAIN')
        elif os.getenv('ALLOWED_HOSTS'):
            # Use first allowed host as domain (common in production)
            allowed_hosts = os.getenv('ALLOWED_HOSTS', '').split(',')
            domain = allowed_hosts[0].strip() if allowed_hosts else 'localhost:8000'
        else:
            domain = 'localhost:8000'
        
        # Remove port if it's standard HTTP/HTTPS port
        if domain.endswith(':80'):
            domain = domain[:-3]
        elif domain.endswith(':443'):
            domain = domain[:-4]
        
        name = options.get('name') or os.getenv('SITE_NAME', 'Kouekam Portfolio')
        
        # Get or create the site with ID 1 (required by SITE_ID = 1 in settings)
        site, created = Site.objects.get_or_create(
            id=settings.SITE_ID,
            defaults={
                'domain': domain,
                'name': name,
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created Site (id={site.id}): {site.name} at {site.domain}'
                )
            )
        else:
            # Update existing site if domain or name is different
            updated = False
            if site.domain != domain:
                site.domain = domain
                updated = True
            if site.name != name:
                site.name = name
                updated = True
            
            if updated:
                site.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully updated Site (id={site.id}): {site.name} at {site.domain}'
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Site (id={site.id}) already configured: {site.name} at {site.domain}'
                    )
                )
