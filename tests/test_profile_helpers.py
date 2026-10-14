from profile_helpers import safe_student_year, validate_profile_fields


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
