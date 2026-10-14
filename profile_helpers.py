"""Validation helpers for the session-only student profile form."""

from __future__ import annotations

from collections.abc import Sequence

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
    name: str,
    year: object,
    field_interest: str,
    goals: str,
    bio: str,
    supported_years: Sequence[str],
) -> tuple[dict[str, str], dict[str, str]]:
    """Trim profile fields and return (cleaned_values, field_errors)."""
    cleaned = {
        "name": (name or "").strip(),
        "year": safe_student_year(year, supported_years),
        "field_interest": (field_interest or "").strip(),
        "goals": (goals or "").strip(),
        "bio": (bio or "").strip(),
    }
    errors: dict[str, str] = {}

    if not cleaned["field_interest"]:
        errors["field_interest"] = "Vui lòng nhập lĩnh vực quan tâm."
    elif len(cleaned["field_interest"]) > MAX_FIELD_INTEREST_LENGTH:
        errors["field_interest"] = (
            f"Lĩnh vực quan tâm không được vượt quá {MAX_FIELD_INTEREST_LENGTH} ký tự."
        )

    if not cleaned["goals"]:
        errors["goals"] = "Vui lòng nhập mục tiêu học tập hoặc nghề nghiệp."
    elif len(cleaned["goals"]) > MAX_GOALS_LENGTH:
        errors["goals"] = f"Mục tiêu không được vượt quá {MAX_GOALS_LENGTH} ký tự."

    if len(cleaned["name"]) > MAX_NAME_LENGTH:
        errors["name"] = f"Họ và tên không được vượt quá {MAX_NAME_LENGTH} ký tự."
    if len(cleaned["bio"]) > MAX_BIO_LENGTH:
        errors["bio"] = f"Giới thiệu không được vượt quá {MAX_BIO_LENGTH} ký tự."

    return cleaned, errors
