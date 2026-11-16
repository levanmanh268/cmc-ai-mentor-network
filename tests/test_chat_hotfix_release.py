"""Issue #60 release traceability and safety gates."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_hotfix_release_is_scoped_to_green_main_and_live_cloud():
    text = (ROOT / ".github/workflows/publish-chat-hotfix-v0.2.1.yml").read_text(
        encoding="utf-8"
    )
    for key in (
        'workflows: ["CI"]',
        'branches: ["main"]',
        "github.event.workflow_run.conclusion == 'success'",
        "github.event.workflow_run.event == 'push'",
        "github.event.workflow_run.head_repository.full_name == github.repository",
        "github.event.workflow_run.head_sha",
        "persist-credentials: false",
        "CURRENT_MAIN",
        "/_stcore/health",
        "gh release create",
        "--target",
        "--prerelease",
        "TAG_SHA",
        "v0.2.1",
    ):
        assert key in text
    assert "v0.2.0" not in text


def test_architecture_trace_and_release_notes_match_local_social_behavior():
    architecture = (ROOT / "docs/architecture.md").read_text(encoding="utf-8")
    notes = (ROOT / "docs/RELEASE_NOTES_v0.2.1.md").read_text(encoding="utf-8")
    app = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "chat_intents.py" in architecture
    assert "local-social" in architecture
    assert "local-social" in notes
    assert "hello cậu" in notes
    assert "3 tài liệu mẫu" in app
    assert architecture.count("```mermaid") == 5
