# Offline RAG Evaluation | Nhóm 6

**Phạm vi:** ứng dụng Streamlit ở root repo; TF-IDF cosine trên 3 tài liệu demo trong `knowledge_base/`. Đây là retrieval smoke test, không phải đánh giá đầy đủ chất lượng sinh câu trả lời hoặc LLM.

## Cách chạy

```bash
python -m scripts.evaluate_rag
python -m pytest tests/test_rag_evaluation.py -q
```

Bộ `nfr-09-v2` có **31 ca tổng cộng**: 18 câu có nguồn kỳ vọng và 13 câu ngoài tài liệu. Một ca hỏi tổng hợp yêu cầu cả `ai_project_guide.md` và `ai_study_guide.md` nằm trong top-k và được trích dẫn. Đây là các synthetic regression cases viết theo corpus hiện tại, không có blind split hoặc người gán nhãn độc lập.

- **Retrieval Recall@3 / Hit@3:** số câu có tài liệu kỳ vọng trong top 3.
- **Citation source-mapping precision:** số citation ID ánh xạ được tới nguồn nằm trong top-k truy xuất chia cho tổng citation ID. Một ca dương tính chỉ PASS nếu mọi ID đều ánh xạ hợp lệ và nguồn kỳ vọng xuất hiện ít nhất một lần; có thể trích nhiều nguồn được truy xuất.
- **Answer correctness proxy:** tỷ lệ các cụm từ bằng chứng kỳ vọng xuất hiện trong đoạn trích được dẫn; không đo tính đúng ngữ nghĩa của câu trả lời LLM.
- **No-evidence refusal:** số câu ngoài kho được từ chối mà không trả nguồn.
- **Retrieval latency:** đo riêng `KnowledgeBase.search(k=3)`, first-search và warm p50/p95. CLI chạy 100 lần warm mỗi truy vấn; không tính khởi tạo tiến trình, Streamlit, mạng hay LLM.

Evaluator cố định `client=None`; output được assert trong pytest và ghi ra CI. Dùng số in từ workflow của đúng SHA, không lấy số cũ làm kết quả của commit mới. Không thay đổi fixture chỉ để tăng điểm mà không ghi lại protocol và lý do.

## Giới hạn

Tập này chỉ dùng 3 tài liệu demo, câu hỏi được thiết kế theo cùng corpus và chưa được reviewer độc lập gán nhãn. Metric citation chỉ đo ánh xạ ID/nguồn và yêu cầu nguồn chuẩn xuất hiện trong citation; nó không xác minh từng claim được nguồn hỗ trợ hoặc nguồn được dẫn có entail câu trả lời. Answer correctness là evidence-term proxy; không thể suy ra hallucination rate, độ chính xác Groq hay chất lượng tổng quát. Prompt injection, truy vấn ngoài phân phối, từ đồng nghĩa và tải đồng thời cần benchmark riêng.

Ngưỡng retrieval TF-IDF là heuristic đã hiệu chỉnh trên corpus demo; cần tập holdout độc lập để đo false refusal và false grounding. Các số latency là mô tả trên máy chạy, không phải SLA hoặc production estimate.

Follow-up cho benchmark độc lập có reviewer gán nhãn: [Issue #83](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/83). Regression kiểm tra citation đa nguồn: [Issue #163](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/163).
