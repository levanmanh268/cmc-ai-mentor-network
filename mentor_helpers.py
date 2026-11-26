"""Validation and session-only operations for user-created mentor drafts."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from mentors_data import validate_mentor

MAX_LENGTHS = {"name": 100, "title": 100, "company": 120, "field": 80, "bio": 600}
ALLOWED_SUPPORT_TYPES = ("Project", "Thực tập", "CV Review", "Nghiên cứu")


def validate_mentor_draft(values: Mapping[str, Any], *, existing_mentors=None, allowed_fields=None, mentor_id=None):
    if not isinstance(values, Mapping):
        raise TypeError("Dữ liệu mentor phải là một object")
    cleaned = {}
    for field, limit in MAX_LENGTHS.items():
        value = values.get(field)
        if not isinstance(value, str):
            raise ValueError(f"{field} phải là văn bản")
        value = value.strip()
        if not value:
            raise ValueError(f"{field} không được để trống")
        if len(value) > limit:
            raise ValueError(f"{field} tối đa {limit} ký tự")
        cleaned[field] = value
    if allowed_fields is not None and cleaned["field"].casefold() not in {x.strip().casefold() for x in allowed_fields}:
        raise ValueError("Lĩnh vực không nằm trong danh sách hỗ trợ")
    experience = values.get("experience_years")
    if isinstance(experience, bool) or not isinstance(experience, int) or experience < 0:
        raise ValueError("Số năm kinh nghiệm phải là số nguyên không âm")
    cleaned["experience_years"] = experience
    strengths = values.get("strengths")
    if not isinstance(strengths, str):
        raise ValueError("Kỹ năng phải là văn bản, phân cách bằng dấu phẩy")
    strengths = [x.strip() for x in strengths.split(",") if x.strip()]
    if not strengths or any(len(x) > 80 for x in strengths):
        raise ValueError("Nhập ít nhất một kỹ năng; mỗi kỹ năng tối đa 80 ký tự")
    cleaned["strengths"] = strengths
    support = values.get("available_for")
    if not isinstance(support, (list, tuple)) or not support:
        raise ValueError("Chọn ít nhất một loại hỗ trợ")
    if any(item not in ALLOWED_SUPPORT_TYPES for item in support):
        raise ValueError("Loại hỗ trợ không hợp lệ")
    cleaned["available_for"] = list(dict.fromkeys(support))
    existing = list(existing_mentors or [])
    ids = set()
    names = {str(item.get("name", "")).strip().casefold() for item in existing}
    for item in existing:
        try:
            ids.add(int(item["id"]))
        except (KeyError, TypeError, ValueError):
            continue
    if cleaned["name"].casefold() in names:
        raise ValueError("Tên mentor đã tồn tại trong danh sách của phiên này")
    candidate = max(ids, default=0) + 1 if mentor_id is None else mentor_id
    if isinstance(candidate, bool) or not isinstance(candidate, int) or candidate <= 0:
        raise ValueError("ID mentor không hợp lệ")
    if candidate in ids:
        raise ValueError("ID mentor đã tồn tại trong phiên này")
    cleaned["id"] = candidate
    return validate_mentor(cleaned)


def add_mentor_draft(session_state: Any, values, *, base_mentors, allowed_fields=None):
    drafts = list(session_state.get("draft_mentors", []))
    occupied = [*base_mentors, *drafts]
    try:
        next_id = int(session_state.get("next_mentor_draft_id", 0))
    except (TypeError, ValueError):
        next_id = 0
    mentor_id = max(next_id, max((int(item["id"]) for item in occupied), default=0) + 1)
    mentor = validate_mentor_draft(values, existing_mentors=occupied, allowed_fields=allowed_fields, mentor_id=mentor_id)
    drafts.append(mentor)
    session_state["draft_mentors"] = drafts
    session_state["next_mentor_draft_id"] = mentor_id + 1
    return dict(mentor)


def delete_mentor_draft(session_state: Any, mentor_id: int) -> bool:
    drafts = list(session_state.get("draft_mentors", []))
    remaining = [item for item in drafts if int(item["id"]) != int(mentor_id)]
    if len(remaining) == len(drafts):
        return False
    session_state["draft_mentors"] = remaining
    return True
