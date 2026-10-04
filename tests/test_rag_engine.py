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
