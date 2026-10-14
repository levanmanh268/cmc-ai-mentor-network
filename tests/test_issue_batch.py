"""Regression checks for the issue-batch integration; no external API calls."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from matching_engine import get_top_matches
from rag_engine import validate_citation_ids
from ui_helpers import (
    clear_matching, mode_label, normalize_sources, validate_profile,
)


@pytest.fixture
def profile():
    return {
        "name": "",
        "year": "Năm 1",
        "field_interest": "RAG, LLM",
        "goals": "Học AI",
        "bio": "",
    }


def test_profile_validation_rejects_whitespace_and_preserves_contract(profile):
    valid, errors = validate_profile(**profile)
    assert not errors
    assert valid == profile
    invalid = dict(profile, goals=" \n ")
    assert validate_profile(**invalid)[0] is None
    assert validate_profile(**dict(profile, field_interest=" "))[0] is None
    assert validate_profile(**dict(profile, year="Năm 9"))[0] is None
    assert validate_profile(**dict(profile, bio="X" * 1001))[0] is None


def test_clear_matching_does_not_delete_favorites_or_profile(profile):
    state = {
        "user_profile": profile,
        "favorite_mentors": [{"id": 1}],
        "top_matches": [{"mentor": {"id": 1}}],
        "match_explanations": {1: "test"},
        "messages": [{"role": "user", "content": "hi"}],
    }
    clear_matching(state)
    assert state["top_matches"] == []
    assert state["match_explanations"] == {}
    assert state["user_profile"] == profile
    assert state["favorite_mentors"] == [{"id": 1}]
    assert len(state["messages"]) == 1


def test_sources_accept_old_history_missing_fields_and_new_chunks():
    sources = normalize_sources([{"name": "old.md", "score": 0.4}, {"source": "new.md", "text": "RAG", "score": "0.5"}])
    assert sources[0]["excerpt"] == ""
    assert sources[1] == {"name": "new.md", "score": 0.5, "excerpt": "RAG"}
    assert normalize_sources([{"name": "bad", "score": "invalid"}])[0]["score"] == 0.0


def test_rag_modes_are_explicit_and_not_misleading():
    assert "chưa được xác minh" in mode_label("online-citations-unverified")
    assert "offline" in mode_label("offline-fallback")
    assert "bằng chứng" in mode_label("no-evidence")
    assert mode_label("unknown")


def test_citation_membership_is_fail_closed():
    assert validate_citation_ids("Đúng theo [S1] và [S2]", 2)
    assert not validate_citation_ids("Không có nguồn", 2)
    assert not validate_citation_ids("bịa [S3]", 2)
    assert not validate_citation_ids("tham khảo [S0]", 2)
    assert not validate_citation_ids("Một nguồn [S1]", 0)


def test_matching_filters_compose_and_rank_only_filtered_results(profile):
    all_items = get_top_matches(profile, top_k=100)
    assert len(all_items) >= 3
    selected = all_items[0]["mentor"]
    field = selected["field"]
    support = selected["available_for"][0]
    subset = get_top_matches(
        profile, top_k=100, field_filter=field, support_filter=support
    )
    assert subset
    assert all(x["mentor"]["field"] == field for x in subset)
    assert all(support in x["mentor"]["available_for"] for x in subset)
    assert subset == get_top_matches(
        profile, top_k=100, field_filter=field, support_filter=support
    )
    assert get_top_matches(profile, field_filter="__not_a_real_domain__") == []
    assert get_top_matches(profile, support_filter="__none__") == []
    assert get_top_matches(profile, top_k=100) == all_items


def test_streamlit_profile_and_chat_controls_survive_rerun(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py", default_timeout=45
    ).run()
    assert not app.exception

    app.sidebar.radio[0].set_value("👤 Hồ sơ cá nhân").run()
    assert not app.exception
    assert any("phiên Streamlit" in x.value for x in app.info)
    assert len(app.button) >= 2

    app.sidebar.radio[0].set_value("💬 AI Assistant").run()
    assert not app.exception
    app.session_state["messages"] = [
        {"role": "assistant", "content": "Tham khảo", "sources": [{"name": "old.md", "score": 0.4}]}
    ]
    app.run()
    assert not app.exception
    assert any("old.md" in str(x.value) for x in app.markdown)
    app.button[0].click().run()
    assert not app.exception
    assert app.session_state["messages"] == []

    app.sidebar.radio[0].set_value("👥 Tìm Mentor").run()
    assert not app.exception
    assert len(app.selectbox) >= 2
