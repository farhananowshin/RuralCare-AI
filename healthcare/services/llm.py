"""LLM-backed symptom checker stub.

This module is intentionally minimal: it documents the swap-in point and
returns a deterministic placeholder. Replace ``check`` with a real call to
your LLM provider (OpenAI, Anthropic, Azure, local model) and shape the
response into the same dict contract as the rule-based backend.

To activate, set in ``settings.py``::

    RURALCARE_SYMPTOM_CHECKER_BACKEND = 'healthcare.services.llm.check'

and provide the relevant API key in the environment.
"""
from __future__ import annotations

import os
from typing import Any


def check(symptoms: str) -> dict[str, Any]:
    """Placeholder LLM checker. Returns a stub result; integrate your client here."""
    if not symptoms or not symptoms.strip():
        return {
            "triage": "self_care",
            "conditions": [],
            "advice": "Please describe your symptoms so we can help.",
            "matched_rule": None,
        }

    # NOTE: a real implementation would call e.g.:
    #   client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    #   response = client.responses.create(model="gpt-4o-mini", input=...)
    # and map the JSON response into the contract below.
    api_key_present = bool(os.environ.get("OPENAI_API_KEY"))

    return {
        "triage": "gp",
        "conditions": [
            {"name": "LLM assessment (stub)", "confidence": 0.0},
        ],
        "advice": (
            "Stub LLM backend. "
            + ("API key detected; integrate a real call. " if api_key_present else "No API key set; ")
            + "See healthcare/services/llm.py."
        ),
        "matched_rule": "LLM stub",
    }
