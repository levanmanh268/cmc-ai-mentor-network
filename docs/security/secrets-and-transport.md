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
Public URL candidate: https://cmc-ai-mentor-network-group6.onrender.com/. An HTTPS URL **alone is not proof** of a successful TLS handshake, redirect enforcement, certificate chain or no mixed content. Independent live verification was unavailable in this environment. Assign a member to capture HTTPS/TLS certificate and browser connection status, any HTTP -> HTTPS redirect, and response headers on the authorized public deployment. Mark **NOT VERIFIED** until evidence is attached.

## Historically exposed Groq credential
`SECURITY.md` records that a Groq key was once pushed to public history. **Removing it from current files does not revoke it.** Only the holder of the key can confirm in the Groq console that it was revoked/rotated and the new key was configured privately. Record `REVOCATION: UNKNOWN / CONFIRMED BY OWNER` in a PRIVATE channel without copying any key. Consider history rewriting only after coordinating with collaborators; require force-push and cache clean-up plan. Public issue must not reproduce secret bytes.

## Acceptance evidence still required
- [ ] Exact main SHA after security PR merge, secret_guard pass and dependency audit on that SHA.
- [ ] Live HTTPS/TLS verification by human tester on approved host and URL.
- [ ] Private key revocation acknowledgement by owner.
- [ ] No secret or personal data published in report, CI output, screenshots, test fixtures or PR comments.
- [ ] Independent review of provider retention and transport statements. No claim of end-to-end encryption or complete history cleanup.

See #177 #137 #87 and `docs/PRIVACY_DATAFLOW.md`.
