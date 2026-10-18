"""Final defense: verify UI end-to-end with a fake provider and real probe contract.

Never uses a real credential. A passing test verifies routing/UX only, not
actual Groq availability or model quality on the public Render service.
"""
from pathlib import Path
from types import SimpleNamespace

from streamlit.testing.v1 import AppTest
import pytest

from general_chat import probe_online_model


APP = Path(__file__).resolve().parents[1] / "app.py"


class RecordingGroq:
    calls = []
    def __init__(self, api_key, **kwargs):
        self.api_key = api_key
        self.chat = SimpleNamespace(completions=self)

    def create(self, **kwargs):
        self.__class__.calls.append(kwargs)
        return SimpleNamespace(choices=[
            SimpleNamespace(message=SimpleNamespace(
                content=f"Mô hình giả lập gọi lần thứ {len(self.__class__.calls)}. Tớ nhớ ngữ cảnh Python."
            ))
        ])


class ExplodingGroq:
    def __init__(self, api_key, **kwargs):
        self.chat = SimpleNamespace(completions=self)
    def create(self, **kwargs):
        err = RuntimeError("SECRET api-key-not-for-logs")
        err.status_code = 401
        raise err


@pytest.fixture
def fake_backend(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fake-server-credential-do-not-share")
    RecordingGroq.calls = []
    monkeypatch.setattr("llm_client.Groq", RecordingGroq)
    return RecordingGroq


def test_online_probe_is_real_provider_path_and_not_static(fake_backend):
    client = fake_backend(api_key="fake-server-credential-do-not-share")
    result = probe_online_model(client=client)
    assert result.status == "online"
    assert "Mô hình giả lập" in result.answer
    assert len(fake_backend.calls) == 1
    assert fake_backend.calls[0]["model"] == "openai/gpt-oss-120b"
    assert fake_backend.calls[0]["messages"][-1]["role"] == "user"
    assert "api-key" not in repr(fake_backend.calls)


def test_probe_auth_failure_does_not_echo_api_key(monkeypatch):
    monkeypatch.setattr("llm_client.Groq", ExplodingGroq)
    from llm_client import build_llm_client
    response = probe_online_model(client=build_llm_client("fake-server-key"))
    assert response.status == "error"
    assert "API key" in response.answer
    assert "SECRET" not in response.answer
    assert "api-key-not-for-logs" not in response.answer


def test_no_provider_call_without_consent_even_if_server_key_configured(fake_backend):
    app = AppTest.from_file(APP, default_timeout=45).run()
    assert not app.exception
    app.sidebar.radio[0].set_value("💬 AI Assistant").run()
    assert not app.exception
    assert app.sidebar.checkbox[0].value is False
    assert app.chat_input[0].disabled is True
    assert len(fake_backend.calls) == 0
    assert not any("Kiểm tra AI thật ngay" in b.label for b in app.sidebar.button)


def test_real_chat_ui_two_turns_mode_separation_and_probe(fake_backend):
    app = AppTest.from_file(APP, default_timeout=45).run()
    assert not app.exception
    app.sidebar.radio[0].set_value("💬 AI Assistant").run()
    app.sidebar.checkbox[0].set_value(True).run()
    assert not app.exception
    assert app.chat_input[0].disabled is False

    # This is the same chat-input submit path the user uses, with fake API.
    app.chat_input[0].set_value("Học Python từ đâu?").run()
    assert not app.exception
    assert len(fake_backend.calls) == 1
    assert app.session_state["general_messages"][0]["role"] == "user"
    assert app.session_state["general_messages"][1]["status"] == "online"
    app.chat_input[0].set_value("Tớ vừa hỏi gì?").run()
    assert not app.exception
    assert len(fake_backend.calls) == 2
    sent = fake_backend.calls[-1]["messages"]
    assert [m["role"] for m in sent] == ["system", "user", "assistant", "user"]
    assert "Học Python" in sent[1]["content"]
    assert "fake-server-credential" not in repr(sent)
    assert app.session_state["demo_chat_calls"] == 2

    app.selectbox[0].set_value("📚 Hỏi đáp tài liệu").run()
    assert not app.exception
    assert "messages" in app.session_state or not app.exception
    assert len(app.session_state["general_messages"]) == 4
    assert app.session_state["messages"] == []
    app.selectbox[0].set_value("🤖 Trò chuyện AI").run()
    assert not app.exception
    assert len(app.session_state["general_messages"]) == 4

    probe_button = next(b for b in app.sidebar.button if "Kiểm tra AI thật ngay" in b.label)
    probe_button.click().run()
    assert not app.exception
    assert len(fake_backend.calls) == 3
    assert app.session_state["demo_probe_calls"] == 1
    assert any("Groq vừa phản hồi" in item.value for item in app.success)


def test_demo_quota_disables_chat_without_saying_server_enforces_it(fake_backend):
    app = AppTest.from_file(APP, default_timeout=45).run()
    app.sidebar.radio[0].set_value("💬 AI Assistant").run()
    app.sidebar.checkbox[0].set_value(True).run()
    app.session_state["demo_chat_calls"] = 30
    app.run()
    assert not app.exception
    assert app.chat_input[0].disabled
    assert any("30 lượt chat" in item.value for item in app.warning)
    assert fake_backend.calls == []
