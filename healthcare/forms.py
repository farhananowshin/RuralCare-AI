"""Healthcare forms."""
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from accounts.models import Doctor, Patient
from .models import Appointment, MedicalRecord, SymptomCheck


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'scheduled_for', 'reason']
        widgets = {
            'scheduled_for': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M',
            ),
            'reason': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Briefly describe your symptoms or visit reason',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['scheduled_for'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['doctor'].queryset = Doctor.objects.select_related('user').order_by('user__first_name')
        self.fields['doctor'].empty_label = '— Select a doctor —'
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Book appointment', css_class='btn btn-success w-100 mt-3'))


class SymptomCheckForm(forms.ModelForm):
    class Meta:
        model = SymptomCheck
        fields = ['symptoms']
        widgets = {
            'symptoms': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'e.g. fever for 3 days, sore throat, mild cough',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Check symptoms', css_class='btn btn-warning w-100 mt-3'))


class MedicalRecordForm(forms.ModelForm):
    """Used by doctors to log a diagnosis/prescription for one of their patients."""

    class Meta:
        model = MedicalRecord
        fields = ['patient', 'diagnosis', 'prescription', 'notes']
        widgets = {
            'diagnosis': forms.TextInput(attrs={'placeholder': 'e.g. Acute pharyngitis'}),
            'prescription': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'e.g. Paracetamol 500mg — 1 tab every 6h for 3 days',
            }),
            'notes': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Follow-up, lifestyle advice, etc. (optional)',
            }),
        }

    def __init__(self, *args, doctor=None, **kwargs):
        super().__init__(*args, **kwargs)

        if doctor is not None:
            # Prefer patients this doctor has seen; fall back to all patients.
            seen_patients = Patient.objects.filter(
                appointments__doctor=doctor
            ).distinct().select_related('user').order_by('user__first_name')
            self.fields['patient'].queryset = (
                seen_patients if seen_patients.exists()
                else Patient.objects.select_related('user').order_by('user__first_name')
            )
        else:
            self.fields['patient'].queryset = Patient.objects.select_related('user').order_by('user__first_name')

        self.fields['patient'].empty_label = '— Select a patient —'

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save record', css_class='btn btn-primary w-100 mt-3'))