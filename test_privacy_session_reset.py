from copy import deepcopy

from profile_helpers import reset_profile_state
from ui_helpers import clear_chat_history


def test_reset_profile_state_does_not_change_another_session():
    session_a = {
        "user_profile": {"name": "Student A", "field_interest": "AI"},
        "top_matches": [{"id": "mentor-a"}],
        "match_explanations": {"mentor-a": "A explanation"},
        "favorite_mentors": [{"id": "favorite-a"}],
        "messages": [{"role": "user", "content": "A chat"}],
    }
    session_b = {
        "user_profile": {"name": "Student B", "field_interest": "Design"},
        "top_matches": [{"id": "mentor-b"}],
        "match_explanations": {"mentor-b": "B explanation"},
        "favorite_mentors": [{"id": "favorite-b"}],
        "messages": [{"role": "user", "content": "B chat"}],
    }
    session_b_before_reset = deepcopy(session_b)

    reset_profile_state(session_a)

    assert session_a["user_profile"] == {}
    assert session_a["top_matches"] == []
    assert session_a["match_explanations"] == {}
    assert session_a["favorite_mentors"] == [{"id": "favorite-a"}]
    assert session_a["messages"] == [{"role": "user", "content": "A chat"}]
    assert session_b == session_b_before_reset


def test_clear_chat_history_only_clears_one_session_and_preserves_favorites():
    session_a = {
        "messages": [{"role": "user", "content": "A chat"}],
        "user_profile": {"name": "Student A"},
        "favorite_mentors": [{"id": "favorite-a"}],
    }
    session_b = {
        "messages": [{"role": "user", "content": "B chat"}],
        "user_profile": {"name": "Student B"},
        "favorite_mentors": [{"id": "favorite-b"}],
    }
    session_b_before_clear = deepcopy(session_b)

    clear_chat_history(session_a)

    assert session_a["messages"] == []
    assert session_a["user_profile"] == {"name": "Student A"}
    assert session_a["favorite_mentors"] == [{"id": "favorite-a"}]
    assert session_b == session_b_before_clear
