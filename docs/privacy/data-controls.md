# Personal data controls and retention

**Scope:** root Streamlit application at `app.py`.
**Issue:** [#179](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/179)
**Status:** DRAFT - closes only after independent review and CI evidence.

This document records local controls implemented by the application and the
retention boundaries they actually provide. It does not claim provider deletion,
database deletion or account deletion that is not implemented.

## 1. Components and actual paths

| Component | Actual path / state | Scope | Status | Reason |
| --- | --- | --- | --- | --- |
| Student profile | `app.py`, `profile_helpers.py`, `st.session_state["user_profile"]` | One browser/Streamlit session | APPLICABLE | Reset clears profile and derived matching state. |
| RAG chat history | `app.py`, `ui_helpers.py`, `st.session_state["messages"]` | One browser/Streamlit session | APPLICABLE | Clear action replaces the message list with an empty list. |
| General chat history | `app.py`, `st.session_state["general_messages"]` | One browser/Streamlit session | APPLICABLE | Clear action replaces the general-chat list with an empty list. |
| Favorite mentors | `app.py`, `st.session_state["favorite_mentors"]` | One browser/Streamlit session | APPLICABLE | Delete UI removes the selected favorite. |
| Session mentor drafts | `mentor_drafts.py`, `st.session_state["session_mentor_drafts"]` | One browser/Streamlit session | APPLICABLE | Draft delete removes only the current session draft. |
| Session state isolation | `st.session_state` in `app.py` | Separate browser sessions | APPLICABLE | Tests verify one AppTest session does not receive another session's profile/favorites. |
| Persistent user database | Application modules/configuration | Entire application | NOT APPLICABLE | No account, registration or database implementation exists. |
| Server account export/delete | Application modules/configuration | Entire application | NOT APPLICABLE | No account exists and no server-side export/deletion service is implemented. |
| Provider deletion request | Groq and hosting providers | External systems | NOT UNDER APP CONTROL | App clear actions stop local use but cannot demonstrate third-party deletion. |
| Provider retention period | Groq API/hosting | External systems | UNKNOWN | Retention must be evidenced by provider policy or an independent provider audit. |
| Encrypted persistent storage | Database/persistent storage | Entire application | NOT APPLICABLE | The prototype has no persistent user store to encrypt or claim. |

## 2. Implemented controls

| Control | Action | Preserved data |
| --- | --- | --- |
| Reset profile | `reset_profile_state()` clears `user_profile`, `top_matches` and `match_explanations` | Favorites and both chat histories remain |
| Clear RAG chat | `clear_chat_history()` clears `messages` | Profile, favorites and matching state remain |
| Clear general chat | The AI Assistant dialog clears `general_messages` | RAG chat, profile and favorites remain |
| Delete favorite | The favorite Delete button removes only one mentor | Profile and chat histories remain |
| Delete mentor draft | The draft Delete confirmation removes only that draft | Repository Mentor data remains unchanged |
| End or restart session | Streamlit session state/process lifecycle ends | Data may be lost; no guarantee of durability |

The profile reset UI says that profile/matching data will be deleted from the
current session. Chat clear actions state that they clear only the current
session. The UI is not a server account deletion feature.

## 3. Retention boundaries

- Profile, chat, favorites and mentor drafts are in Streamlit memory-backed
  `st.session_state`, not a database.
- Streamlit session lifetime is not a guaranteed retention or deletion SLA.
- Refresh, session expiry or process restart can remove session state.
- Groq requests are outside local data controls: revoking consent blocks new
  calls but does not erase payloads already sent.
- Provider logs, retention and deletion depend on Groq/hosting evidence and are
  `UNKNOWN` in this repository.
- There is no account export or right-to-delete workflow because no account or
  server user record exists.

Do not add a simulated account deletion claim or fabricate provider evidence.

## 4. Test evidence

### Automated tests

Run locally:

```powershell
python -m pytest -q tests/test_profile_helpers.py tests/test_ui_helpers.py tests/test_issue_batch.py tests/test_end_to_end_flows.py tests/test_mentor_drafts.py tests/test_privacy_data_controls.py
```

| ID | Steps | Expected | Actual | Result |
| --- | --- | --- | --- | --- |
| DC-01 | Reset a state containing profile/matches/favorites/chat | Profile/matches clear; favorites/chat remain | `test_reset_profile_clears_profile_and_matching_but_preserves_favorites_and_chat` | PASS |
| DC-02 | Clear RAG chat state containing profile/favorites/matches | RAG messages clear; other state remains | `test_clear_chat_history_preserves_profile_and_favorites` | PASS |
| DC-03 | Create a mentor draft in two separate state dictionaries | Draft exists only in the creating state | `test_creation_and_removal_are_session_scoped_and_repository_is_unchanged` | PASS |
| DC-04 | Use two independent AppTest sessions and set profile/favorite in one | The second session remains empty | `test_e2e04_independent_sessions_do_not_share_profiles` | PASS |
| DC-05 | Inspect the data-controls inventory and source UI | Required controls and honest `NOT APPLICABLE`/`UNKNOWN` limits are documented | `test_privacy_data_controls.py` | PASS |

Local targeted run completed with `42 passed in 6.41s`. The result is against
the local working tree, not yet a PR head or hosted CI run.

### Evidence record

- Local source SHA at issue work start: `ec3ef06`
- Local targeted test result: `42 passed in 6.41s`
- PR head SHA: PENDING
- CI run: PENDING
- Independent reviewer: PENDING
- Review date: PENDING
- Result: PENDING for PR/CI review
- Limits: unit/AppTest evidence does not prove hosted provider deletion,
  provider retention, browser/network transfer or hosted session isolation.

## 5. Independent review checklist

- [ ] Confirm every path and state key against the PR head.
- [ ] Confirm profile reset preserves favorites/chat as intended.
- [ ] Confirm RAG/general/favorite/draft controls remain session-only.
- [ ] Confirm no account/database export/delete claim appears.
- [ ] Confirm provider deletion/retention remains `UNKNOWN` unless evidenced.
- [ ] Link CI run, commit SHA and this test table in the PR.

Existing overview: [PRIVACY_DATAFLOW.md](../PRIVACY_DATAFLOW.md) and
[data-inventory.md](data-inventory.md).
