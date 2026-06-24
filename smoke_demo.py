"""Focused smoke test for the user-journey flow requested.

Uses a single Client per role so cookies persist across requests.
"""
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ruralcare.settings")
django.setup()

from django.test import Client
from accounts.models import Doctor, Patient

def section(label):
    print()
    print("=" * 60)
    print(label)
    print("=" * 60)

def login(c, username, password):
    return c.post("/accounts/login/", {"username": username, "password": password},
                  follow=True)

# ---------- patient_demo ----------
section("PATIENT patient_demo / demo12345")
p = Client()
r = login(p, "patient_demo", "demo12345")
print(f"  POST /accounts/login/ (follow)        -> {r.status_code}  (final URL: {r.request['PATH_INFO']})")

for path in ["/accounts/dashboard/patient/", "/healthcare/appointments/",
             "/healthcare/appointments/book/", "/healthcare/records/"]:
    r = p.get(path)
    print(f"  GET  {path:40s} -> {r.status_code}")

# Book a new appointment
dr = Doctor.objects.first()
r = p.post("/healthcare/appointments/book/", {
    "doctor": dr.pk,
    "scheduled_for": "2026-07-10T10:30",
    "reason": "Persistent headache for 2 days",
}, follow=True)
print(f"  POST /healthcare/appointments/book/   -> {r.status_code}  (final URL: {r.request['PATH_INFO']})")

# Symptom check
r = p.post("/healthcare/symptom-check/",
           {"symptoms": "fever and dry cough for 3 days"}, follow=True)
print(f"  POST /healthcare/symptom-check/       -> {r.status_code}  (final URL: {r.request['PATH_INFO']})")

# ---------- dr_demo ----------
section("DOCTOR dr_demo / demo12345")
d = Client()
r = login(d, "dr_demo", "demo12345")
print(f"  POST /accounts/login/ (follow)        -> {r.status_code}  (final URL: {r.request['PATH_INFO']})")

for path in ["/accounts/dashboard/doctor/", "/healthcare/appointments/",
             "/healthcare/records/", "/healthcare/records/add/"]:
    r = d.get(path)
    print(f"  GET  {path:40s} -> {r.status_code}")

# Submit a new medical record for patient_demo
pdemo = Patient.objects.get(user__username="patient_demo")
r = d.post("/healthcare/records/add/", {
    "patient": pdemo.pk,
    "diagnosis": "Acute Bronchitis",
    "prescription": "Amoxicillin 500mg 3x/day for 5 days. Cough syrup as needed.",
    "notes": "Patient advised steam inhalation 2x daily. Follow up if cough persists beyond 7 days.",
}, follow=True)
print(f"  POST /healthcare/records/add/         -> {r.status_code}  (final URL: {r.request['PATH_INFO']})")

# Verify by re-fetching records
r = d.get("/healthcare/records/")
has_new = b"Acute Bronchitis" in r.content
print(f"  GET  /healthcare/records/ (after add) -> {r.status_code}  contains 'Acute Bronchitis': {has_new}")

print()
print("Smoke test complete.")