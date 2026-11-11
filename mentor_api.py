"""Optional ASP.NET Core mentor API client for the ORIGINAL Streamlit frontend.

The curated mentors_data.py list is never replaced or mutated. Shared unverified
suggestions are isolated from per-session drafts and need a working database.
No real-world identity or verified-mentor claims are made.
"""
from __future__ import annotations

import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from mentors_data import validate_mentor

TIMEOUT_SECONDS = 5


class MentorApiUnavailable(RuntimeError):
    """Remote persistence is not ready, disabled or failed safely."""


def api_base_url() -> str | None:
    raw = os.environ.get("MENTOR_API_URL", "").strip().rstrip("/")
    if not raw:
        return None
    parts = urlparse(raw)
    if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
        return None
    if parts.path not in ("", "/") or parts.query or parts.fragment:
        return None
    return raw


def _call(method: str, path: str, payload=None):
    base = api_base_url()
    if not base:
        raise MentorApiUnavailable("Chưa cấu hình backend lưu dữ liệu.")
    headers = {"Accept": "application/json"}
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(base + path, data=data, method=method, headers=headers)
    try:
        with urlopen(req, timeout=TIMEOUT_SECONDS) as response:
            if response.status not in (200, 201):
                raise MentorApiUnavailable("Backend chưa sẵn sàng.")
            result = json.load(response)
    except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
        raise MentorApiUnavailable("Không kết nối được database mentor lúc này.") from exc
    return result


def list_shared_mentor_suggestions() -> list[dict]:
    raw = _call("GET", "/api/mentor-suggestions")
    if not isinstance(raw, list):
        raise MentorApiUnavailable("API trả về dữ liệu sai định dạng.")
    mentors = []
    for row in raw:
        if not isinstance(row, dict) or row.get("verificationStatus") != "unverified":
            raise MentorApiUnavailable("API trả về dữ liệu chưa thể xác thực.")
        try:
            backend_id = row["id"]
            if isinstance(backend_id, bool) or not isinstance(backend_id, int) or backend_id <= 0:
                raise ValueError("invalid id")
            mentor = validate_mentor({
                "id": -backend_id,  # negatives reserved for shared unverified suggestions
                "name": row["name"],
                "title": row["title"],
                "company": row["company"],
                "field": row["field"],
                "experience_years": row["experienceYears"],
                "bio": row["bio"],
                "strengths": row["strengths"],
                "available_for": row["availableFor"],
            })
            mentor["verification_status"] = "unverified"
            mentors.append(mentor)
        except (KeyError, TypeError, ValueError) as exc:
            raise MentorApiUnavailable("API trả về mentor sai định dạng.") from exc
    return mentors


def publish_mentor_suggestion(draft: dict) -> dict:
    """Publish explicit user-approved demo suggestion to a real PostgreSQL backend."""
    checked = validate_mentor(draft)
    data = {
        "name": checked["name"],
        "title": checked["title"],
        "company": checked["company"],
        "field": checked["field"],
        "experienceYears": checked["experience_years"],
        "bio": checked["bio"],
        "strengths": checked["strengths"],
        "availableFor": checked["available_for"],
    }
    raw = _call("POST", "/api/mentor-suggestions", data)
    if not isinstance(raw, dict) or not isinstance(raw.get("id"), int):
        raise MentorApiUnavailable("API chưa xác nhận đã lưu mentor.")
    return raw
