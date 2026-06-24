"""Healthcare views: appointments, records, symptom checker."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import Doctor, Patient
from .forms import AppointmentForm, MedicalRecordForm, SymptomCheckForm
from .models import Appointment, MedicalRecord, SymptomCheck
from .services import analyze, check_symptoms


def _resolve_patient(user):
    return getattr(user, 'patient', None)


def _resolve_doctor(user):
    return getattr(user, 'doctor', None)


@login_required
def appointment_list(request):
    patient = _resolve_patient(request.user)
    doctor = _resolve_doctor(request.user)
    context = {'patient': patient, 'doctor': doctor}
    if patient:
        context['appointments'] = (
            Appointment.objects.filter(patient=patient)
            .select_related('doctor__user')
            .order_by('-scheduled_for')
        )
    elif doctor:
        context['appointments'] = (
            Appointment.objects.filter(doctor=doctor)
            .select_related('patient__user')
            .order_by('-scheduled_for')
        )
    else:
        context['appointments'] = []
    return render(request, 'healthcare/appointment_list.html', context)


@login_required
def appointment_create(request):
    patient = _resolve_patient(request.user)
    if not patient:
        messages.error(request, 'Only patient accounts can book appointments.')
        return redirect('healthcare:appointment_list')
    form = AppointmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        appt = form.save(commit=False)
        appt.patient = patient
        appt.status = Appointment.STATUS_PENDING
        appt.save()
        messages.success(request, 'Appointment booked. Awaiting doctor confirmation.')
        return redirect('healthcare:appointment_list')
    return render(request, 'healthcare/appointment_form.html', {'form': form})


@login_required
def appointment_confirm(request, pk: int):
    doctor = _resolve_doctor(request.user)
    appt = get_object_or_404(Appointment, pk=pk, doctor=doctor)
    appt.status = Appointment.STATUS_CONFIRMED
    appt.save()
    messages.success(request, 'Appointment confirmed.')
    return redirect('healthcare:appointment_list')


@login_required
def record_list(request):
    patient = _resolve_patient(request.user)
    doctor = _resolve_doctor(request.user)
    context = {'patient': patient, 'doctor': doctor}
    if patient:
        context['records'] = patient.medical_records.select_related('doctor__user').order_by('-created_at')
    elif doctor:
        context['records'] = MedicalRecord.objects.filter(doctor=doctor).select_related('patient__user').order_by('-created_at')
    else:
        context['records'] = []
    return render(request, 'healthcare/record_list.html', context)


@login_required
def record_create(request, appointment_pk: int | None = None):
    """Doctors log a diagnosis/prescription for a patient."""
    doctor = _resolve_doctor(request.user)
    if not doctor:
        messages.error(request, 'Only doctor accounts can add medical records.')
        return redirect('healthcare:record_list')

    preset_appt = None
    preset_patient = None
    if appointment_pk is not None:
        preset_appt = get_object_or_404(Appointment, pk=appointment_pk, doctor=doctor)
        preset_patient = preset_appt.patient

    form = MedicalRecordForm(request.POST or None, doctor=doctor)
    if request.method == 'POST' and form.is_valid():
        record = form.save(commit=False)
        record.doctor = doctor
        record.save()
        messages.success(
            request,
            f"Medical record saved for {record.patient.user.get_full_name() or record.patient.user.username}.",
        )
        return redirect('healthcare:record_list')

    # GET: prefill the patient so the doctor doesn't have to re-select them.
    if not request.POST and preset_patient is not None:
        form.initial = {'patient': preset_patient.pk}

    # Surface the patient's most recent symptom check (if any) so the doctor
    # has the AI triage context in front of them while logging a diagnosis.
    recent_check = None
    target_patient = preset_patient
    if target_patient is None and request.method == 'GET':
        posted_patient = request.GET.get('patient')
        if posted_patient:
            target_patient = Patient.objects.filter(pk=posted_patient).first()
    if target_patient is not None:
        recent_check = (
            target_patient.symptom_checks
            .order_by('-created_at')
            .first()
        )

    return render(
        request,
        'healthcare/record_form.html',
        {'form': form, 'appointment': preset_appt, 'recent_check': recent_check},
    )


@login_required
def symptom_check(request):
    patient = _resolve_patient(request.user)
    form = SymptomCheckForm(request.POST or None)
    result = None
    if request.method == 'POST' and form.is_valid():
        symptoms_text = form.cleaned_data['symptoms']
        result = analyze(symptoms_text)
        check_row = SymptomCheck.objects.create(
            patient=patient,
            symptoms=symptoms_text,
            result=result,
        )
        result = check_row.result
    return render(
        request,
        'healthcare/symptom_check.html',
        {'form': form, 'result': result},
    )
