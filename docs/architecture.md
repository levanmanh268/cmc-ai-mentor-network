# Kiến trúc phần mềm CMC AI Mentor Network

# 1. Tổng quan

CMC AI Mentor Network là hệ thống ghép đôi Mentor cho sinh viên CMCU. Hệ thống hỗ trợ sinh viên tìm kiếm Mentor phù hợp và hỗ trợ quá trình kết nối, tư vấn học tập.

# 2. Kiến trúc tổng thể

Hệ thống được tổ chức thành các thành phần:

- Giao diện người dùng: tiếp nhận thao tác và hiển thị kết quả.
- Xử lý nghiệp vụ: xử lý yêu cầu ghép đôi Mentor và các chức năng liên quan.
- Quản lý dữ liệu: lưu trữ và truy xuất thông tin cần thiết.
- Thành phần AI: hỗ trợ tìm kiếm hoặc đề xuất dựa trên dữ liệu phù hợp.
- Kiểm thử: kiểm tra tính đúng đắn, bảo mật, hiệu năng và độ tin cậy.

# 3. Yêu cầu phi chức năng

- NFR-01: Hiệu năng.
- NFR-02: Bảo mật.
- NFR-03: Quyền riêng tư.
- NFR-04: Độ tin cậy.
- NFR-05: Khả năng tương thích.
- NFR-06: Khả năng sử dụng.
- NFR-07: Khả năng bảo trì.
- NFR-08: Khả năng xử lý lỗi.
- NFR-09: Tính ổn định của kết quả AI.
- NFR-10: Khả năng kiểm thử.

# 4. Nguyên tắc thiết kế

- Tách biệt các thành phần theo chức năng.
- Bảo vệ dữ liệu và thông tin xác thực.
- Xử lý lỗi rõ ràng, tránh làm gián đoạn toàn bộ hệ thống.
- Có thể kiểm thử từng thành phần độc lập.
- Ghi nhận kết quả kiểm thử và theo dõi lỗi qua GitHub Issues.

# 5. Kiểm thử

Mỗi yêu cầu phi chức năng phải có tiêu chí chấp nhận và ít nhất một trường hợp kiểm thử tương ứng. Kết quả được ghi lại trong GitHub Issues.
