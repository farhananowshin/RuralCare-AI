"""Clinical workflow models for RuralCare."""
from django.db import models

from accounts.models import Doctor, Patient


class Appointment(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_CONFIRMED = 'confirmed'
    STATUS_COMPLETED = 'completed'
    STATUS_CANCELLED = 'cancelled'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_CONFIRMED, 'Confirmed'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='appointments'
    )
    doctor = models.ForeignKey(
        Doctor, on_delete=models.CASCADE, related_name='appointments'
    )
    scheduled_for = models.DateTimeField()
    reason = models.CharField(max_length=255, blank=True)
    status = models.CharField(
        max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scheduled_for']

    def __str__(self) -> str:
        return f"{self.patient} → {self.doctor} @ {self.scheduled_for:%Y-%m-%d %H:%M}"


class MedicalRecord(models.Model):
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name='medical_records'
    )
    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='authored_records',
    )
    diagnosis = models.CharField(max_length=255)
    prescription = models.TextField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        return f"{self.diagnosis} for {self.patient}"


class SymptomCheck(models.Model):
    """Persists a symptom-checker run. ``result`` is a JSON blob from the
    active :class:`healthcare.services.SymptomCheckerService` implementation."""
    patient = models.ForeignKey(
        Patient,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='symptom_checks',
    )
    symptoms = models.TextField()
    result = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self) -> str:
        owner = self.patient or 'Anonymous'
        return f"SymptomCheck({owner}) at {self.created_at:%Y-%m-%d %H:%M}"
