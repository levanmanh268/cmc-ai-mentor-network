# Dependency Audit Report

**Date:** 2026-10-30  
**Tool:** `pip-audit 2.10.1`  
**Scope:** installed local virtualenv after installing `requirements-test.txt` (root runtime, test, and optional API/document requirements). This is not a scan of every portfolio lab's separate optional dependencies.

## Findings and remediation

The first local scan found six advisory records affecting two installed packages. The duplicate entries represent aliases/advisory records for the same underlying issues:

| Package before fix | Advisory | Patched version | Change |
| --- | --- | --- | --- |
| `pytest 8.4.2` | [GHSA-6w46-j5rx-g56g / CVE-2025-71176](https://github.com/advisories/GHSA-6w46-j5rx-g56g) | `9.0.3` | `requirements.txt` now requires `pytest>=9.0.3,<10` |
| `pip 26.1.1` | [GHSA-wf93-45jw-7689 / CVE-2026-8643](https://github.com/advisories/GHSA-wf93-45jw-7689); [GHSA-qwm4-qh6w-59xr / CVE-2026-13346](https://github.com/advisories/GHSA-qwm4-qh6w-59xr) | `26.2.0` or later | CI install steps now require `pip>=26.2` |

The current local environment was upgraded to `pytest 9.2.0` and `pip 26.2.2`. Re-running:

```bash
python -m pip_audit --local --strict --format json
```

returned **No known vulnerabilities found** (exit code 0).

## Ongoing automated check

`.github/workflows/dependency-audit.yml` audits the installed test/runtime environment on pull requests, pushes to `main`, manual dispatch, and weekly schedule. The first GitHub Actions run for the change is still needed to verify CI's Python 3.11 resolution and publish its JSON artifact. Update dependencies and re-run the audit when a future scan reports an advisory.
