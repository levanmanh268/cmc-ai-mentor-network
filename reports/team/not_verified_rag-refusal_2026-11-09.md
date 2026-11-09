# Báo cáo kiểm thử cá nhân | Issue #187

## 1. Thông tin báo cáo

- **Người thực hiện:** AI assistant trong phiên làm việc này; danh tính thành viên không được xác minh.
- **GitHub username:** NOT VERIFIED.
- **Vai trò:** RAG / kiểm thử.
- **Ngày giờ thực hiện (GMT+7):** 2026-11-09, khoảng 09:06.
- **Issue:** #187.
- **Pull Request:** https://github.com/levanmanh268/cmc-ai-mentor-network/pull/189
- **Người review độc lập:** PENDING.
- **Tình trạng tổng:** NEEDS REVIEW (CI và review độc lập chưa có kết quả).

## 2. Mã nguồn và môi trường

| Trường | Giá trị |
| --- | --- |
| Repository | https://github.com/levanmanh268/cmc-ai-mentor-network |
| Nhánh công việc | `test/issue-187-rag-refusal` |
| Nhánh nền / base PR | `security/sprint-sec01-sec13-20261109` |
| Base SHA | `c8eebeb475034fffaaf93bd1cc9ca3ad0948718e2` |
| Head SHA đã kiểm thử | `f58860d5945eebefcf2c7e0cb9ca3ad0948718e2` |
| Merge SHA / CI main SHA | PENDING |
| Hệ điều hành | Windows; phiên bản không được ghi nhận |
| Python / pytest | Python 3.14.10 / pytest 8.4.2 |
| Chế độ chạy | Offline; provider giả, không dùng API key và không gọi Groq thật |
| Dữ liệu | Markdown tổng hợp trong `tmp_path`; corpus trống hoặc tài liệu GitHub workflow tổng hợp |

PR #182 chưa merge vào `main`, do đó PR #189 dùng nhánh tích hợp của #182 làm base thay vì `main`.

## 3. Các kiểm thử: Steps, Expected, Actual

| ID | Steps / input | Expected | Actual quan sát được | Status |
| --- | --- | --- | --- | --- |
| TC-01 | Tạo knowledge base Markdown trống bằng `tmp_path`; hỏi `Quy trình tạo GitHub issue là gì?`; truyền provider giả. | `mode=no-evidence`, không có nguồn và không gọi provider. | Đúng: `mode=no-evidence`, `sources=()`, provider không được gọi. | PASS |
| TC-02 | Tạo corpus với `GitHub issue branch pull request review workflow documentation.`; hỏi `Chlorophyll photosynthesis plant sunlight`; truyền provider giả. | Câu ngoài chủ đề trả về `mode=no-evidence`, không có nguồn và không gọi provider. | Đúng: `mode=no-evidence`, `sources=()`, provider không được gọi. | PASS |
| TC-03 | Gọi `validate_citation_ids("Unsupported statement [S0].", num_sources=1)`. | Từ chối ID nguồn bắt đầu từ 0. | Trả về `False`. | PASS |
| TC-04 | Gọi `validate_citation_ids("Unsupported statement [S99].", num_sources=1)`. | Từ chối ID vượt số nguồn. | Trả về `False`. | PASS |
| TC-05 | Gọi `validate_citation_ids("Unsupported statement without a source.", num_sources=1)`. | Từ chối câu không có citation. | Trả về `False`. | PASS |

## 4. Lệnh và kết quả tự động

Lệnh đã chạy trên Windows tại head SHA `f58860d5945eebefcf2c7e0cb9ca3ad0948718e2`:

```text
python -m pytest -q tests/test_rag_refusal_security.py tests/test_quality_gates.py tests/test_issue_batch.py
68 passed in 22.15s
```

| Môi trường/job | PASS | FAIL | ERROR | SKIP | SHA | URL log/artifact |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| Local Windows, ba module test liên quan | 68 | 0 | 0 | 0 | `f58860d5945eebefcf2c7e0cb9ca3ad0948718e2` | Kết quả console cục bộ, không có URL |
| GitHub CI Linux | — | — | — | — | — | PENDING; PR chưa có status/check run |
| GitHub CI Windows | — | — | — | — | — | PENDING; PR chưa có status/check run |

**Coverage:** NOT MEASURED.  
**RAG metrics:** NOT MEASURED; đây là guard test, không phải đánh giá semantic RAG.  
**Skip:** Không có trong lệnh kiểm thử đã ghi ở trên.

## 5. TDD và thay đổi sản phẩm

- Không sửa code sản phẩm; issue chỉ yêu cầu kiểm thử hành vi đã có.
- Không có API key và không gọi inference trực tiếp.
- Kết quả test mới được bao gồm trong lệnh kiểm thử: 5 test mới PASS.

## 6. Vấn đề, giới hạn và nội dung chưa xác nhận

- Không phát hiện lỗi trong phạm vi năm case kiểm thử này.
- Kết quả chỉ xác nhận nhánh xử lý `no-evidence` và kiểm tra thành viên citation ID trong bộ test offline.
- `validate_citation_ids` không kiểm tra citation có hỗ trợ ngữ nghĩa cho từng khẳng định hay không.
- Các test này **không chứng minh AI không hallucinate**, không đánh giá chất lượng suy luận hoặc độ đúng ngữ nghĩa.
- Live Groq inference, prompt injection trực tiếp, human UAT, coverage và CI Linux/Windows: NOT RUN / PENDING.
- Review độc lập và CI của PR #189: PENDING.

## 7. Kết luận và bàn giao

**Kết luận:** NEEDS REVIEW. Năm test mới và 63 test liên quan khác PASS cục bộ; chưa đủ bằng chứng để xác nhận CI hoặc review độc lập.

- **PR:** https://github.com/levanmanh268/cmc-ai-mentor-network/pull/189
- **CI run URL:** PENDING.
- **Việc tiếp theo:** Chạy CI trên PR, yêu cầu review độc lập, cập nhật URL và kết quả CI sau khi có.
- **Merge SHA / CI trên main:** PENDING.
