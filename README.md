# RuralCare AI

A Django 5 backend for a Rural Healthcare Support Platform — patient/doctor registration, appointment booking, medical records, and an AI Symptom Checker with a swappable backend.

## Stack

- Python 3.11+ / Django 5
- SQLite (default)
- `django-bootstrap5` + `django-crispy-forms` for UI
- Pluggable symptom-checker service (rule-based default, LLM stub included)

## Project layout

```
ruralcare/                # Django project package (settings, root urls)
accounts/                 # Patient/Doctor profiles + registration/auth views
  management/commands/
    seed_demo.py          # Populates demo data
healthcare/               # Appointments, MedicalRecord, SymptomCheck
  services/
    __init__.py           # check_symptoms() dispatcher
    rule_based.py         # Default rule-based backend
    llm.py                # LLM backend stub (swap-in point)
templates/                # Bootstrap base + per-app templates
db.sqlite3                # SQLite database
manage.py
requirements.txt
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo
python manage.py runserver
```

Then open http://127.0.0.1:8000/.

## URLs

- `/` — home
- `/accounts/register/patient/` — patient registration
- `/accounts/register/doctor/` — doctor registration
- `/accounts/login/` — login
- `/accounts/dashboard/` — role-aware dashboard
- `/healthcare/appointments/` — list appointments
- `/healthcare/appointments/book/` — book appointment
- `/healthcare/records/` — view medical records
- `/healthcare/symptom-check/` — AI symptom checker
- `/admin/` — Django admin

## AI Symptom Checker

The service is exposed through `healthcare.services.check_symptoms(text: str) -> dict`:

```json
{
  "triage": "self_care | gp | urgent",
  "conditions": [{"name": "...", "confidence": 0.0}],
  "advice": "..."
}
```

### Swap the backend

Set `RURALCARE_SYMPTOM_CHECKER_BACKEND` in `ruralcare/settings.py`:

```python
# Default — offline rule-based engine
RURALCARE_SYMPTOM_CHECKER_BACKEND = "healthcare.services.rule_based.RuleBasedSymptomChecker"

# LLM backend stub — requires OPENAI_API_KEY (or replace the body with your provider)
RURALCARE_SYMPTOM_CHECKER_BACKEND = "healthcare.services.llm.LLMSymptomChecker"
```

Each backend module must expose a `check(symptoms: str) -> dict` function. Add your own module under `healthcare/services/` and point the setting at it — no view changes required.

## Demo data

`python manage.py seed_demo` creates:

- 1 demo doctor (username `dr_demo` / password `demo12345`)
- 2 demo patients (username `patient_demo`, `patient_demo2` / password `demo12345`)
- 1 sample appointment
- 1 sample symptom-check result

Log in as any of them to explore the dashboards.# RuralCare-AI
