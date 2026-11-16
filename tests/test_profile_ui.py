"""Streamlit profile-form regression tests without external LLM calls."""

from pathlib import Path

from streamlit.testing.v1 import AppTest


def make_profile_app(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    app = (
        AppTest.from_file(
            Path(__file__).resolve().parents[1] / "app.py",
            default_timeout=45,
        )
        .run()
    )
    assert not app.exception
    app.sidebar.radio[0].set_value("👤 Hồ sơ cá nhân").run()
    assert not app.exception
    return app


def test_invalid_profile_does_not_overwrite_previous_profile(monkeypatch):
    app = make_profile_app(monkeypatch)
    app.session_state["user_profile"] = {
        "name": "Hồ sơ cũ",
        "year": "Năm 2",
        "field_interest": "AI",
        "goals": "Hoàn thành đồ án",
        "bio": "",
    }
    app.run()

    # The profile page renders name, interest and goals as text inputs.
    app.text_input[1].set_value("   ")
    app.text_input[2].set_value(" \t ")
    app.button[0].click().run()

    assert not app.exception
    assert app.session_state["user_profile"]["name"] == "Hồ sơ cũ"
    assert app.session_state["user_profile"]["field_interest"] == "AI"
    assert app.session_state["user_profile"]["goals"] == "Hoàn thành đồ án"
    assert any("Vui lòng nhập lĩnh vực quan tâm." in item.value for item in app.error)
    assert any("Vui lòng nhập mục tiêu" in item.value for item in app.error)
