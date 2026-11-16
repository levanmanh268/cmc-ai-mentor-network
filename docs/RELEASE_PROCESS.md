# Quy trình GitHub Release cho CMC AI Mentor Network

## Khác nhau giữa Issue, Pull Request và Release

- **Issue:** công việc hoặc lỗi cần xử lý.
- **Pull Request:** đề xuất thay đổi mã nguồn kèm review/CI.
- **Closed Issue:** công việc có trạng thái đã đóng; chỉ tính là hoàn thành nếu acceptance criteria thực sự được đáp ứng.
- **GitHub Release:** snapshot version-tagged trên một commit đã chọn, có release notes, source ZIP/TAR và liên kết đến các Issues/PR đã hoàn thành. Đây là phần thầy/cô có thể xem qua tab **Releases**.

## Bản phát hành đầu tiên v0.1.0

Source of truth: `docs/RELEASE_NOTES_v0.1.0.md`. Workflow: `.github/workflows/publish-classroom-release.yml`.

Các bước tự động đã cố định:
1. Tạo branch từ `main`, hoàn thành thay đổi có mã Issue, mở PR.
2. Chỉ merge sau khi CI của PR PASS và review.
3. Khi CI workflow `CI` trên **main** hoàn thành thành công, workflow phát hành kiểm tra đúng `head_sha`, repo và sự kiện `push`.
4. Chỉ một lần tạo GitHub Release `v0.1.0` từ chính commit đã qua CI; đính kèm link CI làm bằng chứng. Nếu release đã có, workflow thoát thành công mà không ghi đè hoặc tạo thêm tag.
5. Kiểm tra `https://github.com/levanmanh268/cmc-ai-mentor-network/releases` và đối chiếu sha của tag với commit CI.

**Cơ chế này chỉ xuất bản v0.1.0**, không tự tạo v0.2.0 khi có commit mới. Các phiên bản sau cần phát hành qua quy trình PR + checklist và phiên bản workflow phù hợp; không đổi tag đã xuất bản.

## Checklist trước mỗi lần phát hành

- [ ] Liệt kê các **closed Issues** đã được xác thực; không đánh đồng issue tạo ra với issue hoàn thành.
- [ ] Không đưa các PR vẫn Open hoặc có merge conflicts vào mục “đã phát hành”.
- [ ] Kiểm tra CI của đúng commit và cả Windows/Linux; kiểm tra Mermaid, startup, offline behavior.
- [ ] Ghi tính năng thực tế, lỗi đã sửa, giới hạn/NFR còn mở và thông tin chạy thử.
- [ ] Kiểm tra không đưa khóa API, credential, `.env` hoặc tài liệu nhạy cảm vào source và release notes.
- [ ] Phân biệt ứng dụng môn học Streamlit ở root với sáu lab AI độc lập trong monorepo.
- [ ] Tạo tag/release bất biến trên commit đã qua CI và xác minh URL của release sau khi publish.
- [ ] Để thầy/cô kiểm tra: liên kết Releases, đóng Issue, Pull Requests, Actions và README.
- [ ] Với tính năng còn dang dở, giữ Issue ở trạng thái Open và đưa vào backlog bản tiếp theo.

## Phân công và bàn giao

Trưởng nhóm Lê Văn Mạnh review/merge và công bố danh sách release. Các thành viên phát triển trong branch riêng theo Issue; mỗi PR gắn `Closes #<issue>` **chỉ khi** toàn bộ tiêu chí chấp nhận của Issue đó đạt. Nếu cần hoàn thiện thêm tài liệu, dùng `Refs #<issue>` và chưa đóng Issue.

`v0.1.0` là **Classroom Prototype (Pre-release)**. Nó chứng minh có source và CI chạy được, không có nghĩa sản phẩm đã triển khai production hoặc tất cả NFR đã nghiệm thu.
