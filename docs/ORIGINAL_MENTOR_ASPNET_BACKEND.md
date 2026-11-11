# Tích hợp ASP.NET backend vào website Mentor gốc

**Website người dùng:** https://cmc-ai-mentor-network-group6.onrender.com

**Kiến trúc đúng:**

```text
Người dùng -> Streamlit app.py (UI gốc, AI Assistant, RAG, matching)
                   |                |
                   |                +-> mentors_data.py (5 mentor mẫu sẵn có)
                   +-> mentor_helpers.py (bản nháp chỉ trong phiên)
                   +-> mentor_api.py -> ASP.NET Core 10 REST API
                                        -> PostgreSQL (đề xuất mentor công khai)
```

Đây là **phần tích hợp vào website gốc**, kế thừa form tạo mentor của Hà Văn Dương từ PR #168, KHÔNG thay UI hiện hành bằng một trang web khác. Mục "👥 Tìm Mentor" và thuật toán hybrid matching cũ vẫn hoạt động khi backend hoặc database mất kết nối.

## Hai loại mentor, không được nhầm lẫn

1. **5 mentor mẫu gốc**: trong `mentors_data.py`, giữ nguyên nội dung và thuật toán matching, không ghi đè.
2. **Bản nháp riêng**: form và tính năng xóa bản nháp trong Streamlit Session State của PR #168, có thể dùng khi không có database.
3. **Đề xuất mentor công khai**: người dùng bấm xác nhận đã được phép công bố rồi gửi bản nháp tới ASP.NET `POST /api/mentor-suggestions`; backend kiểm tra đầu vào, lưu PostgreSQL, trả mã dữ liệu. Dữ liệu mới được hiển thị dưới nhãn **CHƯA XÁC MINH**. Các đề xuất có thể được dùng cho matching trong bản demo nhưng không được mô tả là mentor thật đã được kiểm chứng.

Không có đăng nhập, quyền sở hữu/xóa hồ sơ công khai hoặc xác minh mentor. Do đó hệ thống chưa phù hợp cho dữ liệu cá nhân hoặc production; tuyệt đối không nhập tài khoản, mật khẩu, số điện thoại, email hay dữ liệu nhạy cảm.

## Chạy cục bộ

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Nếu không có `MENTOR_API_URL`, tất cả UI cũ và bản nháp phiên vẫn hoạt động, và không tuyên bố lưu bền vững.

Để bật đọc/ghi đề xuất công khai khi database được cấu hình:

```bash
export MENTOR_API_URL=https://cmc-ai-mentor-group6-aspnet-live.onrender.com
python -m streamlit run app.py
```

Backend ASP.NET phải có PostgreSQL riêng và `GET /health/ready` trả HTTP 200. `MENTOR_API_URL` là URL công khai, không phải chuỗi kết nối hay secret. Chuỗi `DATABASE_URL` chỉ được đặt trong Render backend, không chuyển vào Streamlit, browser hay mã nguồn.

## Đồng bộ động và giới hạn

Bảng đề xuất công khai sử dụng `st.fragment(run_every="10s")` của Streamlit để tải lại từ ASP.NET khoảng 10 giây một lần. Khi người dùng bấm "Tìm Mentor", pool xếp hạng lấy dữ liệu mới nhất từ API theo cơ chế cache TTL 8 giây. Đây là **near-realtime polling**, không phải SSE push ở phía Streamlit. API ASP.NET có SSE cho client phù hợp, nhưng website cũ không tự nhận luồng SSE. Không gọi đây là cập nhật tức thì từng mili giây.

## Yêu cầu nghiệm thu

- [ ] Backend PR #193 chạy 100% CI: xUnit + PostgreSQL 16 E2E + SSE + Docker.
- [ ] Backend có `DATABASE_URL` riêng, health/ready 200. Tuyệt đối không dùng database của dự án Delta Travel.
- [ ] PR tích hợp được người khác review và tất cả kiểm thử Python/Windows/Chromium PASS ở đúng SHA.
- [ ] Trên website Streamlit cũ, lưu bản nháp, tạo đề xuất công khai, thấy đề xuất ở browser B sau khoảng 10 giây, dùng trong matching, giữ nguyên 5 mentor mẫu.
- [ ] Restart hai dịch vụ, xác nhận đề xuất vẫn còn trong PostgreSQL.
- [ ] Chụp bằng chứng đúng URL/commit; không khẳng định DONE khi các bước chưa chạy.

**Tình trạng ở lúc tạo tài liệu:** ASP.NET backend đã có Render service LIVE nhưng chưa có database riêng; Streamlit production chưa merge PR này và chưa bật `MENTOR_API_URL`. Do đó thao tác trên website gốc vẫn ở chế độ phiên, chưa được gọi là persistent.
