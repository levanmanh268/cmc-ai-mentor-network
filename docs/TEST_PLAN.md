# Test Plan | CMC AI Mentor Network

## Phạm vi
Prototype Streamlit + RAG + matching, không bao gồm 6 portfolio labs độc lập. Môi trường Python 3.11+, offline không cần API key.

## Chạy
```bash
python -m pip install -r requirements.txt
python -m py_compile app.py ui_helpers.py profile_helpers.py llm_client.py rag_engine.py matching_engine.py mentors_data.py mentor_data_diagnostics.py ingest.py
python -m pytest -q
python mentor_data_diagnostics.py
python -m scripts.evaluate_rag
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
| Release/docs | sơ đồ Mermaid | Chromium render cả hai phiên bản | `scripts/validate_mermaid.mjs`, CI |

**Evidence chuẩn:** đường dẫn workflow run của đúng SHA commit, số tests pass/fail trong log, hạn chế thủ công nếu chưa chạy. CI chạy Linux và Windows nhưng không có nghĩa đã kiểm thử mọi phiên bản trình duyệt, accessibility hoặc tải đồng thời.

Issue liên quan [#19](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/19), [#34](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/34), [#39](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/39).
