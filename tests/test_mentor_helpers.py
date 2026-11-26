import pytest

from mentor_helpers import add_mentor_draft, delete_mentor_draft, validate_mentor_draft
from mentors_data import get_mentor_repository


def values(**overrides):
    data = {
        "name": "Mentor Demo", "title": "AI Engineer", "company": "CMC",
        "field": "NLP & LLM", "experience_years": 2, "bio": "Hỗ trợ project demo.",
        "strengths": "Python, RAG", "available_for": ["Project"],
    }
    data.update(overrides)
    return data


@pytest.mark.parametrize("payload", [
    values(name="  "), values(name="x" * 101), values(experience_years=-1),
    values(experience_years="two"), values(field="Không có trong danh sách"),
    values(available_for=["Admin access"]), values(available_for=[]), values(strengths="  "),
])
def test_invalid_mentor_draft_is_rejected(payload):
    base = get_mentor_repository().list()
    with pytest.raises(ValueError):
        validate_mentor_draft(payload, existing_mentors=base, allowed_fields=[x["field"] for x in base])


def test_valid_mentor_draft_gets_unique_id_and_normalized_lists():
    base = get_mentor_repository().list()
    mentor = validate_mentor_draft(values(strengths=" Python, RAG ", available_for=["Project", "CV Review"]), existing_mentors=base, allowed_fields=[x["field"] for x in base])
    assert mentor["id"] == max(x["id"] for x in base) + 1
    assert mentor["strengths"] == ["Python", "RAG"]
    assert mentor["available_for"] == ["Project", "CV Review"]


def test_duplicate_name_is_rejected_and_base_repository_is_unchanged():
    base = get_mentor_repository().list()
    with pytest.raises(ValueError, match="đã tồn tại"):
        validate_mentor_draft(values(name=base[0]["name"]), existing_mentors=base, allowed_fields=[x["field"] for x in base])
    assert get_mentor_repository().list() == base


def test_drafts_can_be_added_and_removed_without_mutating_base_data():
    base = get_mentor_repository().list()
    state = {}
    draft = add_mentor_draft(state, values(), base_mentors=base, allowed_fields=[x["field"] for x in base])
    assert state["draft_mentors"] == [draft]
    assert get_mentor_repository().list() == base
    assert delete_mentor_draft(state, draft["id"])
    assert state["draft_mentors"] == []
    assert not delete_mentor_draft(state, draft["id"])
    assert get_mentor_repository().list() == base


def test_draft_ids_are_not_reused_after_deletion():
    base = get_mentor_repository().list()
    state = {}
    first = add_mentor_draft(state, values(), base_mentors=base)
    assert delete_mentor_draft(state, first["id"])
    second = add_mentor_draft(state, values(name="Second Demo Mentor"), base_mentors=base)
    assert second["id"] == first["id"] + 1
