"""Guard against a mock-only Groq integration with unsupported GPT-OSS args."""
from pathlib import Path
from types import SimpleNamespace

from matching_engine import generate_match_explanation
from rag_engine import KnowledgeBase, answer_with_rag


class RecordingClient:
    def __init__(self, reply: str):
        self.reply = reply
        self.calls: list[dict] = []
        self.chat = SimpleNamespace(completions=self)

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return SimpleNamespace(
            choices=[SimpleNamespace(message=SimpleNamespace(content=self.reply))]
        )


def _validate_oss_payload(payload, min_tokens):
    assert payload["model"] == "openai/gpt-oss-120b"
    assert "max_completion_tokens" in payload
    assert payload["max_completion_tokens"] >= min_tokens
    assert payload["include_reasoning"] is False
    assert payload["reasoning_effort"] in ("low", "medium", "high")
    assert "reasoning_format" not in payload
    assert "max_tokens" not in payload


def test_doc_answer_uses_gpt_oss_api_compatible_parameters(tmp_path: Path):
    root = tmp_path / "kb"
    root.mkdir()
    (root / "guide.md").write_text(
        "GitHub issue branch commit test GitHub issue branch commit review "
        "là quy trình phát triển phần mềm của nhóm. Chạy unit test trước khi merge.",
        encoding="utf-8",
    )
    kb = KnowledgeBase(root)
    client = RecordingClient("Quy trình bao gồm issue và unit test [S1].")
    result = answer_with_rag("GitHub issue branch commit", kb, client=client)
    assert result.mode == "online-citations-unverified"
    assert len(client.calls) == 1
    _validate_oss_payload(client.calls[0], min_tokens=900)


def test_matching_explanation_uses_same_valid_model_settings():
    profile = {"year": "Năm 2", "field_interest": "RAG", "goals": "Học AI"}
    mentor = {
        "name": "Mentor Demo", "title": "Engineer", "company": "Demo",
        "field": "RAG", "experience_years": 4, "strengths": ["Python", "RAG"],
    }
    client = RecordingClient("Mentor này phù hợp mục tiêu học RAG.")
    result = generate_match_explanation(profile, mentor, 79.0, client=client)
    assert "RAG" in result
    assert len(client.calls) == 1
    _validate_oss_payload(client.calls[0], min_tokens=300)
