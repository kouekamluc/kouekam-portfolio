"""
Email utility functions for sending emails via Brevo (formerly Sendinblue).
"""
import logging
import sys
from django.conf import settings

logger = logging.getLogger(__name__)

# Try to import Brevo SDK
BREVO_SDK_AVAILABLE = False
ApiClient = None
Configuration = None
TransactionalEmailsApi = None
SendSmtpEmail = None
SendSmtpEmailSender = None
SendSmtpEmailTo = None

try:
    from sib_api_v3_sdk import ApiClient, Configuration, TransactionalEmailsApi, SendSmtpEmail, SendSmtpEmailSender, SendSmtpEmailTo
    BREVO_SDK_AVAILABLE = True
except ImportError as e:
    BREVO_SDK_AVAILABLE = False
    logger.error(f"Brevo SDK not available: {e}", exc_info=True)


def send_email_via_brevo(subject, message, recipient_email, recipient_name=None, sender_email=None, sender_name=None):
    """
    Send an email using Brevo API.
    
    Args:
        subject: Email subject
        message: Email body (plain text)
        recipient_email: Recipient email address
        recipient_name: Optional recipient name
        sender_email: Optional sender email (defaults to BREVO_SENDER_EMAIL)
        sender_name: Optional sender name (defaults to BREVO_SENDER_NAME)
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Check if Brevo SDK is available
        if not BREVO_SDK_AVAILABLE or Configuration is None:
            error_msg = "Brevo SDK is not installed. Please install sib-api-v3-sdk package."
            logger.error(error_msg)
            print(f"ERROR: {error_msg}", file=sys.stderr)
            return False
        
        # Check if Brevo API key is configured
        brevo_api_key = getattr(settings, 'BREVO_API_KEY', None)
        if not brevo_api_key:
            error_msg = "BREVO_API_KEY is not configured in environment variables. Cannot send email."
            logger.error(error_msg)
            print(f"ERROR: {error_msg}", file=sys.stderr)
            return False
        
        # Configure Brevo API client
        try:
            configuration = Configuration()
            configuration.api_key['api-key'] = brevo_api_key
        except Exception as e:
            error_msg = f"Failed to configure Brevo API client: {str(e)}"
            logger.error(error_msg, exc_info=True)
            print(f"ERROR: {error_msg}", file=sys.stderr)
            return False
        
        try:
            api_client = ApiClient(configuration)
            api_instance = TransactionalEmailsApi(api_client)
        except Exception as e:
            error_msg = f"Failed to create Brevo API instance: {str(e)}"
            logger.error(error_msg, exc_info=True)
            print(f"ERROR: {error_msg}", file=sys.stderr)
            return False
        
        # Set sender information
        sender_email = sender_email or getattr(settings, 'BREVO_SENDER_EMAIL', None)
        sender_name = sender_name or getattr(settings, 'BREVO_SENDER_NAME', 'Portfolio')
        
        if not sender_email:
            error_msg = "BREVO_SENDER_EMAIL is not configured. Cannot send email."
            logger.error(error_msg)
            print(f"ERROR: {error_msg}", file=sys.stderr)
            return False
        
        # Create sender object
        try:
            sender = SendSmtpEmailSender(
                email=sender_email,
                name=sender_name
            )
            
            # Create recipient object
            recipient = SendSmtpEmailTo(
                email=recipient_email,
                name=recipient_name or recipient_email
            )
            
            # Create email object
            send_smtp_email = SendSmtpEmail(
                sender=sender,
                to=[recipient],
                subject=subject,
                html_content=None,
                text_content=message
            )
        except Exception as e:
            error_msg = f"Failed to create Brevo email objects: {str(e)}"
            logger.error(error_msg, exc_info=True)
            print(f"ERROR: {error_msg}", file=sys.stderr)
            return False
        
        # Send email
        print(f"INFO: Attempting to send email via Brevo...", file=sys.stderr)
        print(f"INFO: From: {sender_email} ({sender_name})", file=sys.stderr)
        print(f"INFO: To: {recipient_email}", file=sys.stderr)
        print(f"INFO: Subject: {subject}", file=sys.stderr)
        
        api_response = api_instance.send_transac_email(send_smtp_email)
        
        # Log full response for debugging
        print(f"INFO: Brevo API Response: {api_response}", file=sys.stderr)
        message_id = getattr(api_response, 'message_id', 'Unknown')
        
        success_msg = f"Email sent successfully via Brevo. Message ID: {message_id}"
        logger.info(success_msg)
        print(f"INFO: {success_msg}", file=sys.stderr)
        print(f"INFO: Email should be delivered to {recipient_email}", file=sys.stderr)
        return True
        
    except Exception as e:
        error_msg = f"Error sending email via Brevo: {str(e)}"
        error_type = type(e).__name__
        logger.error(error_msg, exc_info=True)
        print(f"ERROR: {error_type}: {error_msg}", file=sys.stderr)
        
        # Check for specific Brevo API errors
        if hasattr(e, 'status'):
            print(f"ERROR: Brevo API Status Code: {e.status}", file=sys.stderr)
        if hasattr(e, 'reason'):
            print(f"ERROR: Brevo API Reason: {e.reason}", file=sys.stderr)
        if hasattr(e, 'body'):
            print(f"ERROR: Brevo API Response Body: {e.body}", file=sys.stderr)
        
        import traceback
        traceback.print_exc(file=sys.stderr)
        return False


def send_contact_form_email(name, email, subject, message):
    """
    Send a contact form submission email via Brevo.
    
    Args:
        name: Sender's name
        email: Sender's email
        subject: Email subject
        message: Email message
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Format the email content
    email_subject = f'Contact Form: {subject or "No Subject"}'
    email_body = f"""New contact form submission from your portfolio website.

From: {name} ({email})
Subject: {subject or "No Subject"}

Message:
{message}

---
This email was sent from the contact form on your portfolio website.
"""
    
    # Send to the configured recipient
    recipient_email = getattr(settings, 'BREVO_CONTACT_RECIPIENT_EMAIL', None)
    if not recipient_email:
        error_msg = "BREVO_CONTACT_RECIPIENT_EMAIL is not configured in environment variables."
        logger.error(error_msg)
        print(f"ERROR: {error_msg}", file=sys.stderr)
        return False
    
    return send_email_via_brevo(
        subject=email_subject,
        message=email_body,
        recipient_email=recipient_email,
        recipient_name="Portfolio Admin"
    )
