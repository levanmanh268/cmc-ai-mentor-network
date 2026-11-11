# Báo cáo kiểm thử cá nhân | Issue #174 (SEC-06)

## 1. Thông tin

- Người thực hiện: Dương Tuấn Dũng (@TuanDungir)
- Issue: #174
- Pull Request triển khai liên quan: https://github.com/levanmanh268/cmc-ai-mentor-network/pull/182
- PR cập nhật evidence: https://github.com/levanmanh268/cmc-ai-mentor-network/pull/201
- Reviewer độc lập: PENDING
- Tình trạng: BLOCKED — chờ review độc lập cho evidence PR; CI code hiện có đã đạt trên PR #182

## 2. Scope và phiên bản

- Code được kiểm tra: root Streamlit classroom app, `app.py` và quota-related AppTests.
- Code SHA: `c8eebeb475034fffaaf93bd1cc9ca3ad0948718e2`.
- Hệ điều hành / runtime local: Windows, Python 3.14.5, pytest 8.4.2.
- Dữ liệu/provider: session state giả lập và fake provider; không gửi request Groq thật, không dùng key thật hay dữ liệu người dùng.

## 3. Kết quả kiểm tra

| ID | Steps / test | Expected | Actual | Status | Evidence |
| --- | --- | --- | --- | --- | --- |
| TC-01 | Audit `app.py`: tìm login/OTP/password-reset/logout endpoint hoặc app-owned identity token | Nếu không có auth endpoint, brute-force/login throttling phải được ghi NOT APPLICABLE, không giả PASS | Root Streamlit không triển khai login, OTP, password reset hay account system | NOT APPLICABLE | `app.py`; [session-and-rate-limit.md](../../docs/security/session-and-rate-limit.md) |
| TC-02 | `tests/test_final_defense_probe.py::test_demo_quota_disables_chat_without_saying_server_enforces_it`; set `demo_chat_calls=30` | Chat UI disabled; provider không được gọi; thông báo không tuyên bố server enforcement | Test xác nhận chat disabled, warning nêu server-side quota cần thiết, fake provider không nhận call | PASS | Local pytest |
| TC-03 | `tests/test_end_to_end_flows.py::test_e2e05_probe_rate_limit_is_session_only`; set `demo_probe_calls=3` | Probe button disabled; không phát sinh provider call | Test xác nhận probe disabled và fake provider không nhận call | PASS | Local pytest |
| TC-04 | `python -m pytest -q tests/test_final_defense_probe.py::test_demo_quota_disables_chat_without_saying_server_enforces_it tests/test_end_to_end_flows.py::test_e2e05_probe_rate_limit_is_session_only` | Hai quota boundary regression đạt | 2 passed | PASS | Local pytest trên code SHA nêu trên |

CI run [42542025271](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42542025271) đạt 5/5 jobs trên SHA `c8eebeb...` của PR #182, gồm regression, Windows, Chromium E2E và Mermaid. Evidence đó không biến quota demo thành server-side control.

## 4. Phân tích áp dụng và giới hạn

- `MAX_CHAT_CALLS_PER_SESSION=30` và `MAX_PROBES_PER_SESSION=3` là counter trong `st.session_state`; chúng giới hạn nút/luồng trong session hiện tại.
- Counter có thể reset khi tạo session/reconnect. Đây **không** phải quota theo user/IP, anti-abuse hay bảo vệ ngân sách API ở server.
- Login brute-force control là **NOT APPLICABLE** cho app hiện tại vì không có login endpoint; không thêm auth giả để tạo kết quả kiểm thử hình thức.
- Nếu triển khai public với shared provider key, cần identity/auth được quản lý, quota backend-side theo account/IP, budget enforcement và monitoring trước khi coi abuse rate limiting là áp dụng/đạt.
- Chưa có browser UAT, kiểm tra production deployment hoặc xác minh quota ở hosting/provider.
- **Kết luận:** các UI demo quota đã được kiểm chứng local; bảo vệ rate-limit production chưa được triển khai. Issue được giữ mở chờ review/merge và maintainer xác nhận phạm vi nghiệm thu.
