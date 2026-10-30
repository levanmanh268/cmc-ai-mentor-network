# Test Cases | CMC AI Mentor Network

## Scope and execution rules

Automated cases cover the root Streamlit prototype and deterministic offline modules. Fake Groq clients verify request construction and failure handling; they do not verify model quality. `AppTest` runs the real Python UI code in-process; it is not human UAT or a hosted-browser test. The separate Chromium suite opens a local server in CI.

Run the automated suite with:

```bash
python -m pip install -r requirements-test.txt
python -m pytest -q -rs
```

## RAG retrieval and answer behavior (TASK-30–37)

| ID | Scenario / setup | Expected result | Automated evidence |
| --- | --- | --- | --- |
| TC-RAG-30 | Ask about GitHub issue, branch and commit using a corpus that contains those facts | Relevant document ranks first; offline answer shows a source marker | `test_task30_clear_answer_query_retrieves_expected_document` |
| TC-RAG-31 | Ask about chlorophyll against Git/RAG documents | `no-evidence`, no sources, clear refusal | `test_task31_out_of_scope_question_refuses_without_sources` |
| TC-RAG-32 | Empty Markdown directory and a client that raises if called | No provider call; `no-evidence` | `test_task32_empty_knowledge_base_never_calls_provider` |
| TC-RAG-33 | Invalid UTF-8, empty Markdown, unsupported TXT, and valid Markdown | Bad/unsupported files are ignored; valid file remains searchable | `test_task33_corrupt_and_unsupported_documents_are_skipped` |
| TC-RAG-34 | Check offline `[S<n>]` references against returned result order | Every emitted reference is a valid source index | `test_task34_offline_citations_map_to_returned_sources`; evaluator citation metric |
| TC-RAG-35 | Question with evidence split across two Markdown files | Both source documents occur in top-k | `test_task35_query_can_retrieve_evidence_from_multiple_documents` |
| TC-RAG-36 | Document contains “ignore previous instructions” and asks for an API key | Prompt labels context as untrusted and tells model not to follow embedded instructions | `test_task36_document_prompt_injection_is_delimited_as_untrusted_context` |
| TC-RAG-37 | Provider raises timeout after retrieval | Offline fallback retains sources and hides exception detail | `test_task37_provider_timeout_falls_back_to_offline_answer` |

**Security limitation:** TC-RAG-36 inspects the prompt sent to a fake client. It does not prove a live model will resist every prompt injection. Do not report it as a penetration test.

## Integration and regression (TASK-41–47)

| ID | Scenario | Expected result | Automated evidence |
| --- | --- | --- | --- |
| TC-INT-41 | Save valid profile, find and favorite a mentor, rerun, then remove favorite | State and ranking remain consistent through the user flow | `tests/test_end_to_end_flows.py::test_e2e02_profile_to_mentor_to_favorites_and_rerun` |
| TC-INT-42 | Submit supported and unsupported questions, switch chat modes | RAG status and sources are correct; two histories stay separate | `test_e2e01_offline_rag_positive_negative_and_chat_mode_isolation` |
| TC-INT-43 | Clear chat with profile/favorites present | Only target chat history is cleared | `tests/test_task09_29_regressions.py::test_task21_clear_ai_chat_preserves_profile_favorites_and_rag_history` |
| TC-INT-44 | Navigate Streamlit pages and update session data | UI renders without uncaught exception and reflects saved state | AppTest suites in `tests/test_streamlit_ui.py`, `tests/test_profile_ui.py`, `tests/test_end_to_end_flows.py` |
| TC-INT-45 | Missing provider, denied consent, timeout or provider error | No unauthorized request; safe fallback/error state | `tests/test_real_ai_chat.py`, `tests/test_final_defense_probe.py`, RAG TASK-37 test |
| TC-INT-46 | Reproduce fixed defect before correction | Regression test is added beside the fix | Relevant regression suites; task-specific issue must link the original defect |
| TC-INT-47 | Change core code | CI runs compile, lint, tests, RAG evaluation and runtime smoke | `.github/workflows/ci.yml`; a GitHub Actions run is required for remote proof |

## CI, security, performance, review and acceptance (TASK-48–79)

See [TRACEABILITY_MATRIX.md](TRACEABILITY_MATRIX.md) for all issue IDs, evidence location and whether the proof is automated or requires a maintainer/user. Never change a manual UAT, live provider, branch-protection or human-review result to PASS without direct evidence.
