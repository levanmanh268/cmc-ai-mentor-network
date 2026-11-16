from pathlib import Path

from streamlit.testing.v1 import AppTest

from mentor_drafts import MENTOR_DRAFTS_KEY


def test_mentor_draft_form_creates_only_session_data(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "")
    app = (
        AppTest.from_file(
            Path(__file__).resolve().parents[1] / "app.py",
            default_timeout=45,
        )
        .run()
    )
    app.sidebar.radio[0].set_value("👥 Tìm Mentor").run()
    assert not app.exception

    next(item for item in app.text_input if item.key == "mentor_draft_name").set_value(
        "Mentor UI Test"
    )
    next(item for item in app.text_input if item.key == "mentor_draft_title").set_value(
        "AI Engineer"
    )
    next(item for item in app.text_input if item.key == "mentor_draft_company").set_value(
        "Session Lab"
    )
    next(item for item in app.text_area if item.key == "mentor_draft_bio").set_value(
        "Mentor draft for this session."
    )
    next(
        item for item in app.text_input if item.key == "mentor_draft_strengths"
    ).set_value("Python, RAG")
    next(
        item for item in app.text_input if item.key == "mentor_draft_supports"
    ).set_value("Project")
    next(
        button for button in app.button if button.key == "create_mentor_draft"
    ).click().run()

    assert not app.exception
    drafts = app.session_state[MENTOR_DRAFTS_KEY]
    assert len(drafts) == 1
    assert drafts[0]["name"] == "Mentor UI Test"
    assert drafts[0]["company"] == "Session Lab"
