# v0.3.1 — Final Defense Readiness Patch (19/10/2026)

**Classroom pre-release**, deadline bảo vệ 20/10/2026. Chưa phải production, không tuyên bố 100% bug-free hay có chất lượng/khả năng tương đương ChatGPT, Gemini, Claude và NotebookLM.

## Đã sửa và thêm
- **Kiểm tra AI thật:** sidebar có nút **🧪 Kiểm tra AI thật ngay** sau khi có Groq API key và user đã đồng ý gửi dữ liệu. Nút gọi `openai/gpt-oss-120b` qua provider client thật và hiển thị nội dung phản hồi; lỗi auth/quota/kết nối hiển thị có kiểm soát. Không coi việc API client tồn tại là đã kết nối thành công.
- **Demo guard:** giới hạn **30 câu hỏi Trò chuyện AI mỗi phiên** và tối đa **3 lần probe mỗi phiên**, khống chế lượt bấm vô ý. Đây không phải auth, rate limit toàn hệ thống hay chống abuse: reconnect tạo phiên mới sẽ reset quota.
- **Adversarial UI tests:** consent mặc định tắt, không gọi mô hình khi chưa đồng ý; mô phỏng chat-submit hai lượt và kiểm tra ngữ cảnh, chuyển Chat ↔ tài liệu không trộn lịch sử, lỗi auth không lộ key.
- **NFR sample:** `scripts/final_smoke_audit.py` đo 50 lần p50/p95 của offline RAG và mentor ranking trong môi trường CI CPU. Không gán các số này thành latency thực của cloud/API.
- **Handover + defense:** `docs/FINAL_DEFENSE_GATE.md` có danh sách rủi ro P0/P1, kịch bản demo 3 phút, câu trả lời phản biện và tiêu chí xác minh.

## Bắt buộc để AI thật hoạt động
1. Quản trị viên vào Render → service **cmc-ai-mentor-network-group6** → Environment, lưu **`GROQ_API_KEY`** hợp lệ hoặc người sử dụng tự nhập key trong widget password. Key không thuộc mã nguồn; không gửi cho người khác.
2. Vào ứng dụng, tick **Đồng ý gửi câu hỏi, lịch sử chat và ngữ cảnh đến Groq**; trong sidebar nhấn **🧪 Kiểm tra AI thật ngay**.
3. Chỉ đánh dấu **online-inference PASS** nếu thấy phản hồi do model tạo ra và trạng thái thành công. Khi 401, 429, timeout, chưa thể coi là PASS; không giả lập model.
4. Test chat 2 lượt, RAG nguồn và không có bằng chứng, lưu profile và matching.

**Tuyên bố kiểm thử đúng phạm vi:** Python unit và Streamlit AppTest dùng client giả lập ở CI. GitHub Actions, Render `live` và `/_stcore/health` chỉ xác minh code/app startup, **không chứng minh đã gọi Groq thành công**. Chưa có bằng chứng API key thật đã được cấu hình/được kiểm thử; việc nghiệm thu AI thật phải làm trên site trước buổi bảo vệ.

## Đường dẫn
- App: https://cmc-ai-mentor-network-group6.onrender.com
- Report: https://github.com/levanmanh268/cmc-ai-mentor-network/blob/main/docs/FINAL_DEFENSE_GATE.md
- Feature acceptance (chờ live inference): https://github.com/levanmanh268/cmc-ai-mentor-network/issues/63
- Final gate: https://github.com/levanmanh268/cmc-ai-mentor-network/issues/67
- Prior release: https://github.com/levanmanh268/cmc-ai-mentor-network/releases/tag/v0.3.0

**Chưa trong phạm vi:** NotebookLM feature parity (audio/video, file upload, web search, mind map), claim-level groundedness benchmark, authentication, user database/persistence, production rate limits, concurrent load/SLA, độc lập penetration test. Đây là *known limitations*, không được nói đã hoàn thành khi giảng viên hỏi.

GitHub Actions sẽ gắn CI SHA, public cloud HTTP probe và tag SHA nếu v0.3.1 vượt qua mọi gate. Bản phát hành là **prerelease**.
