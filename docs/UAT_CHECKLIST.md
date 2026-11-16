# User Acceptance Testing | Nhóm 6

Đối tượng: giảng viên/người dùng lần đầu, dùng prototype offline. **Chưa có kết quả UAT con người thực tế; đánh dấu PASS sau khi người kiểm thử trực tiếp thực hiện.**

Trước khi thử: Python 3.11+, chạy `run_windows.bat` (Windows) hoặc `python -m streamlit run app.py`, mở `http://localhost:8501`. Không cấu hình GROQ_API_KEY.

| ID | Kịch bản / thao tác | Expected result | PASS/FAIL/ngày |
| --- | --- | --- | --- |
| UAT-01 | Vào Hồ sơ; nhập lĩnh vực `RAG` và mục tiêu `Học RAG`, bấm lưu | Thông báo lưu trong phiên, không tạo tài khoản | Chưa kiểm thử |
| UAT-02 | Nhập toàn khoảng trắng ở mục tiêu, bấm lưu | Lỗi validation, không ghi đè hồ sơ hợp lệ | Chưa kiểm thử |
| UAT-03 | Vào AI Assistant, hỏi về quy trình GitHub Issue | Trả đoạn nguồn demo và relevance, ở offline-grounded | Chưa kiểm thử |
| UAT-04 | Hỏi `chlorophyll quang hợp lá cây` | Thông báo không tìm đủ bằng chứng, không bịa nguồn | Chưa kiểm thử |
| UAT-05 | Vào Tìm Mentor, bấm tìm, chọn bộ lọc lĩnh vực/loại hỗ trợ | Kết quả phù hợp bộ lọc, ranking ổn định | Chưa kiểm thử |
| UAT-06 | Bấm Lưu mentor, rerun UI, rồi Xóa trong danh sách đã lưu | Saved mentor giữ trong phiên, xóa đúng item | Chưa kiểm thử |
| UAT-07 | Xóa lịch sử chat | Chỉ xóa messages, không làm mất hồ sơ hay saved mentors | Chưa kiểm thử |
| UAT-08 | Xóa hồ sơ phiên | Profile trở về rỗng, kết quả matching cũ được reset | Chưa kiểm thử |
| UAT-09 | Thoát và khởi động lại server | Không cam kết phục hồi session; hiển thị giới hạn lưu phiên | Chưa kiểm thử |
| UAT-10 | Không có GROQ key, quay lại chat và mentor | Offline vẫn dùng được; không báo AI online | Chưa kiểm thử |

## Cách ghi nhận nghiệm thu
Người kiểm thử: ______  Ngày: ______  Thiết bị / browser: ______

Ngưỡng hoàn thành/thời gian tối đa (thống nhất với thầy **trước khi đo**): ______

Số scenario hoàn thành thực tế: ___ / 10. Thời gian từng scenario: ______. Lỗi và issue ID: ______.

**Không được tự chuyển cột trạng thái thành PASS** khi chưa có người kiểm thử. Screenshot/log không chứa API key và dữ liệu cá nhân thật.

Theo dõi: [Issue #22](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/22), [#35](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/35).
