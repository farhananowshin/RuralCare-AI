"""Registration forms for Patient and Doctor roles."""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit

from .models import Doctor, Patient


class _BaseRegistrationForm(UserCreationForm):
    """Shared fields + crispy layout for both registration forms."""

    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=60, required=False, label='First name')
    last_name = forms.CharField(max_length=60, required=False, label='Last name')

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email',
            'password1', 'password2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='col-md-6'),
                Column('last_name', css_class='col-md-6'),
            ),
            'username',
            'email',
            'password1',
            'password2',
            Submit('submit', 'Create account', css_class='btn btn-success w-100'),
        )


class PatientRegistrationForm(_BaseRegistrationForm):
    village = forms.CharField(max_length=120, required=False)
    phone = forms.CharField(max_length=20, required=False)
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
    )

    class Meta(_BaseRegistrationForm.Meta):
        fields = _BaseRegistrationForm.Meta.fields + (
            'date_of_birth', 'village', 'phone',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout.append(Submit('submit', 'Register as Patient', css_class='btn btn-success w-100'))

    def save(self, commit: bool = True):
        user = super().save(commit=commit)
        if commit:
            Patient.objects.update_or_create(
                user=user,
                defaults={
                    'date_of_birth': self.cleaned_data.get('date_of_birth'),
                    'village': self.cleaned_data.get('village', ''),
                    'phone': self.cleaned_data.get('phone', ''),
                },
            )
        return user


class DoctorRegistrationForm(_BaseRegistrationForm):
    specialty = forms.CharField(max_length=120, required=False)
    license_number = forms.CharField(max_length=60, required=False)
    clinic_name = forms.CharField(max_length=120, required=False)
    available_from = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    available_to = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta(_BaseRegistrationForm.Meta):
        fields = _BaseRegistrationForm.Meta.fields + (
            'specialty', 'license_number', 'clinic_name',
            'available_from', 'available_to',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper.layout.append(Submit('submit', 'Register as Doctor', css_class='btn btn-primary w-100'))

    def save(self, commit: bool = True):
        user = super().save(commit=commit)
        if commit:
            Doctor.objects.update_or_create(
                user=user,
                defaults={
                    'specialty': self.cleaned_data.get('specialty', ''),
                    'license_number': self.cleaned_data.get('license_number', ''),
                    'clinic_name': self.cleaned_data.get('clinic_name', ''),
                    'available_from': self.cleaned_data.get('available_from'),
                    'available_to': self.cleaned_data.get('available_to'),
                },
            )
        return user
