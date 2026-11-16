# BÁO CÁO KIỂM THỬ CÁ NHÂN | ISSUE #165

## 1. Thông tin báo cáo

- **Người thực hiện:** @sonic295207
- **GitHub username:** @sonic295207
- **Vai trò:** Frontend / QA
- **Ngày giờ thực hiện (GMT+7):** 2026-11-04 08:57
- **Issue phụ trách:** #165 — tạo mentor nháp an toàn, chỉ trong phiên
- **Pull Request:** NOT CREATED
- **Người review độc lập:** NOT ASSIGNED
- **Tình trạng tổng:** BLOCKED — chưa thể tạo PR hoặc gắn báo cáo lên issue vì workspace không có Git metadata.

## 2. Mã nguồn và môi trường thử nghiệm

| Trường | Giá trị thực |
| --- | --- |
| Repository | https://github.com/levanmanh268/cmc-ai-mentor-network |
| Nhánh công việc | UNKNOWN — không có `.git` |
| Base SHA lúc bắt đầu | NOT AVAILABLE |
| Head SHA đã thử | NOT AVAILABLE — thay đổi chưa commit |
| Merge SHA thực tế | PENDING |
| CI main SHA hậu merge | PENDING |
| Hệ điều hành | Windows |
| Python / dependencies | Python 3.14.10; requirements.txt trong môi trường ảo riêng; pytest-playwright cài riêng để chạy Chromium |
| Trình duyệt | Chromium 156.0.8078.4 |
| URL thử | http://127.0.0.1:8579 |
| Mock / offline / live | Local Streamlit, offline; không gọi Groq |
| Bộ dữ liệu đầu vào | Seed mentors trong `mentors_data.py` và hồ sơ mentor tổng hợp trong kiểm thử |

## 3. Danh sách kiểm thử

| ID | Requirement / issue | Các bước chạy hoặc input cụ thể | Expected | Actual quan sát được | Status | Bằng chứng |
| --- | --- | --- | --- | --- | --- | --- |
| TC-01 | #165 — xác thực form | Kiểm tra giá trị bắt buộc, độ dài tối đa, kiểu và khoảng kinh nghiệm, lĩnh vực/hỗ trợ hợp lệ, kỹ năng bắt buộc và chuỗi giống API key | Dữ liệu không hợp lệ bị từ chối; dữ liệu hợp lệ được chuẩn hóa | Các ca tham số hóa và chuẩn hóa chạy thành công | PASS | `tests/test_mentor_drafts.py` |
| TC-02 | #165 — ID và cách ly dữ liệu | Tạo nháp trong hai state riêng; đối chiếu ID với seed và kiểm tra repository trước/sau | ID không trùng; chỉ state của phiên đầu có nháp; repository dùng chung không đổi | Các assertion đều đạt | PASS | `tests/test_mentor_drafts.py` |
| TC-03 | #165 — matching và lọc | Tạo mentor tổng hợp, đưa vào `mentor_pool` của phiên; lọc theo lĩnh vực và loại hỗ trợ | Mentor nháp xuất hiện trong kết quả đúng bộ lọc | Mentor nháp được xếp hạng; repository không bị thay đổi | PASS | `tests/test_mentor_drafts.py`, `tests/test_matching_engine.py` |
| TC-04 | #165 — giao diện Streamlit | Điền form qua AppTest và submit | Nháp được tạo trong session state, không lưu vào dữ liệu chung | Nháp duy nhất xuất hiện trong state kiểm thử | PASS | `tests/test_mentor_drafts_ui.py` |
| TC-05 | #165 — luồng Chromium | Tạo mentor, lọc và matching, lưu yêu thích, yêu cầu xóa, xác nhận xóa; kiểm tra browser context thứ hai | Mentor dùng được trong phiên đầu; sau xác nhận bị xóa khỏi phiên đó; context thứ hai không thấy nháp | Kịch bản browser hoàn tất thành công | PASS | `e2e/browser_spec.py::test_browser06_session_mentor_creation_matching_removal_and_isolation` |

## 4. Lệnh thực thi và kết quả

