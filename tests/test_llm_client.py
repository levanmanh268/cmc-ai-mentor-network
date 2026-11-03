from llm_client import build_llm_client, get_groq_api_key, llm_enabled


def test_llm_is_disabled_without_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    assert get_groq_api_key() == ""
    assert llm_enabled() is False
    assert build_llm_client() is None


def test_whitespace_api_key_is_treated_as_missing(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "   ")

    assert get_groq_api_key() == ""
    assert llm_enabled() is False
    assert build_llm_client() is None


def test_example_api_key_is_not_treated_as_configured(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "your_groq_api_key_here")

    assert get_groq_api_key() == ""
    assert llm_enabled() is False
    assert build_llm_client() is None



def test_groq_client_has_bounded_timeout_and_sdk_retry(monkeypatch):
    captured = {}

    class FakeGroq:
        def __init__(self, **kwargs):
            captured.update(kwargs)

    monkeypatch.setattr("llm_client.Groq", FakeGroq)
    client = build_llm_client("test-only-key")
    assert isinstance(client, FakeGroq)
    assert captured["api_key"] == "test-only-key"
    assert captured["timeout"] == 35.0
    assert captured["max_retries"] == 1
