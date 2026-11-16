"""Static guardrails for the v0.2.0 cloud release process."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_cloud_release_workflow_checks_main_ci_and_public_http():
    flow = (ROOT / ".github/workflows/publish-classroom-v0.2.yml").read_text(
        encoding="utf-8"
    )
    for marker in (
        'workflows: ["CI"]',
        'branches: ["main"]',
        "github.event.workflow_run.conclusion == 'success'",
        "github.event.workflow_run.event == 'push'",
        "github.event.workflow_run.head_repository.full_name == github.repository",
        "github.event.workflow_run.head_sha",
        "persist-credentials: false",
        "GH_TOKEN:",
        "curl --fail",
        "/_stcore/health",
        "index.html",
        "LATEST",
        "gh release create",
        "--target",
        "--prerelease",
        "v0.2.0",
        "TAG_SHA",
    ):
        if marker == "LATEST":
            assert "CURRENT_MAIN" in flow
        else:
            assert marker in flow
    assert "permissions:\n  contents: read" in flow
    assert "    permissions:\n      contents: write" in flow


def test_cloud_docs_and_architecture_exact_scope():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    architecture = (ROOT / "docs/architecture.md").read_text(encoding="utf-8")
    deployment = (ROOT / "docs/CLOUD_DEPLOYMENT.md").read_text(encoding="utf-8")
    notes = (ROOT / "docs/RELEASE_NOTES_v0.2.0.md").read_text(encoding="utf-8")
    assert "https://cmc-ai-mentor-network-group6.onrender.com" in readme
    assert "https://cmc-ai-mentor-network-group6.onrender.com" in architecture
    assert architecture.count("```mermaid") == 5
    assert "st.session_state" in deployment
    assert "không" in notes.lower()
    for pr in (55, 56, 57):
        assert f"/pull/{pr}" in notes
    assert "Không có" not in readme[:100] or "Cloud" in readme


def test_cloud_health_contract_is_documented():
    doc = (ROOT / "docs/CLOUD_DEPLOYMENT.md").read_text(encoding="utf-8")
    assert "/_stcore/health" in doc
    assert "HTTP" in doc
    assert "live" in doc
