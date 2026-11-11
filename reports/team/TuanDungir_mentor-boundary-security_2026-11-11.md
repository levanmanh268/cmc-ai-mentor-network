# Báo cáo kiểm thử cá nhân | Issue #185

## 1. Thông tin

- Người thực hiện: TuanDungir
- GitHub username: @TuanDungir
- Vai trò: QA / mentor data
- Ngày: 2026-11-11
- Issue: #185
- Pull Request: https://github.com/levanmanh268/cmc-ai-mentor-network/pull/196
- Reviewer độc lập: PENDING
- Tình trạng: CI PASS; READY FOR REVIEW; review độc lập đang chờ

## 2. Mã nguồn và môi trường

| Trường | Giá trị |
| --- | --- |
| Repository | https://github.com/levanmanh268/cmc-ai-mentor-network |
| Branch | `tuan/issue-185-mentor-boundary-security` |
| Base SHA | `09850bf957300614702066604728320066dec9b9` |
| SHA kiểm thử mới | `744e6a5838eab3cf1a79c4521f8d104074bc0d84` |
| Merge SHA | PENDING |
| OS | Windows |
| Python / pytest | Python 3.14.5 / pytest 8.4.2 |
| Input | Mentor dictionaries giả lập trong unit tests |
| Provider / PII | Không gọi provider; không dùng PII hoặc credentials |

## 3. Steps, Expected, Actual

| ID | Steps / input | Expected | Actual | Status | Evidence |
| --- | --- | --- | --- | --- | --- |
| TC-01 | `python -m pytest -q tests/test_mentor_boundary_security.py tests/test_mentor_data_diagnostics.py` | Duplicate ID, `id=True`, negative experience, missing field, và phần tử strengths rỗng trả diagnostic chính xác; tests hiện có tiếp tục đạt | 11 passed | PASS | Lệnh pytest local |
| TC-02 | `python -m pytest -q` | Toàn bộ repository suite đạt | 311 passed, 26 skipped; 2 test kiến trúc thất bại do full-suite process không khởi chạy được `git` (`WinError 2`) | FAIL môi trường | Lệnh pytest local |
| TC-03 | `python -m pytest -q tests/test_architecture_docs.py` với Git trên PATH | Các test kiến trúc đạt | 8 passed | PASS | Lệnh pytest local |
| TC-04 | GitHub Actions trên PR | CI Linux/Windows và các workflow bắt buộc đạt | 5/5 jobs thành công trên PR SHA `22159140f9cd2eaf380119719003baedbcfa924c` | PASS | https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42928884680 |

## 4. Phạm vi và giới hạn

- Chỉ thêm `tests/test_mentor_boundary_security.py`; không sửa `RAW_MENTORS`, production code, hoặc thuật toán ranking.
- Các test kiểm tra diagnostic output chính xác cho các trường hợp issue nêu; không đánh giá chất lượng semantic của mentor matching.
- Hai lỗi trong full-suite run là lỗi môi trường khi subprocess không tìm thấy `git`; chưa xác định nguyên nhân cụ thể. Không ghi nhận full suite là đạt.
- Đây là unit tests, không phải browser UAT, authentication/RBAC test, hay kiểm thử production.

## 5. Kết luận và bàn giao

**Kết luận:** READY FOR REVIEW. Test mới, test chẩn đoán liên quan, và CI Linux/Windows đều đạt; review độc lập vẫn pending.

- Commit test: `744e6a5838eab3cf1a79c4521f8d104074bc0d84`
- CI run: https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42928884680 (5/5 jobs passed)
- PR: https://github.com/levanmanh268/cmc-ai-mentor-network/pull/196
- Merge SHA / CI trên `main`: PENDING
