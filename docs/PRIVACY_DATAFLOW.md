# Data minimization and retention | Classroom prototype

**Scope:** root Streamlit app. No account database; no OAuth, registration, SMS/email to mentors, or stored conversation service.

| Field/data | Origin | Purpose | Lifetime/storage | External transfer |
| --- | --- | --- | --- | --- |
| `name` (optional) | Student text input | Display/profile context | `st.session_state.user_profile` | Not used in RAG prompt; UI does not send it in matching explanation |
| `year` | Student selectbox | Matching experience fit | Session only | May enter optional Groq matching explanation |
| `field_interest` | Student text input | Matching text and domain overlap | Session only | May enter optional Groq matching explanation |
| `goals` | Student text input | Matching text and explanation | Session only | May enter optional Groq matching explanation |
| `bio` (optional) | Student text area | Text features for ranking | Session only | Not directly included in current matching LLM explanation |
| RAG `messages` | Hỏi đáp tài liệu | Prompt + cited source trong riêng mode RAG | Streamlit session only | Chỉ câu hỏi và Markdown context được gửi khi đã có key và đồng ý |
| General `general_messages` | Trò chuyện AI | Multi-turn model context | Streamlit session only, 16 messages / 12k chars gửi theo cửa sổ | Dữ liệu hội thoại gần đây được chuyển tới Groq khi có key và đồng ý |
| `favorite_mentors` | Save button | Saved demo mentor list | Session only | Not sent as a list to external service |
| Local knowledge base Markdown | Repository | Retrieval context | Tracked files | Relevant snippets sent to Groq when configured |
| Optional `GROQ_API_KEY` | Local environment/.env/Render environment | Authentication to external provider | Process environment | Used by Groq Python client; never commit/log |
| Session Groq key (BYOK) | Masked password widget in sidebar | Authenticate chosen user account to Groq | **Streamlit Session State in Render server RAM** only, not chat history | Sent server → Groq API on calls after opt-in; not end-to-end encrypted exclusively in browser |

**Deletion:** Document-chat clear resets `messages`; general-chat clear resets `general_messages` independently; profile reset clears `user_profile` and matching state; favorite mentors removed via their Delete UI. Streamlit session state expires when session/server closes; no guaranteed durability or immediate third-party data deletion after Groq API requests.

**Controls:** `.env` ignored by Git, secret pattern guard in CI, no app-level logging of raw prompts. **Explicit per-session opt-in:** sidebar checkbox defaults off even if Groq key configured; both RAG and mentor explanations receive `authorized_client=None` until opted in. Revocation stops *new* requests; earlier provider copies are not deleted. No independent network capture or provider privacy audit has yet been completed. This is a code-level dataflow inventory, not independent network capture, privacy impact assessment or provider retention audit. For real personal data, require consent, privacy policy and storage threat model before deployment.

Tracking: [NFR-03 #32](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/32), [NFR-04 #33](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/33).

**Credential exposure caveat:** A session API key is transmitted from the browser to the Streamlit server, resides temporarily in server-side memory and is supplied to the Groq SDK for authentication. It is hidden visually with a password widget, but **not** a client-side-only vault or durable encrypted secret store. This option is intended for controlled demos; avoid collecting keys from untrusted public users. For broad public use, prefer a server-managed key plus authentication, per-user quotas and abuse protection. Do not log raw API requests or secrets. When free-tier instance restarts, session data/keys are lost; provider-side retention is governed by Groq's policies.
