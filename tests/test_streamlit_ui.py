"""Streamlit UI regression tests without external LLM calls."""
from pathlib import Path

from streamlit.testing.v1 import AppTest


def make_app(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "app.py", default_timeout=45).run()
    assert not app.exception
    return app


def test_offline_dashboard_and_chat_navigation(monkeypatch):
    app = make_app(monkeypatch)
    app.sidebar.radio[0].set_value("💬 AI Assistant").run()
    assert not app.exception
    assert any("CMC AI Assistant" in item.value for item in app.title)
    assert app.selectbox[0].value == "🤖 Trò chuyện AI"


def test_mentor_search_results_remain_after_saving(monkeypatch):
    app = make_app(monkeypatch)
    app.sidebar.radio[0].set_value("👥 Tìm Mentor").run()
    assert not app.exception

    app.button(key="search_mentors").click().run()
    assert not app.exception
    assert len(app.session_state["top_matches"]) == 3
    assert len(app.button) >= 4

    app.button(key="save_1").click().run()
    assert not app.exception
    assert len(app.session_state["top_matches"]) == 3
    assert len(app.session_state["favorite_mentors"]) == 1

    # A second render must retain the results and favorites.
    app.run()
    assert not app.exception
    assert len(app.session_state["top_matches"]) == 3
    assert len(app.session_state["favorite_mentors"]) == 1


def test_mentor_draft_create_then_match_favorite_and_confirmed_delete(monkeypatch):
    app = make_app(monkeypatch)
    app.sidebar.radio[0].set_value("👥 Tìm Mentor").run()
    app.text_input(key="mentor_draft_name").set_value("Session Demo Mentor")
    app.text_input(key="mentor_draft_title").set_value("AI Engineer")
    app.text_input(key="mentor_draft_company").set_value("Demo Lab")
    app.text_input(key="mentor_draft_field").set_value("Recommendation System")
    app.text_area(key="mentor_draft_bio").set_value("Demo mentor for RAG projects.")
    app.text_input(key="mentor_draft_strengths").set_value("RAG, Python")
    app.multiselect(key="mentor_draft_support").set_value(["Project"])
    app.button(key="FormSubmitter:create_mentor_draft-Tạo Mentor trong phiên").click().run()
    assert not app.exception
    draft = app.session_state["draft_mentors"][0]
    app.selectbox(key="mentor_field_filter").set_value("Recommendation System")
    app.button(key="search_mentors").click().run()
    assert any(item["mentor"]["id"] == draft["id"] for item in app.session_state["top_matches"])
    app.button(key=f"save_{draft['id']}").click().run()
    assert any(item["id"] == draft["id"] for item in app.session_state["favorite_mentors"])
    app.button(key=f"delete_draft_{draft['id']}").click().run()
    app.checkbox(key="confirm_delete_draft").set_value(True).run()
    next(button for button in app.button if button.label == "Xóa bản nháp đã chọn").click().run()
    assert not app.exception
    assert app.session_state["draft_mentors"] == []
    assert app.session_state["favorite_mentors"] == []
