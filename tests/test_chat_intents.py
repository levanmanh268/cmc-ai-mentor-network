"""Issue #60: avoid treating greetings as unsupported document questions."""
from pathlib import Path
from types import SimpleNamespace

import pytest

from chat_intents import local_social_reply
from rag_engine import KnowledgeBase, answer_with_rag
from ui_helpers import rag_mode_label


@pytest.mark.parametrize(
    "message",
    [
        "hello cậu", "HELLO CẬU!!!", "hello ban", "Hi", "hi cậu 👋",
        "Xin chào!", "chào bạn", "Chao cau", "hey", "HELO",
    ],
)
def test_greetings_are_short_natural_and_friendly(message):
    reply = local_social_reply(message)
    assert reply is not None, message
    assert "Chào cậu" in reply
    assert "offline" in reply


@pytest.mark.parametrize("message", ["Cảm ơn cậu!", "THANKS", "thank you", "cam on nha"])
def test_standalone_thanks_is_handled(message):
    answer = local_social_reply(message)
    assert answer is not None
    assert "Không có gì" in answer


@pytest.mark.parametrize(
    "message",
    ["Bạn làm được gì?", "Cậu có thể làm gì", "HELP", "huong dan su dung"],
)
def test_offline_capabilities_are_explained_truthfully(message):
    reply = local_social_reply(message)
    assert reply is not None
    assert "offline" in reply
    assert "tài liệu" in reply


@pytest.mark.parametrize(
    "message",
    [
        "hello cậu, cho tớ biết chính sách học bổng?",
        "hi, quy trình GitHub issue là gì?",
        "Chào cậu. Tớ muốn học RAG.",
        "Điểm GPA của tớ là bao nhiêu?",
        "Các nhà khoa học chiến thắng Nobel năm 2030 là ai?",
        "hello world lập trình Python",
        "hello cậu" + ("!" * 120),
        "",
    ],
)
def test_non_social_or_mixed_questions_never_bypass_retrieval(message):
    assert local_social_reply(message) is None


@pytest.fixture
def kb(tmp_path):
    root = tmp_path / "docs"
    root.mkdir()
    (root / "course.md").write_text(
        "GitHub issue branch commit review: trước khi merge pull request "
        "hãy chạy unit test để tránh lỗi hồi quy.", encoding="utf-8"
    )
    return KnowledgeBase(root)


def test_greeting_bypasses_retrieval_and_online_llm(kb, monkeypatch):
    def fail_search(*_args, **_kwargs):
        pytest.fail("Social turn must not call KB search")
    monkeypatch.setattr(kb, "search", fail_search)

    class FailingClient:
        @property
        def chat(self):
            pytest.fail("Social turn must not call online LLM")

    response = answer_with_rag("hello cậu", kb, client=FailingClient())
    assert response.mode == "local-social"
    assert response.sources == ()
    assert response.top_score == 0
    assert "Chào cậu" in response.answer
    assert "cục bộ" in rag_mode_label(response.mode)


def test_unknown_facts_still_fail_closed_and_grounded_queries_still_work(kb):
    unknown = answer_with_rag("công thức quang hợp thực vật", kb, client=None)
    assert unknown.mode == "no-evidence"
    assert not unknown.sources

    source_based = answer_with_rag("GitHub issue branch commit", kb, client=None)
    assert source_based.mode == "offline-grounded"
    assert source_based.sources
    assert source_based.sources[0].source == "course.md"


def test_offline_chat_ui_has_onboarding_warning(monkeypatch):
    from streamlit.testing.v1 import AppTest

    monkeypatch.setenv("GROQ_API_KEY", "")
    app = AppTest.from_file(
        Path(__file__).resolve().parents[1] / "app.py",
        default_timeout=45,
    ).run()
    assert not app.exception
    app.sidebar.radio[0].set_value("💬 AI Assistant").run()
    assert not app.exception
    assert any("Bản demo offline" in info.value for info in app.info)
    assert any("3 tài liệu mẫu" in info.value for info in app.info)
