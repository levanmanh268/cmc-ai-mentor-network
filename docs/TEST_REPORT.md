# Automated Test Execution Evidence | Group 6

- **Pytest verdict:** PASS — executed pytest cases (does not include live Groq/UAT)
- **Commit SHA:** `962d125c5a412a5eb607ca117ef4a86bb0f35d36 (modified working tree)`
- **GitHub Actions run:** Not available
- **Evidence source:** JUnit XML and Coverage.py XML, generated in this job.

## Pytest results
- tests: 411
- passed: 410
- failures: 0
- errors: 0
- skipped: 1

## Source-line coverage
- Covered: **419/433 lines (96.77%)**
- Scope: named core Python modules in CI command; **not** all files, branches, browsers or live model output.

## Scope / outstanding acceptance
- Automated pytest + Streamlit AppTest: regression, fake-provider, retrieval and matching.
- In GitHub Actions, Linux/Windows CI and Mermaid/render health have separate job results; this local report has no remote run link.
- Local Chromium browser E2E is reported separately by the browser-e2e CI job and its own JUnit artifact; not included in this pytest report.
- Public cloud browser UAT, accessibility, penetration, load and multi-user cloud testing: NOT VERIFIED by this report.
- **Live Groq inference: NOT VERIFIED** unless separately proved on deployed service with private key, explicit consent and provider response.
- A valid [S1] citation tests membership only, **not semantic groundedness**.
- Check UAT manually and record screenshots with secrets/redacted personal data.

## Local verification details (2026-10-30, Asia/Saigon)

**Environment:** Windows 11, Python 3.14.5, `pip 26.2.2`, `pytest 9.2.0`, full `requirements-test.txt`. Tested tree is based on commit `962d125c5a412a5eb607ca117ef4a86bb0f35d36` with uncommitted modifications; this is the base commit, not a commit containing the changes below.

### Test execution

- Command: `python -m pytest -q -rs --junitxml=<temp>/cmc-junit-final.xml --cov=general_chat --cov=rag_engine --cov=matching_engine --cov=profile_helpers --cov=llm_client --cov=chat_intents --cov=ui_helpers --cov-report=term-missing --cov-report=xml:<temp>/cmc-coverage-final.xml --cov-fail-under=90`
- Console summary: **350 test functions passed, 60 subtests passed, 1 skipped, 0 failed**, 37.20 seconds. JUnit records 411 total cases: 410 passed, 1 skipped.
- The single skip is `tests/test_rag_engine.py::test_symlink_escape_is_not_indexed`, because this Windows environment cannot create symlinks.
- One upstream deprecation warning: Starlette TestClient currently uses `httpx`; it recommends `httpx2`.
- Scoped source-line coverage: **419/433 (96.77%)**, above the configured 90% CI floor. This is line coverage for seven selected modules, not branch or whole-repository coverage.

### Other checks

- `python -m scripts.evaluate_rag`: Recall@3 **9/9**, citation correctness **10/10**, answer evidence proxy **9/9**, out-of-scope refusal **5/5**.
- `python -m scripts.final_smoke_audit`: 100 warm samples per operation. RAG supported query P50/P95 **0.520/1.005 ms**; RAG refusal **0.011/0.011 ms**; mentor ranking **1.366/2.064 ms**.
- `python -m scripts.benchmark_scaling --samples 100`: RAG P50/P95 at 3/30/100 docs: **0.484/0.752**, **0.508/0.736**, **0.599/1.569 ms**. Mentor ranking at 10/100/500 records: **1.537/3.164**, **5.369/9.203**, **84.827/121.798 ms**.
- Core Ruff check: **PASS**. Python `py_compile`: **PASS**. Local Streamlit `/_stcore/health`: HTTP **200**. `git diff --check`: **PASS**.
- Dependency scan: `python -m pip_audit --local --strict --format json` — **No known vulnerabilities found** after upgrading `pip` and `pytest`; see [DEPENDENCY_AUDIT_REPORT.md](DEPENDENCY_AUDIT_REPORT.md).

Performance figures are warm local measurements on synthetic/demo data, not a cloud or concurrency SLA. RAG quality figures are in-sample and do not establish live LLM semantic accuracy.

### Not verified by this local run

- GitHub Actions for the modified tree, Linux behavior, browser E2E, or artifact retention.
- Required PR checks/branch protection: no repository rulesets were visible to this integration, and branch-protection details were not accessible.
- Human UAT, reviewer approval, live Groq inference, confirmation that the historical key was revoked, and exact textbook-chapter alignment.
