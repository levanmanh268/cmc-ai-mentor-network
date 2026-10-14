# CMC AI Mentor Network v0.3.0 | Real LLM Chat Prototype

**Nhóm 6, Đại học CMC — 14/10/2026.** Đây là phiên bản **classroom pre-release** tích hợp một mô hình ngôn ngữ thật (thông qua API của Groq) vào ứng dụng Streamlit. Không phải sản phẩm chính thức của OpenAI, Google hay Anthropic; **không được tuyên bố ngang ChatGPT/Gemini/Claude** về tổng thể.

## Truy cập
- **Cloud:** https://cmc-ai-mentor-network-group6.onrender.com
- **Health:** https://cmc-ai-mentor-network-group6.onrender.com/_stcore/health
- **Code:** https://github.com/levanmanh268/cmc-ai-mentor-network

## Hai chế độ AI riêng biệt
1. **🤖 Trò chuyện AI** (mặc định): mô hình **`openai/gpt-oss-120b` qua Groq**, có khả năng sinh câu trả lời ngôn ngữ tự nhiên, hỗ trợ nhiều lượt và giữ tối đa 16 tin nhắn / 12.000 ký tự lịch sử gần nhất trong phiên. Có thể hỏi toán, Python, AI, viết nội dung, hỏi tiếp về ngữ cảnh trước đó. **Không có web search**, không có file upload, không có trí nhớ qua session.
2. **📚 Hỏi đáp tài liệu**: giữ luồng RAG TF-IDF theo Markdown và nguồn tham khảo `[S1]`…, relevance và trạng thái trả lời. Trả `no-evidence` khi thiếu nguồn. Việc citation ID hợp lệ **không** có nghĩa mọi phát biểu đã được kiểm chứng ngữ nghĩa. Lịch sử tách riêng hoàn toàn khỏi chế độ Trò chuyện AI.

## 🔑 Cách sử dụng AI thật
- **Cách 1 (BYOK):** mở website, dán **Groq API key của chính cậu** trong ô mật khẩu ở sidebar, rồi đánh dấu **Đồng ý gửi câu hỏi, lịch sử chat và ngữ cảnh đến Groq**. Website chỉ cho phép gửi yêu cầu tới mô hình sau khi đồng ý; key giữ tạm trong session của máy chủ Streamlit trên Render (không phải khóa chỉ nằm trong máy người dùng).
- **Cách 2 (quản trị viên):** cấu hình biến môi trường `GROQ_API_KEY` trong dashboard Render, không đẩy key lên GitHub. Nếu dùng cho công chúng, cần xác thực, hạn mức riêng, kiểm soát lạm dụng và theo dõi chi phí trước khi bật. Mỗi phiên vẫn phải opt-in.
- **Không có key:** ứng dụng vẫn mở, Mentor Matching và RAG offline vẫn dùng được, **chế độ Trò chuyện AI không sinh trả lời**. Không dùng câu trả lời cố định giả làm LLM.
- **Nguồn API key:** https://console.groq.com/keys
- API có rate limits/quota và chi phí theo chính sách nhà cung cấp. Không đăng API key trên ảnh, GitHub issue hay tin nhắn.
- Groq xử lý dữ liệu câu hỏi/hội thoại khi cậu đồng ý; việc xóa lịch sử trong Streamlit không tự xóa dữ liệu đã gửi tới Groq.

## Tính năng/khắc phục kỹ thuật
- Thay model mặc định cũ bằng `openai/gpt-oss-120b`, định dạng tham số `include_reasoning=False` tương thích GPT-OSS (không trả nội dung suy luận nội bộ).
- `general_chat.py`: tạo messages user/assistant có context, giới hạn token/chiều dài, loại vai trò không hợp lệ, không đưa lỗi từ nhà cung cấp vào lịch sử model; xử lý lỗi kết nối, invalid key, 429, 500… mà không lộ nội dung exception.
- API key nhập qua Streamlit password input và opt-in mặc định tắt; không hardcode key; không log key, nội dung chat.
- `docs/architecture.md` phiên bản 2.5 với 5 sơ đồ Mermaid; `docs/PRIVACY_DATAFLOW.md` xác nhận BYOK key được truyền tới máy chủ Render và sống trong session RAM.

## GitHub & bằng chứng
- [Feature Issue #63](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/63)
- [Feature PR #64](https://github.com/levanmanh268/cmc-ai-mentor-network/pull/64)
- [Release Issue #65](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/65)
- Nền trước: [v0.2.1](https://github.com/levanmanh268/cmc-ai-mentor-network/releases/tag/v0.2.1)
- Chạy local: `python -m pip install -r requirements.txt` sau đó `python -m streamlit run app.py`; kiểm thử offline: `python -m pytest -q`.

**Kiểm thử đã thực hiện trên PR #64:** kiểm thử unit và Streamlit AppTest bằng fake Groq client, không có key thật. Giới hạn quan trọng: **không thể xác nhận model trả lời end-to-end ngoài mạng khi chưa có Groq API key thật**; CI/health và việc ứng dụng chạy không chứng nhận độ chính xác hoặc tính phí của API. Để nghiệm thu AI thật cần chạy vài câu thử trong session đã nhập key (không chia sẻ key), bao gồm hội thoại nhiều lượt, lỗi 429, switch mode, xóa lịch sử. Bản phát hành sẽ được tự động bổ sung GitHub Actions CI và HTTP probe evidence.

## Known limits
Đây là pre-release môn học, chưa có đăng nhập, quota/người dùng, database bền vững, moderation độc lập, benchmark chất lượng LLM trên bộ test đại diện, kiểm định hội thoại dài ngày hay kiểm thử tải đồng thời. Render Free có thể cold-start. Không có cơ sở để khẳng định 100% không bug hoặc trí thông minh ngang những chatbot hàng đầu.
