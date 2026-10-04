# Customer Feedback Workflow

Mục tiêu của quy trình này là để mọi thay đổi từ khách hàng đều có thể truy vết và nghiệm thu.

## Khi nhận yêu cầu

1. Tạo GitHub Issue bằng template **Customer request** hoặc **Bug report**.
2. Giữ nguyên mô tả nhu cầu gốc của khách hàng.
3. Nhóm phân tích và bổ sung acceptance criteria nếu cần.
4. Chỉ bắt đầu code khi phạm vi đủ rõ.

## Khi phát triển

1. Tạo branch riêng cho issue.
2. Commit có `Refs #issue`.
3. Chạy compile check và pytest.
4. Mở PR có `Closes #issue`.
5. CI phải xanh.
6. Review diff và sửa mọi regression trước khi merge.

## Khi khách hàng thay đổi yêu cầu

Nếu thay đổi nhỏ và PR chưa merge, cập nhật acceptance criteria ngay trên issue và ghi comment giải thích.

Nếu yêu cầu cũ đã hoàn tất và merge, tạo issue mới để giữ lịch sử quyết định rõ ràng.

## Definition of Done

Một yêu cầu được coi là Done khi:

- acceptance criteria đạt
- test liên quan tồn tại hoặc đã được cập nhật
- CI xanh
- review hoàn tất
- PR merge vào main
- issue đóng
