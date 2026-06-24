"""Auto-create Patient/Doctor profile shells when a User is created.

We don't infer the role here - registration views create the right profile
explicitly. These signals just keep an idempotent safety net so any other
``User.objects.create_user`` call (e.g. ``createsuperuser``) doesn't leave
dangling references.
"""
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Doctor, Patient


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_profile(sender, instance, created, **kwargs):
    if not created:
        return
    Patient.objects.get_or_create(user=instance)
    Doctor.objects.get_or_create(user=instance)
