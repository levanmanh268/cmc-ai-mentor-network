# Code Review Record — Issue #149

**Review date:** 2026-11-03  
**Repository:** CMC AI Mentor Network  
**Review scope:** `matching_engine.py` numeric boundaries; neighboring tests in `tests/test_matching_engine.py` and `tests/test_quality_gates.py`. Spot checks also covered LLM error redaction and RAG fallback/source handling in `llm_client.py`, `general_chat.py`, and `rag_engine.py`. This is a focused review of the core application paths, not an exhaustive audit of every independent portfolio lab.

## Findings

### High: mentor matching call sites pass an unsupported pool argument

The Mentor page calls `get_top_matches(..., mentor_pool=mentor_pool)` so it can rank the shared mentors together with session-only drafts. The function previously did not accept `mentor_pool`, so the search action raised `TypeError`; session draft matching and related mentor UI flows failed as well.

**Resolution:** `get_top_matches()` now accepts an optional pool and copies it before filtering. The default still loads the repository pool, while callers can supply a session-specific pool without mutating their list.

**Regression coverage:** the existing session-draft test covers ranking a draft from a supplied pool; the end-to-end and Streamlit UI tests cover mentor search, filters, and saving favorites.

### Low: non-finite numeric values escape matching input fallbacks

`parse_student_year()` and `get_top_matches()` convert their arguments with `int()` and previously caught `TypeError` and `ValueError` only. Converting positive or negative infinity to `int` raises `OverflowError`, bypassing the safe defaults and raising out of the matching helpers. The normal Streamlit year selector does not supply these values, so this is a defensive API/edge-case issue rather than a normal UI-path failure.

**Resolution:** both conversion guards now catch `OverflowError`. Invalid/infinite student years use year 1; invalid `top_k` uses its default of 3 before normal result-count clamping.

**Regression coverage added:**

- `test_parse_student_year_is_safe` now checks positive infinity and NaN.
- `test_qg22_match_count_is_safe` now includes positive infinity for `top_k`.

## Other Reviewed Paths

- LLM provider failures are converted to generic, sanitized user-facing messages; exception text is not returned by `generate_general_reply()`.
- RAG source loading rejects symlinked files and paths outside the knowledge root, skips oversized/unreadable files, and falls back to offline excerpts on provider/citation failures.
- Matching filters run before ranking, result counts are clamped for ordinary invalid values, and profile fields are normalized for scoring.

No additional confirmed defect was identified in these spot-checked paths. This statement is limited to the scope above and is not a security or correctness certification.

## Verification Evidence

| Check | Result | Evidence |
| --- | --- | --- |
| Targeted matching/quality-gate tests | PASS | 64 passed before the optional-pool fix; included again in the final full-suite run. |
| Mentor draft, Streamlit UI, and end-to-end tests | PASS | `E:\python.exe -m pytest -q tests/test_mentor_drafts.py tests/test_streamlit_ui.py tests/test_end_to_end_flows.py`: 20 passed. |
| Full pytest suite | PARTIAL | 308 passed, 26 skipped, 2 failed. Both failures are architecture-doc tests that invoke `git ls-files`; this workspace has no `.git` directory. |
| Runnable suite excluding the two Git-metadata checks | PASS | `E:\python.exe -m pytest -q --deselect=tests/test_architecture_docs.py::test_no_case_insensitive_filename_collision --deselect=tests/test_architecture_docs.py::test_one_canonical_architecture_file_and_readme_links`: 308 passed, 26 skipped, 2 deselected. |
| Editor diagnostics for changed Python/Markdown files | PASS | No diagnostics reported. |
| Latest remote CI before this local patch | PASS, not patch evidence | [Run #186](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/41601450058) passed at remote `main` SHA `33819ff`; it predates this local change. |

**Environment limits:** the available local interpreter is Python 3.14; CI is configured for Python 3.11, so cross-version CI evidence for this patch is still pending. The workspace is not a Git checkout, so a local commit SHA cannot be recorded and the two `git ls-files`-dependent tests cannot pass here. The test failures are unrelated to the matching changes.
