"""Validation and session-state helpers for the student profile form."""

from __future__ import annotations

from collections.abc import MutableMapping, Sequence
from typing import Any

MAX_NAME_LENGTH = 100
MAX_FIELD_INTEREST_LENGTH = 120
MAX_GOALS_LENGTH = 240
MAX_BIO_LENGTH = 500


def safe_student_year(value: object, supported_years: Sequence[str]) -> str:
    """Return a supported year even if an old session contains an unknown value."""
    if value in supported_years:
        return str(value)
    return supported_years[0] if supported_years else ""


def validate_profile_fields(
    name: object,
    year: object,
    field_interest: object,
    goals: object,
    bio: object,
    supported_years: Sequence[str],
) -> tuple[dict[str, str], dict[str, str]]:
    """Trim profile fields and return (cleaned_values, field_errors)."""
    raw_text = {
        "name": name,
        "field_interest": field_interest,
        "goals": goals,
        "bio": bio,
    }
    cleaned = {
        key: value.strip() if isinstance(value, str) else ""
        for key, value in raw_text.items()
    }
    cleaned["year"] = safe_student_year(year, supported_years)
    errors: dict[str, str] = {}

    for key, value in raw_text.items():
        if value is not None and not isinstance(value, str):
            errors[key] = f"Giá trị {key} không hợp lệ. Hãy nhập văn bản."

    if not cleaned["field_interest"] and "field_interest" not in errors:
        errors["field_interest"] = "Vui lòng nhập lĩnh vực quan tâm."
    elif len(cleaned["field_interest"]) > MAX_FIELD_INTEREST_LENGTH:
        errors["field_interest"] = (
            f"Lĩnh vực quan tâm không được vượt quá {MAX_FIELD_INTEREST_LENGTH} ký tự."
        )

    if not cleaned["goals"] and "goals" not in errors:
        errors["goals"] = "Vui lòng nhập mục tiêu học tập hoặc nghề nghiệp."
    elif len(cleaned["goals"]) > MAX_GOALS_LENGTH:
        errors["goals"] = f"Mục tiêu không được vượt quá {MAX_GOALS_LENGTH} ký tự."

    if len(cleaned["name"]) > MAX_NAME_LENGTH:
        errors["name"] = f"Họ và tên không được vượt quá {MAX_NAME_LENGTH} ký tự."
    if len(cleaned["bio"]) > MAX_BIO_LENGTH:
        errors["bio"] = f"Giới thiệu không được vượt quá {MAX_BIO_LENGTH} ký tự."

    return cleaned, errors


def save_profile_state(
    session_state: MutableMapping[str, Any], profile: dict[str, str]
) -> None:
    """Save a validated profile and invalidate derived matching results."""
    session_state["user_profile"] = dict(profile)
    session_state["top_matches"] = []
    session_state["match_explanations"] = {}


def reset_profile_state(session_state: MutableMapping[str, Any]) -> None:
    """Delete the session profile and stale matching data, preserving favorites/chat."""
    session_state["user_profile"] = {}
    session_state["top_matches"] = []
    session_state["match_explanations"] = {}