```powershell
& 'C:\Users\FPT\.copilot\session-state\c49b581b-1ad1-4f5a-b353-616128290719\files\issue165-venv\Scripts\python.exe' -m pytest -q tests\test_mentor_drafts.py tests\test_mentor_drafts_ui.py tests\test_matching_engine.py tests\test_streamlit_ui.py tests\test_end_to_end_flows.py tests\test_issue_batch.py
# 34 passed

& 'C:\Users\FPT\.copilot\session-state\c49b581b-1ad1-4f5a-b353-616128290719\files\issue165-venv\Scripts\python.exe' -m pytest -q e2e\browser_spec.py -k browser06 --browser chromium
# 1 passed, 5 deselected

& 'C:\Users\FPT\.copilot\session-state\c49b581b-1ad1-4f5a-b353-616128290719\files\issue165-venv\Scripts\python.exe' -m py_compile app.py matching_engine.py mentor_drafts.py tests\test_mentor_drafts.py tests\test_mentor_drafts_ui.py tests\test_matching_engine.py tests\test_streamlit_ui.py tests\test_end_to_end_flows.py e2e\browser_spec.py
# exit code 0
```

| Môi trường/job | PASS | FAIL | ERROR | SKIP | BLOCKED/NOT RUN | SHA | URL log/artifact |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| Local pytest regression | 34 | 0 | 0 | 0 | None | NOT AVAILABLE | Local terminal |
| Chromium browser test | 1 | 0 | 0 | 5 | 5 unrelated browser cases deselected by `-k browser06` | NOT AVAILABLE | Local terminal |
| GitHub CI Linux | — | — | — | — | NOT RUN | NOT AVAILABLE | No CI run started |
| GitHub CI Windows | — | — | — | — | NOT RUN | NOT AVAILABLE | No CI run started |
| Dependency audit | — | — | — | — | NOT RUN | NOT AVAILABLE | No audit run |
| UAT người dùng thật | — | — | — | — | NOT RUN | NOT AVAILABLE | No UAT evidence |

**Coverage:** NOT MEASURED.  
**RAG metrics:** NOT MEASURED / NOT APPLICABLE to this feature.  
**Subtests:** 34 pytest cases passed in the focused regression selection; 1 Chromium case passed.  
**Những SKIP:** Không có test bị skip trong các lệnh trên; năm browser cases không thuộc issue này bị loại trừ bằng `-k browser06`.

## 5. TDD và regression

| Bước | Commit SHA | Test | CI run | Kết quả |
| --- | --- | --- | --- | --- |
| RED | NOT RECORDED | N/A | N/A | Không có Git metadata để lưu SHA |
| GREEN | NOT RECORDED | Mentor-draft unit/UI, matching regressions và Chromium flow | N/A | 34 pytest và 1 Chromium test PASS |

## 6. Vấn đề tìm thấy, mức độ và cách xử lý

| Bug | Severity | Steps to reproduce | Expected/Actual | Người sửa | Issue/PR | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| Không ghi nhận lỗi trong phạm vi các ca kiểm thử đã chạy | — | — | — | @sonic295207 | #165 / PR NOT CREATED | BLOCKED chờ đưa thay đổi vào Git checkout và review |

## 7. Rủi ro và giới hạn

- Mentor nháp và yêu thích chỉ nằm trong `st.session_state`; không có database, đăng nhập hoặc persistence qua phiên mới.
- Lĩnh vực và loại hỗ trợ bị giới hạn ở danh mục hiện có của seed mentors.
- Form chặn một số mẫu API key/token/private key phổ biến và hiển thị cảnh báo; đây là kiểm tra theo mẫu, không phải bộ phát hiện bí mật tổng quát. Không nhập dữ liệu nhạy cảm.
- Kiểm thử Chromium chỉ xác nhận ứng dụng local/offline; không xác nhận Groq inference, Render deployment hoặc hành vi bảo mật production.
- Git history, CI trên GitHub, UAT, dependency audit và bảo vệ nhánh `main` chưa được xác minh.

## 8. Kết luận và bàn giao

**Kết luận:** BLOCKED — mã nguồn và kiểm thử local sẵn sàng để đưa vào checkout có Git, nhưng chưa thể tạo commit/PR hoặc bình luận issue từ workspace hiện tại.  
**Các mục cần tiếp tục:** chuyển các thay đổi liên quan #165 và báo cáo này sang Git checkout; chạy CI trên commit thực; tạo PR và yêu cầu review độc lập; đăng liên kết báo cáo/PR lên issue #165.  
**Link review:** PENDING  
**Ngày và SHA đã được merge:** PENDING  
**Kết quả CI trên main sau merge:** PENDING
