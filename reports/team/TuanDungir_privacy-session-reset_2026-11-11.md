# Báo cáo kiểm thử cá nhân | Issue #188

## 1. Thông tin

- Người thực hiện: TuanDungir
- GitHub username: @TuanDungir
- Vai trò: QA / privacy
- Ngày: 2026-11-11
- Issue: #188
- Pull Request: https://github.com/levanmanh268/cmc-ai-mentor-network/pull/197
- Reviewer độc lập: PENDING
- Tình trạng: CI PASS; READY FOR REVIEW; review độc lập đang chờ

## 2. Mã nguồn và môi trường

| Trường | Giá trị |
| --- | --- |
| Repository | https://github.com/levanmanh268/cmc-ai-mentor-network |
| Branch | `tuan/issue-188-privacy-session-reset` |
| Base SHA | `09850bf957300614702066604728320066dec9b9` |
| SHA kiểm thử mới | `52466a719d911823c6b922aed4625800861c9dca` |
| Merge SHA | PENDING |
| OS | Windows |
| Python / pytest | Python 3.14.5 / pytest 8.4.2 |
| Input | Hai dict session độc lập với dữ liệu giả lập |
| Provider / PII | Không gọi provider; không dùng PII hoặc credentials |

## 3. Steps, Expected, Actual

| ID | Steps / input | Expected | Actual | Status | Evidence |
| --- | --- | --- | --- | --- | --- |
| TC-01 | `python -m pytest -q tests/test_privacy_session_reset.py tests/test_profile_helpers.py tests/test_ui_helpers.py` | Reset hồ sơ A xóa profile/matching A, giữ favorites/chat A và không sửa session B; clear chat xóa messages A, giữ favorites/profile A và không sửa session B | 15 passed | PASS | Lệnh pytest local |
| TC-02 | `python -m pytest -q` | Toàn bộ repository suite đạt | 308 passed, 26 skipped; 2 test kiến trúc thất bại vì full-suite process không khởi chạy được `git` (`WinError 2`) | FAIL môi trường | Lệnh pytest local |
| TC-03 | GitHub Actions trên PR | CI Linux/Windows và các workflow bắt buộc đạt | 5/5 jobs thành công trên PR SHA `24befa91c71b08e1d32ee29a840fe591db276152` | PASS | https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42932441796 |

## 4. Phạm vi và giới hạn

- Chỉ thêm `tests/test_privacy_session_reset.py`; không sửa production code.
- Đây là unit test với hai dict session độc lập, không phải browser UAT và không chứng minh cách Streamlit lưu trữ session trên production.
- Hai lỗi của full-suite run là lỗi môi trường khi subprocess không tìm thấy `git`; chưa xác định nguyên nhân cụ thể. Không ghi nhận full suite là đạt.
- Không tạo đăng nhập/logout giả và không kiểm thử isolation giữa các tiến trình hoặc người dùng production.

## 5. Kết luận và bàn giao

**Kết luận:** READY FOR REVIEW. Hai test session-reset, các test helper liên quan và CI Linux/Windows đều đạt; review độc lập vẫn pending.

- Commit test: `52466a719d911823c6b922aed4625800861c9dca`
- CI run: https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42932441796 (5/5 jobs passed)
- PR: https://github.com/levanmanh268/cmc-ai-mentor-network/pull/197
- Merge SHA / CI trên `main`: PENDING
