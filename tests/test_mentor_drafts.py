import pytest

from matching_engine import get_top_matches
from mentor_drafts import (
    MENTOR_DRAFTS_KEY,
    create_session_mentor,
    remove_session_mentor,
    validate_mentor_draft,
)
from mentors_data import get_mentor_repository


def valid_fields(**overrides):
    fields = {
        "name": "Mentor Phiên",
        "title": "AI Engineer",
        "company": "Demo Lab",
        "field": "Computer Vision & Deep Learning",
        "experience_years": 4,
        "bio": "Hỗ trợ sinh viên làm đồ án.",
        "strengths": "Python, Computer Vision",
        "available_for": ["Project"],
    }
    fields.update(overrides)
    return fields


def validation_options():
    mentors = get_mentor_repository().list()
    fields = sorted({mentor["field"] for mentor in mentors})
    supports = sorted({
        support for mentor in mentors for support in mentor["available_for"]
    })
    return fields, supports


def validate(fields):
    allowed_fields, allowed_supports = validation_options()
    return validate_mentor_draft(
        fields,
        allowed_fields=allowed_fields,
        allowed_supports=allowed_supports,
    )


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("name", "", "Vui lòng nhập tên mentor"),
        ("title", "x" * 121, "không được vượt quá 120"),
        ("experience_years", -1, "không được âm"),
        ("experience_years", 81, "không được vượt quá 80"),
        ("experience_years", "bốn", "phải là số nguyên"),
        ("field", "Unknown field", "lĩnh vực hợp lệ"),
        ("available_for", ["Unknown support"], "loại hỗ trợ hợp lệ"),
        ("strengths", [], "Cần nhập"),
        ("bio", "api_key=privatevalue123", "Không nhập API key"),
    ],
)
def test_validate_mentor_draft_rejects_invalid_values(field, value, message):
    with pytest.raises(ValueError, match=message):
        validate(valid_fields(**{field: value}))


def test_validate_mentor_draft_normalizes_strings_and_lists():
    mentor = validate(valid_fields(name="  Mentor A  ", strengths=" Python,\n CV "))

    assert mentor["name"] == "Mentor A"
    assert mentor["strengths"] == ["Python", "CV"]
    assert mentor["available_for"] == ["Project"]


def test_creation_and_removal_are_session_scoped_and_repository_is_unchanged():
    repository = get_mentor_repository()
    original = repository.list()
    allowed_fields, allowed_supports = validation_options()
    first_session = {}
    second_session = {}

    draft = create_session_mentor(
        first_session,
        valid_fields(),
        existing_mentors=original,
        allowed_fields=allowed_fields,
        allowed_supports=allowed_supports,
    )
    assert draft["id"] not in {mentor["id"] for mentor in original}
    assert [item["id"] for item in first_session[MENTOR_DRAFTS_KEY]] == [draft["id"]]
    assert second_session.get(MENTOR_DRAFTS_KEY, []) == []

    matches = get_top_matches(
        {
            "year": "Năm 2",
            "field_interest": "Computer Vision",
            "goals": "Computer Vision project",
        },
        top_k=10,
        field_filter=draft["field"],
        support_filter="Project",
        mentor_pool=[*original, *first_session[MENTOR_DRAFTS_KEY]],
    )
    assert draft["id"] in {item["mentor"]["id"] for item in matches}

    favorites = [draft]
    assert remove_session_mentor(first_session, draft["id"])
    favorites[:] = [item for item in favorites if item["id"] != draft["id"]]
    assert first_session[MENTOR_DRAFTS_KEY] == []
    assert favorites == []
    assert repository.list() == original


def test_generated_draft_ids_do_not_duplicate_existing_session_ids():
    original = get_mentor_repository().list()
    allowed_fields, allowed_supports = validation_options()
    session = {
        MENTOR_DRAFTS_KEY: [
            {
                "id": max(item["id"] for item in original) + 1,
                "name": "Earlier draft",
            }
        ]
    }

    created = create_session_mentor(
        session,
        valid_fields(),
        existing_mentors=original,
        allowed_fields=allowed_fields,
        allowed_supports=allowed_supports,
    )

    assert created["id"] == max(item["id"] for item in original) + 2
