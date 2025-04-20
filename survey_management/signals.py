from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from survey_management.models.user import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a new User is created"""
    if created:
        # Default to ADMIN role for superusers, PATIENT for regular users
        role = 'ADMIN' if instance.is_superuser else 'PATIENT'
        UserProfile.objects.create(user=instance, role=role)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when the User is saved"""
    # Create profile if it doesn't exist (for existing users)
    if not hasattr(instance, 'profile'):
        role = 'ADMIN' if instance.is_superuser else 'PATIENT'
        UserProfile.objects.create(user=instance, role=role)
    else:
        instance.profile.save()
