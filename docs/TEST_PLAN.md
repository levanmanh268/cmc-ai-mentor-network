# Test Plan | CMC AI Mentor Network

**Scope owner:** Lê Hải Đăng — Testing / CI-CD  
**Environment:** Python 3.11; deterministic offline tests; no real API key required.  
**Evidence rule:** every PASS must reference the exact commit SHA and GitHub Actions run. Fake-provider tests do not prove live Groq availability or public-cloud UAT.

## 1. Scope and acceptance criteria

- Regression coverage for empty knowledge base, empty/irrelevant queries, invalid mentor profile fields, LLM/provider failures and offline fallback.
- API/LLM contract coverage uses fake clients/mocks only: authentication, permission, rate-limit, server, timeout, network, blank-response and secret-redaction paths.
- CI must fail closed when JUnit evidence is missing, malformed, empty, entirely skipped, or contains failures/errors.
- No real provider credential is committed, printed, or required by offline tests.
- Linux/Windows CI and Chromium local-app E2E evidence are tied to the exact tested SHA.
- Branch-protection settings are an owner/maintainer decision; this work does not change repository settings.

## 2. Regression matrix

| Area | Scenario | Expected result | Existing automated evidence |
| --- | --- | --- | --- |
| RAG | Knowledge base missing/empty | `no-evidence`, no provider call | `tests/test_quality_gates.py::test_qg10_empty_kb_never_calls_provider` |
| RAG | Empty/whitespace/punctuation/out-of-domain query | `no-evidence`, no provider call | `test_qg11_no_evidence_rejects_unsupported_queries` |
| RAG | Unsupported citation ID | Offline fallback; do not trust invented citation | QG-13/QG-14 |
| RAG | Provider raises exception | Preserve offline sources; redact exception/secret | QG-15 |
| Mentor/profile | Required field empty or over limit | Validation error; no invalid save | QG-17/QG-18 |
| LLM | Missing/placeholder key | Explicit unavailable state; no fake success | `tests/test_llm_client.py`, `tests/test_real_ai_chat.py` |
| LLM | HTTP 400/401/403/404/429/500/502/503/504 | Sanitized user-facing error; no secret leakage | QG-06 |
| LLM | Timeout/network/generic exception | Fail closed and redact provider exception | QG-07 |
| LLM | Blank response / oversized response | Error for blank; bounded output for long response | QG-08/QG-09 |
| LLM | Multi-turn history and unsafe roles | Preserve bounded user/assistant context; reject unsafe input | QG-01/QG-03/QG-04; `tests/test_real_ai_chat.py` |
| LLM client | Timeout and SDK retry bounds | Timeout 35s and one SDK retry configured | `tests/test_llm_client.py::test_groq_client_has_bounded_timeout_and_sdk_retry` |
| Consent/privacy | Server key exists but consent off | No provider call; UI remains disabled | `tests/test_final_defense_probe.py` |
| Reporter | Missing/corrupt/zero/all-skipped JUnit | Non-zero exit; never report PASS | `tests/test_testing_report.py` |
| Reporter | Mixed pass/skip/fail cases | Keep passed/skipped/fail counts distinct | `tests/test_testing_report.py` |
| Browser | Local Chromium UI startup, mentor flow, RAG and consent | Browser assertions recorded in JUnit; screenshots/traces on failure | `e2e/browser_spec.py` and CI `browser-e2e` job |

QG-01..QG-25 are deterministic contracts in `tests/test_quality_gates.py`. The table names representative cases; parameterized inputs produce more pytest cases than matrix rows.

## 3. API/LLM test-gap review (Issue #82)

Compared with `tests/test_quality_gates.py`, `tests/test_final_defense_probe.py`, and `tests/test_real_ai_chat.py`:

