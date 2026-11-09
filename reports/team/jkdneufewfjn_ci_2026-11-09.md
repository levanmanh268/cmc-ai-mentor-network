# Báo cáo kiểm thử cá nhân | Lê Hải Đăng — CI/CD

## 1. Thông tin
- **Người thực hiện:** Lê Hải Đăng
- **GitHub:** @jkdneufewfjn
- **Vai trò:** CI/CD / Testing
- **Ngày (GMT+7):** 2026-11-09
- **Issue:** [#184](https://github.com/levanmanh268/cmc-ai-mentor-network/issues/184)
- **Pull Request:** [#191](https://github.com/levanmanh268/cmc-ai-mentor-network/pull/191)
- **Reviewer độc lập:** PENDING
- **Tình trạng:** READY FOR REVIEW — CI đang queued

## 2. Repo / SHA / môi trường
| Trường | Giá trị |
|---|---|
| Repository | https://github.com/levanmanh268/cmc-ai-mentor-network |
| Branch | `test/issue-184-testing-report-cli-fail-closed` |
| Base branch | `main` |
| Base SHA | `09850bf957300614702066604728320066dec9b9` |
| Head SHA kiểm thử | `dff135099ad020c614c52e20a11466a989affeb3` |
| File thêm | `tests/test_testing_report_cli_negative.py` |
| CI run | [GitHub Actions #42548071611](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42548071611) |
| CI status lúc ghi | QUEUED |
| Local test | isolated pytest run; không phải GitHub CI |

## 3. Test cases — Steps / Expected / Actual
| ID | Steps | Expected | Actual | Status |
|---|---|---|---|---|
| TC-184-01 Missing JUnit | Chạy CLI với đường dẫn JUnit không tồn tại | Exit code != 0, report NOT VERIFIED, không PASS | Local pytest case passed | PASS |
| TC-184-02 Malformed XML | Tạo XML không hợp lệ rồi chạy CLI | Exit code != 0, in lỗi evidence, không PASS | Local pytest case passed | PASS |
| TC-184-03 Zero tests | JUnit có `tests=0` | Exit code != 0, verdict NOT VERIFIED | Local pytest case passed | PASS |
| TC-184-04 One failed | JUnit có `tests=1, failures=1` | Exit code != 0, verdict FAIL | Local pytest case passed | PASS |

## 4. Lệnh và kết quả
```bash
python -m pytest -q tests/test_testing_report_cli_negative.py
```

**Local isolated run:** `4 passed`. Test đã chạy trên bản kiểm tra cục bộ của `scripts/testing_report.py` lấy từ repository; cần xác nhận lại trên CI thật.

| Job | PASS | FAIL | ERROR | SKIP | Status | SHA / URL |
|---|---:|---:|---:|---:|---|---|
| Local isolated pytest | 4 | 0 | 0 | 0 | PASS | SHA `dff135099ad020c614c52e20a11466a989affeb3` |
| GitHub Actions | — | — | — | — | QUEUED / NOT COMPLETED | [Run #42548071611](https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42548071611) |
| Linux/Windows matrix | — | — | — | — | WAITING FOR CI | CI run above |
| Independent review | — | — | — | — | PENDING | PR #191 |

## 5. TDD / regression
- Negative CLI tests added for missing/malformed/empty/failing evidence.
- Production CLI implementation was already present in `main`; no production-code change was needed.
- Workflow files were not modified.

## 6. Issues / findings
- Không có bug mới được khẳng định ngoài phạm vi test.
- Issue #184 yêu cầu fail-closed behavior; tests assert non-zero exit and no PASS claim in generated report.

## 7. Giới hạn / pending
- GitHub Actions run đang QUEUED tại thời điểm báo cáo; chưa ghi nhận kết quả Linux/Windows.
- Reviewer độc lập chưa review.
- Chưa merge; chưa có merge SHA hoặc post-merge CI.
- Không test live Groq, browser UAT, bảo mật cloud hoặc behavior ngoài CLI.
- PR #182 đang mở riêng; PR #191 dựa trên `main` vì CLI script đã tồn tại trên main, không copy code từ PR #182.

## 8. Bàn giao
- **Commit SHA test:** `dff135099ad020c614c52e20a11466a989affeb3`
- **PR:** https://github.com/levanmanh268/cmc-ai-mentor-network/pull/191
- **CI run:** https://github.com/levanmanh268/cmc-ai-mentor-network/actions/runs/42548071611
- **Next:** đợi CI complete + review độc lập, rồi cập nhật report actual result.
