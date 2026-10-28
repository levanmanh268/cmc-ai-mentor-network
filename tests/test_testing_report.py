"""Reporter must never present missing or failed evidence as successful."""
from pathlib import Path
from scripts.testing_report import summarize_junit, summarize_coverage, build_report


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
