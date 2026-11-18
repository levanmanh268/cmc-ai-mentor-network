"""Static privacy-inventory and user-consent regressions."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs" / "privacy" / "data-inventory.md"


def test_privacy_inventory_exists_and_uses_canonical_issue_paths():
    assert INVENTORY.is_file()
    body = INVENTORY.read_text(encoding="utf-8")
    for marker in (
        "# Privacy data inventory",
        "issues/178",
        "app.py",
        "profile_helpers.py",
        "llm_client.py",
        "general_chat.py",
        "rag_engine.py",
        "mentor_drafts.py",
        "APPLICABLE",
        "NOT APPLICABLE",
        "UNKNOWN",
    ):
        assert marker in body


def test_privacy_inventory_does_not_claim_missing_persistence_or_encryption():
    body = INVENTORY.read_text(encoding="utf-8")
    app_source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "Persistent database" in body
    assert "NOT APPLICABLE" in body
    assert "No database" in body or "không có cơ sở dữ liệu" in body
    assert "No encrypted persistent data store" in body
    assert "user_profile" in app_source
    assert "session_state" in app_source
    assert "encrypted persistent" in body.lower()


def test_privacy_inventory_links_consent_and_third_party_unknowns():
    body = INVENTORY.read_text(encoding="utf-8")
    assert "Đồng ý gửi dữ liệu cần thiết" in body
    assert "default" in body.lower()
    assert "Turning consent off" in body
    assert "provider-side" in body.lower()
    assert "UNKNOWN" in body
