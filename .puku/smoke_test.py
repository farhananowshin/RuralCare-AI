"""Quick smoke test for the RuralCare project. Run with:
  .\.venv\Scripts\python.exe .puku\smoke_test.py
"""
import os
import sys
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ruralcare.settings")
django.setup()

from django.test import Client

c = Client()
checks = [
    ("/", 200, "Home"),
    ("/accounts/login/", 200, "Login"),
    ("/accounts/register/patient/", 200, "Patient register"),
    ("/accounts/register/doctor/", 200, "Doctor register"),
]
failures = []
for path, expected, label in checks:
    resp = c.get(path)
    status = "OK" if resp.status_code == expected else "FAIL"
    sys.stdout.write(f"[{status}] {label} {path} -> {resp.status_code}\n")
    sys.stdout.flush()
    if resp.status_code != expected:
        failures.append((path, resp.status_code, expected))

# Login as superuser, then visit a protected page
from django.contrib.auth import get_user_model
U = get_user_model()
admin_user, _ = U.objects.get_or_create(
    username="smoketest_admin",
    defaults={"is_staff": True, "is_superuser": True, "email": "a@b.c"},
)
admin_user.set_password("smoketest_pw_123")
admin_user.save()
ok = c.login(username="smoketest_admin", password="smoketest_pw_123")
sys.stdout.write(f"[{'OK' if ok else 'FAIL'}] Login admin -> {ok}\n")
sys.stdout.flush()
if ok:
    for path, expected, label in [
        ("/accounts/dashboard/", 200, "Dashboard"),
        ("/healthcare/appointments/", 200, "Appointments list"),
        ("/healthcare/records/", 200, "Records list"),
        ("/healthcare/symptom-check/", 200, "Symptom check"),
    ]:
        resp = c.get(path)
        status = "OK" if resp.status_code == expected else "FAIL"
        sys.stdout.write(f"[{status}] {label} {path} -> {resp.status_code}\n")
        sys.stdout.flush()
        if resp.status_code != expected:
            failures.append((path, resp.status_code, expected))

# Service check
from healthcare.services import check_symptoms
import json
sys.stdout.write("\nSymptom checker service:\n")
sys.stdout.flush()
for s in [
    "chest pain radiating to arm",
    "fever, sore throat, cough for 3 days",
    "back pain after lifting",
]:
    out = check_symptoms(s)
    sys.stdout.write(f"IN : {s}\n")
    sys.stdout.write(f"OUT: {json.dumps(out)}\n\n")
    sys.stdout.flush()

# Cleanup
admin_user.delete()

sys.stdout.write(f"\nFailures: {failures if failures else 'none'}\n")
sys.stdout.flush()
sys.exit(0 if not failures else 1)
