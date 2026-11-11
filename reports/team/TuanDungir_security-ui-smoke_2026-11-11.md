# Báo cáo kiểm thử cá nhân | Issue #183

## 1. Thông tin

- Người thực hiện: TuanDungir
- GitHub username: @TuanDungir
- Vai trò: QA / UI security
- Ngày: 2026-11-11
- Issue: #183
- Pull Request: https://github.com/levanmanh268/cmc-ai-mentor-network/pull/199
- Reviewer độc lập: PENDING
- Tình trạng tổng: BLOCKED — chờ CI trên integration branch và review độc lập

## 2. Mã nguồn và môi trường

| Trường | Giá trị |
| --- | --- |
| Repository | https://github.com/levanmanh268/cmc-ai-mentor-network |
| Branch | `tuan/issue-183-security-ui-smoke` |
| Integration base | `security/sprint-sec01-sec13-20261109` (PR #182 còn mở) |
| Base SHA | `c8eebeb475034fffaaf93bd1cc2ed4a884a91d56` |
| Head SHA đã thử | `f8b120c57ce0d3260bfbd671f7b592549d69b975` |
| Merge SHA | PENDING |
| Hệ điều hành | Windows |
| Python / pytest | Python 3.14.5 / pytest 8.4.2 |
| Trình duyệt / URL thử | NOT APPLICABLE — AppTest, không phải browser UAT |
| Provider / dữ liệu | Offline; nhãn Markdown/HTML giả và nguồn RAG fixture; không dùng API key, PII hoặc provider thật |

`main` chưa có `safe_markdown_label` từ PR #182, vì vậy PR #199 dùng đúng integration base theo yêu cầu issue, không sao chép các thay đổi của PR #182.

## 3. Steps, Expected, Actual

| ID | Steps / input | Expected | Actual | Status | Evidence |
| --- | --- | --- | --- | --- | --- |
| TC-01 | `python -m pytest -q tests/test_security_ui_smoke.py::test_mentor_markdown_label_is_escaped_in_search_results`; AppTest hiển thị tên mentor fixture `<b>Demo Mentor</b> **admin** [profile](https://example.test) | Nhãn HTML/Markdown được hiển thị như văn bản, không tạo markup giả | Output Markdown chứa HTML-escaped và metacharacter được escape; AppTest không có exception | PASS | Local pytest |
| TC-02 | `python -m pytest -q tests/test_security_ui_smoke.py::test_rag_source_labels_are_escaped_and_legacy_filename_remains_intact`; RAG fixture trả nhãn giả và `legacy.md` | Nhãn nguồn được escape; `legacy.md` vẫn giữ nguyên và có relevance | Trước sửa, AppTest tái hiện nguồn mới bị nội suy trực tiếp vào Markdown; sau sửa, cả nhãn fixture được escape và `legacy.md` hiển thị nguyên vẹn | PASS sau sửa | Local pytest; regression trong PR #199 |
| TC-03 | `python -m pytest -q tests/test_security_ui_smoke.py tests/test_security_sprint.py tests/test_streamlit_ui.py tests/test_real_ai_chat.py tests/test_rag_engine.py` | Regression UI/security/RAG liên quan không hỏng | 50 passed, 1 skipped | PASS | Local pytest |
| TC-04 | `python -m pytest -q -rs` | Toàn bộ suite trên integration base đạt | 335 passed, 26 skipped. Skip do FastAPI/httpx tùy chọn chưa cài, `python-docx`/`pypdf` tùy chọn chưa cài và symlink không khả dụng trên Windows | PASS WITH SKIPS | Local pytest |
| TC-05 | GitHub Actions trên PR #199 | CI Linux/Windows chạy trên đúng integration base | Chưa có check run. Workflow `.github/workflows/ci.yml` hiện chỉ kích hoạt `pull_request` vào `main`, còn PR #199 phải dùng base integration branch để tránh trộn code PR #182 | BLOCKED | https://github.com/levanmanh268/cmc-ai-mentor-network/pull/199/checks |

Full-suite cần Git trong PATH; môi trường subprocess có `GIT_CONFIG_VALUE_2` rỗng nên lệnh được chạy với biến cấu hình Git sai định dạng đó được loại bỏ. Khi chạy đúng môi trường, hai test architecture cũng đạt.

## 4. Thay đổi và giới hạn

- Thêm hai Streamlit AppTest offline cho tên mentor và tên nguồn RAG.
- AppTest phát hiện tên nguồn RAG trong câu trả lời mới được nội suy trực tiếp vào Markdown; sửa bằng `safe_markdown_label`, đồng bộ với hiển thị lịch sử và tên mentor.
- Không sửa `app.py` ngoài đường render nguồn tìm thấy lỗi.
- Fixture dùng HTML/Markdown vô hại; không chạy script hay payload hoạt động.
- Đây là kiểm thử component/UI bằng AppTest. Không phải browser UAT, không kiểm thử trình duyệt thực hoặc dịch vụ production.
- 26 test skip được liệt kê ở TC-04; không cài thêm dependency tùy chọn.

## 5. Kết luận và bàn giao

**Kết luận:** BLOCKED — code và kiểm thử local đạt; GitHub CI chưa chạy do giới hạn branch filter hiện tại, và chưa có review người độc lập.

- Commit code/test: `f8b120c57ce0d3260bfbd671f7b592549d69b975`
- CI run: NOT RUN; xem trạng thái PR tại https://github.com/levanmanh268/cmc-ai-mentor-network/pull/199/checks
- PR: https://github.com/levanmanh268/cmc-ai-mentor-network/pull/199
- Cần tiếp tục: cấu hình/cho phép CI trên integration branch hoặc chạy CI sau khi PR #182 được tích hợp; chờ reviewer độc lập.
- Merge SHA / CI trên `main`: PENDING
