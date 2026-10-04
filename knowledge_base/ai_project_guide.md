# Hướng dẫn làm project phần mềm có AI

Tài liệu này là nội dung mẫu nội bộ của dự án CMC AI Mentor Network, không phải quy định chính thức của Đại học CMC.

## Quy trình issue đến commit

Mọi thay đổi nên bắt đầu bằng một GitHub Issue mô tả vấn đề, tiêu chí hoàn thành và phạm vi công việc. Issue cần được gán nhãn phù hợp như bug, enhancement hoặc documentation.

Sau khi hiểu issue, tạo branch riêng từ main. Chỉ thay đổi các file thuộc phạm vi issue. Trước khi commit cần xem git status và git diff, chạy kiểm tra phù hợp, sau đó commit với message ngắn gọn có Refs #<issue-number>.

Khi mở Pull Request, mô tả thay đổi, cách kiểm tra và dùng Closes #<issue-number> nếu PR hoàn tất toàn bộ yêu cầu. Không merge khi CI đang fail hoặc review còn lỗi chưa xử lý.

## Vòng lặp debug và review

Một vòng lặp chất lượng tối thiểu gồm: tái hiện lỗi, viết hoặc cập nhật test, sửa nguyên nhân gốc, chạy test, xem diff, review logic, rồi chạy lại test. Nếu review phát hiện regression thì quay lại bước sửa cho đến khi toàn bộ kiểm tra đạt.

Không nên chỉ sửa triệu chứng. Với tính năng AI, cần kiểm thử cả trường hợp API mất kết nối, API key chưa cấu hình, truy xuất không có bằng chứng và input rỗng.

## Nguyên tắc AI có căn cứ

RAG nên tách hai bước: truy xuất tài liệu liên quan và sinh câu trả lời. Khi tài liệu không chứa đủ bằng chứng, trợ lý phải nói rõ giới hạn thay vì bịa thêm. Câu trả lời cần hiển thị nguồn đã dùng để người học kiểm chứng.
