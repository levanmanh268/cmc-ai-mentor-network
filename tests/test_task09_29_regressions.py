"""Traceable regression coverage for TASK-09 through TASK-29."""

from pathlib import Path
from types import SimpleNamespace

import pytest
from streamlit.testing.v1 import AppTest

from matching_engine import calculate_hybrid_score, get_top_matches
from profile_helpers import validate_profile_fields
from mentors_data import validate_mentor


APP = Path(__file__).resolve().parents[1] / "app.py"
YEARS = ["Năm 1", "Năm 2", "Năm 3", "Năm 4"]


def _open_profile_page(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    app = AppTest.from_file(APP, default_timeout=45).run()
    assert not app.exception
    app.sidebar.radio[0].set_value("👤 Hồ sơ cá nhân").run()
    assert not app.exception
    return app


def test_task09_profile_can_be_created_and_updated_in_ui(monkeypatch):
    app = _open_profile_page(monkeypatch)
    app.text_input[0].set_value("Linh")
    app.text_input[1].set_value("AI")
    app.text_input[2].set_value("Build a mentor app")
    app.button[0].click().run()
    assert not app.exception
    assert app.session_state["user_profile"]["name"] == "Linh"

    app.session_state["top_matches"] = [{"id": "stale"}]
    app.session_state["match_explanations"] = {"stale": "old"}
    app.run()
    app.text_input[0].set_value("Linh Nguyen")
    app.text_input[1].set_value("RAG, LLM")
    app.text_input[2].set_value("Build grounded AI")
    app.button[0].click().run()
    assert not app.exception
    assert app.session_state["user_profile"]["name"] == "Linh Nguyen"
    assert app.session_state["user_profile"]["field_interest"] == "RAG, LLM"
    assert app.session_state["top_matches"] == []
    assert app.session_state["match_explanations"] == {}


@pytest.mark.parametrize("field,values", [
    ("field_interest", ("Linh", "Năm 2", "", "Mục tiêu", "")),
    ("goals", ("Linh", "Năm 2", "AI", "   ", "")),
])
def test_task10_each_required_profile_field_rejects_empty(field, values):
    cleaned, errors = validate_profile_fields(*values, YEARS)
    assert field in errors
    assert cleaned[field] == ""


def test_task11_invalid_profile_types_and_lengths_are_rejected_without_exception():
    _, errors = validate_profile_fields(
        123, "Năm 2", ["AI"], "Mục tiêu", {"bio": "not text"}, YEARS
    )
    assert {"name", "field_interest", "bio"} <= errors.keys()

    _, length_errors = validate_profile_fields(
        "x" * 101, "Năm 2", "AI", "Mục tiêu", "x" * 501, YEARS
    )
    assert {"name", "bio"} <= length_errors.keys()


def test_task12_normalizes_profile_text_and_invalid_year():
    values, errors = validate_profile_fields(
        "  Linh  ", "year-unknown", "  AI, RAG  ", "  Build app  ", "  Student  ", YEARS
    )
    assert errors == {}
    assert values == {
        "name": "Linh", "year": "Năm 1", "field_interest": "AI, RAG",
        "goals": "Build app", "bio": "Student",
    }


def test_task13_invalid_profile_update_keeps_existing_valid_profile(monkeypatch):
    app = _open_profile_page(monkeypatch)
    previous = {
        "name": "Existing", "year": "Năm 2", "field_interest": "AI",
        "goals": "Finish project", "bio": "Keep me",
    }
    app.session_state["user_profile"] = previous.copy()
    app.run()
    app.text_input[1].set_value("   ")
    app.button[0].click().run()
    assert app.session_state["user_profile"] == previous
    assert app.error


def test_task14_profile_reset_requires_explicit_confirmation(monkeypatch):
    app = _open_profile_page(monkeypatch)
    app.session_state["user_profile"] = {"name": "Existing", "field_interest": "AI"}
    app.session_state["top_matches"] = [{"id": 1}]
    app.session_state["match_explanations"] = {1: "cached"}
    app.run()
    next(b for b in app.button if "Đặt lại / xóa hồ sơ" in b.label).click().run()
    assert not app.exception
    confirm_button = next(b for b in app.button if "Xóa hồ sơ và kết quả matching" in b.label)
    assert confirm_button.disabled


def test_task15_profile_reset_preserves_favorites_and_both_chat_histories():
    from profile_helpers import reset_profile_state

    state = {
        "user_profile": {"field_interest": "AI"},
        "top_matches": [{"id": 2}], "match_explanations": {2: "cached"},
        "favorite_mentors": [{"id": 1}],
        "messages": [{"role": "user", "content": "RAG"}],
        "general_messages": [{"role": "user", "content": "hello"}],
    }
    reset_profile_state(state)
    assert state["user_profile"] == {}
    assert state["top_matches"] == [] and state["match_explanations"] == {}
    assert state["favorite_mentors"] == [{"id": 1}]
    assert state["messages"] and state["general_messages"]


class _RecordingGroq:
    calls = []
    failure = None
    response = "Fake response"

    def __init__(self, api_key, **kwargs):
        self.chat = SimpleNamespace(completions=self)

    def create(self, **kwargs):
        self.__class__.calls.append(kwargs)
        if self.__class__.failure:
            raise self.__class__.failure
        return SimpleNamespace(choices=[
            SimpleNamespace(message=SimpleNamespace(content=self.__class__.response))
        ])


def _open_online_chat(monkeypatch):
    _RecordingGroq.calls = []
    _RecordingGroq.failure = None
    _RecordingGroq.response = "Fake response"
    monkeypatch.setenv("GROQ_API_KEY", "fake-key-for-tests")
    monkeypatch.setattr("llm_client.Groq", _RecordingGroq)
    app = AppTest.from_file(APP, default_timeout=45).run()
    app.sidebar.radio[0].set_value("💬 AI Assistant").run()
    app.sidebar.checkbox[0].set_value(True).run()
    assert not app.exception and not app.chat_input[0].disabled
    return app


def _open_chat_with_history(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    app = AppTest.from_file(APP, default_timeout=45).run()
    app.sidebar.radio[0].set_value("💬 AI Assistant").run()
    app.session_state["general_messages"] = [
        {"role": "user", "content": "Old question"},
        {"role": "assistant", "content": "Old answer", "status": "online"},
    ]
    app.session_state["confirm_clear_general"] = True
    app.run()
    assert not app.exception
    assert len(app.session_state["general_messages"]) == 2
    return app


def test_task20_clear_ai_assistant_conversation(monkeypatch):
    from ui_helpers import clear_general_chat_history

    app = _open_chat_with_history(monkeypatch)
    state = {"general_messages": app.session_state["general_messages"]}
    clear_general_chat_history(state)
    assert state["general_messages"] == []


def test_task21_clear_ai_chat_preserves_profile_favorites_and_rag_history(monkeypatch):
    from ui_helpers import clear_general_chat_history

    app = _open_chat_with_history(monkeypatch)
    profile = {"name": "Linh", "field_interest": "AI"}
    rag_history = [{"role": "user", "content": "RAG question"}]
    favorites = [{"id": 1, "name": "Mentor"}]
    app.session_state["user_profile"] = profile.copy()
    app.session_state["messages"] = rag_history.copy()
    app.session_state["favorite_mentors"] = favorites.copy()
    clear_general_chat_history(app.session_state)
    assert app.session_state["general_messages"] == []
    assert app.session_state["user_profile"] == profile
    assert app.session_state["messages"] == rag_history
    assert app.session_state["favorite_mentors"] == favorites


@pytest.mark.parametrize("failure,response", [
    (TimeoutError("private timeout details"), "Fake response"),
    (None, "   "),
])
def test_task23_ai_ui_shows_error_for_timeout_or_empty_response(monkeypatch, failure, response):
    app = _open_online_chat(monkeypatch)
    _RecordingGroq.failure = failure
    _RecordingGroq.response = response
    app.chat_input[0].set_value("Answer this question").run()
    assert not app.exception
    assert app.error
    assert app.session_state["general_messages"][-1]["status"] == "error"
    assert "private timeout details" not in str(app.error)


def test_task24_hybrid_match_score_has_expected_component_weights():
    profile = {"year": "Năm 1", "field_interest": "RAG", "goals": "RAG"}
    mentor = {"field": "RAG", "strengths": ["RAG"], "experience_years": 5}
    assert calculate_hybrid_score(profile, mentor, 0.5) == pytest.approx(0.675)


def test_task25_matching_results_are_sorted_highest_score_first():
    profile = {"year": "Năm 2", "field_interest": "RAG LLM", "goals": "Mentor AI"}
    results = get_top_matches(profile, top_k=99)
    assert results
    scores = [row["hybrid_score"] for row in results]
    assert scores == sorted(scores, reverse=True)


def test_task26_field_filter_returns_only_requested_specialty():
    profile = {"year": "Năm 2", "field_interest": "AI", "goals": "Project"}
    all_fields = get_top_matches(profile, top_k=100)
    specialty = all_fields[0]["mentor"]["field"]
    filtered = get_top_matches(profile, top_k=100, field_filter=specialty)
    assert filtered
    assert all(row["mentor"]["field"] == specialty for row in filtered)
    assert len(filtered) < len(all_fields)


def test_task27_no_matching_mentor_shows_explicit_empty_state(monkeypatch):
    app = AppTest.from_file(APP, default_timeout=45).run()
    app.sidebar.radio[0].set_value("👥 Tìm Mentor").run()
    monkeypatch.setattr("matching_engine.get_mentor_repository", lambda: SimpleNamespace(list=lambda: []))
    next(b for b in app.button if "Tìm Mentor" in b.label).click().run()
    assert not app.exception
    assert app.session_state["top_matches"] == []
    assert any("Không tìm thấy mentor phù hợp" in item.value for item in app.info)


def test_task28_empty_and_invalid_mentor_data_are_handled_explicitly(monkeypatch):
    monkeypatch.setattr("matching_engine.get_mentor_repository", lambda: SimpleNamespace(list=lambda: []))
    assert get_top_matches({"field_interest": "AI"}) == []
    with pytest.raises(ValueError, match="missing required fields"):
        validate_mentor({"id": 1, "name": "Incomplete"})


def test_task29_equal_scores_have_stable_id_tiebreak_and_top_k_boundaries(monkeypatch):
    from matching_engine import get_top_matches

    base = {
        "name": "Mentor", "title": "Engineer", "company": "Demo", "field": "AI",
        "experience_years": 4, "bio": "AI mentor", "strengths": ["AI"],
        "available_for": ["Project"],
    }
    pool = [dict(base, id=2), dict(base, id=1)]
    monkeypatch.setattr("matching_engine.get_mentor_repository", lambda: SimpleNamespace(list=lambda: pool))
    profile = {"year": "Năm 2", "field_interest": "AI", "goals": "AI project"}
    results = get_top_matches(profile, top_k=10)
    assert [row["mentor"]["id"] for row in results] == [1, 2]
    assert len(get_top_matches(profile, top_k=1)) == 1
    assert len(get_top_matches(profile, top_k=0)) == 1
    assert len(get_top_matches(profile, top_k=-2)) == 1
