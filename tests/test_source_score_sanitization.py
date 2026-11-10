import pytest

from ui_helpers import source_history_payload


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0.4, 0.4),
        (-0.5, 0.0),
        (1.5, 1.0),
        (float("nan"), 0.0),
        (float("inf"), 0.0),
        (float("-inf"), 0.0),
        ("not-a-score", 0.0),
        (True, 0.0),
    ],
)
def test_source_history_payload_sanitizes_scores(score, expected):
    payload = source_history_payload({"name": "guide.md", "score": score})

    assert payload["score"] == expected


def test_source_history_payload_accepts_numeric_score_strings():
    payload = source_history_payload({"name": "guide.md", "score": "0.4"})

    assert payload["score"] == 0.4
