from profile_helpers import (
    reset_profile_state,
    safe_student_year,
    save_profile_state,
    validate_profile_fields,
)


YEARS = ["Năm 1", "Năm 2", "Năm 3", "Năm 4"]


def test_required_profile_fields_reject_empty_and_whitespace():
    cleaned, errors = validate_profile_fields(
        "  Hà  ", "Năm 2", "   ", " \t ", "", YEARS
    )

    assert cleaned["name"] == "Hà"
    assert errors["field_interest"] == "Vui lòng nhập lĩnh vực quan tâm."
    assert errors["goals"] == "Vui lòng nhập mục tiêu học tập hoặc nghề nghiệp."


def test_valid_profile_is_trimmed_and_optional_fields_may_be_empty():
    cleaned, errors = validate_profile_fields(
        "", "Năm 3", " NLP, LLM ", " Build a RAG app ", " ", YEARS
    )

    assert errors == {}
    assert cleaned == {
        "name": "",
        "year": "Năm 3",
        "field_interest": "NLP, LLM",
        "goals": "Build a RAG app",
        "bio": "",
    }


def test_field_length_limits_are_enforced():
    _, errors = validate_profile_fields(
        "n" * 101,
        "Năm 1",
        "f" * 121,
        "g" * 241,
        "b" * 501,
        YEARS,
    )

    assert "name" in errors
    assert "field_interest" in errors
    assert "goals" in errors
    assert "bio" in errors


def test_unknown_legacy_year_falls_back_without_crashing():
    assert safe_student_year("unknown", YEARS) == "Năm 1"
    assert safe_student_year(None, YEARS) == "Năm 1"
    assert safe_student_year("Năm 4", YEARS) == "Năm 4"


def test_unknown_year_is_normalized_during_validation():
    cleaned, errors = validate_profile_fields(
        "", "legacy-year", "AI", "Practice", "", YEARS
    )

    assert cleaned["year"] == "Năm 1"
    assert errors == {}



def test_saving_updated_profile_invalidates_matching_but_keeps_favorites_and_chat():
    state = {
        "user_profile": {"field_interest": "Old"},
        "top_matches": [{"id": "stale-match"}],
        "match_explanations": {"stale-match": "Old explanation"},
        "favorite_mentors": [{"id": "favorite-1"}],
        "messages": [{"role": "user", "content": "Keep chat"}],
    }
    updated = {
        "name": "Student",
        "year": "Năm 2",
        "field_interest": "NLP",
        "goals": "Build a project",
        "bio": "",
    }

    save_profile_state(state, updated)

    assert state["user_profile"] == updated
    assert state["top_matches"] == []
    assert state["match_explanations"] == {}
    assert state["favorite_mentors"] == [{"id": "favorite-1"}]
    assert state["messages"] == [{"role": "user", "content": "Keep chat"}]


def test_reset_profile_clears_profile_and_matching_but_preserves_favorites_and_chat():
    state = {
        "user_profile": {"field_interest": "Old"},
        "top_matches": [{"id": "stale-match"}],
        "match_explanations": {"stale-match": "Old explanation"},
        "favorite_mentors": [{"id": "favorite-1"}],
        "messages": [{"role": "user", "content": "Keep chat"}],
    }

    reset_profile_state(state)

    assert state["user_profile"] == {}
    assert state["top_matches"] == []
    assert state["match_explanations"] == {}
    assert state["favorite_mentors"] == [{"id": "favorite-1"}]
    assert state["messages"] == [{"role": "user", "content": "Keep chat"}]
