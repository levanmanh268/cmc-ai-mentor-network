# Issue-to-test traceability | TASK-30–79

Status describes evidence available in this checkout, not a claim that every administrative or human step has happened. Automated test references become remotely verifiable only after the changes are pushed and CI completes for that commit.

| Issue | Requirement / acceptance evidence | Current evidence | Evidence status |
| --- | --- | --- | --- |
| TASK-30 | Supported query retrieves expected source | `tests/test_rag_engine.py::test_task30_*`; RAG evaluation | Automated |
| TASK-31 | Out-of-scope query refuses | `test_task31_*`; 5/5 refusal benchmark | Automated |
| TASK-32 | Empty KB does not call provider | `test_task32_*` | Automated |
| TASK-33 | Corrupt/unsupported documents skipped | `test_task33_*`; invalid UTF-8 handling | Automated |
| TASK-34 | Citation IDs point to retrieved sources | `test_task34_*`; 10/10 citation metric | Automated, semantic support not proven |
| TASK-35 | Multi-document retrieval | `test_task35_*` | Automated |
| TASK-36 | Document prompt injection is treated as untrusted input | `test_task36_*` | Prompt contract only; live adversarial model evaluation pending |
| TASK-37 | API timeout falls back safely | `test_task37_*` and existing provider failure tests | Automated with fake provider |
| TASK-38 | Review evaluation cases and limitations | `scripts/evaluate_rag.py`, `docs/RAG_EVALUATION.md` | Completed for current 14-case demo set; independent gold set not available |
| TASK-39 | Recall@k, citation correctness, answer correctness | evaluator metrics; answer metric explicitly named proxy | Measured on demo corpus; no LLM semantic accuracy claim |
| TASK-40 | Evaluation report | `docs/RAG_EVALUATION_REPORT.md` | Local measurement documented |
| TASK-41 | Profile to mentor end-to-end | `tests/test_end_to_end_flows.py::test_e2e02_*` | AppTest automated |
| TASK-42 | User question to RAG answer | `test_e2e01_*`, browser E2E suite | AppTest automated; browser CI pending this revision |
| TASK-43 | Clear chat without losing related data | task 21 regression test and UI helper tests | Automated |
| TASK-44 | Data modules integrated with Streamlit UI | AppTest suites and runtime health in CI | Automated locally/CI configured; remote run pending |
| TASK-45 | AI API unavailable | fake-provider timeout/error and no-key tests | Automated; no live provider outage test |
| TASK-46 | Prevent fixed defects returning | named regression tests in `tests/` | Completed for defects with existing regression coverage; new issues require their own reproducer |
| TASK-47 | Rerun after important change | GitHub CI workflow | Configured; branch CI evidence pending push/PR |
| TASK-48 | Pytest runs in CI | `.github/workflows/ci.yml`, `requirements-test.txt` | Configured |
| TASK-49 | CI fails on pytest failure | pytest command exit status is not suppressed | Configured; remote failure injection not performed |
| TASK-50 | PR requires CI before merge | repository branch protection / ruleset | **Not verified**; rulesets query returned none and branch-protection API denied integration access |
| TASK-51 | Coverage report | pytest-cov XML + CI artifact | Configured |
| TASK-52 | Coverage goal | `--cov-fail-under=90` for named seven-module scope | Configured; 97% measured on local Python 3.14.5 run |
| TASK-53 | Source quality checks | Ruff selected E4/E7/E9/F rules + py_compile | Configured and passed locally |
| TASK-54 | Reproducible test dependencies | `requirements-test.txt` includes all declared test requirements | Configured; local optional API/DOCX/PDF deps absent in this environment |
| TASK-55 | Results attached to commit | JUnit, coverage and report artifacts carry Actions SHA/run | Configured; current local result is not a GitHub artifact |
| TASK-56 | Secret leakage scan | CI `git grep` patterns; `.env` ignored | HEAD scan configured; Git history and previous leaked-key revocation **not verified** |
| TASK-57 | Consent and personal data transfer | `docs/PRIVACY_DATAFLOW.md`; consent regression tests | Code review/test evidence; user comprehension and network capture pending |
| TASK-58 | Prompt injection | RAG test and general-chat system prompt tests | Prompt contract tested; live adversarial robustness not proven |
| TASK-59 | Known dependency vulnerabilities | `.github/workflows/dependency-audit.yml`; `docs/DEPENDENCY_AUDIT_REPORT.md` | Local `pip-audit` initially found 2 vulnerable packages; after upgrades local scan reports no known vulnerabilities. CI run still pending |
| TASK-60 | External API errors/timeouts | fake-client failure tests | Automated; live network outages not simulated |
| TASK-61 | RAG latency | `scripts/final_smoke_audit.py`, 100 warm samples | Local result in `docs/TEST_REPORT.md`; CPU only |
| TASK-62 | Mentor ranking latency | same benchmark, 100 warm samples | Local result in `docs/TEST_REPORT.md`; demo pool only |
| TASK-63 | Increasing data scale | `scripts/benchmark_scaling.py`, 3/30/100 docs and 10/100/500 mentors | Synthetic local measurement; no SLA or production workload |
| TASK-64 | Consecutive requests/session isolation | `test_task64_consecutive_requests_*`; multi-turn AppTest | Automated, sequential only |
| TASK-65 | Test-first process for new functionality | test source for RAG changes | Code contains tests; independent commit-history red/green proof requires PR history |
| TASK-66 | Regression test before bug fix | regression suites | Existing evidence by test, but ordering cannot be proven from current working diff |
| TASK-67 | New tests reviewed in PR | PR review history | Requires human reviewer and pushed PR |
| TASK-68 | Review logic/boundaries/errors | tests and Ruff/compile gates | Automated coverage exists; human review pending |
| TASK-69 | Resolve blocking review comments | PR review threads | Requires actual PR/reviewer |
| TASK-70 | Verify PR/CI process in history | GitHub PR and workflow history | Requires merged/reviewed PR for this change |
| TASK-71 | Test plan | `docs/TEST_PLAN.md` | Existing plan updated with new suites/benchmarks |
| TASK-72 | Test cases | `docs/TEST_CASES.md` | Added |
| TASK-73 | Traceability | this file | Added for TASK-30–79 |
| TASK-74 | Real test report | `docs/TEST_REPORT.md` | Added from actual local run; no CI run yet |
| TASK-75 | User acceptance checklist | `docs/UAT_CHECKLIST.md` | Scenarios documented; human sign-off remains NOT RUN |
| TASK-76 | Unfixed defects/severity | `docs/KNOWN_ISSUES.md` | Added; items needing external evidence are distinguished |
| TASK-77 | Retest release candidate | `docs/TEST_REPORT.md` | Current working tree retested; no nominated release SHA supplied |
| TASK-78 | Compare against course chapter | `docs/TESTING_HANDOFF.md` / this report | General testing concepts mapped; exact book/chapter edition not provided |
| TASK-79 | Quality conclusion and evidence | `docs/TEST_REPORT.md`, `docs/RAG_EVALUATION_REPORT.md` | Local evidence summarized; remote CI/UAT/admin evidence pending |

## Release gates still requiring people or remote permissions

1. Push this revision and wait for Linux/Windows/browser CI artifacts for its exact SHA.
2. A repository administrator must enable and verify required status checks for PRs; this connection could not read branch protection.
3. A group member must perform/sign off UAT. Automation cannot substitute for a human.
4. A reviewer must review the PR and resolve/block any review threads.
5. Provide the exact textbook/chapter if TASK-78 requires line-by-line alignment to a particular source.