- Covered offline/mocked: missing credentials, placeholder credentials, multi-turn payload, invalid roles/history, context limits, consent-off no-call, sanitized 400/401/403/404/429/500/502/503/504 errors, timeout/network/generic exceptions, blank response, output bounds, and RAG fallback.
- Client construction is tested for bounded timeout (35 seconds) and SDK retry configuration (one retry); this asserts configuration, not a real retry against Groq.
- No real API key or live network request is used by these tests.
- **LIVE Groq inference: BLOCKED / NOT VERIFIED** until an authorized tester supplies their own private credential, explicitly consents, and records a redacted successful provider response.
- Public deployed-service UAT remains **NOT RUN** unless a tester records date, URL, browser/device, exact SHA, expected/actual result and redacted evidence.

## 4. CI configuration audit (Issues #78 / #86)

| Check | Configuration / finding |
| --- | --- |
| Triggers | Push to `main`; pull requests targeting `main`. |
| Python runtime | Python 3.11 on Ubuntu and Windows runners. |
| Linux regression | Compile smoke check, secret-pattern guard, pytest/JUnit, scoped coverage, Markdown report, offline diagnostics/RAG evaluation, Streamlit health. |
| Windows regression | Pytest/JUnit, scoped coverage and Markdown report; Streamlit HTTP health check. |
| Browser | Ubuntu + Playwright Chromium; JUnit, Markdown report, screenshots/traces on failure. This tests local CI app, not public Render UAT. |
| Mermaid | Pinned Mermaid CLI 10.9.1 and 11.17.0 validation/render jobs. |
| Secrets | Test jobs set `GROQ_API_KEY` empty; tests use fakes. Never put credentials in repository, artifacts, issue comments or screenshots. |
| Permissions | Workflow-level `contents: read`; no write permission is needed for test jobs. |
| Artifacts | Linux, Windows and Chromium evidence uploaded with 30-day retention; artifacts are valid only for their associated SHA/run. |
| Fail visibility | Reporter rejects missing, malformed, zero-test, all-skipped, failed or errored JUnit. `if: always()` preserves report/upload attempts after test failures. |
| Branch protection | Not changed. Repository owner/maintainer must approve required check names and branch rules. |

## 5. Reproduce locally

```bash
python -m pip install -r requirements.txt
python -m pip install "pytest-cov>=6,<8"
python -m py_compile app.py general_chat.py chat_intents.py ui_helpers.py profile_helpers.py llm_client.py rag_engine.py matching_engine.py mentors_data.py mentor_data_diagnostics.py ingest.py scripts/evaluate_rag.py scripts/final_smoke_audit.py
python -m pytest -q --junitxml=reports/junit-local.xml --cov=general_chat --cov=rag_engine --cov=matching_engine --cov=profile_helpers --cov=llm_client --cov=chat_intents --cov=ui_helpers --cov-report=xml:reports/coverage-local.xml
python -m scripts.testing_report --junit reports/junit-local.xml --coverage reports/coverage-local.xml --output reports/TEST_EXECUTION_REPORT-local.md
python -m scripts.evaluate_rag
python -m scripts.final_smoke_audit
```

For browser E2E:

```bash
python -m pip install "pytest-playwright>=0.6,<1"
python -m playwright install chromium
python -m pytest -q e2e/browser_spec.py --browser chromium --junitxml=reports/junit-browser.xml
```

## 6. Evidence and release handoff

Record for every run: workflow URL, full commit SHA, job name, conclusion, artifact names, test totals (passed/failed/errors/skipped), and any blocked/not-run manual checks. Do not infer PASS from a green unrelated commit or from skipped tests.

- **PASS:** test executed and assertions succeeded at the referenced SHA.
- **FAIL:** assertion/job failed; retain traceback and artifact.
- **SKIPPED:** reported separately; never counted as passed.
- **BLOCKED:** provider, secret, permission or external dependency unavailable.
- **NOT RUN:** no execution evidence exists.

Manual UAT checklist and live-provider evidence must be completed by an authorized human tester. Do not claim the project is bug-free, that live Groq works, or that public-cloud/browser UAT passed based only on offline tests.
