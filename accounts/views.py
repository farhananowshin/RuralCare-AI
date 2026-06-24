"""Views for the accounts app: registration, login, role-aware dashboards."""
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from .forms import DoctorRegistrationForm, PatientRegistrationForm


# ---------------------------------------------------------------------------
# Registration
# ---------------------------------------------------------------------------

@require_http_methods(['GET', 'POST'])
def register_patient(request):
    """Create a Patient profile. After success, redirect to the login page
    with a flash message (per spec)."""
    if request.user.is_authenticated:
        return redirect(_dashboard_url_for(request.user))
    form = PatientRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()  # creates User + Patient profile
        messages.success(
            request,
            'Patient account created successfully. Please sign in with your credentials.',
        )
        return redirect('accounts:login')
    return render(request, 'accounts/register_patient.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def register_doctor(request):
    """Create a Doctor profile. After success, redirect to the login page."""
    if request.user.is_authenticated:
        return redirect(_dashboard_url_for(request.user))
    form = DoctorRegistrationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()  # creates User + Doctor profile
        messages.success(
            request,
            'Doctor account created successfully. Please sign in with your credentials.',
        )
        return redirect('accounts:login')
    return render(request, 'accounts/register_doctor.html', {'form': form})


# ---------------------------------------------------------------------------
# Login / logout with role-aware redirect
# ---------------------------------------------------------------------------

def _dashboard_url_for(user) -> str:
    """Return the URL name for the user's role-specific dashboard."""
    if hasattr(user, 'doctor') and user.doctor:
        return 'accounts:doctor_dashboard'
    if hasattr(user, 'patient') and user.patient:
        return 'accounts:patient_dashboard'
    return 'accounts:dashboard'  # fallback (e.g., superuser)


@require_http_methods(['GET', 'POST'])
def login_view(request):
    """Authenticate then redirect to the role-specific dashboard."""
    if request.user.is_authenticated:
        return redirect(_dashboard_url_for(request.user))
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Welcome back, {user.first_name or user.username}!')
        return redirect(_dashboard_url_for(user))
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


# ---------------------------------------------------------------------------
# Dashboards
# ---------------------------------------------------------------------------

@login_required
def dashboard(request):
    """Generic dispatcher — sends the user to their role-specific dashboard."""
    return redirect(_dashboard_url_for(request.user))


@login_required
def patient_dashboard(request):
    """Patient dashboard: profile + past symptoms + upcoming appointments."""
    user = request.user
    patient = getattr(user, 'patient', None)
    if not patient:
        messages.error(request, 'No patient profile attached to your account.')
        return redirect('home')

    from healthcare.models import Appointment, SymptomCheck

    appointments = (
        Appointment.objects.filter(patient=patient)
        .select_related('doctor__user')
        .order_by('-scheduled_for')[:5]
    )
    symptom_checks = patient.symptom_checks.all()[:5]
    return render(
        request,
        'accounts/patient_dashboard.html',
        {
            'patient': patient,
            'appointments': appointments,
            'symptom_checks': symptom_checks,
        },
    )


@login_required
def doctor_dashboard(request):
    """Doctor dashboard: profile + incoming patient appointments."""
    user = request.user
    doctor = getattr(user, 'doctor', None)
    if not doctor:
        messages.error(request, 'No doctor profile attached to your account.')
        return redirect('home')

    from healthcare.models import Appointment

    appointments = (
        Appointment.objects.filter(doctor=doctor)
        .select_related('patient__user')
        .order_by('-scheduled_for')[:5]
    )
    return render(
        request,
        'accounts/doctor_dashboard.html',
        {
            'doctor': doctor,
            'appointments': appointments,
        },
    )
