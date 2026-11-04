# BÁO CÁO KẾT QUẢ KIỂM THỬ CÁ NHÂN | NHÓM 6

> **Hướng dẫn:** Copy file này sang một tệp mới tên `reports/team/<github_username>_<workstream>_<YYYY-MM-DD>.md`. Thay mọi `<...>` bằng dữ liệu THỰC TẾ. Không gửi file mẫu chưa điền để nhận điểm hoàn thành. Nếu chưa chạy, ghi `NOT RUN` hoặc `BLOCKED`, tuyệt đối không tự điền PASS. Hướng dẫn tổng: `docs/TEAM_TESTING_EXECUTION_PLAN_2026-11-04.md`.

## 1. Thông tin báo cáo

- **Người thực hiện:** <họ tên>
- **GitHub username:** @<username>
- **Vai trò trong nhóm:** <frontend / backend / QA / CI / RAG / leader>
- **Ngày giờ thực hiện (GMT+7):** <YYYY-MM-DD HH:mm>
- **Issue phụ trách:** #<số issue 1>, #<số issue 2>
- **Pull Request:** <URL đến PR hoặc NOT CREATED>
- **Người review độc lập:** @<username hoặc NOT ASSIGNED>
- **Tình trạng tổng:** <READY FOR REVIEW / NEEDS FIXES / BLOCKED / NOT RUN>

## 2. Mã nguồn và môi trường thử nghiệm

| Trường | Giá trị thực |
| --- | --- |
| Repository | https://github.com/levanmanh268/cmc-ai-mentor-network |
| Nhánh công việc | <branch> |
| Base SHA lúc bắt đầu | <sha> |
| Head SHA đã thử | <sha, không dùng SHA của commit khác> |
| Merge SHA thực tế nếu có | <sha hoặc PENDING> |
| CI main SHA hậu merge | <sha hoặc PENDING> |
| Hệ điều hành | <Windows/Linux và version> |
| Python / dependencies | <version / cách cài> |
| Trình duyệt nếu có | <Chrome/Chromium/Edge, version> |
| URL thử | <localhost, Render hoặc NOT APPLICABLE> |
| Mock / offline / live | <loại thực tế> |
| Bộ dữ liệu đầu vào | <mô tả nguồn đã được phép sử dụng> |

## 3. Danh sách kiểm thử có Steps, Expected và Actual

| ID | Requirement / issue | Các bước chạy hoặc input cụ thể | Expected | Actual quan sát được | Status | Bằng chứng |
| --- | --- | --- | --- | --- | --- | --- |
| TC-01 | #<issue> | <từng bước và input> | <điều kiện mong đợi trước khi chạy> | <output/log thực tế> | PASS/FAIL/SKIPPED/BLOCKED/NOT RUN | <link CI/log/screenshot> |
| TC-02 | #<issue> | <từng bước và input> | <...> | <...> | <...> | <...> |
| TC-03 | #<issue> | <từng bước và input> | <...> | <...> | <...> | <...> |

Không gộp mọi test thành một dòng “PASS”. Case FAIL ghi input tối giản đủ tái hiện; tránh dán dữ liệu nhạy cảm.

## 4. Lệnh thực thi và kết quả máy tự động

```bash
# Paste lệnh đã thực sự chạy; ví dụ:
python -m pip install -r requirements-test.txt
python -m pytest -q -rs
python -m scripts.evaluate_rag
# Không khẳng định các lệnh trên đã chạy nếu thực tế chưa chạy.
```

