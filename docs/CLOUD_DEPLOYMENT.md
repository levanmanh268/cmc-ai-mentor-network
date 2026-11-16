# Cloud deployment | CMC AI Mentor Network

## Public deployment (classroom prototype)
- Streamlit app: https://cmc-ai-mentor-network-group6.onrender.com
- HTTP probe: https://cmc-ai-mentor-network-group6.onrender.com/_stcore/health
- Render dashboard: https://dashboard.render.com/web/srv-db7db1vavr4c73fq899g
- Runtime: Python on Render Free, Singapore, branch `main`, `autoDeploy=yes`.
- Public HTTPS is provided by Render. The code is a modular monolith, **not** a microservice fleet or a durable multi-user SaaS.

## Build and run configuration

| Setting | Value |
| --- | --- |
| Repository | `https://github.com/levanmanh268/cmc-ai-mentor-network` |
| Branch | `main` |
| Build | `python -m pip install --upgrade pip && python -m pip install -r requirements.txt` |
| Start | `python -m streamlit run app.py --server.headless true --server.address 0.0.0.0 --server.port $PORT` |
| Secret / LLM | `GROQ_API_KEY` empty for public offline demo; do not insert keys in repo |
| Region / plan | Singapore / Free |

## Independent smoke verification

```bash
curl --fail --show-error --location \
  https://cmc-ai-mentor-network-group6.onrender.com/_stcore/health

curl --fail --show-error --location \
  https://cmc-ai-mentor-network-group6.onrender.com/ -o index.html
```

Expected `/_stcore/health` body: `ok`. Root page should return HTML containing a Streamlit shell. These checks prove the HTTP process is reachable; they do **not** validate all features, user sessions, correct AI claims or load handling.

## Deploy / Release chain

1. Merge only reviewed PR with Linux/Windows tests and 5 Mermaid diagram renders passing.
2. Render automatically builds the newest `main` commit and runs Streamlit.
3. Inspect Render's **Deploys** and app logs. A deploy is confirmed only when it reaches `live`, with no startup errors.
4. Open UI manually and follow [UAT_CHECKLIST](UAT_CHECKLIST.md); if nobody has signed off, retain `Not Run`.
5. Separate GitHub Action `Publish Cloud Classroom v0.2.0` publishes immutable `v0.2.0` only after successful `main` CI and HTTP cloud health/root probe, then appends direct proof to Release notes.
6. Confirm the Render `live` deployment's git SHA and GitHub release tag/CI head SHA refer to the exact intended revision. HTTP health **alone** cannot prove deploy SHA equality.

## Free tier / privacy caveats

Cold starts may be slow; limited CPU/RAM, no SLA, and memory-backed `st.session_state` can disappear when the instance restarts. Do not treat favorites, chat or profile as persistently stored accounts.

Cloud demo runs without Groq key. If a maintainer later sets `GROQ_API_KEY`, the UI requires an explicit opt-in to send question/context/matching data externally. Users must not upload confidential personal records. The test/demo mentor dataset is fictional.

**This is a student prototype, not production-ready.** Performance P95, independent groundedness, privacy review and human UAT require their own evidence. Latest docs: [architecture](architecture.md) and [non-functional requirements](non-functional-requirements.md).

## Real LLM chat activation (Issue #63)

The site provides **two separate modes**: General AI conversation (requires Groq GPT-OSS 120B) and grounded Markdown retrieval. The session can supply an ephemeral Groq API key through a masked Streamlit sidebar field; the key is transmitted to the Render server over the hosted Streamlit session, temporarily held in memory, and used after the user opts in. Do **not** paste keys into chat or source control. The administrator can alternatively set `GROQ_API_KEY` in **Render → Environment** without committing credentials; consider authentication and rate limits before public shared-key usage.

`openai/gpt-oss-120b` is the default model for all online paths. Missing key or no consent means general chat is disabled; grounded document RAG remains offline-capable. An HTTP health check never establishes that AI inference with a real key works. Tests mock Groq SDK; to prove end-to-end model responses, use a *real nonproduction key and consent* in a controlled session and inspect the response, without sharing the key in logs/screenshots.
