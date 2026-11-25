# SEC-05 / SEC-06 | Session lifecycle, quotas and applicability

**Issues:** #173 (P0), #174 (P2). **Scope:** current root Streamlit classroom app.

## Scope audit
- `st.session_state` stores profile, RAG/chat histories, favorites, optional session Groq key, chat/probe counters. This is not a secure authenticated account session.
- There is no root login, OTP, password reset, logout endpoint or app-owned auth token. Thus login brute-force throttling, secure account logout and 401/403 after logout are **NOT APPLICABLE**, not tests already passed.
- Browser/Streamlit framework cookies may exist. There is **no evidence** from this code audit that its platform cookies have particular HttpOnly/Secure/SameSite/TTL flags. Do not claim these were configured in app.py.
- Clearing profile and chat histories is a session state operation, not an identity logout. Test the isolation and deletion behavior only for the existing features.
- `MAX_CHAT_CALLS_PER_SESSION=30` and `MAX_PROBES_PER_SESSION=3` are demo counters: they can reset on reconnect. They are **not** server-side per-user/IP quotas or an anti-DoS guarantee.

## Tests
- SEC-05: independent per-session mutable mappings, profile reset and chat clear: tests/test_security_sprint.py.
- SEC-05: different real browser contexts must be verified by QA in authorized staging/cloud, including BYOK and optional mentor drafts.
- SEC-06: inspect current demo counters and negative path when they reach quota. Existing Streamlit probe tests may offer evidence; do not falsely claim live rate limiting.

## Future multi-user requirements
Trusted authentication provider; session invalidation and expiry; cookie policies at hosting/auth layers; backend-owned authorization; rate limits per account/IP and API provider budget; non-enumerating password-reset messages; multi-session tests. Do not add fake authentication controls to a no-login prototype just to satisfy a numerical checklist.

## Remaining gates
Human verification of browser isolation and platform-level session cookie attributes. Production-grade rate limiting is not implemented. Review before asserting a secure multi-user deployment.
