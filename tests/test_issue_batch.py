"""Cross-module integration on the team branches, offline, without external keys."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from matching_engine import get_top_matches
from rag_engine import validate_citation_ids
from profile_helpers import validate_profile_fields, save_profile_state, reset_profile_state
from ui_helpers import (
    clear_chat_history, normalize_saved_source, rag_mode_label, source_history_payload,
)


def test_profile_validation_and_reset_preserve_favorites():
    cleaned, errors = validate_profile_fields(
        "   ", "Năm 1", "  ", "  ", "", ["Năm 1", "Năm 2"]
    )
    assert "field_interest" in errors and "goals" in errors
    state = {
        "user_profile": {"name": "abc"},
        "favorite_mentors": [{"id": 1}],
        "messages": [{"role": "user", "content": "question"}],
        "top_matches": [1],
        "match_explanations": {1: "cached"},
    }
    reset_profile_state(state)
    assert state["user_profile"] == {}
    assert state["top_matches"] == [] and state["match_explanations"] == {}
    assert state["favorite_mentors"] == [{"id": 1}]
    assert len(state["messages"]) == 1


def test_legacy_source_history_and_mode_remain_honest():
    assert normalize_saved_source({"name": "a.md", "score": 0.5})["excerpt"] == ""
    assert source_history_payload({"name": "b.md", "score": 0.4, "text": "Evidence"})["excerpt"] == "Evidence"
    assert "chưa được xác minh" in rag_mode_label("online-citations-unverified")
    state = {"messages": [1], "user_profile": {"goals": "project"}}
    clear_chat_history(state)
    assert state["messages"] == []
    assert state["user_profile"]["goals"] == "project"


def test_rag_citation_membership():
    assert validate_citation_ids("tham khảo [S1] và [S2]", 2)
    assert not validate_citation_ids("không nguồn", 2)
    assert not validate_citation_ids("bịa [S99]", 2)
    assert not validate_citation_ids("sai [S0]", 2)
    assert not validate_citation_ids("tham khảo [S1]", 0)


def test_filtering_before_ranking_with_empty_path():
    profile = {"year": "Năm 1", "field_interest": "RAG", "goals": "Học AI"}
    original = get_top_matches(profile, top_k=100)
    mentor = original[0]["mentor"]
    domain, support = mentor["field"], mentor["available_for"][0]
    filtered = get_top_matches(profile, top_k=100, field_filter=domain, support_filter=support)
    assert filtered
    assert all(m["mentor"]["field"] == domain and support in m["mentor"]["available_for"] for m in filtered)
    assert get_top_matches(profile, field_filter="__unknown__") == []
    assert get_top_matches(profile, support_filter="__unknown__") == []
    assert get_top_matches(profile, top_k=100) == original


def test_streamlit_navigation_and_filters(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=45
    ).run()
    assert not app.exception
    app.sidebar.radio[0].set_value("👤 Hồ sơ cá nhân").run()
    assert not app.exception
    assert any("phiên Streamlit" in x.value for x in app.info)
    app.sidebar.radio[0].set_value("💬 AI Assistant").run()
    assert not app.exception
    app.session_state["messages"] = [{
        "role": "assistant", "content": "Tham khảo",
        "sources": [{"name": "legacy.md", "score": 0.3}],
    }]
    app.run()
    assert not app.exception
    assert any("legacy.md" in str(x.value) for x in app.markdown)
    app.sidebar.radio[0].set_value("👥 Tìm Mentor").run()
    assert not app.exception
    assert len(app.selectbox) >= 2
