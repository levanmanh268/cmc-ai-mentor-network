"""Small, pure UI helpers. Session state is ephemeral; do not persist user data."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

STUDENT_YEARS = ("Năm 1", "Năm 2", "Năm 3", "Năm 4")
PROFILE_LIMITS = {"name": 100, "field_interest": 180, "goals": 400, "bio": 1000}

RAG_MODE_LABELS = {
    "no-evidence": "Chưa tìm thấy bằng chứng phù hợp trong tài liệu.",
    "offline-grounded": "Chế độ offline: hiển thị các đoạn tài liệu đã truy xuất, không tự sinh kết luận.",
    "online-citations-unverified": "AI có trích dẫn nguồn truy xuất, nhưng các khẳng định chưa được xác minh ngữ nghĩa.",
    "offline-fallback": "Dịch vụ AI gặp lỗi hoặc trích dẫn không hợp lệ; đang hiển thị nguồn offline.",
}


def validate_profile(
    *, name: str, year: str, field_interest: str, goals: str, bio: str
) -> tuple[dict[str, str] | None, list[str]]:
    values = {
        "name": name.strip(),
        "year": year,
        "field_interest": field_interest.strip(),
        "goals": goals.strip(),
        "bio": bio.strip(),
    }
    errors: list[str] = []
    if values["year"] not in STUDENT_YEARS:
        errors.append("Năm học không hợp lệ.")
    if not values["field_interest"]:
        errors.append("Vui lòng nhập lĩnh vực quan tâm.")
    if not values["goals"]:
        errors.append("Vui lòng nhập mục tiêu học tập.")
    for key, max_len in PROFILE_LIMITS.items():
        if len(values[key]) > max_len:
            errors.append(f"Trường {key} vượt quá {max_len} ký tự.")
    return (None if errors else values), errors


def normalize_sources(sources: Iterable[Any] | None) -> list[dict[str, Any]]:
    """Normalize fresh RetrievedChunk and legacy Session State source dicts."""
    normalized: list[dict[str, Any]] = []
    for source in sources or []:
        if isinstance(source, Mapping):
            name = source.get("source") or source.get("name") or "Không rõ tài liệu"
            excerpt = source.get("excerpt") or source.get("text") or ""
            raw_score = source.get("score", 0.0)
        else:
            name = getattr(source, "source", "Không rõ tài liệu")
            excerpt = getattr(source, "text", "")
            raw_score = getattr(source, "score", 0.0)
        try:
            score = float(raw_score)
        except (TypeError, ValueError):
            score = 0.0
        if not (0 <= score <= 1):
            score = 0.0
        normalized.append(
            {
                "name": str(name)[:180],
                "score": score,
                "excerpt": str(excerpt)[:350],
            }
        )
    return normalized


def mode_label(mode: str | None) -> str:
    return RAG_MODE_LABELS.get(mode or "", "Trạng thái AI chưa xác định; hãy kiểm tra nguồn.")


def clear_matching(state: Any) -> None:
    state["top_matches"] = []
    state["match_explanations"] = {}