| Môi trường/job | PASS | FAIL | ERROR | SKIP | BLOCKED/NOT RUN | SHA | URL log/artifact |
| --- | ---: | ---: | ---: | ---: | --- | --- | --- |
| Local pytest | <n> | <n> | <n> | <n> | <status> | <sha> | <URL hoặc đường dẫn log> |
| GitHub CI Linux | <n> | <n> | <n> | <n> | <status> | <sha> | <URL> |
| GitHub CI Windows | <n> | <n> | <n> | <n> | <status> | <sha> | <URL> |
| Chromium browser | <n> | <n> | <n> | <n> | <status> | <sha> | <URL> |
| Dependency audit | <n/a> | <n/a> | <n/a> | <n/a> | <status> | <sha> | <URL> |
| UAT người dùng thật | <n> | <n> | <n> | <n> | <status> | <sha> | <biên bản> |

**Coverage:** <covered/total lines, percent, named module scope> hoặc `NOT MEASURED`.  
**RAG metrics:** <dataset, held-out hay demo, retrieval/citation/semantic correctness/refusal riêng> hoặc `NOT MEASURED`.  
**Subtests:** <n> ghi riêng, không cộng nhầm vào con số pytest functions.  
**Những SKIP:** liệt kê từng test và lý do, nhất là khi thiếu dependency.

## 5. TDD và regression nếu có

| Bước | Commit SHA | Test | CI run | Kết quả |
| --- | --- | --- | --- | --- |
| RED: tạo test tái hiện | <sha/NOT APPLICABLE> | <tên test> | <URL> | <failure expected> |
| GREEN: sửa code và giữ test | <sha/NOT APPLICABLE> | <tên test> | <URL> | <pass> |

Không phải mọi nhiệm vụ đều cần TDD; nếu nhiệm vụ chỉ là QA thủ công hoặc tài liệu, ghi `NOT APPLICABLE`.

## 6. Vấn đề tìm thấy, mức độ và cách xử lý

| Bug | Severity P0/P1/P2 | Steps to reproduce | Expected/Actual | Người sửa | Issue/PR | Trạng thái |
| --- | --- | --- | --- | --- | --- | --- |
| BUG-01 | <P...> | <...> | <...> | <owner> | <URL> | OPEN/FIXED/BLOCKED |

Đính kèm ảnh hoặc trace có liên kết và đã xóa/che tên riêng, API key, email, thông tin hồ sơ người thử. Chỉ ghi “No issue found” nếu thật sự đã chạy đúng kịch bản trong phạm vi được nêu.

## 7. Rủi ro, các giới hạn và nội dung KHÔNG ĐƯỢC nhận là đã kiểm tra

- **Live Groq inference:** <PASS có bằng chứng riêng / BLOCKED / NOT RUN>
- **Human UAT:** <PASS có biên bản / FAIL / BLOCKED / NOT RUN>
- **Prompt injection live / semantic RAG:** <chi tiết hoặc NOT RUN>
- **Git history secret audit / key revocation:** <đã xác nhận qua kênh riêng của leader / UNKNOWN; tuyệt đối không đăng key>
- **Bảo vệ nhánh main:** <đã xác minh / chưa xác minh>
- **Tính đúng ngữ nghĩa và hallucination:** <kết luận trong đúng phạm vi, không tự viết "zero hallucination">
- **Khác:** <...>

## 8. Kết luận và bàn giao

**Tôi xác nhận**: thông tin PASS/FAIL và các số liệu được lấy từ kết quả thực nghiệm đúng commit SHA; các mục chưa làm được đã ghi rõ.  
**Kết luận:** <READY FOR REVIEW / NEEDS FIXES / BLOCKED / NOT RUN>  
**Các mục cần tiếp tục:** <issue, owner, next action>  
**Link review:** <URL hoặc PENDING>  
**Ngày và SHA đã được merge:** <YYYY-MM-DD, SHA hoặc PENDING>  
**Kết quả CI trên main sau merge:** <URL hoặc PENDING>  

**Bắt buộc:** Comment trên từng issue đã nhận bằng link tới file `.md` vừa nộp và PR chứa nó. Thành viên không tự merge PR của chính mình thay cho review độc lập. Mọi kết luận tổng thể phải được trưởng nhóm đối chiếu ở issue #166.
