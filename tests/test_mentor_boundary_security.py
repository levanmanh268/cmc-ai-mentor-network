from mentor_data_diagnostics import diagnose_mentors


def _mentor(**overrides):
    mentor = {
        "id": 1,
        "name": "Mentor Test",
        "title": "AI Engineer",
        "company": "Demo",
        "field": "NLP",
        "experience_years": 4,
        "bio": "AI mentor",
        "strengths": ["RAG"],
        "available_for": ["Project"],
    }
    mentor.update(overrides)
    return mentor


def _issues(mentor):
    return [
        (issue.mentor_index, issue.mentor_id, issue.field, issue.message)
        for issue in diagnose_mentors([mentor])
    ]


def test_diagnose_reports_duplicate_mentor_id():
    issues = diagnose_mentors([_mentor(), _mentor()])

    assert [
        (issue.mentor_index, issue.mentor_id, issue.field, issue.message)
        for issue in issues
    ] == [(2, 1, "id", "is duplicated from mentor #1")]


def test_diagnose_rejects_boolean_mentor_id():
    assert _issues(_mentor(id=True)) == [
        (1, True, "id", "must be an integer")
    ]


def test_diagnose_rejects_negative_experience():
    assert _issues(_mentor(experience_years=-1)) == [
        (1, 1, "experience_years", "must be zero or greater")
    ]


def test_diagnose_reports_missing_required_field():
    mentor = _mentor()
    del mentor["bio"]

    assert _issues(mentor) == [(1, 1, "bio", "is required")]


def test_diagnose_rejects_blank_strength_item():
    assert _issues(_mentor(strengths=["RAG", "  "])) == [
        (1, 1, "strengths", "must contain only non-empty strings")
    ]
