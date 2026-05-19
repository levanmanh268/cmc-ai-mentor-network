# matching_engine.py
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from mentors_data import mentors
from groq import Groq

client = Groq(api_key="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")

# ==================== LAZY LOADING ====================
_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        print("Đang tải embedding model cho Matching (chỉ load khi cần)...")
        _embedding_model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
        print("✅ Embedding model đã sẵn sàng!")
    return _embedding_model


def get_student_embedding(student_profile: dict):
    model = get_embedding_model()
    text = f"{student_profile.get('field_interest', '')} {student_profile.get('goals', '')} {student_profile.get('bio', '')}"
    return model.encode(text)


def calculate_hybrid_score(student_profile: dict, mentor: dict, semantic_score: float):
    score = semantic_score * 0.7
    bonus = 0

    year_raw = student_profile.get("year", 1)
    if isinstance(year_raw, str):
        student_year = int(''.join(filter(str.isdigit, year_raw)))
    else:
        student_year = int(year_raw)

    mentor_exp = mentor.get("experience_years", 0)

    if student_profile.get("field_interest") and mentor.get("field"):
        if student_profile["field_interest"].lower() in mentor["field"].lower():
            bonus += 0.15

    if mentor_exp >= 3 and student_year <= 2:
        bonus += 0.10

    return min(score + bonus, 1.0)


def get_top_matches(student_profile: dict, top_k: int = 3):
    model = get_embedding_model()
    student_vec = get_student_embedding(student_profile)

    mentor_texts = [
        f"{m['name']} {m['title']} {m['bio']} {' '.join(m['strengths'])}"
        for m in mentors
    ]
    mentor_vecs = model.encode(mentor_texts)

    similarities = cosine_similarity([student_vec], mentor_vecs)[0]

    scored_mentors = []
    for i, mentor in enumerate(mentors):
        hybrid_score = calculate_hybrid_score(student_profile, mentor, similarities[i])
        scored_mentors.append({
            "mentor": mentor,
            "semantic_score": round(similarities[i] * 100, 1),
            "hybrid_score": round(hybrid_score * 100, 1)
        })

    scored_mentors.sort(key=lambda x: x["hybrid_score"], reverse=True)
    return scored_mentors[:top_k]


def generate_match_explanation(student_profile: dict, mentor: dict, hybrid_score: float):
    prompt = f"""Bạn là chuyên gia tư vấn mentor cho sinh viên CMCU ngành AI.

Hãy viết một đoạn giải thích **ngắn gọn (3-4 câu)**, tự nhiên và chuyên nghiệp bằng tiếng Việt.

**Thông tin sinh viên:**
- Năm học: {student_profile.get('year')}
- Lĩnh vực quan tâm: {student_profile.get('field_interest')}
- Mục tiêu: {student_profile.get('goals')}

**Thông tin Mentor:**
- Tên: {mentor['name']} - {mentor['title']} tại {mentor['company']}
- Kinh nghiệm: {mentor['experience_years']} năm
- Điểm mạnh: {', '.join(mentor['strengths'])}

**Yêu cầu:**
- Giải thích rõ tại sao mentor này phù hợp với sinh viên.
- Nhấn mạnh sự trùng khớp về lĩnh vực, kỹ năng hoặc mục tiêu.
- Giọng điệu tích cực và khích lệ.
- Độ dài tối đa 4 câu."""

    response = client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama-3.3-70b-versatile",
        temperature=0.6,
        max_tokens=280
    )
    return response.choices[0].message.content.strip()