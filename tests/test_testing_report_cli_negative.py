"""Negative CLI tests: testing_report must fail closed on invalid JUnit evidence."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[1]


def _coverage_xml(path: Path) -> Path:
    path.write_text(
        '<coverage lines-valid="10" lines-covered="7"></coverage>',
        encoding="utf-8",
    )
    return path


def _run_cli(tmp_path: Path, junit: Path, coverage: Path) -> subprocess.CompletedProcess[str]:
    output = tmp_path / "execution-report.md"
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.testing_report",
            "--junit",
            str(junit),
            "--coverage",
            str(coverage),
            "--output",
            str(output),
        ],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def _assert_fail_closed(result: subprocess.CompletedProcess[str], report: Path) -> None:
    assert result.returncode != 0, result.stdout + result.stderr
    assert report.is_file()
    report_text = report.read_text(encoding="utf-8")
    assert "PASS" not in report_text
    assert "NOT VERIFIED" in report_text or "FAIL" in report_text


def test_missing_junit_exits_nonzero_and_does_not_report_pass(tmp_path: Path) -> None:
    junit = tmp_path / "missing-junit.xml"
    coverage = _coverage_xml(tmp_path / "coverage.xml")

    result = _run_cli(tmp_path, junit, coverage)

    _assert_fail_closed(result, tmp_path / "execution-report.md")
    assert "JUnit XML missing" in (tmp_path / "execution-report.md").read_text(encoding="utf-8")


def test_malformed_junit_xml_exits_nonzero_and_does_not_report_pass(tmp_path: Path) -> None:
    junit = tmp_path / "broken-junit.xml"
    junit.write_text("<testsuite><testcase>", encoding="utf-8")
    coverage = _coverage_xml(tmp_path / "coverage.xml")

    result = _run_cli(tmp_path, junit, coverage)

    _assert_fail_closed(result, tmp_path / "execution-report.md")
    assert "Invalid evidence XML" in result.stdout


def test_zero_tests_exits_nonzero_and_does_not_report_pass(tmp_path: Path) -> None:
    junit = tmp_path / "zero-tests.xml"
    junit.write_text('<testsuite tests="0" failures="0" errors="0" skipped="0"></testsuite>', encoding="utf-8")
    coverage = _coverage_xml(tmp_path / "coverage.xml")

    result = _run_cli(tmp_path, junit, coverage)

    _assert_fail_closed(result, tmp_path / "execution-report.md")
    assert "zero tests executed" in (tmp_path / "execution-report.md").read_text(encoding="utf-8")


def test_one_failed_test_exits_nonzero_and_does_not_report_pass(tmp_path: Path) -> None:
    junit = tmp_path / "one-failure.xml"
    junit.write_text(
        '<testsuite tests="1" failures="1" errors="0" skipped="0"></testsuite>',
        encoding="utf-8",
    )
    coverage = _coverage_xml(tmp_path / "coverage.xml")

    result = _run_cli(tmp_path, junit, coverage)

    _assert_fail_closed(result, tmp_path / "execution-report.md")
    report_text = (tmp_path / "execution-report.md").read_text(encoding="utf-8")
    assert "FAIL" in report_text
    assert "failures: 1" in report_text
