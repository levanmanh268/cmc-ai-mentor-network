"""Streamlit UI regression tests without external LLM calls."""
import os

from streamlit.testing.v1 import AppTest


def make_app(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    app = AppTest.from_file("app.py", default_timeout=45).run()
    assert not app.exception
    return app


def test_offline_dashboard_and_chat_navigation(monkeypatch):
    app = make_app(monkeypatch)
    app.sidebar.radio[0].set_value("💬 AI Assistant").run()
    assert not app.exception
    assert any("Grounded AI Assistant" in item.value for item in app.title)


def test_mentor_search_results_remain_after_saving(monkeypatch):
    app = make_app(monkeypatch)
    app.sidebar.radio[0].set_value("👥 Tìm Mentor").run()
    assert not app.exception

    app.button[0].click().run()
    assert not app.exception
    assert len(app.session_state["top_matches"]) == 3
    assert len(app.button) >= 4

    # Search button is at index 0, the next three buttons save matches.
    app.button[1].click().run()
    assert not app.exception
    assert len(app.session_state["top_matches"]) == 3
    assert len(app.session_state["favorite_mentors"]) == 1

    # A second render must retain the results and favorites.
    app.run()
    assert not app.exception
    assert len(app.session_state["top_matches"]) == 3
    assert len(app.session_state["favorite_mentors"]) == 1
