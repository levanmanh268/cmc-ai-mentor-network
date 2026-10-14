"""Static release-process checks; external GitHub state is verified after publishing."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RELEASE_NOTES = ROOT / "docs" / "RELEASE_NOTES_v0.1.0.md"
RELEASE_PROCESS = ROOT / "docs" / "RELEASE_PROCESS.md"
WORKFLOW = ROOT / ".github" / "workflows" / "publish-classroom-release.yml"


def test_first_release_notes_trace_closed_and_open_issues_separately():
    notes = RELEASE_NOTES.read_text(encoding="utf-8")
    for closed in (1, 2, 3, 4, 5, 11, 13, 14, 20, 24, 29, 40):
        assert f"/issues/{closed})" in notes, f"Missing closed Issue #{closed}"
    for open_issue in (17, 18, 19, 21, 22, 23, 50, 51):
        assert f"/issues/{open_issue})" in notes, f"Missing open Issue #{open_issue}"
    assert "chưa merge" in notes
    assert "online-citations-unverified" in notes
    assert "Không có đăng nhập" in notes
    assert "portfolio độc lập" in notes


def test_first_release_workflow_is_trusted_main_ci_only_and_one_shot():
    source = WORKFLOW.read_text(encoding="utf-8")
    checks = (
        'workflows: ["CI"]',
        'branches: ["main"]',
        "workflow_run.conclusion == 'success'",
        "workflow_run.event == 'push'",
        "workflow_run.head_repository.full_name == github.repository",
        "workflow_run.head_sha",
        "persist-credentials: false",
        "LATEST_MAIN_SHA",
        "gh release view",
        "gh release create",
        "v0.1.0",
        "--target",
        "--notes-file",
        "--prerelease",
        "TAG_SHA",
    )
    for marker in checks:
        assert marker in source, f"Missing release safety marker: {marker}"
    assert "permissions:\n  contents: read" in source
    assert "    permissions:\n      contents: write" in source
    assert "if:" in source


def test_readme_has_release_navigation_and_documented_process():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "(docs/RELEASE_NOTES_v0.1.0.md)" in readme
    assert "(docs/RELEASE_PROCESS.md)" in readme
    assert "https://github.com/levanmanh268/cmc-ai-mentor-network/releases" in readme
    process = RELEASE_PROCESS.read_text(encoding="utf-8")
    assert "Closed Issue" in process
    assert "GitHub Release" in process
