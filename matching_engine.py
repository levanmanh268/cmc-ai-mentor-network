from __future__ import annotations

import os
import re
from typing import Any

from dotenv import load_dotenv
from groq import Groq
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from mentors_data import mentors

load_dotenv()
_api_key = os.getenv("GROQ_API_KEY", "").strip()
client = Groq(api_key=_api_key) if _api_key else None


def parse_student_year(value: Any) -> int:
    """Return a safe year in the range 1..4."""
    if isinstance(value, str):
        digits = "".join(ch for ch in value if ch.isdigit())
        parsed = int(digits) if digits else 1
    else:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            parsed = 1
    return max(1, min(parsed, 4))


def _normalize_text(value: Any) -> str:
    text = str(value or "").lower()
    text = re.sub(r"[^\wÀ-ỹ+#.\s-]", " ", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def _profile_text(student_profile: dict) -> str:
    return " ".join(
        [
            _normalize_text(student_profile.get("field_interest")),
            _normalize_text(student_profile.get("goals")),
            _normalize_text(student_profile.get("bio")),
        ]
    ).strip()


def _mentor_text(mentor: dict) -> str:
    return " ".join(
        [
            _normalize_text(mentor.get("field")),
            _normalize_text(mentor.get("title")),
            _normalize_text(mentor.get("bio")),
            _normalize_text(" ".join(mentor.get("strengths", []))),
            _normalize_text(" ".join(mentor.get("available_for", []))),
        ]
    )


def _keyword_set(text: str) -> set[str]:
    tokens = re.findall(r"[\wÀ-ỹ+#.]{2,}", _normalize_text(text), flags=re.UNICODE)
    stop = {
        "và", "của", "cho", "với", "làm", "em", "anh", "chị", "the", "and",
        "ai", "năm", "project", "student", "mentor",
    }
    return {token for token in tokens if token not in stop}


def _domain_overlap(student_profile: dict, mentor: dict) -> float:
    student_terms = _keyword_set(
        f"{student_profile.get('field_interest', '')} {student_profile.get('goals', '')}"
    )
    mentor_terms = _keyword_set(
        f"{mentor.get('field', '')} {' '.join(mentor.get('strengths', []))}"
    )
    if not student_terms or not mentor_terms:
        return 0.0
    overlap = student_terms & mentor_terms
    return min(len(overlap) / max(1, min(len(student_terms), 5)), 1.0)


def _experience_fit(student_profile: dict, mentor: dict) -> float:
    year = parse_student_year(student_profile.get("year", 1))
    try:
        experience = max(0, int(mentor.get("experience_years", 0) or 0))
    except (TypeError, ValueError):
        experience = 0

    if year <= 2:
        if experience >= 5:
            return 1.0
        if experience >= 3:
            return 0.8
        return 0.5

    if experience >= 3:
        return 0.8
    return 0.6


def calculate_hybrid_score(
    student_profile: dict,
    mentor: dict,
    semantic_score: float,
) -> float:
    semantic = max(0.0, min(float(semantic_score), 1.0))
    domain = _domain_overlap(student_profile, mentor)
    experience = _experience_fit(student_profile, mentor)

    score = semantic * 0.65 + domain * 0.25 + experience * 0.10
    return max(0.0, min(score, 1.0))


def _semantic_scores(student_profile: dict) -> list[float]:
    student_text = _profile_text(student_profile)
    mentor_texts = [_mentor_text(mentor) for mentor in mentors]

    if not student_text.strip():
        return [0.0] * len(mentors)

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        sublinear_tf=True,
    )
    matrix = vectorizer.fit_transform([student_text, *mentor_texts])
    scores = cosine_similarity(matrix[0:1], matrix[1:])[0]
    return [max(0.0, min(float(score), 1.0)) for score in scores]


def get_top_matches(student_profile: dict, top_k: int = 3) -> list[dict]:
    semantic_scores = _semantic_scores(student_profile)

    scored: list[dict] = []
    for mentor, semantic in zip(mentors, semantic_scores):
        hybrid = calculate_hybrid_score(student_profile, mentor, semantic)
        scored.append(
            {
                "mentor": mentor,
                "semantic_score": round(semantic * 100, 1),
                "hybrid_score": round(hybrid * 100, 1),
                "domain_overlap": round(_domain_overlap(student_profile, mentor) * 100, 1),
            }
        )

    scored.sort(
        key=lambda item: (
            -item["hybrid_score"],
            -item["semantic_score"],
            int(item["mentor"].get("id", 9999)),
        )
    )

    try:
        requested = int(top_k)
    except (TypeError, ValueError):
        requested = 3
    requested = max(1, min(requested, len(scored)))
    return scored[:requested]


def _fallback_explanation(student_profile: dict, mentor: dict, hybrid_score: float) -> str:
    student_terms = _keyword_set(
        f"{student_profile.get('field_interest', '')} {student_profile.get('goals', '')}"
    )
    mentor_terms = _keyword_set(
        f"{mentor.get('field', '')} {' '.join(mentor.get('strengths', []))}"
    )
    overlap = sorted(student_terms & mentor_terms)
    overlap_text = ", ".join(overlap[:4])

    if overlap_text:
        reason = f"Hai bên trùng các chủ đề: {overlap_text}."
    else:
        reason = (
            f"Mentor có chuyên môn {mentor.get('field', 'AI')} và "
            f"{mentor.get('experience_years', 0)} năm kinh nghiệm."
        )

    strengths = ", ".join(mentor.get("strengths", [])[:3]) or "AI"
    return (
        f"Match score {hybrid_score:.1f}%. {reason} "
        f"Điểm mạnh nổi bật của {mentor['name']} là {strengths}. "
        "Bạn nên dùng buổi trao đổi đầu tiên để kiểm tra mức phù hợp với mục tiêu hiện tại."
    )


def generate_match_explanation(
    student_profile: dict,
    mentor: dict,
    hybrid_score: float,
) -> str:
    if client is None:
        return _fallback_explanation(student_profile, mentor, hybrid_score)

    prompt = f"""Bạn là trợ lý giải thích kết quả mentor matching.

Chỉ dùng dữ liệu sau, không bịa thêm thành tích hoặc kinh nghiệm:
Sinh viên:
- Năm học: {student_profile.get('year')}
- Lĩnh vực: {student_profile.get('field_interest')}
- Mục tiêu: {student_profile.get('goals')}

Mentor:
- Tên: {mentor.get('name')}
- Vai trò: {mentor.get('title')}
- Công ty: {mentor.get('company')}
- Lĩnh vực: {mentor.get('field')}
- Kinh nghiệm: {mentor.get('experience_years')} năm
- Strengths: {', '.join(mentor.get('strengths', []))}
- Match score: {hybrid_score:.1f}%

Viết tối đa 4 câu tiếng Việt, cụ thể, không phóng đại.
"""

    try:
        completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            max_tokens=260,
        )
        text = completion.choices[0].message.content.strip()
        return text or _fallback_explanation(student_profile, mentor, hybrid_score)
    except Exception:
        return _fallback_explanation(student_profile, mentor, hybrid_score)
