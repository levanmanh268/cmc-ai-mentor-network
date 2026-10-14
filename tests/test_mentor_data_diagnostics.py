from mentor_data_diagnostics import (
    diagnose_mentors,
    format_diagnostic_report,
)
from mentors_data import RAW_MENTORS


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


def test_diagnose_current_mentor_data_passes_without_changing_it():
    original = [dict(mentor) for mentor in RAW_MENTORS]

    assert diagnose_mentors(RAW_MENTORS) == []
    assert RAW_MENTORS == original


def test_diagnose_reports_duplicate_ids_and_required_values():
    issues = diagnose_mentors(
        [
            _mentor(),
            _mentor(id=1, name="  ", company=None, field=""),
        ]
    )

    assert [(issue.mentor_index, issue.field) for issue in issues] == [
        (2, "id"),
        (2, "name"),
        (2, "company"),
        (2, "field"),
    ]
    report = format_diagnostic_report(issues)
    assert "FAIL (4 issue(s) found)" in report
    assert "is duplicated from mentor #1" in report
    assert "mentor #2 (id=1)" in report


def test_diagnose_reports_missing_fields_and_non_mapping_records():
    issues = diagnose_mentors([{"id": 2, "name": "Mentor B"}, None])

    assert [(issue.mentor_index, issue.field) for issue in issues] == [
        (1, "title"),
        (1, "company"),
        (1, "field"),
        (1, "experience_years"),
        (1, "bio"),
        (1, "strengths"),
        (1, "available_for"),
        (2, "<mentor>"),
    ]


def test_diagnose_rejects_invalid_required_field_types_and_list_items():
    issues = diagnose_mentors(
        [
            _mentor(name=7, strengths=["RAG", " "]),
            _mentor(id=2, available_for=42),
        ]
    )

    assert [(issue.mentor_id, issue.field) for issue in issues] == [
        (1, "name"),
        (1, "strengths"),
        (2, "available_for"),
    ]


def test_diagnose_rejects_invalid_experience_type_and_negative_values():
    issues = diagnose_mentors(
        [
            _mentor(experience_years="4"),
            _mentor(id=2, experience_years=-1),
            _mentor(id=3, experience_years=True),
        ]
    )

    assert [
        (issue.mentor_id, issue.message)
        for issue in issues
        if issue.field == "experience_years"
    ] == [
        (1, "must be an integer"),
        (2, "must be zero or greater"),
        (3, "must be an integer"),
    ]


def test_diagnose_handles_empty_data_and_zero_year_experience():
    assert format_diagnostic_report(diagnose_mentors([])) == (
        "Mentor data quality check: PASS (0 issues)."
    )
    assert diagnose_mentors([_mentor(experience_years=0)]) == []
