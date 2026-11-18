# SECURITY & PRIVACY SPRINT | CMC AI Mentor Network, Nhóm 6

**Ngày:** 09/11/2026. **Giáo trình tham chiếu do giảng viên cung cấp:** *Engineering Software Products: An Introduction to Modern Software Engineering* (Ian Sommerville), Security and Privacy Chương 7; Testing/Security Testing Chương 9. **Source:** bộ 13 issue thầy gửi. **Trưởng nhóm:** Lê Văn Mạnh.

## 1. Bàn giao chính thức
- [GitHub Issues SEC-01..SEC-13](https://github.com/levanmanh268/cmc-ai-mentor-network/issues?q=is%3Aissue+SEC-)
- [PR #182: code, regression và tài liệu Security & Privacy](https://github.com/levanmanh268/cmc-ai-mentor-network/pull/182)
- [Báo cáo 12 security test groups](security-test-report.md)
- [Đánh giá rủi ro CIA](risk-assessment.md) và [sơ đồ mối đe dọa](threat-model.md)
- [Access-control matrix](access-control-matrix.md) và [session / rate-limit](session-and-rate-limit.md)
- [Bảo vệ key và truyền dữ liệu](secrets-and-transport.md)
- [Privacy data inventory](../privacy/data-inventory.md) và [quyền kiểm soát dữ liệu](../privacy/data-controls.md)
- [Security review và kịch bản demo](security-review.md)

## 2. Phân công và trạng thái triển khai

| ID | Issue | Priority | Phụ trách dự kiến | Artefact/evidence | Đánh giá đúng phạm vi |
| --- | --- | --- | --- | --- | --- |
| SEC-01 | [#169](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/169) | P0 | Mạnh | `risk-assessment.md`, 10 rủi ro CIA | Có bản phân tích, cần review |
| SEC-02 | [#170](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/170) | P1 | Mạnh | `threat-model.md` Mermaid DFD, 6 abuse cases | Có bản phân tích, cần review |
| SEC-03 | [#171](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/171) | P0 | Dương Tuấn Dũng | `rag_engine.py`, `security_controls.py`, input/path tests | Code trên PR, CI cần xác minh |
| SEC-04 | [#172](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/172) | P1 | Hà Văn Dương | `app.py` escaped labels, XSS/Markdown unit tests | Browser XSS manual cần xác minh |
| SEC-05 | [#173](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/173) | P0 | Hà Văn Dương | Session tests, session document | Logout auth N/A, browser isolation pending |
| SEC-06 | [#174](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/174) | P2 | Dương Tuấn Dũng | Demo quota audit | Brute-force login N/A; no true rate limit |
| SEC-07 | [#175](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/175) | P0 | Đỗ Văn Cường | `access-control-matrix.md` | Root app has no login: N/A, not PASS |
| SEC-08 | [#176](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/176) | P0 | Đỗ Văn Cường | Access matrix, session isolation | Account RBAC N/A; shared data authz future |
| SEC-09 | [#177](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/177) | P0 | Nguyễn Văn Phúc | `secrets-and-transport.md`, HEAD secret scan | Historical key revocation UNKNOWN; HTTPS check pending |
| SEC-10 | [#178](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/178) | P1 | Nguyễn Văn Phúc | `data-inventory.md`, consent tests | Third-party retention pending |
| SEC-11 | [#179](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/179) | P2 | Nguyễn Văn Phúc | `data-controls.md`, reset tests | Account deletion N/A, session control applies |
| SEC-12 | [#180](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/180) | P1 | Lê Hải Đăng | `security-test-report.md`, >8 tests and CI | Update ACTUAL after test run |
| SEC-13 | [#181](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/181) | P2 | Lê Hải Đăng + cả nhóm | `security-review.md`, 2 safe demos | Needs reviewer, runtime and UAT evidence |

**Lưu ý người phụ trách:** các tài khoản GitHub chưa xác minh chỉ được ghi tên người phụ trách *đề xuất*; không tự gán nhầm thành viên. Cần review chéo giữa người viết và reviewer.

## 3. Pipeline kiểm thử end-to-end

### Cài đặt và chạy an toàn trên máy/CI của nhóm
```bash
git clone https://github.com/levanmanh268/cmc-ai-mentor-network.git
cd cmc-ai-mentor-network
git fetch origin
git switch security/sprint-sec01-sec13-20261109
python -m pip install -r requirements.txt
python -m pytest -q -rs tests/test_security_sprint.py
python -m pytest -q -rs
python -m scripts.secret_guard
python -m py_compile app.py security_controls.py rag_engine.py tests/test_security_sprint.py
```

**Lưu ý:** Luôn ghi commit SHA thực tế của branch tại lúc chạy test và link workflow. Đừng gán số PASS của branch A cho merge commit B.

### Chạy demo bảo mật ngắn trước giảng viên
1. Giới thiệu Data Flow Diagram: browser và Streamlit session RAM; tài liệu Markdown là input không tin cậy; Groq chỉ gọi khi có key và consent.
2. Mở test input: type sai, query quá dài, symlinked knowledge root. Chỉ ra test trước khi sửa sẽ không đảm bảo biên kiểm soát; sau sửa test PASS đúng SHA.
3. Hiển thị escaped Markdown label không thi hành HTML/script và không giả mạo nhãn. Browser demo dùng payload vô hại/localhost, không quét hệ thống người khác.
4. Tắt checkbox Groq consent và mô tả vì sao client bị chặn. Không dán key thật trong video/demo.
5. Mở bảng risk assessment, giải thích còn điều kiện nào được ghi BLOCKED và người phụ trách tương ứng.

### Báo cáo nộp tối thiểu
Mỗi người gắn file Markdown `reports/team/<github_username>_security_<YYYY-MM-DD>.md` vào PR/issue. Nội dung: issue, môi trường, base/head/merge SHA, Steps/Expected/Actual, PASS/FAIL/SKIP/BLOCKED/NOT RUN, CI run, screenshots đã xóa dữ liệu cá nhân, reviewer, known issues, kết luận đúng scope. Dùng template đã có ở `reports/team/REPORT_TEMPLATE.md`.

## 4. Release / acceptance gates

**Không tự đánh dấu Sprint hoàn tất nếu còn:**
- [ ] PR security chưa được review độc lập và merge.
- [ ] Linux/Windows/browser CI hoặc regression đỏ trên SHA mới.
- [ ] Thiếu post-merge CI và test report so với main SHA.
- [ ] Key từng lộ chưa được chủ sở hữu xác nhận đã thu hồi/đổi; không đăng key.
- [ ] Chưa kiểm chứng TLS và privacy notice trên deployed environment.
- [ ] Chưa có người thực hiện UAT/kiểm thử browser/session isolation thực tế.
- [ ] RAG prompt-injection live chưa được đánh giá mà báo "AI an toàn tuyệt đối".
- [ ] Branch main vẫn chưa bật protected review/required checks theo #131.

Một issue chỉ được đóng khi code/docs thực sự đáp ứng tiêu chí áp dụng, có bằng chứng, PR được review, và mọi phần N/A được giải thích minh bạch. Không tự bịa cơ chế login, database hoặc cam kết không có bug.
