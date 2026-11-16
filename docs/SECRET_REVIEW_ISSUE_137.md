# Secret Exposure Review — Issue #137

**Review date:** 2026-11-09  
**Scope:** Current workspace source, tests/fixtures, text configuration, exception handling, and available log files. This is a workspace snapshot, not a Git checkout; tracked-file status and repository history could not be inspected locally.

## Findings

### Current files

A redacted pattern scan examined 162 text/config files using the repository CI guard's credential patterns:

- Groq-style keys: `gsk_` followed by at least 20 alphanumeric characters.
- API-key-like values: `sk-` followed by at least 20 token characters.
- PEM private-key headers.

**Result:** no candidate locations found. The scan printed only file/line/pattern metadata if a match occurred; no secret values were emitted. This result is limited to these patterns and file types; it is not proof that no credential of any form exists.

- No local `.env` file was present.
- `.env.example` contains only `GROQ_API_KEY=your_groq_api_key_here`.
- No `*.log` files were present in the workspace.
- `.gitignore` excludes `.env` and `*.log`.
- Test fixtures contain deliberately fake credentials for redaction tests; they are not usable credentials and do not match the scanner's candidate patterns.

### Exception and output handling

- `general_chat.py` maps provider exceptions to generic Vietnamese errors and does not return provider exception text.
- `rag_engine.py` falls back to offline excerpts on provider/citation errors rather than displaying exception details.
- `scripts/testing_report.py` prints the exception type for malformed XML, not the exception message or file content.
- Mentor draft validation rejects common API key, secret, token, password and private-key patterns with a generic message that does not echo the submitted value.
- The UI labels the key field as session-only/password input and does not add the key to chat history. The key is still sent to the app server to create a provider client; consent is required before provider calls.

### Historical exposure — unresolved verification

`SECURITY.md` states that a Groq credential was previously committed to the public repository and warns that deleting it from current files does not invalidate historical copies. This workspace has no `.git` directory, so the prior commit, history cleanup, and current credential revocation/rotation could not be verified. Treat that old credential as compromised until the repository owner confirms revocation/rotation through the provider console. Do not copy or repost the value into this issue or report.

## Verification

| Check | Result | Evidence |
| --- | --- | --- |
| Redacted source/config/fixture scan | PASS for configured patterns | 162 text/config files; zero candidate locations; values were not printed |
| Local `.env` and log inventory | PASS | `.env` absent; no `*.log` files found |
| Secret redaction/consent/draft validation tests | PASS | `python -m pytest -q tests/test_quality_gates.py tests/test_real_ai_chat.py tests/test_final_defense_probe.py tests/test_mentor_drafts.py`: 88 passed |
| Git-tracked-file scan and history review | BLOCKED | Workspace has no `.git`; `git ls-files` and history checks cannot run |
| Historical key revocation/rotation | NOT VERIFIED | Requires repository owner to confirm in Groq Console; no secret was accessed |
| Remote CI secret-guard step | NOT VERIFIED for this workspace snapshot | Current remote workflow references `python -m scripts.secret_guard`, but `scripts/secret_guard.py` is absent locally; remote run evidence is separate from this local scan |

## Recommended Actions

1. Confirm the previously exposed Groq key has been revoked and replaced; do not enter or disclose it during this review.
2. Re-run the repository `scripts.secret_guard` on a complete Git checkout and inspect Git history using the approved credential-rotation procedure.
3. Keep runtime secrets in the provider/hosting secret store or ignored local `.env`; keep only placeholders in `.env.example`.
4. Keep test credentials synthetic and ensure error/log paths never serialize provider exceptions or request headers.

**Conclusion:** no live credential pattern was detected in the files available in this workspace, and relevant redaction tests passed. Historical exposure remains an outstanding credential-management risk until revocation/rotation is confirmed.
