"""Offline AppTest smoke tests for untrusted labels rendered by the UI."""

from pathlib import Path
from types import SimpleNamespace

from streamlit.testing.v1 import AppTest

import rag_engine


APP = Path(__file__).resolve().parents[1] / "app.py"


def make_app(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    app = AppTest.from_file(APP, default_timeout=45).run()
    assert not app.exception
    return app


def test_mentor_markdown_label_is_escaped_in_search_results(monkeypatch):
    app = make_app(monkeypatch)
    mentor_id = "fixture-mentor"
    app.session_state["active_mentor_filters"] = ("Tất cả", "Tất cả")
    app.session_state["top_matches"] = [
        {
            "mentor": {
                "id": mentor_id,
                "name": "<b>Demo Mentor</b> **admin** [profile](https://example.test)",
                "title": "Mentor giả lập",
                "company": "CMC",
                "field": "AI",
                "experience_years": 2,
                "bio": "Fixture only.",
            },
            "hybrid_score": 88.0,
            "semantic_score": 81.0,
        }
    ]
    app.session_state["match_explanations"] = {mentor_id: "Fixture explanation."}

    app.sidebar.radio[0].set_value("👥 Tìm Mentor").run()

    assert not app.exception
    rendered = [element.value for element in app.markdown]
    assert any(
        "&lt;b&gt;Demo Mentor&lt;/b&gt; \\*\\*admin\\*\\* "
        "\\[profile\\]\\(https://example.test\\)" in value
        for value in rendered
    )


def test_rag_source_labels_are_escaped_and_legacy_filename_remains_intact(monkeypatch):
    def fake_answer_with_rag(*args, **kwargs):
        return SimpleNamespace(
            answer="Fixture response.",
            sources=(
                SimpleNamespace(
                    source="<b>Fixture</b> **source** [link](https://example.test)",
                    score=0.5,
                    text="",
                ),
                SimpleNamespace(source="legacy.md", score=0.25, text=""),
            ),
            mode="offline-grounded",
        )

    monkeypatch.setattr(rag_engine, "answer_with_rag", fake_answer_with_rag)
    app = make_app(monkeypatch)
    app.sidebar.radio[0].set_value("💬 AI Assistant").run()
    app.selectbox[0].set_value("📚 Hỏi đáp tài liệu").run()
    app.chat_input[0].set_value("fixture question").run()

    assert not app.exception
    rendered = [element.value for element in app.markdown]
    assert any(
        "&lt;b&gt;Fixture&lt;/b&gt; \\*\\*source\\*\\* "
        "\\[link\\]\\(https://example.test\\)" in value
        for value in rendered
    )
    assert any("**legacy.md** • relevance=0.250" in value for value in rendered)
