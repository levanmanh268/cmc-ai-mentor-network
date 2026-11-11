"""Offline regression tests for RAG no-evidence and citation refusal guards."""
from pathlib import Path
from types import SimpleNamespace

from rag_engine import KnowledgeBase, answer_with_rag, validate_citation_ids


class RecordingProvider:
    def __init__(self):
        self.calls = []
        self.chat = SimpleNamespace(completions=self)

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(choices=[
            SimpleNamespace(message=SimpleNamespace(content="Unexpected answer [S1]"))
        ])


def build_knowledge_base(tmp_path: Path, text: str | None = None) -> KnowledgeBase:
    root = tmp_path / "knowledge_base"
    root.mkdir()
    if text is not None:
        (root / "guide.md").write_text(text, encoding="utf-8")
    return KnowledgeBase(root)


def test_empty_corpus_returns_no_evidence_without_provider_call(tmp_path):
    knowledge_base = build_knowledge_base(tmp_path)
    provider = RecordingProvider()

    result = answer_with_rag(
        "Quy trình tạo GitHub issue là gì?", knowledge_base, client=provider
    )

    assert result.mode == "no-evidence"
    assert result.sources == ()
    assert provider.calls == []


def test_off_topic_question_returns_no_evidence_without_provider_call(tmp_path):
    knowledge_base = build_knowledge_base(
        tmp_path,
        "GitHub issue branch pull request review workflow documentation.",
    )
    provider = RecordingProvider()

    result = answer_with_rag(
        "Chlorophyll photosynthesis plant sunlight", knowledge_base, client=provider
    )

    assert result.mode == "no-evidence"
    assert result.sources == ()
    assert provider.calls == []


def test_zero_citation_id_is_rejected():
    assert not validate_citation_ids("Unsupported statement [S0].", num_sources=1)


def test_out_of_range_citation_id_is_rejected():
    assert not validate_citation_ids("Unsupported statement [S99].", num_sources=1)


def test_answer_without_citation_is_rejected():
    assert not validate_citation_ids("Unsupported statement without a source.", num_sources=1)