"""SEC-03/04/05/09/10/11/12: offline security regression cases.

No live-model, browser penetration test, auth or RBAC claims.
"""
from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from security_controls import consented_client, safe_markdown_label, valid_rag_question
from profile_helpers import reset_profile_state, save_profile_state
from ui_helpers import clear_chat_history
from rag_engine import KnowledgeBase, answer_with_rag
from scripts.secret_guard import find_secret_patterns


@pytest.mark.parametrize("value", [None, 0, [], {}, "", "   ", "\n\t"])
def test_sec03_rejects_wrong_type_or_empty_query(value):
    assert not valid_rag_question(value)


def test_sec03_rejects_oversized_query_before_provider_call(tmp_path):
    (tmp_path / "guide.md").write_text("Tài liệu demo hướng dẫn lập trình Python an toàn.", encoding="utf-8")
    kb = KnowledgeBase(tmp_path)
    calls = []

    class Provider:
        chat = SimpleNamespace(
            completions=SimpleNamespace(create=lambda **kwargs: calls.append(kwargs))
        )

    assert not kb.search("a" * 4001)
    result = answer_with_rag("a" * 4001, kb, client=Provider())
    assert result.mode == "no-evidence"
    assert result.sources == ()
    assert calls == []


def test_sec03_rejects_non_string_answer_input_without_crashing(tmp_path):
    result = answer_with_rag({"untrusted": "payload"}, KnowledgeBase(tmp_path))
    assert result.mode == "no-evidence"


def test_sec03_symlinked_root_not_indexed_portable(tmp_path, monkeypatch):
    (tmp_path / "external.md").write_text("SECRET DOCUMENT OUTSIDE APPROVED ROOT", encoding="utf-8")
    original = Path.is_symlink
    monkeypatch.setattr(
        Path, "is_symlink",
        lambda self: True if self == tmp_path else original(self),
    )
    assert KnowledgeBase(tmp_path).document_count == 0


def test_sec04_dynamic_markdown_label_escapes_html_and_formatting():
    payload = "<img src=x onerror=alert(1)> **admin** [phish](https://example.test)"
    rendered = safe_markdown_label(payload)
    assert "<img" not in rendered
    assert "&lt;img" in rendered
    assert "\\*\\*admin\\*\\*" in rendered
    assert "\\[" in rendered


def test_sec04_source_filename_preserves_dot_for_ui_traceability():
    assert safe_markdown_label("legacy.md") == "legacy.md"

def test_sec04_dynamic_label_cannot_start_new_heading_or_inject_newline():
    rendered = safe_markdown_label("Mentor\n# forged title\t**trusted**")
    assert "\n" not in rendered
    assert "\\#" in rendered
    assert len(rendered) < 200


def test_sec05_session_profile_reset_does_not_touch_other_session():
    a = {"user_profile": {"name": "A"}, "messages": [{"role": "user"}]}
    b = {"user_profile": {"name": "B"}, "messages": [{"role": "assistant"}]}
    reset_profile_state(a)
    assert a["user_profile"] == {}
    assert b["user_profile"] == {"name": "B"}
    assert a["messages"] == [{"role": "user"}]


def test_sec05_clearing_chat_preserves_profile_and_favorites():
    state = {
        "messages": [{"role": "user", "content": "private"}],
        "user_profile": {"name": "Demo"},
        "favorite_mentors": [{"id": 1}],
    }
    clear_chat_history(state)
    assert state["messages"] == []
    assert state["user_profile"]["name"] == "Demo"
    assert state["favorite_mentors"] == [{"id": 1}]


@pytest.mark.parametrize("consent", [False, None, "", 0, "true", [], {}])
def test_sec10_consent_deny_by_default(consent):
    assert consented_client(object(), consent) is None


def test_sec10_consent_explicit_true_only():
    client = object()
    assert consented_client(client, True) is client
    assert consented_client(None, True) is None


def test_sec09_secret_guard_detects_fake_examples_without_real_keys():
    fake_key = "gsk_" + ("X" * 24)
    fake_openai = "sk-" + ("y" * 24)
    findings = find_secret_patterns(fake_key + "\n" + fake_openai)
    assert len(findings) >= 2
    assert find_secret_patterns("GROQ_API_KEY=your_api_key_here") == []


def test_sec11_save_profile_does_not_update_another_session():
    a = {"user_profile": {}, "top_matches": [1], "match_explanations": {"x": "y"}}
    b = {"user_profile": {"name": "private"}}
    save_profile_state(a, {"name": "A"})
    assert a["user_profile"] == {"name": "A"}
    assert a["top_matches"] == []
    assert b["user_profile"] == {"name": "private"}
