"""Identity models for RuralCare.

We use the default ``django.contrib.auth.User`` and attach a 1:1 ``Patient`` or
``Doctor`` profile to it. This keeps the auth machinery stock and avoids the
``AUTH_USER_MODEL`` migration dance mid-hackathon.
"""
from django.conf import settings
from django.db import models


class Patient(models.Model):
    """A patient profile, linked to a Django auth User."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient',
    )
    date_of_birth = models.DateField(null=True, blank=True)
    village = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self) -> str:
        full = self.user.get_full_name() or self.user.username
        return f"Patient: {full}"


class Doctor(models.Model):
    """A doctor profile, linked to a Django auth User."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor',
    )
    specialty = models.CharField(max_length=120, blank=True)
    license_number = models.CharField(max_length=60, blank=True)
    clinic_name = models.CharField(max_length=120, blank=True)
    available_from = models.TimeField(null=True, blank=True)
    available_to = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['user__first_name', 'user__last_name']

    def __str__(self) -> str:
        full = self.user.get_full_name() or self.user.username
        return f"Dr. {full} ({self.specialty or 'general'})"
