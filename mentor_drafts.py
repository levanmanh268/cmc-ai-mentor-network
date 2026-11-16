from __future__ import annotations

import re
from collections.abc import Mapping, MutableMapping, Sequence
from typing import Any

from mentors_data import validate_mentor


MENTOR_DRAFTS_KEY = "session_mentor_drafts"
MAX_LENGTHS = {
    "name": 100,
    "title": 120,
    "company": 120,
    "field": 120,
    "bio": 500,
}
MAX_STRENGTH_LENGTH = 60
MAX_STRENGTHS = 10
MAX_STRENGTH_INPUT = MAX_STRENGTHS * (MAX_STRENGTH_LENGTH + 1)
MAX_SUPPORTS = 8
MAX_SUPPORT_INPUT = MAX_SUPPORTS * (MAX_STRENGTH_LENGTH + 1)
MAX_EXPERIENCE_YEARS = 80
_FIELD_LABELS = {
    "name": "tên mentor",
    "title": "chức danh",
    "company": "công ty / tổ chức",
    "field": "lĩnh vực",
    "bio": "phần giới thiệu",
}
_SECRET_PATTERNS = (
    re.compile(r"\b(?:gsk_[A-Za-z0-9]{20,}|sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16})\b"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\b(?:api[_ -]?key|secret|access[_ -]?token|password)\s*[:=]\s*\S+", re.IGNORECASE),
)


def _contains_secret(value: str) -> bool:
    return any(pattern.search(value) for pattern in _SECRET_PATTERNS)


def _parse_list(value: Any, field_name: str) -> list[str]:
    if isinstance(value, str):
        items = value.replace("\n", ",").split(",")
    elif isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        items = value
    else:
        raise ValueError(f"{field_name} không hợp lệ.")

    result = []
    for item in items:
        if not isinstance(item, str):
            raise ValueError(f"{field_name} không hợp lệ.")
        cleaned = item.strip()
        if cleaned:
            result.append(cleaned)
    return result


def validate_mentor_draft(
    fields: Mapping[str, Any],
    *,
    allowed_fields: Sequence[str],
    allowed_supports: Sequence[str],
) -> dict[str, Any]:
    """Validate form data and return a normalized, not-yet-persisted mentor."""
    if not isinstance(fields, Mapping):
        raise ValueError("Thông tin mentor không hợp lệ.")

    normalized: dict[str, Any] = {}
    for field_name, max_length in MAX_LENGTHS.items():
        value = fields.get(field_name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"Vui lòng nhập {_FIELD_LABELS[field_name]}.")
        value = value.strip()
        if len(value) > max_length:
            raise ValueError(f"{field_name} không được vượt quá {max_length} ký tự.")
        if _contains_secret(value):
            raise ValueError("Không nhập API key, secret hoặc private key vào hồ sơ mentor.")
        normalized[field_name] = value

    experience = fields.get("experience_years")
    if isinstance(experience, bool) or not isinstance(experience, int):
        raise ValueError("Số năm kinh nghiệm phải là số nguyên.")
    if experience < 0:
        raise ValueError("Số năm kinh nghiệm không được âm.")
    if experience > MAX_EXPERIENCE_YEARS:
        raise ValueError(
            f"Số năm kinh nghiệm không được vượt quá {MAX_EXPERIENCE_YEARS}."
        )

    strengths = _parse_list(fields.get("strengths"), "Kỹ năng")
    if not strengths or len(strengths) > MAX_STRENGTHS:
        raise ValueError(f"Cần nhập từ 1 đến {MAX_STRENGTHS} kỹ năng.")
    if any(len(item) > MAX_STRENGTH_LENGTH for item in strengths):
        raise ValueError(f"Mỗi kỹ năng không được vượt quá {MAX_STRENGTH_LENGTH} ký tự.")
    if any(_contains_secret(item) for item in strengths):
        raise ValueError("Không nhập API key hoặc secret vào hồ sơ mentor.")

    supports = _parse_list(fields.get("available_for"), "Loại hỗ trợ")
    allowed_support_set = {item.casefold() for item in allowed_supports}
    if not supports or len(supports) > MAX_SUPPORTS or any(
        item.casefold() not in allowed_support_set for item in supports
    ):
        raise ValueError("Vui lòng chọn loại hỗ trợ hợp lệ.")
    allowed_field_set = {item.casefold() for item in allowed_fields}
    if normalized["field"].casefold() not in allowed_field_set:
        raise ValueError("Vui lòng chọn lĩnh vực hợp lệ.")

    normalized["experience_years"] = experience
    normalized["strengths"] = strengths
    normalized["available_for"] = supports
    return normalized


def create_session_mentor(
    session_state: MutableMapping[str, Any],
    fields: Mapping[str, Any],
    *,
    existing_mentors: Sequence[Mapping[str, Any]],
    allowed_fields: Sequence[str],
    allowed_supports: Sequence[str],
) -> dict[str, Any]:
    """Add a validated mentor only to the caller's session state."""
    draft = validate_mentor_draft(
        fields,
        allowed_fields=allowed_fields,
        allowed_supports=allowed_supports,
    )
    drafts = list(session_state.get(MENTOR_DRAFTS_KEY, []))
    used_ids = {
        int(mentor["id"])
        for mentor in [*existing_mentors, *drafts]
        if isinstance(mentor, Mapping) and "id" in mentor
    }
    mentor_id = max(used_ids, default=0) + 1
    while mentor_id in used_ids:
        mentor_id += 1
    draft["id"] = mentor_id
    draft = validate_mentor(draft)
    drafts.append(draft)
    session_state[MENTOR_DRAFTS_KEY] = drafts
    return dict(draft)


def remove_session_mentor(
    session_state: MutableMapping[str, Any],
    mentor_id: int,
) -> bool:
    """Remove a draft by ID from this session without touching shared data."""
    drafts = list(session_state.get(MENTOR_DRAFTS_KEY, []))
    remaining = [mentor for mentor in drafts if int(mentor["id"]) != int(mentor_id)]
    if len(remaining) == len(drafts):
        return False
    session_state[MENTOR_DRAFTS_KEY] = remaining
    return True
