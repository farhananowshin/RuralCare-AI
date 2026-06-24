"""Smart doctor-matcher: ranks verified doctors by specialty fit to the
symptom text.

Same contract as ``rule_based.check``: ``match(symptoms: str) -> dict``.
The ``analyze`` aggregator in ``services/__init__.py`` is responsible for
stitching this output into the final result dict the view consumes.

Output shape::

    {
        "recommended_doctors": [
            {"id": int, "name": str, "specialty": str,
             "score": float, "reason": str},
            ...
        ]
    }
"""
from __future__ import annotations

import re
from typing import Any

from accounts.models import Doctor


# Map of symptom-keyword clusters → list of matching specialties, ordered by
# preference. First match wins for the top recommendation; the rest appear in
# the recommendation list with descending scores.
SPECIALTY_HINTS: list[tuple[str, list[str]]] = [
    (r"chest pain|radiating to (?:arm|jaw)|palpitation|heart",
     ["Cardiologist", "General Physician"]),
    (r"stroke|face droop|slurred speech|one[- ]sided weakness",
     ["General Physician"]),
    (r"child|baby|infant|toddler|pediatric",
     ["Pediatrician", "General Physician"]),
    (r"pregnan|prenatal|antenatal",
     ["General Physician"]),
    (r"skin|rash|hives|itching|allerg",
     ["General Physician"]),
    (r"fever|cough|sore throat|runny nose|flu",
     ["General Physician"]),
    (r"vomit|diarrh|stomach|nausea",
     ["General Physician"]),
    (r"back pain|joint|muscle|sprain",
     ["General Physician"]),
]


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())


def _specialty_score(doctor_specialty: str, preferred: list[str]) -> float:
    """Return 0.0–1.0 fit score based on how well the doctor's specialty
    matches the user's preferred specialties (in order)."""
    if not doctor_specialty:
        return 0.0
    ds = doctor_specialty.lower()
    for idx, hint in enumerate(preferred):
        if hint.lower() in ds or ds in hint.lower():
            # Earlier hint → higher base score.
            return round(0.95 - idx * 0.15, 2)
    return 0.30  # generic fallback: doctor is still qualified, just not first pick


def match(symptoms: str) -> dict[str, Any]:
    """Return ranked doctor recommendations matching the symptom cluster."""
    if not symptoms or not symptoms.strip():
        return {"recommended_doctors": []}

    text = _normalise(symptoms)

    # Find the first matching cluster to drive preferred ordering.
    preferred: list[str] = ["General Physician"]
    matched_cluster: str | None = None
    for pattern, hints in SPECIALTY_HINTS:
        if re.search(pattern, text):
            preferred = hints
            matched_cluster = pattern
            break

    # Score every doctor, then take the top 3.
    scored: list[dict[str, Any]] = []
    for doctor in Doctor.objects.select_related("user").order_by("user__first_name"):
        score = _specialty_score(doctor.specialty, preferred)
        reason = (
            f"Specialty '{doctor.specialty}' matches the symptom pattern"
            if matched_cluster and doctor.specialty and any(
                h.lower() in doctor.specialty.lower() for h in preferred
            )
            else "Available local clinician"
        )
        scored.append({
            "id": doctor.pk,
            "name": doctor.user.get_full_name() or doctor.user.username,
            "specialty": doctor.specialty or "General",
            "score": score,
            "reason": reason,
        })

    scored.sort(key=lambda d: d["score"], reverse=True)
    top = scored[:3]
    return {
        "recommended_doctors": top,
        "matched_cluster": matched_cluster or "",
    }
