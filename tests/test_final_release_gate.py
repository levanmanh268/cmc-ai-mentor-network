"""Guard release tag provenance and final defense handoff correctness."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_v031_immutable_release_fails_closed_on_untrusted_sha():
    flow = (ROOT / ".github/workflows/publish-final-v0.3.1.yml").read_text(encoding="utf-8")
    for required in (
        'workflows: ["CI"]',
        'branches: ["main"]',
        "workflow_run.conclusion == 'success'",
        "workflow_run.event == 'push'",
        "workflow_run.head_repository.full_name == github.repository",
        "workflow_run.head_sha",
        "CURRENT_MAIN",
        "persist-credentials: false",
        "gh release view",
        "gh release create",
        "TAG_SHA",
        "v0.3.1",
        "/_stcore/health",
        "docs/RELEASE_NOTES_v0.3.1.md",
    ):
        assert required in flow
    assert "v0.3.0" not in flow


def test_final_handoff_explicitly_does_not_fake_live_groq_evidence():
    doc = (ROOT / "docs/FINAL_DEFENSE_GATE.md").read_text(encoding="utf-8")
    release = (ROOT / "docs/RELEASE_NOTES_v0.3.1.md").read_text(encoding="utf-8")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    for marker in ("Groq", "probe", "P0", "RAG", "Mentor", "rate limit", "API key"):
        assert marker.lower() in doc.lower()
    assert "không chứng minh" in release
    assert "FINAL_DEFENSE_GATE.md" in readme
    assert "probe_online_model(client=authorized_client)" in source
    assert "MAX_CHAT_CALLS_PER_SESSION = 30" in source
    assert "MAX_PROBES_PER_SESSION = 3" in source
