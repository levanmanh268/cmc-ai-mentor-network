# Báo cáo kiểm thử cá nhân | Issue #171 (SEC-03)

## 1. Thông tin

- Người thực hiện: Dương Tuấn Dũng (@TuanDungir)
- Issue: #171
- PR code/security controls: https://github.com/levanmanh268/cmc-ai-mentor-network/pull/182
- PR bằng chứng issue #171/#174: PENDING
- Reviewer độc lập: PENDING
- Tình trạng: BLOCKED — chờ CI/review độc lập cho PR bằng chứng; controls được triển khai ở PR #182

## 2. Scope và phiên bản

- Phạm vi: root Streamlit classroom app; `rag_engine.py`, `general_chat.py`, `matching_engine.py`, `mentors_data.py`, `security_controls.py` và regression tests.
- Code SHA được kiểm tra: `c8eebeb475034fffaaf93bd1cc9ca3ad0948718e2`.
- Hệ điều hành / runtime local: Windows, Python 3.14.5, pytest 8.4.2.
- Input/provider: tài liệu Markdown và fake provider; không dùng API key thật, PII, live model hay dịch vụ bên ngoài.
- App hiện không có database hoặc shell-execution path cho các trường input được audit; rà soát mã bằng tìm kiếm source không phát hiện SQL query, `subprocess`, `os.system`, `eval` hoặc `exec` trong các file phạm vi.

## 3. Test evidence

| ID | Steps / test | Expected | Actual | Status | Evidence |
| --- | --- | --- | --- | --- | --- |
| TC-01 | `tests/test_security_sprint.py::test_sec03_rejects_wrong_type_or_empty_query` và `test_sec03_rejects_non_string_answer_input_without_crashing` | Kiểu sai/rỗng bị từ chối, không gây lỗi | Các giá trị sai kiểu và rỗng bị từ chối; input không phải chuỗi trả `no-evidence` | PASS | Local pytest |
| TC-02 | `tests/test_security_sprint.py::test_sec03_rejects_oversized_query_before_provider_call` | Query vượt 4.000 ký tự không gọi provider | 4.001 ký tự trả `no-evidence`, không có source và fake provider không nhận request | PASS | Local pytest |
| TC-03 | `tests/test_security_sprint.py::test_sec03_symlinked_root_not_indexed_portable`; `test_symlinked_markdown_file_is_not_ingested` trong PR #192 | Không ingest root/file symlink trỏ ra ngoài knowledge root | Symlinked root bị từ chối; test symlink-file dùng monkeypatch, không phụ thuộc Windows symlink permission | PASS | Local pytest |
| TC-04 | `tests/test_rag_engine.py::test_model_without_citations_is_not_called_grounded`; `tests/test_quality_gates.py::test_qg14_invented_citation_falls_back` | Citation thiếu/sai không được coi là grounded | Fake responses thiếu hoặc bịa citation được fallback sang câu trả lời offline | PASS | Local pytest |
| TC-05 | Prompt injection trong Markdown: `test_untrusted_markdown_instructions_stay_out_of_system_prompt` trong PR #192 | Chỉ thị trong tài liệu ở user/context data, không thay system policy | Assertion xác nhận system message giữ policy, payload chỉ ở user context; test file security của PR #192 đạt 3 passed trên SHA `59605ba2dff44671b8eecc3f1e3c5cc0f29b6217` | PASS — separate PR | [PR #192](https://github.com/levanmanh268/cmc-ai-mentor-network/pull/192); local test run |
| TC-06 | `python -m pytest -q tests/test_security_sprint.py tests/test_rag_engine.py tests/test_quality_gates.py` | Regression bảo mật/RAG đạt | 88 passed, 1 skipped | PASS | Local pytest trên code SHA nêu trên |

CI run [42542025271](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42542025271) đạt 5/5 jobs trên SHA code `c8eebeb...` của PR #182. Test mới của PR #192 được chạy local tại SHA `59605ba...`; CI đó không bao gồm test của PR #192 và không thay thế review độc lập cho issue này.

## 4. Kết luận và giới hạn

- Các guard hiện có từ chối input sai/quá dài trước provider, chỉ nạp Markdown trong knowledge root và fallback khi provider trả citation không hợp lệ.
- Không có test này chứng minh khả năng chống mọi prompt injection, độ đúng ngữ nghĩa RAG hoặc độ an toàn của live model.
- Chưa xác minh browser/cloud UAT, red-team live, key rotation, authentication hoặc production deployment.
- **Kết luận:** các negative tests đạt local trên code SHA đã ghi; test phân tách injection được chạy local ở PR #192. BLOCKED chờ CI/review độc lập cho PR evidence và đối chiếu acceptance của maintainer.
- Issue #171 được giữ mở; không tự đóng trước review/merge.
