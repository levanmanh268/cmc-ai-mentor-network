from pathlib import Path

from rag_engine import KnowledgeBase, answer_with_rag


def _build_kb(tmp_path: Path) -> KnowledgeBase:
    root = tmp_path / "knowledge_base"
    root.mkdir()
    (root / "git.md").write_text(
        "# Git workflow\nMỗi thay đổi bắt đầu bằng GitHub Issue. "
        "Tạo branch riêng, chạy test rồi commit với Refs issue.",
        encoding="utf-8",
    )
    (root / "rag.md").write_text(
        "# RAG\nRAG truy xuất tài liệu trước khi sinh câu trả lời. "
        "Khi không đủ bằng chứng, hệ thống nên từ chối suy diễn.",
        encoding="utf-8",
    )
    return KnowledgeBase(root, chunk_words=80, overlap_words=10)


def test_retrieval_returns_relevant_source(tmp_path):
    kb = _build_kb(tmp_path)
    results = kb.search("GitHub issue branch commit", k=2)

    assert results
    assert results[0].source == "git.md"
    assert 0.0 <= results[0].score <= 1.0


def test_retrieval_rejects_unrelated_query(tmp_path):
    kb = _build_kb(tmp_path)
    results = kb.search("công thức quang hợp thực vật", k=2)

    assert results == []


def test_offline_answer_is_grounded(tmp_path):
    kb = _build_kb(tmp_path)
    result = answer_with_rag("RAG làm gì khi thiếu bằng chứng?", kb, client=None)

    assert result.mode == "offline-grounded"
    assert result.sources
    assert "không tự suy diễn" in result.answer


def test_model_without_citations_is_not_called_grounded(tmp_path):
    kb = _build_kb(tmp_path)
    class FakeLLM:
        def __init__(self, text):
            self.text = text
        @property
        def chat(self):
            return self
        @property
        def completions(self):
            return self
        def create(self, **_):
            from types import SimpleNamespace
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=self.text))])

    for malicious in ("Ai đó có thể bịa câu trả lời.", "Sai [S99]"):
        response = answer_with_rag("GitHub issue branch", kb, client=FakeLLM(malicious))
        assert response.mode == "offline-fallback"
        assert response.sources
        assert response.answer.startswith("AI sinh ngôn ngữ đang ở chế độ offline")


def test_valid_citation_is_explicitly_unverified(tmp_path):
    kb = _build_kb(tmp_path)
    class FakeLLM:
        @property
        def chat(self):
            return self
        @property
        def completions(self):
            return self
        def create(self, **_):
            from types import SimpleNamespace
            return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Kiểm tra issue [S1]") )])
    response = answer_with_rag("GitHub issue branch", kb, client=FakeLLM())
    assert response.mode == "online-citations-unverified"


def test_symlink_escape_is_not_indexed(tmp_path):
    root = tmp_path / "docs"
    root.mkdir()
    secret = tmp_path / "private.md"
    secret.write_text("Top secret payroll document", encoding="utf-8")
    import os
    import pytest
    try:
        (root / "link.md").symlink_to(secret)
    except (OSError, NotImplementedError):
        pytest.skip("Symlinks unavailable in this test environment")
    (root / "public.md").write_text("Public course guide.", encoding="utf-8")
    kb = KnowledgeBase(root)
    assert kb.document_count == 1
    assert kb.search("payroll") == []


def test_punctuation_only_corpus_does_not_crash(tmp_path):
    root = tmp_path / "docs"
    root.mkdir()
    (root / "punctuation.md").write_text("!!! ??? ...", encoding="utf-8")
    kb = KnowledgeBase(root)
    assert kb.search("something") == []
