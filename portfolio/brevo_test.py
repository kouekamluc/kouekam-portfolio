"""
Test script to verify Brevo configuration.
Run this in Django shell: python manage.py shell < portfolio/brevo_test.py
Or: python manage.py shell, then: exec(open('portfolio/brevo_test.py').read())
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'kouekam_hub.settings')
django.setup()

from django.conf import settings
from portfolio.email_utils import send_email_via_brevo

print("=" * 60)
print("Brevo Configuration Test")
print("=" * 60)

# Check environment variables
print("\n1. Checking environment variables:")
brevo_api_key = getattr(settings, 'BREVO_API_KEY', None)
brevo_sender_email = getattr(settings, 'BREVO_SENDER_EMAIL', None)
brevo_sender_name = getattr(settings, 'BREVO_SENDER_NAME', 'Portfolio')
brevo_recipient = getattr(settings, 'BREVO_CONTACT_RECIPIENT_EMAIL', None)

print(f"   BREVO_API_KEY: {'✓ Set' if brevo_api_key else '✗ NOT SET'}")
print(f"   BREVO_SENDER_EMAIL: {brevo_sender_email or '✗ NOT SET'}")
print(f"   BREVO_SENDER_NAME: {brevo_sender_name}")
print(f"   BREVO_CONTACT_RECIPIENT_EMAIL: {brevo_recipient or '✗ NOT SET'}")

# Check SDK availability
print("\n2. Checking Brevo SDK:")
try:
    from sib_api_v3_sdk import ApiClient, Configuration, TransactionalEmailsApi
    print("   ✓ Brevo SDK is installed")
except ImportError as e:
    print(f"   ✗ Brevo SDK not available: {e}")
    exit(1)

# Test email sending
if brevo_api_key and brevo_sender_email and brevo_recipient:
    print("\n3. Testing email send:")
    print(f"   Sending test email to: {brevo_recipient}")
    
    success = send_email_via_brevo(
        subject="Test Email from Portfolio",
        message="This is a test email to verify Brevo configuration.",
        recipient_email=brevo_recipient,
        recipient_name="Test Recipient"
    )
    
    if success:
        print("   ✓ Test email sent successfully!")
        print("   Check your email inbox (and spam folder) for the test message.")
    else:
        print("   ✗ Test email failed. Check logs above for details.")
else:
    print("\n3. Skipping email test - missing required configuration")

print("\n" + "=" * 60)
