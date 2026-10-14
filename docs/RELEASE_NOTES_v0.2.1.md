# v0.2.1 | Offline Greeting UX Hotfix

**Nhóm 6 — CMC AI Mentor Network** · Classroom prototype patch on top of v0.2.0.

## 🐛 Lỗi đã sửa (Issue #60)

Người dùng gõ `hello cậu` trong **AI Assistant** của bản cloud `v0.2.0` nhưng nhận câu trả lời “chưa tìm thấy bằng chứng trong tài liệu”. RAG TF-IDF trước đây coi *mọi tin nhắn* là câu hỏi tài liệu, dẫn đến lời chào bị từ chối sai ngữ cảnh.

Bản vá này:
- Nhận diện **chào hỏi/cảm ơn/câu hỏi trợ lý làm được gì** bằng tập ý định ngắn và cố định, trả template địa phương với trạng thái `local-social`. Không gọi Groq, không sinh nguồn giả.
- Không chặn câu hỏi có nội dung: `hello cậu, cho tớ hỏi về ...` vẫn qua luồng RAG; câu hỏi không có bằng chứng vẫn trả `no-evidence`.
- Nêu rõ **cloud offline**: chỉ chào hỏi cơ bản và tra cứu **3 tài liệu Markdown demo**. Để có hội thoại do LLM sinh ra cần cấu hình secret Groq ở môi trường và người dùng opt-in.
- Cập nhật trạng thái giao diện, README, 5 sơ đồ Mermaid kiến trúc và regression tests.

**Ví dụ tự kiểm thử**:
1. `hello cậu` → lời chào tự nhiên, trạng thái chào hỏi cục bộ, không có citation.
2. `Bạn làm được gì?` → giải thích đúng khả năng và giới hạn offline.
3. `Quy trình xử lý một Issue GitHub như thế nào?` → có nguồn Markdown nếu retrieval tìm được bằng chứng.
4. `Công thức quang hợp thực vật?` → `no-evidence`, không tự trả kiến thức ngoài kho.

## Cần hiểu đúng giới hạn

Đây **không phải** một LLM mới hoặc sản phẩm tương đương NotebookLM/Gemini. Tính năng chào hỏi chỉ là logic xác định. Khả năng retrieval, groundedness và bảo mật vẫn cần các benchmark/UAT/NFR riêng. Phiên Streamlit không lưu hồ sơ hoặc chat lâu dài.

## Bản cloud, mã nguồn và bằng chứng

- **Demo:** https://cmc-ai-mentor-network-group6.onrender.com
- **Endpoint:** https://cmc-ai-mentor-network-group6.onrender.com/_stcore/health
- **Issue:** https://github.com/levanmanh268/cmc-ai-mentor-network/issues/60
- **Kiến trúc:** https://github.com/levanmanh268/cmc-ai-mentor-network/blob/main/docs/architecture.md
- **Test:** `python -m pytest -q` và `python -m pytest tests/test_chat_intents.py -q`

Release workflow thêm link GitHub CI/commit của bản vá sau khi `main` xanh, kiểm tra public HTTP health/root và tạo tag bất biến `v0.2.1`. Render tự triển khai `main`, tình trạng phiên bản đang chạy phải được xác minh riêng qua Render Deploys (không suy luận từ HTTP 200).

**Bản trước:** [v0.2.0](https://github.com/levanmanh268/cmc-ai-mentor-network/releases/tag/v0.2.0).
