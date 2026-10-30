"""Generate a concise CI execution report from machine-generated test evidence.

Never labels absent/malformed reports as PASS. JUnit counts are from pytest,
coverage percentage is line coverage of explicitly selected modules only.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import xml.etree.ElementTree as ET


def summarize_junit(xml_path: Path) -> dict[str, int] | None:
    if not xml_path.is_file():
        return None
    root = ET.parse(xml_path).getroot()
    suites = [root] if root.tag == "testsuite" else list(root.iter("testsuite"))
    if not suites:
        return None
    keys = ("tests", "failures", "errors", "skipped")
    totals = {key: sum(int(suite.attrib.get(key, 0)) for suite in suites) for key in keys}
    totals["passed"] = max(0, totals["tests"] - totals["failures"] - totals["errors"] - totals["skipped"])
    return totals


def summarize_coverage(xml_path: Path) -> tuple[float, int, int] | None:
    if not xml_path.is_file():
        return None
    root = ET.parse(xml_path).getroot()
    if root.tag != "coverage":
        return None
    total = int(root.attrib.get("lines-valid", 0))
    covered = int(root.attrib.get("lines-covered", 0))
    if total <= 0:
        return None
    return round(100 * covered / total, 2), covered, total


def build_report(
    junit: dict[str, int] | None,
    coverage: tuple[float, int, int] | None,
    *,
    sha: str,
    repo: str,
    run_id: str,
) -> str:
    if junit is None:
        verdict = "NOT VERIFIED — JUnit output unavailable"
    elif junit["failures"] or junit["errors"]:
        verdict = "FAIL — test failures/errors present"
    elif junit["tests"] == 0:
        verdict = "NOT VERIFIED — zero tests executed"
    else:
        verdict = "PASS — executed pytest cases (does not include live Groq/UAT)"
    url = f"https://github.com/{repo}/actions/runs/{run_id}" if repo and run_id else "Not available"
    lines = [
        "# Automated Test Execution Evidence | Group 6",
        "",
        f"- **Pytest verdict:** {verdict}",
        f"- **Commit SHA:** `{sha or 'NOT SET'}`",
        f"- **GitHub Actions run:** {url}",
        "- **Evidence source:** JUnit XML and Coverage.py XML, generated in this job.",
        "",
        "## Pytest results",
    ]
    if junit is None:
        lines.append("JUnit XML missing; **no test-pass claim can be made**.")
    else:
        for key in ("tests", "passed", "failures", "errors", "skipped"):
            lines.append(f"- {key}: {junit[key]}")
    lines += ["", "## Source-line coverage"]
    if coverage is None:
        lines.append("Coverage XML missing; **coverage not measured**.")
    else:
        percent, covered, total = coverage
        lines.append(f"- Covered: **{covered}/{total} lines ({percent:.2f}%)**")
        lines.append("- Scope: named core Python modules in CI command; **not** all files, branches, browsers or live model output.")
    lines += [
        "",
        "## Scope / outstanding acceptance",
        "- Automated pytest + Streamlit AppTest: regression, fake-provider, retrieval and matching.",
        "- In GitHub Actions, Linux/Windows CI and Mermaid/render health have separate job results; this local report has no remote run link.",
        "- Local Chromium browser E2E is reported separately by the browser-e2e CI job and its own JUnit artifact; not included in this pytest report.",
        "- Public cloud browser UAT, accessibility, penetration, load and multi-user cloud testing: NOT VERIFIED by this report.",
        "- **Live Groq inference: NOT VERIFIED** unless separately proved on deployed service with private key, explicit consent and provider response.",
        "- A valid [S1] citation tests membership only, **not semantic groundedness**.",
        "- Check UAT manually and record screenshots with secrets/redacted personal data.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--junit", type=Path, default=Path("reports/junit.xml"))
    parser.add_argument("--coverage", type=Path, default=Path("reports/coverage.xml"))
    parser.add_argument("--output", type=Path, default=Path("reports/TEST_EXECUTION_REPORT.md"))
    args = parser.parse_args()
    try:
        junit = summarize_junit(args.junit)
        coverage = summarize_coverage(args.coverage)
    except (ET.ParseError, ValueError, OSError) as error:
        print(f"Invalid evidence XML: {type(error).__name__}")
        junit, coverage = None, None
    report = build_report(
        junit, coverage,
        sha=os.getenv("GITHUB_SHA", ""),
        repo=os.getenv("GITHUB_REPOSITORY", ""),
        run_id=os.getenv("GITHUB_RUN_ID", ""),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(report, encoding="utf-8")
    print(report)
    return 1 if junit is None or junit["tests"] == 0 or junit["failures"] or junit["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
