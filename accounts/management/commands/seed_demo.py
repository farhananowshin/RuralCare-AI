"""Seed demo data so the screens aren't empty on first run.

Idempotent: re-running won't duplicate rows. Creates:
  - 1 superuser (admin)
  - 3 doctors with distinct specialties (drsmith, drkhan, drpatel)
  - 5 patients (ravi, lakshmi, amit, sara, arjun)
  - Classic demo pair (dr_demo + patient_demo) with 3 appointments and 2 records
  - Pre-booked appointments (mix of pending + confirmed)
  - Medical records
  - Sample symptom-check rows
"""
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Doctor, Patient
from healthcare.models import Appointment, MedicalRecord, SymptomCheck
from healthcare.services import check_symptoms


def _ensure_user(username, first_name, last_name, email, password='demo1234'):
    user, _ = User.objects.get_or_create(
        username=username,
        defaults={'first_name': first_name, 'last_name': last_name, 'email': email},
    )
    user.first_name = first_name
    user.last_name = last_name
    user.email = email
    user.set_password(password)
    user.save()
    return user


class Command(BaseCommand):
    help = "Create demo users, appointments, and sample symptom checks."

    def handle(self, *args, **options):
        # ---- Superuser ----
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@ruralcare.test',
                password='admin1234',
            )
            self.stdout.write(self.style.SUCCESS('  + superuser admin / admin1234'))
        else:
            self.stdout.write('  - superuser admin already exists')

        # ---- Doctors (3 distinct specialties) ----
        doctor_specs = [
            {
                'username': 'drsmith',
                'first_name': 'Anita',
                'last_name': 'Smith',
                'email': 'anita.smith@ruralcare.test',
                'specialty': 'General Physician',
                'license_number': 'LIC-GP-001',
                'clinic_name': 'Sunrise Rural Clinic',
                'available_from': '09:00',
                'available_to': '17:00',
            },
            {
                'username': 'drkhan',
                'first_name': 'Imran',
                'last_name': 'Khan',
                'email': 'imran.khan@ruralcare.test',
                'specialty': 'Cardiologist',
                'license_number': 'LIC-CD-002',
                'clinic_name': 'Heart Care Centre',
                'available_from': '10:00',
                'available_to': '18:00',
            },
            {
                'username': 'drpatel',
                'first_name': 'Priya',
                'last_name': 'Patel',
                'email': 'priya.patel@ruralcare.test',
                'specialty': 'Pediatrician',
                'license_number': 'LIC-PD-003',
                'clinic_name': 'Little Stars Clinic',
                'available_from': '08:00',
                'available_to': '16:00',
            },
        ]
        doctors = []
        for spec in doctor_specs:
            user = _ensure_user(
                spec['username'], spec['first_name'], spec['last_name'], spec['email']
            )
            Doctor.objects.update_or_create(
                user=user,
                defaults={
                    'specialty': spec['specialty'],
                    'license_number': spec['license_number'],
                    'clinic_name': spec['clinic_name'],
                    'available_from': spec['available_from'],
                    'available_to': spec['available_to'],
                },
            )
            doctors.append(user.doctor)
            self.stdout.write(f'  - doctor {spec["username"]} / demo1234 ({spec["specialty"]})')

        # ---- Patients (5) ----
        patient_specs = [
            ('ravi',    'Ravi',    'Kumar',  'Gopalpur',   '+91-90000-00001'),
            ('lakshmi', 'Lakshmi', 'Devi',   'Rampur',     '+91-90000-00002'),
            ('amit',    'Amit',    'Singh',  'Madhopur',   '+91-90000-00003'),
            ('sara',    'Sara',    'Begum',  'Krishnapur', '+91-90000-00004'),
            ('arjun',   'Arjun',   'Yadav',  'Sultanpur',  '+91-90000-00005'),
        ]
        patients = []
        for uname, first, last, village, phone in patient_specs:
            user = _ensure_user(uname, first, last, f'{uname}@example.com')
            Patient.objects.update_or_create(
                user=user,
                defaults={'village': village, 'phone': phone},
            )
            patients.append(user.patient)
            self.stdout.write(f'  - patient {uname} / demo1234 ({village})')

        # ---- Classic demo pair (dr_demo + patient_demo) ----
        # These match the README and give the user something visibly populated
        # the moment they log in with the documented credentials.
        dr_demo_user = _ensure_user(
            'dr_demo', 'Demo', 'Doctor', 'dr_demo@ruralcare.test',
            password='demo12345',
        )
        dr_demo, _ = Doctor.objects.update_or_create(
            user=dr_demo_user,
            defaults={
                'specialty': 'General Physician',
                'license_number': 'LIC-DEMO-001',
                'clinic_name': 'RuralCare Demo Clinic',
                'available_from': '09:00',
                'available_to': '17:00',
            },
        )

        patient_demo_user = _ensure_user(
            'patient_demo', 'Demo', 'Patient', 'patient_demo@ruralcare.test',
            password='demo12345',
        )
        patient_demo, _ = Patient.objects.update_or_create(
            user=patient_demo_user,
            defaults={'village': 'Gopalpur', 'phone': '+91-90000-11111'},
        )

        # ---- 3 Appointments for patient_demo <-> dr_demo ----
        demo_appts = [
            (timezone.now() + timedelta(days=1), Appointment.STATUS_CONFIRMED,
             'Persistent dry cough and mild fever for 4 days'),
            (timezone.now() + timedelta(days=3), Appointment.STATUS_PENDING,
             'Follow-up visit for blood pressure check'),
            (timezone.now() + timedelta(days=5), Appointment.STATUS_CONFIRMED,
             'Routine seasonal checkup'),
        ]
        demo_appt_rows = []
        for scheduled_for, status, reason in demo_appts:
            appt, _ = Appointment.objects.update_or_create(
                patient=patient_demo,
                doctor=dr_demo,
                scheduled_for=scheduled_for,
                defaults={'reason': reason, 'status': status},
            )
            demo_appt_rows.append(appt)

        # ---- 2 Medical Records for patient_demo (authored by dr_demo) ----
        record_specs = [
            {
                'diagnosis': 'Seasonal Influenza',
                'prescription': 'Paracetamol 500mg — 1 tab every 6 hours for 3 days. Plenty of fluids and rest.',
                'notes': 'Patient reports fever for 3 days; symptoms consistent with seasonal flu. Follow up if fever persists.',
            },
            {
                'diagnosis': 'Mild Hypertension',
                'prescription': 'Amlodipine 5mg once daily in the morning. Low-salt diet and 30 min brisk walk daily.',
                'notes': 'Recheck BP after 2 weeks; advise reducing processed food intake.',
            },
        ]
        for spec in record_specs:
            MedicalRecord.objects.update_or_create(
                patient=patient_demo,
                diagnosis=spec['diagnosis'],
                defaults={
                    'doctor': dr_demo,
                    'prescription': spec['prescription'],
                    'notes': spec['notes'],
                },
            )

        # ---- A few additional appointments + records for richer dashboards ----
        appt_specs = [
            (patients[0], doctors[0], 2, 'Persistent cough and mild fever', Appointment.STATUS_CONFIRMED),
            (patients[1], doctors[1], 3, 'Chest discomfort on exertion', Appointment.STATUS_PENDING),
            (patients[2], doctors[2], 4, 'Child vaccinations due', Appointment.STATUS_CONFIRMED),
            (patients[3], doctors[0], 5, 'Routine checkup', Appointment.STATUS_PENDING),
            (patients[4], doctors[1], 7, 'Follow-up on blood pressure medication', Appointment.STATUS_PENDING),
        ]
        for patient, doctor, days, reason, status in appt_specs:
            Appointment.objects.get_or_create(
                patient=patient,
                doctor=doctor,
                scheduled_for=timezone.now() + timedelta(days=days),
                defaults={'reason': reason, 'status': status},
            )

        # One additional record per other sample patient
        MedicalRecord.objects.update_or_create(
            patient=patients[0],
            diagnosis='Seasonal flu',
            defaults={
                'doctor': doctors[0],
                'prescription': 'Paracetamol 500mg, 3x/day for 3 days. Rest and fluids.',
                'notes': 'Follow up if fever persists beyond 5 days.',
            },
        )
        MedicalRecord.objects.update_or_create(
            patient=patients[1],
            diagnosis='Mild hypertension',
            defaults={
                'doctor': doctors[1],
                'prescription': 'Amlodipine 5mg once daily. Low-salt diet.',
                'notes': 'Recheck BP after 2 weeks.',
            },
        )

        # ---- Symptom checks (3, one per triage band) ----
        symptom_samples = [
            ('fever, sore throat, cough for 3 days', patient_demo),
            ('back pain after lifting',              patients[2]),
            ('chest pain radiating to arm',          patients[1]),
        ]
        for text, patient in symptom_samples:
            SymptomCheck.objects.get_or_create(
                patient=patient,
                symptoms=text,
                defaults={'result': check_symptoms(text)},
            )

        self.stdout.write(self.style.SUCCESS('\nDemo data ready.'))
        self.stdout.write(self.style.HTTP_INFO('Logins:'))
        self.stdout.write('  Admin    : admin / admin1234')
        self.stdout.write('  Doctor   : dr_demo / demo12345  (General Physician)')
        self.stdout.write('  Patient  : patient_demo / demo12345  (Gopalpur)')
        self.stdout.write('  Doctors  : drsmith, drkhan, drpatel  (all demo1234)')
        self.stdout.write('  Patients : ravi, lakshmi, amit, sara, arjun  (all demo1234)')
