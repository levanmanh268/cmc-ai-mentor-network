"""CI contract checks for one-shot v0.3.0 cloud / real AI release."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_release_v030_requires_exact_main_ci_and_cloud_http_checks():
    workflow = (ROOT / ".github/workflows/publish-real-ai-v0.3.yml").read_text(encoding="utf-8")
    for marker in (
        'workflows: ["CI"]',
        'branches: ["main"]',
        "workflow_run.conclusion == 'success'",
        "workflow_run.event == 'push'",
        "workflow_run.head_repository.full_name == github.repository",
        "workflow_run.head_sha",
        "persist-credentials: false",
        "CURRENT_MAIN",
        "gh release view",
        "gh release create",
        "--target",
        "--prerelease",
        "/_stcore/health",
        "TAG_SHA",
        "v0.3.0",
    ):
        assert marker in workflow
    assert "v0.2.1" not in workflow
    assert "permissions:\n  contents: read" in workflow
    assert "    permissions:\n      contents: write" in workflow


def test_notes_truthfully_describe_real_ai_and_missing_credential():
    notes = (ROOT / "docs/RELEASE_NOTES_v0.3.0.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    architecture = (ROOT / "docs/architecture.md").read_text(encoding="utf-8")
    assert "openai/gpt-oss-120b" in notes
    assert "BYOK" in notes
    assert "chưa có Groq API key thật" in notes
    assert "Không có key" in notes
    assert "/pull/64" in notes
    assert "(docs/RELEASE_NOTES_v0.3.0.md)" in readme
    assert architecture.count("```mermaid") == 5
    assert "general_chat.py" in architecture
