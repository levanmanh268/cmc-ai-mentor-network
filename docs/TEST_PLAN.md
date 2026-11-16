# Test Plan | CMC AI Mentor Network

## Phạm vi
Prototype Streamlit + RAG + matching, không bao gồm 6 portfolio labs độc lập. Môi trường Python 3.11+, offline không cần API key.

## Chạy
```bash
python -m pip install -r requirements.txt
python -m py_compile app.py general_chat.py chat_intents.py ui_helpers.py profile_helpers.py llm_client.py rag_engine.py matching_engine.py mentors_data.py mentor_data_diagnostics.py ingest.py scripts/final_smoke_audit.py
python -m pytest -q
python mentor_data_diagnostics.py
python -m scripts.evaluate_rag
python -m scripts.final_smoke_audit
python -m streamlit run app.py
```

## Ma trận regression
| Lớp | Input / sự cố | Kỳ vọng | Test |
| --- | --- | --- | --- |
| RAG | knowledge_base trống | không crash, trả `no-evidence` | `tests/test_rag_engine.py` / bổ sung |
| RAG | query trống / ngoài knowledge base | `no-evidence` | `tests/test_rag_engine.py` |
| RAG | citation [S99] hay không citation | không công nhận online, `offline-fallback` | `tests/test_rag_engine.py`, `tests/test_issue_batch.py` |
| RAG | LLM ném exception | fallback nguồn offline, không lộ traceback | `tests/test_rag_engine.py` |
| Mentor | dữ liệu sai field/ID/kiểu | validator hoặc diagnostic báo lỗi | `tests/test_matching_engine.py`, `tests/test_mentor_data_diagnostics.py` |
| Mentor | lọc không có kết quả | trả list rỗng và UI thông báo | `tests/test_issue_batch.py` |
| UI | save mentor, rerun | kết quả và favorites giữ trong phiên | `tests/test_streamlit_ui.py` |
| UI | hồ sơ sai, chat history cũ | thông báo rõ; no crash | `tests/test_issue_batch.py` |
| Quyền riêng tư | có key nhưng chưa đồng ý gửi dữ liệu | offline theo mặc định, tắt lại chặn yêu cầu mới | `tests/test_issue_batch.py` |
| General chat (fake API) | gửi 2 câu liên tiếp → history user/assistant, không fake offline | `tests/test_final_defense_probe.py` |
| Groq consent/probe (fake API) | chưa đồng ý không gọi, đã đồng ý probe gọi provider, 401 không lộ key | `tests/test_final_defense_probe.py` |
| Demo quota | sau 30 yêu cầu trong 1 session, input chat disabled (không phải server rate limit) | `tests/test_final_defense_probe.py` |
| CPU latency sample | 50 samples/operation, p50/p95 trên local CPU; không áp dụng cloud/LLM | `scripts/final_smoke_audit.py` |
| Release/docs | sơ đồ Mermaid | Chromium render cả hai phiên bản | `scripts/validate_mermaid.mjs`, CI |

**Evidence chuẩn:** đường dẫn workflow run của đúng SHA commit, số tests pass/fail trong log, hạn chế thủ công nếu chưa chạy. CI chạy Linux và Windows nhưng không có nghĩa đã kiểm thử mọi phiên bản trình duyệt, accessibility hoặc tải đồng thời.

Issue liên quan [#19](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/19), [#34](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/34), [#39](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/39).

**Chốt bảo vệ (20/10/2026):** xem [FINAL_DEFENSE_GATE.md](FINAL_DEFENSE_GATE.md), đặc biệt yêu cầu live Groq API probe sau khi cấu hình key. CI/fake client không chứng minh đã có inference online trên cloud.
