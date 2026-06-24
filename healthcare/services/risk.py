"""Follow-up risk scoring for a triage result.

Given the triage band produced by the rule-based checker and the symptom
text, compute a simple 0–100 risk score plus a human-readable level
(low / moderate / high). The score is intentionally explainable so the
demo can show *why* a patient was flagged.

Output shape::

    {
        "risk_score": int (0-100),
        "risk_level": "low" | "moderate" | "high",
        "risk_reasons": [str, ...],
    }
"""
from __future__ import annotations

import re
from typing import Any

# Base triage band weight.
TRIAGE_BASE = {
    "urgent": 70,
    "gp": 35,
    "self_care": 10,
}

# Keyword clusters that bump the risk score up.
HIGH_RISK_KEYWORDS = [
    (r"chest pain|radiating", 20, "Possible cardiac symptoms"),
    (r"shortness of breath", 15, "Breathing difficulty"),
    (r"unconscious|fainting", 25, "Loss of consciousness"),
    (r"face droop|slurred speech|one[- ]sided", 25, "Stroke red flags"),
    (r"blood", 15, "Blood in symptom description"),
    (r"severe", 10, "Severe symptom reported"),
    (r"\b\d{2,3}\b ?(f|°f|fever)?", 0, "Body temperature mentioned"),  # placeholder
]

LOW_RISK_KEYWORDS = [
    (r"\bmild\b", -5, "Mild severity self-reported"),
    (r"after lifting|overexertion", -5, "Mechanism suggests minor strain"),
]

# Length-based heuristic: short queries → user may be underreporting.
SHORT_QUERY_THRESHOLD = 20
SHORT_QUERY_PENALTY = 5


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def score(symptoms: str, triage: str) -> dict[str, Any]:
    """Return a risk score and reasons for the given symptom text + triage."""
    if not symptoms or not symptoms.strip():
        return {
            "risk_score": 0,
            "risk_level": "low",
            "risk_reasons": ["No symptoms described."],
        }

    base = TRIAGE_BASE.get(triage, 25)
    score_value = float(base)
    reasons: list[str] = [
        f"Base score for triage band '{triage}': {base}",
    ]

    text = _normalise(symptoms)

    for pattern, delta, label in HIGH_RISK_KEYWORDS:
        if re.search(pattern, text) and delta:
            score_value += delta
            reasons.append(f"+{delta} ({label})")

    for pattern, delta, label in LOW_RISK_KEYWORDS:
        if re.search(pattern, text) and delta:
            score_value += delta  # delta is already negative
            reasons.append(f"{delta} ({label})")

    if len(symptoms.strip()) < SHORT_QUERY_THRESHOLD:
        score_value += SHORT_QUERY_PENALTY
        reasons.append(f"+{SHORT_QUERY_PENALTY} (Brief description — may underreport)")

    score_value = max(0, min(100, int(round(score_value))))

    if score_value >= 70:
        level = "high"
    elif score_value >= 35:
        level = "moderate"
    else:
        level = "low"

    return {
        "risk_score": score_value,
        "risk_level": level,
        "risk_reasons": reasons,
    }
