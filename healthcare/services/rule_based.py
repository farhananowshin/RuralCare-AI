"""Default offline symptom checker.

Maps keyword clusters to triage + candidate conditions. Deliberately simple
so the demo works without any external API or model download.
"""
from __future__ import annotations

import re
from typing import Any

# Order matters: first matching cluster wins. Keep clusters disjoint.
SYMPTOM_RULES: list[dict[str, Any]] = [
    {
        "name": "Cardiac emergency",
        "triage": "urgent",
        "keywords": [
            r"chest pain", r"crushing pain", r"radiating to (?:arm|jaw)",
            r"shortness of breath", r"unconscious", r"fainting",
        ],
        "conditions": [
            ("Myocardial infarction", 0.55),
            ("Pulmonary embolism", 0.25),
            ("Anxiety / panic attack", 0.20),
        ],
        "advice": "Call emergency services immediately. Do not drive yourself.",
    },
    {
        "name": "Stroke red flags",
        "triage": "urgent",
        "keywords": [
            r"face droop", r"slurred speech", r"one[- ]sided weakness",
            r"sudden confusion", r"vision loss", r"severe headache",
        ],
        "conditions": [
            ("Stroke (FAST positive)", 0.65),
            ("Migraine", 0.20),
            ("Hypertensive emergency", 0.15),
        ],
        "advice": "Time-critical. Go to the nearest hospital; note symptom onset time.",
    },
    {
        "name": "Respiratory infection",
        "triage": "gp",
        "keywords": [
            r"fever", r"cough", r"sore throat", r"runny nose",
            r"shortness of breath (mild)", r"chills",
        ],
        "conditions": [
            ("Upper respiratory infection", 0.50),
            ("Influenza", 0.30),
            ("COVID-19", 0.20),
        ],
        "advice": "Rest, hydrate, monitor temperature. See a clinician if it worsens or lasts > 5 days.",
    },
    {
        "name": "Gastroenteritis",
        "triage": "gp",
        "keywords": [
            r"vomiting", r"diarrh(o)?ea", r"stomach cramp", r"nausea",
            r"dehydration",
        ],
        "conditions": [
            ("Viral gastroenteritis", 0.55),
            ("Food poisoning", 0.30),
            ("Appendicitis", 0.15),
        ],
        "advice": "Oral rehydration, bland diet. Seek care for severe pain, blood, or persistent dehydration.",
    },
    {
        "name": "Allergic reaction",
        "triage": "gp",
        "keywords": [
            r"rash", r"hives", r"itching", r"swelling", r"allerg",
        ],
        "conditions": [
            ("Allergic dermatitis", 0.55),
            ("Urticaria", 0.30),
            ("Anaphylaxis (assess airway)", 0.15),
        ],
        "advice": "Antihistamine may help. Emergency care for breathing trouble or facial swelling.",
    },
    {
        "name": "Musculoskeletal",
        "triage": "self_care",
        "keywords": [
            r"back pain", r"joint pain", r"muscle ache", r"stiffness",
            r"sprain",
        ],
        "conditions": [
            ("Mechanical back pain", 0.50),
            ("Strain / sprain", 0.35),
            ("Osteoarthritis flare", 0.15),
        ],
        "advice": "Rest, gentle movement, OTC analgesia. See a clinician if no improvement in 1-2 weeks.",
    },
]


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def check(symptoms: str) -> dict[str, Any]:
    """Run the rule-based checker and return a structured result."""
    if not symptoms or not symptoms.strip():
        return {
            "triage": "self_care",
            "conditions": [],
            "advice": "Please describe your symptoms so we can help.",
        }

    text = _normalise(symptoms)
    for rule in SYMPTOM_RULES:
        for kw in rule["keywords"]:
            if re.search(kw, text):
                return {
                    "triage": rule["triage"],
                    "conditions": [
                        {"name": name, "confidence": conf}
                        for name, conf in rule["conditions"]
                    ],
                    "advice": rule["advice"],
                    "matched_rule": rule["name"],
                }

    return {
        "triage": "gp",
        "conditions": [
            {"name": "Non-specific symptoms", "confidence": 1.0},
        ],
        "advice": "Symptoms don't match a known pattern. Schedule a visit with a clinician.",
        "matched_rule": None,
    }
