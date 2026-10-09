from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

REQUIRED_FIELDS = (
    "id",
    "name",
    "title",
    "company",
    "field",
    "experience_years",
    "bio",
    "strengths",
    "available_for",
)

RAW_MENTORS = [
    {
        "id": 1,
        "name": "Anh Tuấn",
        "title": "Senior AI Engineer",
        "company": "VNG Corporation",
        "field": "NLP & LLM",
        "experience_years": 5,
        "bio": "Có kinh nghiệm xây dựng hệ thống RAG và chatbot cho sản phẩm thực tế. Đam mê hỗ trợ sinh viên làm project AI.",
        "strengths": ["RAG", "LLM Application", "Prompt Engineering", "Production AI"],
        "available_for": ["Project", "Thực tập", "CV Review"],
    },
    {
        "id": 2,
        "name": "Chị Lan",
        "title": "ML Researcher",
        "company": "VinAI",
        "field": "Computer Vision & Deep Learning",
        "experience_years": 4,
        "bio": "Nghiên cứu về mô hình thị giác máy tính và đã có paper. Thích hướng dẫn sinh viên làm project CV.",
        "strengths": ["Computer Vision", "Deep Learning", "Research Methodology"],
        "available_for": ["Project", "Nghiên cứu"],
    },
    {
        "id": 3,
        "name": "Anh Minh",
        "title": "AI Engineer",
        "company": "Tiki",
        "field": "Recommendation System",
        "experience_years": 3,
        "bio": "Xây dựng hệ thống gợi ý cho hàng triệu người dùng. Có kinh nghiệm thực tế về production ML.",
        "strengths": ["Recommendation Systems", "MLOps", "Python", "Data Pipeline"],
        "available_for": ["Project", "Thực tập"],
    },
    {
        "id": 4,
        "name": "Chị Hương",
        "title": "Data Scientist",
        "company": "Shopee",
        "field": "NLP & Analytics",
        "experience_years": 4,
        "bio": "Làm về phân tích dữ liệu văn bản và chatbot. Rất nhiệt tình hỗ trợ sinh viên mới.",
        "strengths": ["NLP", "Data Analysis", "Chatbot", "Python"],
        "available_for": ["Project", "CV Review", "Thực tập"],
    },
    {
        "id": 5,
        "name": "Anh Khoa",
        "title": "AI Researcher",
        "company": "FPT AI Center",
        "field": "Multimodal & LLM",
        "experience_years": 6,
        "bio": "Nghiên cứu multimodal model và LLM fine-tuning. Có nhiều kinh nghiệm hướng dẫn project cho sinh viên.",
        "strengths": ["LLM", "Multimodal", "Research", "Fine-tuning"],
        "available_for": ["Project", "Nghiên cứu"],
    },
]


def _normalize_string_list(value: Any, field_name: str) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        items = [item.strip() for item in value.split(",") if item.strip()]
        return items
    if isinstance(value, Iterable) and not isinstance(value, (str, bytes, bytearray)):
        cleaned = []
        for item in value:
            if item is None:
                continue
            text = str(item).strip()
            if text:
                cleaned.append(text)
        return cleaned
    raise TypeError(f"{field_name} must be a string or list-like value")


def validate_mentor(mentor: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(mentor, Mapping):
        raise TypeError("Mentor data must be a mapping/dictionary")

    missing = [field for field in REQUIRED_FIELDS if field not in mentor]
    if missing:
        raise ValueError(f"Mentor data is missing required fields: {', '.join(missing)}")

    normalized = dict(mentor)

    for field_name in ("name", "title", "company", "field", "bio"):
        value = normalized.get(field_name)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} must be a non-empty string")
        normalized[field_name] = value.strip()

    try:
        normalized["id"] = int(normalized["id"])
    except (TypeError, ValueError) as exc:
        raise ValueError("id must be an integer") from exc

    try:
        normalized["experience_years"] = int(normalized["experience_years"])
    except (TypeError, ValueError) as exc:
        raise ValueError("experience_years must be an integer") from exc

    normalized["strengths"] = _normalize_string_list(normalized["strengths"], "strengths")
    normalized["available_for"] = _normalize_string_list(normalized["available_for"], "available_for")

    return normalized


class MentorRepository:
    def __init__(self, mentors_data: Iterable[Mapping[str, Any]]):
        self._mentors = [validate_mentor(mentor) for mentor in mentors_data]

    def list(self) -> list[dict[str, Any]]:
        return [dict(mentor) for mentor in self._mentors]

    def get_by_id(self, mentor_id: int) -> dict[str, Any] | None:
        for mentor in self._mentors:
            if int(mentor["id"]) == int(mentor_id):
                return dict(mentor)
        return None


def get_mentor_repository() -> MentorRepository:
    return _default_repository


def get_mentors() -> list[dict[str, Any]]:
    return _default_repository.list()


_default_repository = MentorRepository(RAW_MENTORS)
mentors = get_mentors()