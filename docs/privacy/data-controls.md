# SEC-11 | Data access, edit, reset and retention controls

**Issue:** #179 (P2). **Current architecture:** no authenticated account or durable server user database.

## Controls available now
1. Profile: edit and "Lưu hồ sơ trong phiên". "Đặt lại / xóa hồ sơ trong phiên" clears `user_profile`, stale matches and explanations. Does **not** delete favorites or chat history.
2. Grounded RAG: "Xóa lịch sử hội thoại" clears RAG `messages` only.
3. General chat: dedicated clear dialog clears `general_messages` only.
4. Mentor favorites: each item has a remove button; the list exists in current session.
5. Groq: disable checkbox to stop **new** provider requests; cannot retract prior transmissions. User can revoke own BYOK at provider.
6. Session expiration: best-effort in-memory Streamlit lifecycle; no per-account retention TTL or guaranteed erase at provider.

## Tests and proof boundary
- `tests/test_security_sprint.py` has session-state reset/clear cross-session unit cases and explicit-deny consent cases. These do NOT simulate browser cookie logout or prove cloud isolation.
- Manual test: open browser profiles A and B, fill different fictional profiles, reset A, verify B unaffected, then repeat favorites and chat. Record browser, build SHA, screenshot redacted. If feature #165 is merged, verify mentor draft A not visible to B.
- No login, logout, password or cross-account access; account delete and server-side per-user export are **NOT APPLICABLE** to current prototype. If actual storage is added, reopen SEC-07/08/11 with server-side access controls and deletion endpoints.

## Acceptance
Document actual deletion scopes and bounds, one verified edit/reset user control, two runnable session tests, human UAT when available. Never promise 24h/30d deletion without platform/vendor contract evidence.
