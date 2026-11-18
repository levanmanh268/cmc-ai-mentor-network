# Privacy data inventory - CMC AI Mentor Network

**Scope:** root Streamlit application at `app.py` for the classroom prototype.
**Issue:** [#178](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/178)
**Status:** DRAFT - requires independent review and CI evidence before closure.

This inventory describes code that is present in the repository. It is not an
independent provider privacy audit or evidence of Groq retention behavior.
Third-party retention is `UNKNOWN` unless an authoritative provider policy or
provider evidence is linked.

## 1. Components and actual paths

| Component | Actual path / field | Scope | Status | Reason |
| --- | --- | --- | --- | --- |
| Student profile | `app.py`, `profile_helpers.py`, `st.session_state["user_profile"]`: `name`, `year`, `field_interest`, `goals`, `bio` | One browser session | APPLICABLE | Fields are rendered by the profile form and retained in Streamlit session RAM. |
| Chat history | `app.py`, `st.session_state["messages"]` and `["general_messages"]` | One browser session | APPLICABLE | RAG and general chat have separate session histories. |
| Saved/favorite mentors | `app.py`, `st.session_state["favorite_mentors"]` | One browser session | APPLICABLE | Favorites are UI state and can be removed. |
| Session mentor drafts | `mentor_drafts.py`, `st.session_state["mentor_drafts"]` | One browser session | APPLICABLE | Draft fields are validated and held only in session state. |
| Local knowledge base | `rag_engine.py`, `knowledge_base/**/*.md` | Server/repository | APPLICABLE | Markdown is loaded directly from repository files; no vector database is used. |
| Groq API key, BYOK | `app.py` session password widget, `llm_client.py`, `GROQ_API_KEY` environment variable | Browser -> Streamlit server -> Groq | APPLICABLE | User key or server key is used only to construct a Groq client. |
| Groq inference | `general_chat.py`, `rag_engine.py`, `matching_engine.py` | External transfer after opt-in | APPLICABLE | Calls require `authorized_client` and explicit checkbox consent. |
| Accounts/authentication | Application code and configuration | Entire application | NOT APPLICABLE | There is no login, OAuth, account table or user identity record. |
| Persistent database | Application repository | Entire application | NOT APPLICABLE | No database package, account table or profile persistence implementation exists. |
| Persistent encryption | Application database/storage | Entire application | NOT APPLICABLE | No encrypted persistent data store exists to claim as evidence. |
| Mentor email/SMS delivery | `app.py` and Mentor matching modules | Entire application | NOT APPLICABLE | The prototype has no email, SMS or external mentor messaging integration. |
| Provider-independent retention | Groq service | Groq account/API | UNKNOWN | Provider-side retention and deletion policies are not independently evidenced by this repository. |
| Analytics/telemetry | Streamlit configuration | Hosted application | UNKNOWN | This inventory does not independently verify Render or Streamlit-host telemetry settings. |

## 2. Data inventory

| Data | Collection point | Purpose | Storage/lifetime | Transfer |
| --- | --- | --- | --- | --- |
| `name` | Profile text input | Optional profile display | `st.session_state`, session RAM | Not included in current RAG or Mentor matching prompt; no evidence of external transfer |
| `year` | Profile selectbox | Mentor experience-fit scoring | Session RAM | May be sent in a Mentor explanation request only after consent |
| `field_interest` | Profile text input | Matching and Mentor explanation | Session RAM | May be sent to Groq for a matching explanation after consent |
| `goals` | Profile text input | Matching and Mentor explanation | Session RAM | May be sent to Groq for a matching explanation after consent |
| `bio` | Profile text area | Matching text features | Session RAM | Not directly included in the current matching explanation |
| RAG question and history | Chat input and `messages` | Grounded answer/review | Session RAM | Question and retrieved Markdown excerpts may be sent to Groq after consent |
| General-chat question/history | Chat input and `general_messages` | Multiturn model response | Recent bounded context, session RAM | Recent chat can be sent to Groq after consent |
| Retrieved Markdown excerpts | `knowledge_base/**/*.md` | RAG evidence/context | Repository + session response sources | Relevant excerpts may be sent to Groq in RAG mode after consent |
| Saved mentors | Favorite button | Demo UI list | Session RAM | Not sent as a separate list by the current code |
| Mentor draft fields | Mentor draft form | Session-only demo Mentor pool | Session RAM | Draft fields are not sent merely by creating a draft |
| Mentor explanation context | Profile, selected Mentor and match score | Generate selected-match explanation | Constructed per request | Sent only after consent; current code omits profile name and student/Mentor bios |
| BYOK key | Sidebar password field | Authenticate a user Groq account | Session RAM on the Streamlit server; not chat history | Sent from Streamlit server to Groq for authorized calls |
| Server `GROQ_API_KEY` | Server environment or `.env` | Authenticate Groq client | Process environment | Used by Groq SDK for calls after consent |

The in-app profile notice states that profile data is session-only and may be
lost when the session ends. No account-level database or persistent profile
storage is claimed. Data in provider systems is not a local deletion target.

## 3. User-facing notice and opt-in

The actual consent checkbox is in the root sidebar:

- The label is **"Đồng ý gửi dữ liệu cần thiết cho tính năng đang dùng đến Groq"**.
- Its default is `False`, including when a server key or BYOK key is configured.
- The help text identifies general chat history, RAG retrieved excerpts and
  bounded profile/Mentor fields used for explanations.
- Turning consent off prevents new calls through `authorized_client=None`.
- Turning consent off does not revoke or delete requests already sent.
- The BYOK field is visually masked and is described as session-only.
- The UI does not claim browser-side encryption or encrypted persistent storage.

Consent is one gate, not an abuse, authentication or provider-retention control.

## 4. Third-party transfer and retention

| Destination | Applicable | Basis | Retention |
| --- | --- | --- | --- |
| Groq API | APPLICABLE | Python Groq client receives model messages after consent | UNKNOWN; not independently audited |
| Render hosting | APPLICABLE if deployed | App process and Streamlit session state run on Render | UNKNOWN; not independently audited |
| Streamlit telemetry | POSSIBLE | Hosting/configuration status is external to app logic | UNKNOWN; not independently audited |
| GitHub | NOT APPLICABLE to runtime user data | Repository contains code/docs, not this session data | Repository policy, not a provider-retention claim |

Do not write real API keys, passwords, PII or provider payload logs to GitHub,
screenshots or issue comments.

## 5. Local deletion controls

| Data | Control | Scope |
| --- | --- | --- |
| RAG history | "Xóa lịch sử hội thoại" | Clears `messages` in current session |
| General chat | "Xóa cuộc trò chuyện AI" | Clears `general_messages` in current session |
| Profile/matching state | "Đặt lại / xóa hồ sơ trong phiên" | Clears profile and derived matching state |
| Favorites | Delete button per mentor | Removes selected favorite from session |
| Mentor drafts | Delete UI for draft | Removes draft from session pool |
| Session/key data | Session end or process restart | May lose Streamlit session RAM data |

These controls delete local session copies only. They do not demonstrate
deletion by Groq or hosting providers.

## 6. Test evidence

### 6.1 Automated checks

Run:

```powershell
python -m pytest -q tests/test_real_ai_chat.py tests/test_end_to_end_flows.py tests/test_issue_batch.py tests/test_streamlit_ui.py
python -m pytest -q tests/test_privacy_inventory.py
```

The privacy regression test should verify:

| ID | Steps | Expected | Actual | Result |
| --- | --- | --- | --- | --- |
| PI-01 | Inspect the inventory and source paths | Required component/data paths exist and statuses are honest | To be filled after independent review | BLOCKED |
| PI-02 | Start AppTest with a configured key | Consent defaults off | Automated unit/browser coverage | PENDING |
| PI-03 | Leave consent off and submit chat/RAG/mentor action | No external provider call | Automated coverage | PENDING |
| PI-04 | Enable consent, submit each mode, then revoke | Only enabled/new calls reach the provider | Automated coverage | PENDING |
| PI-05 | Inspect Mentor explanation payload | Profile name and student/Mentor bios are omitted | Automated coverage | PENDING |
| PI-06 | Inspect third-party retention claims | No claim stronger than repository evidence; unknown retention is labeled | Source review | PENDING |

Do not replace this table with fabricated PASS evidence. Independent review must
record the reviewer, date, commit SHA and CI run link.

### 6.2 Evidence record

- Commit SHA: `ec3ef06` at local test start; update at the PR head.
- CI: PENDING - add workflow/run URL here after the PR is created.
- Independent reviewer: PENDING
- Review date: PENDING
- Steps/Expected/Actual/PASS/FAIL/SKIP/BLOCKED: PENDING for live-provider evidence
- Limits: no live Groq credential, provider retention policy capture or hosted
  Render telemetry capture is included in local unit evidence.

Existing overview: [PRIVACY_DATAFLOW.md](../PRIVACY_DATAFLOW.md). It should be
kept consistent with this canonical inventory.
