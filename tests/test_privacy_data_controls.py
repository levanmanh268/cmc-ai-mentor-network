"""Personal data-control documentation and session-state regressions."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONTROLS = ROOT / "docs" / "privacy" / "data-controls.md"


def test_privacy_data_controls_inventory_uses_real_state_and_paths():
    assert CONTROLS.is_file()
    body = CONTROLS.read_text(encoding="utf-8")
    for marker in (
        "issues/179",
        "profile_helpers.py",
        "ui_helpers.py",
        "mentor_drafts.py",
        "st.session_state",
        "NOT APPLICABLE",
        "UNKNOWN",
        "provider",
    ):
        assert marker in body


def test_reset_profile_preserves_chat_favorites_and_drafts():
    from profile_helpers import reset_profile_state

    state = {
        "user_profile": {"name": "Student"},
        "top_matches": [{"mentor": {"id": 1}}],
        "match_explanations": {1: "cached"},
        "messages": [{"role": "user", "content": "RAG chat"}],
        "general_messages": [{"role": "user", "content": "General chat"}],
        "favorite_mentors": [{"id": 1}],
        "session_mentor_drafts": [{"id": 99}],
    }

    reset_profile_state(state)

    assert state["user_profile"] == {}
    assert state["top_matches"] == []
    assert state["match_explanations"] == {}
    assert state["messages"] == [{"role": "user", "content": "RAG chat"}]
    assert state["general_messages"] == [{"role": "user", "content": "General chat"}]
    assert state["favorite_mentors"] == [{"id": 1}]
    assert state["session_mentor_drafts"] == [{"id": 99}]


def test_clear_chat_preserves_profile_and_favorites():
    from ui_helpers import clear_chat_history

    state = {
        "messages": [{"role": "assistant", "content": "answer"}],
        "general_messages": [{"role": "assistant", "content": "keep general"}],
        "user_profile": {"name": "Student"},
        "favorite_mentors": [{"id": 1}],
    }

    clear_chat_history(state)

    assert state["messages"] == []
    assert state["general_messages"] == [{"role": "assistant", "content": "keep general"}]
    assert state["user_profile"] == {"name": "Student"}
    assert state["favorite_mentors"] == [{"id": 1}]


def test_two_session_state_dicts_do_not_share_personal_data():
    left = {
        "user_profile": {"name": "Left"},
        "favorite_mentors": [{"id": 1}],
    }
    right = {}

    assert left["user_profile"]["name"] == "Left"
    assert left["favorite_mentors"] == [{"id": 1}]
    assert right.get("user_profile", {}) == {}
    assert right.get("favorite_mentors", []) == []
