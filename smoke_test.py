"""End-to-end smoke test for RuralCare AI.

Walks every URL as an anonymous visitor, then logs in as each demo role and
checks the role-specific dashboard + the full symptom-check flow.
"""
import os, django, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ruralcare.settings")
django.setup()

from django.test import Client

c = Client()
print("=" * 60)
print("ANONYMOUS")
print("=" * 60)
for path in ["/", "/accounts/login/", "/accounts/register/patient/",
             "/accounts/register/doctor/", "/healthcare/symptom-check/"]:
    r = c.get(path)
    print(f"  GET {path:40s} -> {r.status_code}")

print()
print("=" * 60)
print("PATIENT ravi")
print("=" * 60)
c.post("/accounts/login/", {"username": "ravi", "password": "demo1234"})
for path in ["/accounts/dashboard/", "/accounts/dashboard/patient/",
             "/healthcare/symptom-check/", "/healthcare/appointments/",
             "/healthcare/appointments/book/", "/healthcare/records/"]:
    r = c.get(path)
    print(f"  GET {path:40s} -> {r.status_code}")

print()
print("Posting symptoms...")
r = c.post("/healthcare/symptom-check/",
           {"symptoms": "I have a high fever and dry cough for 3 days"})
print(f"  POST symptom-check                -> {r.status_code}")

print()
print("=" * 60)
print("DOCTOR drsmith")
print("=" * 60)
c2 = Client()
c2.post("/accounts/login/", {"username": "drsmith", "password": "demo1234"})
for path in ["/accounts/dashboard/", "/accounts/dashboard/doctor/",
             "/healthcare/appointments/"]:
    r = c2.get(path)
    print(f"  GET {path:40s} -> {r.status_code}")

print()
print("=" * 60)
print("ADMIN")
print("=" * 60)
c3 = Client()
c3.post("/accounts/login/", {"username": "admin", "password": "admin1234"})
for path in ["/admin/", "/accounts/dashboard/"]:
    r = c3.get(path)
    print(f"  GET {path:40s} -> {r.status_code}")

print()
print("Smoke test complete.")