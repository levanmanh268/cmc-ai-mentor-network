# Báo cáo kiểm thử cá nhân | Issue #186

## 1. Thông tin

- Người thực hiện: TuanDungir
- GitHub username: @TuanDungir
- Vai trò: UI / QA
- Ngày giờ thực hiện (GMT+7): 2026-11-11
- Issue: #186
- Pull Request: https://github.com/levanmanh268/cmc-ai-mentor-network/pull/195
- Reviewer độc lập: @levanmanh268 (được yêu cầu; review đang chờ)
- Tình trạng: READY FOR REVIEW; CI và review chưa hoàn tất

## 2. Mã nguồn và môi trường

| Trường | Giá trị |
| --- | --- |
| Repository | https://github.com/levanmanh268/cmc-ai-mentor-network |
| Nhánh | `tuan/issue-186-source-score-sanitization` |
| Base SHA | `09850bf957300614702066604728320066dec9b9` |
| Commit chứa sửa đổi và kiểm thử | `3b47b05d5e1652e6246ba2849834b0d22a9c99b4` |
| Merge SHA | PENDING |
| Hệ điều hành | Windows |
| Python / pytest | Python 3.14.5 / pytest 8.4.2 |
| Dữ liệu | Điểm nguồn giả lập trong unit test |
| Provider / mạng | Offline; không gọi provider |

## 3. Kiểm thử

| ID | Steps / input | Expected | Actual | Trạng thái | Bằng chứng |
| --- | --- | --- | --- | --- | --- |
| TC-01 | Trước sửa lỗi, chạy `tests/test_source_score_sanitization.py` với `NaN`, `Infinity`, `-Infinity`, Boolean, giá trị biên và chuỗi số/rác | Điểm không hợp lệ thành `0.0`; điểm hữu hạn được giữ hoặc clamp trong `[0.0, 1.0]` | 3 case thất bại: `NaN`, `Infinity`, `True` được chuyển thành `1.0`; 6 case đạt | FAIL trước sửa (TDD red) | Lệnh pytest local |
| TC-02 | Chạy `python -m pytest -q tests/test_source_score_sanitization.py tests/test_ui_helpers.py` | Kiểm thử mới và hành vi helper hiện có đều đạt | 15 passed | PASS | Lệnh pytest local |
| TC-03 | Chạy `python -m pytest -q` trên Windows | Toàn bộ suite đạt | 315 passed, 26 skipped, 2 failed. Hai test `test_architecture_docs` không khởi chạy được `git` (`WinError 2`) trong full-suite run | FAIL môi trường | Lệnh pytest local |
| TC-04 | Chạy riêng `python -m pytest -q tests/test_architecture_docs.py` khi Git có trên PATH | Kiểm tra tài liệu kiến trúc đạt | 8 passed | PASS | Lệnh pytest local |
| TC-05 | GitHub Actions trên PR #195 | Các job liên quan đạt | Đang chạy tại thời điểm ghi báo cáo | PENDING | https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42870573757 |

## 4. Thay đổi và giới hạn

- `source_history_payload` dùng `math.isfinite` sau khi parse; `NaN`, vô cực, Boolean và giá trị parse lỗi trở thành `0.0` trước khi clamp.
- Giữ hành vi chấp nhận chuỗi số hợp lệ và clamp điểm hữu hạn vào `[0.0, 1.0]`.
- Không gọi LLM/provider, không dùng dữ liệu cá nhân hoặc credential thật.
- Hai lỗi của full-suite run chỉ ghi nhận là lỗi khởi chạy tiến trình `git`; chưa xác định nguyên nhân cụ thể. Không tuyên bố full suite đạt.
- UAT người dùng, CI Windows/Linux, review độc lập và kiểm tra trên `main`: PENDING.

## 5. Kết luận và bàn giao

**Kết luận:** READY FOR REVIEW. Thay đổi và kiểm thử hồi quy đã push lên PR #195; issue chưa được đóng. Chờ CI xanh và review độc lập trước khi merge.

- SHA đã kiểm thử local: `3b47b05d5e1652e6246ba2849834b0d22a9c99b4`
- CI run: https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42870573757 (pending)
- Merge SHA / CI hậu merge: PENDING
- Pull Request: https://github.com/levanmanh268/cmc-ai-mentor-network/pull/195
