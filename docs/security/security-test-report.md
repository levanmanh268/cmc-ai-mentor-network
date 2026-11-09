# SEC-12 | Security test plan and machine-verifiable report

**Issue:** #180. **Version:** 2026-11-09 tested security code snapshot. **Environment:** GitHub PR branch `security/sprint-sec01-sec13-20261109`. **Verified test SHA:** `98510e9f670118bab722d526faee5aaa2d524ecc`. **Run:** [#42541686498](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42541686498). **Not** a penetration test or production security signoff.

## Test-case matrix
| ID | Threat | Actual test/steps | Expected (defined before run) | Actual | Status |
| --- | --- | --- | --- | --- | --- |
| SEC-TC-01 | invalid types | `test_sec03_rejects_wrong_type_or_empty_query` parametrize None/int/list/dict/empty | reject input without crash | Test assertions passed in automated CI [run 42541686498](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42541686498) | PASS |
| SEC-TC-02 | oversized RAG | `test_sec03_rejects_oversized_query_before_provider_call` | zero fake-provider calls, no evidence | Test assertions passed in automated CI [run 42541686498](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42541686498) | PASS |
| SEC-TC-03 | wrong type API | `test_sec03_rejects_non_string_answer_input_without_crashing` | no crash/no provider | Test assertions passed in automated CI [run 42541686498](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42541686498) | PASS |
| SEC-TC-04 | path symlink escape | `test_sec03_symlinked_root_not_indexed_portable` | ignore root symlink; 0 documents | Test assertions passed in automated CI [run 42541686498](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42541686498) | PASS |
| SEC-TC-05 | Markdown HTML injection | `test_sec04_dynamic_markdown_label_escapes_html_and_formatting` | HTML and Markdown delimiters escaped | Test assertions passed in automated CI [run 42541686498](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42541686498) | PASS |
| SEC-TC-06 | Markdown heading spoofing | `test_sec04_dynamic_label_cannot_start_new_heading_or_inject_newline` | no raw newline/new heading | Test assertions passed in automated CI [run 42541686498](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42541686498) | PASS |
| SEC-TC-07 | session profile isolation | `test_sec05_session_profile_reset_does_not_touch_other_session` | only A cleared, B intact | Test assertions passed in automated CI [run 42541686498](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42541686498) | PASS |
| SEC-TC-08 | chat deletion scope | `test_sec05_clearing_chat_preserves_profile_and_favorites` | chat clears without profile/favorites deletion | Test assertions passed in automated CI [run 42541686498](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42541686498) | PASS |
| SEC-TC-09 | no consent data transfer | `test_sec10_consent_deny_by_default` (7 values) | no authorized provider client | Test assertions passed in automated CI [run 42541686498](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42541686498) | PASS |
| SEC-TC-10 | explicit opt-in | `test_sec10_consent_explicit_true_only` | only literal True permits configured client | Test assertions passed in automated CI [run 42541686498](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42541686498) | PASS |
| SEC-TC-11 | secret patterns | `test_sec09_secret_guard_detects_fake_examples_without_real_keys` | fake patterns detected; placeholders allowed | Test assertions passed in automated CI [run 42541686498](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42541686498) | PASS |
| SEC-TC-12 | per-session profile updates | `test_sec11_save_profile_does_not_update_another_session` | no cross-session updates in unit test | Test assertions passed in automated CI [run 42541686498](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42541686498) | PASS |

**Run commands (execute on checked-out PR SHA):**
```bash
python -m pip install -r requirements.txt
python -m pytest -q -rs tests/test_security_sprint.py
python -m pytest -q -rs
python -m scripts.secret_guard
python -m py_compile app.py rag_engine.py security_controls.py tests/test_security_sprint.py
```

## Evidence table
| Evidence | SHA | Workflow link | Verdict |
| --- | --- | --- | --- |
| Local helper-only syntax/check | PENDING | PENDING | NOT VERIFIED |
| Linux pytest full + security | `98510e9f670118bab722d526faee5aaa2d524ecc` | [CI 42541686498](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42541686498) | PASS: 334 passed, 25 skipped, 0 failed; scoped line coverage 96% |
| Windows pytest full + security | `98510e9f670118bab722d526faee5aaa2d524ecc` | [CI 42541686498](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42541686498) | PASS: 334 passed, 25 skipped, 0 failed |
| Chromium UI E2E | `98510e9f670118bab722d526faee5aaa2d524ecc` | [CI 42541686498](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42541686498) | PASS: 5 tests |
| Secret guard (tracked HEAD only) | `98510e9f670118bab722d526faee5aaa2d524ecc` | [CI 42541686498](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42541686498) | PASS: No tracked secret pattern detected |
| Human UAT/XSS browser DOM | PENDING | PENDING | NOT RUN |
| Prompt-injection adversarial live model | PENDING | PENDING | NOT RUN |
| Deployed HTTPS certificate/headers | PENDING | PENDING | NOT RUN |
| Previously exposed key revoked by owner | UNKNOWN | Private owner acknowledgement | NOT VERIFIED |

**Observation:** CI exercised each of the new security tests without failures (non-skipped, deterministic assertions). Specific effects were observed through assertions: invalid/oversized questions denied before provider call; symlinked root produced 0 documents; label escaped HTML/Markdown; consent denied on false-like values; session A resets did not touch B; fake secrets detected. The 25 SKIP cases are from optional API/document suites under existing main dependency installation, NOT newly skipped security tests. On PR #161 they are addressed separately; no claim of zero SKIPs on this branch.

**Important:** This report documents tested SHA `98510e9...`, while later documentation-only commits may move PR HEAD. For final merge gate, verify CI on exact newest PR head and then again on post-merge main SHA. Security case count is not equivalent to independence or test quality. All cases are in-scope classroom unit checks; untested network/cloud controls remain open.

## How to update this file
After CI finishes, replace ONLY the values supported by the exact GitHub Actions run/SHA and logs; add observed actual outputs. Do not transform a manually documented expectation into a PASS. Separate new PR checks from post-merge main checks. Reviewer must confirm before closing #180.
