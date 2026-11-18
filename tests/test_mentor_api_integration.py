"""Offline tests for ASP.NET mentor API integration into existing Streamlit app."""
from __future__ import annotations

import io
import json
from unittest.mock import patch

import pytest

from mentor_api import (
    MentorApiUnavailable,
    api_base_url,
    list_shared_mentor_suggestions,
    publish_mentor_suggestion,
)
from mentors_data import get_mentor_repository


class FakeResponse:
    def __init__(self, payload, status=200):
        self.status = status
        self.raw = io.BytesIO(json.dumps(payload).encode("utf-8"))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self, size=-1):
        return self.raw.read(size)


def example_api_mentor():
    return {
        "id": 9, "name": "Demo Shared", "title": "Research Engineer",
        "company": "Lab", "field": "NLP & LLM", "experienceYears": 3,
        "bio": "Mentor được thêm để thử nghiệm ứng dụng.",
        "strengths": ["RAG", "Python"], "availableFor": ["Project"],
        "verificationStatus": "unverified",
    }


def example_local_draft():
    return {
        "id": 1001, "name": "Draft Shared", "title": "Engineer",
        "company": "Demo Lab", "field": "NLP & LLM",
        "experience_years": 2,
        "bio": "Nội dung minh họa cho kiểm thử.",
        "strengths": ["Python"], "available_for": ["Project"],
    }


def test_remote_api_unconfigured_keeps_original_mentors(monkeypatch):
    monkeypatch.delenv("MENTOR_API_URL", raising=False)
    originals = get_mentor_repository().list()
    assert api_base_url() is None
    with pytest.raises(MentorApiUnavailable):
        list_shared_mentor_suggestions()
    assert get_mentor_repository().list() == originals


@pytest.mark.parametrize("invalid", [
    "http://example.com", "https://user:secret@example.com",
    "https://example.com/extra", "https://example.com?key=secret",
    "javascript:bad", "https://",
])
def test_untrusted_backend_endpoints_are_disabled(monkeypatch, invalid):
    monkeypatch.setenv("MENTOR_API_URL", invalid)
    assert api_base_url() is None


def test_unverified_shared_mentor_maps_to_negative_id(monkeypatch):
    monkeypatch.setenv("MENTOR_API_URL", "https://mentor-api.example.test")
    monkeypatch.setattr("mentor_api.urlopen",
                        lambda req, timeout: FakeResponse([example_api_mentor()]))
    original_ids = {x["id"] for x in get_mentor_repository().list()}
    public = list_shared_mentor_suggestions()
    assert public[0]["id"] == -9
    assert public[0]["available_for"] == ["Project"]
    assert public[0]["verification_status"] == "unverified"
    assert public[0]["id"] not in original_ids


def test_api_rejects_mislabelled_verified_mentor(monkeypatch):
    monkeypatch.setenv("MENTOR_API_URL", "https://mentor-api.example.test")
    invalid = example_api_mentor()
    invalid["verificationStatus"] = "verified"
    monkeypatch.setattr("mentor_api.urlopen", lambda req, timeout: FakeResponse([invalid]))
    with pytest.raises(MentorApiUnavailable):
        list_shared_mentor_suggestions()


def test_publish_sends_only_mentor_schema_as_json(monkeypatch):
    monkeypatch.setenv("MENTOR_API_URL", "https://mentor-api.example.test")
    seen = {}
    def fake(req, timeout):
        seen["url"] = req.full_url
        seen["method"] = req.get_method()
        seen["payload"] = json.loads(req.data.decode("utf-8"))
        return FakeResponse(example_api_mentor(), status=201)
    monkeypatch.setattr("mentor_api.urlopen", fake)
    publish_mentor_suggestion(example_local_draft())
    assert seen["method"] == "POST"
    assert seen["url"] == "https://mentor-api.example.test/api/mentor-suggestions"
    assert seen["payload"]["experienceYears"] == 2
    assert "id" not in seen["payload"]
    assert "email" not in seen["payload"]


def test_api_outage_fails_closed_without_fake_persistence(monkeypatch):
    monkeypatch.setenv("MENTOR_API_URL", "https://mentor-api.example.test")
    from urllib.error import URLError
    def failed(req, timeout):
        raise URLError("unavailable")
    monkeypatch.setattr("mentor_api.urlopen", failed)
    with pytest.raises(MentorApiUnavailable):
        publish_mentor_suggestion(example_local_draft())


def test_invalid_backend_json_is_not_silently_accepted(monkeypatch):
    monkeypatch.setenv("MENTOR_API_URL", "https://mentor-api.example.test")
    monkeypatch.setattr("mentor_api.urlopen", lambda req, timeout: FakeResponse({"not": "list"}))
    with pytest.raises(MentorApiUnavailable):
        list_shared_mentor_suggestions()
