# FINAL DEFENSE: Adversarial Readiness Gate — Group 6

**Due date:** 20/10/2026. **Audit on:** 19/10/2026. **Scope:** root Streamlit classroom app only; independent portfolio labs are NOT integrated. These findings are a formal *risk register*, not a certificate that the application is 100% bug-free.

## P0 — Must be proven on the actual demonstration website

1. **AI thật:** Open AI Assistant → 🤖 Trò chuyện AI. If the admin set Render `GROQ_API_KEY`, user must tick explicit consent (or user enters a private per-session key). Press **🧪 Kiểm tra AI thật ngay**. **PASS ONLY** if there is a real provider-generated content response with model name and no authentication/quota error. This is a network request and consumes provider quota. A static greeting or passing HTTP health is **not** evidence of real model intelligence.
2. **Multi-turn:** after the probe, ask "Tớ đang học cấu trúc dữ liệu Python. Nêu 2 ý." then "Ở câu trước tớ đang học môn nào?" Confirm model actually uses preceding user/assistant context. Not proving reasoning quality or parity with ChatGPT.
3. **Privacy:** uncheck consent → general-chat input disabled and new provider calls cannot be made. Never expose API key in notes/screenshots/logs. Public shared key requires authentication and *server-side* quotas before general public use. The 30-message session counter is **only a classroom safety nudge**, bypassable by creating new sessions, not anti-abuse.
4. **RAG:** switch 📚 Hỏi đáp tài liệu; ask "Quy trình xử lý một issue GitHub là gì?" and verify retrieved sources displayed. Ask "Công thức quang hợp thực vật?" → no-evidence (depending on the demo corpus); if LLM is enabled, answers must cite returned source ID. Citation syntax alone is not semantic verification.
5. **Mentor:** fill profile (year, interests, goals), click Save; open Tìm Mentor → apply field/support filters → check top-3 matching, explanations and Save/delete favorites. These are **demo mentor records**, not real mentorship reservations.
6. **Session:** refresh/restart may lose data; this is documented, not a reliable account database. Browser UAT is still manual; automated Streamlit AppTest does not simulate a human or real hosted WebSocket.

## Automated gates (evidence is the specific run, not a blanket claim)
- `python -m pip install -r requirements.txt`
- `python -m pytest -q`
- `python mentor_data_diagnostics.py`
- `python -m scripts.evaluate_rag`
- `python -m scripts.final_smoke_audit`
- `python -m streamlit run app.py` plus `/_stcore/health`
- GitHub CI on **exact merged SHA**: Linux tests, Windows tests, Mermaid CLI 10.9.1/11.17.0 and HTTP startup.
- Render latest deploy = same SHA, status `live`, not just `build_success`. Cloud HTTP `/_stcore/health` and root page 200.
- New immutable GitHub prerelease tag only after trusted `main` CI and cloud HTTP; tag SHA = deployed SHA. **Even perfect CI cannot show real API key works without a live call.**
- Performance script samples 50 calls per CPU-only local task after warmup, reports median/p95, **not** a cloud/network/model SLA or concurrency benchmark; no pre-agreed acceptance threshold.

## Risk register (adversarial teacher questions)

| Severity | Risk / what the teacher could ask | Observed limit / defense |
| --- | --- | --- |
| **P0** | "Does your AI actually answer questions?" | **Blocked until a valid Groq credential + consent + live probe.** Offline chat will not pretend to be an LLM. |
| **P0** | "Can anyone open it without supplying a key?" | Only if the admin configures a working server `GROQ_API_KEY`; each browser must still consent. No free GPU on Render Free. |
| **P1** | "Will a public API key be abused?" | Yes without auth/server quotas. Per-session counter resets on reconnect and **is not secure rate limiting**. Do not publish unrestricted shared-key service. |
| **P1** | "Are its answers hallucination-free like NotebookLM?" | No. General AI has no claim-level verification. RAG validates citation *membership*, not semantic entailment; three small Markdown demo docs. |
| **P1** | "Does it have NotebookLM audio, video, web search, uploads, mind maps?" | No. None of those can be claimed for this root app. It is a bounded classroom demo and mentor matching app, **not NotebookLM parity**. |
| **P1** | "Are users' profiles durable?" | No. Session State RAM only; may be lost when WebSocket/process restarts. No login/DB, no account-level privacy isolation audit. |
| **P1** | "Is privacy audited?" | No independent provider retention/penetration test; BYOK key resides in Render server session memory. Consent stops *new* calls only. |
| **P2** | "Is performance proven?" | Small CPU-only p50/p95 sample is reproducible. No browser/cloud load test, no inference SLA or cost tests, no NFR pass threshold. |
| **P2** | "Has a human tested all browser paths?" | Manual UAT required on the actual link. Tests mock provider to check routing, not model output quality. |
| **P2** | "Are all issues resolved?" | No; issue tracker NFR-01 through NFR-10 and feature #63 require scoped evidence/owner acceptance. Never silently close unverified issues. |

## Suggested 3-minute defense (truthful and reproducible)
1. Show dashboard and architecture: a **modular Streamlit monolith** with deterministic retrieval, optional Groq GPT-OSS LLM and mentor scoring (not microservices).
2. Activate real AI (credential not visible, consent enabled) → click **Kiểm tra AI thật ngay** → show real response, then multi-turn knowledge question. If 401/429 appears, **do not fake** an online response; explain key/rate limits and switch to deterministic offline RAG demo.
3. Switch to grounded documentation and show both positive citation and no-evidence refusal.
4. Demonstrate profile → mentor search/filter → favorite and explain score.
5. Show CI 4/4 and immutable GitHub release, then say: "Trạng thái CI PASS xác nhận test tự động; trả lời AI thực được xác nhận riêng bởi bài probe; chưa khẳng định hallucination bằng 0 hay hội thoại ngang mô hình thương mại."

## Deployment and handoff
- Live app: https://cmc-ai-mentor-network-group6.onrender.com
- Cloud dashboard: https://dashboard.render.com/web/srv-db7db1vavr4c73fq899g
- Model key: set `GROQ_API_KEY` in Render Environment (never paste into GitHub or chat).
- Issue verification #67: https://github.com/levanmanh268/cmc-ai-mentor-network/issues/67
- Feature live-inference acceptance #63: https://github.com/levanmanh268/cmc-ai-mentor-network/issues/63

**Do not declare P0 online-inference green until someone has pressed the probe with a valid credential on the deployed URL and observed a real model response.**
