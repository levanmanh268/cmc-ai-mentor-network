from types import SimpleNamespace

from ui_helpers import normalize_saved_source, rag_mode_label, source_history_payload


def test_source_history_payload_keeps_excerpt_and_clamps_score():
    chunk = SimpleNamespace(
        source="guide.md",
        score=1.4,
        text="  Useful evidence from the guide.  ",
    )

    payload = source_history_payload(chunk)

    assert payload == {
        "name": "guide.md",
        "score": 1.0,
        "excerpt": "Useful evidence from the guide.",
    }


def test_source_history_payload_truncates_long_excerpt():
    payload = source_history_payload(
        {"name": "long.md", "score": 0.2, "excerpt": "x" * 400}
    )

    assert len(payload["excerpt"]) == 351
    assert payload["excerpt"].endswith("…")


def test_legacy_sources_with_missing_fields_do_not_crash():
    assert normalize_saved_source({"name": "old.md", "score": 0.5}) == {
        "name": "old.md",
        "score": 0.5,
        "excerpt": "",
    }
    assert normalize_saved_source({}) == {
        "name": "Nguồn không xác định",
        "score": 0.0,
        "excerpt": "",
    }
    assert normalize_saved_source(None) is None


def test_all_rag_modes_have_truthful_vietnamese_labels():
    modes = (
        "no-evidence",
        "offline-grounded",
        "online-citations-unverified",
        "offline-fallback",
    )

    for mode in modes:
        label = rag_mode_label(mode)
        assert mode not in label
        assert label

    assert "chưa được xác minh ngữ nghĩa" in rag_mode_label(
        "online-citations-unverified"
    ).lower()
    assert "bằng chứng" in rag_mode_label("no-evidence").lower()


def test_unknown_and_missing_modes_are_safe():
    assert "chưa được nhận diện" in rag_mode_label("future-mode")
    assert "Không có thông tin" in rag_mode_label(None)



def test_clear_chat_history_preserves_profile_and_favorites():
    from ui_helpers import clear_chat_history

    state = {
        "messages": [{"role": "user", "content": "hello"}],
        "user_profile": {"name": "Keep profile"},
        "favorite_mentors": [{"id": "mentor-1"}],
        "top_matches": [{"id": "match-1"}],
    }

    clear_chat_history(state)

    assert state["messages"] == []
    assert state["user_profile"] == {"name": "Keep profile"}
    assert state["favorite_mentors"] == [{"id": "mentor-1"}]
    assert state["top_matches"] == [{"id": "match-1"}]
