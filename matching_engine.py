import os

from dotenv import load_dotenv
from groq import Groq
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

from mentors_data import mentors

load_dotenv()
_api_key = os.getenv("GROQ_API_KEY", "").strip()
client = Groq(api_key=_api_key) if _api_key else None

_embedding_model = None


def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
    return _embedding_model


def get_student_embedding(student_profile: dict):
    model = get_embedding_model()
    text = (
        f"{student_profile.get('field_interest', '')} "
        f"{student_profile.get('goals', '')} "
        f"{student_profile.get('bio', '')}"
    )
    return model.encode(text)


def _parse_year(value) -> int:
    if isinstance(value, str):
        digits = "".join(filter(str.isdigit, value))
        return int(digits) if digits else 1
    try:
        return int(value)
    except (TypeError, ValueError):
        return 1


def calculate_hybrid_score(student_profile: dict, mentor: dict, semantic_score: float):
    score = max(0.0, min(float(semantic_score), 1.0)) * 0.7
    bonus = 0.0

    student_year = _parse_year(student_profile.get("year", 1))
    mentor_exp = int(mentor.get("experience_years", 0) or 0)

    interests = str(student_profile.get("field_interest", "")).lower()
    mentor_field = str(mentor.get("field", "")).lower()
    if interests and mentor_field and any(
        token.strip() and token.strip() in mentor_field
        for token in interests.replace("&", ",").split(",")
    ):
        bonus += 0.15

    if mentor_exp >= 3 and student_year <= 2:
        bonus += 0.10

    return min(score + bonus, 1.0)


def get_top_matches(student_profile: dict, top_k: int = 3):
    model = get_embedding_model()
    student_vec = get_student_embedding(student_profile)

    mentor_texts = [
        f"{m['name']} {m['title']} {m['field']} {m['bio']} {' '.join(m['strengths'])}"
        for m in mentors
    ]
    mentor_vecs = model.encode(mentor_texts)
    similarities = cosine_similarity([student_vec], mentor_vecs)[0]

    scored_mentors = []
    for index, mentor in enumerate(mentors):
        hybrid_score = calculate_hybrid_score(student_profile, mentor, similarities[index])
        scored_mentors.append(
            {
                "mentor": mentor,
                "semantic_score": round(float(similarities[index]) * 100, 1),
                "hybrid_score": round(hybrid_score * 100, 1),
            }
        )

    scored_mentors.sort(key=lambda item: item["hybrid_score"], reverse=True)
    return scored_mentors[: max(1, min(int(top_k), len(scored_mentors)))]


def _fallback_explanation(student_profile: dict, mentor: dict) -> str:
    interests = student_profile.get("field_interest") or "AI"
    strengths = ", ".join(mentor.get("strengths", [])[:3])
    return (
        f"{mentor['name']} phù hợp vì kinh nghiệm của mentor tập trung vào {mentor.get('field', 'AI')}, "
        f"gần với mối quan tâm {interests} của bạn. "
        f"Các thế mạnh nổi bật gồm {strengths}. "
        "Bạn có thể bắt đầu bằng một buổi trao đổi ngắn về mục tiêu project hoặc thực tập."
    )


def generate_match_explanation(student_profile: dict, mentor: dict, hybrid_score: float):
    if client is None:
        return _fallback_explanation(student_profile, mentor)

    prompt = f"""Bạn là chuyên gia tư vấn mentor cho sinh viên CMCU ngành AI.
Viết 3-4 câu tiếng Việt, ngắn gọn và cụ thể.

Sinh viên:
- Năm học: {student_profile.get('year')}
- Lĩnh vực: {student_profile.get('field_interest')}
- Mục tiêu: {student_profile.get('goals')}

Mentor:
- {mentor['name']} - {mentor['title']} tại {mentor['company']}
- Kinh nghiệm: {mentor['experience_years']} năm
- Điểm mạnh: {', '.join(mentor['strengths'])}
- Match score: {hybrid_score:.1f}%

Không bịa thành tích ngoài dữ liệu trên.
"""

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=280,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return _fallback_explanation(student_profile, mentor)
