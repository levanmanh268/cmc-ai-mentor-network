from copy import deepcopy

from profile_helpers import reset_profile_state
from ui_helpers import clear_chat_history


def test_reset_profile_state_isolated_between_sessions():
    session_a = {
        "user_profile": {"field_interest": "NLP"},
        "top_matches": [{"id": "stale-a"}],
        "match_explanations": {"stale-a": "Old explanation"},
        "favorite_mentors": [{"id": "favorite-a"}],
        "messages": [{"role": "user", "content": "Keep A chat"}],
    }
    session_b = {
        "user_profile": {"field_interest": "RAG"},
        "top_matches": [{"id": "match-b"}],
        "match_explanations": {"match-b": "Keep B explanation"},
        "favorite_mentors": [{"id": "favorite-b"}],
        "messages": [{"role": "user", "content": "Keep B chat"}],
    }
    original_session_b = deepcopy(session_b)

    reset_profile_state(session_a)

    assert session_a["user_profile"] == {}
    assert session_a["top_matches"] == []
    assert session_a["match_explanations"] == {}
    assert session_a["favorite_mentors"] == [{"id": "favorite-a"}]
    assert session_a["messages"] == [{"role": "user", "content": "Keep A chat"}]
    assert session_b == original_session_b


def test_clear_chat_history_keeps_favorites_and_other_session():
    session_a = {
        "messages": [{"role": "user", "content": "Remove A chat"}],
        "user_profile": {"field_interest": "NLP"},
        "favorite_mentors": [{"id": "favorite-a"}],
    }
    session_b = {
        "messages": [{"role": "user", "content": "Keep B chat"}],
        "favorite_mentors": [{"id": "favorite-b"}],
    }
    original_session_b = deepcopy(session_b)

    clear_chat_history(session_a)

    assert session_a["messages"] == []
    assert session_a["user_profile"] == {"field_interest": "NLP"}
    assert session_a["favorite_mentors"] == [{"id": "favorite-a"}]
    assert session_b == original_session_b
