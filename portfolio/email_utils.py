"""
Email utility functions for sending emails via Brevo (formerly Sendinblue).
"""
import logging
from django.conf import settings
from sib_api_v3_sdk import ApiClient, Configuration, TransactionalEmailsApi, SendSmtpEmail, SendSmtpEmailSender, SendSmtpEmailTo

logger = logging.getLogger(__name__)


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
    # Check if Brevo API key is configured
    if not settings.BREVO_API_KEY:
        logger.error("BREVO_API_KEY is not configured. Cannot send email.")
        return False
    
    try:
        # Configure Brevo API client
        configuration = Configuration()
        configuration.api_key['api-key'] = settings.BREVO_API_KEY
        
        api_client = ApiClient(configuration)
        api_instance = TransactionalEmailsApi(api_client)
        
        # Set sender information
        sender_email = sender_email or settings.BREVO_SENDER_EMAIL
        sender_name = sender_name or settings.BREVO_SENDER_NAME
        
        # Create sender object
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
        
        # Send email
        api_response = api_instance.send_transac_email(send_smtp_email)
        logger.info(f"Email sent successfully via Brevo. Message ID: {api_response.message_id}")
        return True
        
    except Exception as e:
        logger.error(f"Error sending email via Brevo: {str(e)}", exc_info=True)
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
    recipient_email = settings.BREVO_CONTACT_RECIPIENT_EMAIL
    if not recipient_email:
        logger.error("BREVO_CONTACT_RECIPIENT_EMAIL is not configured.")
        return False
    
    return send_email_via_brevo(
        subject=email_subject,
        message=email_body,
        recipient_email=recipient_email,
        recipient_name="Portfolio Admin"
    )
