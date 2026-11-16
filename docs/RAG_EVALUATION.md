# Offline RAG Evaluation | Nhóm 6

**Phạm vi:** ứng dụng Streamlit ở root repo; hiện dùng TF-IDF cosine trên 3 Markdown tài liệu demo trong `knowledge_base/`. Không đánh đồng retrieval smoke test với LLM faithfulness hoặc năng lực NotebookLM.

## Phương pháp có thể lặp lại

```bash
python -m scripts.evaluate_rag
python -m pytest tests/test_rag_evaluation.py -q
```

Bộ [14 trường hợp](../scripts/evaluate_rag.py) gồm 9 câu hỏi có expected source và 5 câu hỏi ngoài tài liệu. Số liệu được **in từ chương trình** và assert bởi CI, không phải số đo người viết tự đoán.

- **Hit@3:** số câu hỏi có tài liệu kỳ vọng nằm trong 3 nguồn retrieval đầu / 9.
- **No-evidence refusal:** số câu ngoài kho trả về 0 nguồn + `no-evidence` / 5.
- Kịch bản offline, `client=None`, deterministic; không đánh giá chất lượng sinh văn bản từ Groq, không đánh giá semantic entailment ở cấp claim.
- Các truy vấn được thiết kế theo đúng kho demo đang dùng; không phải test độc lập trên corpus mới và không được báo cáo như độ chính xác tổng quát.

**Kết quả:** Cần đọc dòng `Hit@3: X/9; No-evidence: Y/5` từ GitHub CI hoặc chạy local. Nếu test fail, báo cáo PASS/FAIL theo thực tế và xem chi tiết từng query. Không sửa câu hỏi chỉ để tối đa hóa điểm mà không ghi nhận thay đổi protocol.

**Known limitations:** từ đồng nghĩa, query đảo ngữ cảnh, ngôn ngữ khác và prompt injection chưa có benchmark đại diện. Score TF-IDF `0.06` kết hợp OOV/query-term coverage `0.55` là heuristic hiệu chỉnh sơ bộ trên corpus demo; cần benchmark ngoài phân phối để đo false-refusal và false-grounding. Citation hợp lệ theo ID không chứng minh mọi khẳng định được nguồn hỗ trợ.

Tracking: [Issue #17](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/17).
