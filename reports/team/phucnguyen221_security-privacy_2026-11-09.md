# Báo cáo kiểm thử cá nhân | Issue #87

## 1. Thông tin báo cáo

- **Người thực hiện:** Nguyễn Văn Phúc (@phucnguyen221).
- **Vai trò:** QA / security sanity.
- **Ngày giờ (GMT+7):** 2026-11-09.
- **Issue:** #87.
- **Pull Request:** https://github.com/levanmanh268/cmc-ai-mentor-network/pull/192
- **Base:** `security/sprint-sec01-sec13-20261109` (base PR #182), vì phần hardening liên quan chưa có trên `main`.
- **Người review độc lập:** PENDING.
- **Trạng thái:** NEEDS REVIEW.

## 2. Môi trường và phạm vi

| Trường | Giá trị |
| --- | --- |
| Repository | https://github.com/levanmanh268/cmc-ai-mentor-network |
| Branch | `test/issue-87-security-sanity` |
| Base SHA | `c8eebeb475034fffaaf93bd1cc9ca3ad0948718e2` |
| Test commit SHA | `1e8277cb66cda32038311490ba041e395ae382fa` |
| Report commit / CI-tested SHA | PENDING |
| OS / Python | Windows / Python 3.14.10 |
| Chạy | Offline, fake provider, dữ liệu tổng hợp; không có API key thật |
| CI run | PENDING |

Đây là **security sanity suite**, không phải penetration test, red-team đánh giá model, hay xác nhận sản phẩm an toàn tuyệt đối. Không đưa PII, secret thật, hay dữ liệu production vào test hoặc báo cáo.

## 3. Threat → testcase → kết quả → mức độ và xử lý

| ID | Threat / severity | Steps và testcase | Expected | Actual | Fix / xử lý |
| --- | --- | --- | --- | --- | --- |
| SEC87-01 | Input sai kiểu/rỗng/quá dài; P1 (availability) | Chạy `test_sec03_rejects_wrong_type_or_empty_query`, `test_sec03_rejects_oversized_query_before_provider_call`, `test_sec03_rejects_non_string_answer_input_without_crashing` và `test_qg01_invalid_history_does_not_invoke_provider`. | Từ chối input trước retrieval/provider, không crash, không có provider call. | Các assertion PASS trong bộ 107 test local. | Giới hạn 4.000 ký tự và validate kiểu tại boundary trong PR #182. |
| SEC87-02 | Symlink/path escape và Markdown quá cỡ; P0/P1 (confidentiality/availability) | Chạy `test_sec03_symlinked_root_not_indexed_portable`, `test_qg23_oversized_document_not_indexed`, `test_qg25_source_name_is_relative_to_kb`. | Không index root symlink; bỏ file trên 2 MB; source path giữ tương đối trong kho tài liệu. | Các assertion PASS trong bộ 107 test local. | Từ chối symlink root/file và file vượt giới hạn trong `KnowledgeBase` ở PR #182. Chưa có pentest filesystem/cloud. |
| SEC87-03 | Chỉ dẫn độc hại trong Markdown (prompt injection); P1 (integrity) | Chạy `test_untrusted_markdown_instructions_stay_out_of_system_prompt` với tài liệu tổng hợp chứa “Ignore all prior instructions…”. | System prompt nói tài liệu là dữ liệu không đáng tin; payload không được chèn vào system role. | PASS: payload chỉ xuất hiện trong context của user message; system prompt chứa rule không làm theo chỉ dẫn trong tài liệu. | Tách system/context và rule chống chỉ dẫn tài liệu đã có ở PR #182; test này kiểm tra cấu trúc prompt, **không** chứng minh model chống được prompt injection khi chạy live. |
| SEC87-04 | Provider exception làm lộ credential; P0 (confidentiality) | Chạy `test_provider_exception_secret_is_not_returned_or_logged`, `test_qg06_provider_http_errors_are_sanitized`, `test_qg07_network_and_generic_error_are_sanitized`, `test_qg15_provider_error_preserves_offline_document_sources`. | Chuỗi credential giả từ lỗi không xuất hiện trong answer/log; dùng fallback offline. | PASS: fake secret không xuất hiện trong output hoặc captured log; provider failure dùng `offline-fallback`. | Lỗi provider được sanitize/fallback; không ghi payload/credential thô. Không sử dụng key thật. |
| SEC87-05 | Session/state lẫn giữa người dùng; P0 (confidentiality) | Chạy `test_sec05_session_profile_reset_does_not_touch_other_session`, `test_sec11_save_profile_does_not_update_another_session`, `test_e2e04_independent_sessions_do_not_share_profiles`. | Reset/update session A không đổi state session B. | PASS trong unit/AppTest giả lập hai session. | State giữ theo Streamlit session; test không xác nhận isolation trên deployment/cloud thật. |
| SEC87-06 | Gọi provider khi chưa consent hoặc sau revoke; P0 (confidentiality) | Chạy `test_sec10_consent_deny_by_default`, `test_sec10_consent_explicit_true_only`, `test_e2e03_groq_consent_revocation_blocks_new_calls`. | Mặc định từ chối; không gọi provider khi consent off/revoked; chỉ explicit true mới bật. | PASS; test fake xác nhận số provider calls không tăng khi consent off/revoke. | Opt-in rõ ràng và fail-closed; không gửi request tới Groq thật. |
| SEC87-07 | Credential vô tình nằm trong tracked files; P0 (confidentiality) | Chạy `python -m scripts.secret_guard`; kiểm tra test fake pattern `test_sec09_secret_guard_detects_fake_examples_without_real_keys` và `test_secret_guard_detects_fake_credentials_without_echoing_values`. | Phát hiện chuỗi credential giả; không in secret value; không có mẫu key thật trong tracked files. | Secret guard báo `No tracked secret pattern detected.`; các test assertions PASS. | Dùng secret guard trên tracked HEAD và chỉ dùng giá trị giả trong test. Git-history audit/key revocation không được bao hàm. |

## 4. Lệnh đã chạy và kết quả

```text
python -m pytest -q tests/test_issue_87_security_sanity.py tests/test_security_sprint.py tests/test_quality_gates.py tests/test_real_ai_chat.py tests/test_end_to_end_flows.py tests/test_secret_guard.py
107 passed in 7.25s

python -m scripts.secret_guard
No tracked secret pattern detected.
```

| Môi trường/job | PASS | FAIL | ERROR | SKIP | SHA / URL |
| --- | ---: | ---: | ---: | ---: | --- |
| Local Windows, security-related test set | 107 | 0 | 0 | 0 | `1e8277cb66cda32038311490ba041e395ae382fa` |
| Secret guard local | 1 | 0 | 0 | 0 | Test commit SHA ở trên |
| GitHub CI Linux | PENDING | — | — | — | PENDING |
| GitHub CI Windows | PENDING | — | — | — | PENDING |

Coverage và dependency audit: NOT MEASURED / NOT RUN. Bộ 107 bao gồm các testcase bảo mật hiện có trên integration base; không phải 107 bài pentest độc lập.

## 5. Rủi ro và giới hạn chưa xác minh

- Prompt injection/semantic faithfulness trên live model: **NOT VERIFIED**; test mới chỉ xác minh cấu trúc prompt offline.
- Pentest cloud/deployment, HTTPS headers và isolation giữa browser/user thật: **NOT VERIFIED / NOT RUN**.
- Git history secret audit và xác nhận revoke key từng lộ: **NOT VERIFIED**; chỉ quét tracked files của snapshot và dùng secret giả.
- Provider consent tests dùng fake client; không gửi dữ liệu hoặc gọi Groq thật.
- Không có kết luận “AI không hallucinate” hoặc “không còn lỗ hổng”.

## 6. Bàn giao

- **PR:** https://github.com/levanmanh268/cmc-ai-mentor-network/pull/192
- **CI run URL:** PENDING.
- **Kết luận:** NEEDS REVIEW; chờ CI trên PR và independent review.
- **Việc tiếp theo:** Xác nhận CI đúng head SHA, xin review độc lập, cập nhật URL/kết quả. Chỉ xem xét pentest cloud trong môi trường được cho phép.
