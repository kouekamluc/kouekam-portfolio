from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.db import transaction
import logging
from .models import Profile

logger = logging.getLogger(__name__)

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create a Profile when a User is created"""
    if created:
        try:
            Profile.objects.get_or_create(user=instance)
        except Exception as e:
            logger.error(f"Error creating profile for user {instance.username}: {e}", exc_info=True)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the profile when the user is saved"""
    # Only save if profile exists to avoid recursion
    if kwargs.get('created', False):
        return  # Profile creation is handled by create_user_profile
    
    try:
        if hasattr(instance, 'profile'):
            # Use transaction to ensure atomicity
            with transaction.atomic():
                instance.profile.save()
    except Exception as e:
        logger.error(f"Error saving profile for user {instance.username}: {e}", exc_info=True)

