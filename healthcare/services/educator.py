"""Plain-language patient educator.

Turns the terse triage band + risk score into a friendly explanation the
patient can act on. Designed for low-literacy / rural audiences: short
sentences, no jargon, actionable next steps.

Output shape::

    {
        "explanation": str,         # 1-3 sentence plain-language summary
        "next_steps": [str, ...],   # bullet list of concrete actions
        "warning_signs": [str, ...] # when to escalate
    }
"""
from __future__ import annotations

from typing import Any


TRIAGE_COPY: dict[str, dict[str, Any]] = {
    "urgent": {
        "headline": "This sounds serious.",
        "next_steps": [
            "Go to the nearest hospital or call emergency services now.",
            "Do not eat, drink, or take new medicines before being seen.",
            "Ask a family member or neighbour to travel with you.",
        ],
        "warning_signs": [
            "Trouble breathing or speaking.",
            "Fainting or severe weakness.",
            "Symptoms getting worse every minute.",
        ],
    },
    "gp": {
        "headline": "You should see a doctor, but it's not an emergency.",
        "next_steps": [
            "Book an appointment with a clinician in the next 1–2 days.",
            "Drink plenty of water and rest.",
            "Note when the symptoms started and what makes them better or worse.",
        ],
        "warning_signs": [
            "Fever above 39 °C that does not respond to paracetamol.",
            "Symptoms last longer than 5 days without improvement.",
            "New symptoms like rash, vomiting, or breathing trouble.",
        ],
    },
    "self_care": {
        "headline": "This sounds manageable at home for now.",
        "next_steps": [
            "Rest and stay hydrated.",
            "Use over-the-counter pain relief if you can take it safely.",
            "Watch for any change over the next 24–48 hours.",
        ],
        "warning_signs": [
            "Pain or symptoms suddenly get worse.",
            "New symptoms you did not have before.",
            "No improvement after 2–3 days.",
        ],
    },
}


def explain(triage: str, risk_level: str) -> dict[str, Any]:
    """Return a friendly explanation + actionable next steps for the patient."""
    copy = TRIAGE_COPY.get(triage, TRIAGE_COPY["gp"])

    if risk_level == "high":
        lead = (
            f"{copy['headline']} Our risk model rates this as HIGH — please do "
            "not delay care."
        )
    elif risk_level == "moderate":
        lead = (
            f"{copy['headline']} Our risk model rates this as MODERATE — plan "
            "to be seen soon."
        )
    else:
        lead = (
            f"{copy['headline']} Our risk model rates this as LOW, but keep "
            "watching your symptoms."
        )

    return {
        "explanation": lead,
        "next_steps": copy["next_steps"],
        "warning_signs": copy["warning_signs"],
    }
