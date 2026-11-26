# SEC-09 | Secrets, HTTPS/TLS and encryption decisions

**Owner proposed:** Nguyễn Văn Phúc. **Issue:** #177. **Status:** partial control verification, operational sign-off outstanding.

## Existing controls (code-audited)
- `llm_client.py` reads `GROQ_API_KEY` from environment or session override; SDK is constructed server-side. No key literal should be stored in source.
- `.gitignore` excludes `.env`, and `.env.example` exists for placeholder-only configuration.
- `scripts/secret_guard.py` scans tracked HEAD files for recognizable key/private key patterns. It does NOT search commit history or guarantee detection of arbitrary credentials.
- The Streamlit sidebar's password widget masks typed BYOK visually. Its value still travels browser -> Streamlit server and resides in session RAM before use. Do not describe it as client-only encrypted vault.
- User opt-in defaults false. `consented_client` preserves None until explicit True. Groq receives prompt/history/snippets only when a request is made with opt-in and a client.
- No app-owned persistent account database to assess storage encryption at rest. GitHub/Render/provider controls are third-party responsibilities outside this source review.

## Transport verification
Authorized public URL: https://cmc-ai-mentor-network-group6.onrender.com/.

Local observation on 2026-11-18:

| Steps | Expected | Actual | Result |
| --- | --- | --- | --- |
| `curl.exe --head --max-redirs 0 http://cmc-ai-mentor-network-group6.onrender.com/_stcore/health` | Plain HTTP redirects to the HTTPS URL | `301 Moved Permanently`; `Location` points to the same health path on `https://cmc-ai-mentor-network-group6.onrender.com` | PASS |
| `Invoke-WebRequest https://cmc-ai-mentor-network-group6.onrender.com/_stcore/health` | Trusted HTTPS request succeeds and health endpoint responds | `200`; response body `ok`; request completed with the platform's normal TLS certificate validation enabled | PASS (HTTPS health smoke only) |

These observations verify the redirect and a successful HTTPS request at that
time. They do **not** document the certificate chain/expiry, negotiated TLS
version/cipher, security headers, browser lock state, mixed content, application
behavior or continued availability. Do not treat them as a full TLS audit or
production security certification. The deployed service may change after this
observation.

## Historically exposed Groq credential
`SECURITY.md` records that a Groq key was once pushed to public history. **Removing it from current files does not revoke it.** Only the holder of the key can confirm in the Groq console that it was revoked/rotated and the new key was configured privately. Record `REVOCATION: UNKNOWN / CONFIRMED BY OWNER` in a PRIVATE channel without copying any key. Consider history rewriting only after coordinating with collaborators; require force-push and cache clean-up plan. Public issue must not reproduce secret bytes.

## Acceptance evidence still required
- [ ] Exact main SHA after security PR merge, secret_guard pass and dependency audit on that SHA.
- [ ] Independent human/browser review of certificate details, TLS configuration, security headers and mixed content on the approved host.
- [ ] Historical Git scan covering all relevant refs and deleted/unreachable history. `scripts/secret_guard.py` scans tracked HEAD only; a clean HEAD result is not a clean-history claim.
- [ ] Private key revocation acknowledgement by owner.
- [ ] No secret or personal data published in report, CI output, screenshots, test fixtures or PR comments.
- [ ] Independent review of provider retention and transport statements. No claim of end-to-end encryption or complete history cleanup.

## Verification log

| Steps | Expected | Actual | Result |
| --- | --- | --- | --- |
| Inspect `.gitignore` and `.env.example`; run `git check-ignore -v .env` and `git check-ignore .env.example` | `.env` is ignored; the safe placeholder example remains trackable | `.env` matches `.gitignore:2`; `.env.example` is not ignored | PASS |
| Run `python -m pytest -q tests/test_secret_guard.py` on the updated PR branch worktree based on `c8eebeb475034fffaaf93bd1cc2ed4a884a91d56` | Synthetic Groq/API/PEM patterns are detected without publishing real credentials | `2 passed in 0.02s`; fixtures construct fake patterns only | PASS |
| Run `python -m scripts.secret_guard` after the documentation update | Tracked current files are checked; output contains no secret bytes | `No tracked secret pattern detected.` | PASS (HEAD only) |
| Stream objects from `git rev-list --objects --all` through `git cat-file --batch` and scan recognizable patterns without printing matches | Search all locally reachable refs while suppressing credential bytes | Scanned 2,068 locally reachable Git objects: 4 Groq-style pattern hits in 4 blobs, 1 API-key-like pattern hit in 1 blob, and 0 PEM private-key pattern hits. Matches are not confirmed active credentials and may include synthetic fixtures. | PASS (local refs only) |
| Confirm prior exposed key revocation in provider console | Owner confirms revoke/rotation without sharing key | Requires credential owner; no confirmation available to this code review | BLOCKED |
| Inspect certificate chain, TLS version/cipher, response headers and browser mixed content | Human/browser evidence recorded for the authorized deployment | Not captured by the HTTP health smoke above | SKIP |

**Evidence limits:** The tests use fake credentials; no live secret is included.
Historical matches were counted only; no matched value or sensitive line was
printed or recorded. This scan covers objects reachable from refs fetched in
this local clone only. It cannot cover deleted/unreachable remote objects,
unfetched refs, forks, caches or provider logs, and a pattern hit does not prove
that a credential is valid or revoked. Owner-only revocation and detailed
browser/TLS checks remain open gates. Local observations and the prior CI run
do not replace a fresh CI run on the updated PR head or independent review.

See #177 #137 #87 and `docs/PRIVACY_DATAFLOW.md`.
