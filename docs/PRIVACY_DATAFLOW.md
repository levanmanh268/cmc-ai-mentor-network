# Data minimization and retention | Classroom prototype

**Scope:** root Streamlit app. No account database; no OAuth, registration, SMS/email to mentors, or stored conversation service.

| Field/data | Origin | Purpose | Lifetime/storage | External transfer |
| --- | --- | --- | --- | --- |
| `name` (optional) | Student text input | Display/profile context | `st.session_state.user_profile` | Not used in RAG prompt; UI does not send it in matching explanation |
| `year` | Student selectbox | Matching experience fit | Session only | May enter optional Groq matching explanation |
| `field_interest` | Student text input | Matching text and domain overlap | Session only | May enter optional Groq matching explanation |
| `goals` | Student text input | Matching text and explanation | Session only | May enter optional Groq matching explanation |
| `bio` (optional) | Student text area | Text features for ranking | Session only | Not directly included in current matching LLM explanation |
| Chat prompts / messages | Student chat | RAG questions/history | Session only | Prompt and retrieved Markdown context transferred to Groq only when configured |
| `favorite_mentors` | Save button | Saved demo mentor list | Session only | Not sent as a list to external service |
| Local knowledge base Markdown | Repository | Retrieval context | Tracked files | Relevant snippets sent to Groq when configured |
| Optional `GROQ_API_KEY` | Local environment/.env | Authentication to external provider | Process environment | Used by Groq Python client; never paste into chat, commit or log |

**Deletion:** Chat clear resets `messages`; profile reset clears `user_profile` and matching state; favorite mentors removed via their Delete UI. Streamlit session state expires when session/server closes; no guaranteed durability or immediate third-party data deletion after Groq API requests.

**Controls:** `.env` ignored by Git, secret pattern guard in CI, no app-level logging of raw prompts. This is a code-level dataflow inventory, not independent network capture, privacy impact assessment or provider retention audit. For real personal data, require consent, privacy policy and storage threat model before deployment.

Tracking: [NFR-03 #32](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/32), [NFR-04 #33](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/33).
