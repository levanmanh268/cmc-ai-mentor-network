"""Reporter must never present missing or failed evidence as successful."""
from pathlib import Path
from scripts.testing_report import summarize_junit, summarize_coverage, build_report
import scripts.testing_report as reporter


def test_evidence_report_parses_junit_and_coverage(tmp_path):
    junit = tmp_path / "junit.xml"
    junit.write_text(
        '<testsuites><testsuite tests="4" errors="0" failures="1" skipped="1">'
        '<testcase name="a"/><testcase name="b"/></testsuite></testsuites>',
        encoding="utf-8",
    )
    coverage = tmp_path / "coverage.xml"
    coverage.write_text('<coverage lines-valid="200" lines-covered="150"/>', encoding="utf-8")
    totals = summarize_junit(junit)
    assert totals == {"tests": 4, "failures": 1, "errors": 0, "skipped": 1, "passed": 2}
    percent, covered, total = summarize_coverage(coverage)
    assert (percent, covered, total) == (75.0, 150, 200)
    report = build_report(totals, (percent, covered, total), sha="abc", repo="x/y", run_id="12")
    assert "FAIL" in report
    assert "75.00%" in report
    assert "https://github.com/x/y/actions/runs/12" in report


def test_evidence_report_never_fakes_missing_xml(tmp_path):
    assert summarize_junit(tmp_path / "missing.xml") is None
    assert summarize_coverage(tmp_path / "missing.xml") is None
    report = build_report(None, None, sha="", repo="", run_id="")
    assert "NOT VERIFIED" in report
    assert "PASS —" not in report


def test_report_sha_markdown_and_separate_chromium_evidence():
    totals = {"tests": 1, "failures": 0, "errors": 0, "skipped": 0, "passed": 1}
    report = build_report(totals, (100.0, 1, 1), sha="abc123", repo="group6/app", run_id="42")
    assert "- **Commit SHA:** `abc123`" in report
    assert r"\`" not in report
    assert "Local Chromium browser E2E" in report
    assert "Public cloud browser UAT" in report



def test_skipped_cases_are_never_counted_as_passed(tmp_path):
    junit = tmp_path / "junit.xml"
    junit.write_text(
        '<testsuites><testsuite tests="3" failures="0" errors="0" skipped="1">'
        '<testcase name="pass"/><testcase name="skip"><skipped/></testcase>'
        '<testcase name="pass2"/></testsuite></testsuites>',
        encoding="utf-8",
    )
    totals = summarize_junit(junit)
    assert totals == {"tests": 3, "failures": 0, "errors": 0, "skipped": 1, "passed": 2}
    report = build_report(totals, None, sha="abc", repo="x/y", run_id="12")
    assert "- passed: 2" in report
    assert "- skipped: 1" in report
    assert "skipped cases are reported separately" in report


@pytest.mark.parametrize(
    ("xml_content", "expected_text"),
    [
        (None, "JUnit XML missing"),
        ("<testsuites><broken></testsuites>", "NOT VERIFIED"),
        ('<testsuites><testsuite tests="0" failures="0" errors="0" skipped="0"/></testsuites>', "zero tests executed"),
        ('<testsuites><testsuite tests="2" failures="0" errors="0" skipped="2"/></testsuites>', "zero tests executed"),
    ],
)
def test_report_cli_fails_closed_for_missing_corrupt_zero_or_all_skipped_junit(
    tmp_path, monkeypatch, xml_content, expected_text
):
    junit = tmp_path / "junit.xml"
    coverage = tmp_path / "coverage.xml"
    output = tmp_path / "report.md"
    if xml_content is not None:
        junit.write_text(xml_content, encoding="utf-8")
    monkeypatch.setattr(
        "sys.argv",
        ["testing_report", "--junit", str(junit), "--coverage", str(coverage), "--output", str(output)],
    )
    assert reporter.main() == 1
    report = output.read_text(encoding="utf-8")
    assert expected_text in report
    assert "PASS —" not in report
