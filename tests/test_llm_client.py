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
