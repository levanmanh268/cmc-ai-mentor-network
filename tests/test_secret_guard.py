from scripts.secret_guard import find_secret_patterns


def test_secret_guard_detects_fake_credentials_without_echoing_values():
    fake_values = "\n".join(
        (
            "gsk_" + "a" * 24,
            "sk-" + "b" * 24,
            "-----BEGIN " + "PRIVATE KEY-----",
        )
    )

    findings = find_secret_patterns(fake_values)

    assert len(findings) == 3


def test_secret_guard_allows_environment_variable_instructions():
    assert find_secret_patterns("Set GROQ_API_KEY in your local environment.") == []