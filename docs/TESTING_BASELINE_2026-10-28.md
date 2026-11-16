# Initial Testing Baseline

**Project:** CMC AI Mentor Network  
**Baseline date:** 2026-10-28  
**Scope:** Streamlit application, repository test suites, and the configured GitHub Actions CI workflow.  
**Evidence rule:** A status is PASS only when tied to an observed test run and commit. Local checks that could not execute are marked BLOCKED, not PASS.

## Executive Summary

The latest observed CI run for `main` completed successfully: [CI run #172, commit `a43979f`](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/40617273185). The run reports green Linux `test`, Windows `windows-local`, Chromium browser E2E, and both Mermaid CLI matrix jobs. The Linux job includes the configured Python compile smoke check and regression suite.

A fresh local run of `python -m pytest -q` and a local Python compile check could not be performed in this workspace. The `python` command resolves to the Windows app-execution alias, and `py -3 --version` fails because its configured interpreter (`E:\python3.14t.exe`) is missing. Therefore, the remote CI result is a baseline for commit `a43979f`, not proof that the current local working tree has been tested.

## Test Structure and Existing Coverage Map

- The root `tests/` directory contains 24 Python test modules covering chat intents, LLM behavior, matching, profile validation, RAG, UI flows, release gates, diagnostics, and evidence-report generation.
- Test functions in those root modules cover unit, integration, and in-process Streamlit `AppTest` flows. Parameterized functions may produce multiple pytest cases; the source-level function count is not the collected case count.
- Additional test suites live under `cagent_lab/tests/`, `edu_trainer_ai/tests/`, `enterprise_doc_ai/tests/`, `model_pretraining_lab/tests/`, `model_posttraining_lab/tests/`, and `retail_ops_ai/tests/`.
- `e2e/browser_spec.py` is the dedicated real-browser suite. It is run separately by CI with Chromium and is not included by pytest's default `test_*.py` collection pattern.
- [TESTING_HANDOFF.md](TESTING_HANDOFF.md) contains a 39-row traceability matrix, the test strategy, local commands, and known limits. It explicitly records manual UAT as NOT RUN and real Groq acceptance as NOT VERIFIED until evidence exists.

The repository has broad automated coverage for the main application and several independent labs. This baseline does not claim that every requirement, deployment configuration, provider integration, or user workflow has been tested.

## CI Configuration and Latest Observed Run

The workflow at [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) runs on pushes and pull requests targeting `main`. It uses Python 3.11 and includes:

- Linux dependencies, secret-pattern guard, Python `py_compile` smoke check, pytest with JUnit and scoped coverage output, evidence-report generation, offline diagnostics/RAG evaluation, and Streamlit health smoke.
- Windows pytest/JUnit and Streamlit HTTP health smoke.
- Mermaid rendering against CLI versions 10.9.1 and 11.17.0.
- Chromium browser E2E against a local Streamlit instance, with failure screenshots/traces and JUnit output.
- CI artifacts for JUnit, coverage/report evidence, Windows JUnit, and browser results where produced.

| CI check | Status | Evidence |
| --- | --- | --- |
| Linux `test` job, including compile smoke and regression tests | PASS | [Run #172](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/40617273185), commit `a43979f` |
| Windows unit/UI and Streamlit startup | PASS | `windows-local` job in [run #172](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/40617273185) |
| Mermaid CLI 10.9.1 and 11.17.0 | PASS | Both matrix jobs in [run #172](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/40617273185) |
| Chromium real-localhost browser E2E | PASS | `Chromium browser E2E` job in [run #172](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/40617273185) |
| Full run | PASS | Completed successfully in 1m 39s; 3 artifacts reported by GitHub |

The observed run summary shows all listed jobs green. Exact pytest collected/passed/skipped counts and coverage percentages are not stated in the summary snapshot and were not independently read from the downloadable JUnit/coverage artifacts. They are intentionally not inferred here.

## Status Classification

| Area | Status | Notes |
| --- | --- | --- |
| Latest remote automated CI at commit `a43979f` | PASS | Run #172 completed successfully across the observed jobs. |
| Local `python -m pytest -q` | BLOCKED | Python runtime unavailable; command did not execute. This is not a test failure. |
| Local Python syntax/compile check | BLOCKED | No working local Python interpreter. Remote CI compile smoke passed for the configured module list. |
| Pytest skipped count | NOT VERIFIED | Requires JUnit or full pytest output; do not assume zero skips. |
| Manual UAT against the deployed application | NOT RUN / NOT VERIFIED | Follow the UAT checklist and attach tester, environment, date, and results. |
| Live Groq/provider acceptance | NOT RUN / NOT VERIFIED | CI deliberately clears `GROQ_API_KEY`; fake-provider tests do not prove live provider behavior. |
| Coverage percentage and exact collected-case totals | NOT VERIFIED | Retrieve the run's coverage and JUnit artifacts before publishing numerical claims. |
| Untested requirements | PARTIAL / NOT FULLY MAPPED | The handoff matrix documents 39 test objectives; each product requirement still needs evidence mapping and review. |

No FAIL result was visible in the latest observed run. This does not establish that no tests were skipped or that all requirements are covered.

## Risks and Follow-up

1. Restore/install a supported local Python 3.11 environment, then rerun the documented pytest and compile commands from the repository root.
2. Download the JUnit and coverage artifacts for run #172 and record exact collected, passed, failed, skipped, and coverage figures, tied to the artifact's commit SHA.
3. Run and document the manual UAT and live-provider acceptance separately; do not mix these with offline or mocked CI evidence.
4. Review the CI annotation for `actions/upload-artifact@v4`: GitHub reports that this action targets deprecated Node.js 20 and is being forced onto Node.js 24. Track an update to a supported action version and confirm compatibility.
5. Keep future reports tied to a specific commit and CI run; rerun the baseline after material test or workflow changes.

## Reproduction Commands

Run from the repository root after installing the project's dependencies:

```powershell
python -m pytest -q
python -m py_compile general_chat.py chat_intents.py app.py ui_helpers.py profile_helpers.py llm_client.py rag_engine.py matching_engine.py mentors_data.py mentor_data_diagnostics.py ingest.py scripts/evaluate_rag.py scripts/final_smoke_audit.py
```

## Revalidation 2026-11-03

This section updates the baseline with newer remote CI and cloud observations without rewriting the original 2026-10-28 snapshot.

### Latest `main` CI

[CI run #186](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/41601450058) completed successfully for `main` at commit [`33819ff`](https://github.com/levanmanh268/cmc-ai-mentor-network/commit/33819ff51575596c5c17bb2ec79c8a43b0e985c7). GitHub shows a push at 2026-11-03 08:11 UTC (15:11 GMT+7), total duration 1m37s, and three artifacts.

| Job | Status | Duration |
| --- | --- | --- |
| Linux `test` | PASS | 59s |
| Windows `windows-local` | PASS | 1m34s |
| Mermaid CLI matrix (10.9.1 and 11.17.0) | PASS | Both matrix jobs completed successfully |
| Chromium browser E2E | PASS | 1m15s |
| Overall run | PASS | 1m37s |

The current workflow includes the Linux secret guard (`python -m scripts.secret_guard`), compile smoke, pytest/JUnit/coverage and evidence report, offline mentor/RAG diagnostics, Streamlit health smoke, Windows tests and startup check, two Mermaid CLI versions, and Chromium E2E. The run summary shows all jobs green. Exact pytest collected/passed/skipped counts and coverage percentages were not extracted from the downloadable artifacts; step-level skipped counts are therefore not asserted.

GitHub reported 3 warnings because `actions/upload-artifact@v4` targets Node.js 20 and is being forced onto Node.js 24, plus 4 notices about the `ubuntu-latest` runner migration to Ubuntu 26. These did not fail run #186 and are maintenance/compatibility follow-ups, not test failures.

### Public Cloud Smoke Observation

| Check | Observed result | Classification |
| --- | --- | --- |
| Render health endpoint | Response body observed as `ok` after the free service woke from sleep | PASS for health body; HTTP status code not captured separately |
| Public root UI | Streamlit page loaded and dashboard content rendered: 3 knowledge-base documents, 4 indexed chunks, LLM shown as offline | PARTIAL smoke only; no feature workflow submitted |
| WebSocket | Browser console recorded WebSocket close code `1006` during the observation | Warning to investigate if reproducible; dashboard subsequently rendered |
| Deployment SHA vs CI SHA | Not verified from Render deployment metadata | NOT VERIFIED |

The public cloud smoke is not human UAT. UAT-01 through UAT-10 remain NOT RUN because no tester completed and signed off the interaction checklist. Live Groq acceptance remains BLOCKED/NOT RUN: no user-owned API key was provided or entered. Do not infer live inference success from CI, the health endpoint, or the offline dashboard.

### Local Verification and Report Availability

| Check | Result |
| --- | --- |
| `python -m pytest -q` on the local Windows workspace | BLOCKED: `python` resolves to the Microsoft Store execution alias |
| `py -3 --version` | BLOCKED: launcher targets missing `E:\python3.14t.exe` |
| Local `py_compile` | BLOCKED for the same missing interpreter |
| Current report path on GitHub `main` | NOT PRESENT as of this check; GitHub returns 404 for this path |

The local Python failures did not execute pytest and are not test failures. Do not claim that this workspace or this report file was tested at commit `33819ff`; the successful run belongs to the remote `main` commit identified above.

## Revalidation 2026-11-09

This update preserves the earlier snapshots and records the latest `main` CI and the current local test outcome.

### Latest `main` CI

[CI run #198](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/41749168727) completed successfully for `main` at commit [`09850bf`](https://github.com/levanmanh268/cmc-ai-mentor-network/commit/09850bf957300614702066604728320066dec9b9). It was a push run created on 2026-11-04 at 00:45 UTC (07:45 GMT+7), completed in 1m37s, with three artifacts.

| Job | Status | Duration |
| --- | --- | --- |
| Linux `test` | PASS | 54s |
| Windows `windows-local` | PASS | 1m29s |
| Mermaid CLI matrix (10.9.1 and 11.17.0) | PASS | Both matrix jobs completed successfully |
| Chromium browser E2E | PASS | 1m33s |
| Overall run | PASS | 1m37s |

The run summary shows all listed jobs green. Exact pytest totals, skip count, and coverage percentage from CI artifacts were not extracted; do not infer them from the run conclusion.

### Current Local Verification

The active interpreter is Python 3.14.10. The full command `python -m pytest -q --tb=no` collected and executed the suite, with this result:

| Status | Count | Notes |
| --- | ---: | --- |
| PASS | 308 | Includes all tests in the touched local snapshot |
| SKIP | 26 | Pytest-reported skips |
| FAIL | 2 | Both are architecture-doc tests that invoke `git ls-files`; this workspace has no `.git` directory, so they fail before their assertions run |

When those two Git-metadata-dependent tests are deselected, the suite reports **308 passed, 26 skipped, 2 deselected**. The local core-module `py_compile` command from the reproduction section completed successfully using `E:\python.exe`.

### Outstanding Status

- Latest remote CI on `main`: PASS at SHA `09850bf`.
- Local pytest: partial, due to the two missing-Git-metadata failures above; this is not evidence that the remote CI failed.
- Public cloud manual UAT (UAT-01 through UAT-10): NOT RUN by a human tester.
- Live Groq inference: NOT RUN; do not enter a key or mark provider acceptance PASS without a controlled, user-owned credential and explicit consent.
- Exact CI JUnit/coverage figures and deployment SHA equality: NOT VERIFIED.
- This report and local test outcomes are workspace evidence, not changes committed to SHA `09850bf`.
