from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Any

from mentors_data import RAW_MENTORS, REQUIRED_FIELDS


@dataclass(frozen=True)
class DiagnosticIssue:
    mentor_index: int
    mentor_id: Any
    field: str
    message: str


def diagnose_mentors(mentors: Iterable[Any]) -> list[DiagnosticIssue]:
    issues: list[DiagnosticIssue] = []
    first_index_by_id: dict[int, int] = {}

    for index, mentor in enumerate(mentors, start=1):
        if not isinstance(mentor, Mapping):
            issues.append(
                DiagnosticIssue(index, None, "<mentor>", "must be a mapping/dictionary")
            )
            continue

        mentor_id = mentor.get("id")
        if "id" not in mentor or mentor_id is None or mentor_id == "":
            issues.append(DiagnosticIssue(index, mentor_id, "id", "is required"))
        elif isinstance(mentor_id, bool) or not isinstance(mentor_id, int):
            issues.append(DiagnosticIssue(index, mentor_id, "id", "must be an integer"))
        elif mentor_id < 1:
            issues.append(DiagnosticIssue(index, mentor_id, "id", "must be positive"))
        elif mentor_id in first_index_by_id:
            issues.append(
                DiagnosticIssue(
                    index,
                    mentor_id,
                    "id",
                    f"is duplicated from mentor #{first_index_by_id[mentor_id]}",
                )
            )
        else:
            first_index_by_id[mentor_id] = index

        for field in REQUIRED_FIELDS:
            if field not in mentor:
                if field != "id":
                    issues.append(
                        DiagnosticIssue(index, mentor_id, field, "is required")
                    )
                continue

            if field in ("id", "experience_years"):
                continue

            value = mentor[field]
            if value is None or (isinstance(value, str) and not value.strip()):
                issues.append(
                    DiagnosticIssue(index, mentor_id, field, "must not be empty")
                )
            elif isinstance(value, (list, tuple, set, frozenset)) and not value:
                issues.append(
                    DiagnosticIssue(index, mentor_id, field, "must not be empty")
                )

        for field in ("name", "title", "company", "field", "bio"):
            value = mentor.get(field)
            if value is not None and not isinstance(value, str):
                issues.append(
                    DiagnosticIssue(index, mentor_id, field, "must be a string")
                )

        for field in ("strengths", "available_for"):
            value = mentor.get(field)
            if value is None:
                continue
            if isinstance(value, str):
                continue
            if not isinstance(value, (list, tuple, set, frozenset)):
                issues.append(
                    DiagnosticIssue(index, mentor_id, field, "must be a string or list")
                )
            elif any(not isinstance(item, str) or not item.strip() for item in value):
                issues.append(
                    DiagnosticIssue(
                        index,
                        mentor_id,
                        field,
                        "must contain only non-empty strings",
                    )
                )

        if "experience_years" in mentor:
            experience = mentor["experience_years"]
            if not isinstance(experience, int) or isinstance(experience, bool):
                issues.append(
                    DiagnosticIssue(
                        index,
                        mentor_id,
                        "experience_years",
                        "must be an integer",
                    )
                )
            elif experience < 0:
                issues.append(
                    DiagnosticIssue(
                        index,
                        mentor_id,
                        "experience_years",
                        "must be zero or greater",
                    )
                )

    return issues


def format_diagnostic_report(issues: Iterable[DiagnosticIssue]) -> str:
    issue_list = list(issues)
    if not issue_list:
        return "Mentor data quality check: PASS (0 issues)."

    lines = [
        f"Mentor data quality check: FAIL ({len(issue_list)} issue(s) found)."
    ]
    for issue in issue_list:
        mentor = f"mentor #{issue.mentor_index}"
        if issue.mentor_id is not None:
            mentor += f" (id={issue.mentor_id})"
        lines.append(f"- {mentor} — {issue.field}: {issue.message}")
    return "\n".join(lines)


def main() -> int:
    issues = diagnose_mentors(RAW_MENTORS)
    print(format_diagnostic_report(issues))
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
