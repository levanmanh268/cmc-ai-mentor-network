from pathlib import Path

from scripts.secret_guard import scan_file, scan_repository


def test_secret_guard_catches_realistic_groq_secret(tmp_path):
    sample = tmp_path / ".env"
    sample.write_text("GROQ_API_KEY=gsk_abcdefghijklmnopqrstuvwxyz123456\n", encoding="utf-8")
    findings = scan_file(sample)
    assert findings
    assert findings[0]["pattern"] == "Groq-style key"


def test_secret_guard_ignores_placeholder_values(tmp_path):
    sample = tmp_path / ".env.example"
    sample.write_text("GROQ_API_KEY=your_groq_api_key_here\n", encoding="utf-8")
    findings = scan_file(sample)
    assert findings == []


def test_secret_guard_scans_repository_tree(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    (root / "config").mkdir()
    (root / "config" / "keys.txt").write_text("sk-abcdefghijklmnopqrstuvwx_123456\n", encoding="utf-8")
    findings = scan_repository(root)
    assert findings
    assert any(item["pattern"] == "API key-like value" for item in findings)
