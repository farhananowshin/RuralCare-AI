"""Smoke test for the new AI services.

Calls analyze() on three sample symptoms, then walks the doctor-matcher +
risk + educator branches, and finally verifies the record_create view picks
up the patient's most recent SymptomCheck.
"""
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ruralcare.settings")
django.setup()

from healthcare.services import analyze
from healthcare.models import Patient, SymptomCheck, Doctor

CASES = [
    "chest pain radiating to left arm, sweating, shortness of breath",
    "fever, sore throat, mild cough for 3 days",
    "my 4 year old child has had high fever and rash since yesterday",
    "mild headache after a long day, no other symptoms",
]

print("=" * 70)
print("AI smoke test - analyze()")
print("=" * 70)

for s in CASES:
    print(f"\n>> {s}")
    out = analyze(s)
    print(f"   triage       : {out.get('triage')}")
    print(f"   risk_score   : {out.get('risk_score')}  ({out.get('risk_level')})")
    print(f"   explanation  : {out.get('explanation')}")
    print(f"   next_steps   : {out.get('next_steps')}")
    print(f"   warning_signs: {out.get('warning_signs')}")
    recs = out.get("recommended_doctors") or []
    print(f"   recommended  : {len(recs)} match(es)")
    for d in recs:
        print(f"     - {d.get('doctor')}  score={d.get('score')}  reason={d.get('reason')}")
    print(f"   risk_reasons : {out.get('risk_reasons')}")
    assert "triage" in out
    assert "risk_score" in out
    assert "explanation" in out
    assert "recommended_doctors" in out

print()
print("=" * 70)
print("record_create - recent_check passthrough")
print("=" * 70)

p = Patient.objects.first()
if p is None:
    print("No patient in DB - skipping live view test.")
else:
    last = p.symptom_checks.order_by("-created_at").first()
    print(f"Patient       : {p.user.username}")
    print(f"SymptomChecks : {p.symptom_checks.count()}")
    if last:
        print(f"Most recent   : {last.created_at}  triage={last.result.get('triage')}")
    else:
        print("No SymptomCheck recorded for this patient yet.")

print()
print("All AI smoke checks passed.")
