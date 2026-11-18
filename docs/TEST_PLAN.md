# Test Plan | CMC AI Mentor Network

## Phạm vi
Prototype Streamlit + RAG + matching, không bao gồm 6 portfolio labs độc lập. Môi trường Python 3.11+, offline không cần API key.

## Chạy
```bash
python -m pip install -r requirements-test.txt
python -m scripts.secret_guard
python -m py_compile app.py general_chat.py chat_intents.py ui_helpers.py profile_helpers.py llm_client.py rag_engine.py matching_engine.py mentors_data.py mentor_data_diagnostics.py ingest.py scripts/evaluate_rag.py scripts/final_smoke_audit.py scripts/benchmark_scaling.py scripts/testing_report.py
python -m pytest -q
python mentor_data_diagnostics.py
python -m scripts.evaluate_rag
python -m scripts.final_smoke_audit
python -m scripts.benchmark_scaling --output reports/scaling.json
python -m streamlit run app.py
```

## Ma trận regression
| Lớp | Input / sự cố | Kỳ vọng | Test |
| --- | --- | --- | --- |
| RAG | knowledge_base trống | không crash, trả `no-evidence` | `tests/test_rag_engine.py` / bổ sung |
| RAG | query trống / ngoài knowledge base | `no-evidence` | `tests/test_rag_engine.py` |
| RAG | citation [S99] hay không citation | không công nhận online, `offline-fallback` | `tests/test_rag_engine.py`, `tests/test_issue_batch.py` |
| RAG | LLM ném exception | fallback nguồn offline, không lộ traceback | `tests/test_rag_engine.py`, `tests/test_real_ai_chat.py` |
| Mentor | dữ liệu sai field/ID/kiểu | validator hoặc diagnostic báo lỗi | `tests/test_matching_engine.py`, `tests/test_mentor_data_diagnostics.py` |
| Mentor | lọc không có kết quả | trả list rỗng và UI thông báo | `tests/test_issue_batch.py` |
| UI | save mentor, rerun | kết quả và favorites giữ trong phiên | `tests/test_streamlit_ui.py` |
| UI | hồ sơ sai, chat history cũ | thông báo rõ; no crash | `tests/test_issue_batch.py` |
| Quyền riêng tư | có key nhưng chưa đồng ý gửi dữ liệu | offline theo mặc định, tắt lại chặn yêu cầu mới | `tests/test_issue_batch.py` |
| General chat (fake API) | gửi 2 câu liên tiếp → history user/assistant, không fake offline | `tests/test_final_defense_probe.py` |
| Groq consent/probe (fake API) | chưa đồng ý không gọi, đã đồng ý probe gọi provider, 401 không lộ key | `tests/test_final_defense_probe.py` |
| Demo quota | sau 30 yêu cầu trong 1 session, input chat disabled (không phải server rate limit) | `tests/test_final_defense_probe.py` |
| CPU latency sample | Một cold request + 100 warm samples/operation; p50/p95, phần cứng, dataset; mentor pool demo + synthetic scale; không áp dụng cloud/LLM | `scripts/final_smoke_audit.py`, `scripts/benchmark_mentor_ranking.py`, `tests/test_final_smoke_audit.py`, `tests/test_mentor_ranking_benchmark.py`, `docs/MENTOR_RANKING_BENCHMARK.md` |
| Data scale | 3/30/100 tài liệu và 10/100/500 mentor, 100 samples mỗi quy mô | `scripts/benchmark_scaling.py`, `tests/test_benchmark_scaling.py` |
| Coverage gate | Line coverage tối thiểu 90% cho 7 module cốt lõi; không bao gồm branch coverage | CI `pytest-cov --cov-fail-under=90` |
| Source lint | Ruff `E4,E7,E9,F` trên module cốt lõi cùng `py_compile` | `.github/workflows/ci.yml` |
| Secret guard | Fake credential patterns fail detection test; tracked files clean | `tests/test_secret_guard.py`, `scripts/secret_guard.py` |
| NFR-09 retrieval fixture | 31 versioned cases: expected-source hit, no-evidence refusal, TF-IDF retrieval p50/p95; not semantic faithfulness or cloud latency | `tests/test_rag_evaluation.py`, `scripts/evaluate_rag.py` |
| Release/docs | sơ đồ Mermaid | Chromium render cả hai phiên bản | `scripts/validate_mermaid.mjs`, CI |

## NFR traceability

| NFR | Automated evidence | Human/operational evidence still required |
| --- | --- | --- |
| 01 Performance | `scripts/final_smoke_audit.py` (cold + 100 warm samples) | Approve threshold; capture target hardware and production/browser latency if required |
| 02 Credential security | `scripts/secret_guard.py`, `tests/test_secret_guard.py`, CI | Review Git history and confirm exposed-key revocation with repository owner |
| 03 Privacy | consent/fallback tests in `tests/test_issue_batch.py` and `tests/test_final_defense_probe.py` | UAT consent comprehension; provider/network retention audit |
| 04 Data reliability | `tests/test_streamlit_ui.py`, `tests/test_issue_batch.py` | Confirm session-only prototype is acceptable; persistent storage is not implemented |
| 05 Compatibility | Linux and Windows jobs in `.github/workflows/ci.yml` | Browser/device matrix beyond CI runners |
| 06 Usability | Scenario definitions in `docs/UAT_CHECKLIST.md` | Five real participants and recorded completion/time observations |
| 07 Maintainability | `tests/test_architecture_docs.py`, compile and regression CI | Issue/PR review and human architecture review |
| 08 Error handling | RAG, matching, profile and fake-provider regression tests | Review any new production/provider failure mode |
| 09 AI quality | Versioned offline retrieval/refusal fixture in `scripts/evaluate_rag.py` | Independent gold labels and claim-level groundedness review |
| 10 Testability | This matrix, documented commands and required CI checks | Attach successful workflow URL and record any failed test reproduction |

**Evidence chuẩn:** đường dẫn workflow run của đúng SHA commit, số tests pass/fail trong log, hạn chế thủ công nếu chưa chạy. Test cases, issue traceability, actual-run report, and known limitations are tracked in `TEST_CASES.md`, `TRACEABILITY_MATRIX.md`, `TEST_REPORT.md`, and `KNOWN_ISSUES.md`. RAG metrics and limitations are in [RAG Evaluation](RAG_EVALUATION.md) and `RAG_EVALUATION_REPORT.md`. CI chạy Linux và Windows nhưng không có nghĩa đã kiểm thử mọi phiên bản trình duyệt, accessibility, tải đồng thời hoặc đạt SLA. UAT do người thật thực hiện phải được ghi riêng; không suy ra PASS từ test tự động.

Issue liên quan [#19](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/19), [#34](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/34), [#39](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/39).

**Chốt bảo vệ (20/10/2026):** xem [FINAL_DEFENSE_GATE.md](FINAL_DEFENSE_GATE.md), đặc biệt yêu cầu live Groq API probe sau khi cấu hình key. CI/fake client không chứng minh đã có inference online trên cloud.
