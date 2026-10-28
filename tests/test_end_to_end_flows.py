"""AppTest integration flows across Streamlit navigation and fake Groq boundary.

These exercises run the real app.py code in-process. They are NOT Selenium,
Playwright, hosted-browser UAT, or a real external provider test.
"""
from pathlib import Path
from types import SimpleNamespace

import pytest
from streamlit.testing.v1 import AppTest


APP = Path(__file__).resolve().parents[1] / "app.py"


class FakeGroq:
    calls = []

    def __init__(self, api_key, **kwargs):
        self.chat = SimpleNamespace(completions=self)

    def create(self, **kwargs):
        self.__class__.calls.append(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content="Fake model output, not real Groq."))]
        )


def open_app(monkeypatch, *, online=False):
    FakeGroq.calls = []
    monkeypatch.setenv("GROQ_API_KEY", "fake-testing-key" if online else "")
    if online:
        monkeypatch.setattr("llm_client.Groq", FakeGroq)
    app = AppTest.from_file(APP, default_timeout=45).run()
    assert not app.exception
    return app


def test_e2e01_offline_rag_positive_negative_and_chat_mode_isolation(monkeypatch):
    app = open_app(monkeypatch)
    app.sidebar.radio[0].set_value("💬 AI Assistant").run()
    assert app.chat_input[0].disabled
    app.selectbox[0].set_value("📚 Hỏi đáp tài liệu").run()
    app.chat_input[0].set_value("Issue và Pull Request sau commit?").run()
    assert not app.exception
    assert app.session_state["messages"][-1]["mode"] == "offline-grounded"
    assert app.session_state["messages"][-1]["sources"]

    app.chat_input[0].set_value("Chlorophyll quang hợp lá cây quang năng").run()
    assert not app.exception
    assert app.session_state["messages"][-1]["mode"] == "no-evidence"
    assert app.session_state["messages"][-1]["sources"] == []
    assert len(app.session_state["messages"]) == 4

    app.selectbox[0].set_value("🤖 Trò chuyện AI").run()
    assert not app.exception
    assert app.session_state["general_messages"] == []
    assert app.chat_input[0].disabled
    app.selectbox[0].set_value("📚 Hỏi đáp tài liệu").run()
    assert len(app.session_state["messages"]) == 4


def test_e2e02_profile_to_mentor_to_favorites_and_rerun(monkeypatch):
    app = open_app(monkeypatch)
    app.sidebar.radio[0].set_value("👤 Hồ sơ cá nhân").run()
    assert not app.exception
    app.text_input[1].set_value("RAG, LLM")
    app.text_input[2].set_value("Xây dựng ứng dụng AI")
    save = next(b for b in app.button if "Lưu hồ sơ" in b.label)
    save.click().run()
    assert not app.exception
    assert app.session_state["user_profile"]["field_interest"] == "RAG, LLM"
    assert app.session_state["user_profile"]["goals"] == "Xây dựng ứng dụng AI"

    app.sidebar.radio[0].set_value("👥 Tìm Mentor").run()
    assert not app.exception
    next(b for b in app.button if "Tìm Mentor" in b.label).click().run()
    assert not app.exception
    assert len(app.session_state["top_matches"]) == 3

    next(b for b in app.button if "Lưu mentor" in b.label).click().run()
    assert not app.exception
    assert len(app.session_state["favorite_mentors"]) == 1
    app.run()
    assert len(app.session_state["favorite_mentors"]) == 1

    next(b for b in app.button if b.label == "Xóa").click().run()
    assert not app.exception
    assert app.session_state["favorite_mentors"] == []


def test_e2e03_groq_consent_revocation_blocks_new_calls(monkeypatch):
    app = open_app(monkeypatch, online=True)
    app.sidebar.radio[0].set_value("💬 AI Assistant").run()
    assert app.sidebar.checkbox[0].value is False
    assert app.chat_input[0].disabled
    assert FakeGroq.calls == []

    app.sidebar.checkbox[0].set_value(True).run()
    assert not app.chat_input[0].disabled
    app.chat_input[0].set_value("Học Python").run()
    assert not app.exception
    assert len(FakeGroq.calls) == 1
    assert app.session_state["general_messages"][-1]["status"] == "online"

    app.sidebar.checkbox[0].set_value(False).run()
    assert app.chat_input[0].disabled
    assert len(FakeGroq.calls) == 1
    assert len(app.session_state["general_messages"]) == 2


def test_e2e04_independent_sessions_do_not_share_profiles(monkeypatch):
    left = open_app(monkeypatch)
    right = AppTest.from_file(APP, default_timeout=45).run()
    assert not right.exception
    left.session_state["user_profile"] = {"field_interest": "Python"}
    left.session_state["favorite_mentors"] = [{"id": 1}]
    left.run()
    right.run()
    assert not left.exception and not right.exception
    assert right.session_state["user_profile"] == {}
    assert right.session_state["favorite_mentors"] == []


def test_e2e05_probe_rate_limit_is_session_only(monkeypatch):
    app = open_app(monkeypatch, online=True)
    app.sidebar.checkbox[0].set_value(True).run()
    app.session_state["demo_probe_calls"] = 3
    app.run()
    probe = next(b for b in app.sidebar.button if "Kiểm tra AI thật ngay" in b.label)
    assert probe.disabled
    assert FakeGroq.calls == []


def test_e2e06_mentor_no_result_filter_ui(monkeypatch):
    app = open_app(monkeypatch)
    app.sidebar.radio[0].set_value("👥 Tìm Mentor").run()
    assert not app.exception
    # Every available filter can be used without a provider or secret.
    choices = app.selectbox[0].options
    assert "Tất cả" in choices
    assert len(choices) > 1
    app.selectbox[0].set_value(choices[1]).run()
    next(b for b in app.button if "Tìm Mentor" in b.label).click().run()
    assert not app.exception
    assert all(item["mentor"]["field"] == choices[1] for item in app.session_state["top_matches"])
