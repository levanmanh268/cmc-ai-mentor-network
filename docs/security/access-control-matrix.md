# SEC-07 / SEC-08 | Authentication and access control applicability

**Issues:** #175, #176. **Scope:** root Streamlit app, not sample FastAPI labs.

## Evidence / architectural decision

Repository root `app.py` is a Streamlit prototype with profile form, RAG/chat, mentor matching and favorites. It has **no user registration/login/logout/account database, password verifier, admin panel, JWT, OAuth, or protected business API**. A Groq API key authenticates the *application to Groq*, NOT an application user. Streamlit session state does NOT establish user identity.

Therefore:
- SEC-07 existing password/login/logout/authentication tests: **NOT APPLICABLE** to this prototype. Do not claim three successful login tests, or implement dummy password/login UI for checklist compliance.
- SEC-08 cross-account RBAC/403 tests: **NOT APPLICABLE** until account identity/role protected endpoints exist.
- Nevertheless, cross-session isolation and disallowing anonymous shared writes **are applicable security requirements** and must be tested.

## Current access matrix

| Actor/context | Public app UI | Session profile/chat/favorites | Shared mentor source records | Server Groq environment key | Provider calls | GitHub admin controls |
| --- | --- | --- | --- | --- | --- | --- |
| Anonymous browser session A | Allow | Own session only | Read demo records only | Cannot read directly | Only after consent and configured key | Deny |
| Anonymous browser session B | Allow | Own session only, not A's | Read demo records only | Cannot read directly | Own explicit consent required | Deny |
| Server-side Streamlit process | Host UI | Holds per-session state in RAM | Read from shipped source | Reads environment by config | Can initiate when consent gate passes | No special GitHub admin right |
| Groq provider | N/A | Only submitted question/context/history | No direct source access | Receives provider credential for API auth | Processes submitted request | Deny |
| GitHub repository admin | Code/repo governance | No right to individual running sessions by feature design; hosting ops caveat | Code maintainer | Manage deployment secrets outside repo | No independent opt-in | Allow by GitHub controls |

**Caveat:** This is a design matrix; it does not prove client isolation or strong tenancy. Testing needs two separate browser contexts. No protected server resource should be introduced without actual authentication/authorization enforced at backend/API.

## Future security gate if persistent mentor accounts are demanded
1. Define trusted identity provider, login/logout/reset/expiration; store password only via Argon2id/bcrypt if self-managed.
2. Choose server-side authorization by resource ownership/role, not UI-only checks.
3. Add server-backed database and authorization checks, cross-user tests for 401/403, ownership and IDOR, session expiry and logout invalidation.
4. Use deployment-level per-user rate limiting, CSRF/CORS/cookie review as appropriate.
5. Treat this as a separately scoped feature, not present in the current version.

Cross references: #165 (mentor draft session-only), #173 (session safety), #174 (rate limit), #175 and #176.
