# Offline RAG Evaluation | Nhóm 6

**Phạm vi:** ứng dụng Streamlit ở root repo; hiện dùng TF-IDF cosine trên 3 Markdown tài liệu demo trong `knowledge_base/`. Không đánh đồng retrieval smoke test với LLM faithfulness hoặc năng lực NotebookLM.

## Phương pháp có thể lặp lại

```bash
python -m scripts.evaluate_rag
python -m pytest tests/test_rag_evaluation.py -q
```

Bộ [31 trường hợp, nfr-09-v1](../scripts/evaluate_rag.py) gồm 18 câu hỏi có expected source và 13 câu hỏi ngoài tài liệu. Các prompt là synthetic regression cases được viết theo corpus hiện tại; chưa có independent reviewer hoặc blind split. Số liệu được in từ chương trình và assert bởi CI.

- **Hit@3:** số câu hỏi có tài liệu kỳ vọng nằm trong 3 nguồn retrieval đầu / 18.
- **No-evidence refusal:** số câu ngoài kho trả về 0 nguồn + `no-evidence` / 13.
- **Retrieval latency:** `KnowledgeBase.search(k=3)` được đo riêng trên cả 31 query. Mỗi query có một lần search đầu sau khi knowledge base được nạp và 100 lần lặp warm; báo cáo p50 (median) và p95 theo nearest-rank trên các mẫu tương ứng. Đây chỉ là TF-IDF retrieval, không gồm khởi tạo process/index, tạo câu trả lời, Streamlit/browser, mạng hay LLM.
- Kịch bản offline, `client=None`, deterministic; không đánh giá chất lượng sinh văn bản từ Groq, không đánh giá semantic entailment ở cấp claim.
- Các truy vấn được thiết kế theo đúng kho demo đang dùng; không phải test độc lập trên corpus mới và không được báo cáo như độ chính xác tổng quát.

**Kết quả local (branch NFR, Windows, Python 3.14.5, 3 docs / 4 chunks):** `Hit@3: 18/18; No-evidence: 13/13`. Lần chạy `python -X utf8 -m scripts.evaluate_rag` đo 31 first-search samples: p50 **0.798 ms**, p95 **5.991 ms**; 3,100 warm samples (100/query): p50 **1.166 ms**, p95 **2.958 ms**. Các số phụ thuộc máy và tải nền, không phải SLA hoặc ngưỡng pass/fail. Đây là kết quả hồi quy trên máy local, không thay thế kết quả CI Python 3.11 hoặc đánh giá độc lập; đọc dòng output từ workflow chạy đúng SHA trước khi ghi nhận kết quả CI.

**Known limitations:** bộ này không phải tập gold được gán nhãn độc lập, không đo claim-level citation precision, groundedness hay hallucination rate. Từ đồng nghĩa, query đảo ngữ cảnh, ngôn ngữ khác và prompt injection chưa có benchmark đại diện. Score TF-IDF `0.06` kết hợp OOV/query-term coverage `0.55` là heuristic hiệu chỉnh sơ bộ trên corpus demo; cần benchmark ngoài phân phối để đo false-refusal và false-grounding. Bộ tài liệu chỉ có 3 docs / 4 chunks; sample latency mô tả corpus demo, không dự đoán corpus lớn, tải đồng thời hay latency production/cloud. Citation hợp lệ theo ID không chứng minh mọi khẳng định được nguồn hỗ trợ; vì vậy không thể kết luận NFR-09 đạt chỉ từ các con số này.

Tracking: [Issue #17](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/17).
