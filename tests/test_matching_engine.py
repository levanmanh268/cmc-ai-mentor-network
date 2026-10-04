from matching_engine import (
    calculate_hybrid_score,
    get_top_matches,
    parse_student_year,
)


def test_parse_student_year_is_safe():
    assert parse_student_year("Năm 1") == 1
    assert parse_student_year("year 4") == 4
    assert parse_student_year("unknown") == 1
    assert parse_student_year(9) == 4
    assert parse_student_year(None) == 1


def test_hybrid_score_is_bounded():
    mentor = {
        "field": "NLP & LLM",
        "strengths": ["RAG", "LLM"],
        "experience_years": 5,
    }
    profile = {
        "year": "Năm 1",
        "field_interest": "RAG, LLM",
        "goals": "Làm chatbot RAG",
    }

    assert 0.0 <= calculate_hybrid_score(profile, mentor, -4.0) <= 1.0
    assert 0.0 <= calculate_hybrid_score(profile, mentor, 7.0) <= 1.0


def test_rag_profile_prefers_rag_llm_mentor():
    profile = {
        "year": "Năm 1",
        "field_interest": "RAG, LLM, NLP",
        "goals": "Xây dựng chatbot dùng retrieval",
        "bio": "Em học Python và muốn làm AI application.",
    }

    results = get_top_matches(profile, top_k=3)

    assert len(results) == 3
    assert results[0]["mentor"]["name"] in {"Anh Tuấn", "Anh Khoa"}
    assert results[0]["hybrid_score"] >= results[1]["hybrid_score"]


def test_empty_profile_still_returns_stable_results():
    results = get_top_matches({}, top_k=100)

    assert len(results) == 5
    assert all(0.0 <= item["hybrid_score"] <= 100.0 for item in results)
