"""Symptom checker service layer.

Active backend is selected via ``settings.RURALCARE_SYMPTOM_CHECKER_BACKEND``
which must be an importable path to a class implementing
``check(symptoms: str) -> dict`` and returning:

    {
        "triage": "self_care" | "gp" | "urgent",
        "conditions": [{"name": str, "confidence": float}, ...],
        "advice": str,
    }
"""
from __future__ import annotations

import importlib
from functools import lru_cache
from typing import Any, Callable

from django.conf import settings


def _load_backend() -> Callable[[str], dict[str, Any]]:
    """Import the configured backend module and return its ``check`` callable."""
    dotted = settings.RURALCARE_SYMPTOM_CHECKER_BACKEND
    module_path, _, attr = dotted.rpartition('.')
    if not module_path:
        raise ImproperlyConfigured(
            f"RURALCARE_SYMPTOM_CHECKER_BACKEND={dotted!r} is not a dotted path"
        )
    module = importlib.import_module(module_path)
    try:
        return getattr(module, attr)
    except AttributeError as exc:  # pragma: no cover - misconfig guard
        raise ImproperlyConfigured(
            f"{dotted!r} does not expose a callable named {attr!r}"
        ) from exc


@lru_cache(maxsize=1)
def get_symptom_checker() -> Callable[[str], dict[str, Any]]:
    """Return the cached ``check`` callable for the active backend."""
    return _load_backend()


def check_symptoms(symptoms: str) -> dict[str, Any]:
    """Convenience wrapper that calls the active backend."""
    return get_symptom_checker()(symptoms)


# Re-export so callers can ``from healthcare.services import ImproperlyConfigured``.
from django.core.exceptions import ImproperlyConfigured  # noqa: E402

# New AI feature modules. All implement ``check`` / ``score`` / ``explain`` /
# ``match`` and return small dicts that ``analyze`` merges together.
from . import doctor_matcher, educator, risk  # noqa: E402


def analyze(symptoms: str) -> dict[str, Any]:
    """Run the full AI pipeline and return a single merged result dict.

    The returned dict is the source of truth for the symptom-check view
    and the home page demo. Keys:

        triage, conditions, advice, matched_rule   (from rule_based)
        risk_score, risk_level, risk_reasons        (from risk)
        explanation, next_steps, warning_signs      (from educator)
        recommended_doctors, matched_cluster         (from doctor_matcher)
    """
    triage_result = check_symptoms(symptoms)
    risk_result = risk.score(symptoms, triage_result.get("triage", "self_care"))
    explanation = educator.explain(
        triage_result.get("triage", "self_care"),
        risk_result.get("risk_level", "low"),
    )
    matches = doctor_matcher.match(symptoms)

    merged = dict(triage_result)
    merged.update(risk_result)
    merged.update(explanation)
    merged.update(matches)
    return merged
